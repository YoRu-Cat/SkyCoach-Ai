from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path

from .dataset import load_jsonl_dataset, split_xy
from .tokenizer import ScratchTokenizer
from .model_nb import ScratchNaiveBayes
from .model_linear import ScratchLinearSoftmax
from .metrics import accuracy_score, macro_f1_score
from .calibration import fit_temperature, apply_temperature


@dataclass(frozen=True)
class TrainingConfig:
    train_path: str
    val_path: str
    test_path: str
    hardset_path: str
    artifact_dir: str


@dataclass(frozen=True)
class TrainingReport:
    champion_model: str
    val_macro_f1: float
    val_accuracy: float
    test_macro_f1: float
    test_accuracy: float
    hardset_macro_f1: float
    hardset_accuracy: float
    temperature: float
    report_path: str
    tokenizer_path: str
    model_path: str


def _argmax_prob_rows(rows: list[dict[str, float]]) -> list[str]:
    return [max(row.items(), key=lambda x: x[1])[0] for row in rows]


def train_phase4(config: TrainingConfig) -> TrainingReport:
    train_rows = load_jsonl_dataset(config.train_path)
    val_rows = load_jsonl_dataset(config.val_path)
    test_rows = load_jsonl_dataset(config.test_path)
    hard_rows = load_jsonl_dataset(config.hardset_path)

    x_train, y_train = split_xy(train_rows)
    x_val, y_val = split_xy(val_rows)
    x_test, y_test = split_xy(test_rows)
    x_hard, y_hard = split_xy(hard_rows)

    labels = sorted({*y_train, *y_val, *y_test, *y_hard})

    tokenizer = ScratchTokenizer(min_token_freq=1, max_vocab_size=5000)
    tokenizer.train(x_train)

    nb = ScratchNaiveBayes(labels=labels, alpha=1.0)
    nb.fit(x_train, y_train, tokenizer)

    linear = ScratchLinearSoftmax(labels=labels, lr=0.05, epochs=30, l2=1e-4)
    linear.fit(x_train, y_train, tokenizer)

    candidates = {
        "scratch_naive_bayes": nb,
        "scratch_linear_softmax": linear,
    }

    best_name = ""
    best_val_f1 = -1.0
    best_val_acc = -1.0
    best_model = None

    for name, model in candidates.items():
        pred = model.predict(x_val, tokenizer)
        f1 = macro_f1_score(y_val, pred, labels)
        acc = accuracy_score(y_val, pred)
        if f1 > best_val_f1 or (f1 == best_val_f1 and acc > best_val_acc):
            best_name = name
            best_val_f1 = f1
            best_val_acc = acc
            best_model = model

    assert best_model is not None

    val_probs = best_model.predict_proba(x_val, tokenizer)
    temperature = fit_temperature(y_val, val_probs)

    def calibrated_predict(texts: list[str]) -> list[str]:
        probs = best_model.predict_proba(texts, tokenizer)
        calibrated = [apply_temperature(row, temperature) for row in probs]
        return _argmax_prob_rows(calibrated)

    test_pred = calibrated_predict(x_test)
    hard_pred = calibrated_predict(x_hard)

    test_f1 = macro_f1_score(y_test, test_pred, labels)
    test_acc = accuracy_score(y_test, test_pred)
    hard_f1 = macro_f1_score(y_hard, hard_pred, labels)
    hard_acc = accuracy_score(y_hard, hard_pred)

    artifact_dir = Path(config.artifact_dir)
    artifact_dir.mkdir(parents=True, exist_ok=True)

    report_path = artifact_dir / "phase4_training_report.json"
    tokenizer_path = artifact_dir / "phase4_tokenizer.json"
    model_path = artifact_dir / "phase4_champion_model.json"

    report_payload = {
        "champion_model": best_name,
        "labels": labels,
        "val": {"macro_f1": best_val_f1, "accuracy": best_val_acc},
        "test": {"macro_f1": test_f1, "accuracy": test_acc},
        "hardset": {"macro_f1": hard_f1, "accuracy": hard_acc},
        "temperature": temperature,
    }

    with report_path.open("w", encoding="utf-8") as f:
        json.dump(report_payload, f, indent=2)

    with tokenizer_path.open("w", encoding="utf-8") as f:
        json.dump(tokenizer.to_dict(), f, indent=2)

    with model_path.open("w", encoding="utf-8") as f:
        json.dump(best_model.to_dict(), f)

    return TrainingReport(
        champion_model=best_name,
        val_macro_f1=best_val_f1,
        val_accuracy=best_val_acc,
        test_macro_f1=test_f1,
        test_accuracy=test_acc,
        hardset_macro_f1=hard_f1,
        hardset_accuracy=hard_acc,
        temperature=temperature,
        report_path=str(report_path),
        tokenizer_path=str(tokenizer_path),
        model_path=str(model_path),
    )
