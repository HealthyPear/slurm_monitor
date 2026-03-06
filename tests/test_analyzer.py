"""Tests for SLURM monitoring package"""

import pytest
import pandas as pd
from datetime import datetime, timedelta

from slurm_monitoring.collector import SlurmCollector
from slurm_monitoring.analyzer import ClusterAnalyzer
from slurm_monitoring.exporters import CSVExporter, JSONExporter


@pytest.fixture
def sample_jobs_data():
    """Create sample job data for testing"""
    return pd.DataFrame(
        {
            "JobID": ["1", "2", "3"],
            "User": ["user1", "user1", "user2"],
            "Account": ["acct1", "acct1", "acct2"],
            "AllocCPUS": [4, 8, 16],
            "CPUTime": [120, 240, 360],
            "State": ["COMPLETED", "COMPLETED", "COMPLETED"],
            "Start": [
                datetime.now() - timedelta(days=1),
                datetime.now() - timedelta(days=2),
                datetime.now() - timedelta(days=3),
            ],
            "End": [
                datetime.now() - timedelta(days=1) + timedelta(hours=1),
                datetime.now() - timedelta(days=2) + timedelta(hours=2),
                datetime.now() - timedelta(days=3) + timedelta(hours=3),
            ],
        }
    )


def test_cluster_analyzer_initialization(sample_jobs_data):
    """Test ClusterAnalyzer initialization"""
    analyzer = ClusterAnalyzer(sample_jobs_data)
    assert analyzer.jobs_data is not None


def test_compute_core_utilization(sample_jobs_data):
    """Test core utilization computation"""
    analyzer = ClusterAnalyzer(sample_jobs_data)
    stats = analyzer.compute_core_utilization()

    assert "total_core_hours" in stats
    assert "average_cores_per_job" in stats
    assert stats["total_core_hours"] > 0


def test_user_breakdown(sample_jobs_data):
    """Test user breakdown"""
    analyzer = ClusterAnalyzer(sample_jobs_data)
    breakdown = analyzer.breakdown_by_user()

    assert "user1" in breakdown
    assert "user2" in breakdown
    assert breakdown["user1"]["job_count"] == 2
    assert breakdown["user2"]["job_count"] == 1


def test_peak_times(sample_jobs_data):
    """Test peak times identification"""
    analyzer = ClusterAnalyzer(sample_jobs_data)
    peaks = analyzer.identify_peak_times()

    assert "peak_hour" in peaks
    assert "jobs_at_peak" in peaks


def test_job_duration_stats(sample_jobs_data):
    """Test job duration statistics"""
    analyzer = ClusterAnalyzer(sample_jobs_data)
    stats = analyzer.compute_job_duration_stats()

    assert "average_duration_minutes" in stats
    assert "max_duration_minutes" in stats
