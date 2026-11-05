"""Data aggregation for SLURM statistics"""

import pandas as pd
from typing import Dict, Optional


class DataAggregator:
    """Aggregates SLURM data by various dimensions"""

    def __init__(self, jobs_data: Optional[pd.DataFrame] = None):
        """Initialize data aggregator"""
        self.jobs_data = jobs_data if jobs_data is not None else pd.DataFrame()

    def aggregate_by_user(self) -> Dict:
        """
        Aggregate resource usage by user

        Returns:
            Dictionary with per-user statistics
        """
        if self.jobs_data.empty or "User" not in self.jobs_data.columns:
            return {}

        user_stats = {}
        grouped = self.jobs_data.groupby("User")

        for user, group in grouped:
            user_stats[user] = {
                "job_count": len(group),
                "total_cores_allocated": float(
                    group["AllocCPUS"].sum() if "AllocCPUS" in group.columns else 0
                ),
                "average_cores_per_job": float(
                    group["AllocCPUS"].mean() if "AllocCPUS" in group.columns else 0
                ),
                "total_cpu_hours": float(
                    group["CPUTime"].sum() / 60 if "CPUTime" in group.columns else 0
                ),
            }

        return user_stats

    def aggregate_by_account(self) -> Dict:
        """
        Aggregate resource usage by account

        Returns:
            Dictionary with per-account statistics
        """
        if self.jobs_data.empty or "Account" not in self.jobs_data.columns:
            return {}

        account_stats = {}
        grouped = self.jobs_data.groupby("Account")

        for account, group in grouped:
            account_stats[account] = {
                "job_count": len(group),
                "total_cores_allocated": float(
                    group["AllocCPUS"].sum() if "AllocCPUS" in group.columns else 0
                ),
                "average_cores_per_job": float(
                    group["AllocCPUS"].mean() if "AllocCPUS" in group.columns else 0
                ),
                "number_of_users": len(group["User"].unique()) if "User" in group.columns else 0,
            }

        return account_stats

    def job_durations(self) -> pd.Series:
        """
        Per-job durations in minutes

        Returns:
            Series of durations (empty if no usable Start/End data)
        """
        if self.jobs_data.empty:
            return pd.Series(dtype=float)

        df = self.jobs_data.copy()

        # Ensure datetime columns
        if "Start" in df.columns:
            df["Start"] = pd.to_datetime(df["Start"], errors="coerce")
        if "End" in df.columns:
            df["End"] = pd.to_datetime(df["End"], errors="coerce")

        df = df.dropna(subset=["Start", "End"])
        return (df["End"] - df["Start"]).dt.total_seconds() / 60

    def job_duration_stats(self) -> Dict:
        """
        Compute statistics about job durations

        Returns:
            Dictionary with job duration statistics
        """
        durations = self.job_durations()
        if durations.empty:
            return {}

        return {
            "average_duration_minutes": float(durations.mean()),
            "median_duration_minutes": float(durations.median()),
            "min_duration_minutes": float(durations.min()),
            "max_duration_minutes": float(durations.max()),
            "std_duration_minutes": float(durations.std()),
        }

    def job_frequency(self) -> Dict:
        """
        Compute job submission frequency

        Returns:
            Dictionary with frequency statistics
        """
        if self.jobs_data.empty or "Start" not in self.jobs_data.columns:
            return {}

        df = self.jobs_data.copy()
        df["Start"] = pd.to_datetime(df["Start"], errors="coerce")
        df = df.dropna(subset=["Start"])

        if df.empty:
            return {}

        # Total time span
        start_date = df["Start"].min()
        end_date = df["Start"].max()
        total_days = (end_date - start_date).days + 1

        return {
            "total_jobs": len(df),
            "total_days": total_days,
            "average_jobs_per_day": float(len(df) / max(total_days, 1)),
            "period_start": start_date.isoformat(),
            "period_end": end_date.isoformat(),
        }

    def aggregate_by_state(self) -> Dict:
        """Aggregate job counts by state"""
        if self.jobs_data.empty or "State" not in self.jobs_data.columns:
            return {}

        state_counts = self.jobs_data["State"].value_counts().to_dict()
        return {state: int(count) for state, count in state_counts.items()}
