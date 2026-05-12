"""Standalone evaluation harness.

Loads the saved champion model, trains the alternative model family on the
same data, and writes a JSON report with accuracy, precision, recall, F1
(per-class, macro, weighted), confusion matrices, and inference latency
for both models across val / test / hardset / noisy-test splits.

    python -m ml_system.training.evaluation

Writes to ``ml_system/models/current/evaluation_report.json``.
"""
from __future__ import annotations

import json
import random
import time
from pathlib import Path

from ml_system.config.settings import CONFIG
from ml_system.training import metrics as cls_metrics
from ml_system.training.tokenizer import Tokenizer
from ml_system.training.trainer import load_dataset, split_xy
from ml_system.training.models import NaiveBayesModel, LinearSoftmaxModel
from ml_system.inference.engine import (
    load_model_from_json,
    load_tokenizer_from_json,
)


def _perturb_phrase(text: str, rng: random.Random, char_swap_rate: float = 0.08) -> str:
    """Drop, duplicate, or swap individual characters at ``char_swap_rate``.
    Simulates the typo noise typical of real user input.
    """
    out: list[str] = []
    i = 0
    chars = list(text)
    while i < len(chars):
        ch = chars[i]
        if ch.isalpha() and rng.random() < char_swap_rate:
            op = rng.choice(["drop", "dup", "swap"])
            if op == "drop":
                i += 1
                continue
            if op == "dup":
                out.append(ch)
                out.append(ch)
                i += 1
                continue
            if op == "swap" and i + 1 < len(chars) and chars[i + 1].isalpha():
                out.append(chars[i + 1])
                out.append(ch)
                i += 2
                continue
        out.append(ch)
        i += 1
    return "".join(out)


def _build_noisy_split(
    x: list[str],
    y: list[str],
    seed: int = 1234,
) -> tuple[list[str], list[str]]:
    rng = random.Random(seed)
    return [_perturb_phrase(text, rng) for text in x], list(y)


DEFAULT_DATASETS = {
    "train": Path("ml_system/data/datasets/train.jsonl"),
    "val": Path("ml_system/data/datasets/val.jsonl"),
    "test": Path("ml_system/data/datasets/test.jsonl"),
    "hardset": Path("ml_system/data/datasets/hardset.jsonl"),
}


def _predict_labels(model, tokenizer: Tokenizer, texts: list[str]) -> list[str]:
    probs = model.predict_proba(texts, tokenizer)
    return [max(p.items(), key=lambda kv: kv[1])[0] for p in probs]


def _evaluate_model_on_splits(
    name: str,
    model,
    tokenizer: Tokenizer,
    splits: dict[str, tuple[list[str], list[str]]],
    labels: list[str],
) -> dict:
    return {
        split_name: cls_metrics.evaluate(
            y, _predict_labels(model, tokenizer, x), labels,
        )
        for split_name, (x, y) in splits.items()
    }


def run_evaluation(
    datasets: dict[str, Path] = DEFAULT_DATASETS,
    output_path: Path | None = None,
) -> dict:
    """Run the full head-to-head evaluation and persist the report."""
    train_rows = load_dataset(datasets["train"])
    val_rows = load_dataset(datasets["val"])
    test_rows = load_dataset(datasets["test"])
    hard_rows = load_dataset(datasets["hardset"])

    x_train, y_train = split_xy(train_rows)
    x_val, y_val = split_xy(val_rows)
    x_test, y_test = split_xy(test_rows)
    x_hard, y_hard = split_xy(hard_rows)

    labels = sorted({*y_train, *y_val, *y_test, *y_hard})

    # Same labels, perturbed phrases.
    x_noisy_test, y_noisy_test = _build_noisy_split(x_test, y_test, seed=1234)

    splits = {
        "val": (x_val, y_val),
        "test": (x_test, y_test),
        "hardset": (x_hard, y_hard),
        "noisy_test": (x_noisy_test, y_noisy_test),
    }

    current_dir = CONFIG.get_current_model_path()
    tokenizer = load_tokenizer_from_json(current_dir / "tokenizer.json")
    champion = load_model_from_json(current_dir / "model.json")
    champion_type = champion.to_dict().get("model_type", "unknown")

    # Train the other model family on the same tokenizer so the report
    # always covers two comparable models.
    if champion_type == "naive_bayes":
        challenger = LinearSoftmaxModel(
            labels=labels,
            lr=CONFIG.learning_rate,
            epochs=CONFIG.epochs,
            l2=CONFIG.l2_regularization,
        )
        challenger.fit(x_train, y_train, tokenizer)
        model_one_name, model_one = "naive_bayes", champion
        model_two_name, model_two = "linear_softmax", challenger
    else:
        challenger = NaiveBayesModel(labels=labels, alpha=CONFIG.laplace_alpha)
        challenger.fit(x_train, y_train, tokenizer)
        model_one_name, model_one = "linear_softmax", champion
        model_two_name, model_two = "naive_bayes", challenger

    eval_one = _evaluate_model_on_splits(model_one_name, model_one, tokenizer, splits, labels)
    eval_two = _evaluate_model_on_splits(model_two_name, model_two, tokenizer, splits, labels)

    # Median per-phrase inference latency on the test split, in microseconds.
    def _latency_us(model) -> float:
        sample = x_test[: min(2000, len(x_test))] or x_test
        if not sample:
            return 0.0
        timings: list[float] = []
        for phrase in sample:
            t0 = time.perf_counter()
            model.predict_proba([phrase], tokenizer)
            timings.append((time.perf_counter() - t0) * 1_000_000)
        timings.sort()
        return timings[len(timings) // 2]

    latency = {
        model_one_name: _latency_us(model_one),
        model_two_name: _latency_us(model_two),
    }

    def _summary_row(name: str, evals: dict) -> dict:
        row = {"model": name}
        for split_name, ev in evals.items():
            row[f"{split_name}_accuracy"] = ev["accuracy"]
            row[f"{split_name}_precision_macro"] = ev["macro"]["precision"]
            row[f"{split_name}_recall_macro"] = ev["macro"]["recall"]
            row[f"{split_name}_f1_macro"] = ev["macro"]["f1"]
            row[f"{split_name}_f1_weighted"] = ev["weighted"]["f1"]
        row["median_inference_us"] = latency[name]
        return row

    comparison = [
        _summary_row(model_one_name, eval_one),
        _summary_row(model_two_name, eval_two),
    ]
    winner_test = max(
        comparison,
        key=lambda r: (
            r["test_f1_macro"],
            r["noisy_test_f1_macro"],
            r["hardset_f1_macro"],
            r["val_f1_macro"],
        ),
    )["model"]
    winner_robust = max(
        comparison,
        key=lambda r: (
            r["noisy_test_f1_macro"],
            r["hardset_f1_macro"],
            r["test_f1_macro"],
        ),
    )["model"]
    winner_overall = max(
        comparison,
        key=lambda r: (
            (
                r["test_f1_macro"]
                + r["noisy_test_f1_macro"]
                + r["hardset_f1_macro"]
                + r["val_f1_macro"]
            )
            / 4.0,
            -r["median_inference_us"],
        ),
    )["model"]

    report = {
        "labels": labels,
        "champion_on_disk": champion_type,
        "models": {
            model_one_name: eval_one,
            model_two_name: eval_two,
        },
        "comparison": comparison,
        "winners": {
            "by_test_macro_f1": winner_test,
            "by_noisy_test_macro_f1": winner_robust,
            "overall": winner_overall,
        },
        "split_sizes": {
            "train": len(x_train),
            "val": len(x_val),
            "test": len(x_test),
            "hardset": len(x_hard),
            "noisy_test": len(x_noisy_test),
        },
        "metric_definitions": {
            "accuracy": "Fraction of phrases where the predicted label matches the gold label.",
            "precision_macro": "Unweighted mean of per-class precision (TP / (TP+FP)).",
            "recall_macro": "Unweighted mean of per-class recall (TP / (TP+FN)).",
            "f1_macro": "Harmonic mean of macro precision and macro recall.",
            "f1_weighted": "Per-class F1 averaged with class-support weights.",
            "confusion_matrix": "Rows = true label, columns = predicted label (order matches 'labels').",
            "noisy_test": "Test split with character-level typo perturbation (drop/dup/swap at ~8% rate) - measures robustness.",
            "median_inference_us": "Median per-phrase inference latency in microseconds, measured on the test split.",
        },
    }

    output_path = output_path or (current_dir / "evaluation_report.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


if __name__ == "__main__":
    result = run_evaluation()
    print(json.dumps({
        "winners": result["winners"],
        "comparison": result["comparison"],
    }, indent=2))
