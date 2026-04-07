from pathlib import Path
import json
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from mlops.phase3.annotation.workflow import AnnotationConfig, AnnotationWorkflow


BASE = Path(__file__).resolve().parent


def _read_jsonl(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def main() -> None:
    rows_a = _read_jsonl(BASE / "samples" / "annotator_a.jsonl")
    rows_b = _read_jsonl(BASE / "samples" / "annotator_b.jsonl")

    workflow = AnnotationWorkflow()
    report = workflow.run(
        rows_a,
        rows_b,
        AnnotationConfig(
            merged_output_path=str(BASE / "outputs" / "merged_annotations.jsonl"),
            golden_output_path=str(BASE / "outputs" / "golden_frozen.jsonl"),
        ),
    )

    print("Phase 3 annotation workflow completed")
    print(f"total_rows_a={report.total_rows_a}")
    print(f"total_rows_b={report.total_rows_b}")
    print(f"valid_pairs={report.valid_pairs}")
    print(f"auto_agreements={report.auto_agreements}")
    print(f"resolved_conflicts={report.resolved_conflicts}")
    print(f"unresolved_conflicts={report.unresolved_conflicts}")
    print(f"frozen_golden_rows={report.frozen_golden_rows}")
    print(f"merged_output_path={report.merged_output_path}")
    print(f"golden_output_path={report.golden_output_path}")


if __name__ == "__main__":
    main()
