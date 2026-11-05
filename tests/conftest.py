"""Shared pytest fixtures and mocking utilities for SLURM Monitoring tests"""

import pytest
import pandas as pd
from datetime import datetime, timedelta
from unittest.mock import Mock, patch


@pytest.fixture
def sample_jobs_data():
    """Create sample job data for testing"""
    return pd.DataFrame(
        {
            "JobID": ["1", "2", "3", "4", "5"],
            "User": ["user1", "user1", "user2", "user2", "user3"],
            "Account": ["acct1", "acct1", "acct2", "acct2", "acct1"],
            "AllocCPUS": [4, 8, 16, 32, 2],
            "CPUTime": [120, 240, 360, 480, 60],
            "State": ["COMPLETED", "COMPLETED", "COMPLETED", "COMPLETED", "FAILED"],
            "Start": [datetime.now() - timedelta(days=i) for i in range(1, 6)],
            "End": [datetime.now() - timedelta(days=i) + timedelta(hours=i) for i in range(1, 6)],
        }
    )


@pytest.fixture
def sample_queue_state():
    """Sample queue state for snapshot testing"""
    return {
        "running": 45,
        "pending": 3261,
        "total": 3306,
    }


@pytest.fixture
def sample_snapshots():
    """Sample historical snapshots"""
    snapshots = []
    base_time = datetime.now() - timedelta(hours=24)

    for i in range(24):
        timestamp = base_time + timedelta(hours=i)
        snapshots.append(
            {
                "timestamp": timestamp.isoformat(),
                "running": 40 + (i % 10),  # Varies 40-50
                "pending": 3000 + (i * 50),  # Increases over time
                "total": 3040 + (i * 50),
            }
        )

    return snapshots


@pytest.fixture
def temp_data_dir(tmp_path):
    """Create a temporary data directory for testing"""
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    return data_dir


@pytest.fixture
def mock_slurm_collector():
    """Mock SlurmCollector that returns sample data instead of calling SLURM"""
    mock = Mock()
    mock.get_job_history = Mock(return_value=None)  # Will be set by test
    mock.get_cluster_state = Mock(return_value={})
    mock.get_running_jobs = Mock(return_value=pd.DataFrame())
    mock.get_pending_jobs = Mock(return_value=pd.DataFrame())
    return mock


@pytest.fixture
def mock_subprocess():
    """Mock subprocess.run for SLURM commands"""
    with patch("subprocess.run") as mock_run:
        yield mock_run
