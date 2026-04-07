# Phase 2 - Data Quality Pipeline

This phase cleans and balances labeled phrase data produced by ingestion.

Implemented:

- Text normalization
- Near-duplicate detection
- Noise/profanity filtering
- Balanced sampling per label
- Deterministic split generation

## Run sample quality job

```bash
python mlops/phase2/run_quality.py
```

## Run tests

```bash
python -m pytest tests/mlops/test_phase2_quality.py -q
```
