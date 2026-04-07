from __future__ import annotations

import json
from pathlib import Path

from .feedback_store import FeedbackStore
from .model_versioning import ModelVersionRegistry


class LearningRetrainer:
    """Coordinate retraining with accumulated feedback and uncertain predictions."""

    def __init__(
        self,
        feedback_dir: str | Path,
        registry_dir: str | Path,
        min_feedback_threshold: int = 20,
    ) -> None:
        self.feedback_store = FeedbackStore(feedback_dir)
        self.version_registry = ModelVersionRegistry(registry_dir)
        self.min_feedback_threshold = min_feedback_threshold

    def should_retrain(self) -> bool:
        feedback_count = self.feedback_store.get_feedback_count()
        uncertain_count = self.feedback_store.get_uncertain_count()
        total_new_data = feedback_count + uncertain_count
        return total_new_data >= self.min_feedback_threshold

    def prepare_retraining_pool(self) -> list[dict]:
        feedback_records = self.feedback_store.load_feedback_as_jsonl()
        uncertain_records = self.feedback_store.load_uncertain_as_jsonl()

        pool = []
        for fb in feedback_records:
            pool.append(
                {
                    "phrase": fb["phrase"],
                    "label": fb["corrected_label"],
                    "source": "user_correction",
                    "original_prediction": fb["predicted_label"],
                    "timestamp": fb["feedback_timestamp"],
                }
            )

        for un in uncertain_records:
            pool.append(
                {
                    "phrase": un["phrase"],
                    "label": un["predicted_label"],
                    "source": "uncertain_flagged",
                    "confidence": un["confidence"],
                    "timestamp": un["flagged_timestamp"],
                }
            )

        return pool

    def prepare_combined_training_data(
        self,
        original_train_path: str | Path,
        retraining_pool: list[dict],
    ) -> list[dict]:
        combined = []

        with open(original_train_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    record = json.loads(line)
                    combined.append(
                        {
                            "phrase": record.get("phrase"),
                            "label": record.get("label"),
                            "source": "original",
                        }
                    )

        combined.extend(retraining_pool)
        return combined

    def check_if_improved(
        self,
        new_val_f1: float,
        current_val_f1: float,
        improvement_threshold: float = 0.02,
    ) -> tuple[bool, float]:
        improvement = new_val_f1 - current_val_f1
        return improvement >= improvement_threshold, improvement
