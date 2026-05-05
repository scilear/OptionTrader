from datetime import datetime
import logging
from pathlib import Path

import duckdb
import yaml

from src.core.compute_snapshot import compute_for_snapshot


def _seed_minimal_compute_schema(conn):
    conn.execute(
        """
        CREATE TABLE snapshots (snapshot_id INTEGER, ts TIMESTAMP, spot DOUBLE);
        CREATE TABLE option_quotes (snapshot_id INTEGER, expiry DATE, strike DOUBLE, option_right TEXT, bid DOUBLE, ask DOUBLE);
        CREATE TABLE iv_points (iv_id INTEGER, snapshot_id INTEGER, expiry DATE, delta_bucket TEXT, iv_mid DOUBLE, iv_bid DOUBLE, iv_ask DOUBLE, solve_status TEXT, quality_score DOUBLE, fit_model_id TEXT, fit_residual DOUBLE, fit_support INTEGER, fit_confidence DOUBLE, fit_reason_codes TEXT);
        CREATE TABLE surface_metrics (metric_id INTEGER, snapshot_id INTEGER, expiry_bucket TEXT, atm_iv_mid DOUBLE, rr25_mid DOUBLE, rr10_mid DOUBLE, fly25_mid DOUBLE, fly10_mid DOUBLE, term_slope_mid DOUBLE, atm_iv_worst DOUBLE, rr25_worst DOUBLE, rr10_worst DOUBLE, fly25_worst DOUBLE, fly10_worst DOUBLE, term_slope_worst DOUBLE, fit_model_id TEXT, fit_residual DOUBLE, fit_support INTEGER, fit_confidence DOUBLE, surface_quality_score DOUBLE, qc_pass BOOLEAN, qc_reason_codes TEXT);
        CREATE TABLE alerts (alert_id INTEGER, snapshot_id INTEGER, alert_type TEXT, expiry_bucket TEXT, severity DOUBLE, zscore_mid DOUBLE, zscore_worst DOUBLE, tradability_score DOUBLE, confidence_tier TEXT, persistence_count INTEGER, regime_label TEXT, signal_state TEXT, transition_reason_code TEXT, explain TEXT);
        CREATE TABLE trade_ideas (trade_id INTEGER, alert_id INTEGER, template TEXT, legs TEXT, price_mid DOUBLE, price_worst DOUBLE, greeks TEXT, scenarios TEXT, risk_flags TEXT);
        CREATE TABLE regime_state (regime_date DATE PRIMARY KEY, vix_percentile DOUBLE, rv20_percentile DOUBLE, drawdown_percent DOUBLE, regime_score INTEGER, regime_label TEXT, regime_config_hash TEXT);
        """
    )


def _load_test_config_with_overrides(**overrides):
    config = yaml.safe_load(Path("config/config-test.yaml").read_text())
    alerts_cfg = config.setdefault("alerts", {})
    lifecycle_cfg = alerts_cfg.setdefault("lifecycle", {})
    for key, value in overrides.items():
        if key.startswith("lifecycle_"):
            lifecycle_cfg[key.replace("lifecycle_", "")] = value
        else:
            alerts_cfg[key] = value
    return config


def _seed_minimal_compute_schema_with_underlying_run(conn):
    conn.execute(
        """
        CREATE TABLE snapshots (
            snapshot_id INTEGER,
            ts TIMESTAMP,
            spot DOUBLE,
            run_id INTEGER,
            underlying TEXT
        );
        CREATE TABLE option_quotes (snapshot_id INTEGER, expiry DATE, strike DOUBLE, option_right TEXT, bid DOUBLE, ask DOUBLE);
        CREATE TABLE iv_points (iv_id INTEGER, snapshot_id INTEGER, expiry DATE, delta_bucket TEXT, iv_mid DOUBLE, iv_bid DOUBLE, iv_ask DOUBLE, solve_status TEXT, quality_score DOUBLE, fit_model_id TEXT, fit_residual DOUBLE, fit_support INTEGER, fit_confidence DOUBLE, fit_reason_codes TEXT);
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
            term_slope_worst DOUBLE,
            fit_model_id TEXT,
            fit_residual DOUBLE,
            fit_support INTEGER,
            fit_confidence DOUBLE,
            surface_quality_score DOUBLE,
            qc_pass BOOLEAN,
            qc_reason_codes TEXT
        );
        CREATE TABLE alerts (alert_id INTEGER, snapshot_id INTEGER, alert_type TEXT, expiry_bucket TEXT, severity DOUBLE, zscore_mid DOUBLE, zscore_worst DOUBLE, tradability_score DOUBLE, confidence_tier TEXT, persistence_count INTEGER, regime_label TEXT, signal_state TEXT, transition_reason_code TEXT, explain TEXT);
        CREATE TABLE trade_ideas (trade_id INTEGER, alert_id INTEGER, template TEXT, legs TEXT, price_mid DOUBLE, price_worst DOUBLE, greeks TEXT, scenarios TEXT, risk_flags TEXT);
        CREATE TABLE regime_state (regime_date DATE PRIMARY KEY, vix_percentile DOUBLE, rv20_percentile DOUBLE, drawdown_percent DOUBLE, regime_score INTEGER, regime_label TEXT, regime_config_hash TEXT);
        """
    )


def test_regime_filter_blocks_rr(monkeypatch):
    conn = duckdb.connect(":memory:")
    _seed_minimal_compute_schema(conn)
    conn.execute("INSERT INTO snapshots VALUES (1, ?, 100.0)", (datetime(2026, 2, 13),))
    conn.execute(
        "INSERT INTO regime_state VALUES ('2026-02-13', 90, 90, 12, 6, 'Stress', NULL)"
    )

    class ConnWrapper:
        def __init__(self, inner):
            self.inner = inner

        def execute(self, *args, **kwargs):
            return self.inner.execute(*args, **kwargs)

        def close(self):
            pass

    def fake_connect():
        return ConnWrapper(conn)

    def fake_compute_iv_points(*_args, **_kwargs):
        return []

    def fake_compute_surface_metrics(*_args, **_kwargs):
        return [{"expiry_bucket": "30D", "tier": "Core", "atm_iv_mid": 0.2, "rr25_mid": 0.1, "rr10_mid": 0.1, "fly25_mid": 0.1, "fly10_mid": 0.1, "term_slope_mid": 0.0}]

    def fake_compute_alerts(*_args, **_kwargs):
        return [{"expiry_bucket": "30D", "alert_type": "RR_EXTREME", "zscore_mid": 2.5, "zscore_worst": 2.1, "persistence": 2}]

    monkeypatch.setattr("src.core.compute_snapshot.connect", fake_connect)
    monkeypatch.setattr("src.core.compute_snapshot.compute_iv_points", fake_compute_iv_points)
    monkeypatch.setattr("src.core.compute_snapshot.compute_surface_metrics", fake_compute_surface_metrics)
    monkeypatch.setattr("src.core.compute_snapshot.compute_alerts", fake_compute_alerts)

    compute_for_snapshot(1, purge_existing=True)
    count = conn.execute("SELECT COUNT(*) FROM alerts").fetchone()[0]
    assert count == 0


def test_regime_hash_mismatch_logs_warning(monkeypatch, caplog):
    conn = duckdb.connect(":memory:")
    _seed_minimal_compute_schema(conn)
    conn.execute("INSERT INTO snapshots VALUES (1, ?, 100.0)", (datetime(2026, 2, 13),))
    conn.execute(
        "INSERT INTO regime_state VALUES ('2026-02-13', 50, 50, 2, 0, 'Neutral', 'stale_hash')"
    )

    class ConnWrapper:
        def __init__(self, inner):
            self.inner = inner

        def execute(self, *args, **kwargs):
            return self.inner.execute(*args, **kwargs)

        def close(self):
            pass

    monkeypatch.setattr("src.core.compute_snapshot.connect", lambda: ConnWrapper(conn))
    monkeypatch.setattr("src.core.compute_snapshot.compute_iv_points", lambda *_a, **_k: [])
    monkeypatch.setattr("src.core.compute_snapshot.compute_surface_metrics", lambda *_a, **_k: [])
    monkeypatch.setattr("src.core.compute_snapshot.compute_alerts", lambda *_a, **_k: [])
    monkeypatch.setattr("src.core.compute_snapshot.regime_threshold_hash", lambda *_a, **_k: "new_hash")
    monkeypatch.setattr("src.core.compute_snapshot.regime_params_from_config", lambda *_a, **_k: object())

    with caplog.at_level(logging.WARNING, logger="compute"):
        compute_for_snapshot(1, purge_existing=True)

    assert "Regime threshold hash mismatch" in caplog.text
    assert "persisted_hash=stale_hash" in caplog.text
    assert "current_hash=new_hash" in caplog.text


def test_regime_hash_match_has_no_warning(monkeypatch, caplog):
    conn = duckdb.connect(":memory:")
    _seed_minimal_compute_schema(conn)
    conn.execute("INSERT INTO snapshots VALUES (1, ?, 100.0)", (datetime(2026, 2, 13),))
    conn.execute(
        "INSERT INTO regime_state VALUES ('2026-02-13', 50, 50, 2, 0, 'Neutral', 'same_hash')"
    )

    class ConnWrapper:
        def __init__(self, inner):
            self.inner = inner

        def execute(self, *args, **kwargs):
            return self.inner.execute(*args, **kwargs)

        def close(self):
            pass

    monkeypatch.setattr("src.core.compute_snapshot.connect", lambda: ConnWrapper(conn))
    monkeypatch.setattr("src.core.compute_snapshot.compute_iv_points", lambda *_a, **_k: [])
    monkeypatch.setattr("src.core.compute_snapshot.compute_surface_metrics", lambda *_a, **_k: [])
    monkeypatch.setattr("src.core.compute_snapshot.compute_alerts", lambda *_a, **_k: [])
    monkeypatch.setattr("src.core.compute_snapshot.regime_threshold_hash", lambda *_a, **_k: "same_hash")
    monkeypatch.setattr("src.core.compute_snapshot.regime_params_from_config", lambda *_a, **_k: object())

    with caplog.at_level(logging.WARNING, logger="compute"):
        compute_for_snapshot(1, purge_existing=True)

    assert "Regime threshold hash mismatch" not in caplog.text


def test_emit_non_execution_states_persists_candidate(monkeypatch):
    conn = duckdb.connect(":memory:")
    _seed_minimal_compute_schema(conn)
    conn.execute("INSERT INTO snapshots VALUES (1, ?, 100.0)", (datetime(2026, 2, 13),))
    conn.execute(
        "INSERT INTO option_quotes VALUES (1, '2026-03-15', 100.0, 'C', 1.0, 1.2)"
    )
    conn.execute(
        "INSERT INTO regime_state VALUES ('2026-02-13', 50, 50, 2, 0, 'Neutral', 'same_hash')"
    )

    class ConnWrapper:
        def __init__(self, inner):
            self.inner = inner

        def execute(self, *args, **kwargs):
            return self.inner.execute(*args, **kwargs)

        def close(self):
            pass

    monkeypatch.setattr("src.core.compute_snapshot.connect", lambda: ConnWrapper(conn))
    monkeypatch.setattr(
        "src.core.compute_snapshot.load_config",
        lambda path=None: _load_test_config_with_overrides(emit_non_execution_states=True),
    )
    monkeypatch.setattr("src.core.compute_snapshot.compute_iv_points", lambda *_a, **_k: [])
    monkeypatch.setattr(
        "src.core.compute_snapshot.compute_surface_metrics",
        lambda *_a, **_k: [
            {
                "expiry_bucket": "30D",
                "tier": "Core",
                "atm_iv_mid": 0.2,
                "rr25_mid": 0.1,
                "rr10_mid": 0.1,
                "fly25_mid": 0.1,
                "fly10_mid": 0.1,
                "term_slope_mid": 0.0,
            }
        ],
    )
    monkeypatch.setattr(
        "src.core.compute_snapshot.compute_alerts",
        lambda *_a, **_k: [
            {
                "expiry_bucket": "30D",
                "alert_type": "TERM_KINK",
                "zscore_mid": 2.5,
                "zscore_worst": 2.2,
                "persistence": 2,
            }
        ],
    )
    monkeypatch.setattr("src.core.compute_snapshot.regime_threshold_hash", lambda *_a, **_k: "same_hash")
    monkeypatch.setattr("src.core.compute_snapshot.regime_params_from_config", lambda *_a, **_k: object())

    compute_for_snapshot(1, purge_existing=True)

    row = conn.execute(
        "SELECT signal_state, transition_reason_code FROM alerts LIMIT 1"
    ).fetchone()
    assert row == ("Candidate", "fit_confidence_below_validated")


def test_lifecycle_validated_state_when_execution_blocked(monkeypatch):
    conn = duckdb.connect(":memory:")
    _seed_minimal_compute_schema(conn)
    conn.execute("INSERT INTO snapshots VALUES (1, ?, 100.0)", (datetime(2026, 2, 13),))
    conn.execute(
        "INSERT INTO option_quotes VALUES (1, '2026-03-15', 100.0, 'C', 1.0, 1.2)"
    )
    conn.execute(
        "INSERT INTO regime_state VALUES ('2026-02-13', 50, 50, 2, 0, 'Neutral', 'same_hash')"
    )

    class ConnWrapper:
        def __init__(self, inner):
            self.inner = inner

        def execute(self, *args, **kwargs):
            return self.inner.execute(*args, **kwargs)

        def close(self):
            pass

    class Point:
        expiry = datetime(2026, 3, 15).date()
        delta_bucket = "ATM"
        iv_mid = 0.2
        iv_bid = 0.19
        iv_ask = 0.21
        solve_status = "ok"
        quality_score = 1.0
        fit_model_id = "test"
        fit_residual = 0.0
        fit_support = 5
        fit_confidence = 0.9
        fit_reason_codes = ()

    def fake_tradability_score(*_args, **_kwargs):
        return 0.7

    monkeypatch.setattr("src.core.compute_snapshot.connect", lambda: ConnWrapper(conn))
    monkeypatch.setattr(
        "src.core.compute_snapshot.load_config",
        lambda path=None: _load_test_config_with_overrides(
            emit_non_execution_states=True,
            lifecycle_require_full_tier_for_execution=True,
        ),
    )
    monkeypatch.setattr("src.core.compute_snapshot.compute_iv_points", lambda *_a, **_k: [Point()])
    monkeypatch.setattr(
        "src.core.compute_snapshot.compute_tradability_score",
        fake_tradability_score,
    )
    monkeypatch.setattr(
        "src.core.compute_snapshot.compute_surface_metrics",
        lambda *_a, **_k: [
            {
                "expiry_bucket": "30D",
                "tier": "Core",
                "atm_iv_mid": 0.2,
                "rr25_mid": 0.1,
                "rr10_mid": 0.1,
                "fly25_mid": 0.1,
                "fly10_mid": 0.1,
                "term_slope_mid": 0.0,
                "atm_iv_worst": 0.2,
                "rr25_worst": 0.1,
                "rr10_worst": 0.1,
                "fly25_worst": 0.1,
                "fly10_worst": 0.1,
                "term_slope_worst": 0.0,
            }
        ],
    )
    monkeypatch.setattr(
        "src.core.compute_snapshot.compute_alerts",
        lambda *_a, **_k: [
            {
                "expiry_bucket": "30D",
                "alert_type": "TERM_KINK",
                "zscore_mid": 2.5,
                "zscore_worst": 2.2,
                "persistence": 2,
            }
        ],
    )
    monkeypatch.setattr("src.core.compute_snapshot.regime_threshold_hash", lambda *_a, **_k: "same_hash")
    monkeypatch.setattr("src.core.compute_snapshot.regime_params_from_config", lambda *_a, **_k: object())

    compute_for_snapshot(1, purge_existing=True)

    row = conn.execute(
        "SELECT signal_state, transition_reason_code FROM alerts LIMIT 1"
    ).fetchone()
    assert row == ("Validated", "tier_not_full")


def test_metric_series_uses_qc_pass_rows_only(monkeypatch):
    conn = duckdb.connect(":memory:")
    _seed_minimal_compute_schema_with_underlying_run(conn)
    conn.execute(
        "INSERT INTO snapshots VALUES (1, ?, 100.0, 101, 'SPX')",
        (datetime(2026, 2, 13),),
    )
    conn.execute(
        "INSERT INTO option_quotes VALUES (1, '2026-03-15', 100.0, 'C', 1.0, 1.2)"
    )
    conn.execute(
        "INSERT INTO regime_state VALUES ('2026-02-13', 50, 50, 2, 0, 'Neutral', 'same_hash')"
    )
    conn.execute(
        """
        INSERT INTO snapshots VALUES
            (2, '2026-02-10 16:00:00', 99.0, 101, 'SPX'),
            (3, '2026-02-11 16:00:00', 99.5, 101, 'SPX')
        """
    )
    conn.execute(
        """
        INSERT INTO surface_metrics VALUES
            (10, 2, '30D', 0.2, 1.0, 0.0, 0.0, 0.0, 0.0, 0.2, 1.0, 0.0, 0.0, 0.0, 0.0, 'fit', 0.0, 5, 0.9, 0.9, TRUE, '[]'),
            (11, 3, '30D', 0.2, 5.0, 0.0, 0.0, 0.0, 0.0, 0.2, 5.0, 0.0, 0.0, 0.0, 0.0, 'fit', 0.0, 5, 0.9, 0.9, FALSE, '["surface_qc_failed"]')
        """
    )

    class ConnWrapper:
        def __init__(self, inner):
            self.inner = inner

        def execute(self, *args, **kwargs):
            return self.inner.execute(*args, **kwargs)

        def close(self):
            pass

    captured = {}

    def fake_compute_alerts(metrics_df, *_args, **_kwargs):
        captured["rr25_mid_values"] = list(metrics_df["rr25_mid"].tolist())
        return []

    monkeypatch.setattr("src.core.compute_snapshot.connect", lambda: ConnWrapper(conn))
    monkeypatch.setattr(
        "src.core.compute_snapshot.load_config",
        lambda path=None: _load_test_config_with_overrides(
            history_scope="run",
            metric_series_qc_only=True,
        ),
    )
    monkeypatch.setattr("src.core.compute_snapshot.compute_iv_points", lambda *_a, **_k: [])
    monkeypatch.setattr(
        "src.core.compute_snapshot.compute_surface_metrics",
        lambda *_a, **_k: [
            {
                "expiry_bucket": "30D",
                "tier": "Core",
                "atm_iv_mid": 0.2,
                "rr25_mid": 0.1,
                "rr10_mid": 0.1,
                "fly25_mid": 0.1,
                "fly10_mid": 0.1,
                "term_slope_mid": 0.0,
                "atm_iv_worst": 0.2,
                "rr25_worst": 0.1,
                "rr10_worst": 0.1,
                "fly25_worst": 0.1,
                "fly10_worst": 0.1,
                "term_slope_worst": 0.0,
            }
        ],
    )
    monkeypatch.setattr("src.core.compute_snapshot.compute_alerts", fake_compute_alerts)
    monkeypatch.setattr("src.core.compute_snapshot.regime_threshold_hash", lambda *_a, **_k: "same_hash")
    monkeypatch.setattr("src.core.compute_snapshot.regime_params_from_config", lambda *_a, **_k: object())

    compute_for_snapshot(1, purge_existing=True)

    assert captured["rr25_mid_values"] == [1.0, 0.1]


def test_metric_series_filters_future_and_other_underlying(monkeypatch):
    conn = duckdb.connect(":memory:")
    _seed_minimal_compute_schema_with_underlying_run(conn)
    conn.execute(
        "INSERT INTO snapshots VALUES (1, ?, 100.0, NULL, 'SPX')",
        (datetime(2026, 2, 13),),
    )
    conn.execute(
        "INSERT INTO option_quotes VALUES (1, '2026-03-15', 100.0, 'C', 1.0, 1.2)"
    )
    conn.execute(
        "INSERT INTO regime_state VALUES ('2026-02-13', 50, 50, 2, 0, 'Neutral', 'same_hash')"
    )
    conn.execute(
        """
        INSERT INTO snapshots VALUES
            (2, '2026-02-10 16:00:00', 99.0, NULL, 'SPX'),
            (3, '2026-02-14 16:00:00', 99.5, NULL, 'SPX'),
            (4, '2026-02-11 16:00:00', 101.0, NULL, 'NDX')
        """
    )
    conn.execute(
        """
        INSERT INTO surface_metrics VALUES
            (20, 2, '30D', 0.2, 1.0, 0.0, 0.0, 0.0, 0.0, 0.2, 1.0, 0.0, 0.0, 0.0, 0.0, 'fit', 0.0, 5, 0.9, 0.9, TRUE, '[]'),
            (21, 3, '30D', 0.2, 2.0, 0.0, 0.0, 0.0, 0.0, 0.2, 2.0, 0.0, 0.0, 0.0, 0.0, 'fit', 0.0, 5, 0.9, 0.9, TRUE, '[]'),
            (22, 4, '30D', 0.2, 3.0, 0.0, 0.0, 0.0, 0.0, 0.2, 3.0, 0.0, 0.0, 0.0, 0.0, 'fit', 0.0, 5, 0.9, 0.9, TRUE, '[]')
        """
    )

    class ConnWrapper:
        def __init__(self, inner):
            self.inner = inner

        def execute(self, *args, **kwargs):
            return self.inner.execute(*args, **kwargs)

        def close(self):
            pass

    captured = {}

    def fake_compute_alerts(metrics_df, *_args, **_kwargs):
        captured["rr25_mid_values"] = list(metrics_df["rr25_mid"].tolist())
        return []

    monkeypatch.setattr("src.core.compute_snapshot.connect", lambda: ConnWrapper(conn))
    monkeypatch.setattr(
        "src.core.compute_snapshot.load_config",
        lambda path=None: _load_test_config_with_overrides(
            history_scope="global",
            metric_series_qc_only=True,
        ),
    )
    monkeypatch.setattr("src.core.compute_snapshot.compute_iv_points", lambda *_a, **_k: [])
    monkeypatch.setattr(
        "src.core.compute_snapshot.compute_surface_metrics",
        lambda *_a, **_k: [
            {
                "expiry_bucket": "30D",
                "tier": "Core",
                "atm_iv_mid": 0.2,
                "rr25_mid": 0.1,
                "rr10_mid": 0.1,
                "fly25_mid": 0.1,
                "fly10_mid": 0.1,
                "term_slope_mid": 0.0,
                "atm_iv_worst": 0.2,
                "rr25_worst": 0.1,
                "rr10_worst": 0.1,
                "fly25_worst": 0.1,
                "fly10_worst": 0.1,
                "term_slope_worst": 0.0,
            }
        ],
    )
    monkeypatch.setattr("src.core.compute_snapshot.compute_alerts", fake_compute_alerts)
    monkeypatch.setattr("src.core.compute_snapshot.regime_threshold_hash", lambda *_a, **_k: "same_hash")
    monkeypatch.setattr("src.core.compute_snapshot.regime_params_from_config", lambda *_a, **_k: object())

    compute_for_snapshot(1, purge_existing=True)

    assert captured["rr25_mid_values"] == [1.0, 0.1]
