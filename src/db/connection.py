from __future__ import annotations

import duckdb

from src.core.config import load_config


def connect():
    config = load_config()
    db_path = config["storage"]["path"]
    return duckdb.connect(db_path)
