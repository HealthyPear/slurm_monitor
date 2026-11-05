"""CSV export for statistics"""

from pathlib import Path
from typing import Dict, Any
import pandas as pd
import logging

logger = logging.getLogger(__name__)


class CSVExporter:
    """Exports analysis results to CSV format"""

    def export(self, data: Dict[str, Any], filepath: str) -> bool:
        """
        Export dictionary data to CSV file

        Args:
            data: Dictionary of data to export
            filepath: Path to output CSV file

        Returns:
            True if successful, False otherwise
        """
        try:
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)

            # Handle nested dictionaries
            flattened = self._flatten_dict(data)
            df = pd.DataFrame([flattened])

            df.to_csv(filepath, index=False)
            logger.info(f"Exported data to {filepath}")
            return True

        except Exception as e:
            logger.error(f"Failed to export to CSV: {e}")
            return False

    def export_user_stats(self, user_stats: Dict, filepath: str) -> bool:
        """Export per-user statistics to CSV"""
        try:
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)

            # Convert user stats to DataFrame
            rows = []
            for user, stats in user_stats.items():
                row = {"user": user}
                row.update(stats)
                rows.append(row)

            df = pd.DataFrame(rows)
            df.to_csv(filepath, index=False)
            logger.info(f"Exported user stats to {filepath}")
            return True

        except Exception as e:
            logger.error(f"Failed to export user stats: {e}")
            return False

    def export_utilization(self, utilization: pd.DataFrame, filepath: str) -> bool:
        """Export utilization time series to CSV"""
        try:
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)

            if isinstance(utilization, pd.Series):
                utilization.to_csv(filepath, index=True)
            else:
                utilization.to_csv(filepath, index=False)

            logger.info(f"Exported utilization to {filepath}")
            return True

        except Exception as e:
            logger.error(f"Failed to export utilization: {e}")
            return False

    def _flatten_dict(self, data: Dict, parent_key: str = "") -> Dict:
        """Flatten nested dictionaries"""
        items: list[tuple[str, Any]] = []
        for k, v in data.items():
            new_key = f"{parent_key}_{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key).items())
            elif isinstance(v, list):
                items.append((new_key, str(v)))
            else:
                items.append((new_key, v))
        return dict(items)
