from __future__ import annotations

import re
from collections import Counter
import math


class Tokenizer:
    """Tokenizer for text normalization and vocabulary building."""

    def __init__(
        self,
        min_token_freq: int = 1,
        max_vocab_size: int = 5000,
        use_char_ngrams: bool = True,
        char_ngram_min: int = 3,
        char_ngram_max: int = 5,
    ) -> None:
        self.min_token_freq = min_token_freq
        self.max_vocab_size = max_vocab_size
        self.use_char_ngrams = use_char_ngrams
        self.char_ngram_min = char_ngram_min
        self.char_ngram_max = char_ngram_max
        self.vocab: dict[str, int] = {"<PAD>": 0, "<UNK>": 1}

    @staticmethod
    def normalize(text: str) -> str:
        text = text.lower()
        text = re.sub(r"[^a-z0-9\s]", " ", text)
        return re.sub(r"\s+", " ", text).strip()

    def tokenize(self, text: str) -> list[str]:
        normalized = self.normalize(text)
        base_tokens = [tok for tok in normalized.split(" ") if tok]

        if not self.use_char_ngrams:
            return base_tokens

        # Character n-grams help model misspellings and inflections robustly.
        ngram_tokens: list[str] = []
        for token in base_tokens:
            if not token.isalpha() or len(token) < self.char_ngram_min:
                continue
            padded = f"^{token}$"
            for n in range(self.char_ngram_min, self.char_ngram_max + 1):
                if len(padded) < n:
                    continue
                for i in range(len(padded) - n + 1):
                    ngram_tokens.append(f"cg_{padded[i:i+n]}")

        return base_tokens + ngram_tokens

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
            "use_char_ngrams": self.use_char_ngrams,
            "char_ngram_min": self.char_ngram_min,
            "char_ngram_max": self.char_ngram_max,
            "vocab": self.vocab,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Tokenizer:
        tok = cls(
            min_token_freq=data["min_token_freq"],
            max_vocab_size=data["max_vocab_size"],
            use_char_ngrams=data.get("use_char_ngrams", True),
            char_ngram_min=data.get("char_ngram_min", 3),
            char_ngram_max=data.get("char_ngram_max", 5),
        )
        tok.vocab = data["vocab"]
        return tok
