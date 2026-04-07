from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import re
from typing import Any


_ALLOWED_LICENSES = {
    "cc-by",
    "cc-by-sa",
    "cc0",
    "odc-by",
    "mit",
    "apache-2.0",
    "custom-permitted",
}


@dataclass(frozen=True)
class SourceInfo:
    source_name: str
    source_url: str
    license: str
    collected_at: str


@dataclass(frozen=True)
class RawPhraseRecord:
    phrase: str
    language: str
    source: SourceInfo
    split_hint: str = "unspecified"


def normalize_phrase(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _is_valid_url(value: str) -> bool:
    return bool(re.match(r"^https?://", value.strip()))


def validate_raw_record(payload: dict[str, Any]) -> RawPhraseRecord:
    phrase = str(payload.get("phrase", "")).strip()
    language = str(payload.get("language", "")).strip().lower()
    source_name = str(payload.get("source_name", "")).strip()
    source_url = str(payload.get("source_url", "")).strip()
    license_name = str(payload.get("license", "")).strip().lower()
    collected_at = str(payload.get("collected_at", "")).strip() or utc_now_iso()
    split_hint = str(payload.get("split_hint", "unspecified")).strip().lower() or "unspecified"

    if len(phrase) < 3:
        raise ValueError("Invalid record: phrase must be at least 3 characters")
    if language != "en":
        raise ValueError("Invalid record: only English phrases are accepted")
    if not source_name:
        raise ValueError("Invalid record: source_name is required")
    if not _is_valid_url(source_url):
        raise ValueError("Invalid record: source_url must start with http:// or https://")
    if license_name not in _ALLOWED_LICENSES:
        raise ValueError("Invalid record: license is not in allowed list")

    return RawPhraseRecord(
        phrase=phrase,
        language=language,
        source=SourceInfo(
            source_name=source_name,
            source_url=source_url,
            license=license_name,
            collected_at=collected_at,
        ),
        split_hint=split_hint,
    )
