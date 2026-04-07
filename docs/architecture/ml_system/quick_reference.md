# ML System - Quick Reference Card

## 🚀 Quick Start (3 Steps)

```bash
# Step 1: Start using (in your code)
from ml_system.api import get_ml_system
ml = get_ml_system()

# Step 2: Train a model once (if current model is missing)
ml.train(
    "ml_system/data/datasets/train.jsonl",
    "ml_system/data/datasets/val.jsonl",
    "ml_system/data/datasets/test.jsonl",
    "ml_system/data/datasets/hardset.jsonl",
)

# Step 3: Predict
result = ml.predict("I take the bus")
```

---

## 📍 Main Entry Points

### Single API

```python
from ml_system.api import get_ml_system

ml = get_ml_system()  # Singleton, reuses same instance
```

### Key Methods

```python
ml.predict(phrase)                    # → {label, confidence, ...}
ml.submit_feedback(p, pred, conf, cor) # → {recorded, status}
ml.get_status()                       # → {feedback_count, should_retrain, ...}
ml.train(train_p, val_p, test_p, hard_p) # → {model, f1, version}
```

---

## ⚙️ Configuration

```python
from ml_system.config.settings import CONFIG

CONFIG.base_dir                          # Path to ml_system/
CONFIG.confidence_threshold              # 0.72 (fallback to Unclear)
CONFIG.min_feedback_for_retraining       # 20 items
CONFIG.temperature_scaling               # 0.50
CONFIG.labels                            # ["Indoor", "Outdoor", "Mixed", "Unclear"]
```

---

## 📂 Folder Structure

```
ml_system/
├── api.py                  ← USE THIS (main entry)
├── schemas.py              ← Data types
├── config/settings.py      ← All settings
│
├── training/               ← Model learning
│   ├── tokenizer.py
│   ├── models.py
│   └── trainer.py
│
├── inference/              ← Predictions
│   └── engine.py
│
└── learning/               ← Continuous improvement
    └── orchestrator.py
```

---

## 🔄 Workflows

### Making a Prediction

```python
from ml_system.api import get_ml_system

ml = get_ml_system()
result = ml.predict("I sit at my desk working")

# Result:
{
    "label": "Indoor",
    "confidence": 0.92,
    "rationale": "High confidence (0.92)",
    "model": "linear_softmax",
    "all_scores": {
        "Indoor": 0.92,
        "Outdoor": 0.03,
        "Mixed": 0.04,
        "Unclear": 0.01
    }
}

# If uncertain (confidence < 0.72):
# Auto-stored in ml_system/learning/feedback/uncertain.jsonl
```

### Submitting Feedback

```python
ml.submit_feedback(
    phrase="I sit at my desk working",
    predicted="Unclear",
    confidence=0.30,
    corrected="Indoor"
)

# Returns status
{
    "recorded": True,
    "feedback_count": 4,
    "uncertain_predictions": 12,
    "total_new_data": 16,
    "should_retrain": False,
    "message": "Thanks for the correction!"
}
```

### Checking Status

```python
status = ml.get_status()

# Returns all monitoring info
{
    "feedback_records": 4,              # Corrections from users
    "uncertain_predictions": 12,        # Auto-flagged predictions
    "total_new_data": 16,               # Combined total
    "should_retrain": False,            # (>= 20 items = True)
    "active_model_version": "v1",
    "active_model_test_f1": 0.8333,
}
```

### Training with Accumulated Data

```python
# When ready (>= 20 feedback items)
if ml.get_status()['should_retrain']:
    results = ml.train(
        train_path="ml_system/data/datasets/train.jsonl",
        val_path="ml_system/data/datasets/val.jsonl",
        test_path="ml_system/data/datasets/test.jsonl",
        hardset_path="ml_system/data/datasets/hardset.jsonl",
    )

    # Results
    {
        "champion_model": "linear_softmax",
        "val_f1": 1.0,
        "test_f1": 0.9167,
        "hardset_f1": 0.5833,
        "temperature": 0.50,
        "version": "v2",
        "model_path": "...",
        "promoted": True
    }

    # New model now active in ml_system/models/current/
```

---

## 📊 Data Types (Schemas)

```python
from ml_system.schemas import (
    PredictionRequest,           # Request to predict
    PredictionResponse,          # Prediction result
    PredictionFeedback,          # User correction
    UncertainPrediction,         # Auto-flagged predictions
    TrainingRecord,              # Training data point
    ModelVersion,                # Version info
    TrainingReport,              # Training metrics
)
```

---

## 🔧 Validation

```bash
# Validate structure is correct
python ml_system/validate_structure.py

# Expected output:
# ✅ Directories:      OK
# ✅ Python modules:   OK
# ✅ API entry point:  OK
# ✅ Configuration:    OK
```

---

## 📚 Documentation

| Document                                                                    | Purpose           |
| --------------------------------------------------------------------------- | ----------------- |
| [overview.md](overview.md)                                                  | Full architecture |
| [integration.md](integration.md)                                            | Step-by-step      |
| [ml_system/validate_structure.py](../../../ml_system/validate_structure.py) | Verification      |

---

## 🐛 Troubleshooting

### "No module named 'ml_system'"

```bash
cd e:\Java\Project\Project Ai
python -c "from ml_system.api import get_ml_system; print('OK')"
```

### "No trained models found"

```bash
# Train directly in the unified system
python -c "from ml_system.api import get_ml_system; ml = get_ml_system(); ml.train('ml_system/data/datasets/train.jsonl','ml_system/data/datasets/val.jsonl','ml_system/data/datasets/test.jsonl','ml_system/data/datasets/hardset.jsonl')"
```

### All predictions return "Unclear"

This is expected! Reasons:

- Confidence threshold = 0.72 (prevents weak predictions)
- Small dataset (low confidence scores)
- Provide corrections to improve

### Models not training

Make sure data files exist:

```
ml_system/data/datasets/
├── train.jsonl
├── val.jsonl
├── test.jsonl
└── hardset.jsonl
```

---

## 💡 Tips & Tricks

### Always get singleton

```python
from ml_system.api import get_ml_system

ml = get_ml_system()  # Same instance every time
ml2 = get_ml_system()
assert ml is ml2  # True!
```

### Check exact threshold

```python
from ml_system.config.settings import CONFIG
print(CONFIG.confidence_threshold)  # 0.72
```

### Monitor learning progress

```python
status = ml.get_status()

if status['should_retrain']:
    print("Ready to retrain!")
    print(f"Items: {status['total_new_data']}/20")
```

### Batch predictions

```python
phrases = ["...", "...", "..."]
for phrase in phrases:
    result = ml.predict(phrase)
    print(f"{phrase}: {result['label']}")
```

---

## 🎯 Common Tasks

### Task: Make Single Prediction

```python
from ml_system.api import get_ml_system
ml = get_ml_system()
print(ml.predict("I take the bus"))
```

### Task: Record User Correction

```python
ml.submit_feedback("I take the bus", "Unclear", 0.30, "Outdoor")
```

### Task: Check Learning Status

```python
status = ml.get_status()
print(f"Can retrain? {status['should_retrain']}")
```

### Task: Train New Model

```python
if ml.get_status()['should_retrain']:
    ml.train(
        "ml_system/data/datasets/train.jsonl",
        "ml_system/data/datasets/val.jsonl",
        "ml_system/data/datasets/test.jsonl",
        "ml_system/data/datasets/hardset.jsonl",
    )
```

### Task: Add to FastAPI

```python
from ml_system.api import get_ml_system
from fastapi import APIRouter

router = APIRouter()
ml = get_ml_system()

@router.post("/predict")
def predict(phrase: str):
    return ml.predict(phrase)

@router.post("/feedback")
def feedback(phrase: str, label: str, corrected: str):
    return ml.submit_feedback(phrase, label, 0.5, corrected)
```

---

## ✅ Validation Checklist

Before deploying, verify:

- [ ] Trained models copied to `ml_system/models/current/`
- [ ] `ml_system/validate_structure.py` passes
- [ ] Can import: `from ml_system.api import get_ml_system`
- [ ] Can make prediction: `ml.predict("test")`
- [ ] Backend updated to use new API
- [ ] Frontend calls new `/api/predict` endpoint
- [ ] Feedback loop tested (submit corrections)

---

## 📞 Quick Links

- **Start Here:** [ml_system/api.py](../../../ml_system/api.py)
- **Learn More:** [overview.md](overview.md)
- **Integration:** [integration.md](integration.md)
- **Validation:** `python ml_system/validate_structure.py`
- **Architecture Diagram:** [docs/architecture/system_design.md](../system_design.md)

---

**Status:** ✅ Ready to use! Copy models, follow 3-step integration, and start predicting.
