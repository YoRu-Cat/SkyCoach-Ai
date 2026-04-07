from __future__ import annotations

from dataclasses import dataclass
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
from difflib import SequenceMatcher
from typing import Iterable

from .schema import QualityRecord, is_noise_phrase, normalize_phrase, validate_quality_record


@dataclass(frozen=True)
class QualityConfig:
    output_jsonl_path: str
    split_ratios: tuple[float, float, float] = (0.8, 0.1, 0.1)
    duplicate_similarity_threshold: float = 0.92


@dataclass(frozen=True)
class QualityReport:
    total_rows: int
    valid_rows: int
    invalid_rows: int
    noise_removed: int
    deduped_rows: int
    balanced_rows: int
    written_rows: int
    label_counts: dict[str, int]
    split_counts: dict[str, int]
    output_path: str


class QualityPipeline:
    def __init__(self, config: QualityConfig) -> None:
        self._config = config

    @staticmethod
    def _record_hash(record: QualityRecord) -> str:
        normalized = normalize_phrase(record.phrase)
        label = record.label.lower()
        digest = hashlib.sha256(f"{label}:{normalized}".encode("utf-8")).hexdigest()
        return digest

    def _is_duplicate(self, normalized_phrase: str, seen_phrases: list[str]) -> bool:
        for candidate in seen_phrases:
            if normalized_phrase == candidate:
                return True
            if SequenceMatcher(None, normalized_phrase, candidate).ratio() >= self._config.duplicate_similarity_threshold:
                return True
        return False

    def _choose_split(self, index: int, total: int) -> str:
        train_ratio, val_ratio, test_ratio = self._config.split_ratios
        train_cutoff = int(total * train_ratio)
        val_cutoff = train_cutoff + max(1, int(total * val_ratio)) if total >= 3 else train_cutoff + 1
        if index < train_cutoff:
            return "train"
        if index < val_cutoff:
            return "val"
        return "test"

    def run(self, rows: Iterable[dict]) -> QualityReport:
        total_rows = 0
        valid_rows = 0
        invalid_rows = 0
        noise_removed = 0
        deduped_rows = 0

        parsed_rows: list[QualityRecord] = []
        seen_phrases: list[str] = []

        for row in rows:
            total_rows += 1
            try:
                parsed = validate_quality_record(row)
            except Exception:
                invalid_rows += 1
                continue

            valid_rows += 1
            if is_noise_phrase(parsed.phrase):
                noise_removed += 1
                continue

            normalized = normalize_phrase(parsed.phrase)
            if self._is_duplicate(normalized, seen_phrases):
                deduped_rows += 1
                continue

            seen_phrases.append(normalized)
            parsed_rows.append(parsed)

        label_buckets: dict[str, list[QualityRecord]] = defaultdict(list)
        for record in parsed_rows:
            label_buckets[record.label].append(record)

        if label_buckets:
            min_count = min(len(bucket) for bucket in label_buckets.values())
        else:
            min_count = 0

        balanced_rows: list[QualityRecord] = []
        for label in sorted(label_buckets.keys()):
            balanced_rows.extend(sorted(label_buckets[label], key=lambda row: self._record_hash(row))[:min_count])

        split_rows: list[dict] = []
        balanced_grouped: dict[str, list[QualityRecord]] = defaultdict(list)
        for row in balanced_rows:
            balanced_grouped[row.label].append(row)

        for label, bucket in balanced_grouped.items():
            ordered = sorted(bucket, key=lambda row: self._record_hash(row))
            for index, record in enumerate(ordered):
                split_rows.append(
                    {
                        "phrase": record.phrase,
                        "label": record.label,
                        "language": record.language,
                        "split": self._choose_split(index, len(ordered)),
                        "record_hash": self._record_hash(record),
                        "source": {
                            "source_name": record.source.source_name,
                            "source_url": record.source.source_url,
                            "license": record.source.license,
                            "collected_at": record.source.collected_at,
                        },
                    }
                )

        split_counts = Counter(row["split"] for row in split_rows)
        label_counts = Counter(row["label"] for row in split_rows)

        output_path = Path(self._config.output_jsonl_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w", encoding="utf-8") as f:
            for row in split_rows:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")

        return QualityReport(
            total_rows=total_rows,
            valid_rows=valid_rows,
            invalid_rows=invalid_rows,
            noise_removed=noise_removed,
            deduped_rows=deduped_rows,
            balanced_rows=len(split_rows),
            written_rows=len(split_rows),
            label_counts=dict(label_counts),
            split_counts=dict(split_counts),
            output_path=str(output_path),
        )
