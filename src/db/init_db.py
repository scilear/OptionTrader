from __future__ import annotations

import sys
from pathlib import Path

repo_root = Path(__file__).resolve().parents[2]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

import os

from src.core.bootstrap import ensure_repo_root_on_path

ensure_repo_root_on_path()

from src.db.connection import _is_pg, connect


PG_TYPE_MAP = {
    "INTEGER": "INTEGER",
    "DOUBLE": "DOUBLE PRECISION",
    "TEXT": "TEXT",
    "BOOLEAN": "BOOLEAN",
    "TIMESTAMP": "TIMESTAMP",
    "DATE": "DATE",
    "BLOB": "BYTEA",
}


def _table_columns(conn, table_name: str) -> set[str]:
    if _is_pg(conn):
        rows = conn.execute(
            "SELECT column_name FROM information_schema.columns WHERE table_name = %s",
            (table_name,),
        ).fetchall()
        return {row[0] for row in rows}
    rows = conn.execute(f"PRAGMA table_info('{table_name}')").fetchall()
    return {row[1] for row in rows}


def _list_tables(conn) -> set[str]:
    if _is_pg(conn):
        rows = conn.execute(
            "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
        ).fetchall()
        return {row[0] for row in rows}
    return {row[0] for row in conn.execute("SHOW TABLES").fetchall()}


def _pg_col_type(raw: str) -> str:
    return PG_TYPE_MAP.get(raw.upper(), raw)


def _add_column(conn, table: str, col: str, col_type: str) -> None:
    typ = _pg_col_type(col_type) if _is_pg(conn) else col_type
    conn.execute(f"ALTER TABLE {table} ADD COLUMN {col} {typ}")


def init_db(schema_path: Path | None = None) -> None:
    path = schema_path or Path("src/db/schema.sql")
    sql = path.read_text()
    conn = connect()
    try:
        if os.getenv("OPTIONTRADER_RESET_DB") == "1":
            tables = [
                "trade_ideas",
                "alerts",
                "surface_metrics",
                "iv_points",
                "option_quotes",
                "regime_state",
                "snapshots",
                "pipeline_runs",
            ]
            for t in tables:
                conn.execute(f"DROP TABLE IF EXISTS {t}")
        conn.execute(sql)
        if "run_id" not in _table_columns(conn, "snapshots"):
            _add_column(conn, "snapshots", "run_id", "INTEGER")
        if "regime_config_hash" not in _table_columns(conn, "regime_state"):
            _add_column(conn, "regime_state", "regime_config_hash", "TEXT")
        regime_columns = _table_columns(conn, "regime_state")
        for col in ("vix_spot", "rv20_value", "drawdown_value", "event_score", "stress_proxy_score"):
            if col not in regime_columns:
                _add_column(conn, "regime_state", col, "DOUBLE")
        if "decomposition" not in regime_columns:
            _add_column(conn, "regime_state", "decomposition", "TEXT")
        existing_tables = _list_tables(conn)
        if "regime_snapshot_labels" not in existing_tables:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS regime_snapshot_labels (
                    snapshot_id INTEGER PRIMARY KEY,
                    run_id INTEGER,
                    regime_date DATE NOT NULL,
                    regime_label TEXT NOT NULL,
                    regime_config_hash TEXT,
                    decomposition TEXT,
                    FOREIGN KEY(snapshot_id) REFERENCES snapshots(snapshot_id)
                )
                """
            )
        regime_snapshot_columns = _table_columns(conn, "regime_snapshot_labels")
        regime_snapshot_col_types = {
            "run_id": "INTEGER",
            "regime_date": "DATE",
            "regime_label": "TEXT",
            "regime_config_hash": "TEXT",
            "decomposition": "TEXT",
        }
        for col, typ in regime_snapshot_col_types.items():
            if col not in regime_snapshot_columns:
                _add_column(conn, "regime_snapshot_labels", col, typ)
        iv_columns = _table_columns(conn, "iv_points")
        if "fit_model_id" not in iv_columns:
            _add_column(conn, "iv_points", "fit_model_id", "TEXT")
        if "fit_residual" not in iv_columns:
            _add_column(conn, "iv_points", "fit_residual", "DOUBLE")
        if "fit_support" not in iv_columns:
            _add_column(conn, "iv_points", "fit_support", "INTEGER")
        if "fit_confidence" not in iv_columns:
            _add_column(conn, "iv_points", "fit_confidence", "DOUBLE")
        if "fit_reason_codes" not in iv_columns:
            _add_column(conn, "iv_points", "fit_reason_codes", "TEXT")
        surface_columns = _table_columns(conn, "surface_metrics")
        if "fit_model_id" not in surface_columns:
            _add_column(conn, "surface_metrics", "fit_model_id", "TEXT")
        if "fit_residual" not in surface_columns:
            _add_column(conn, "surface_metrics", "fit_residual", "DOUBLE")
        if "fit_support" not in surface_columns:
            _add_column(conn, "surface_metrics", "fit_support", "INTEGER")
        if "fit_confidence" not in surface_columns:
            _add_column(conn, "surface_metrics", "fit_confidence", "DOUBLE")
        if "surface_quality_score" not in surface_columns:
            _add_column(conn, "surface_metrics", "surface_quality_score", "DOUBLE")
        if "qc_pass" not in surface_columns:
            _add_column(conn, "surface_metrics", "qc_pass", "BOOLEAN")
        if "qc_reason_codes" not in surface_columns:
            _add_column(conn, "surface_metrics", "qc_reason_codes", "TEXT")
        if "alert_outcomes" not in existing_tables:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS alert_outcomes (
                    alert_id INTEGER PRIMARY KEY,
                    horizon_days INTEGER NOT NULL,
                    outcome_label TEXT NOT NULL,
                    resolved_snapshot_id INTEGER,
                    resolved_ts TIMESTAMP,
                    base_metric_value DOUBLE,
                    resolved_metric_value DOUBLE,
                    reversion_ratio DOUBLE,
                    outcome_source TEXT,
                    evaluated_at TIMESTAMP NOT NULL,
                    FOREIGN KEY(alert_id) REFERENCES alerts(alert_id)
                )
                """
            )
        alert_outcome_columns = _table_columns(conn, "alert_outcomes")
        for col in (
            "horizon_days",
            "outcome_label",
            "resolved_snapshot_id",
            "resolved_ts",
            "base_metric_value",
            "resolved_metric_value",
            "reversion_ratio",
            "outcome_source",
            "evaluated_at",
        ):
            if col not in alert_outcome_columns:
                typ = {
                    "horizon_days": "INTEGER",
                    "outcome_label": "TEXT",
                    "resolved_snapshot_id": "INTEGER",
                    "resolved_ts": "TIMESTAMP",
                    "outcome_source": "TEXT",
                    "evaluated_at": "TIMESTAMP",
                }.get(col, "DOUBLE")
                _add_column(conn, "alert_outcomes", col, typ)
        alert_columns = _table_columns(conn, "alerts")
        if "signal_state" not in alert_columns:
            _add_column(conn, "alerts", "signal_state", "TEXT")
        if "transition_reason_code" not in alert_columns:
            _add_column(conn, "alerts", "transition_reason_code", "TEXT")
        conn.execute(
            "UPDATE alerts SET signal_state = 'ExecutionReady' WHERE signal_state IS NULL"
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_iv_points_snapshot_id ON iv_points(snapshot_id)")
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_surface_metrics_snapshot_id ON surface_metrics(snapshot_id)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_alert_outcomes_label ON alert_outcomes(outcome_label)"
        )
    finally:
        conn.close()


if __name__ == "__main__":
    init_db()
