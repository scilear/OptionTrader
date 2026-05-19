import pandas as pd

from src.core.alerts import compute_alerts
from src.core.compute_snapshot import _resolve_regime_override_threshold


def test_pessimistic_gate_blocks():
    data = pd.DataFrame(
        {
            "ts": pd.date_range("2026-01-01", periods=6, freq="D"),
            "expiry_bucket": ["30D"] * 6,
            "rr25_mid": [0.0, 0.0, 0.0, 0.0, 0.0, 3.0],
            "rr25_worst": [0.0, 1.0, 0.0, 1.0, 0.0, 1.0],
        }
    )
    alerts = compute_alerts(data, window=6, threshold=2.0, persistence_required=1)
    assert len(alerts) == 0


def test_persistence_required():
    data = pd.DataFrame(
        {
            "ts": pd.date_range("2026-01-01", periods=3, freq="D"),
            "expiry_bucket": ["30D"] * 3,
            "rr25_mid": [0.0, 0.0, 3.0],
            "rr25_worst": [0.0, 0.0, 3.0],
        }
    )
    alerts = compute_alerts(data, window=3, threshold=2.0, persistence_required=2)
    assert len(alerts) == 0


def test_alert_emits_when_signal_and_persistence_pass():
    data = pd.DataFrame(
        {
            "ts": pd.date_range("2026-01-01", periods=5, freq="D"),
            "expiry_bucket": ["30D"] * 5,
            "rr25_mid": [0.0, 0.0, 3.0, 3.1, 3.2],
            "rr25_worst": [0.0, 0.0, 3.0, 3.1, 3.2],
        }
    )
    alerts = compute_alerts(data, window=5, threshold=0.25, persistence_required=2)
    assert len(alerts) == 1
    assert alerts[0]["alert_type"] == "RR_EXTREME"
    assert alerts[0]["score_method_mid"] in {"mad", "iqr", "std"}
    assert alerts[0]["score_method_worst"] in {"mad", "iqr", "std"}
    assert alerts[0]["evidence_overlap"]["detected"] is False


def test_pessimistic_gate_toggle_allows_mid_only_signal_when_disabled():
    data = pd.DataFrame(
        {
            "ts": pd.date_range("2026-01-01", periods=6, freq="D"),
            "expiry_bucket": ["30D"] * 6,
            "rr25_mid": [0.0, 0.0, 0.0, 0.0, 0.0, 3.0],
            "rr25_worst": [0.0, 1.0, 0.0, 1.0, 0.0, 1.0],
        }
    )
    alerts = compute_alerts(
        data,
        window=6,
        threshold=2.0,
        persistence_required=1,
        pessimistic_gate=False,
    )
    assert len(alerts) == 1
    assert alerts[0]["alert_type"] == "RR_EXTREME"


def test_sparse_and_flat_series_emit_no_alert():
    sparse = pd.DataFrame(
        {
            "ts": pd.date_range("2026-01-01", periods=2, freq="D"),
            "expiry_bucket": ["30D"] * 2,
            "rr25_mid": [0.0, 3.0],
            "rr25_worst": [0.0, 3.0],
        }
    )
    flat = pd.DataFrame(
        {
            "ts": pd.date_range("2026-01-01", periods=6, freq="D"),
            "expiry_bucket": ["30D"] * 6,
            "rr25_mid": [1.0] * 6,
            "rr25_worst": [1.0] * 6,
        }
    )

    sparse_alerts = compute_alerts(
        sparse,
        window=6,
        threshold=2.0,
        persistence_required=1,
    )
    flat_alerts = compute_alerts(
        flat,
        window=6,
        threshold=2.0,
        persistence_required=1,
    )

    assert sparse_alerts == []
    assert flat_alerts == []


def test_overlap_guardrail_keeps_only_dominant_signal():
    data = pd.DataFrame(
        {
            "ts": pd.date_range("2026-01-01", periods=6, freq="D"),
            "expiry_bucket": ["30D"] * 6,
            "rr25_mid": [0.0, 0.0, 0.0, 2.0, 2.1, 2.2],
            "rr25_worst": [0.0, 0.0, 0.0, 2.0, 2.1, 2.2],
            "fly25_mid": [0.0, 0.0, 0.0, 1.7, 1.8, 1.9],
            "fly25_worst": [0.0, 0.0, 0.0, 1.7, 1.8, 1.9],
        }
    )
    alerts = compute_alerts(
        data,
        window=6,
        threshold=0.50,
        persistence_required=1,
    )

    assert len(alerts) == 1
    assert alerts[0]["alert_type"] in {"RR_EXTREME", "FLY_EXTREME"}
    overlap = alerts[0]["evidence_overlap"]
    assert overlap["detected"] is True
    assert overlap["candidate_count"] == 2
    assert set(overlap["suppressed_alert_types"]) == {"RR_EXTREME", "FLY_EXTREME"} - {
        alerts[0]["alert_type"]
    }
    assert alerts[0]["effective_severity"] < abs(alerts[0]["zscore_mid"])


def test_overlap_guardrail_does_not_merge_opposing_signals():
    data = pd.DataFrame(
        {
            "ts": pd.date_range("2026-01-01", periods=6, freq="D"),
            "expiry_bucket": ["30D"] * 6,
            "rr25_mid": [0.0, 0.0, 0.0, 2.0, 2.1, 2.2],
            "rr25_worst": [0.0, 0.0, 0.0, 2.0, 2.1, 2.2],
            "fly25_mid": [0.0, 0.0, 0.0, -1.7, -1.8, -1.9],
            "fly25_worst": [0.0, 0.0, 0.0, -1.7, -1.8, -1.9],
        }
    )
    alerts = compute_alerts(
        data,
        window=6,
        threshold=0.50,
        persistence_required=1,
    )

    assert len(alerts) == 2
    assert {alert["alert_type"] for alert in alerts} == {"RR_EXTREME", "FLY_EXTREME"}
    assert all(alert["evidence_overlap"]["detected"] is False for alert in alerts)


def test_regime_override_threshold_lookup() -> None:
    config = {
        "alerts": {
            "regime_overrides": {
                "Transition": {"RR_EXTREME": {"min_abs_zscore": 6.0}},
                "Calm": {"RR_EXTREME": {"min_abs_zscore": 5.0}},
                "Stress": {"RR_EXTREME": {"min_abs_zscore": 5.0}},
            }
        }
    }

    assert _resolve_regime_override_threshold(config, "Transition", "RR_EXTREME") == 6.0
    assert _resolve_regime_override_threshold(config, "Calm", "RR_EXTREME") == 5.0
    assert _resolve_regime_override_threshold(config, "Stress", "RR_EXTREME") == 5.0
    assert _resolve_regime_override_threshold(config, "Transition", "FLY_EXTREME") is None
    assert _resolve_regime_override_threshold(config, "Unknown", "RR_EXTREME") is None
