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
