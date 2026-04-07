import tempfile

from ml_system.learning.orchestrator import ContinuousLearningEngine


def test_learning_engine_initialization():
    with tempfile.TemporaryDirectory() as tmpdir:
        engine = ContinuousLearningEngine(base_dir=tmpdir)

        assert engine.feedback_store is not None
        assert engine.drift_monitor is not None
        assert engine.version_registry is not None
        assert engine.retrainer is not None

        status = engine.get_learning_status()
        assert status["feedback_records"] == 0
        assert status["uncertain_predictions"] == 0
        assert status["should_retrain"] is False


def test_feedback_collection():
    with tempfile.TemporaryDirectory() as tmpdir:
        engine = ContinuousLearningEngine(base_dir=tmpdir)

        engine.record_prediction_feedback(
            phrase="I take the bus to work",
            predicted_label="Indoor",
            predicted_confidence=0.65,
            corrected_label="Outdoor",
        )

        status = engine.get_learning_status()
        assert status["feedback_records"] == 1
        assert status["total_new_data"] == 1


def test_uncertain_predictions():
    with tempfile.TemporaryDirectory() as tmpdir:
        engine = ContinuousLearningEngine(base_dir=tmpdir)

        engine.flag_uncertain_prediction(
            phrase="Going to the gym",
            predicted_label="Mixed",
            confidence=0.50,
            all_scores={"Indoor": 0.28, "Outdoor": 0.30, "Mixed": 0.25, "Unclear": 0.17},
        )

        status = engine.get_learning_status()
        assert status["uncertain_predictions"] == 1
        assert status["total_new_data"] == 1


def test_retraining_threshold():
    with tempfile.TemporaryDirectory() as tmpdir:
        engine = ContinuousLearningEngine(base_dir=tmpdir, min_retraining_threshold=5)

        for i in range(4):
            engine.record_prediction_feedback(
                phrase=f"Activity {i}",
                predicted_label="Outdoor",
                predicted_confidence=0.60 + i * 0.05,
                corrected_label="Indoor",
            )

        should_retrain, total = engine.check_retraining_needed()
        assert should_retrain is False
        assert total == 4

        engine.record_prediction_feedback(
            phrase="Activity 5",
            predicted_label="Indoor",
            predicted_confidence=0.50,
            corrected_label="Outdoor",
        )

        should_retrain, total = engine.check_retraining_needed()
        assert should_retrain is True
        assert total == 5


def test_model_versioning_and_promotion():
    with tempfile.TemporaryDirectory() as tmpdir:
        engine = ContinuousLearningEngine(base_dir=tmpdir)

        engine.register_new_model_version(
            version_id="v1",
            model_path="path/v1.json",
            tokenizer_path="path/v1_tok.json",
            training_data_size=1000,
            val_macro_f1=0.90,
            test_macro_f1=0.85,
            hardset_macro_f1=0.50,
            reason="initial_training",
        )

        versions = engine.version_registry.list_versions()
        assert len(versions) == 1
        assert versions[0]["version_id"] == "v1"

        engine.promote_model_version("v1")
        active = engine.version_registry.get_active_model()
        assert active["version_id"] == "v1"
        assert active["is_active"] is True
