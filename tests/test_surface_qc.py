from __future__ import annotations

from datetime import date

from src.core.metrics import IvPoint
from src.core.surface_qc import evaluate_surface_qc


def test_surface_qc_detects_vertical_and_calendar_violations() -> None:
    metrics = [
        {
            "expiry_bucket": "21D",
            "atm_iv_mid": 0.20,
            "rr25_mid": 0.20,
            "rr10_mid": 0.10,
            "fly25_mid": -0.01,
            "fly10_mid": -0.02,
        },
        {
            "expiry_bucket": "45D",
            "atm_iv_mid": 0.10,
            "rr25_mid": 0.10,
            "rr10_mid": 0.12,
            "fly25_mid": 0.01,
            "fly10_mid": 0.01,
        },
    ]
    points = [
        IvPoint(
            expiry=date(2026, 3, 15),
            delta_bucket="+0.25C",
            iv_mid=0.20,
            iv_bid=0.19,
            iv_ask=0.21,
            solve_status="ok",
            quality_score=1.0,
            fit_confidence=0.9,
        )
    ]

    result = evaluate_surface_qc(metrics, points, no_arb_epsilon=0.0)
    assert not result.passed
    assert "vertical_rr_magnitude_inversion" in result.reason_codes
    assert "vertical_negative_fly25" in result.reason_codes
    assert any(code.startswith("calendar_total_variance_violation") for code in result.reason_codes)


def test_surface_qc_allows_normal_contango_when_total_variance_is_monotone() -> None:
    metrics = [
        {"expiry_bucket": "21D", "atm_iv_mid": 0.20, "rr25_mid": 0.05, "rr10_mid": 0.10, "fly25_mid": 0.01, "fly10_mid": 0.01},
        {"expiry_bucket": "45D", "atm_iv_mid": 0.24, "rr25_mid": 0.05, "rr10_mid": 0.10, "fly25_mid": 0.01, "fly10_mid": 0.01},
    ]
    points = [
        IvPoint(
            expiry=date(2026, 3, 15),
            delta_bucket="ATM",
            iv_mid=0.20,
            iv_bid=0.19,
            iv_ask=0.21,
            solve_status="ok",
            quality_score=1.0,
            fit_confidence=0.9,
        )
    ]

    result = evaluate_surface_qc(metrics, points, no_arb_epsilon=0.0)
    assert result.passed
    assert result.reason_codes == ()


def test_surface_qc_blocks_degraded_surface() -> None:
    metrics = [{"expiry_bucket": "30D", "atm_iv_mid": 0.20, "rr25_mid": 0.05, "rr10_mid": 0.10, "fly25_mid": 0.01, "fly10_mid": 0.01}]
    points = [
        IvPoint(
            expiry=date(2026, 3, 15),
            delta_bucket="+0.25C",
            iv_mid=0.20,
            iv_bid=0.19,
            iv_ask=0.21,
            solve_status="degraded",
            quality_score=1.0,
            fit_confidence=0.2,
        )
    ]

    result = evaluate_surface_qc(metrics, points, no_arb_epsilon=0.005)
    assert not result.passed
    assert "degraded_surface_fit" in result.reason_codes


def test_surface_qc_uses_configured_epsilon() -> None:
    metrics = [{"expiry_bucket": "30D", "atm_iv_mid": 0.20, "rr25_mid": 0.11, "rr10_mid": 0.10, "fly25_mid": 0.001, "fly10_mid": 0.001}]
    points = [
        IvPoint(
            expiry=date(2026, 3, 15),
            delta_bucket="ATM",
            iv_mid=0.20,
            iv_bid=0.19,
            iv_ask=0.21,
            solve_status="ok",
            quality_score=1.0,
            fit_confidence=0.9,
        )
    ]

    strict = evaluate_surface_qc(metrics, points, no_arb_epsilon=0.0)
    tolerant = evaluate_surface_qc(metrics, points, no_arb_epsilon=0.02)

    assert not strict.passed
    assert strict.reason_codes == ("vertical_rr_magnitude_inversion",)
    assert tolerant.passed


def test_surface_qc_supports_split_epsilons_by_domain() -> None:
    metrics = [
        {
            "expiry_bucket": "21D",
            "atm_iv_mid": 0.30,
            "rr25_mid": 0.20,
            "rr10_mid": 0.10,
            "fly25_mid": 0.01,
            "fly10_mid": 0.01,
        },
        {
            "expiry_bucket": "45D",
            "atm_iv_mid": 0.20,
            "rr25_mid": 0.10,
            "rr10_mid": 0.10,
            "fly25_mid": 0.01,
            "fly10_mid": 0.01,
        },
    ]
    points = [
        IvPoint(
            expiry=date(2026, 3, 15),
            delta_bucket="ATM",
            iv_mid=0.20,
            iv_bid=0.19,
            iv_ask=0.21,
            solve_status="ok",
            quality_score=1.0,
            fit_confidence=0.9,
        )
    ]

    result = evaluate_surface_qc(
        metrics,
        points,
        no_arb_epsilon=0.005,
        iv_epsilon=0.2,
        var_epsilon=0.0,
    )
    assert not result.passed
    assert result.reason_codes == ("calendar_total_variance_violation:21D->45D",)
