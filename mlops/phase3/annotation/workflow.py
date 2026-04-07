from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from typing import Iterable

from .schema import AnnotationRecord, ResolvedRecord, normalize_phrase, validate_annotation_row


@dataclass(frozen=True)
class AnnotationConfig:
    merged_output_path: str
    golden_output_path: str


@dataclass(frozen=True)
class AnnotationReport:
    total_rows_a: int
    total_rows_b: int
    valid_pairs: int
    auto_agreements: int
    resolved_conflicts: int
    unresolved_conflicts: int
    frozen_golden_rows: int
    merged_output_path: str
    golden_output_path: str


class AnnotationWorkflow:
    @staticmethod
    def _phrase_hash(text: str) -> str:
        return hashlib.sha256(normalize_phrase(text).encode("utf-8")).hexdigest()

    @staticmethod
    def _resolve_conflict(label_a: str, label_b: str) -> tuple[str, str, str]:
        if label_a == label_b:
            return label_a, "resolved", "annotators_agreed"

        pair = {label_a, label_b}
        if "Unclear" in pair and len(pair) == 2:
            chosen = (pair - {"Unclear"}).pop()
            return chosen, "resolved", "prefer_specific_over_unclear"

        if pair == {"Indoor", "Outdoor"}:
            return "Mixed", "resolved", "opposite_environment_labels"

        if "Mixed" in pair and len(pair) == 2:
            chosen = (pair - {"Mixed"}).pop()
            return chosen, "resolved", "prefer_specific_over_mixed"

        return "Unclear", "needs_review", "manual_review_required"

    def run(
        self,
        rows_a: Iterable[dict],
        rows_b: Iterable[dict],
        config: AnnotationConfig,
    ) -> AnnotationReport:
        parsed_a: dict[str, AnnotationRecord] = {}
        parsed_b: dict[str, AnnotationRecord] = {}

        total_rows_a = 0
        total_rows_b = 0

        for row in rows_a:
            total_rows_a += 1
            parsed = validate_annotation_row(row)
            parsed_a[self._phrase_hash(parsed.phrase)] = parsed

        for row in rows_b:
            total_rows_b += 1
            parsed = validate_annotation_row(row)
            parsed_b[self._phrase_hash(parsed.phrase)] = parsed

        common_keys = sorted(set(parsed_a.keys()) & set(parsed_b.keys()))

        merged: list[dict] = []
        golden: list[dict] = []

        auto_agreements = 0
        resolved_conflicts = 0
        unresolved_conflicts = 0

        for key in common_keys:
            a = parsed_a[key]
            b = parsed_b[key]

            resolved_label, status, reason = self._resolve_conflict(a.label, b.label)
            if reason == "annotators_agreed":
                auto_agreements += 1
            elif status == "resolved":
                resolved_conflicts += 1
            else:
                unresolved_conflicts += 1

            merged_row = {
                "phrase": normalize_phrase(a.phrase),
                "phrase_hash": key,
                "annotator_a": a.annotator_id,
                "annotator_b": b.annotator_id,
                "label_a": a.label,
                "label_b": b.label,
                "resolved_label": resolved_label,
                "status": status,
                "resolution_reason": reason,
            }
            merged.append(merged_row)

            if status == "resolved":
                golden.append(
                    {
                        "phrase": merged_row["phrase"],
                        "phrase_hash": key,
                        "label": resolved_label,
                        "source": "phase3_double_annotation",
                    }
                )

        merged_path = Path(config.merged_output_path)
        golden_path = Path(config.golden_output_path)
        merged_path.parent.mkdir(parents=True, exist_ok=True)
        golden_path.parent.mkdir(parents=True, exist_ok=True)

        with merged_path.open("w", encoding="utf-8") as f:
            for row in merged:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")

        with golden_path.open("w", encoding="utf-8") as f:
            for row in golden:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")

        return AnnotationReport(
            total_rows_a=total_rows_a,
            total_rows_b=total_rows_b,
            valid_pairs=len(common_keys),
            auto_agreements=auto_agreements,
            resolved_conflicts=resolved_conflicts,
            unresolved_conflicts=unresolved_conflicts,
            frozen_golden_rows=len(golden),
            merged_output_path=str(merged_path),
            golden_output_path=str(golden_path),
        )
