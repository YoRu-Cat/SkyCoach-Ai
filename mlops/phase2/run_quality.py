from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from mlops.phase2.quality.pipeline import QualityConfig, QualityPipeline


BASE = Path(__file__).resolve().parent


def main() -> None:
    input_path = BASE / "samples" / "sample_quality.jsonl"
    output_path = BASE / "outputs" / "phase2_cleaned.jsonl"

    with input_path.open("r", encoding="utf-8") as f:
        rows = [__import__("json").loads(line) for line in f if line.strip()]

    pipeline = QualityPipeline(QualityConfig(output_jsonl_path=str(output_path)))
    report = pipeline.run(rows)

    print("Phase 2 data quality completed")
    print(f"total_rows={report.total_rows}")
    print(f"valid_rows={report.valid_rows}")
    print(f"invalid_rows={report.invalid_rows}")
    print(f"noise_removed={report.noise_removed}")
    print(f"deduped_rows={report.deduped_rows}")
    print(f"balanced_rows={report.balanced_rows}")
    print(f"written_rows={report.written_rows}")
    print(f"label_counts={report.label_counts}")
    print(f"split_counts={report.split_counts}")
    print(f"output_path={report.output_path}")


if __name__ == "__main__":
    main()
