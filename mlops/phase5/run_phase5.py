#!/usr/bin/env python
"""
Phase 5: Backend Inference Integration

This phase loads trained models from Phase 4 and sets up the inference engine
for real-time predictions.

Run with: python mlops/phase5/run_phase5.py
"""

from __future__ import annotations

from pathlib import Path
import sys
import subprocess
import json

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from mlops.phase5.inference.schema import PredictionRequest
from mlops.phase5.inference.inference import PredictionEngine


def ensure_phase4_artifacts():
    """Ensure Phase 4 artifacts exist by running Phase 4 training if needed."""
    artifacts_dir = Path("mlops/phase5/artifacts")
    tokenizer_path = artifacts_dir / "phase4_tokenizer.json"
    model_path = artifacts_dir / "phase4_champion_model.json"
    report_path = artifacts_dir / "phase4_training_report.json"

    if all([tokenizer_path.exists(), model_path.exists(), report_path.exists()]):
        print("✓ Phase 4 artifacts found in mlops/phase5/artifacts/")
        return artifacts_dir

    print("⚠ Phase 4 artifacts not found. Running Phase 4 training...")
    result = subprocess.run(
        [sys.executable, "mlops/phase4/run_training.py"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print(f"✗ Phase 4 training failed:\n{result.stderr}")
        sys.exit(1)

    print("✓ Phase 4 training complete")

    phase4_artifacts = Path("mlops/phase4/artifacts")
    if not phase4_artifacts.exists():
        print("✗ Phase 4 artifacts directory not found")
        sys.exit(1)

    artifacts_dir.mkdir(parents=True, exist_ok=True)

    for file in ["phase4_tokenizer.json", "phase4_champion_model.json", "phase4_training_report.json"]:
        src = phase4_artifacts / file
        dst = artifacts_dir / file
        if src.exists():
            dst.write_text(src.read_text())
        else:
            print(f"✗ Missing artifact: {file}")
            sys.exit(1)

    print(f"✓ Phase 4 artifacts copied to {artifacts_dir}")
    return artifacts_dir


def run_phase5():
    artifacts_dir = ensure_phase4_artifacts()

    print("\n--- Phase 5: Backend Inference Integration ---\n")

    engine = PredictionEngine(
        tokenizer_path=artifacts_dir / "phase4_tokenizer.json",
        model_path=artifacts_dir / "phase4_champion_model.json",
        report_path=artifacts_dir / "phase4_training_report.json",
        min_confidence=0.72,
    )

    report = engine.report
    print(f"Champion Model: {report['champion_model']}")
    print(f"Labels: {', '.join(report['labels'])}")
    print(f"Temperature: {report['temperature']:.2f}")
    print(f"Test F1: {report['test']['macro_f1']:.4f}")
    print(f"Validation F1: {report['val']['macro_f1']:.4f}\n")

    test_phrases = [
        "I take the bus to work every morning",
        "Let me check if the AC is working",
        "I will drive to the gym",
        "The meeting is at home",
        "Going outside for a walk",
    ]

    print("--- Sample Predictions ---\n")
    for phrase in test_phrases:
        request = PredictionRequest(phrase=phrase)
        response = engine.predict(request)
        print(f"Phrase: {phrase}")
        print(f"  Label: {response.label}")
        print(f"  Confidence: {response.confidence:.2f}")
        print(f"  Rationale: {response.rationale}")
        print(f"  All Scores: {', '.join([f'{k}={v:.2f}' for k, v in response.all_scores.items()])}\n")

    print("✓ Phase 5 inference engine validated successfully!")


if __name__ == "__main__":
    run_phase5()
