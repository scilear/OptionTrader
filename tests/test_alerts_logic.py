import pandas as pd

from src.core.alerts import compute_alerts


def test_pessimistic_gate_blocks():
    data = pd.DataFrame(
        {
            "ts": pd.date_range("2026-01-01", periods=5, freq="D"),
            "expiry_bucket": ["30D"] * 5,
            "rr25_mid": [0.0, 0.0, 0.0, 0.0, 3.0],
            "rr25_worst": [0.0, 0.0, 0.0, 0.0, 0.1],
        }
    )
    alerts = compute_alerts(data, window=5, threshold=2.0, persistence_required=1)
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
