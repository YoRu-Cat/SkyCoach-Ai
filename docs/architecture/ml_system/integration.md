# ML System Integration Guide

## Quick Start

The restructured `ml_system/` provides a production-ready, collaborative architecture that consolidates all ML functionality into a single unified API.

### Current Status

✅ All directories created and validated  
✅ All Python modules importable  
✅ All configuration centralized  
✅ API ready to use  
✅ End-to-end training, inference, and learning live in `ml_system/`

## 3-Step Integration

### Step 1: Train Inside ml_system

```bash
# Train directly via the unified API
python -c "from ml_system.api import get_ml_system; ml = get_ml_system(); ml.train('ml_system/data/datasets/train.jsonl','ml_system/data/datasets/val.jsonl','ml_system/data/datasets/test.jsonl','ml_system/data/datasets/hardset.jsonl')"
```

### Step 2: Update Backend

```python
# In backend/api/routes.py - use unified API

from ml_system.api import get_ml_system

ml_system = get_ml_system()

@router.post("/api/predict")
async def predict(request: dict):
    return ml_system.predict(request["phrase"])

@router.post("/api/feedback")
async def submit_feedback(request: dict):
    return ml_system.submit_feedback(...)

@router.get("/api/learning-status")
async def learning_status():
    return ml_system.get_status()
```

### Step 3: Validate Endpoints

1. POST `/predict`
2. POST `/feedback`
3. GET `/learning-status`

## Component Mapping

### Unified Component Layout

| Component  | Path                            | Purpose                        |
| ---------- | ------------------------------- | ------------------------------ |
| Policies   | ml_system/policies/             | Policy documents & gates       |
| Ingestion  | ml_system/pipelines/ingestion/  | Data ingestion & dedup         |
| Quality    | ml_system/pipelines/quality/    | Data quality & filtering       |
| Annotation | ml_system/pipelines/annotation/ | Labeling & conflict resolution |
| Training   | ml_system/training/             | Model training                 |
| Inference  | ml_system/inference/            | Predictions                    |
| Learning   | ml_system/learning/             | Continuous learning            |
| API        | ml_system/api.py                | Unified entry point            |
| Schemas    | ml_system/schemas.py            | Unified data types             |
| Config     | ml_system/config/               | Centralized settings           |

## API Usage

### Initialization

```python
from ml_system.api import get_ml_system

# Get singleton instance (reuses same object)
ml = get_ml_system()
```

### Making Predictions

```python
result = ml.predict("I take the bus to work")

# Returns:
{
    "label": "Outdoor",           # Classification
    "confidence": 0.87,           # 0-1 score
    "rationale": "...",           # Why this label
    "model": "linear_softmax",    # Model used
    "all_scores": {               # All class scores
        "Indoor": 0.05,
        "Outdoor": 0.87,
        "Mixed": 0.06,
        "Unclear": 0.02,
    }
}

# If confidence < 0.72:
{
    "label": "Unclear",
    "confidence": 0.30,
    "rationale": "Confidence 0.30 below threshold 0.72",
    "model": "linear_softmax",
    "all_scores": {...}
}

# Auto-flagged as uncertain & stored for potential retraining
```

### Feedback Collection

```python
# Record user correction
ml.submit_feedback(
    phrase="I take the bus to work",
    predicted="Unclear",
    confidence=0.30,
    corrected="Outdoor",
)

# Returns status update
{
    "recorded": True,
    "feedback_count": 4,
    "uncertain_count": 12,
    "total_new_data": 16,
    "should_retrain": False,
    "message": "Thanks for the correction!"
}
```

### Monitoring

```python
status = ml.get_status()

print(f"Feedback items: {status['feedback_records']}")
print(f"Uncertain preds: {status['uncertain_predictions']}")
print(f"Ready to retrain? {status['should_retrain']}")
print(f"Active model: {status['active_model_version']}")
print(f"Test F1 score: {status['active_model_test_f1']:.4f}")
```

### Retraining (When Ready)

```python
if ml.get_status()['should_retrain']:
    # Automatically combines feedback + uncertain predictions
    results = ml.train(
        train_path="ml_system/data/datasets/train.jsonl",
        val_path="ml_system/data/datasets/val.jsonl",
        test_path="ml_system/data/datasets/test.jsonl",
        hardset_path="ml_system/data/datasets/hardset.jsonl",
    )

    print(f"New model F1: {results['test_f1']:.4f}")
    print(f"Registered as: {results['version']}")
```

## Data Flow

### Training Path

```
ml_system/data/datasets/
├── train.jsonl        → Used for training
├── val.jsonl          → Used for champion selection
├── test.jsonl         → Used for final evaluation
└── hardset.jsonl      → Used for edge case evaluation

↓ (Trainer.train)

ml_system/training/
├── tokenizer.py       → Builds vocabulary
├── models.py          → Trains NaiveBayes & LinearSoftmax
└── trainer.py         → Orchestrates & calibrates

↓ (saves artifacts)

ml_system/models/versions/
├── v1/
│   ├── model.json
│   ├── tokenizer.json
│   └── report.json
└── versions.jsonl     → Metadata log

↓ (promotes to current)

ml_system/models/current/
├── model.json         → Active model
├── tokenizer.json     → Active tokenizer
└── report.json        → Performance metrics
```

### Prediction Path

```
Request: "I take the bus to work"
├→ ml_system/inference/engine.py loads from ml_system/models/current/
├→ Tokenizer.tokenize() preprocesses text
├→ Model.predict_proba() scores classes
├→ Temperature scaling (0.50)
├→ Check confidence vs 0.72 threshold
└→ Response with label, confidence, all_scores

If uncertain (conf < 0.72):
└→ Flag & store in ml_system/learning/feedback/uncertain.jsonl
```

### Feedback Path

```
User says: "That should be Outdoor, not Unclear"
├→ ml_system/learning/orchestrator.py records
├→ Store in ml_system/learning/feedback/feedback.jsonl
├→ Update counters (feedback_records, total_new_data)
├→ Check if total_new_data >= 20
└→ If yes: flag should_retrain = True

Next ml.train():
└→ Combines original data + feedback + uncertain → retraining pool
```

## Configuration

All settings in `ml_system/config/settings.py`:

```python
from ml_system.config.settings import CONFIG

# Paths
CONFIG.base_dir                          # ml_system/
CONFIG.data_dir                          # ml_system/data/
CONFIG.models_dir                        # ml_system/models/
CONFIG.learning_dir                      # ml_system/learning/

# Model parameters
CONFIG.tokenizer_max_vocab               # 5000
CONFIG.epochs                            # 30
CONFIG.learning_rate                     # 0.05

# Inference
CONFIG.confidence_threshold              # 0.72 → fallback to Unclear
CONFIG.temperature_scaling               # 0.50

# Learning
CONFIG.min_feedback_for_retraining       # 20 items
CONFIG.improvement_threshold             # Check if new F1 > old F1

# Labels
CONFIG.labels                            # ["Indoor", "Outdoor", "Mixed", "Unclear"]
```

## Folder Organization

```
ml_system/
├── api.py                          ← Start here (main entry point)
├── schemas.py                      ← Data types (used everywhere)
├── config/
│   └── settings.py                 ← All settings
│
├── training/                       ← Model learning
│   ├── tokenizer.py
│   ├── models.py
│   └── trainer.py
│
├── inference/                      ← Predictions
│   └── engine.py
│
├── learning/                       ← Continuous improvement
│   └── orchestrator.py
│       (+ feedback/ & versions/ dirs)
│
├── pipelines/                      ← Data processing (extensible)
│   ├── ingestion/
│   ├── quality/
│   └── annotation/
│
├── data/                           ← Managed by code
│   ├── raw/
│   ├── processed/
│   └── datasets/
│
├── models/                         ← Managed by code
│   ├── current/
│   └── versions/
│
├── policies/                       ← Reference docs
│   ├── label_policy.json
│   ├── release_gates.json
│   └── edge_case_policy.json
│
└── README.md                       ← Architecture docs
```

## Testing the Integration

After copying models to `ml_system/models/current/`:

```bash
# Test predictions work
python -c "
from ml_system.api import get_ml_system
ml = get_ml_system()
print(ml.predict('I take the bus'))
"

# Test feedback flow
python -c "
from ml_system.api import get_ml_system
ml = get_ml_system()
ml.submit_feedback('I take the bus', 'Unclear', 0.30, 'Outdoor')
print(ml.get_status())
"
```

## Next Steps

1. **Train initial model** via `ml_system.api.get_ml_system().train(...)`
2. **Update backend** endpoints to use new API
3. **Test predictions** manually
4. **Test feedback loop** by submitting corrections
5. **Monitor status** during learning phase
6. **Trigger retraining** when 20+ items accumulated

## FAQ

### Q: Will this break existing APIs?

**A:** No. `/predict`, `/feedback`, and `/learning-status` remain available via unified `ml_system` internals.

### Q: How do I import historical feedback data?

**A:** Append historical records into `ml_system/learning/feedback/feedback.jsonl` and `ml_system/learning/feedback/uncertain_predictions.jsonl`.

### Q: Can I run a phase-based pipeline too?

**A:** Not needed. The repository now uses only `ml_system`.

### Q: What if the new model performs worse?

**A:** All versions are saved in ml_system/models/versions/. Rollback via:

```python
ml.learning_orchestrator.promote_version('v1')
```

### Q: How do I add custom preprocessing?

**A:** Modify ml_system/training/tokenizer.py and retrain.

### Q: Can I use different models?

**A:** Yes, create new file in ml_system/training/models.py with same interface and update trainer.py to use it.

## Troubleshooting

### ❌ "No module named 'ml_system'"

```bash
# Make sure you're in the project root
cd e:\Java\Project\Project Ai
python -c "from ml_system.api import get_ml_system"
```

### ❌ "No trained models found"

```bash
# Train directly in ml_system
python -c "from ml_system.api import get_ml_system; ml = get_ml_system(); ml.train('ml_system/data/datasets/train.jsonl','ml_system/data/datasets/val.jsonl','ml_system/data/datasets/test.jsonl','ml_system/data/datasets/hardset.jsonl')"
```

### ❌ Predictions all return "Unclear"

This is expected! The system has safeguards:

- Confidence threshold = 0.72 (prevents uncertain predictions)
- Small training set may produce low confidence scores
- Temperature scaling applied (0.50)

Provide corrections via feedback to improve.

## Summary

The new `ml_system/` provides:

✅ **Simple API** - One entry point for all ML ops  
✅ **Centralized Config** - All settings in one place  
✅ **Clean Schemas** - Type-safe data structures  
✅ **Modular Components** - Easy to extend  
✅ **Production Ready** - Versioning, feedback, monitoring  
✅ **Team Friendly** - Clear folder structure, no silos

Start using it today by running the 3-step integration above!
