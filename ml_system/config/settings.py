"""
ML System Configuration and Settings
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class MLSystemConfig:
    """Central configuration for the ML system."""
    
    base_dir: Path = Path("ml_system")
    data_dir: Path = Path("ml_system/data")
    models_dir: Path = Path("ml_system/models")
    training_dir: Path = Path("ml_system/training")
    inference_dir: Path = Path("ml_system/inference")
    learning_dir: Path = Path("ml_system/learning")
    pipelines_dir: Path = Path("ml_system/pipelines")
    policies_dir: Path = Path("ml_system/policies")
    
    tokenizer_max_vocab: int = 50000
    tokenizer_min_freq: int = 1
    
    epochs: int = 30
    learning_rate: float = 0.05
    l2_regularization: float = 1e-4
    laplace_alpha: float = 1.0
    linear_backend: str = "pytorch"
    linear_batch_size: int = 32
    
    confidence_threshold: float = 0.62
    min_confidence_floor: float = 0.55
    ambiguity_margin: float = 0.08
    temperature_scaling: float = 0.50
    
    min_feedback_for_retraining: int = 20
    improvement_threshold: float = 0.02
    drift_confidence_drop_threshold: float = 0.05
    
    labels: list[str] = None # type: ignore
    
    def __post_init__(self):
        if self.labels is None:
            self.labels = ["Indoor", "Outdoor", "Mixed", "Unclear"]

    def get_current_model_path(self) -> Path:
        return self.models_dir / "current"
    
    def get_version_dir(self) -> Path:
        return self.models_dir / "versions"


CONFIG = MLSystemConfig()
