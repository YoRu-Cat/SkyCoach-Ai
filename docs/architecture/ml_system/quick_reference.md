# ML System Quick Reference

## Init

```python
from ml_system.api import get_ml_system
ml = get_ml_system()
```

## Predict

```python
result = ml.predict("going to tobacco shop")
```

Common keys in result:

- `label`
- `confidence`
- `rationale`
- `model`
- `all_scores`
- `suggestions`

## Feedback

```python
ml.submit_feedback(
    phrase="going to tobacco shop",
    predicted="Unclear",
    confidence=0.45,
    corrected="Outdoor",
)
```

## Status

```python
status = ml.get_status()
```

## Config Values

- `CONFIG.confidence_threshold = 0.62`
- `CONFIG.temperature_scaling = 0.50`
- `CONFIG.min_feedback_for_retraining = 20`

## Train

```python
ml.train(
    "ml_system/data/datasets/train.jsonl",
    "ml_system/data/datasets/val.jsonl",
    "ml_system/data/datasets/test.jsonl",
    "ml_system/data/datasets/hardset.jsonl",
)
```
