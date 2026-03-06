"""Tests for sreport and seff collectors"""

import pytest
from unittest.mock import patch, MagicMock
import pandas as pd

from slurm_monitoring.collector.sreport import SreportCollector
from slurm_monitoring.collector.seff import SeffCollector
from slurm_monitoring.analyzer.efficiency import EfficiencyAnalyzer


class TestSreportCollector:
    """Test sreport collector"""

    @patch("subprocess.run")
    def test_get_account_utilization_by_user(self, mock_run):
        """Test retrieving user account utilization"""
        mock_output = "cluster1|acct1|user1|100|0.45\ncluster1|acct1|user2|200|0.55"
        mock_run.return_value = MagicMock(
            stdout=mock_output,
            returncode=0,
            stderr=""
        )
        
        collector = SreportCollector()
        df = collector.get_account_utilization_by_user()
        
        assert df is not None
        assert not df.empty
        assert "User" in df.columns
        assert "Account" in df.columns

    @patch("subprocess.run")
    def test_get_cluster_utilization(self, mock_run):
        """Test retrieving cluster utilization summary"""
        mock_output = "cluster1|512|10|256|32|8|2|4"
        mock_run.return_value = MagicMock(
            stdout=mock_output,
            returncode=0,
            stderr=""
        )
        
        collector = SreportCollector()
        metrics = collector.get_cluster_utilization()
        
        assert isinstance(metrics, dict)
        assert "cluster" in metrics

    @patch("subprocess.run")
    def test_sreport_timeout_handling(self, mock_run):
        """Test handling of sreport timeout"""
        mock_run.side_effect = TimeoutError("Command timed out")
        
        collector = SreportCollector()
        # Should handle gracefully
        collector.get_account_utilization_by_user()


class TestSeffCollector:
    """Test seff collector"""

    @patch("subprocess.run")
    def test_get_job_efficiency(self, mock_run):
        """Test retrieving job efficiency metrics"""
        mock_output = """Job ID: 12345
Cluster: cluster1
State: COMPLETED
Nodes: 1
Cores per node: 4
CPU Efficiency: 45.2%
Memory Allocated: 32GB
Memory Used: 12.5GB
Memory Efficiency: 39.1%
Elapsed (wall clock) time: 01:23:45
"""
        mock_run.return_value = MagicMock(
            stdout=mock_output,
            returncode=0,
            stderr=""
        )
        
        collector = SeffCollector()
        metrics = collector.get_job_efficiency("12345")
        
        assert metrics is not None
        assert metrics["job_id"] == "12345"
        assert metrics["cpu_efficiency"] == 45.2
        assert metrics["memory_efficiency"] == 39.1

    @patch("subprocess.run")
    def test_get_job_efficiency_batch(self, mock_run):
        """Test retrieving efficiency for multiple jobs"""
        mock_output = """Job ID: 12345
State: COMPLETED
CPU Efficiency: 45.2%
Memory Efficiency: 39.1%
"""
        mock_run.return_value = MagicMock(
            stdout=mock_output,
            returncode=0,
            stderr=""
        )
        
        collector = SeffCollector()
        df = collector.get_job_efficiency_batch(["12345", "12346"])
        
        assert isinstance(df, pd.DataFrame)

    def test_parse_time_string(self):
        """Test time string parsing"""
        collector = SeffCollector()
        
        # Test HH:MM:SS format
        seconds = collector._parse_time_string("01:23:45")
        assert seconds == 3600 + 23*60 + 45
        
        # Test with days
        seconds = collector._parse_time_string("1 day 02:30:00")
        assert seconds == 86400 + 2*3600 + 30*60

    def test_convert_memory(self):
        """Test memory conversion"""
        assert SeffCollector._convert_memory(1024, "M") == 1.024  # 1024 MB = 1.024 GB
        assert SeffCollector._convert_memory(1, "G") == 1.0
        assert SeffCollector._convert_memory(512, "M") == 0.512


class TestEfficiencyAnalyzer:
    """Test efficiency analyzer"""

    def test_get_summary_statistics(self):
        """Test summary statistics calculation"""
        data = {
            "job_id": ["1", "2", "3"],
            "cpu_efficiency": [45.0, 65.0, 85.0],
            "memory_efficiency": [50.0, 60.0, 90.0],
            "state": ["COMPLETED", "COMPLETED", "COMPLETED"],
        }
        df = pd.DataFrame(data)
        analyzer = EfficiencyAnalyzer(df)
        
        stats = analyzer.get_summary_statistics()
        
        assert stats["total_jobs"] == 3
        assert stats["cpu_efficiency"]["average"] == 65.0
        assert stats["memory_efficiency"]["average"] == pytest.approx(66.67, rel=0.1)

    def test_categorize_efficiency(self):
        """Test job categorization by efficiency"""
        data = {
            "job_id": ["1", "2", "3", "4", "5"],
            "cpu_efficiency": [85.0, 65.0, 45.0, 25.0, 10.0],
            "memory_efficiency": [90.0, 70.0, 50.0, 30.0, 20.0],
            "state": ["COMPLETED", "COMPLETED", "COMPLETED", "COMPLETED", "FAILED"],
        }
        df = pd.DataFrame(data)
        analyzer = EfficiencyAnalyzer(df)
        
        categories = analyzer.categorize_efficiency()
        
        assert len(categories["excellent"]) > 0
        assert len(categories["good"]) > 0
        assert len(categories["fair"]) > 0
        assert len(categories["poor"]) > 0
        assert len(categories["failed"]) > 0

    def test_identify_waste_opportunities(self):
        """Test waste identification"""
        data = {
            "job_id": ["1", "2", "3"],
            "cpu_efficiency": [20.0, 60.0, 80.0],
            "memory_efficiency": [30.0, 70.0, 85.0],
            "state": ["COMPLETED", "COMPLETED", "COMPLETED"],
        }
        df = pd.DataFrame(data)
        analyzer = EfficiencyAnalyzer(df)
        
        waste = analyzer.identify_waste_opportunities(cpu_threshold=50, memory_threshold=50)
        
        assert len(waste) >= 1  # At least job 1 should be identified
        assert "1" in waste["job_id"].values

    def test_get_recommendations(self):
        """Test recommendation generation"""
        data = {
            "job_id": ["1", "2"],
            "cpu_efficiency": [35.0, 40.0],
            "memory_efficiency": [30.0, 35.0],
            "state": ["COMPLETED", "COMPLETED"],
        }
        df = pd.DataFrame(data)
        analyzer = EfficiencyAnalyzer(df)
        
        recommendations = analyzer.get_recommendations()
        
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        # Should have warning about low efficiency
        assert any("⚠️" in rec for rec in recommendations)

    def test_empty_dataframe(self):
        """Test handling of empty DataFrame"""
        df = pd.DataFrame()
        analyzer = EfficiencyAnalyzer(df)
        
        stats = analyzer.get_summary_statistics()
        assert stats == {}
        
        categories = analyzer.categorize_efficiency()
        for v in categories.values():
            assert v == []
