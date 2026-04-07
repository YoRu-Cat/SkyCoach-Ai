from __future__ import annotations

from collections import Counter
import math
import random

from .tokenizer import ScratchTokenizer


class ScratchLinearSoftmax:
    def __init__(self, labels: list[str], lr: float = 0.05, epochs: int = 20, l2: float = 1e-4) -> None:
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

    def _features(self, text: str, tokenizer: ScratchTokenizer) -> Counter[str]:
        return Counter(tokenizer.tokenize(text))

    def _predict_scores(self, features: Counter[str]) -> dict[str, float]:
        scores: dict[str, float] = {}
        for label in self.labels:
            value = self.bias[label]
            w = self.weights[label]
            for token, count in features.items():
                value += w.get(token, 0.0) * count
            scores[label] = value
        return scores

    def fit(self, texts: list[str], y: list[str], tokenizer: ScratchTokenizer) -> None:
        indices = list(range(len(texts)))
        rng = random.Random(42)

        for _ in range(self.epochs):
            rng.shuffle(indices)
            for idx in indices:
                text = texts[idx]
                gold = y[idx]
                features = self._features(text, tokenizer)
                probs = self._softmax(self._predict_scores(features))

                for label in self.labels:
                    target = 1.0 if label == gold else 0.0
                    grad = probs[label] - target

                    self.bias[label] -= self.lr * grad
                    w = self.weights[label]
                    for token, count in features.items():
                        current = w.get(token, 0.0)
                        update = grad * count + self.l2 * current
                        w[token] = current - self.lr * update

    def predict_proba(self, texts: list[str], tokenizer: ScratchTokenizer) -> list[dict[str, float]]:
        probs: list[dict[str, float]] = []
        for text in texts:
            features = self._features(text, tokenizer)
            probs.append(self._softmax(self._predict_scores(features)))
        return probs

    def predict(self, texts: list[str], tokenizer: ScratchTokenizer) -> list[str]:
        probs = self.predict_proba(texts, tokenizer)
        return [max(row.items(), key=lambda x: x[1])[0] for row in probs]

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
