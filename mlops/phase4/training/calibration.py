from __future__ import annotations

import math


def apply_temperature(prob: dict[str, float], temperature: float) -> dict[str, float]:
    temperature = max(0.1, float(temperature))
    adjusted = {label: max(1e-12, p) ** (1.0 / temperature) for label, p in prob.items()}
    total = sum(adjusted.values())
    return {label: value / total for label, value in adjusted.items()}


def nll(y_true: list[str], probs: list[dict[str, float]]) -> float:
    if not y_true:
        return 0.0
    loss = 0.0
    for target, row in zip(y_true, probs):
        loss -= math.log(max(1e-12, row.get(target, 1e-12)))
    return loss / len(y_true)


def fit_temperature(y_true: list[str], probs: list[dict[str, float]]) -> float:
    best_temp = 1.0
    best_loss = nll(y_true, probs)

    t = 0.5
    while t <= 3.0:
        calibrated = [apply_temperature(row, t) for row in probs]
        loss = nll(y_true, calibrated)
        if loss < best_loss:
            best_loss = loss
            best_temp = round(t, 2)
        t += 0.05

    return best_temp
