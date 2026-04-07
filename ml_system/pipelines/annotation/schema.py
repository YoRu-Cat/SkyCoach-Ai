from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import re
from typing import Any


_ALLOWED_LABELS = {"Indoor", "Outdoor", "Mixed", "Unclear"}


@dataclass(frozen=True)
class AnnotationRecord:
    phrase: str
    annotator_id: str
    label: str
    note: str
    annotated_at: str


@dataclass(frozen=True)
class ResolvedRecord:
    phrase: str
    label_a: str
    label_b: str
    resolved_label: str
    status: str
    resolution_reason: str


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def normalize_phrase(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def validate_annotation_row(payload: dict[str, Any]) -> AnnotationRecord:
    phrase = str(payload.get("phrase", "")).strip()
    annotator_id = str(payload.get("annotator_id", "")).strip()
    label = str(payload.get("label", "")).strip().title()
    note = str(payload.get("note", "")).strip()
    annotated_at = str(payload.get("annotated_at", "")).strip() or utc_now_iso()

    if len(phrase) < 2:
        raise ValueError("Invalid annotation row: phrase is required")
    if not annotator_id:
        raise ValueError("Invalid annotation row: annotator_id is required")
    if label not in _ALLOWED_LABELS:
        raise ValueError("Invalid annotation row: unknown label")

    return AnnotationRecord(
        phrase=phrase,
        annotator_id=annotator_id,
        label=label,
        note=note,
        annotated_at=annotated_at,
    )
