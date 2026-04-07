from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from typing import Iterable

from .schema import RawPhraseRecord, normalize_phrase, validate_raw_record


@dataclass(frozen=True)
class IngestionConfig:
    output_jsonl_path: str


@dataclass(frozen=True)
class IngestionReport:
    total_rows: int
    valid_rows: int
    invalid_rows: int
    deduped_rows: int
    written_rows: int
    output_path: str


class IngestionPipeline:
    def __init__(self, config: IngestionConfig) -> None:
        self._config = config

    @staticmethod
    def _record_hash(record: RawPhraseRecord) -> str:
        normalized = normalize_phrase(record.phrase)
        return hashlib.sha256(normalized.encode("utf-8")).hexdigest()

    def run(self, rows: Iterable[dict]) -> IngestionReport:
        total_rows = 0
        valid_rows = 0
        invalid_rows = 0
        deduped_rows = 0

        seen_hashes: set[str] = set()
        staged: list[dict] = []

        for row in rows:
            total_rows += 1
            try:
                parsed = validate_raw_record(row)
            except Exception:
                invalid_rows += 1
                continue

            valid_rows += 1
            content_hash = self._record_hash(parsed)
            if content_hash in seen_hashes:
                deduped_rows += 1
                continue

            seen_hashes.add(content_hash)
            staged.append(
                {
                    "phrase": parsed.phrase,
                    "language": parsed.language,
                    "split_hint": parsed.split_hint,
                    "record_hash": content_hash,
                    "source": {
                        "source_name": parsed.source.source_name,
                        "source_url": parsed.source.source_url,
                        "license": parsed.source.license,
                        "collected_at": parsed.source.collected_at,
                    },
                }
            )

        output_path = Path(self._config.output_jsonl_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w", encoding="utf-8") as f:
            for row in staged:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")

        return IngestionReport(
            total_rows=total_rows,
            valid_rows=valid_rows,
            invalid_rows=invalid_rows,
            deduped_rows=deduped_rows,
            written_rows=len(staged),
            output_path=str(output_path),
        )
