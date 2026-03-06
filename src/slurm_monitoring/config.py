"""Configuration management for SLURM monitoring"""

from pathlib import Path
from typing import Optional
import yaml
import os


class Config:
    """Configuration handler for SLURM monitoring tool"""

    def __init__(self, config_file: Optional[str] = None):
        """Initialize configuration from file or defaults"""
        self.config = self._load_config(config_file)

    def _load_config(self, config_file: Optional[str]) -> dict:
        """Load configuration from file or use defaults"""
        defaults = {
            "slurm": {
                "command_timeout": 30,
                "host": "localhost",
            },
            "collection": {
                "default_lookback_days": 30,
                "cache_dir": str(Path.home() / ".slurm-monitoring" / "cache"),
            },
            "api": {
                "host": "0.0.0.0",
                "port": 5000,
                "debug": False,
            },
            "visualization": {
                "theme": "seaborn",
                "output_format": "html",
            },
        }

        # Try to load user config
        if config_file is None:
            config_file = self._find_config_file()

        if config_file and Path(config_file).exists():
            with open(config_file) as f:
                user_config = yaml.safe_load(f) or {}
                # Deep merge user config with defaults
                self._merge_configs(defaults, user_config)

        return defaults

    def _find_config_file(self) -> Optional[str]:
        """Find configuration file in standard locations"""
        locations = [
            "slurm_config.yaml",
            Path.home() / "slurm_config.yaml",
            Path.home() / ".config" / "slurm_monitoring" / "config.yaml",
            "/etc/slurm_monitoring/config.yaml",
        ]
        for loc in locations:
            if Path(loc).exists():
                return str(loc)
        return None

    def _merge_configs(self, defaults: dict, user_config: dict) -> None:
        """Recursively merge user config into defaults"""
        for key, value in user_config.items():
            if key in defaults and isinstance(defaults[key], dict) and isinstance(value, dict):
                self._merge_configs(defaults[key], value)
            else:
                defaults[key] = value

    def get(self, key: str, default=None):
        """Get configuration value using dot notation"""
        keys = key.split(".")
        value = self.config
        for k in keys:
            value = value.get(k, {}) if isinstance(value, dict) else default
        return value if value != {} else default


# Global configuration instance
_config = None


def get_config() -> Config:
    """Get or create global configuration instance"""
    global _config
    if _config is None:
        _config = Config()
    return _config
