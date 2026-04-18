# Project Part 1 Write-up (SkyCoach AI)

## Dataset Used

This submission uses the SkyCoach activity-intent dataset bundled with the project. The notebook loads the four JSONL splits from `data/datasets`:

- `train.jsonl`
- `val.jsonl`
- `test.jsonl`
- `hardset.jsonl`

The task is text classification for weather-aware activity planning.

## Dataset Features

The raw dataset contains:

- `phrase` - text activity phrase
- `label` - categorical target label

Labels used in the project:

- Indoor
- Outdoor
- Mixed
- Unclear

The notebook also creates simple engineered features for exploration:

- `phrase_length`
- `token_count`
- `split`

## Two Models in the Project

### Model 1: TF-IDF + Multinomial Naive Bayes

This is the model demonstrated in the notebook.

Why it is suitable:

- It is strong for short text classification.
- It works well with sparse TF-IDF vectors.
- It is fast, simple, and easy to explain.

### Model 2: Ensemble Classical ML Pipeline

The broader SkyCoach project also includes a classical ML ensemble path in `services/task_classifier_ml.py`.

Why it is suitable:

- It can compare multiple learners.
- It captures different decision boundaries.
- It is useful as a stronger second-stage model for later project phases.

## Submission Contents

This package includes:

- A documented Jupyter notebook
- A write-up with dataset, model, and suitability details
- The dataset splits needed to run the notebook independently

## Notes

- This bundle is separated from the main application build.
- The notebook is self-contained and uses bundled relative dataset paths.
