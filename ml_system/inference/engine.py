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
        confidence_threshold: float = 0.72,
    ) -> None:
        # Use defaults from current model directory if not provided
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
        self.temperature = self.report.get("temperature", 1.0)
        self.model_name = self.report.get("champion_model", "unknown")

    def _apply_temperature(self, logits: dict[str, float]) -> dict[str, float]:
        """Apply temperature scaling."""
        max_logit = max(logits.values())
        scaled = {k: (v - max_logit) / self.temperature for k, v in logits.items()}
        exp_scores = {k: math.exp(v) for k, v in scaled.items()}
        total = sum(exp_scores.values())
        return {k: v / total for k, v in exp_scores.items()}

    def predict(self, request: PredictionRequest) -> PredictionResponse:
        """Make a prediction."""
        probs_list = self.model.predict_proba([request.phrase], self.tokenizer)
        all_scores = probs_list[0]

        calibrated = self._apply_temperature(all_scores)

        top_label = max(calibrated.items(), key=lambda x: x[1])[0]
        top_confidence = calibrated[top_label]

        if top_confidence < self.confidence_threshold:
            final_label = "Unclear"
            rationale = f"Confidence {top_confidence:.2f} below threshold {self.confidence_threshold}"
        else:
            final_label = top_label
            rationale = f"Predicted with confidence {top_confidence:.2f}"

        return PredictionResponse(
            label=final_label,
            confidence=top_confidence,
            rationale=rationale,
            model=self.model_name,
            all_scores=calibrated,
        )
