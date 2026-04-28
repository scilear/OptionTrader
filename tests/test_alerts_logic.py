import pandas as pd

from src.core.alerts import compute_alerts


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
    alerts = compute_alerts(data, window=5, threshold=0.5, persistence_required=2)
    assert len(alerts) == 1
    assert alerts[0]["alert_type"] == "RR_EXTREME"


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
