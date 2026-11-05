"""Historical data collection and analysis"""

import json
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd
import logging
from typing import Dict

logger = logging.getLogger(__name__)


class HistoryCollector:
    """Collects and analyzes queue snapshots over time"""

    def __init__(self, data_dir: str = "~/.slurm_monitoring/data"):
        """Initialize history collector

        Args:
            data_dir: Directory to store historical snapshots
        """
        self.data_dir = Path(data_dir).expanduser()
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.queue_file = self.data_dir / "queue_snapshots.jsonl"

    def record_snapshot(self, queue_summary: Dict) -> None:
        """Record current queue state with timestamp

        Args:
            queue_summary: Dictionary from squeue.get_summary()
        """
        try:
            snapshot = {
                "timestamp": datetime.now().isoformat(),
                **queue_summary,
            }

            with open(self.queue_file, "a") as f:
                f.write(json.dumps(snapshot) + "\n")

            logger.info(f"Recorded snapshot: {snapshot['total']} total jobs")
        except Exception as e:
            logger.error(f"Failed to record snapshot: {e}")

    def get_trends(self, hours: int = 24) -> Dict:
        """Analyze trends over the last N hours

        Args:
            hours: Number of hours to analyze

        Returns:
            Dictionary with trend analysis
        """
        if not self.queue_file.exists():
            return {}

        try:
            snapshots = []
            cutoff_time = datetime.now() - timedelta(hours=hours)

            with open(self.queue_file, "r") as f:
                for line in f:
                    if not line.strip():
                        continue
                    data = json.loads(line)
                    ts = datetime.fromisoformat(data["timestamp"])
                    if ts >= cutoff_time:
                        snapshots.append(data)

            if not snapshots:
                return {}

            df = pd.DataFrame(snapshots)

            return {
                "hours_analyzed": hours,
                "snapshots_collected": len(snapshots),
                "avg_running": float(df["running"].mean()),
                "max_running": int(df["running"].max()),
                "min_running": int(df["running"].min()),
                "avg_pending": float(df["pending"].mean()),
                "max_pending": int(df["pending"].max()),
                "min_pending": int(df["pending"].min()),
                "avg_total": float(df["total"].mean()),
                "max_total": int(df["total"].max()),
                "min_total": int(df["total"].min()),
                "latest_snapshot": snapshots[-1],
            }
        except Exception as e:
            logger.error(f"Failed to analyze trends: {e}")
            return {}
