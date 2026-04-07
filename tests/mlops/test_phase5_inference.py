from __future__ import annotations

import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from mlops.phase5.inference.schema import PredictionRequest
from mlops.phase5.inference.inference import PredictionEngine


def test_phase5_inference_engine_loads():
    """Test that the inference engine can load Phase 4 artifacts."""
    artifacts_dir = Path("mlops/phase5/artifacts")
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    tokenizer_path = artifacts_dir / "phase4_tokenizer.json"
    model_path = artifacts_dir / "phase4_champion_model.json"
    report_path = artifacts_dir / "phase4_training_report.json"

    if not all([tokenizer_path.exists(), model_path.exists(), report_path.exists()]):
        raise FileNotFoundError(f"Phase 4 artifacts missing in {artifacts_dir}")

    engine = PredictionEngine(
        tokenizer_path=tokenizer_path,
        model_path=model_path,
        report_path=report_path,
        min_confidence=0.72,
    )

    assert engine.tokenizer is not None
    assert engine.model is not None
    assert len(engine.labels) > 0
    assert engine.temperature > 0


def test_phase5_inference_prediction():
    """Test that predictions work correctly."""
    artifacts_dir = Path("mlops/phase5/artifacts")
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    tokenizer_path = artifacts_dir / "phase4_tokenizer.json"
    model_path = artifacts_dir / "phase4_champion_model.json"
    report_path = artifacts_dir / "phase4_training_report.json"

    if not all([tokenizer_path.exists(), model_path.exists(), report_path.exists()]):
        raise FileNotFoundError(f"Phase 4 artifacts missing in {artifacts_dir}")

    engine = PredictionEngine(
        tokenizer_path=tokenizer_path,
        model_path=model_path,
        report_path=report_path,
        min_confidence=0.72,
    )

    request = PredictionRequest(phrase="I take the bus to work")
    response = engine.predict(request)

    assert response.label in ["Indoor", "Outdoor", "Mixed", "Unclear"]
    assert 0.0 <= response.confidence <= 1.0
    assert len(response.all_scores) > 0
    assert response.model == engine.model_name
