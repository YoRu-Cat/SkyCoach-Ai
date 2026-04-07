#!/usr/bin/env python
"""
Phase 6: Continuous Learning Loop

This phase implements feedback collection, drift monitoring, and model retraining.

Run with: python mlops/phase6/run_phase6.py
"""

from __future__ import annotations

from pathlib import Path
import sys
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from mlops.phase6.learning_orchestrator import ContinuousLearningEngine


def simulate_production_usage():
    """Simulate a day of production predictions with some corrections."""
    print("\n--- Phase 6: Continuous Learning Loop Demonstration ---\n")

    engine = ContinuousLearningEngine(base_dir="mlops/phase6/learning")

    print("Step 1: Simulating production predictions with feedback loop")
    print("-" * 60)

    predictions = [
        {
            "phrase": "I take the bus to work every morning",
            "predicted": "Indoor",
            "confidence": 0.58,
            "user_corrected_to": "Outdoor",
        },
        {
            "phrase": "Let me check if the AC is working",
            "predicted": "Mixed",
            "confidence": 0.52,
            "user_corrected_to": "Indoor",
        },
        {
            "phrase": "I will drive to the gym",
            "predicted": "Indoor",
            "confidence": 0.62,
            "user_corrected_to": None,
        },
        {
            "phrase": "Going for a jog in the park",
            "predicted": "Mixed",
            "confidence": 0.48,
            "user_corrected_to": "Outdoor",
        },
        {
            "phrase": "Meeting at the coffee shop",
            "predicted": "Outdoor",
            "confidence": 0.41,
            "user_corrected_to": "Indoor",
        },
    ]

    for pred in predictions:
        engine.flag_uncertain_prediction(
            phrase=pred["phrase"],
            predicted_label=pred["predicted"],
            confidence=pred["confidence"],
            all_scores={
                "Indoor": 0.30,
                "Outdoor": 0.25,
                "Mixed": 0.20,
                "Unclear": 0.25,
            },
        )

        if pred["user_corrected_to"]:
            engine.record_prediction_feedback(
                phrase=pred["phrase"],
                predicted_label=pred["predicted"],
                predicted_confidence=pred["confidence"],
                corrected_label=pred["user_corrected_to"],
            )
            print(f"✓ Correction: {pred['phrase'][:35]:35s} → {pred['user_corrected_to']}")

    print("\nStep 2: Logging prediction batch for drift monitoring")
    print("-" * 60)

    batch = [
        {"label": label, "confidence": conf}
        for label, conf in zip(
            ["Indoor", "Outdoor", "Mixed", "Mixed", "Outdoor"],
            [0.58, 0.62, 0.52, 0.48, 0.41],
        )
    ]
    engine.log_prediction_batch(batch)
    print(f"✓ Logged {len(batch)} predictions")

    print("\nStep 3: Checking learning status")
    print("-" * 60)

    status = engine.get_learning_status()
    print(f"Feedback records: {status['feedback_records']}")
    print(f"Uncertain predictions: {status['uncertain_predictions']}")
    print(f"Total new data: {status['total_new_data']}")
    print(f"Should retrain: {status['should_retrain']}")
    print(f"Retraining threshold: 20 items")

    print("\nStep 4: Registering initial model version")
    print("-" * 60)

    engine.register_new_model_version(
        version_id="v1_initial",
        model_path="mlops/phase5/artifacts/phase4_champion_model.json",
        tokenizer_path="mlops/phase5/artifacts/phase4_tokenizer.json",
        training_data_size=1000,
        val_macro_f1=1.0,
        test_macro_f1=0.8333,
        hardset_macro_f1=0.4167,
        reason="initial_deployment",
    )

    engine.promote_model_version("v1_initial")
    print("✓ Model v1_initial registered and promoted to active")

    print("\nStep 5: Checking model versions")
    print("-" * 60)

    versions = engine.version_registry.list_versions()
    for v in versions:
        active_marker = " (ACTIVE)" if v["is_active"] else ""
        print(
            f"  {v['version_id']:20s} | "
            f"F1: {v.get('test_macro_f1', 0):.4f} | "
            f"Data: {v['training_data_size']:5d}{active_marker}"
        )

    print("\nStep 6: Showing retraining pool (prepared from feedback)")
    print("-" * 60)

    pool = engine.get_retraining_pool()
    if pool:
        for item in pool[:3]:
            print(
                f"  {item['phrase'][:35]:35s} → "
                f"{item['label']:10s} (source: {item['source']})"
            )
        if len(pool) > 3:
            print(f"  ... and {len(pool) - 3} more items")
    else:
        print("  (Empty - no feedback collected yet)")

    print("\nStep 7: Drift monitoring")
    print("-" * 60)

    alerts = engine.drift_monitor.get_active_alerts()
    if alerts:
        print(f"  Active alerts: {len(alerts)}")
        for alert in alerts[:2]:
            print(f"    - {alert.get('message')}")
    else:
        print("✓ No drift alerts (performance stable)")

    print("\n✓ Phase 6 demonstration complete!")
    print("\nKey takeaways:")
    print("  1. User corrections are captured for future retraining")
    print("  2. Uncertain predictions (< 0.72 confidence) are flagged")
    print("  3. Drift monitoring tracks model performance changes")
    print("  4. Model versions are tracked with rollback capability")
    print("  5. New data pool prepared for scheduled retraining")


if __name__ == "__main__":
    simulate_production_usage()
