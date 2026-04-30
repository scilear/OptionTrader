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

        iv_cols = conn.execute("DESCRIBE iv_points").fetchall()
        iv_col_names = {c[0] for c in iv_cols}
        assert "fit_model_id" in iv_col_names
        assert "fit_residual" in iv_col_names
        assert "fit_support" in iv_col_names
        assert "fit_confidence" in iv_col_names
        assert "fit_reason_codes" in iv_col_names

        surface_cols = conn.execute("DESCRIBE surface_metrics").fetchall()
        surface_col_names = {c[0] for c in surface_cols}
        assert "fit_model_id" in surface_col_names
        assert "fit_residual" in surface_col_names
        assert "fit_support" in surface_col_names
        assert "fit_confidence" in surface_col_names
        assert "surface_quality_score" in surface_col_names
        assert "qc_pass" in surface_col_names
        assert "qc_reason_codes" in surface_col_names

        snapshot_cols = conn.execute("DESCRIBE snapshots").fetchall()
        snapshot_col_names = {c[0] for c in snapshot_cols}
        assert "run_id" in snapshot_col_names

        indexes = {
            (row[0], row[1])
            for row in conn.execute(
                "SELECT index_name, table_name FROM duckdb_indexes()"
            ).fetchall()
        }
        assert ("idx_iv_points_snapshot_id", "iv_points") in indexes
        assert ("idx_surface_metrics_snapshot_id", "surface_metrics") in indexes
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
        conn.execute(
            """
            CREATE TABLE iv_points (
                iv_id INTEGER,
                snapshot_id INTEGER,
                expiry DATE,
                delta_bucket TEXT,
                iv_mid DOUBLE,
                iv_bid DOUBLE,
                iv_ask DOUBLE,
                solve_status TEXT,
                quality_score DOUBLE
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE surface_metrics (
                metric_id INTEGER,
                snapshot_id INTEGER,
                expiry_bucket TEXT,
                atm_iv_mid DOUBLE,
                rr25_mid DOUBLE,
                rr10_mid DOUBLE,
                fly25_mid DOUBLE,
                fly10_mid DOUBLE,
                term_slope_mid DOUBLE,
                atm_iv_worst DOUBLE,
                rr25_worst DOUBLE,
                rr10_worst DOUBLE,
                fly25_worst DOUBLE,
                fly10_worst DOUBLE,
                term_slope_worst DOUBLE
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

        iv_cols = migrated.execute("DESCRIBE iv_points").fetchall()
        iv_col_names = {col[0] for col in iv_cols}
        assert "fit_model_id" in iv_col_names
        assert "fit_residual" in iv_col_names
        assert "fit_support" in iv_col_names
        assert "fit_confidence" in iv_col_names
        assert "fit_reason_codes" in iv_col_names

        surface_cols = migrated.execute("DESCRIBE surface_metrics").fetchall()
        surface_col_names = {col[0] for col in surface_cols}
        assert "fit_model_id" in surface_col_names
        assert "fit_residual" in surface_col_names
        assert "fit_support" in surface_col_names
        assert "fit_confidence" in surface_col_names
        assert "surface_quality_score" in surface_col_names
        assert "qc_pass" in surface_col_names
        assert "qc_reason_codes" in surface_col_names

        indexes = {
            (row[0], row[1])
            for row in migrated.execute(
                "SELECT index_name, table_name FROM duckdb_indexes()"
            ).fetchall()
        }
        assert ("idx_iv_points_snapshot_id", "iv_points") in indexes
        assert ("idx_surface_metrics_snapshot_id", "surface_metrics") in indexes
    finally:
        migrated.close()
