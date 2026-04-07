from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class PredictionFeedback:
    """User correction to a model prediction."""
    phrase: str
    predicted_label: str
    predicted_confidence: float
    corrected_label: str
    feedback_timestamp: str
    feedback_source: str = "user"


@dataclass(frozen=True)
class UncertainPrediction:
    """Prediction flagged for review due to low confidence."""
    phrase: str
    predicted_label: str
    confidence: float
    all_scores: dict[str, float]
    flagged_timestamp: str
    confidence_threshold: float = 0.72


@dataclass(frozen=True)
class LearningEvent:
    """Record of a retraining event."""
    event_id: str
    event_type: str
    timestamp: str
    description: str
    feedback_count: int
    new_model_path: str | None = None
    performance_improvement: float | None = None
    was_rolled_back: bool = False


@dataclass(frozen=True)
class ModelVersion:
    """Tracked version of a trained model."""
    version_id: str
    model_path: str
    tokenizer_path: str
    created_at: str
    training_data_size: int
    val_macro_f1: float
    test_macro_f1: float
    hardset_macro_f1: float
    parent_version: str | None = None
    is_active: bool = False
    reason: str = ""
