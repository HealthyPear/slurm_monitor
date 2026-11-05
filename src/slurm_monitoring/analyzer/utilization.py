"""Core utilization analysis"""

import pandas as pd
from typing import Dict, Optional


class UtilizationAnalyzer:
    """Analyzes CPU core utilization patterns"""

    def __init__(self, jobs_data: Optional[pd.DataFrame] = None):
        """Initialize utilization analyzer"""
        self.jobs_data = jobs_data if jobs_data is not None else pd.DataFrame()

    def compute_utilization(self) -> Dict:
        """
        Compute overall core utilization statistics

        Returns:
            Dictionary with utilization metrics
        """
        if self.jobs_data.empty:
            return {
                "total_core_hours": 0,
                "average_cores_per_job": 0,
                "max_cores_used": 0,
                "min_cores_used": 0,
            }

        total_core_hours = self._compute_core_hours()
        avg_cores = self.jobs_data["AllocCPUS"].mean() if "AllocCPUS" in self.jobs_data else 0
        max_cores = self.jobs_data["AllocCPUS"].max() if "AllocCPUS" in self.jobs_data else 0
        min_cores = self.jobs_data["AllocCPUS"].min() if "AllocCPUS" in self.jobs_data else 0

        return {
            "total_core_hours": float(total_core_hours),
            "average_cores_per_job": float(avg_cores),
            "max_cores_used": float(max_cores),
            "min_cores_used": float(min_cores),
        }

    def utilization_by_time(self, bucket_size: str = "1H") -> pd.Series | pd.DataFrame:
        """
        Compute utilization broken down by time buckets

        Args:
            bucket_size: Time bucket size (e.g., '1H' for hourly, '1D' for daily)

        Returns:
            DataFrame with utilization by time period
        """
        if self.jobs_data.empty:
            return pd.DataFrame()

        df = self.jobs_data.copy()

        # Ensure we have datetime columns
        if "Start" in df.columns:
            df["Start"] = pd.to_datetime(df["Start"], errors="coerce")
        if "End" in df.columns:
            df["End"] = pd.to_datetime(df["End"], errors="coerce")

        # Remove rows with invalid timestamps
        df = df.dropna(subset=["Start", "End"])

        if df.empty:
            return pd.DataFrame()

        # Set Start as index and resample
        df_indexed = df.set_index("Start")
        utilization = df_indexed["AllocCPUS"].resample(bucket_size).sum()

        return utilization

    def _compute_core_hours(self) -> float:
        """Compute total core-hours used"""
        if self.jobs_data.empty:
            return 0.0

        if "CPUTime" in self.jobs_data:
            # CPUTime is typically in minutes
            return float(self.jobs_data["CPUTime"].sum() / 60.0)

        if "AllocCPUS" in self.jobs_data and "Start" in self.jobs_data:
            # Calculate from allocations and duration
            df = self.jobs_data.copy()
            df["Start"] = pd.to_datetime(df["Start"], errors="coerce")
            df["End"] = pd.to_datetime(df["End"], errors="coerce")
            df_valid = df.dropna(subset=["Start", "End"])

            if not df_valid.empty:
                df_valid["duration_hours"] = (
                    df_valid["End"] - df_valid["Start"]
                ).dt.total_seconds() / 3600
                return float((df_valid["AllocCPUS"] * df_valid["duration_hours"]).sum())

        return 0.0

    def get_hourly_stats(self) -> pd.Series | pd.DataFrame:
        """Get hourly utilization statistics"""
        return self.utilization_by_time(bucket_size="1H")

    def get_daily_stats(self) -> pd.Series | pd.DataFrame:
        """Get daily utilization statistics"""
        return self.utilization_by_time(bucket_size="1D")

    def get_weekly_stats(self) -> pd.Series | pd.DataFrame:
        """Get weekly utilization statistics"""
        return self.utilization_by_time(bucket_size="1W")
