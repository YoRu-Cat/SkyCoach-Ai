from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from mlops.phase1.ingestion.adapters import JsonlFileAdapter
from mlops.phase1.ingestion.pipeline import IngestionConfig, IngestionPipeline


BASE = Path(__file__).resolve().parent


def main() -> None:
    input_path = BASE / "samples" / "sample_ingestion.jsonl"
    output_path = BASE / "outputs" / "phase1_ingested.jsonl"

    adapter = JsonlFileAdapter(str(input_path))
    pipeline = IngestionPipeline(IngestionConfig(output_jsonl_path=str(output_path)))
    report = pipeline.run(adapter.read())

    print("Phase 1 ingestion completed")
    print(f"total_rows={report.total_rows}")
    print(f"valid_rows={report.valid_rows}")
    print(f"invalid_rows={report.invalid_rows}")
    print(f"deduped_rows={report.deduped_rows}")
    print(f"written_rows={report.written_rows}")
    print(f"output_path={report.output_path}")


if __name__ == "__main__":
    main()
