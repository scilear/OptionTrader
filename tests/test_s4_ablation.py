from __future__ import annotations

from datetime import datetime, timedelta

import duckdb

import scripts.evaluate_alert_outcomes as outcome_mod
import scripts.generate_regime_ablation_artifact as ablation_mod


def _create_ablation_tables(conn: duckdb.DuckDBPyConnection) -> None:
    conn.execute(
        """
        CREATE TABLE pipeline_runs (
            run_id INTEGER,
            code_version TEXT
        );
        CREATE TABLE snapshots (
            snapshot_id INTEGER,
            run_id INTEGER,
            ts TIMESTAMP,
            underlying TEXT
        );
        CREATE TABLE alerts (
            alert_id INTEGER,
            snapshot_id INTEGER,
            alert_type TEXT,
            expiry_bucket TEXT,
            regime_label TEXT
        );
        CREATE TABLE surface_metrics (
            snapshot_id INTEGER,
            expiry_bucket TEXT,
            rr25_mid DOUBLE,
            fly25_mid DOUBLE,
            term_slope_mid DOUBLE
        );
        CREATE TABLE alert_outcomes (
            alert_id INTEGER,
            horizon_days INTEGER,
            outcome_label TEXT,
            resolved_snapshot_id INTEGER,
            resolved_ts TIMESTAMP,
            base_metric_value DOUBLE,
            resolved_metric_value DOUBLE,
            reversion_ratio DOUBLE,
            outcome_source TEXT,
            evaluated_at TIMESTAMP
        );
        """
    )


def test_evaluate_outcomes_respects_underlying(monkeypatch, tmp_path):
    db_path = tmp_path / "outcomes.duckdb"
    conn = duckdb.connect(str(db_path))
    try:
        _create_ablation_tables(conn)
        base_ts = datetime(2026, 4, 1, 12, 0, 0)

        conn.execute("INSERT INTO pipeline_runs VALUES (1, 'cand123')")
        conn.execute("INSERT INTO snapshots VALUES (1, 1, ?, 'SPX')", (base_ts,))
        conn.execute("INSERT INTO snapshots VALUES (2, 1, ?, 'NDX')", (base_ts + timedelta(days=1),))
        conn.execute("INSERT INTO snapshots VALUES (3, 1, ?, 'SPX')", (base_ts + timedelta(days=1),))

        conn.execute("INSERT INTO alerts VALUES (10, 1, 'RR_EXTREME', '30D', 'Transition')")
        conn.execute("INSERT INTO surface_metrics VALUES (1, '30D', 1.0, 0.0, 0.0)")
        conn.execute("INSERT INTO surface_metrics VALUES (2, '30D', 0.1, 0.0, 0.0)")
        conn.execute("INSERT INTO surface_metrics VALUES (3, '30D', 0.5, 0.0, 0.0)")
    finally:
        conn.close()

    monkeypatch.setattr(
        outcome_mod,
        "connect",
        lambda: duckdb.connect(str(db_path)),
    )

    inserted = outcome_mod.evaluate_alert_outcomes(horizon_days=1, overwrite=True)
    assert inserted == 1

    check = duckdb.connect(str(db_path))
    try:
        resolved_snapshot_id = check.execute(
            "SELECT resolved_snapshot_id FROM alert_outcomes WHERE alert_id = 10"
        ).fetchone()[0]
    finally:
        check.close()

    assert resolved_snapshot_id == 3


def test_ablation_metrics_use_real_lineage_data(monkeypatch, tmp_path):
    db_path = tmp_path / "ablation.duckdb"
    conn = duckdb.connect(str(db_path))
    try:
        _create_ablation_tables(conn)
        ts = datetime(2026, 4, 2, 12, 0, 0)

        conn.execute("INSERT INTO pipeline_runs VALUES (1, 'base001')")
        conn.execute("INSERT INTO pipeline_runs VALUES (2, 'cand001')")
        conn.execute("INSERT INTO snapshots VALUES (11, 1, ?, 'SPX')", (ts,))
        conn.execute("INSERT INTO snapshots VALUES (22, 2, ?, 'SPX')", (ts,))

        conn.execute("INSERT INTO alerts VALUES (101, 11, 'RR_EXTREME', '30D', 'Transition')")
        conn.execute("INSERT INTO alerts VALUES (202, 22, 'RR_EXTREME', '30D', 'Transition')")

        now = datetime.utcnow()
        conn.execute(
            "INSERT INTO alert_outcomes VALUES (101, 5, 'fp', 11, ?, 1.0, 0.9, 0.1, 'test', ?)",
            (ts, now),
        )
        conn.execute(
            "INSERT INTO alert_outcomes VALUES (202, 5, 'tp', 22, ?, 1.0, 0.2, 0.8, 'test', ?)",
            (ts, now),
        )
    finally:
        conn.close()

    monkeypatch.setattr(ablation_mod, "connect", lambda: duckdb.connect(str(db_path)))

    baseline_total, _, _ = ablation_mod._fetch_alert_stats(
        "SPX", "2026-04-01T00:00:00Z", "2026-04-15T23:59:59Z", "base001"
    )
    candidate_total, _, _ = ablation_mod._fetch_alert_stats(
        "SPX", "2026-04-01T00:00:00Z", "2026-04-15T23:59:59Z", "cand001"
    )
    baseline_metrics = ablation_mod._fetch_precision_metrics(
        "SPX", "2026-04-01T00:00:00Z", "2026-04-15T23:59:59Z", "base001", 5
    )
    candidate_metrics = ablation_mod._fetch_precision_metrics(
        "SPX", "2026-04-01T00:00:00Z", "2026-04-15T23:59:59Z", "cand001", 5
    )

    assert baseline_total == 1
    assert candidate_total == 1
    assert baseline_metrics["precision"] == 0.0
    assert candidate_metrics["precision"] == 1.0
