from __future__ import annotations

import json
import math
from pathlib import Path
from ml_system.config.settings import CONFIG
from ml_system.schemas import PredictionRequest, PredictionResponse
from ml_system.training.tokenizer import Tokenizer
from ml_system.training.models import NaiveBayesModel, LinearSoftmaxModel


def load_tokenizer_from_json(path: str | Path) -> Tokenizer:
    """Load tokenizer from JSON."""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return Tokenizer.from_dict(data)


def load_model_from_json(path: str | Path) -> NaiveBayesModel | LinearSoftmaxModel:
    """Load model from JSON."""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    model_type = data.get("model_type")
    if model_type == "naive_bayes":
        return NaiveBayesModel.from_dict(data)
    elif model_type in {"linear_softmax", "scratch_linear_softmax"}:
        return LinearSoftmaxModel.from_dict(data)
    else:
        raise ValueError(f"Unknown model type: {model_type}")


def load_report_from_json(path: str | Path) -> dict:
    """Load training report from JSON."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


class InferenceEngine:
    """Production inference engine."""

    def __init__(
        self,
        tokenizer_path: str | Path = None,
        model_path: str | Path = None,
        report_path: str | Path = None,
        confidence_threshold: float = CONFIG.confidence_threshold,
    ) -> None:
        current_dir = CONFIG.get_current_model_path()
        
        self.tokenizer = load_tokenizer_from_json(
            tokenizer_path or current_dir / "tokenizer.json"
        )
        self.model = load_model_from_json(
            model_path or current_dir / "model.json"
        )
        default_report = current_dir / "report.json"
        if not default_report.exists():
            default_report = current_dir / "training_report.json"
        self.report = load_report_from_json(
            report_path or default_report
        )
        
        self.confidence_threshold = confidence_threshold
        self.min_confidence_floor = CONFIG.min_confidence_floor
        self.ambiguity_margin = CONFIG.ambiguity_margin
        self.temperature = self.report.get("temperature", 1.0)
        self.model_name = self.report.get("champion_model", "unknown")

    def _apply_temperature(self, probs: dict[str, float]) -> dict[str, float]:
        """Apply temperature scaling to probabilities using log-space for numerical stability."""
        if self.temperature <= 0:
            return probs

        safe_logs = {
            label: math.log(max(value, 1e-12))
            for label, value in probs.items()
        }
        max_log = max(safe_logs.values())
        scaled = {
            label: (value - max_log) / self.temperature
            for label, value in safe_logs.items()
        }
        exp_scores = {label: math.exp(value) for label, value in scaled.items()}
        total = sum(exp_scores.values())
        if total <= 0:
            return probs
        return {label: value / total for label, value in exp_scores.items()}

    def _token_signal_strength(self, phrase: str) -> float:
        tokens = self.tokenizer.tokenize(phrase)

        if hasattr(self.model, "weights"):
            weighted_tokens: set[str] = set()
            for label in getattr(self.model, "labels", []):
                weighted_tokens.update(getattr(self.model, "weights", {}).get(label, {}).keys())
            if not tokens:
                return 0.0
            overlap = sum(1 for token in tokens if token in weighted_tokens)
            return overlap / max(1, len(tokens))

        if hasattr(self.model, "token_count_per_class"):
            vocab: set[str] = set()
            for counts in getattr(self.model, "token_count_per_class", {}).values():
                vocab.update(counts.keys())
            if not tokens:
                return 0.0
            overlap = sum(1 for token in tokens if token in vocab)
            return overlap / max(1, len(tokens))

        return 1.0

    def predict(self, request: PredictionRequest) -> PredictionResponse:
        """Make a prediction."""
        phrase = (request.phrase or "").strip()
        if not phrase:
            uniform = {
                label: 1.0 / max(1, len(self.model.labels))
                for label in self.model.labels
            }
            return PredictionResponse(
                label="Unclear",
                confidence=0.0,
                rationale="Empty input",
                model=self.model_name,
                all_scores=uniform,
            )

        probs_list = self.model.predict_proba([phrase], self.tokenizer)
        all_scores = probs_list[0]

        signal_strength = self._token_signal_strength(phrase)
        if signal_strength < 0.08:
            # If almost all tokens are unseen, avoid overconfident bias-only predictions.
            uniform = {
                label: 1.0 / max(1, len(self.model.labels))
                for label in self.model.labels
            }
            return PredictionResponse(
                label="Unclear",
                confidence=0.0,
                rationale="Insufficient known activity signals in input",
                model=self.model_name,
                all_scores=uniform,
            )

        calibrated = all_scores

        ranked = sorted(calibrated.items(), key=lambda x: x[1], reverse=True)
        top_label, top_confidence = ranked[0]
        runner_up_confidence = ranked[1][1] if len(ranked) > 1 else 0.0
        margin = top_confidence - runner_up_confidence

        if top_confidence < self.min_confidence_floor:
            final_label = "Unclear"
            rationale = (
                f"Confidence {top_confidence:.2f} below minimum floor "
                f"{self.min_confidence_floor:.2f}"
            )
        elif top_confidence < self.confidence_threshold and margin < self.ambiguity_margin:
            final_label = "Unclear"
            rationale = (
                f"Borderline confidence {top_confidence:.2f} with small class margin "
                f"{margin:.2f}"
            )
        else:
            final_label = top_label
            if top_confidence < self.confidence_threshold:
                rationale = (
                    f"Predicted with confidence {top_confidence:.2f}; accepted due to "
                    f"clear margin {margin:.2f}"
                )
            else:
                rationale = f"Predicted with confidence {top_confidence:.2f}"

        return PredictionResponse(
            label=final_label,
            confidence=top_confidence,
            rationale=rationale,
            model=self.model_name,
            all_scores=calibrated,
        )
