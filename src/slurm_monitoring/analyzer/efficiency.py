"""Efficiency analyzer for job performance metrics"""

import logging
from typing import Dict, List, Any
import pandas as pd

logger = logging.getLogger(__name__)


class EfficiencyAnalyzer:
    """Analyzes job efficiency metrics from seff data"""

    def __init__(self, efficiency_df: pd.DataFrame):
        """Initialize efficiency analyzer
        
        Args:
            efficiency_df: DataFrame with job efficiency data from SeffCollector
        """
        self.data = efficiency_df

    def get_summary_statistics(self) -> Dict[str, Any]:
        """Get summary statistics for job efficiency
        
        Returns:
            Dict with average, min, max efficiency metrics
        """
        if self.data.empty:
            return {}
        
        return {
            "total_jobs": len(self.data),
            "cpu_efficiency": {
                "average": self.data["cpu_efficiency"].mean(),
                "median": self.data["cpu_efficiency"].median(),
                "min": self.data["cpu_efficiency"].min(),
                "max": self.data["cpu_efficiency"].max(),
                "std": self.data["cpu_efficiency"].std(),
            },
            "memory_efficiency": {
                "average": self.data["memory_efficiency"].mean(),
                "median": self.data["memory_efficiency"].median(),
                "min": self.data["memory_efficiency"].min(),
                "max": self.data["memory_efficiency"].max(),
                "std": self.data["memory_efficiency"].std(),
            },
        }

    def categorize_efficiency(self, cpu_threshold_high: float = 80,
                             cpu_threshold_med: float = 50,
                             memory_threshold_high: float = 80,
                             memory_threshold_med: float = 50) -> Dict[str, List[str]]:
        """Categorize jobs by efficiency level
        
        Args:
            cpu_threshold_high: CPU efficiency above this is "good"
            cpu_threshold_med: CPU efficiency above this is "medium"
            memory_threshold_high: Memory efficiency above this is "good"
            memory_threshold_med: Memory efficiency above this is "medium"
            
        Returns:
            Dict with job IDs categorized by efficiency level
        """
        categories = {
            "excellent": [],
            "good": [],
            "fair": [],
            "poor": [],
            "failed": [],
        }
        
        if self.data.empty:
            return categories
        
        for _, job in self.data.iterrows():
            job_id = job["job_id"]
            state = job.get("state", "UNKNOWN")
            
            # Failed jobs
            if state in ["FAILED", "TIMEOUT", "OUT_OF_MEMORY"]:
                categories["failed"].append(job_id)
                continue
            
            # Calculate combined efficiency score
            cpu_eff = job.get("cpu_efficiency", 0) or 0
            mem_eff = job.get("memory_efficiency", 0) or 0
            avg_eff = (cpu_eff + mem_eff) / 2
            
            # Categorize
            if avg_eff >= 80:
                categories["excellent"].append(job_id)
            elif avg_eff >= 60:
                categories["good"].append(job_id)
            elif avg_eff >= 40:
                categories["fair"].append(job_id)
            else:
                categories["poor"].append(job_id)
        
        return categories

    def identify_waste_opportunities(self, cpu_threshold: float = 50,
                                    memory_threshold: float = 50) -> pd.DataFrame:
        """Identify jobs with significant waste
        
        Args:
            cpu_threshold: CPU efficiency threshold (%)
            memory_threshold: Memory efficiency threshold (%)
            
        Returns:
            DataFrame of jobs with efficiency below thresholds
        """
        if self.data.empty:
            return pd.DataFrame()
        
        # Find jobs with poor utilization in any dimension
        waste = self.data[
            (self.data["cpu_efficiency"] < cpu_threshold) |
            (self.data["memory_efficiency"] < memory_threshold)
        ].copy()
        
        # Sort by potential waste (lowest efficiency)
        waste["efficiency_score"] = (
            waste["cpu_efficiency"] + waste["memory_efficiency"]
        ) / 2
        
        return waste.sort_values("efficiency_score")

    def get_recommendations(self, cpu_threshold: float = 50,
                           memory_threshold: float = 50) -> List[str]:
        """Generate recommendations based on efficiency analysis
        
        Args:
            cpu_threshold: CPU efficiency threshold (%)
            memory_threshold: Memory efficiency threshold (%)
            
        Returns:
            List of actionable recommendations
        """
        recommendations = []
        
        if self.data.empty:
            return ["No job data available for analysis"]
        
        stats = self.get_summary_statistics()
        
        # CPU efficiency recommendations
        if stats.get("cpu_efficiency", {}).get("average", 0) < 50:
            recommendations.append(
                "⚠️ Average CPU efficiency is low. Consider: "
                "1) Increasing job parallelism, 2) Using vectorized code, "
                "3) Reducing job complexity"
            )
        
        # Memory efficiency recommendations
        if stats.get("memory_efficiency", {}).get("average", 0) < 50:
            recommendations.append(
                "⚠️ Average memory efficiency is low. Consider: "
                "1) Reducing memory allocation, 2) Implementing memory-efficient algorithms, "
                "3) Using streaming for large data"
            )
        
        # Waste opportunities
        waste = self.identify_waste_opportunities(cpu_threshold, memory_threshold)
        if len(waste) > len(self.data) * 0.2:  # More than 20% of jobs are wasteful
            recommendations.append(
                f"⚠️ {len(waste)} jobs ({len(waste)/len(self.data)*100:.1f}%) exceeded waste thresholds. "
                "Review resource requests for common patterns."
            )
        
        # Positive feedback
        if stats.get("cpu_efficiency", {}).get("average", 0) >= 70:
            recommendations.append(
                "✅ Good CPU utilization! Continue current practice."
            )
        
        if not recommendations:
            recommendations.append(
                "✅ Job efficiency looks good overall. Continue monitoring."
            )
        
        return recommendations

    def get_efficiency_by_user(self) -> pd.DataFrame:
        """Get efficiency metrics aggregated by user
        
        Returns:
            DataFrame with per-user efficiency statistics
        """
        if self.data.empty or "user" not in self.data.columns:
            return pd.DataFrame()
        
        return self.data.groupby("user").agg({
            "cpu_efficiency": ["mean", "min", "max", "count"],
            "memory_efficiency": ["mean", "min", "max"],
        })

    def get_efficiency_by_state(self) -> pd.DataFrame:
        """Get efficiency metrics aggregated by job state
        
        Returns:
            DataFrame with per-state efficiency statistics
        """
        if self.data.empty or "state" not in self.data.columns:
            return pd.DataFrame()
        
        return self.data.groupby("state").agg({
            "job_id": "count",
            "cpu_efficiency": ["mean", "min", "max"],
            "memory_efficiency": ["mean", "min", "max"],
        }).rename(columns={"job_id": "count"})
