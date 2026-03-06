"""SLURM sinfo (cluster state) data collection"""

import subprocess
import pandas as pd
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class SinfoCollector:
    """Collects current cluster node state using sinfo command"""

    def __init__(self, timeout: int = 30):
        """Initialize sinfo collector"""
        self.timeout = timeout

    def collect(self) -> pd.DataFrame:
        """Collect cluster state data"""
        try:
            return self.get_nodes()
        except Exception as e:
            logger.error(f"Failed to collect sinfo data: {e}")
            return pd.DataFrame()

    def get_nodes(self) -> pd.DataFrame:
        """
        Get current cluster node state

        Returns:
            DataFrame with node information
        """
        cmd = [
            "sinfo",
            "-h",
            "--format=%N|%t|%c|%m|%z|%Z|%G",
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout,
            )
            if result.returncode != 0:
                logger.warning(f"sinfo returned non-zero exit code: {result.stderr}")
                return pd.DataFrame()

            return self._parse_sinfo_output(result.stdout)

        except subprocess.TimeoutExpired:
            logger.error(f"sinfo command timed out after {self.timeout}s")
            return pd.DataFrame()
        except FileNotFoundError:
            logger.error("sinfo command not found")
            return pd.DataFrame()

    def _parse_sinfo_output(self, output: str) -> pd.DataFrame:
        """Parse sinfo output into DataFrame"""
        if not output.strip():
            return pd.DataFrame()

        lines = output.strip().split("\n")
        if not lines:
            return pd.DataFrame()

        headers = [
            "Nodename",
            "State",
            "CPUs",
            "Memory",
            "CPUs_per_node",
            "Sockets",
            "GPUs",
        ]
        data = []

        for line in lines:
            if not line.strip():
                continue
            values = line.split("|")
            data.append(dict(zip(headers, values)))

        df = pd.DataFrame(data)

        # Convert numeric columns
        for col in ["CPUs", "Memory", "Sockets"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        return df

    def get_summary(self) -> dict:
        """Get summary of cluster state"""
        nodes = self.get_nodes()
        if nodes.empty:
            return {}

        total_cpus = nodes["CPUs"].sum()
        total_memory = nodes["Memory"].sum()
        states = nodes["State"].value_counts().to_dict()

        return {
            "total_cpus": total_cpus,
            "total_memory_mb": total_memory,
            "node_states": states,
            "total_nodes": len(nodes),
        }
