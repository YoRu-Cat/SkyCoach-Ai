"""Pure-Python classification metrics for the trainer and evaluator.

No scikit-learn dependency at inference time. Returns plain dicts/lists so
results are JSON-serialisable.
"""
from __future__ import annotations

from typing import Iterable


def _safe_div(num: float, den: float) -> float:
    return num / den if den > 0 else 0.0


def confusion_matrix(
    y_true: list[str],
    y_pred: list[str],
    labels: list[str],
) -> list[list[int]]:
    """Rows = true labels, columns = predicted labels, ordered by `labels`."""
    index = {label: i for i, label in enumerate(labels)}
    matrix = [[0 for _ in labels] for _ in labels]
    for t, p in zip(y_true, y_pred):
        if t not in index or p not in index:
            continue
        matrix[index[t]][index[p]] += 1
    return matrix


def per_class_counts(
    y_true: list[str],
    y_pred: list[str],
    labels: list[str],
) -> dict[str, dict[str, int]]:
    """Per-class TP / FP / FN / TN / support."""
    counts: dict[str, dict[str, int]] = {}
    total = len(y_true)
    for label in labels:
        tp = sum(1 for t, p in zip(y_true, y_pred) if t == label and p == label)
        fp = sum(1 for t, p in zip(y_true, y_pred) if t != label and p == label)
        fn = sum(1 for t, p in zip(y_true, y_pred) if t == label and p != label)
        tn = total - tp - fp - fn
        support = sum(1 for t in y_true if t == label)
        counts[label] = {
            "tp": tp, "fp": fp, "fn": fn, "tn": tn, "support": support,
        }
    return counts


def per_class_metrics(
    y_true: list[str],
    y_pred: list[str],
    labels: list[str],
) -> dict[str, dict[str, float]]:
    """Returns precision, recall, F1, accuracy and support per label."""
    counts = per_class_counts(y_true, y_pred, labels)
    out: dict[str, dict[str, float]] = {}
    total = len(y_true) if y_true else 0
    for label, c in counts.items():
        precision = _safe_div(c["tp"], c["tp"] + c["fp"])
        recall = _safe_div(c["tp"], c["tp"] + c["fn"])
        f1 = _safe_div(2 * precision * recall, precision + recall)
        per_label_acc = _safe_div(c["tp"] + c["tn"], total)
        out[label] = {
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "accuracy": per_label_acc,
            "support": float(c["support"]),
        }
    return out


def accuracy(y_true: list[str], y_pred: list[str]) -> float:
    if not y_true:
        return 0.0
    correct = sum(1 for t, p in zip(y_true, y_pred) if t == p)
    return correct / len(y_true)


def _macro_average(per_label: dict[str, dict[str, float]], key: str) -> float:
    values = [m[key] for m in per_label.values()]
    return sum(values) / len(values) if values else 0.0


def _weighted_average(per_label: dict[str, dict[str, float]], key: str) -> float:
    total_support = sum(m["support"] for m in per_label.values())
    if total_support <= 0:
        return 0.0
    return sum(m[key] * m["support"] for m in per_label.values()) / total_support


def evaluate(
    y_true: list[str],
    y_pred: list[str],
    labels: list[str],
) -> dict:
    """Full classification report ready for JSON persistence."""
    per_label = per_class_metrics(y_true, y_pred, labels)
    return {
        "labels": labels,
        "support": len(y_true),
        "accuracy": accuracy(y_true, y_pred),
        "macro": {
            "precision": _macro_average(per_label, "precision"),
            "recall": _macro_average(per_label, "recall"),
            "f1": _macro_average(per_label, "f1"),
        },
        "weighted": {
            "precision": _weighted_average(per_label, "precision"),
            "recall": _weighted_average(per_label, "recall"),
            "f1": _weighted_average(per_label, "f1"),
        },
        "per_class": per_label,
        "confusion_matrix": confusion_matrix(y_true, y_pred, labels),
    }


def macro_f1(y_true: list[str], y_pred: list[str], labels: list[str]) -> float:
    """Convenience wrapper to keep the original trainer API working."""
    return evaluate(y_true, y_pred, labels)["macro"]["f1"]


__all__ = [
    "accuracy",
    "confusion_matrix",
    "evaluate",
    "macro_f1",
    "per_class_counts",
    "per_class_metrics",
]
