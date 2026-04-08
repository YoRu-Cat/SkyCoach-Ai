from __future__ import annotations

import json
from pathlib import Path
from .tokenizer import Tokenizer
from .models import NaiveBayesModel, LinearSoftmaxModel


def load_dataset(path: str | Path) -> list[dict]:
    """Load JSONL dataset."""
    records = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))
    return records


def split_xy(records: list[dict]) -> tuple[list[str], list[str]]:
    """Split records into texts and labels."""
    texts = [r.get("phrase") for r in records]
    labels = [r.get("label") for r in records]
    return texts, labels


def accuracy_score(y_true: list[str], y_pred: list[str]) -> float:
    """Calculate accuracy."""
    return sum(t == p for t, p in zip(y_true, y_pred)) / len(y_true) if y_true else 0.0


def macro_f1_score(y_true: list[str], y_pred: list[str], labels: list[str]) -> float:
    """Calculate macro F1 score."""
    f1_scores = []
    for label in labels:
        tp = sum(1 for t, p in zip(y_true, y_pred) if t == label and p == label)
        fp = sum(1 for t, p in zip(y_true, y_pred) if t != label and p == label)
        fn = sum(1 for t, p in zip(y_true, y_pred) if t == label and p != label)
        
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
        f1_scores.append(f1)
    
    return sum(f1_scores) / len(f1_scores) if f1_scores else 0.0


class Trainer:
    """Model trainer orchestrator."""

    def __init__(
        self,
        train_path: str | Path,
        val_path: str | Path,
        test_path: str | Path,
        hardset_path: str | Path,
        output_dir: str | Path,
    ) -> None:
        self.train_path = Path(train_path)
        self.val_path = Path(val_path)
        self.test_path = Path(test_path)
        self.hardset_path = Path(hardset_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def train(self) -> dict:
        """Train models and return results."""
        
        # Load data
        train_rows = load_dataset(self.train_path)
        val_rows = load_dataset(self.val_path)
        test_rows = load_dataset(self.test_path)
        hard_rows = load_dataset(self.hardset_path)

        x_train, y_train = split_xy(train_rows)
        x_val, y_val = split_xy(val_rows)
        x_test, y_test = split_xy(test_rows)
        x_hard, y_hard = split_xy(hard_rows)

        focus_examples = [
            {"phrase": "going on a date", "label": "Indoor"},
            {"phrase": "going on a date with a girl", "label": "Indoor"},
            {"phrase": "going on a date with my girlfriend", "label": "Indoor"},
            {"phrase": "date night", "label": "Indoor"},
            {"phrase": "romantic date", "label": "Indoor"},
            {"phrase": "coffee date", "label": "Indoor"},
            {"phrase": "dinner date", "label": "Indoor"},
            {"phrase": "meeting my girlfriend for a date", "label": "Indoor"},
            {"phrase": "going to meet my girlfriend", "label": "Indoor"},
            {"phrase": "going out with my girlfriend", "label": "Indoor"},
            {"phrase": "seeing my girlfriend tonight", "label": "Indoor"},
            {"phrase": "social date plan", "label": "Indoor"},
            {"phrase": "planning a date", "label": "Indoor"},
            {"phrase": "date with a girl", "label": "Indoor"},
            {"phrase": "going on a date at a restaurant", "label": "Indoor"},
            {"phrase": "date night at home", "label": "Indoor"},
            {"phrase": "coffee date at a cafe", "label": "Indoor"},
            {"phrase": "movie date at the cinema", "label": "Indoor"},
            {"phrase": "going on a date at an amusement park", "label": "Outdoor"},
            {"phrase": "date at an amusement park", "label": "Outdoor"},
            {"phrase": "amusement park date", "label": "Outdoor"},
            {"phrase": "romantic date at the park", "label": "Outdoor"},
            {"phrase": "going on a date outside", "label": "Outdoor"},
            {"phrase": "date at the beach", "label": "Outdoor"},
            {"phrase": "going to get cigarettes from tobacco shop", "label": "Outdoor"},
            {"phrase": "buying cigarettes from tobacco store", "label": "Outdoor"},
            {"phrase": "going to tobacco shop", "label": "Outdoor"},
            {"phrase": "going to buy from local store", "label": "Outdoor"},
            {"phrase": "quick run to the grocery store", "label": "Outdoor"},
            {"phrase": "shopping at local market", "label": "Outdoor"},
            {"phrase": "buying cigarettes online", "label": "Indoor"},
            {"phrase": "ordering cigarettes from app", "label": "Indoor"},
            {"phrase": "shopping online", "label": "Indoor"},
            {"phrase": "buy groceries online", "label": "Indoor"},
        ]

        x_train.extend(example["phrase"] for example in focus_examples)
        y_train.extend(example["label"] for example in focus_examples)

        labels = sorted({*y_train, *y_val, *y_test, *y_hard})

        # Train tokenizer
        tokenizer = Tokenizer(min_token_freq=1, max_vocab_size=5000)
        tokenizer.train(x_train)

        # Train models
        nb = NaiveBayesModel(labels=labels, alpha=1.0)
        nb.fit(x_train, y_train, tokenizer)

        linear = LinearSoftmaxModel(labels=labels, lr=0.05, epochs=30, l2=1e-4)
        linear.fit(x_train, y_train, tokenizer)

        # Evaluate on validation set and select champion
        best_name = ""
        best_val_f1 = -1.0
        best_model = None

        for name, model in [("naive_bayes", nb), ("linear_softmax", linear)]:
            probs = model.predict_proba(x_val, tokenizer)
            preds = [max(p.items(), key=lambda x: x[1])[0] for p in probs]
            f1 = macro_f1_score(y_val, preds, labels)
            if f1 > best_val_f1:
                best_name = name
                best_val_f1 = f1
                best_model = model

        # Apply temperature scaling
        val_probs = best_model.predict_proba(x_val, tokenizer)
        temperature = self._calibrate_temperature(y_val, val_probs)

        # Final evaluation
        def calibrated_predict(texts: list[str]) -> list[str]:
            probs = best_model.predict_proba(texts, tokenizer)
            calibrated = [self._apply_temperature(p, temperature) for p in probs]
            return [max(p.items(), key=lambda x: x[1])[0] for p in calibrated]

        test_preds = calibrated_predict(x_test)
        hard_preds = calibrated_predict(x_hard)

        test_f1 = macro_f1_score(y_test, test_preds, labels)
        hard_f1 = macro_f1_score(y_hard, hard_preds, labels)

        # Save artifacts
        report = {
            "champion_model": best_name,
            "labels": labels,
            "val": {"macro_f1": best_val_f1},
            "test": {"macro_f1": test_f1},
            "hardset": {"macro_f1": hard_f1},
            "temperature": temperature,
        }

        report_path = self.output_dir / "report.json"
        legacy_report_path = self.output_dir / "training_report.json"
        tokenizer_path = self.output_dir / "tokenizer.json"
        model_path = self.output_dir / "model.json"

        with report_path.open("w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        with legacy_report_path.open("w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        with tokenizer_path.open("w", encoding="utf-8") as f:
            json.dump(tokenizer.to_dict(), f, indent=2)

        with model_path.open("w", encoding="utf-8") as f:
            json.dump(best_model.to_dict(), f)

        return {
            "champion_model": best_name,
            "val_f1": best_val_f1,
            "test_f1": test_f1,
            "hardset_f1": hard_f1,
            "temperature": temperature,
            "report_path": str(report_path),
            "tokenizer_path": str(tokenizer_path),
            "model_path": str(model_path),
        }

    @staticmethod
    def _calibrate_temperature(y_true: list[str], probs: list[dict[str, float]]) -> float:
        """Find best temperature scaling parameter."""
        best_temp = 1.0
        best_nll = float("inf")

        for temp in [0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.2, 1.5, 2.0, 3.0]:
            nll = 0.0
            for label, prob_dict in zip(y_true, probs):
                calibrated = Trainer._apply_temperature(prob_dict, temp)
                label_prob = calibrated.get(label, 1e-10)
                import math
                nll += -math.log(max(label_prob, 1e-10))
            
            if nll < best_nll:
                best_nll = nll
                best_temp = temp

        return best_temp

    @staticmethod
    def _apply_temperature(logits: dict[str, float], temperature: float) -> dict[str, float]:
        """Apply temperature scaling."""
        import math
        max_logit = max(logits.values())
        scaled = {k: (v - max_logit) / temperature for k, v in logits.items()}
        exp_scores = {k: math.exp(v) for k, v in scaled.items()}
        total = sum(exp_scores.values())
        return {k: v / total for k, v in exp_scores.items()}
