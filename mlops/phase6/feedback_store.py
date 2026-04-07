from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime
from .schema import PredictionFeedback, UncertainPrediction


class FeedbackStore:
    """Manage persistent storage of user feedback and uncertain predictions."""

    def __init__(self, feedback_dir: str | Path) -> None:
        self.feedback_dir = Path(feedback_dir)
        self.feedback_dir.mkdir(parents=True, exist_ok=True)
        self.feedback_file = self.feedback_dir / "feedback.jsonl"
        self.uncertain_file = self.feedback_dir / "uncertain_predictions.jsonl"

    def record_feedback(self, feedback: PredictionFeedback) -> None:
        """Store user correction feedback."""
        record = {
            "phrase": feedback.phrase,
            "predicted_label": feedback.predicted_label,
            "predicted_confidence": feedback.predicted_confidence,
            "corrected_label": feedback.corrected_label,
            "feedback_timestamp": feedback.feedback_timestamp,
            "feedback_source": feedback.feedback_source,
        }
        with self.feedback_file.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")

    def record_uncertain_prediction(self, pred: UncertainPrediction) -> None:
        """Flag prediction for review due to low confidence."""
        record = {
            "phrase": pred.phrase,
            "predicted_label": pred.predicted_label,
            "confidence": pred.confidence,
            "all_scores": pred.all_scores,
            "flagged_timestamp": pred.flagged_timestamp,
            "confidence_threshold": pred.confidence_threshold,
        }
        with self.uncertain_file.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")

    def get_feedback_count(self) -> int:
        """Count total feedback records."""
        if not self.feedback_file.exists():
            return 0
        with self.feedback_file.open("r", encoding="utf-8") as f:
            return sum(1 for _ in f)

    def get_uncertain_count(self) -> int:
        """Count total uncertain predictions."""
        if not self.uncertain_file.exists():
            return 0
        with self.uncertain_file.open("r", encoding="utf-8") as f:
            return sum(1 for _ in f)

    def load_feedback_as_jsonl(self) -> list[dict]:
        """Load all feedback records as dicts."""
        if not self.feedback_file.exists():
            return []
        records = []
        with self.feedback_file.open("r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    records.append(json.loads(line))
        return records

    def load_uncertain_as_jsonl(self) -> list[dict]:
        """Load all uncertain predictions as dicts."""
        if not self.uncertain_file.exists():
            return []
        records = []
        with self.uncertain_file.open("r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    records.append(json.loads(line))
        return records

    def clear_feedback(self) -> None:
        """Clear all feedback records (after processing)."""
        if self.feedback_file.exists():
            self.feedback_file.unlink()

    def clear_uncertain(self) -> None:
        """Clear all uncertain predictions (after processing)."""
        if self.uncertain_file.exists():
            self.uncertain_file.unlink()
