# Phase 3 - Annotation Workflow

This phase adds annotation operations for high-quality supervised training data.

Implemented:

- Labeling guideline v1
- Double-annotation merge workflow
- Conflict resolution rules
- Golden test set freeze utility

## Run sample annotation workflow

```bash
python mlops/phase3/run_annotation.py
```

## Run tests

```bash
python -m pytest tests/mlops/test_phase3_annotation.py -q
```
