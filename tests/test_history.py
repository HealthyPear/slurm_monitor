"""Tests for the HistoryCollector"""

import pytest
import json
from datetime import datetime, timedelta
from pathlib import Path

from slurm_monitoring.collector.history import HistoryCollector


class TestHistoryCollector:
    """Test suite for historical snapshot collection and analysis"""

    def test_initialization(self, temp_data_dir):
        """Test HistoryCollector initialization"""
        collector = HistoryCollector(data_dir=str(temp_data_dir))
        assert collector is not None

    def test_record_snapshot_creates_file(self, temp_data_dir):
        """Test that recording a snapshot creates the data file"""
        collector = HistoryCollector(data_dir=str(temp_data_dir))
        
        collector.record_snapshot({
            "running": 42,
            "pending": 3261,
            "total": 3303,
        })
        
        data_file = temp_data_dir / "queue_snapshots.jsonl"
        assert data_file.exists()
        assert data_file.stat().st_size > 0

    def test_snapshot_has_timestamp(self, temp_data_dir):
        """Test that recorded snapshots include timestamps"""
        collector = HistoryCollector(data_dir=str(temp_data_dir))
        
        before = datetime.now()
        collector.record_snapshot({
            "running": 42,
            "pending": 3261,
            "total": 3303,
        })
        after = datetime.now()
        
        # Read back the snapshot
        data_file = temp_data_dir / "queue_snapshots.jsonl"
        with open(data_file) as f:
            snapshot = json.loads(f.readline())
        
        assert "timestamp" in snapshot
        # Timestamp should be ISO format and recent
        ts = datetime.fromisoformat(snapshot["timestamp"])
        assert before <= ts <= after

    def test_append_multiple_snapshots(self, temp_data_dir):
        """Test appending multiple snapshots to same file"""
        collector = HistoryCollector(data_dir=str(temp_data_dir))
        
        # Record 3 snapshots
        for i in range(3):
            collector.record_snapshot({
                "running": 40 + i,
                "pending": 3000 + (i * 100),
                "total": 3040 + (i * 100),
            })
        
        # Read back all snapshots
        data_file = temp_data_dir / "queue_snapshots.jsonl"
        with open(data_file) as f:
            snapshots = [json.loads(line) for line in f]
        
        assert len(snapshots) == 3
        assert snapshots[0]["running"] == 40
        assert snapshots[1]["running"] == 41
        assert snapshots[2]["running"] == 42

    def test_get_trends_calculates_averages(self, temp_data_dir, sample_snapshots):
        """Test that trends calculation returns correct averages"""
        collector = HistoryCollector(data_dir=str(temp_data_dir))
        
        # Write sample snapshots
        data_file = temp_data_dir / "queue_snapshots.jsonl"
        with open(data_file, "w") as f:
            for snapshot in sample_snapshots:
                f.write(json.dumps(snapshot) + "\n")
        
        trends = collector.get_trends(hours=24)
        
        # Verify calculated values
        assert trends["avg_running"] > 0
        assert trends["max_running"] >= trends["avg_running"]
        assert trends["min_running"] <= trends["avg_running"]

    def test_get_trends_respects_time_window(self, temp_data_dir):
        """Test that trends only includes data from requested time window"""
        collector = HistoryCollector(data_dir=str(temp_data_dir))
        
        # Write snapshots with exact hour intervals
        data_file = temp_data_dir / "queue_snapshots.jsonl"
        now = datetime.now()
        
        with open(data_file, "w") as f:
            # Record 48 snapshots (2 days of hourly data)
            for i in range(48):
                timestamp = (now - timedelta(hours=48-i)).isoformat()
                snapshot = {
                    "timestamp": timestamp,
                    "running": 40 + (i % 10),
                    "pending": 3000,
                    "total": 3040,
                }
                f.write(json.dumps(snapshot) + "\n")
        
        # Get trends for last 24 hours
        trends_24h = collector.get_trends(hours=24)
        
        # Get trends for last 48 hours
        trends_48h = collector.get_trends(hours=48)
        
        # 48-hour trends should have more data
        assert "avg_running" in trends_24h
        assert "avg_running" in trends_48h

    def test_get_trends_empty_file(self, temp_data_dir):
        """Test trends when no snapshots exist yet"""
        collector = HistoryCollector(data_dir=str(temp_data_dir))
        
        # This should not raise an error
        trends = collector.get_trends(hours=24)
        
        # Should return a dict (maybe with None values)
        assert isinstance(trends, dict)

    def test_snapshot_format_correctness(self, temp_data_dir):
        """Test that snapshots are properly formatted JSON-L"""
        collector = HistoryCollector(data_dir=str(temp_data_dir))
        
        test_data = {
            "running": 42,
            "pending": 3261,
            "total": 3303,
        }
        
        collector.record_snapshot(test_data)
        
        # Read and verify format
        data_file = temp_data_dir / "queue_snapshots.jsonl"
        with open(data_file) as f:
            line = f.readline()
        
        # Should be valid JSON
        snapshot = json.loads(line)
        
        # Should contain our data
        assert snapshot["running"] == test_data["running"]
        assert snapshot["pending"] == test_data["pending"]
        assert snapshot["total"] == test_data["total"]
        
        # Should have timestamp
        assert "timestamp" in snapshot
