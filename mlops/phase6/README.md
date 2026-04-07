# Phase 6 - Continuous Learning Loop

This phase implements a production-ready continuous learning system that captures user feedback, monitors model performance, and triggers retraining with improved data.

## Components

### schema.py

- `PredictionFeedback` - User correction to a model prediction
- `UncertainPrediction` - Low-confidence prediction flagged for review
- `LearningEvent` - Retraining event record
- `ModelVersion` - Tracked model version with metadata

### feedback_store.py

- `FeedbackStore` class:
  - `record_feedback()` - Store user corrections
  - `record_uncertain_prediction()` - Flag low-confidence predictions
  - `load_feedback_as_jsonl()` - Load accumulated feedback
  - `clear_feedback()` - Clear after processing

### drift_monitor.py

- `DriftMonitor` class:
  - `log_metrics_snapshot()` - Record prediction batch metrics
  - `detect_drift()` - Identify performance degradation
  - `get_active_alerts()` - Retrieve drift alerts

### model_versioning.py

- `ModelVersionRegistry` class:
  - `register_model()` - Track model version
  - `set_active_model()` - Promote/rollback versions
  - `list_versions()` - Version history

### retrainer.py

- `LearningRetrainer` class:
  - `should_retrain()` - Check if enough data accumulated
  - `prepare_retraining_pool()` - Combine feedback + uncertain predictions
  - `check_if_improved()` - Validate improvement

### learning_orchestrator.py

- `ContinuousLearningEngine` class:
  - Main orchestrator tying all components together
  - `record_prediction_feedback()` - User correction entry point
  - `flag_uncertain_prediction()` - Low-confidence flagging entry point
  - `log_prediction_batch()` - Batch metrics logging
  - `check_retraining_needed()` - Retraining decision
  - `register_new_model_version()` - New model registration
  - `get_learning_status()` - Full status report

## Run Demonstration

```bash
python mlops/phase6/run_phase6.py
```

Shows:

- Feedback collection from user corrections
- Uncertain prediction flagging
- Drift monitoring
- Model versioning
- Retraining pool preparation

## Run Tests

```bash
python -m pytest tests/mlops/test_phase6_learning.py -v
```

Tests:

- Engine initialization
- Feedback collection
- Uncertain prediction flagging
- Retraining threshold logic
- Model versioning
- Model promotion and rollback

## Integration into FastAPI

The learning engine can be integrated into `backend/main.py` to capture feedback:

```python
from mlops.phase6.learning_orchestrator import ContinuousLearningEngine

engine = ContinuousLearningEngine(base_dir="mlops/phase6/learning")

@router.post("/api/predict-with-feedback")
async def predict_with_feedback(request: PredictionRequest) -> PredictionResponse:
    # Get prediction from Phase 5
    response = inference_engine.predict(request)

    # Auto-flag uncertain predictions
    if response.confidence < 0.72:
        engine.flag_uncertain_prediction(
            phrase=request.phrase,
            predicted_label=response.label,
            confidence=response.confidence,
            all_scores=response.all_scores,
        )

    return response

@router.post("/api/feedback")
async def submit_feedback(phrase: str, predicted: str, corrected: str) -> dict:
    engine.record_prediction_feedback(
        phrase=phrase,
        predicted_label=predicted,
        predicted_confidence=0.65,  # from original prediction
        corrected_label=corrected,
    )
    return {"status": "feedback_recorded"}

@router.get("/api/learning-status")
async def get_learning_status() -> dict:
    return engine.get_learning_status()
```

## Data Flow

1. **Prediction** → Phase 5 inference engine predicts
2. **Uncertainty Check** → Flag if confidence < 0.72
3. **Batch Logging** → Log prediction metrics for drift
4. **Feedback Collection** → User corrects if needed
5. **Accumulation** → Store in feedback store
6. **Retraining Trigger** → When N=20 items accumulated
7. **Pool Preparation** → Combine original + feedback data
8. **Model Training** → Use Phase 2-4 pipelines
9. **Validation** → Ensure improvement over current
10. **Versioning** → Register new or rollback

## Key Features

- ✅ Persistent feedback storage (JSONL)
- ✅ Drift detection with alerting
- ✅ Model versioning with rollback
- ✅ Automatic retraining coordination
- ✅ Confidence-based uncertainty flagging
- ✅ Performance improvement validation

## Success Criteria (Phase 0)

- Macro F1 ≥ 0.93 on test set
- Outdoor recall ≥ 0.95
- Models retrain when 20+ new data items
- Drift alerts trigger on 5%+ confidence drop
