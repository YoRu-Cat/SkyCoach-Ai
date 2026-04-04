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


def _activity_variants(activity: str) -> list[str]:
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

    return [variant for variant in variants if variant]


def _build_training_set() -> tuple[list[str], list[str]]:
    texts: list[str] = []
    labels: list[str] = []

    for label, activities in ACTIVITY_CORPUS.items():
        for activity in activities:
            for variant in _activity_variants(activity):
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
def _trained_model() -> tuple[Pipeline, ModelInfo]:
    texts, labels = _build_training_set()
    if len(texts) < 10:
        raise RuntimeError("Training set is too small to build a reliable classifier")

    class_counts = {label: labels.count(label) for label in sorted(set(labels))}
    min_class_count = min(class_counts.values())
    folds = max(3, min(5, min_class_count))
    cv = StratifiedKFold(n_splits=folds, shuffle=True, random_state=42)

    best_estimator: Pipeline | None = None
    best_score = -1.0
    best_name = ""

    for model_name, pipeline, parameter_sets in _candidate_models():
        for parameters in parameter_sets:
            candidate = clone(pipeline).set_params(**parameters)
            scores = cross_val_score(candidate, texts, labels, scoring="accuracy", cv=cv, n_jobs=1)
            score = float(scores.mean())

            if score > best_score:
                best_score = score
                best_estimator = clone(candidate).fit(texts, labels)
                best_name = model_name

    if best_estimator is None:
        raise RuntimeError("Could not train a task classification model")

    return best_estimator, ModelInfo(name=best_name, cv_accuracy=best_score)


def predict_task_label(text: str) -> PredictionResult:
    model, model_info = _trained_model()
    normalized = _normalize_text(text)
    probabilities = model.predict_proba([normalized])[0].tolist()
    classes = model.named_steps["classifier"].classes_.tolist()
    best_index = max(range(len(probabilities)), key=lambda index: probabilities[index])

    return PredictionResult(
        classification=cast(TaskLabel, classes[best_index]),
        confidence=float(probabilities[best_index]),
        model_name=model_info.name,
        cv_accuracy=model_info.cv_accuracy,
    )


def model_summary() -> ModelInfo:
    _, model_info = _trained_model()
    return model_info