import pandas as pd

from src.core.metrics import event_premium_series


def test_event_premium_series():
    df = pd.DataFrame(
        {
            "ts": pd.date_range("2026-01-01", periods=5, freq="D"),
            "atm_iv_mid": [0.2, 0.2, 0.21, 0.21, 0.2],
        }
    )
    series = event_premium_series(df)
    assert len(series) == 5
