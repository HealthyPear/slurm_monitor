"""SLURM sacct (accounting) data collection"""

import subprocess
from datetime import datetime, timedelta
import pandas as pd
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class SacctCollector:
    """Collects historical job data using sacct command"""

    def __init__(self, config=None):
        """Initialize sacct collector

        Args:
            config: Config object with sacct settings. If None, uses defaults.
        """
        self.config = config

        # Set defaults
        self.timeout = 120
        self.include_all_users = False
        self.format_fields = [
            "JobID",
            "JobName",
            "User",
            "Account",
            "Start",
            "End",
            "CPUTime",
            "AllocCPUS",
            "State",
            "ExitCode",
        ]

        # Override with config if provided
        if config:
            self.timeout = config.get("sacct.timeout", self.timeout)
            self.include_all_users = config.get("sacct.include_all_users", self.include_all_users)
            format_fields = config.get("sacct.format_fields")
            if format_fields:
                self.format_fields = format_fields

    def collect(self) -> pd.DataFrame:
        """Collect accounting data"""
        try:
            return self.get_jobs(days=30)
        except Exception as e:
            logger.error(f"Failed to collect sacct data: {e}")
            return pd.DataFrame()

    def get_jobs(self, days: int = 30, user: Optional[str] = None) -> pd.DataFrame:
        """
        Get job history from sacct

        Args:
            days: Number of days to look back
            user: Optional user filter

        Returns:
            DataFrame with job history
        """
        start_time = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%S")

        cmd = [
            "sacct",
            f"--starttime={start_time}",
            f"--format={','.join(self.format_fields)}",
            "--parsable2",
        ]

        # Add -a flag if configured to include all users
        if self.include_all_users:
            cmd.insert(1, "-a")

        if user:
            cmd.extend(["-u", user])

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout,
            )
            if result.returncode != 0:
                logger.warning(f"sacct returned non-zero exit code: {result.stderr}")
                return pd.DataFrame()

            # Parse output
            return self._parse_sacct_output(result.stdout)

        except subprocess.TimeoutExpired:
            logger.error(f"sacct command timed out after {self.timeout}s")
            return pd.DataFrame()
        except FileNotFoundError:
            logger.error("sacct command not found - SLURM may not be installed")
            return pd.DataFrame()

    def _parse_sacct_output(self, output: str) -> pd.DataFrame:
        """Parse sacct output into DataFrame"""
        if not output.strip():
            return pd.DataFrame()

        lines = output.strip().split("\n")
        if not lines:
            return pd.DataFrame()

        # Parse header
        headers = lines[0].split("|")
        data = []

        for line in lines[1:]:
            if not line.strip():
                continue
            values = line.split("|")
            data.append(dict(zip(headers, values)))

        df = pd.DataFrame(data)

        # Convert numeric columns
        numeric_cols = ["AllocCPUS", "CPUTime"]
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        # Convert datetime columns
        for col in ["Start", "End"]:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors="coerce")

        return df

    def get_users(self, days: int = 30) -> List[str]:
        """Get list of users with jobs in the specified period"""
        jobs = self.get_jobs(days=days)
        if jobs.empty:
            return []
        return jobs["User"].unique().tolist()

    def get_user_stats(self, days: int = 30) -> Dict:
        """Get per-user statistics"""
        users = self.get_users(days=days)
        stats = {}
        for user in users:
            jobs = self.get_jobs(days=days, user=user)
            stats[user] = {
                "job_count": len(jobs),
                "total_cpu_hours": jobs["CPUTime"].sum() if "CPUTime" in jobs.columns else 0,
                "total_cores": jobs["AllocCPUS"].sum() if "AllocCPUS" in jobs.columns else 0,
            }
        return stats
