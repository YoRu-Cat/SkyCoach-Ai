from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime
from .schema import ModelVersion


class ModelVersionRegistry:
    """Manage multiple model versions with rollback capability."""

    def __init__(self, registry_dir: str | Path) -> None:
        self.registry_dir = Path(registry_dir)
        self.registry_dir.mkdir(parents=True, exist_ok=True)
        self.versions_file = self.registry_dir / "model_versions.jsonl"

    def register_model(
        self,
        version_id: str,
        model_path: str,
        tokenizer_path: str,
        training_data_size: int,
        val_macro_f1: float,
        test_macro_f1: float,
        hardset_macro_f1: float,
        parent_version: str | None = None,
        reason: str = "",
    ) -> None:
        """Register a newly trained model version."""
        version = {
            "version_id": version_id,
            "model_path": model_path,
            "tokenizer_path": tokenizer_path,
            "created_at": datetime.utcnow().isoformat() + "Z",
            "training_data_size": training_data_size,
            "val_macro_f1": val_macro_f1,
            "test_macro_f1": test_macro_f1,
            "hardset_macro_f1": hardset_macro_f1,
            "parent_version": parent_version,
            "is_active": False,
            "reason": reason,
        }
        with self.versions_file.open("a", encoding="utf-8") as f:
            f.write(json.dumps(version) + "\n")

    def get_active_model(self) -> dict | None:
        """Get currently active model version."""
        if not self.versions_file.exists():
            return None
        with self.versions_file.open("r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    version = json.loads(line)
                    if version.get("is_active"):
                        return version
        return None

    def set_active_model(self, version_id: str) -> None:
        """Promote a version to active (can be rollback)."""
        if not self.versions_file.exists():
            return

        lines = []
        with self.versions_file.open("r", encoding="utf-8") as f:
            lines = f.readlines()

        with self.versions_file.open("w", encoding="utf-8") as f:
            for line in lines:
                if line.strip():
                    version = json.loads(line)
                    if version["version_id"] == version_id:
                        version["is_active"] = True
                    else:
                        version["is_active"] = False
                    f.write(json.dumps(version) + "\n")

    def list_versions(self) -> list[dict]:
        """List all model versions."""
        if not self.versions_file.exists():
            return []
        versions = []
        with self.versions_file.open("r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    versions.append(json.loads(line))
        return versions

    def get_version(self, version_id: str) -> dict | None:
        """Get specific model version."""
        if not self.versions_file.exists():
            return None
        with self.versions_file.open("r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    version = json.loads(line)
                    if version["version_id"] == version_id:
                        return version
        return None
