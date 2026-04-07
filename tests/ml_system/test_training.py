import json
from pathlib import Path

from ml_system.training.trainer import Trainer


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row) + "\n")


def test_training_produces_artifacts_and_metrics(tmp_path: Path):
    train_path = tmp_path / "train.jsonl"
    val_path = tmp_path / "val.jsonl"
    test_path = tmp_path / "test.jsonl"
    hardset_path = tmp_path / "hardset.jsonl"
    artifacts = tmp_path / "artifacts"

    train_rows = [
        {"phrase": "office meeting", "label": "Indoor"},
        {"phrase": "study at home", "label": "Indoor"},
        {"phrase": "go to park", "label": "Outdoor"},
        {"phrase": "cycling outside", "label": "Outdoor"},
        {"phrase": "work then gym", "label": "Mixed"},
        {"phrase": "idk what", "label": "Unclear"},
    ]
    val_rows = [
        {"phrase": "meeting in office", "label": "Indoor"},
        {"phrase": "walk to uni", "label": "Outdoor"},
        {"phrase": "study and football", "label": "Mixed"},
        {"phrase": "random stuff", "label": "Unclear"},
    ]
    test_rows = val_rows
    hardset_rows = val_rows

    _write_jsonl(train_path, train_rows)
    _write_jsonl(val_path, val_rows)
    _write_jsonl(test_path, test_rows)
    _write_jsonl(hardset_path, hardset_rows)

    report = Trainer(train_path, val_path, test_path, hardset_path, artifacts).train()

    assert report["champion_model"] in {"naive_bayes", "linear_softmax"}
    assert 0.0 <= report["val_f1"] <= 1.0
    assert 0.0 <= report["test_f1"] <= 1.0
    assert 0.0 <= report["hardset_f1"] <= 1.0
    assert report["temperature"] >= 0.5

    assert (artifacts / "report.json").exists()
    assert (artifacts / "training_report.json").exists()
    assert (artifacts / "tokenizer.json").exists()
    assert (artifacts / "model.json").exists()
