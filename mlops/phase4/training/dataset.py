from __future__ import annotations

import json
from pathlib import Path
from dataclasses import dataclass


@dataclass(frozen=True)
class LabeledPhrase:
    phrase: str
    label: str


def load_jsonl_dataset(path: str) -> list[LabeledPhrase]:
    rows: list[LabeledPhrase] = []
    with Path(path).open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            obj = json.loads(line)
            rows.append(LabeledPhrase(phrase=str(obj["phrase"]), label=str(obj["label"])))
    return rows


def split_xy(rows: list[LabeledPhrase]) -> tuple[list[str], list[str]]:
    return [row.phrase for row in rows], [row.label for row in rows]
