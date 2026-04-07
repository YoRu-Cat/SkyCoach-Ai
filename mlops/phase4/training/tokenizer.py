from __future__ import annotations

from dataclasses import dataclass
import re
from collections import Counter


@dataclass
class ScratchTokenizer:
    min_token_freq: int = 1
    max_vocab_size: int = 5000

    def __post_init__(self) -> None:
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

    def encode(self, text: str) -> list[int]:
        return [self.vocab.get(tok, self.vocab["<UNK>"]) for tok in self.tokenize(text)]

    def to_dict(self) -> dict:
        return {
            "min_token_freq": self.min_token_freq,
            "max_vocab_size": self.max_vocab_size,
            "vocab": self.vocab,
        }
