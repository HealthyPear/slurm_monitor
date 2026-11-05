import pandas as pd
import pytest
from click.testing import CliRunner

from slurm_monitoring import cli as cli_module


def _row(job_id, cpu, mem):
    return {
        "job_id": job_id,
        "state": "COMPLETED",
        "nodes": 1,
        "cpus": 4,
        "cpu_efficiency": cpu,
        "memory_allocated": "8.00 GB",
        "memory_used": "300.00 MB",
        "memory_efficiency": mem,
        "wall_time_allocated": "01:00:00",
        "wall_time_used": "00:10:00",
        "wall_time_efficiency": 16.7,
    }


@pytest.fixture
def fake_seff(monkeypatch):
    def install(rows):
        class FakeSeff:
            def get_job_efficiency_batch(self, job_ids):
                return pd.DataFrame(rows)

        monkeypatch.setattr(cli_module, "SeffCollector", FakeSeff)

    return install


def test_single_job_shows_details_not_min_max(fake_seff):
    fake_seff([_row("1", 62.8, 3.8)])
    result = CliRunner().invoke(cli_module.cli, ["efficiency", "--job-id", "1"])
    assert result.exit_code == 0, result.output
    assert "JOB 1 EFFICIENCY" in result.output
    assert "CPU efficiency: 62.8%" in result.output
    assert "Memory efficiency: 3.8%" in result.output
    assert "8.00 GB" in result.output
    assert "Min:" not in result.output
    assert "Max:" not in result.output


def test_several_jobs_show_summary(fake_seff):
    fake_seff([_row("1", 60.0, 10.0), _row("2", 80.0, 30.0)])
    result = CliRunner().invoke(cli_module.cli, ["efficiency", "--job-id", "1"])
    assert "EFFICIENCY SUMMARY" in result.output
    assert "Min: 60.0%" in result.output
    assert "Max: 80.0%" in result.output
