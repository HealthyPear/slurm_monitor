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
    assert html.count('class="tab') == 4
    assert "logy" in html
    assert "Core Allocation by User" in html
    assert "Job Duration Distribution" in html
    assert html.count("plotly.js v") == 1


def test_duration_plot_is_a_histogram_with_mean_and_median(fake_jobs):
    from slurm_monitoring.visualizers import PlotGenerator

    durations = pd.Series([1.0, 2.0, 5.0, 10.0, 60.0, 600.0])
    fig = PlotGenerator().plot_job_duration_distribution(durations)
    assert fig.layout.xaxis.type == "log"
    assert int(sum(fig.data[0].y)) == len(durations)
    labels = [a.text for a in fig.layout.annotations]
    assert any(t.startswith("Median") for t in labels)
    assert any(t.startswith("Average") for t in labels)
