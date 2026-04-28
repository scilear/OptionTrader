import duckdb
from pathlib import Path

from src.db.init_db import init_db
import yaml


def test_schema_executes():
    conn = duckdb.connect(":memory:")
    try:
        sql = Path("src/db/schema.sql").read_text()
        conn.execute(sql)
        tables = conn.execute("SHOW TABLES").fetchall()
        assert ("option_quotes",) in tables
        assert ("pipeline_runs",) in tables
        cols = conn.execute("DESCRIBE option_quotes").fetchall()
        col_names = {c[0] for c in cols}
        assert "option_right" in col_names
        assert "right" not in col_names
        snapshot_cols = conn.execute("DESCRIBE snapshots").fetchall()
        snapshot_col_names = {c[0] for c in snapshot_cols}
        assert "run_id" in snapshot_col_names
    finally:
        conn.close()


def test_init_db_migrates_existing_snapshots_table(monkeypatch, tmp_path):
    db_path = tmp_path / "migrate.duckdb"
    config = yaml.safe_load(Path("config/config-test.yaml").read_text())
    config["storage"]["path"] = str(db_path)
    config_path = tmp_path / "config.yaml"
    config_path.write_text(yaml.safe_dump(config, sort_keys=False))
    monkeypatch.setenv("OPTIONTRADER_CONFIG", str(config_path))

    conn = duckdb.connect(str(db_path))
    try:
        conn.execute(
            """
            CREATE TABLE snapshots (
                snapshot_id INTEGER PRIMARY KEY,
                ts TIMESTAMP,
                underlying TEXT,
                spot DOUBLE,
                source TEXT,
                session_tag TEXT,
                notes TEXT
            )
            """
        )
    finally:
        conn.close()

    init_db()

    migrated = duckdb.connect(str(db_path))
    try:
        cols = migrated.execute("DESCRIBE snapshots").fetchall()
        col_names = {col[0] for col in cols}
        assert "run_id" in col_names
    finally:
        migrated.close()
