"""
Unified Data Schemas for all ML Pipeline Components
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


# ============================================================================
# DATA PIPELINE SCHEMAS
# ============================================================================

@dataclass(frozen=True)
class RawPhraseRecord:
    """Raw phrase from ingestion."""
    phrase: str
    source: str
    original_id: Optional[str] = None


@dataclass(frozen=True)
class QualityRecord:
    """Phrase after quality checks."""
    phrase: str
    label: Optional[str] = None
    is_noise: bool = False
    is_duplicate: bool = False


@dataclass(frozen=True)
class AnnotatedRecord:
    """Phrase with annotation."""
    phrase: str
    label: str
    annotator: str
    confidence: float


@dataclass(frozen=True)
class TrainingRecord:
    """Final training data record."""
    phrase: str
    label: str
    split: str  # "train", "val", "test", "hardset"


# ============================================================================
# PREDICTION AND FEEDBACK SCHEMAS
# ============================================================================

@dataclass(frozen=True)
class PredictionRequest:
    """Input for prediction."""
    phrase: str


@dataclass(frozen=True)
class PredictionResponse:
    """Output from prediction."""
    label: str
    confidence: float
    rationale: str
    model: str
    all_scores: dict[str, float]


@dataclass(frozen=True)
class PredictionFeedback:
    """User correction to a prediction."""
    phrase: str
    predicted_label: str
    predicted_confidence: float
    corrected_label: str
    feedback_timestamp: str
    feedback_source: str = "user"


@dataclass(frozen=True)
class UncertainPrediction:
    """Low-confidence prediction flagged for review."""
    phrase: str
    predicted_label: str
    confidence: float
    all_scores: dict[str, float]
    flagged_timestamp: str
    confidence_threshold: float = 0.72


# ============================================================================
# MODEL and VERSIONING SCHEMAS
# ============================================================================

@dataclass(frozen=True)
class ModelVersion:
    """Tracked model version."""
    version_id: str
    model_path: str
    tokenizer_path: str
    created_at: str
    training_data_size: int
    val_macro_f1: float
    test_macro_f1: float
    hardset_macro_f1: float
    parent_version: Optional[str] = None
    is_active: bool = False
    reason: str = ""


@dataclass(frozen=True)
class TrainingReport:
    """Report from training run."""
    champion_model: str
    val_macro_f1: float
    val_accuracy: float
    test_macro_f1: float
    test_accuracy: float
    hardset_macro_f1: float
    hardset_accuracy: float
    temperature: float
    report_path: str
    tokenizer_path: str
    model_path: str


# ============================================================================
# MONITORING SCHEMAS
# ============================================================================

@dataclass(frozen=True)
class DriftMetrics:
    """Performance snapshot for drift detection."""
    timestamp: str
    prediction_count: int
    avg_confidence: float
    label_distribution: dict[str, int]
    uncertain_count: int
