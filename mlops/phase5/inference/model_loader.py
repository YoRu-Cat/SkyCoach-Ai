from __future__ import annotations

import json
from pathlib import Path
from collections import Counter
import math
import random


class ScratchTokenizer:
    def __init__(self, min_token_freq: int = 1, max_vocab_size: int = 5000) -> None:
        self.min_token_freq = min_token_freq
        self.max_vocab_size = max_vocab_size
        self.vocab: dict[str, int] = {"<PAD>": 0, "<UNK>": 1}

    @staticmethod
    def normalize(text: str) -> str:
        import re
        text = text.lower()
        text = re.sub(r"[^a-z0-9\s]", " ", text)
        return re.sub(r"\s+", " ", text).strip()

    def tokenize(self, text: str) -> list[str]:
        normalized = self.normalize(text)
        return [tok for tok in normalized.split(" ") if tok]

    def to_dict(self) -> dict:
        return {
            "min_token_freq": self.min_token_freq,
            "max_vocab_size": self.max_vocab_size,
            "vocab": self.vocab,
        }

    @classmethod
    def from_dict(cls, data: dict) -> ScratchTokenizer:
        tok = cls(
            min_token_freq=data["min_token_freq"],
            max_vocab_size=data["max_vocab_size"],
        )
        tok.vocab = data["vocab"]
        return tok


class ScratchNaiveBayes:
    def __init__(self, labels: list[str], alpha: float = 1.0) -> None:
        self.labels = sorted(labels)
        self.alpha = alpha
        self.class_doc_count: dict[str, int] = {label: 0 for label in self.labels}
        self.token_count_per_class: dict[str, Counter[str]] = {label: Counter() for label in self.labels}
        self.total_token_count_per_class: dict[str, int] = {label: 0 for label in self.labels}
        self.vocab: set[str] = set()

    def predict_proba(self, texts: list[str], tokenizer: ScratchTokenizer) -> list[dict[str, float]]:
        all_probs: list[dict[str, float]] = []
        for text in texts:
            tokens = tokenizer.tokenize(text)
            scores = {label: self._log_prob(tokens, label) for label in self.labels}
            max_score = max(scores.values())
            exp_scores = {label: math.exp(score - max_score) for label, score in scores.items()}
            total = sum(exp_scores.values())
            all_probs.append({label: value / total for label, value in exp_scores.items()})
        return all_probs

    def _log_prob(self, tokens: list[str], label: str) -> float:
        total_docs = sum(self.class_doc_count.values())
        class_prior = (self.class_doc_count[label] + self.alpha) / (
            total_docs + self.alpha * len(self.labels)
        )
        score = math.log(class_prior)
        vocab_size = max(1, len(self.vocab))
        denom = self.total_token_count_per_class[label] + self.alpha * vocab_size
        token_counts = self.token_count_per_class[label]
        for token in tokens:
            prob = (token_counts[token] + self.alpha) / denom
            score += math.log(prob)
        return score

    def to_dict(self) -> dict:
        return {
            "model_type": "scratch_naive_bayes",
            "labels": self.labels,
            "alpha": self.alpha,
            "class_doc_count": self.class_doc_count,
            "token_count_per_class": {k: dict(v) for k, v in self.token_count_per_class.items()},
            "total_token_count_per_class": self.total_token_count_per_class,
        }

    @classmethod
    def from_dict(cls, data: dict) -> ScratchNaiveBayes:
        model = cls(labels=data["labels"], alpha=data["alpha"])
        model.class_doc_count = data["class_doc_count"]
        model.token_count_per_class = {k: Counter(v) for k, v in data["token_count_per_class"].items()}
        model.total_token_count_per_class = data["total_token_count_per_class"]
        model.vocab = set()
        for counts in model.token_count_per_class.values():
            model.vocab.update(counts.keys())
        return model


class ScratchLinearSoftmax:
    def __init__(self, labels: list[str], lr: float = 0.05, epochs: int = 30, l2: float = 1e-4) -> None:
        self.labels = sorted(labels)
        self.lr = lr
        self.epochs = epochs
        self.l2 = l2
        self.weights: dict[str, dict[str, float]] = {label: {} for label in self.labels}
        self.bias: dict[str, float] = {label: 0.0 for label in self.labels}

    @staticmethod
    def _softmax(scores: dict[str, float]) -> dict[str, float]:
        max_score = max(scores.values())
        exp_scores = {k: math.exp(v - max_score) for k, v in scores.items()}
        total = sum(exp_scores.values())
        return {k: v / total for k, v in exp_scores.items()}

    def _predict_scores(self, features: Counter[str]) -> dict[str, float]:
        scores: dict[str, float] = {}
        for label in self.labels:
            value = self.bias[label]
            w = self.weights[label]
            for token, count in features.items():
                value += w.get(token, 0.0) * count
            scores[label] = value
        return scores

    def predict_proba(self, texts: list[str], tokenizer: ScratchTokenizer) -> list[dict[str, float]]:
        probs: list[dict[str, float]] = []
        for text in texts:
            features = Counter(tokenizer.tokenize(text))
            probs.append(self._softmax(self._predict_scores(features)))
        return probs

    def to_dict(self) -> dict:
        return {
            "model_type": "scratch_linear_softmax",
            "labels": self.labels,
            "lr": self.lr,
            "epochs": self.epochs,
            "l2": self.l2,
            "weights": self.weights,
            "bias": self.bias,
        }

    @classmethod
    def from_dict(cls, data: dict) -> ScratchLinearSoftmax:
        model = cls(
            labels=data["labels"],
            lr=data["lr"],
            epochs=data["epochs"],
            l2=data["l2"],
        )
        model.weights = data["weights"]
        model.bias = data["bias"]
        return model


def load_tokenizer_from_json(json_path: str | Path) -> ScratchTokenizer:
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return ScratchTokenizer.from_dict(data)


def load_model_from_json(json_path: str | Path) -> ScratchNaiveBayes | ScratchLinearSoftmax:
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    model_type = data.get("model_type")
    if model_type == "scratch_naive_bayes":
        return ScratchNaiveBayes.from_dict(data)
    elif model_type == "scratch_linear_softmax":
        return ScratchLinearSoftmax.from_dict(data)
    else:
        raise ValueError(f"Unknown model type: {model_type}")


def load_report_from_json(json_path: str | Path) -> dict:
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)
