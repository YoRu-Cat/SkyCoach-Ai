from __future__ import annotations

import math
from pathlib import Path

from .schema import PredictionRequest, PredictionResponse
from .model_loader import (
    load_tokenizer_from_json,
    load_model_from_json,
    load_report_from_json,
    ScratchTokenizer,
    ScratchNaiveBayes,
    ScratchLinearSoftmax,
)


class PredictionEngine:
    def __init__(
        self,
        tokenizer_path: str | Path,
        model_path: str | Path,
        report_path: str | Path,
        min_confidence: float = 0.72,
    ) -> None:
        self.tokenizer = load_tokenizer_from_json(tokenizer_path)
        self.model = load_model_from_json(model_path)
        self.report = load_report_from_json(report_path)
        self.min_confidence = min_confidence
        self.labels = self.report.get("labels", [])
        self.temperature = self.report.get("temperature", 1.0)
        self.model_name = self.report.get("champion_model", "unknown")

    def _apply_temperature(self, logits: dict[str, float]) -> dict[str, float]:
        """Apply temperature scaling to calibrate probabilities."""
        max_logit = max(logits.values())
        scaled = {k: (v - max_logit) / self.temperature for k, v in logits.items()}
        exp_scores = {k: math.exp(v) for k, v in scaled.items()}
        total = sum(exp_scores.values())
        return {k: v / total for k, v in exp_scores.items()}

    def predict(self, request: PredictionRequest) -> PredictionResponse:
        """Predict the label and confidence for a phrase."""
        probs_list = self.model.predict_proba([request.phrase], self.tokenizer)
        all_scores = probs_list[0]

        calibrated = self._apply_temperature(all_scores)

        top_label = max(calibrated.items(), key=lambda x: x[1])[0]
        top_confidence = calibrated[top_label]

        if top_confidence < self.min_confidence:
            final_label = "Unclear"
            rationale = f"Confidence {top_confidence:.2f} below threshold {self.min_confidence}"
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
