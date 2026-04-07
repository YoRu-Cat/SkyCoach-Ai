from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PredictionRequest:
    phrase: str


@dataclass(frozen=True)
class PredictionResponse:
    label: str
    confidence: float
    rationale: str
    model: str
    all_scores: dict[str, float]
