from __future__ import annotations

import logging
from datetime import datetime

from src.db.connection import connect
from src.core.compute_snapshot import compute_for_snapshot


def replay_snapshots(limit: int = 20) -> int:
    logger = logging.getLogger("replay")
    conn = connect()
    try:
        rows = conn.execute(
            "SELECT snapshot_id FROM snapshots ORDER BY ts DESC LIMIT ?",
            (limit,),
        ).fetchall()
        snapshot_ids = [r[0] for r in rows][::-1]
    finally:
        conn.close()

    if not snapshot_ids:
        logger.info("no snapshots to replay")
        return 0

    logger.info("replaying %s snapshots", len(snapshot_ids))
    for snapshot_id in snapshot_ids:
        compute_for_snapshot(snapshot_id, purge_existing=True)
    logger.info("replay complete")
    return len(snapshot_ids)
