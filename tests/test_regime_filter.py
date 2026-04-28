from datetime import datetime

import duckdb

from src.core.compute_snapshot import compute_for_snapshot


def test_regime_filter_blocks_rr(monkeypatch):
    conn = duckdb.connect(":memory:")
    conn.execute(
        """
        CREATE TABLE snapshots (snapshot_id INTEGER, ts TIMESTAMP, spot DOUBLE);
        CREATE TABLE option_quotes (snapshot_id INTEGER, expiry DATE, strike DOUBLE, option_right TEXT, bid DOUBLE, ask DOUBLE);
        CREATE TABLE iv_points (iv_id INTEGER, snapshot_id INTEGER, expiry DATE, delta_bucket TEXT, iv_mid DOUBLE, iv_bid DOUBLE, iv_ask DOUBLE, solve_status TEXT, quality_score DOUBLE);
        CREATE TABLE surface_metrics (metric_id INTEGER, snapshot_id INTEGER, expiry_bucket TEXT, atm_iv_mid DOUBLE, rr25_mid DOUBLE, rr10_mid DOUBLE, fly25_mid DOUBLE, fly10_mid DOUBLE, term_slope_mid DOUBLE, atm_iv_worst DOUBLE, rr25_worst DOUBLE, rr10_worst DOUBLE, fly25_worst DOUBLE, fly10_worst DOUBLE, term_slope_worst DOUBLE);
        CREATE TABLE alerts (alert_id INTEGER, snapshot_id INTEGER, alert_type TEXT, expiry_bucket TEXT, severity DOUBLE, zscore_mid DOUBLE, zscore_worst DOUBLE, tradability_score DOUBLE, confidence_tier TEXT, persistence_count INTEGER, regime_label TEXT, explain TEXT);
        CREATE TABLE trade_ideas (trade_id INTEGER, alert_id INTEGER, template TEXT, legs TEXT, price_mid DOUBLE, price_worst DOUBLE, greeks TEXT, scenarios TEXT, risk_flags TEXT);
        CREATE TABLE regime_state (regime_date DATE PRIMARY KEY, vix_percentile DOUBLE, rv20_percentile DOUBLE, drawdown_percent DOUBLE, regime_score INTEGER, regime_label TEXT, regime_config_hash TEXT);
        """
    )
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
