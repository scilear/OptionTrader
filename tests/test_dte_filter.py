from datetime import datetime, date

import pandas as pd

from src.core.metrics import filter_quotes_by_dte


def test_filter_quotes_by_dte():
    snapshot_ts = datetime(2026, 2, 13)
    quotes = pd.DataFrame(
        {
            "expiry": [date(2026, 2, 27), date(2026, 3, 28), date(2026, 6, 1)],
            "strike": [100, 100, 100],
            "option_right": ["C", "C", "C"],
            "bid": [1.0, 1.0, 1.0],
            "ask": [1.2, 1.2, 1.2],
        }
    )

    filtered = filter_quotes_by_dte(quotes, snapshot_ts, dte_min=14, dte_max=60)
    assert len(filtered) == 2
