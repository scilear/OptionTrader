from __future__ import annotations

import logging
from pathlib import Path

from src.core.config import load_config


def setup_logging() -> None:
    config = load_config()
    log_cfg = config.get("logging", {})
    level = log_cfg.get("level", "INFO")
    log_file = log_cfg.get("file")

    handlers = [logging.StreamHandler()]
    if log_file:
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(log_file))

    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=handlers,
    )
