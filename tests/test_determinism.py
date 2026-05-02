from __future__ import annotations

from datetime import date, datetime
import json
from pathlib import Path

import duckdb

from src.core.compute_snapshot import compute_for_snapshot
from src.core.metrics import IvPoint


def test_compute_for_snapshot_is_repeatable(monkeypatch):
    conn = duckdb.connect(":memory:")
    conn.execute(Path("src/db/schema.sql").read_text())
    conn.execute(
        """
        INSERT INTO snapshots (
            snapshot_id, run_id, ts, underlying, spot, source, session_tag, notes
        ) VALUES (DEFAULT, NULL, ?, 'SPX', 100.0, 'test', 'mid', NULL)
        """,
        (datetime(2026, 2, 13),),
    )
    conn.execute(
        """
        INSERT INTO option_quotes (
            quote_id, snapshot_id, expiry, strike, option_right, bid, ask, last,
            bid_size, ask_size, oi, volume, flags
        ) VALUES (DEFAULT, 1, '2026-03-15', 100.0, 'C', 1.0, 1.2, 0.0, 0, 0, 0, 0, NULL)
        """
    )
    conn.execute(
        """
        INSERT INTO regime_state (
            regime_date,
            vix_percentile,
            rv20_percentile,
            drawdown_percent,
            regime_score,
            regime_label,
            regime_config_hash
        ) VALUES ('2026-02-13', 50, 50, 2, 0, 'Neutral', NULL)
        """
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
        expiry = date(2026, 3, 15)
        return [
            IvPoint(expiry, "ATM", 0.2, 0.19, 0.21, "ok", 1.0, fit_confidence=0.9),
            IvPoint(expiry, "+0.25C", 0.21, 0.20, 0.22, "ok", 1.0, fit_confidence=0.9),
            IvPoint(expiry, "-0.25P", 0.22, 0.21, 0.23, "ok", 1.0, fit_confidence=0.9),
            IvPoint(expiry, "+0.10C", 0.23, 0.22, 0.24, "ok", 1.0, fit_confidence=0.9),
            IvPoint(expiry, "-0.10P", 0.24, 0.23, 0.25, "ok", 1.0, fit_confidence=0.9),
        ]

    def fake_compute_surface_metrics(*_args, **_kwargs):
        return [
            {
                "expiry_bucket": "30D",
                "tier": "Full",
                "atm_iv_mid": 0.2,
                "rr25_mid": -0.01,
                "rr10_mid": -0.01,
                "fly25_mid": 0.015,
                "fly10_mid": 0.02,
                "term_slope_mid": 0.0,
                "atm_iv_worst": 0.19,
                "rr25_worst": -0.01,
                "rr10_worst": -0.01,
                "fly25_worst": 0.01,
                "fly10_worst": 0.015,
                "term_slope_worst": 0.0,
            }
        ]

    def fake_compute_alerts(*_args, **_kwargs):
        return [
            {
                "expiry_bucket": "30D",
                "alert_type": "FLY_EXTREME",
                "zscore_mid": 2.7,
                "zscore_worst": 2.2,
                "persistence": 2,
            }
        ]

    def fake_build_trade_ideas(*_args, **_kwargs):
        return [
            {
                "template": "Fly_1x2x1",
                "legs": json.dumps([{"right": "P", "delta": -0.25, "action": "BUY"}]),
                "price_mid": 1.23,
                "price_worst": 1.45,
                "greeks": json.dumps({"delta": -0.1}),
                "scenarios": json.dumps({}),
                "risk_flags": json.dumps(["pin_risk"]),
            }
        ]

    monkeypatch.setattr("src.core.compute_snapshot.connect", fake_connect)
    monkeypatch.setattr("src.core.compute_snapshot.compute_iv_points", fake_compute_iv_points)
    monkeypatch.setattr(
        "src.core.compute_snapshot.compute_surface_metrics",
        fake_compute_surface_metrics,
    )
    monkeypatch.setattr("src.core.compute_snapshot.compute_alerts", fake_compute_alerts)
    monkeypatch.setattr("src.core.compute_snapshot.compute_tradability_score", lambda *_args: 0.8)
    monkeypatch.setattr("src.core.compute_snapshot.build_trade_ideas", fake_build_trade_ideas)

    compute_for_snapshot(1, purge_existing=True)
    first_metrics = conn.execute(
        """
        SELECT expiry_bucket, atm_iv_mid, rr25_mid, rr10_mid, fly25_mid, fly10_mid,
               term_slope_mid, atm_iv_worst, rr25_worst, rr10_worst, fly25_worst,
               fly10_worst, term_slope_worst
        FROM surface_metrics
        ORDER BY expiry_bucket
        """
    ).fetchall()
    first_alerts = conn.execute(
        """
        SELECT alert_type, expiry_bucket, severity, zscore_mid, zscore_worst,
               tradability_score, confidence_tier, persistence_count, regime_label, explain
        FROM alerts
        ORDER BY alert_type, expiry_bucket
        """
    ).fetchall()
    first_ideas = conn.execute(
        """
        SELECT template, legs, price_mid, price_worst, greeks, scenarios, risk_flags
        FROM trade_ideas
        ORDER BY template
        """
    ).fetchall()

    compute_for_snapshot(1, purge_existing=True)
    second_metrics = conn.execute(
        """
        SELECT expiry_bucket, atm_iv_mid, rr25_mid, rr10_mid, fly25_mid, fly10_mid,
               term_slope_mid, atm_iv_worst, rr25_worst, rr10_worst, fly25_worst,
               fly10_worst, term_slope_worst
        FROM surface_metrics
        ORDER BY expiry_bucket
        """
    ).fetchall()
    second_alerts = conn.execute(
        """
        SELECT alert_type, expiry_bucket, severity, zscore_mid, zscore_worst,
               tradability_score, confidence_tier, persistence_count, regime_label, explain
        FROM alerts
        ORDER BY alert_type, expiry_bucket
        """
    ).fetchall()
    second_ideas = conn.execute(
        """
        SELECT template, legs, price_mid, price_worst, greeks, scenarios, risk_flags
        FROM trade_ideas
        ORDER BY template
        """
    ).fetchall()

    assert first_metrics == second_metrics
    assert first_alerts == second_alerts
    assert first_ideas == second_ideas
