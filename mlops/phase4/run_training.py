from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from mlops.phase4.training import TrainingConfig, train_phase4


BASE = Path(__file__).resolve().parent


def main() -> None:
    report = train_phase4(
        TrainingConfig(
            train_path=str(BASE / "samples" / "train.jsonl"),
            val_path=str(BASE / "samples" / "val.jsonl"),
            test_path=str(BASE / "samples" / "test.jsonl"),
            hardset_path=str(BASE / "samples" / "hardset.jsonl"),
            artifact_dir=str(BASE / "artifacts"),
        )
    )

    print("Phase 4 training completed")
    print(f"champion_model={report.champion_model}")
    print(f"val_macro_f1={report.val_macro_f1:.4f}")
    print(f"val_accuracy={report.val_accuracy:.4f}")
    print(f"test_macro_f1={report.test_macro_f1:.4f}")
    print(f"test_accuracy={report.test_accuracy:.4f}")
    print(f"hardset_macro_f1={report.hardset_macro_f1:.4f}")
    print(f"hardset_accuracy={report.hardset_accuracy:.4f}")
    print(f"temperature={report.temperature:.2f}")
    print(f"report_path={report.report_path}")
    print(f"tokenizer_path={report.tokenizer_path}")
    print(f"model_path={report.model_path}")


if __name__ == "__main__":
    main()
