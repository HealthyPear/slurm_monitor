"""Pattern analysis for SLURM job data"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime, timedelta


class PatternAnalyzer:
    """Analyzes patterns in job submissions and resource usage"""

    def __init__(self, jobs_data: Optional[pd.DataFrame] = None):
        """Initialize pattern analyzer"""
        self.jobs_data = jobs_data if jobs_data is not None else pd.DataFrame()

    def find_peak_times(self) -> Dict:
        """
        Identify peak usage times

        Returns:
            Dictionary with peak time information
        """
        if self.jobs_data.empty:
            return {}

        df = self.jobs_data.copy()

        # Ensure Start is datetime
        if "Start" in df.columns:
            df["Start"] = pd.to_datetime(df["Start"], errors="coerce")
            df = df.dropna(subset=["Start"])

        if df.empty:
            return {}

        # Extract hour of day
        df["hour"] = df["Start"].dt.hour

        # Count jobs per hour
        hourly_counts = df.groupby("hour").size()

        # Find peak hour
        peak_hour = hourly_counts.idxmax()
        peak_count = hourly_counts.max()

        # Get top hours
        top_hours = hourly_counts.nlargest(5).to_dict()

        return {
            "peak_hour": int(peak_hour),
            "jobs_at_peak": int(peak_count),
            "top_hours": {int(k): int(v) for k, v in top_hours.items()},
        }

    def find_idle_periods(self) -> List[Dict]:
        """
        Identify periods with low or zero utilization

        Returns:
            List of idle periods
        """
        if self.jobs_data.empty:
            return []

        df = self.jobs_data.copy()

        # Ensure we have datetime columns
        if "Start" in df.columns:
            df["Start"] = pd.to_datetime(df["Start"], errors="coerce")
        if "End" in df.columns:
            df["End"] = pd.to_datetime(df["End"], errors="coerce")

        df = df.dropna(subset=["Start", "End"])

        if df.empty:
            return []

        # Sort by start time
        df = df.sort_values("Start")

        # Find gaps between jobs
        idle_periods = []
        prev_end = df["Start"].min()

        for idx, row in df.iterrows():
            if row["Start"] > prev_end:
                gap = (row["Start"] - prev_end).total_seconds() / 3600
                idle_periods.append(
                    {
                        "start": prev_end.isoformat(),
                        "end": row["Start"].isoformat(),
                        "duration_hours": gap,
                    }
                )
            prev_end = max(prev_end, row["End"])

        # Filter for significant idle periods (> 1 hour)
        return [p for p in idle_periods if p["duration_hours"] > 1]

    def get_day_of_week_distribution(self) -> Dict:
        """Get job distribution by day of week"""
        if self.jobs_data.empty:
            return {}

        df = self.jobs_data.copy()

        if "Start" in df.columns:
            df["Start"] = pd.to_datetime(df["Start"], errors="coerce")
            df = df.dropna(subset=["Start"])

        if df.empty:
            return {}

        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        df["day_of_week"] = df["Start"].dt.day_name()

        distribution = df["day_of_week"].value_counts().to_dict()

        return {day: distribution.get(day, 0) for day in days}

    def get_job_submission_rate(self) -> Dict:
        """Get job submission rate over time"""
        if self.jobs_data.empty:
            return {}

        df = self.jobs_data.copy()

        if "Start" in df.columns:
            df["Start"] = pd.to_datetime(df["Start"], errors="coerce")
            df_indexed = df.dropna(subset=["Start"]).set_index("Start")

            # Resample to daily rate
            daily_rate = df_indexed.resample("1D").size()

            return {
                "mean_jobs_per_day": float(daily_rate.mean()),
                "max_jobs_per_day": int(daily_rate.max()),
                "min_jobs_per_day": int(daily_rate.min()),
            }

        return {}
