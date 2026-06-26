from __future__ import annotations

from src.core.config import load_config


def connect():
    config = load_config()
    engine = config["storage"].get("engine", "duckdb")
    if engine == "postgres":
        import psycopg2
        return psycopg2.connect(config["storage"]["dsn"])
    import duckdb
    return duckdb.connect(config["storage"]["path"])
