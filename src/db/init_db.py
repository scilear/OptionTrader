from __future__ import annotations

import sys
from pathlib import Path

repo_root = Path(__file__).resolve().parents[2]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

import os

from src.core.bootstrap import ensure_repo_root_on_path

ensure_repo_root_on_path()

from src.db.connection import connect


def _table_columns(conn, table_name: str) -> set[str]:
    rows = conn.execute(f"PRAGMA table_info('{table_name}')").fetchall()
    return {row[1] for row in rows}


def init_db(schema_path: Path | None = None) -> None:
    path = schema_path or Path("src/db/schema.sql")
    sql = path.read_text()
    conn = connect()
    try:
        if os.getenv("OPTIONTRADER_RESET_DB") == "1":
            conn.execute("DROP TABLE IF EXISTS trade_ideas")
            conn.execute("DROP TABLE IF EXISTS alerts")
            conn.execute("DROP TABLE IF EXISTS surface_metrics")
            conn.execute("DROP TABLE IF EXISTS iv_points")
            conn.execute("DROP TABLE IF EXISTS option_quotes")
            conn.execute("DROP TABLE IF EXISTS regime_state")
            conn.execute("DROP TABLE IF EXISTS snapshots")
            conn.execute("DROP TABLE IF EXISTS pipeline_runs")
        conn.execute(sql)
        if "run_id" not in _table_columns(conn, "snapshots"):
            conn.execute("ALTER TABLE snapshots ADD COLUMN run_id INTEGER")
        if "regime_config_hash" not in _table_columns(conn, "regime_state"):
            conn.execute("ALTER TABLE regime_state ADD COLUMN regime_config_hash TEXT")
        regime_columns = _table_columns(conn, "regime_state")
        if "vix_spot" not in regime_columns:
            conn.execute("ALTER TABLE regime_state ADD COLUMN vix_spot DOUBLE")
        if "rv20_value" not in regime_columns:
            conn.execute("ALTER TABLE regime_state ADD COLUMN rv20_value DOUBLE")
        if "drawdown_value" not in regime_columns:
            conn.execute("ALTER TABLE regime_state ADD COLUMN drawdown_value DOUBLE")
        if "event_score" not in regime_columns:
            conn.execute("ALTER TABLE regime_state ADD COLUMN event_score DOUBLE")
        if "stress_proxy_score" not in regime_columns:
            conn.execute("ALTER TABLE regime_state ADD COLUMN stress_proxy_score DOUBLE")
        if "decomposition" not in regime_columns:
            conn.execute("ALTER TABLE regime_state ADD COLUMN decomposition TEXT")
        iv_columns = _table_columns(conn, "iv_points")
        if "fit_model_id" not in iv_columns:
            conn.execute("ALTER TABLE iv_points ADD COLUMN fit_model_id TEXT")
        if "fit_residual" not in iv_columns:
            conn.execute("ALTER TABLE iv_points ADD COLUMN fit_residual DOUBLE")
        if "fit_support" not in iv_columns:
            conn.execute("ALTER TABLE iv_points ADD COLUMN fit_support INTEGER")
        if "fit_confidence" not in iv_columns:
            conn.execute("ALTER TABLE iv_points ADD COLUMN fit_confidence DOUBLE")
        if "fit_reason_codes" not in iv_columns:
            conn.execute("ALTER TABLE iv_points ADD COLUMN fit_reason_codes TEXT")
        surface_columns = _table_columns(conn, "surface_metrics")
        if "fit_model_id" not in surface_columns:
            conn.execute("ALTER TABLE surface_metrics ADD COLUMN fit_model_id TEXT")
        if "fit_residual" not in surface_columns:
            conn.execute("ALTER TABLE surface_metrics ADD COLUMN fit_residual DOUBLE")
        if "fit_support" not in surface_columns:
            conn.execute("ALTER TABLE surface_metrics ADD COLUMN fit_support INTEGER")
        if "fit_confidence" not in surface_columns:
            conn.execute("ALTER TABLE surface_metrics ADD COLUMN fit_confidence DOUBLE")
        if "surface_quality_score" not in surface_columns:
            conn.execute("ALTER TABLE surface_metrics ADD COLUMN surface_quality_score DOUBLE")
        if "qc_pass" not in surface_columns:
            conn.execute("ALTER TABLE surface_metrics ADD COLUMN qc_pass BOOLEAN")
        if "qc_reason_codes" not in surface_columns:
            conn.execute("ALTER TABLE surface_metrics ADD COLUMN qc_reason_codes TEXT")
        if "alert_outcomes" not in {
            row[0] for row in conn.execute("SHOW TABLES").fetchall()
        }:
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
        if "horizon_days" not in alert_outcome_columns:
            conn.execute("ALTER TABLE alert_outcomes ADD COLUMN horizon_days INTEGER")
        if "outcome_label" not in alert_outcome_columns:
            conn.execute("ALTER TABLE alert_outcomes ADD COLUMN outcome_label TEXT")
        if "resolved_snapshot_id" not in alert_outcome_columns:
            conn.execute("ALTER TABLE alert_outcomes ADD COLUMN resolved_snapshot_id INTEGER")
        if "resolved_ts" not in alert_outcome_columns:
            conn.execute("ALTER TABLE alert_outcomes ADD COLUMN resolved_ts TIMESTAMP")
        if "base_metric_value" not in alert_outcome_columns:
            conn.execute("ALTER TABLE alert_outcomes ADD COLUMN base_metric_value DOUBLE")
        if "resolved_metric_value" not in alert_outcome_columns:
            conn.execute("ALTER TABLE alert_outcomes ADD COLUMN resolved_metric_value DOUBLE")
        if "reversion_ratio" not in alert_outcome_columns:
            conn.execute("ALTER TABLE alert_outcomes ADD COLUMN reversion_ratio DOUBLE")
        if "outcome_source" not in alert_outcome_columns:
            conn.execute("ALTER TABLE alert_outcomes ADD COLUMN outcome_source TEXT")
        if "evaluated_at" not in alert_outcome_columns:
            conn.execute("ALTER TABLE alert_outcomes ADD COLUMN evaluated_at TIMESTAMP")
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
