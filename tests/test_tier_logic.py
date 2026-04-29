from datetime import datetime, date

import pandas as pd

from src.core.metrics import compute_surface_metrics, IvPoint


def test_tier_full_vs_core():
    ts = datetime(2026, 2, 13)
    points = [
        IvPoint(date(2026, 3, 15), "ATM", 0.2, 0.19, 0.21, "ok", 1.0),
        IvPoint(date(2026, 3, 15), "+0.25C", 0.21, 0.2, 0.22, "ok", 1.0),
        IvPoint(date(2026, 3, 15), "-0.25P", 0.22, 0.21, 0.23, "ok", 1.0),
        IvPoint(date(2026, 3, 15), "+0.10C", 0.23, 0.22, 0.24, "ok", 1.0),
        IvPoint(date(2026, 3, 15), "-0.10P", 0.24, 0.23, 0.25, "ok", 1.0),
    ]
    metrics = compute_surface_metrics(points, ts, [30])
    assert metrics[0]["tier"] == "Full"


def test_tier_respects_min_valid_points_thresholds():
    ts = datetime(2026, 2, 13)
    points = [
        IvPoint(date(2026, 3, 15), "ATM", 0.2, 0.19, 0.21, "ok", 1.0),
        IvPoint(date(2026, 3, 15), "+0.25C", 0.21, 0.2, 0.22, "ok", 1.0),
        IvPoint(date(2026, 3, 15), "-0.25P", 0.22, 0.21, 0.23, "ok", 1.0),
        IvPoint(date(2026, 3, 15), "+0.10C", 0.23, 0.22, 0.24, "ok", 1.0),
        IvPoint(date(2026, 3, 15), "-0.10P", 0.24, 0.23, 0.25, "ok", 0.0),
    ]
    metrics = compute_surface_metrics(
        points,
        ts,
        [30],
        min_valid_points_core=3,
        min_valid_points_full=5,
    )
    assert metrics[0]["tier"] == "Core"


def test_compute_surface_metrics_requires_core_membership_even_if_count_met():
    ts = datetime(2026, 2, 13)
    points = [
        IvPoint(date(2026, 3, 15), "ATM", 0.2, 0.19, 0.21, "ok", 1.0),
        IvPoint(date(2026, 3, 15), "+0.25C", 0.21, 0.2, 0.22, "ok", 1.0),
        IvPoint(date(2026, 3, 15), "+0.10C", 0.23, 0.22, 0.24, "ok", 1.0),
        IvPoint(date(2026, 3, 15), "-0.10P", 0.24, 0.23, 0.25, "ok", 1.0),
        IvPoint(date(2026, 3, 15), "-0.40P", 0.26, 0.25, 0.27, "ok", 1.0),
    ]
    metrics = compute_surface_metrics(
        points,
        ts,
        [30],
        min_valid_points_core=3,
        min_valid_points_full=5,
    )
    assert metrics[0]["tier"] is None


def test_delta_points_config_changes_selected_buckets(monkeypatch):
    ts = datetime(2026, 2, 13)
    quotes = pd.DataFrame(
        [
            {"expiry": "2026-03-15", "strike": 90.0, "option_right": "C", "bid": 1.0, "ask": 1.2},
            {"expiry": "2026-03-15", "strike": 100.0, "option_right": "C", "bid": 1.0, "ask": 1.2},
            {"expiry": "2026-03-15", "strike": 110.0, "option_right": "C", "bid": 1.0, "ask": 1.2},
            {"expiry": "2026-03-15", "strike": 90.0, "option_right": "P", "bid": 1.0, "ask": 1.2},
            {"expiry": "2026-03-15", "strike": 100.0, "option_right": "P", "bid": 1.0, "ask": 1.2},
            {"expiry": "2026-03-15", "strike": 110.0, "option_right": "P", "bid": 1.0, "ask": 1.2},
        ]
    )

    class _IvResult:
        def __init__(self, iv: float):
            self.iv = iv

    def fake_solve_iv(*_args, **_kwargs):
        return _IvResult(0.2)

    def fake_bs_delta(spot, strike, rate, div, t_years, iv, right):
        if right == "C":
            return {90.0: 0.25, 100.0: 0.50, 110.0: 0.10}[float(strike)]
        return {90.0: -0.25, 100.0: -0.50, 110.0: -0.10}[float(strike)]

    monkeypatch.setattr("src.core.metrics.solve_iv", fake_solve_iv)
    monkeypatch.setattr("src.core.metrics.bs_delta", fake_bs_delta)

    from src.core.metrics import compute_iv_points

    points_10 = compute_iv_points(
        quotes,
        ts,
        100.0,
        spread_gate_pct=0.5,
        delta_points=[0.10],
    )
    buckets_10 = {p.delta_bucket for p in points_10}
    assert "+0.10C" in buckets_10
    assert "-0.10P" in buckets_10
    assert "+0.25C" not in buckets_10
    assert "-0.25P" not in buckets_10
    assert all(p.solve_status == "ok" for p in points_10)

    points_25 = compute_iv_points(
        quotes,
        ts,
        100.0,
        spread_gate_pct=0.5,
        delta_points=[0.25],
    )
    buckets_25 = {p.delta_bucket for p in points_25}
    assert "+0.25C" in buckets_25
    assert "-0.25P" in buckets_25
    assert "+0.10C" not in buckets_25
    assert "-0.10P" not in buckets_25
    assert all(p.solve_status == "ok" for p in points_25)
