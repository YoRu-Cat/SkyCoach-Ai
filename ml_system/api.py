"""
Unified ML System API
Provides clean interface to all ML functionality
"""

from __future__ import annotations

from pathlib import Path
from ml_system.config.settings import CONFIG
from ml_system.schemas import PredictionRequest
from ml_system.inference.engine import InferenceEngine
from ml_system.learning.orchestrator import LearningOrchestrator
from ml_system.training.trainer import Trainer
from ml_system.pipelines.ingestion.pipeline import IngestionConfig, IngestionPipeline
from ml_system.pipelines.quality.pipeline import QualityConfig, QualityPipeline
from ml_system.pipelines.annotation.workflow import AnnotationConfig, AnnotationWorkflow


class MLSystem:
    """Complete ML system interface."""

    def __init__(self):
        self.inference = None
        self.learning = LearningOrchestrator()
        self._ensure_models_exist()

    def _ensure_models_exist(self):
        """Load inference engine, trigger training if needed."""
        current_dir = CONFIG.get_current_model_path()

        model_exists = (current_dir / "model.json").exists()
        tokenizer_exists = (current_dir / "tokenizer.json").exists()
        report_exists = (current_dir / "report.json").exists() or (current_dir / "training_report.json").exists()

        if model_exists and tokenizer_exists and report_exists:
            try:
                self.inference = InferenceEngine()
            except Exception as e:
                print(f"Warning: Could not load inference engine: {e}")
        else:
            print("⚠ No trained models found. Inference unavailable until training completes.")

    def predict(self, phrase: str) -> dict:
        """Make a prediction."""
        if self.inference is None:
            raise ValueError("Models not initialized. Run training first.")
        
        request = PredictionRequest(phrase=phrase)
        response = self.inference.predict(request)
        
        # Auto-flag uncertain predictions
        if response.confidence < CONFIG.confidence_threshold:
            self.learning.flag_uncertain(
                phrase=phrase,
                predicted=response.label,
                confidence=response.confidence,
                all_scores=response.all_scores,
            )
        
        ranked_scores = sorted(
            response.all_scores.items(),
            key=lambda item: item[1],
            reverse=True,
        )
        top_suggestions = [
            {"label": label, "confidence": score}
            for label, score in ranked_scores
            if label != "Unclear"
        ][:2]

        return {
            "label": response.label,
            "confidence": response.confidence,
            "rationale": response.rationale,
            "model": response.model,
            "all_scores": response.all_scores,
            "suggestions": top_suggestions,
        }

    def submit_feedback(self, phrase: str, predicted: str, confidence: float, corrected: str) -> dict:
        """Submit user correction."""
        self.learning.record_feedback(phrase, predicted, confidence, corrected)
        status = self.learning.get_status()
        
        return {
            "status": "feedback_recorded",
            "total_feedback": status["feedback_records"],
            "should_retrain": status["should_retrain"],
        }

    def get_status(self) -> dict:
        """Get system status."""
        return self.learning.get_status()

    def get_retraining_pool(self) -> list[dict]:
        """Get prepared retraining data."""
        return self.learning.get_retraining_pool()

    def train(self, train_path: str | Path, val_path: str | Path, 
              test_path: str | Path, hardset_path: str | Path) -> dict:
        """Train models."""
        output_dir = CONFIG.get_current_model_path()
        output_dir.mkdir(parents=True, exist_ok=True)
        
        trainer = Trainer(train_path, val_path, test_path, hardset_path, output_dir)
        results = trainer.train()
        
        # Reload inference engine
        self.inference = InferenceEngine()
        
        # Register version
        self.learning.register_version(
            version_id=f"v{len(self.learning.version_registry.list_versions()) + 1}",
            model_path=str(output_dir / "model.json"),
            tokenizer_path=str(output_dir / "tokenizer.json"),
            training_size=512,  # From dataset
            val_f1=results["val_f1"],
            test_f1=results["test_f1"],
            hardset_f1=results["hardset_f1"],
        )
        
        # Promote to active
        self.learning.promote_version(f"v{len(self.learning.version_registry.list_versions())}")
        
        return results

    def run_ingestion(self, rows: list[dict], output_path: str | Path) -> dict:
        pipeline = IngestionPipeline(IngestionConfig(output_jsonl_path=str(output_path)))
        report = pipeline.run(rows)
        return {
            "total_rows": report.total_rows,
            "valid_rows": report.valid_rows,
            "invalid_rows": report.invalid_rows,
            "deduped_rows": report.deduped_rows,
            "written_rows": report.written_rows,
            "output_path": report.output_path,
        }

    def run_quality(self, rows: list[dict], output_path: str | Path) -> dict:
        pipeline = QualityPipeline(QualityConfig(output_jsonl_path=str(output_path)))
        report = pipeline.run(rows)
        return {
            "total_rows": report.total_rows,
            "valid_rows": report.valid_rows,
            "invalid_rows": report.invalid_rows,
            "noise_removed": report.noise_removed,
            "deduped_rows": report.deduped_rows,
            "balanced_rows": report.balanced_rows,
            "written_rows": report.written_rows,
            "label_counts": report.label_counts,
            "split_counts": report.split_counts,
            "output_path": report.output_path,
        }

    def run_annotation(
        self,
        rows_a: list[dict],
        rows_b: list[dict],
        merged_output_path: str | Path,
        golden_output_path: str | Path,
    ) -> dict:
        workflow = AnnotationWorkflow()
        report = workflow.run(
            rows_a=rows_a,
            rows_b=rows_b,
            config=AnnotationConfig(
                merged_output_path=str(merged_output_path),
                golden_output_path=str(golden_output_path),
            ),
        )
        return {
            "total_rows_a": report.total_rows_a,
            "total_rows_b": report.total_rows_b,
            "valid_pairs": report.valid_pairs,
            "auto_agreements": report.auto_agreements,
            "resolved_conflicts": report.resolved_conflicts,
            "unresolved_conflicts": report.unresolved_conflicts,
            "frozen_golden_rows": report.frozen_golden_rows,
            "merged_output_path": report.merged_output_path,
            "golden_output_path": report.golden_output_path,
        }


# Global instance
_ml_system = None


def get_ml_system() -> MLSystem:
    """Get or create ML system instance."""
    global _ml_system
    if _ml_system is None:
        _ml_system = MLSystem()
    return _ml_system
