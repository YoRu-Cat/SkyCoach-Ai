# Phase 1 - Data Ingestion Pipeline

This phase implements only ingestion foundations:

- Source adapters for open/licensed data inputs
- Schema validation for raw records
- Dedupe hashing by normalized phrase text
- Source metadata capture
- Smoke tests

## Run smoke ingestion

```bash
python mlops/phase1/run_ingestion.py
```

## Run tests

```bash
python -m pytest tests/mlops/test_phase1_ingestion.py -q
```
