import json
from pathlib import Path

from mlops.phase3.annotation.workflow import AnnotationConfig, AnnotationWorkflow


def test_phase3_annotation_workflow_merges_resolves_and_freezes(tmp_path: Path):
    rows_a = [
        {"phrase": "going to uni", "annotator_id": "ann_a", "label": "Outdoor", "note": "", "annotated_at": "2026-04-07T10:00:00Z"},
        {"phrase": "office meeting", "annotator_id": "ann_a", "label": "Indoor", "note": "", "annotated_at": "2026-04-07T10:00:01Z"},
        {"phrase": "study then football", "annotator_id": "ann_a", "label": "Mixed", "note": "", "annotated_at": "2026-04-07T10:00:02Z"},
        {"phrase": "do something", "annotator_id": "ann_a", "label": "Unclear", "note": "", "annotated_at": "2026-04-07T10:00:03Z"},
    ]
    rows_b = [
        {"phrase": "Going to UNI", "annotator_id": "ann_b", "label": "Outdoor", "note": "", "annotated_at": "2026-04-07T10:01:00Z"},
        {"phrase": "office meeting", "annotator_id": "ann_b", "label": "Indoor", "note": "", "annotated_at": "2026-04-07T10:01:01Z"},
        {"phrase": "study then football", "annotator_id": "ann_b", "label": "Outdoor", "note": "", "annotated_at": "2026-04-07T10:01:02Z"},
        {"phrase": "do something", "annotator_id": "ann_b", "label": "Mixed", "note": "", "annotated_at": "2026-04-07T10:01:03Z"},
    ]

    merged_path = tmp_path / "merged.jsonl"
    golden_path = tmp_path / "golden.jsonl"

    workflow = AnnotationWorkflow()
    report = workflow.run(
        rows_a,
        rows_b,
        AnnotationConfig(
            merged_output_path=str(merged_path),
            golden_output_path=str(golden_path),
        ),
    )

    assert report.total_rows_a == 4
    assert report.total_rows_b == 4
    assert report.valid_pairs == 4
    assert report.auto_agreements == 2
    assert report.resolved_conflicts == 2
    assert report.unresolved_conflicts == 0
    assert report.frozen_golden_rows == 4

    merged_lines = [json.loads(line) for line in merged_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    golden_lines = [json.loads(line) for line in golden_path.read_text(encoding="utf-8").splitlines() if line.strip()]

    assert len(merged_lines) == 4
    assert len(golden_lines) == 4
    assert all(row["status"] == "resolved" for row in merged_lines)
    assert {row["label"] for row in golden_lines}.issubset({"Indoor", "Outdoor", "Mixed", "Unclear"})
