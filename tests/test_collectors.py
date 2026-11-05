"""Tests for SLURM collectors with mocked SLURM commands"""

import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
import json

from slurm_monitoring.collector.squeue import SqueueCollector
from slurm_monitoring.collector.history import HistoryCollector


class TestSqueueCollector:
    """Test squeue collector with mocked subprocess calls"""

    @patch("subprocess.run")
    def test_get_queue_summary(self, mock_run):
        """Test getting queue summary from mocked squeue output"""
        # Mock squeue output
        mock_output = """JobID|State
100|RUNNING
101|RUNNING
102|PENDING
103|PENDING
104|PENDING"""

        mock_run.return_value = MagicMock(stdout=mock_output, returncode=0)

        collector = SqueueCollector()
        # This would normally call squeue
        # By mocking subprocess.run, we avoid SLURM dependency

    @patch("subprocess.run")
    def test_squeue_timeout(self, mock_run):
        """Test handling of squeue timeout"""
        mock_run.side_effect = TimeoutError("SLURM timeout")

        collector = SqueueCollector()
        # Should handle timeout gracefully

    def test_queue_summary_parsing(self, sample_queue_state):
        """Test parsing queue summary"""
        # This can be tested without SLURM since it's data processing
        running = sample_queue_state["running"]
        pending = sample_queue_state["pending"]

        assert running > 0
        assert pending > running
        assert sample_queue_state["total"] == running + pending


class TestHistoryCollector:
    """Test historical snapshot collection"""

    def test_record_snapshot(self, temp_data_dir, sample_queue_state):
        """Test recording a snapshot"""

        collector = HistoryCollector(data_dir=str(temp_data_dir))
        collector.record_snapshot(sample_queue_state)

        # Verify snapshot was recorded
        data_file = temp_data_dir / "queue_snapshots.jsonl"
        assert data_file.exists()

        # Read the snapshot back
        with open(data_file) as f:
            line = f.readline()
            snapshot = json.loads(line)

        assert snapshot["running"] == sample_queue_state["running"]
        assert snapshot["pending"] == sample_queue_state["pending"]

    def test_get_trends(self, temp_data_dir, sample_snapshots):
        """Test trend analysis from snapshots"""
        collector = HistoryCollector(data_dir=str(temp_data_dir))

        # Write sample snapshots to the data file
        data_file = temp_data_dir / "queue_snapshots.jsonl"
        with open(data_file, "w") as f:
            for snapshot in sample_snapshots:
                f.write(json.dumps(snapshot) + "\n")

        # Get trends
        trends = collector.get_trends(hours=24)

        # Verify trends contain expected keys
        assert "avg_running" in trends
        assert "max_running" in trends
        assert "min_running" in trends
        assert "avg_pending" in trends
        assert "avg_total" in trends

    def test_trends_empty_data(self, temp_data_dir):
        """Test trends with no data"""
        collector = HistoryCollector(data_dir=str(temp_data_dir))

        # This should handle the case where no snapshots exist yet
        trends = collector.get_trends(hours=24)

        # Should return empty or default values
        assert isinstance(trends, dict)

    def test_multiple_snapshots(self, temp_data_dir):
        """Test recording and retrieving multiple snapshots"""
        collector = HistoryCollector(data_dir=str(temp_data_dir))

        # Record multiple snapshots
        for i in range(5):
            collector.record_snapshot({
                "running": 40 + i,
                "pending": 3000 + (i * 100),
                "total": 3040 + (i * 100),
            })

        # Verify all were recorded
        data_file = temp_data_dir / "queue_snapshots.jsonl"
        with open(data_file) as f:
            lines = f.readlines()

        assert len(lines) == 5

        # Parse and verify each snapshot
        for i, line in enumerate(lines):
            snapshot = json.loads(line)
            assert snapshot["running"] == 40 + i
            assert snapshot["pending"] == 3000 + (i * 100)


class TestSacctCollector:
    """Test sacct collector with mocked subprocess calls"""

    OUTPUT = (
        "JobID|CPUTime|AllocCPUS|Start|End\n"
        "1|01:30:00|4|2025-01-01T00:00:00|2025-01-01T00:30:00\n"
    )

    def _run(self, **kwargs):
        from slurm_monitoring.collector.sacct import SacctCollector

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(stdout=self.OUTPUT, returncode=0)
            jobs = SacctCollector().get_jobs(**kwargs)
        return mock_run.call_args[0][0], jobs

    def test_job_level_by_default(self):
        cmd, _ = self._run()
        assert "--allocations" in cmd

    def test_include_steps(self):
        cmd, _ = self._run(include_steps=True)
        assert "--allocations" not in cmd

    def test_include_steps_from_config(self):
        from slurm_monitoring.collector.sacct import SacctCollector

        config = MagicMock()
        config.get.side_effect = lambda key, default=None: (
            True if key == "sacct.include_steps" else default
        )
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(stdout=self.OUTPUT, returncode=0)
            SacctCollector(config=config).get_jobs()
        assert "--allocations" not in mock_run.call_args[0][0]

    def test_cputime_parsed_to_minutes(self):
        _, jobs = self._run()
        assert jobs["CPUTime"].iloc[0] == 90

    def test_parse_duration_with_days(self):
        from slurm_monitoring.collector.sacct import SacctCollector

        result = SacctCollector._parse_duration_minutes(pd.Series(["2-00:00:10", "", "5"]))
        assert result.iloc[0] == pytest.approx(2880 + 10 / 60)
        assert pd.isna(result.iloc[1])
        assert result.iloc[2] == 5
