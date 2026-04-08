# ML System Overview

## Purpose

`ml_system` is the unified runtime for training, inference, and continuous learning.

## Components

- `api.py`: singleton entry point (`get_ml_system()`)
- `training/`: tokenizer, models, trainer
- `inference/`: prediction engine
- `learning/`: feedback ingestion and retraining orchestration
- `config/settings.py`: central config values

## Active Runtime Facts

- Confidence threshold: 0.62
- Temperature scaling: 0.50
- Labels: Indoor, Outdoor, Mixed, Unclear

## Typical Prediction Flow

1. Receive phrase.
2. Tokenize and score classes.
3. Apply temperature scaling.
4. Apply confidence threshold.
5. Return label plus `all_scores` and optional suggestions.

## Typical Learning Flow

1. Record user feedback from `/api/feedback`.
2. Track uncertain predictions.
3. Trigger retraining once minimum feedback threshold is reached.
4. Promote improved model artifact to current version.
