from __future__ import annotations

from datetime import date

import pandas as pd

from src.core.surface_fit import fit_surface_for_expiry


def test_fit_surface_interpolates_bucket_from_bracket() -> None:
    rows = pd.DataFrame(
        [
            {
                "expiry": date(2026, 3, 15),
                "strike": 100.0,
                "right": "C",
                "iv_mid": 0.20,
                "iv_bid": 0.19,
                "iv_ask": 0.21,
                "delta": 0.35,
                "quality": 1.0,
            },
            {
                "expiry": date(2026, 3, 15),
                "strike": 105.0,
                "right": "C",
                "iv_mid": 0.30,
                "iv_bid": 0.29,
                "iv_ask": 0.31,
                "delta": 0.15,
                "quality": 1.0,
            },
            {
                "expiry": date(2026, 3, 15),
                "strike": 100.0,
                "right": "P",
                "iv_mid": 0.22,
                "iv_bid": 0.21,
                "iv_ask": 0.23,
                "delta": -0.35,
                "quality": 1.0,
            },
            {
                "expiry": date(2026, 3, 15),
                "strike": 95.0,
                "right": "P",
                "iv_mid": 0.26,
                "iv_bid": 0.25,
                "iv_ask": 0.27,
                "delta": -0.15,
                "quality": 1.0,
            },
        ]
    )

    points = fit_surface_for_expiry(
        rows=rows,
        expiry=date(2026, 3, 15),
        spot=100.0,
        rate=0.0,
        div=0.0,
        t_years=30 / 365,
        delta_points=[0.25],
    )
    points_by_bucket = {p.delta_bucket: p for p in points}

    assert points_by_bucket["+0.25C"].solve_status == "ok"
    assert abs(points_by_bucket["+0.25C"].iv_mid - 0.25) < 1e-9
    assert points_by_bucket["+0.25C"].fit_model_id == "linear_delta_v1"


def test_fit_surface_marks_degraded_on_sparse_support() -> None:
    rows = pd.DataFrame(
        [
            {
                "expiry": date(2026, 3, 15),
                "strike": 100.0,
                "right": "C",
                "iv_mid": 0.20,
                "iv_bid": 0.19,
                "iv_ask": 0.21,
                "delta": 0.50,
                "quality": 1.0,
            },
            {
                "expiry": date(2026, 3, 15),
                "strike": 100.0,
                "right": "P",
                "iv_mid": 0.22,
                "iv_bid": 0.21,
                "iv_ask": 0.23,
                "delta": -0.50,
                "quality": 1.0,
            },
        ]
    )

    points = fit_surface_for_expiry(
        rows=rows,
        expiry=date(2026, 3, 15),
        spot=100.0,
        rate=0.0,
        div=0.0,
        t_years=30 / 365,
        delta_points=[0.25],
    )
    points_by_bucket = {p.delta_bucket: p for p in points}

    assert points_by_bucket["+0.25C"].solve_status == "degraded"
    assert "insufficient_support" in points_by_bucket["+0.25C"].reason_codes
    assert points_by_bucket["-0.25P"].solve_status == "degraded"
