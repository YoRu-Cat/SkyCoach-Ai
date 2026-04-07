from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, Protocol


class SourceAdapter(Protocol):
    def read(self) -> Iterable[dict]:
        ...


class InMemoryAdapter:
    def __init__(self, rows: list[dict]) -> None:
        self._rows = rows

    def read(self) -> Iterable[dict]:
        for row in self._rows:
            yield row


class JsonlFileAdapter:
    def __init__(self, file_path: str) -> None:
        self._path = Path(file_path)

    def read(self) -> Iterable[dict]:
        with self._path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                yield json.loads(line)
