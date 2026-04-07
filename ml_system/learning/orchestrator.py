from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from ml_system.config.settings import CONFIG
from ml_system.schemas import PredictionFeedback, UncertainPrediction

from .drift_monitor import DriftMonitor
from .feedback_store import FeedbackStore
from .model_versioning import ModelVersionRegistry
from .retrainer import LearningRetrainer


class ContinuousLearningEngine:
    """Orchestrate feedback capture, drift monitoring, and model version lifecycle."""

    def __init__(
        self,
        base_dir: str | Path | None = None,
        min_retraining_threshold: int | None = None,
    ) -> None:
        self.base_dir = Path(base_dir or CONFIG.learning_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

        self.feedback_store = FeedbackStore(self.base_dir / "feedback")
        self.drift_monitor = DriftMonitor(self.base_dir / "monitoring")
        self.version_registry = ModelVersionRegistry(self.base_dir / "versions")
        self.retrainer = LearningRetrainer(
            feedback_dir=self.base_dir / "feedback",
            registry_dir=self.base_dir / "versions",
            min_feedback_threshold=min_retraining_threshold or CONFIG.min_feedback_for_retraining,
        )
        self.events_file = self.base_dir / "learning_events.jsonl"

    def record_prediction_feedback(
        self,
        phrase: str,
        predicted_label: str,
        predicted_confidence: float,
        corrected_label: str,
        source: str = "user",
    ) -> None:
        feedback = PredictionFeedback(
            phrase=phrase,
            predicted_label=predicted_label,
            predicted_confidence=predicted_confidence,
            corrected_label=corrected_label,
            feedback_timestamp=datetime.utcnow().isoformat() + "Z",
            feedback_source=source,
        )
        self.feedback_store.record_feedback(feedback)

    def flag_uncertain_prediction(
        self,
        phrase: str,
        predicted_label: str,
        confidence: float,
        all_scores: dict[str, float],
        confidence_threshold: float | None = None,
    ) -> None:
        threshold = confidence_threshold or CONFIG.confidence_threshold
        if confidence < threshold:
            pred = UncertainPrediction(
                phrase=phrase,
                predicted_label=predicted_label,
                confidence=confidence,
                all_scores=all_scores,
                flagged_timestamp=datetime.utcnow().isoformat() + "Z",
                confidence_threshold=threshold,
            )
            self.feedback_store.record_uncertain_prediction(pred)

    def log_prediction_batch(self, predictions: list[dict]) -> None:
        if not predictions:
            return

        avg_confidence = sum(p.get("confidence", 0.0) for p in predictions) / len(predictions)
        label_dist: dict[str, int] = {}
        uncertain_count = 0

        for pred in predictions:
            label = pred.get("label", "Unknown")
            label_dist[label] = label_dist.get(label, 0) + 1
            if pred.get("confidence", 1.0) < CONFIG.confidence_threshold:
                uncertain_count += 1

        self.drift_monitor.log_metrics_snapshot(
            prediction_count=len(predictions),
            avg_confidence=avg_confidence,
            label_distribution=label_dist,
            uncertain_count=uncertain_count,
        )
        self.drift_monitor.detect_drift(CONFIG.drift_confidence_drop_threshold)

    def check_retraining_needed(self) -> tuple[bool, int]:
        should_retrain = self.retrainer.should_retrain()
        feedback_count = self.feedback_store.get_feedback_count()
        uncertain_count = self.feedback_store.get_uncertain_count()
        total = feedback_count + uncertain_count
        return should_retrain, total

    def get_retraining_pool(self) -> list[dict]:
        return self.retrainer.prepare_retraining_pool()

    def register_new_model_version(
        self,
        version_id: str,
        model_path: str,
        tokenizer_path: str,
        training_data_size: int,
        val_macro_f1: float,
        test_macro_f1: float,
        hardset_macro_f1: float,
        reason: str = "retraining_cycle",
    ) -> None:
        active_model = self.version_registry.get_active_model()
        parent_version = active_model.get("version_id") if active_model else None

        self.version_registry.register_model(
            version_id=version_id,
            model_path=model_path,
            tokenizer_path=tokenizer_path,
            training_data_size=training_data_size,
            val_macro_f1=val_macro_f1,
            test_macro_f1=test_macro_f1,
            hardset_macro_f1=hardset_macro_f1,
            parent_version=parent_version,
            reason=reason,
        )

    def promote_model_version(self, version_id: str) -> None:
        event = {
            "event_id": f"promote_{version_id}_{datetime.utcnow().timestamp()}",
            "event_type": "model_promotion",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "description": f"Promoted model version {version_id} to active",
            "version_id": version_id,
        }
        self.version_registry.set_active_model(version_id)
        self._log_event(event)

    def get_learning_status(self) -> dict:
        feedback_count = self.feedback_store.get_feedback_count()
        uncertain_count = self.feedback_store.get_uncertain_count()
        should_retrain, total_new_data = self.check_retraining_needed()
        active_model = self.version_registry.get_active_model()
        drift_alerts = self.drift_monitor.get_active_alerts()

        return {
            "feedback_records": feedback_count,
            "uncertain_predictions": uncertain_count,
            "total_new_data": total_new_data,
            "should_retrain": should_retrain,
            "active_model_version": active_model.get("version_id") if active_model else None,
            "active_model_test_f1": active_model.get("test_macro_f1") if active_model else None,
            "model_versions_count": len(self.version_registry.list_versions()),
            "drift_alert_count": len(drift_alerts),
            "recent_drift_alert": drift_alerts[-1] if drift_alerts else None,
        }

    def clear_processed_feedback(self) -> None:
        self.feedback_store.clear_feedback()
        self.feedback_store.clear_uncertain()

    def _log_event(self, event: dict) -> None:
        with self.events_file.open("a", encoding="utf-8") as f:
            f.write(json.dumps(event) + "\n")


class LearningOrchestrator(ContinuousLearningEngine):
    """Backward-compatible alias used by ml_system.api."""

    def record_feedback(self, phrase: str, predicted: str, confidence: float, corrected: str) -> None:
        self.record_prediction_feedback(phrase, predicted, confidence, corrected)

    def flag_uncertain(self, phrase: str, predicted: str, confidence: float, all_scores: dict[str, float]) -> None:
        self.flag_uncertain_prediction(phrase, predicted, confidence, all_scores)

    def get_status(self) -> dict:
        return self.get_learning_status()

    def register_version(
        self,
        version_id: str,
        model_path: str,
        tokenizer_path: str,
        training_size: int,
        val_f1: float,
        test_f1: float,
        hardset_f1: float,
    ) -> None:
        self.register_new_model_version(
            version_id=version_id,
            model_path=model_path,
            tokenizer_path=tokenizer_path,
            training_data_size=training_size,
            val_macro_f1=val_f1,
            test_macro_f1=test_f1,
            hardset_macro_f1=hardset_f1,
            reason="unified_training_cycle",
        )

    def promote_version(self, version_id: str) -> None:
        self.promote_model_version(version_id)
