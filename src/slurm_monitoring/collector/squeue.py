"""SLURM squeue (job queue) data collection"""

import subprocess
import pandas as pd
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class SqueueCollector:
    """Collects current job queue state using squeue command"""

    def __init__(self, config=None):
        """Initialize squeue collector

        Args:
            config: Config object with squeue settings. If None, uses defaults.
        """
        self.config = config
        self.timeout = 30
        self.format_fields = [
            "JobID",
            "User",
            "Name",
            "State",
            "CPUs",
            "TimeLimit",
            "StartTime",
        ]

        if config:
            self.timeout = config.get("squeue.timeout", self.timeout)
            format_fields = config.get("squeue.format_fields")
            if format_fields:
                self.format_fields = format_fields

    def collect(self) -> pd.DataFrame:
        """Collect job queue data"""
        try:
            return self.get_jobs()
        except Exception as e:
            logger.error(f"Failed to collect squeue data: {e}")
            return pd.DataFrame()

    def get_jobs(self) -> pd.DataFrame:
        """
        Get currently running and queued jobs

        Returns:
            DataFrame with job queue information
        """
        cmd = [
            "squeue",
            "-h",
            "--format=%i|%j|%u|%a|%t|%C|%m|%S|%e",
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout,
            )
            if result.returncode != 0:
                logger.warning(f"squeue returned non-zero exit code: {result.stderr}")
                return pd.DataFrame()

            return self._parse_squeue_output(result.stdout)

        except subprocess.TimeoutExpired:
            logger.error(f"squeue command timed out after {self.timeout}s")
            return pd.DataFrame()
        except FileNotFoundError:
            logger.error("squeue command not found")
            return pd.DataFrame()

    def _parse_squeue_output(self, output: str) -> pd.DataFrame:
        """Parse squeue output into DataFrame"""
        if not output.strip():
            return pd.DataFrame()

        lines = output.strip().split("\n")
        if not lines:
            return pd.DataFrame()

        headers = [
            "JobID",
            "JobName",
            "User",
            "Account",
            "State",
            "CPUs",
            "Memory",
            "StartTime",
            "EndTime",
        ]
        data = []

        for line in lines:
            if not line.strip():
                continue
            values = line.split("|")
            data.append(dict(zip(headers, values)))

        df = pd.DataFrame(data)

        # Convert numeric columns
        for col in ["CPUs"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        return df

    def get_summary(self) -> dict:
        """Get summary of current job queue"""
        jobs = self.get_jobs()
        if jobs.empty:
            return {"running": 0, "pending": 0, "total": 0}

        summary = {
            "running": len(jobs[jobs["State"] == "RUNNING"]),
            "pending": len(jobs[jobs["State"] == "PENDING"]),
            "total": len(jobs),
            "total_cpus_in_use": jobs[jobs["State"] == "RUNNING"]["CPUs"].sum(),
        }
        return summary
