from __future__ import annotations

from datetime import datetime

import pandas as pd

from src.core.metrics import compute_iv_points


def _quotes_for_chain(strikes: list[float], base_bid: float = 1.0, spread: float = 0.2) -> pd.DataFrame:
    rows: list[dict] = []
    for strike in strikes:
        rows.append(
            {
                "expiry": "2026-03-15",
                "strike": strike,
                "option_right": "C",
                "bid": base_bid,
                "ask": base_bid + spread,
            }
        )
        rows.append(
            {
                "expiry": "2026-03-15",
                "strike": strike,
                "option_right": "P",
                "bid": base_bid,
                "ask": base_bid + spread,
            }
        )
    return pd.DataFrame(rows)


def test_stability_score_one_strike_removal_is_bounded(monkeypatch) -> None:
    class _IvResult:
        def __init__(self, iv: float):
            self.iv = iv

    def fake_solve_iv(*_args, **_kwargs):
        return _IvResult(0.20)

    delta_map_call = {80.0: 0.45, 90.0: 0.30, 95.0: 0.25, 100.0: 0.50, 105.0: 0.20, 110.0: 0.15}
    delta_map_put = {80.0: -0.15, 90.0: -0.20, 95.0: -0.25, 100.0: -0.50, 105.0: -0.30, 110.0: -0.45}

    def fake_bs_delta(_spot, strike, _rate, _div, _t_years, _iv, right):
        if right == "C":
            return delta_map_call[float(strike)]
        return delta_map_put[float(strike)]

    monkeypatch.setattr("src.core.metrics.solve_iv", fake_solve_iv)
    monkeypatch.setattr("src.core.metrics.bs_delta", fake_bs_delta)

    ts = datetime(2026, 2, 13)
    full_chain = _quotes_for_chain([80.0, 90.0, 95.0, 100.0, 105.0, 110.0])
    removed_chain = _quotes_for_chain([80.0, 90.0, 100.0, 105.0, 110.0])

    full_points = compute_iv_points(full_chain, ts, 100.0, spread_gate_pct=0.5, delta_points=[0.25])
    removed_points = compute_iv_points(removed_chain, ts, 100.0, spread_gate_pct=0.5, delta_points=[0.25])

    full_by_bucket = {p.delta_bucket: p.iv_mid for p in full_points}
    removed_by_bucket = {p.delta_bucket: p.iv_mid for p in removed_points}

    max_delta_iv = max(abs((full_by_bucket[b] or 0.0) - (removed_by_bucket[b] or 0.0)) for b in {"+0.25C", "-0.25P", "ATM"})
    assert max_delta_iv <= 0.02


def test_sparse_wings_emit_degraded_status(monkeypatch) -> None:
    class _IvResult:
        def __init__(self, iv: float):
            self.iv = iv

    def fake_solve_iv(*_args, **_kwargs):
        return _IvResult(0.20)

    def fake_bs_delta(_spot, strike, _rate, _div, _t_years, _iv, right):
        if right == "C":
            return {100.0: 0.50, 110.0: 0.30}[float(strike)]
        return {90.0: -0.30, 100.0: -0.50}[float(strike)]

    monkeypatch.setattr("src.core.metrics.solve_iv", fake_solve_iv)
    monkeypatch.setattr("src.core.metrics.bs_delta", fake_bs_delta)

    ts = datetime(2026, 2, 13)
    quotes = pd.DataFrame(
        [
            {"expiry": "2026-03-15", "strike": 100.0, "option_right": "C", "bid": 1.0, "ask": 1.2},
            {"expiry": "2026-03-15", "strike": 110.0, "option_right": "C", "bid": 1.0, "ask": 1.2},
            {"expiry": "2026-03-15", "strike": 90.0, "option_right": "P", "bid": 1.0, "ask": 1.2},
            {"expiry": "2026-03-15", "strike": 100.0, "option_right": "P", "bid": 1.0, "ask": 1.2},
        ]
    )

    points = compute_iv_points(quotes, ts, 100.0, spread_gate_pct=0.5, delta_points=[0.10])
    status_by_bucket = {p.delta_bucket: p.solve_status for p in points}
    assert status_by_bucket["+0.10C"] == "degraded"
    assert status_by_bucket["-0.10P"] == "degraded"
