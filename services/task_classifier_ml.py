from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import re
from typing import Literal, cast

from sklearn.decomposition import TruncatedSVD
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.base import clone
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.tree import DecisionTreeClassifier

from services.auto_judge import ACTIVITY_CORPUS


TaskLabel = Literal["Indoor", "Outdoor"]


@dataclass(frozen=True)
class ModelInfo:
    name: str
    cv_accuracy: float


@dataclass(frozen=True)
class PredictionResult:
    classification: TaskLabel
    confidence: float
    model_name: str
    cv_accuracy: float


def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9\s]", " ", text.lower())).strip()


def _activity_variants(activity: str, label: str) -> list[str]:
    cleaned = _normalize_text(activity)
    if not cleaned:
        return []

    templates = [
        "{activity}",
        "going to {activity}",
        "doing {activity}",
        "planning to {activity}",
        "need to {activity}",
        "trying to {activity}",
        "want to {activity}",
    ]

    variants = {cleaned}
    for template in templates:
        variants.add(_normalize_text(template.format(activity=cleaned)))

    if " " in cleaned:
        variants.add(_normalize_text(f"my {cleaned}"))
        variants.add(_normalize_text(f"let us {cleaned}"))

    # Add context-aware variants so the model learns environment cues
    # from data instead of brittle runtime overrides.
    if label == "Outdoor":
        variants.add(_normalize_text(f"{cleaned} outside"))
        variants.add(_normalize_text(f"outside {cleaned}"))
        variants.add(_normalize_text(f"going outside for {cleaned}"))
    elif label == "Indoor":
        variants.add(_normalize_text(f"{cleaned} inside"))
        variants.add(_normalize_text(f"inside {cleaned}"))
        variants.add(_normalize_text(f"staying indoors for {cleaned}"))

    return [variant for variant in variants if variant]


def _build_training_set() -> tuple[list[str], list[str]]:
    texts: list[str] = []
    labels: list[str] = []

    for label, activities in ACTIVITY_CORPUS.items():
        for activity in activities:
            for variant in _activity_variants(activity, label):
                texts.append(variant)
                labels.append(label)

    return texts, labels


def _build_pipeline(classifier) -> Pipeline:
    return Pipeline(
        steps=[
            (
                "vectorizer",
                TfidfVectorizer(
                    analyzer="word",
                    ngram_range=(1, 2),
                    min_df=1,
                    lowercase=True,
                    strip_accents="unicode",
                ),
            ),
            ("svd", TruncatedSVD(n_components=24, random_state=42)),
            ("classifier", classifier),
        ]
    )


def _candidate_models() -> list[tuple[str, Pipeline, list[dict]]]:
    return [
        (
            "Decision Tree",
            _build_pipeline(DecisionTreeClassifier(random_state=42, class_weight="balanced")),
            [
                {"classifier__max_depth": 6, "classifier__min_samples_leaf": 1},
                {"classifier__max_depth": 10, "classifier__min_samples_leaf": 2},
                {"classifier__max_depth": None, "classifier__min_samples_leaf": 2},
            ],
        ),
        (
            "Random Forest",
            _build_pipeline(RandomForestClassifier(random_state=42, class_weight="balanced_subsample")),
            [
                {"classifier__n_estimators": 120, "classifier__max_depth": None, "classifier__min_samples_leaf": 1},
                {"classifier__n_estimators": 200, "classifier__max_depth": 12, "classifier__min_samples_leaf": 2},
            ],
        ),
        (
            "Gradient Boosting",
            _build_pipeline(GradientBoostingClassifier(random_state=42)),
            [
                {"classifier__n_estimators": 80, "classifier__learning_rate": 0.05, "classifier__max_depth": 2},
                {"classifier__n_estimators": 120, "classifier__learning_rate": 0.1, "classifier__max_depth": 3},
            ],
        ),
    ]


@lru_cache(maxsize=1)
def _trained_ensemble() -> tuple[list[tuple[str, Pipeline, float]], ModelInfo]:
    texts, labels = _build_training_set()
    if len(texts) < 10:
        raise RuntimeError("Training set is too small to build a reliable classifier")

    class_counts = {label: labels.count(label) for label in sorted(set(labels))}
    min_class_count = min(class_counts.values())
    folds = max(3, min(5, min_class_count))
    cv = StratifiedKFold(n_splits=folds, shuffle=True, random_state=42)

    tuned_models: list[tuple[str, Pipeline, float]] = []

    for model_name, pipeline, parameter_sets in _candidate_models():
        best_model_score = -1.0
        best_model_estimator: Pipeline | None = None

        for parameters in parameter_sets:
            candidate = clone(pipeline).set_params(**parameters)
            scores = cross_val_score(candidate, texts, labels, scoring="accuracy", cv=cv, n_jobs=1)
            score = float(scores.mean())

            if score > best_model_score:
                best_model_score = score
                best_model_estimator = clone(candidate).fit(texts, labels)

        if best_model_estimator is not None:
            tuned_models.append((model_name, best_model_estimator, best_model_score))

    if not tuned_models:
        raise RuntimeError("Could not train a task classification model")

    average_cv = sum(score for _, _, score in tuned_models) / len(tuned_models)
    model_names = " + ".join(name for name, _, _ in tuned_models)

    return tuned_models, ModelInfo(name=f"Ensemble ({model_names})", cv_accuracy=average_cv)


def predict_task_label(text: str) -> PredictionResult:
    models, model_info = _trained_ensemble()
    normalized = _normalize_text(text)
    class_scores: dict[str, float] = {}

    for _, model, _ in models:
        probabilities = model.predict_proba([normalized])[0].tolist()
        classes = model.named_steps["classifier"].classes_.tolist()
        for class_name, probability in zip(classes, probabilities):
            class_scores[class_name] = class_scores.get(class_name, 0.0) + float(probability)

    averaged_scores = {
        class_name: score / len(models)
        for class_name, score in class_scores.items()
    }

    best_class = max(averaged_scores, key=averaged_scores.get)
    best_confidence = averaged_scores[best_class]

    return PredictionResult(
        classification=cast(TaskLabel, best_class),
        confidence=float(best_confidence),
        model_name=model_info.name,
        cv_accuracy=model_info.cv_accuracy,
    )


def model_summary() -> ModelInfo:
    _, model_info = _trained_ensemble()
    return model_info