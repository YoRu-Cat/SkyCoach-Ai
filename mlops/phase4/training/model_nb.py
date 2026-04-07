from __future__ import annotations

from collections import Counter, defaultdict
import math

from .tokenizer import ScratchTokenizer


class ScratchNaiveBayes:
    def __init__(self, labels: list[str], alpha: float = 1.0) -> None:
        self.labels = sorted(labels)
        self.alpha = alpha
        self.class_doc_count: dict[str, int] = {label: 0 for label in self.labels}
        self.token_count_per_class: dict[str, Counter[str]] = {label: Counter() for label in self.labels}
        self.total_token_count_per_class: dict[str, int] = {label: 0 for label in self.labels}
        self.vocab: set[str] = set()

    def fit(self, texts: list[str], y: list[str], tokenizer: ScratchTokenizer) -> None:
        for text, label in zip(texts, y):
            tokens = tokenizer.tokenize(text)
            self.class_doc_count[label] += 1
            self.token_count_per_class[label].update(tokens)
            self.total_token_count_per_class[label] += len(tokens)
            self.vocab.update(tokens)

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

    def predict(self, texts: list[str], tokenizer: ScratchTokenizer) -> list[str]:
        probs = self.predict_proba(texts, tokenizer)
        return [max(row.items(), key=lambda x: x[1])[0] for row in probs]

    def to_dict(self) -> dict:
        return {
            "model_type": "scratch_naive_bayes",
            "labels": self.labels,
            "alpha": self.alpha,
            "class_doc_count": self.class_doc_count,
            "token_count_per_class": {k: dict(v) for k, v in self.token_count_per_class.items()},
            "total_token_count_per_class": self.total_token_count_per_class,
        }
