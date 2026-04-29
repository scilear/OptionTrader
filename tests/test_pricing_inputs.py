from __future__ import annotations

from datetime import date, datetime
from pathlib import Path

import duckdb
import pandas as pd
import yaml

from src.core.compute_snapshot import compute_for_snapshot
from src.core.iv_solve import _bs_price
from src.core.metrics import compute_iv_points


def _quote_row(
    spot: float,
    strike: float,
    expiry: date,
    snapshot_ts: datetime,
    vol: float,
    right: str,
) -> dict:
    t_years = (expiry - snapshot_ts.date()).days / 365
    mid = _bs_price(spot, strike, 0.0, 0.0, t_years, vol, right)
    return {
        "expiry": expiry.isoformat(),
        "strike": strike,
        "option_right": right,
        "bid": mid * 0.99,
        "ask": mid * 1.01,
    }


def test_compute_iv_points_changes_when_pricing_inputs_change():
    snapshot_ts = datetime(2026, 1, 1)
    expiry = date(2027, 1, 1)
    quotes = pd.DataFrame(
        [
            _quote_row(100.0, 90.0, expiry, snapshot_ts, 0.15, "C"),
            _quote_row(100.0, 90.0, expiry, snapshot_ts, 0.15, "P"),
            _quote_row(100.0, 100.0, expiry, snapshot_ts, 0.35, "C"),
            _quote_row(100.0, 100.0, expiry, snapshot_ts, 0.35, "P"),
        ]
    )

    base_points = compute_iv_points(
        quotes,
        snapshot_ts,
        100.0,
        spread_gate_pct=0.5,
        rate=0.0,
        div=0.0,
    )
    high_div_points = compute_iv_points(
        quotes,
        snapshot_ts,
        100.0,
        spread_gate_pct=0.5,
        rate=0.0,
        div=0.2,
    )

    base_atm = next(point.iv_mid for point in base_points if point.delta_bucket == "ATM")
    high_div_atm = next(point.iv_mid for point in high_div_points if point.delta_bucket == "ATM")
    assert base_atm is not None
    assert high_div_atm is not None
    assert abs(base_atm - high_div_atm) > 0.05


def test_compute_for_snapshot_passes_configured_pricing_inputs(monkeypatch, tmp_path):
    config = yaml.safe_load(Path("config/config-test.yaml").read_text())
    config["storage"]["path"] = str(tmp_path / "pricing.duckdb")
    config["pricing"]["rate"] = 0.03
    config["pricing"]["dividend_yield"] = 0.01
    config_path = tmp_path / "config.yaml"
    config_path.write_text(yaml.safe_dump(config, sort_keys=False))
    monkeypatch.setenv("OPTIONTRADER_CONFIG", str(config_path))

    conn = duckdb.connect(str(tmp_path / "pricing.duckdb"))
    conn.execute(
        """
        CREATE TABLE snapshots (snapshot_id INTEGER, ts TIMESTAMP, spot DOUBLE);
        CREATE TABLE option_quotes (snapshot_id INTEGER, expiry DATE, strike DOUBLE, option_right TEXT, bid DOUBLE, ask DOUBLE);
        CREATE TABLE iv_points (iv_id INTEGER, snapshot_id INTEGER, expiry DATE, delta_bucket TEXT, iv_mid DOUBLE, iv_bid DOUBLE, iv_ask DOUBLE, solve_status TEXT, quality_score DOUBLE, fit_model_id TEXT, fit_residual DOUBLE, fit_support INTEGER, fit_confidence DOUBLE, fit_reason_codes TEXT);
        CREATE TABLE surface_metrics (metric_id INTEGER, snapshot_id INTEGER, expiry_bucket TEXT, atm_iv_mid DOUBLE, rr25_mid DOUBLE, rr10_mid DOUBLE, fly25_mid DOUBLE, fly10_mid DOUBLE, term_slope_mid DOUBLE, atm_iv_worst DOUBLE, rr25_worst DOUBLE, rr10_worst DOUBLE, fly25_worst DOUBLE, fly10_worst DOUBLE, term_slope_worst DOUBLE, fit_model_id TEXT, fit_residual DOUBLE, fit_support INTEGER, fit_confidence DOUBLE, surface_quality_score DOUBLE, qc_pass BOOLEAN, qc_reason_codes TEXT);
        CREATE TABLE alerts (alert_id INTEGER, snapshot_id INTEGER, alert_type TEXT, expiry_bucket TEXT, severity DOUBLE, zscore_mid DOUBLE, zscore_worst DOUBLE, tradability_score DOUBLE, confidence_tier TEXT, persistence_count INTEGER, regime_label TEXT, explain TEXT);
        CREATE TABLE trade_ideas (trade_id INTEGER, alert_id INTEGER, template TEXT, legs TEXT, price_mid DOUBLE, price_worst DOUBLE, greeks TEXT, scenarios TEXT, risk_flags TEXT);
        CREATE TABLE regime_state (regime_date DATE PRIMARY KEY, vix_percentile DOUBLE, rv20_percentile DOUBLE, drawdown_percent DOUBLE, regime_score INTEGER, regime_label TEXT, regime_config_hash TEXT);
        """
    )
    conn.execute("INSERT INTO snapshots VALUES (1, ?, 100.0)", (datetime(2026, 2, 13),))
    conn.execute(
        "INSERT INTO option_quotes VALUES (1, '2026-03-15', 100.0, 'C', 1.0, 1.2)"
    )
    conn.execute(
        "INSERT INTO regime_state VALUES ('2026-02-13', 50, 50, 2, 0, 'Neutral', NULL)"
    )

    class ConnWrapper:
        def __init__(self, inner):
            self.inner = inner

        def execute(self, *args, **kwargs):
            return self.inner.execute(*args, **kwargs)

        def close(self):
            pass

    captured: dict[str, float] = {}

    def fake_connect():
        return ConnWrapper(conn)

    def fake_compute_iv_points(*_args, **_kwargs):
        return []

    def fake_compute_surface_metrics(*_args, **_kwargs):
        return [
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
        ]

    def fake_compute_alerts(*_args, **_kwargs):
        return [
            {
                "expiry_bucket": "30D",
                "alert_type": "TERM_KINK",
                "zscore_mid": 2.5,
                "zscore_worst": 2.2,
                "persistence": 2,
            }
        ]

    def fake_build_trade_ideas(_alert_type, _expiry_bucket, context):
        captured["rate"] = context.rate
        captured["div"] = context.div
        return []

    monkeypatch.setattr("src.core.compute_snapshot.connect", fake_connect)
    monkeypatch.setattr("src.core.compute_snapshot.compute_iv_points", fake_compute_iv_points)
    monkeypatch.setattr(
        "src.core.compute_snapshot.compute_surface_metrics",
        fake_compute_surface_metrics,
    )
    monkeypatch.setattr("src.core.compute_snapshot.compute_alerts", fake_compute_alerts)
    monkeypatch.setattr("src.core.compute_snapshot.build_trade_ideas", fake_build_trade_ideas)

    compute_for_snapshot(1, purge_existing=True)

    assert captured["rate"] == 0.03
    assert captured["div"] == 0.01
