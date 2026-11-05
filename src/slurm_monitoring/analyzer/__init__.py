"""Analysis module for SLURM cluster data"""

from .utilization import UtilizationAnalyzer
from .patterns import PatternAnalyzer
from .aggregator import DataAggregator


class ClusterAnalyzer:
    """Main analyzer for cluster statistics and patterns"""

    def __init__(self, jobs_data=None):
        """Initialize analyzer with optional job data"""
        self.jobs_data = jobs_data
        self.utilization = UtilizationAnalyzer(jobs_data)
        self.patterns = PatternAnalyzer(jobs_data)
        self.aggregator = DataAggregator(jobs_data)

    def compute_core_utilization(self):
        """Compute overall core utilization statistics"""
        return self.utilization.compute_utilization()

    def compute_core_utilization_by_time(self):
        """Compute core utilization broken down by time periods"""
        return self.utilization.utilization_by_time()

    def breakdown_by_user(self):
        """Get user-based breakdown of resource usage"""
        return self.aggregator.aggregate_by_user()

    def breakdown_by_account(self):
        """Get account-based breakdown of resource usage"""
        return self.aggregator.aggregate_by_account()

    def identify_peak_times(self):
        """Identify peak usage times"""
        return self.patterns.find_peak_times()

    def identify_idle_periods(self):
        """Identify periods of low cluster utilization"""
        return self.patterns.find_idle_periods()

    def compute_job_duration_stats(self):
        """Compute statistics about job durations"""
        return self.aggregator.job_duration_stats()

    def get_job_durations(self):
        """Per-job durations in minutes"""
        return self.aggregator.job_durations()

    def compute_job_frequency(self):
        """Compute job submission frequency over time"""
        return self.aggregator.job_frequency()

    def get_summary(self):
        """Get overall summary statistics"""
        return {
            "utilization": self.compute_core_utilization(),
            "peak_times": self.identify_peak_times(),
            "user_breakdown": self.breakdown_by_user(),
            "job_stats": self.compute_job_duration_stats(),
        }

    def export_to_csv(self, filepath: str):
        """Export analysis results to CSV"""
        from ..exporters import CSVExporter

        exporter = CSVExporter()
        exporter.export(self.get_summary(), filepath)

    def export_to_json(self, filepath: str):
        """Export analysis results to JSON"""
        from ..exporters import JSONExporter

        exporter = JSONExporter()
        exporter.export(self.get_summary(), filepath)
