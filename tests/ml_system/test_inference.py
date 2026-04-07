from pathlib import Path
import json

from ml_system.inference.engine import InferenceEngine
from ml_system.schemas import PredictionRequest
from ml_system.training.trainer import Trainer


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row) + "\n")


def test_inference_engine_loads_and_predicts(tmp_path: Path):
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

    _write_jsonl(train_path, train_rows)
    _write_jsonl(val_path, val_rows)
    _write_jsonl(test_path, val_rows)
    _write_jsonl(hardset_path, val_rows)

    Trainer(train_path, val_path, test_path, hardset_path, artifacts).train()

    engine = InferenceEngine(
        tokenizer_path=artifacts / "tokenizer.json",
        model_path=artifacts / "model.json",
        report_path=artifacts / "report.json",
        confidence_threshold=0.72,
    )

    response = engine.predict(PredictionRequest(phrase="I take the bus to work"))

    assert response.label in ["Indoor", "Outdoor", "Mixed", "Unclear"]
    assert 0.0 <= response.confidence <= 1.0
    assert len(response.all_scores) > 0
    assert response.model == engine.model_name
