from __future__ import annotations

import json
from pathlib import Path

from mlops.phase5.inference.schema import PredictionRequest
from mlops.phase5.inference.inference import PredictionEngine


def test_phase5_inference():
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

    test_cases = [
        "I take the bus to work every morning",
        "Let me check if the AC is working",
        "I am going to the office",
        "The gym is closed today",
    ]

    for phrase in test_cases:
        request = PredictionRequest(phrase=phrase)
        response = engine.predict(request)
        assert response.label in ["Indoor", "Outdoor", "Mixed", "Unclear"]
        assert 0.0 <= response.confidence <= 1.0
        assert len(response.all_scores) > 0
        print(f"✓ {phrase[:40]:40s} → {response.label:8s} ({response.confidence:.2f})")

    print(f"\n✓ All {len(test_cases)} inference tests passed!")
