"""Collector for SLURM sreport command output"""

import subprocess
import logging
from typing import Dict, List, Any, Optional
import pandas as pd

from slurm_monitoring.config import Config

logger = logging.getLogger(__name__)


class SreportCollector:
    """Collects cluster accounting reports from sreport command"""

    def __init__(self, config_file: Optional[str] = None):
        """Initialize sreport collector

        Args:
            config_file: Path to SLURM configuration file
        """
        self.config = Config(config_file or "slurm_config.yaml")
        self.sreport_config = self.config.config.get("sreport", {})
        self.timeout = self.sreport_config.get("timeout", 120)

    def get_account_utilization_by_user(
        self, start_time: Optional[str] = None, end_time: Optional[str] = None
    ) -> Optional[pd.DataFrame]:
        """Get account utilization by user

        Args:
            start_time: Start time (e.g., "2026-01-01") or None for all available
            end_time: End time (e.g., "2026-03-06") or None for all available

        Returns:
            DataFrame with columns: Cluster, Account, User, ProportionUsed, TRESUsageOutDataVolume, etc.
        """
        cmd = ["sreport", "cluster", "AccountUtilByUser"]

        if start_time:
            cmd.extend(["Start={}".format(start_time)])
        if end_time:
            cmd.extend(["End={}".format(end_time)])

        cmd.append("format=Cluster,Account,User,TRESUsageOutCPU,ProportionUsed")

        return self._run_sreport_command(cmd)

    def get_account_utilization_by_account(
        self, start_time: Optional[str] = None, end_time: Optional[str] = None
    ) -> Optional[pd.DataFrame]:
        """Get account utilization by account

        Args:
            start_time: Start time (e.g., "2026-01-01")
            end_time: End time (e.g., "2026-03-06")

        Returns:
            DataFrame with account-level statistics
        """
        cmd = ["sreport", "cluster", "AccountUtilByAccount"]

        if start_time:
            cmd.extend(["Start={}".format(start_time)])
        if end_time:
            cmd.extend(["End={}".format(end_time)])

        cmd.append("format=Cluster,Account,TRESUsageOutCPU,ProportionUsed")

        return self._run_sreport_command(cmd)

    def get_top_users(
        self, start_time: Optional[str] = None, end_time: Optional[str] = None, limit: int = 10
    ) -> Optional[pd.DataFrame]:
        """Get top users by resource usage

        Args:
            start_time: Start time
            end_time: End time
            limit: Number of top users to return

        Returns:
            DataFrame with top users sorted by CPU usage
        """
        cmd = ["sreport", "user", "TopUsage"]

        if start_time:
            cmd.extend(["Start={}".format(start_time)])
        if end_time:
            cmd.extend(["End={}".format(end_time)])

        cmd.append("format=User,Account,CPU,CPUCount")

        df = self._run_sreport_command(cmd)
        if df is not None and not df.empty:
            df = df.sort_values("CPU", ascending=False).head(limit)

        return df

    def get_cluster_utilization(
        self, start_time: Optional[str] = None, end_time: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get overall cluster utilization summary

        Args:
            start_time: Start time
            end_time: End time

        Returns:
            Dict with cluster utilization metrics
        """
        cmd = ["sreport", "cluster", "Utilization"]

        if start_time:
            cmd.extend(["Start={}".format(start_time)])
        if end_time:
            cmd.extend(["End={}".format(end_time)])

        cmd.append("format=Cluster,Allocated,Down,Idle,Other,OverSubscribed,PlannedDown,Reserved")

        df = self._run_sreport_command(cmd)

        if df is None or df.empty:
            return {}

        # Convert to dictionary
        row = df.iloc[0]
        return {
            "cluster": row.get("Cluster"),
            "allocated": row.get("Allocated"),
            "down": row.get("Down"),
            "idle": row.get("Idle"),
            "other": row.get("Other"),
            "over_subscribed": row.get("OverSubscribed"),
            "planned_down": row.get("PlannedDown"),
            "reserved": row.get("Reserved"),
        }

    def _run_sreport_command(self, cmd: List[str]) -> Optional[pd.DataFrame]:
        """Run sreport command and parse output

        Args:
            cmd: Command list (e.g., ["sreport", "cluster", "AccountUtilByUser", ...])

        Returns:
            DataFrame with parsed output, or None on error
        """
        try:
            # Add common options
            cmd = cmd + ["--parsable2", "--noheader"]

            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=self.timeout, check=False
            )

            if result.returncode != 0:
                logger.warning(f"sreport command failed: {result.stderr}")
                return None

            if not result.stdout.strip():
                logger.warning("sreport returned empty output")
                return None

            # Parse output
            lines = result.stdout.strip().split("\n")
            if not lines:
                return None

            # Parse CSV with pipe delimiter
            data = []
            for line in lines:
                if line:
                    data.append(line.split("|"))

            # Get headers from command format=... argument
            headers = self._extract_headers_from_command(cmd)

            if not headers or not data:
                return pd.DataFrame()

            # Ensure consistent column count
            for row in data:
                while len(row) < len(headers):
                    row.append("")

            df = pd.DataFrame(data, columns=headers)
            return df

        except subprocess.TimeoutExpired:
            logger.error(f"sreport command timed out after {self.timeout}s")
            return None
        except Exception as e:
            logger.error(f"Error running sreport: {e}")
            return None

    def _extract_headers_from_command(self, cmd: List[str]) -> List[str]:
        """Extract column headers from format= argument

        Args:
            cmd: Command list

        Returns:
            List of header names
        """
        for arg in cmd:
            if arg.startswith("format="):
                headers = arg.replace("format=", "").split(",")
                return [h.strip() for h in headers]

        return []
