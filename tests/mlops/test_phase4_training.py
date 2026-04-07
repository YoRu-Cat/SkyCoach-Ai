import json
from pathlib import Path

from mlops.phase4.training import TrainingConfig, train_phase4


def test_phase4_training_produces_artifacts_and_metrics(tmp_path: Path):
    base = Path("e:/Java/Project/Project Ai/mlops/phase4/samples")
    artifacts = tmp_path / "artifacts"

    report = train_phase4(
        TrainingConfig(
            train_path=str(base / "train.jsonl"),
            val_path=str(base / "val.jsonl"),
            test_path=str(base / "test.jsonl"),
            hardset_path=str(base / "hardset.jsonl"),
            artifact_dir=str(artifacts),
        )
    )

    assert report.champion_model in {"scratch_naive_bayes", "scratch_linear_softmax"}
    assert 0.0 <= report.val_macro_f1 <= 1.0
    assert 0.0 <= report.test_macro_f1 <= 1.0
    assert 0.0 <= report.hardset_macro_f1 <= 1.0
    assert report.temperature >= 0.5

    report_path = Path(report.report_path)
    tokenizer_path = Path(report.tokenizer_path)
    model_path = Path(report.model_path)

    assert report_path.exists()
    assert tokenizer_path.exists()
    assert model_path.exists()

    payload = json.loads(report_path.read_text(encoding="utf-8"))
    assert "val" in payload and "test" in payload and "hardset" in payload
    assert "champion_model" in payload and "temperature" in payload
