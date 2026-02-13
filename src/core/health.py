from __future__ import annotations

from dataclasses import dataclass

from src.db.connection import connect


@dataclass
class HealthSummary:
    snapshots: int
    quotes: int
    iv_points: int
    metrics: int
    alerts: int


def compute_health_summary() -> HealthSummary:
    conn = connect()
    try:
        snapshots = conn.execute("SELECT COUNT(*) FROM snapshots").fetchone()[0]
        quotes = conn.execute("SELECT COUNT(*) FROM option_quotes").fetchone()[0]
        iv_points = conn.execute("SELECT COUNT(*) FROM iv_points").fetchone()[0]
        metrics = conn.execute("SELECT COUNT(*) FROM surface_metrics").fetchone()[0]
        alerts = conn.execute("SELECT COUNT(*) FROM alerts").fetchone()[0]
    finally:
        conn.close()

    return HealthSummary(
        snapshots=int(snapshots or 0),
        quotes=int(quotes or 0),
        iv_points=int(iv_points or 0),
        metrics=int(metrics or 0),
        alerts=int(alerts or 0),
    )
