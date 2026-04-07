# Phase 4 - Model Training (In-house)

This phase implements model training components built in-house (no outsourced model dependency).

Implemented:

- Tokenizer training from scratch
- Scratch Multinomial Naive Bayes classifier
- Scratch linear softmax classifier (SGD)
- Probability calibration (temperature scaling)
- Hard-set evaluation and champion model selection

## Run training

```bash
python mlops/phase4/run_training.py
```

## Run tests

```bash
python -m pytest tests/mlops/test_phase4_training.py -q
```
