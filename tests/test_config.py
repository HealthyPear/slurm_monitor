"""Tests for configuration file discovery"""

from slurm_monitoring.config import Config


def _isolate(monkeypatch, tmp_path):
    home = tmp_path / "home"
    cwd = tmp_path / "cwd"
    home.mkdir()
    cwd.mkdir()
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.chdir(cwd)
    return home, cwd


def test_dotfile_in_home_is_loaded(monkeypatch, tmp_path):
    home, _ = _isolate(monkeypatch, tmp_path)
    (home / ".slurm_config.yaml").write_text("sacct:\n  include_all_users: true\n")

    assert Config().get("sacct.include_all_users") is True


def test_home_file_without_dot_is_loaded(monkeypatch, tmp_path):
    home, _ = _isolate(monkeypatch, tmp_path)
    (home / "slurm_config.yaml").write_text("api:\n  port: 5001\n")

    assert Config().get("api.port") == 5001


def test_current_directory_takes_precedence(monkeypatch, tmp_path):
    home, cwd = _isolate(monkeypatch, tmp_path)
    (home / ".slurm_config.yaml").write_text("api:\n  port: 5001\n")
    (cwd / "slurm_config.yaml").write_text("api:\n  port: 5002\n")

    assert Config().get("api.port") == 5002


def test_defaults_without_config_file(monkeypatch, tmp_path):
    _isolate(monkeypatch, tmp_path)

    assert Config().get("sacct.include_all_users") is False
