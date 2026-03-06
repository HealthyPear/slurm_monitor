"""JSON export for statistics"""

import json
from pathlib import Path
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class JSONExporter:
    """Exports analysis results to JSON format"""

    def export(self, data: Dict[str, Any], filepath: str) -> bool:
        """
        Export data to JSON file

        Args:
            data: Dictionary of data to export
            filepath: Path to output JSON file

        Returns:
            True if successful, False otherwise
        """
        try:
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)

            with open(filepath, "w") as f:
                json.dump(data, f, indent=2, default=str)

            logger.info(f"Exported data to {filepath}")
            return True

        except Exception as e:
            logger.error(f"Failed to export to JSON: {e}")
            return False

    def export_user_stats(self, user_stats: Dict, filepath: str) -> bool:
        """Export per-user statistics to JSON"""
        return self.export(user_stats, filepath)

    def export_utilization(self, utilization: Dict, filepath: str) -> bool:
        """Export utilization stats to JSON"""
        return self.export(utilization, filepath)
