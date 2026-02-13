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


@dataclass
class LatestSnapshotSummary:
    snapshot_id: int | None
    ts: str | None
    alert_count: int


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


def latest_snapshot_summary() -> LatestSnapshotSummary:
    conn = connect()
    try:
        row = conn.execute(
            "SELECT snapshot_id, ts FROM snapshots ORDER BY ts DESC LIMIT 1"
        ).fetchone()
        if not row:
            return LatestSnapshotSummary(snapshot_id=None, ts=None, alert_count=0)

        snapshot_id, ts = row[0], row[1]
        alert_count = conn.execute(
            "SELECT COUNT(*) FROM alerts WHERE snapshot_id = ?",
            (snapshot_id,),
        ).fetchone()[0]
    finally:
        conn.close()

    return LatestSnapshotSummary(
        snapshot_id=int(snapshot_id),
        ts=str(ts),
        alert_count=int(alert_count or 0),
    )
