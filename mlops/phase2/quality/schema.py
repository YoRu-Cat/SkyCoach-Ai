from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import re
from typing import Any


_ALLOWED_LABELS = {"Indoor", "Outdoor", "Mixed", "Unclear"}
_NOISE_TERMS = {
    "idk",
    "something",
    "do stuff",
    "random",
    "blah",
    "test",
    "asd",
    "qwerty",
}
_PROFANITY_TERMS = {
    "fuck",
    "shit",
    "bitch",
    "asshole",
    "damn",
}


@dataclass(frozen=True)
class QualitySource:
    source_name: str
    source_url: str
    license: str
    collected_at: str


@dataclass(frozen=True)
class QualityRecord:
    phrase: str
    label: str
    language: str
    source: QualitySource
    split_hint: str = "unspecified"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def normalize_phrase(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def validate_quality_record(payload: dict[str, Any]) -> QualityRecord:
    phrase = str(payload.get("phrase", "")).strip()
    label = str(payload.get("label", "")).strip().title()
    language = str(payload.get("language", "")).strip().lower()
    source_name = str(payload.get("source_name", "")).strip()
    source_url = str(payload.get("source_url", "")).strip()
    license_name = str(payload.get("license", "")).strip().lower()
    collected_at = str(payload.get("collected_at", "")).strip() or utc_now_iso()
    split_hint = str(payload.get("split_hint", "unspecified")).strip().lower() or "unspecified"

    if len(phrase) < 2:
        raise ValueError("phrase is required")
    if label not in _ALLOWED_LABELS:
        raise ValueError("label is not supported")
    if language != "en":
        raise ValueError("only English records are supported in phase 2")
    if not source_name or not source_url.startswith(("http://", "https://")):
        raise ValueError("source metadata is invalid")
    if not license_name:
        raise ValueError("license is required")

    return QualityRecord(
        phrase=phrase,
        label=label,
        language=language,
        source=QualitySource(
            source_name=source_name,
            source_url=source_url,
            license=license_name,
            collected_at=collected_at,
        ),
        split_hint=split_hint,
    )


def is_noise_phrase(text: str) -> bool:
    normalized = normalize_phrase(text)
    if len(normalized) < 3:
        return True

    tokens = normalized.split()
    if not tokens:
        return True

    if normalized in _NOISE_TERMS:
        return True
    if any(term in normalized for term in _PROFANITY_TERMS):
        return True
    if len(tokens) == 1 and len(tokens[0]) < 4:
        return True
    if sum(char.isalpha() for char in normalized) < 2:
        return True
    return False
