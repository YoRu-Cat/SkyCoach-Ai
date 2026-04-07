import hashlib
import json
from pathlib import Path

from mlops.phase2.quality.pipeline import QualityConfig, QualityPipeline
from mlops.phase2.quality.schema import normalize_phrase


def test_phase2_quality_filters_noise_duplicates_and_balances(tmp_path: Path):
    rows = [
        {
            "phrase": "going to uni",
            "label": "Outdoor",
            "language": "en",
            "source_name": "dataset_a",
            "source_url": "https://example.org/a",
            "license": "cc-by",
            "collected_at": "2026-04-07T00:00:00Z",
            "split_hint": "train",
        },
        {
            "phrase": "Going to UNI",
            "label": "Outdoor",
            "language": "en",
            "source_name": "dataset_b",
            "source_url": "https://example.org/b",
            "license": "cc-by",
            "collected_at": "2026-04-07T00:00:01Z",
            "split_hint": "train",
        },
        {
            "phrase": "play football outside",
            "label": "Outdoor",
            "language": "en",
            "source_name": "dataset_c",
            "source_url": "https://example.org/c",
            "license": "cc-by",
            "collected_at": "2026-04-07T00:00:02Z",
            "split_hint": "train",
        },
        {
            "phrase": "office meeting",
            "label": "Indoor",
            "language": "en",
            "source_name": "dataset_d",
            "source_url": "https://example.org/d",
            "license": "cc-by-sa",
            "collected_at": "2026-04-07T00:00:03Z",
            "split_hint": "val",
        },
        {
            "phrase": "study at home",
            "label": "Indoor",
            "language": "en",
            "source_name": "dataset_d",
            "source_url": "https://example.org/d",
            "license": "cc-by-sa",
            "collected_at": "2026-04-07T00:00:04Z",
            "split_hint": "val",
        },
        {
            "phrase": "idk",
            "label": "Unclear",
            "language": "en",
            "source_name": "dataset_e",
            "source_url": "https://example.org/e",
            "license": "cc-by",
            "collected_at": "2026-04-07T00:00:05Z",
            "split_hint": "train",
        },
    ]

    output_path = tmp_path / "cleaned.jsonl"
    pipeline = QualityPipeline(QualityConfig(output_jsonl_path=str(output_path)))
    report = pipeline.run(rows)

    assert report.total_rows == 6
    assert report.valid_rows == 6
    assert report.invalid_rows == 0
    assert report.noise_removed == 1
    assert report.deduped_rows == 1
    assert report.written_rows == 4
    assert report.label_counts == {"Indoor": 2, "Outdoor": 2}
    assert report.split_counts == {"train": 2, "val": 2}

    lines = output_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 4
    parsed = [json.loads(line) for line in lines]
    assert {row["label"] for row in parsed} == {"Indoor", "Outdoor"}
    for row in parsed:
        expected_hash = hashlib.sha256(
            f"{row['label'].lower()}:{normalize_phrase(row['phrase'])}".encode("utf-8")
        ).hexdigest()
        assert row["record_hash"] == expected_hash
