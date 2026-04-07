# Phase 5 - Backend Inference Integration

This phase loads trained models from Phase 4 and provides a production-ready inference engine for real-time predictions.

## Components

### model_loader.py
- `ScratchTokenizer.from_dict()` - Reconstructs tokenizer from JSON
- `ScratchNaiveBayes.from_dict()` - Reconstructs NB model from JSON
- `ScratchLinearSoftmax.from_dict()` - Reconstructs linear softmax model from JSON
- Load functions for tokenizer, model, and report

### inference.py
- `PredictionEngine` class that:
  - Loads Phase 4 artifacts (tokenizer, model, report)
  - Applies temperature calibration
  - Enforces confidence threshold (min_confidence=0.72 from Phase 0)
  - Returns "Unclear" if below threshold
  - Provides all prediction scores for transparency

### schema.py
- `PredictionRequest` - Input: phrase to classify
- `PredictionResponse` - Output: label, confidence, rationale, model name, all scores

## Run Inference

```bash
python mlops/phase5/run_phase5.py
```

This will:
1. Check for Phase 4 artifacts in `mlops/phase5/artifacts/`
2. If missing, run Phase 4 training to generate them
3. Load the trained model and tokenizer
4. Make sample predictions on test phrases
5. Display results with confidence scores

## Run Tests

```bash
python -m pytest tests/mlops/test_phase5_inference.py -v
```

Tests:
- `test_phase5_inference_engine_loads()` - Verify artifacts load correctly
- `test_phase5_inference_prediction()` - Verify predictions work

## API Integration

The `PredictionEngine` is ready to be integrated into `backend/main.py` via FastAPI endpoint `/predict`.

Example usage:
```python
from mlops.phase5.inference.inference import PredictionEngine
from mlops.phase5.inference.schema import PredictionRequest

engine = PredictionEngine(
    tokenizer_path="mlops/phase5/artifacts/phase4_tokenizer.json",
    model_path="mlops/phase5/artifacts/phase4_champion_model.json",
    report_path="mlops/phase5/artifacts/phase4_training_report.json",
    min_confidence=0.72,
)

request = PredictionRequest(phrase="I take the bus to work")
response = engine.predict(request)
# response.label, response.confidence, response.all_scores
```

## Phase 0 Policy Compliance

- Min confidence threshold: 0.72 (from Phase 0 release gates)
- Fallback label: "Unclear" when confidence < threshold
- Temperature scaling: Applied from Phase 4 calibration
- Labels: Indoor, Outdoor, Mixed, Unclear (from Phase 0 taxonomy)
