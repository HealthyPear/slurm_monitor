import pandas as pd
import pytest
from click.testing import CliRunner

from slurm_monitoring import cli as cli_module


@pytest.fixture
def fake_jobs(monkeypatch):
    start = pd.date_range("2026-01-01", periods=6, freq="h")
    jobs = pd.DataFrame(
        {
            "JobID": [str(i) for i in range(6)],
            "User": ["alice", "bob"] * 3,
            "Submit": start,
            "Start": start,
            "End": start + pd.Timedelta(minutes=30),
            "AllocCPUS": [1, 2, 4, 8, 1, 2],
            "CPUTime": [30.0, 60.0, 120.0, 240.0, 30.0, 60.0],
            "ElapsedRaw": [1800] * 6,
            "State": ["COMPLETED"] * 6,
        }
    )

    class FakeCollector:
        def get_job_history(self, days=30, include_steps=None):
            return jobs

    monkeypatch.setattr(cli_module, "SlurmCollector", FakeCollector)


def test_visualize_defaults_to_all_metrics(fake_jobs, tmp_path):
    result = CliRunner().invoke(cli_module.cli, ["visualize", "--output", str(tmp_path)])
    assert result.exit_code == 0, result.output
    written = {p.name for p in tmp_path.glob("*.html")}
    assert {"core_utilization.html", "user_distribution.html", "job_duration.html"} <= written


def test_visualize_single_metric(fake_jobs, tmp_path):
    out = tmp_path / "users.html"
    result = CliRunner().invoke(
        cli_module.cli, ["visualize", "--metric", "user-distribution", "--output", str(out)]
    )
    assert result.exit_code == 0, result.output
    assert out.exists()


def test_dashboard_contains_all_charts(fake_jobs, tmp_path):
    out = tmp_path / "dash.html"
    result = CliRunner().invoke(cli_module.cli, ["dashboard", "--output", str(out)])
    assert result.exit_code == 0, result.output
    html = out.read_text()
    assert "SLURM Cluster Statistics Dashboard" in html
    assert "Core Allocation by User" in html
    assert "Job Duration Statistics" in html
    assert html.count("plotly.js v") == 1
