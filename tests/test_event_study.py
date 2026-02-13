import pandas as pd

from src.core.event_study import compute_event_study, compute_event_study_by_regime


def test_event_study_empty():
    stats = compute_event_study(pd.DataFrame(columns=["ts", "rr25_mid"]), "rr25_mid", 2.0)
    assert stats.events == 0


def test_event_study_detects_events():
    data = pd.DataFrame(
        {
            "ts": pd.date_range("2026-01-01", periods=80, freq="D"),
            "rr25_mid": [0.0] * 60 + [3.0] * 20,
        }
    )
    stats = compute_event_study(data, "rr25_mid", 2.0, max_days=10)
    assert stats.events >= 1


def test_event_study_by_regime():
    data = pd.DataFrame(
        {
            "ts": pd.date_range("2026-01-01", periods=80, freq="D"),
            "rr25_mid": [0.0] * 60 + [3.0] * 20,
        }
    )
    regime = pd.DataFrame(
        {
            "regime_date": pd.date_range("2026-01-01", periods=80, freq="D"),
            "regime_label": ["Calm"] * 80,
        }
    )
    result = compute_event_study_by_regime(data, "rr25_mid", 2.0, regime)
    assert not result.empty
