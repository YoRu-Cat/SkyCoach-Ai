import json
from pathlib import Path

from mlops.phase1.ingestion.adapters import InMemoryAdapter
from mlops.phase1.ingestion.pipeline import IngestionConfig, IngestionPipeline


def test_phase1_ingestion_dedupes_and_validates(tmp_path: Path):
    rows = [
        {
            "phrase": "going to uni",
            "language": "en",
            "source_name": "dataset_a",
            "source_url": "https://example.org/a",
            "license": "cc-by",
            "collected_at": "2026-04-07T00:00:00Z",
            "split_hint": "train",
        },
        {
            "phrase": "Going to UNI",
            "language": "en",
            "source_name": "dataset_b",
            "source_url": "https://example.org/b",
            "license": "cc-by",
            "collected_at": "2026-04-07T00:00:01Z",
            "split_hint": "train",
        },
        {
            "phrase": "ok",
            "language": "en",
            "source_name": "dataset_c",
            "source_url": "https://example.org/c",
            "license": "cc-by",
            "collected_at": "2026-04-07T00:00:02Z",
            "split_hint": "train",
        },
        {
            "phrase": "office meeting",
            "language": "en",
            "source_name": "dataset_a",
            "source_url": "https://example.org/a",
            "license": "cc-by-sa",
            "collected_at": "2026-04-07T00:00:03Z",
            "split_hint": "val",
        },
    ]

    adapter = InMemoryAdapter(rows)
    output_path = tmp_path / "ingested.jsonl"

    pipeline = IngestionPipeline(IngestionConfig(output_jsonl_path=str(output_path)))
    report = pipeline.run(adapter.read())

    assert report.total_rows == 4
    assert report.valid_rows == 3
    assert report.invalid_rows == 1
    assert report.deduped_rows == 1
    assert report.written_rows == 2

    lines = output_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 2

    parsed = [json.loads(line) for line in lines]
    assert all("record_hash" in row for row in parsed)
    assert all("source" in row for row in parsed)
