from __future__ import annotations

import re
from collections import Counter
import math


class Tokenizer:
    """Tokenizer for text normalization and vocabulary building."""

    def __init__(self, min_token_freq: int = 1, max_vocab_size: int = 5000) -> None:
        self.min_token_freq = min_token_freq
        self.max_vocab_size = max_vocab_size
        self.vocab: dict[str, int] = {"<PAD>": 0, "<UNK>": 1}

    @staticmethod
    def normalize(text: str) -> str:
        text = text.lower()
        text = re.sub(r"[^a-z0-9\s]", " ", text)
        return re.sub(r"\s+", " ", text).strip()

    def tokenize(self, text: str) -> list[str]:
        normalized = self.normalize(text)
        return [tok for tok in normalized.split(" ") if tok]

    def train(self, texts: list[str]) -> None:
        counts: Counter[str] = Counter()
        for text in texts:
            counts.update(self.tokenize(text))

        candidates = [
            token for token, freq in counts.most_common(self.max_vocab_size)
            if freq >= self.min_token_freq and token not in self.vocab
        ]

        for token in candidates:
            self.vocab[token] = len(self.vocab)

    def to_dict(self) -> dict:
        return {
            "min_token_freq": self.min_token_freq,
            "max_vocab_size": self.max_vocab_size,
            "vocab": self.vocab,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Tokenizer:
        tok = cls(
            min_token_freq=data["min_token_freq"],
            max_vocab_size=data["max_vocab_size"],
        )
        tok.vocab = data["vocab"]
        return tok
