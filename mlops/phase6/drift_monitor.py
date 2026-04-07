from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass


@dataclass(frozen=True)
class DriftMetrics:
    """Model performance metrics snapshot."""
    timestamp: str
    prediction_count: int
    avg_confidence: float
    label_distribution: dict[str, int]
    uncertain_count: int


class DriftMonitor:
    """Track model performance and detect drift."""

    def __init__(self, monitor_dir: str | Path) -> None:
        self.monitor_dir = Path(monitor_dir)
        self.monitor_dir.mkdir(parents=True, exist_ok=True)
        self.metrics_file = self.monitor_dir / "drift_metrics.jsonl"
        self.drift_alerts = self.monitor_dir / "drift_alerts.jsonl"

    def log_metrics_snapshot(
        self,
        prediction_count: int,
        avg_confidence: float,
        label_distribution: dict[str, int],
        uncertain_count: int,
    ) -> None:
        """Record periodic performance snapshot."""
        metrics = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "prediction_count": prediction_count,
            "avg_confidence": avg_confidence,
            "label_distribution": label_distribution,
            "uncertain_count": uncertain_count,
        }
        with self.metrics_file.open("a", encoding="utf-8") as f:
            f.write(json.dumps(metrics) + "\n")

    def detect_drift(self, threshold_confidence_drop: float = 0.05) -> bool:
        """Detect significant performance degradation by comparing recent metrics."""
        if not self.metrics_file.exists():
            return False

        records = []
        with self.metrics_file.open("r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    records.append(json.loads(line))

        if len(records) < 2:
            return False

        early = records[0]["avg_confidence"]
        recent = records[-1]["avg_confidence"]

        confidence_drop = early - recent
        if confidence_drop > threshold_confidence_drop:
            alert = {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "alert_type": "confidence_degradation",
                "early_confidence": early,
                "recent_confidence": recent,
                "drop": confidence_drop,
                "threshold": threshold_confidence_drop,
                "message": f"Model confidence dropped by {confidence_drop:.2%}",
            }
            with self.drift_alerts.open("a", encoding="utf-8") as f:
                f.write(json.dumps(alert) + "\n")
            return True

        return False

    def get_active_alerts(self) -> list[dict]:
        """Retrieve all drift alerts."""
        if not self.drift_alerts.exists():
            return []
        alerts = []
        with self.drift_alerts.open("r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    alerts.append(json.loads(line))
        return alerts
