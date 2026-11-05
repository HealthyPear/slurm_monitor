import http.server

import pytest
from click.testing import CliRunner

from slurm_monitoring import cli as cli_module
from slurm_monitoring import config as config_module


class FakeServer:
    instances: list = []

    def __init__(self, address, handler):
        self.address = address
        FakeServer.instances.append(self)

    def serve_forever(self):
        raise KeyboardInterrupt

    def server_close(self):
        pass


@pytest.fixture
def serve_env(monkeypatch, tmp_path):
    FakeServer.instances = []
    monkeypatch.setattr(http.server, "ThreadingHTTPServer", FakeServer)
    monkeypatch.setattr(cli_module, "_write_dashboard", lambda days, output: True)
    return tmp_path


def _set_config(monkeypatch, values):
    class FakeConfig:
        def get(self, key, default=None):
            return values.get(key, default)

    monkeypatch.setattr(config_module, "get_config", lambda: FakeConfig())


def _serve(tmp_path, *args):
    return CliRunner().invoke(
        cli_module.cli, ["serve", "--output", str(tmp_path / "d.html"), *args]
    )


def test_serve_defaults(serve_env, monkeypatch):
    _set_config(monkeypatch, {})
    result = _serve(serve_env)
    assert result.exit_code == 0, result.output
    assert FakeServer.instances[0].address == ("127.0.0.1", 8000)


def test_serve_port_from_config(serve_env, monkeypatch):
    _set_config(monkeypatch, {"dashboard.port": 9100, "dashboard.host": "0.0.0.0"})
    _serve(serve_env)
    assert FakeServer.instances[0].address == ("0.0.0.0", 9100)


def test_serve_cli_port_overrides_config(serve_env, monkeypatch):
    _set_config(monkeypatch, {"dashboard.port": 9100})
    _serve(serve_env, "--port", "8765")
    assert FakeServer.instances[0].address[1] == 8765


def test_serve_port_in_use_gives_hint(serve_env, monkeypatch):
    _set_config(monkeypatch, {})

    def busy(address, handler):
        raise OSError(98, "Address already in use")

    monkeypatch.setattr(http.server, "ThreadingHTTPServer", busy)
    result = _serve(serve_env)
    assert result.exit_code != 0
    assert "--port" in result.output
