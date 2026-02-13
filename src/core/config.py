from __future__ import annotations

import os
from pathlib import Path

import yaml


def get_config_path() -> Path:
    env_path = os.getenv("OPTIONTRADER_CONFIG")
    if env_path:
        return Path(env_path)
    return Path("config/config-v1.yaml")


def load_config(path: Path | None = None) -> dict:
    config_path = path or get_config_path()
    return yaml.safe_load(config_path.read_text())
