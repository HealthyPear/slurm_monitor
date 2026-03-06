"""Collection module for SLURM cluster data"""

from .sacct import SacctCollector
from .sinfo import SinfoCollector
from .squeue import SqueueCollector


class SlurmCollector:
    """Main collector that aggregates data from multiple SLURM sources"""

    def __init__(self):
        """Initialize collector with sub-collectors"""
        self.sacct = SacctCollector()
        self.sinfo = SinfoCollector()
        self.squeue = SqueueCollector()

    def collect_all(self):
        """Collect data from all sources"""
        sacct_data = self.sacct.collect()
        sinfo_data = self.sinfo.collect()
        squeue_data = self.squeue.collect()

        return {
            "accounting": sacct_data,
            "cluster_state": sinfo_data,
            "running_jobs": squeue_data,
        }

    def get_job_history(self, days: int = 30):
        """Get historical job data from accounting"""
        return self.sacct.get_jobs(days=days)

    def get_cluster_state(self):
        """Get current cluster state"""
        return self.sinfo.get_nodes()

    def get_running_jobs(self):
        """Get currently running jobs"""
        return self.squeue.get_jobs()
