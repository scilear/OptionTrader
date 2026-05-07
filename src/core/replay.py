from __future__ import annotations

from dataclasses import dataclass
import logging
from datetime import datetime

from src.db.connection import connect
from src.core.compute_snapshot import compute_for_snapshot


@dataclass(frozen=True)
class WalkForwardSplit:
    split_id: int
    train_snapshot_ids: tuple[int, ...]
    test_snapshot_ids: tuple[int, ...]
    train_start_ts: datetime
    train_end_ts: datetime
    test_start_ts: datetime
    test_end_ts: datetime


def build_walk_forward_splits(
    snapshots: list[tuple[int, datetime]],
    train_size: int,
    test_size: int,
    step_size: int | None = None,
) -> list[WalkForwardSplit]:
    """Build deterministic walk-forward splits from ordered snapshot rows."""
    if train_size <= 0:
        raise ValueError("train_size must be > 0")
    if test_size <= 0:
        raise ValueError("test_size must be > 0")

    resolved_step = step_size if step_size is not None else test_size
    if resolved_step <= 0:
        raise ValueError("step_size must be > 0")

    splits: list[WalkForwardSplit] = []
    cursor = 0
    split_id = 1
    total = len(snapshots)
    while (cursor + train_size + test_size) <= total:
        train_rows = snapshots[cursor : cursor + train_size]
        test_rows = snapshots[cursor + train_size : cursor + train_size + test_size]
        if not train_rows or not test_rows:
            break
        splits.append(
            WalkForwardSplit(
                split_id=split_id,
                train_snapshot_ids=tuple(row[0] for row in train_rows),
                test_snapshot_ids=tuple(row[0] for row in test_rows),
                train_start_ts=train_rows[0][1],
                train_end_ts=train_rows[-1][1],
                test_start_ts=test_rows[0][1],
                test_end_ts=test_rows[-1][1],
            )
        )
        split_id += 1
        cursor += resolved_step
    return splits


def _fetch_ordered_snapshot_rows(
    *,
    underlying: str,
    start_ts: str,
    end_ts: str,
    lineage_prefix: str | None = None,
) -> list[tuple[int, datetime]]:
    conn = connect()
    try:
        if lineage_prefix:
            rows = conn.execute(
                """
                SELECT s.snapshot_id, s.ts
                FROM snapshots s
                JOIN pipeline_runs pr ON pr.run_id = s.run_id
                WHERE s.underlying = ?
                  AND s.ts >= ?
                  AND s.ts <= ?
                  AND pr.code_version LIKE ?
                ORDER BY s.ts, s.snapshot_id
                """,
                (underlying, start_ts, end_ts, f"{lineage_prefix}%"),
            ).fetchall()
        else:
            rows = conn.execute(
                """
                SELECT s.snapshot_id, s.ts
                FROM snapshots s
                WHERE s.underlying = ?
                  AND s.ts >= ?
                  AND s.ts <= ?
                ORDER BY s.ts, s.snapshot_id
                """,
                (underlying, start_ts, end_ts),
            ).fetchall()
    finally:
        conn.close()

    return [(int(snapshot_id), ts) for snapshot_id, ts in rows]


def replay_walk_forward(
    *,
    underlying: str,
    start_ts: str,
    end_ts: str,
    train_size: int,
    test_size: int,
    step_size: int | None = None,
    lineage_prefix: str | None = None,
    purge_existing: bool = True,
    execute_test_replay: bool = True,
) -> list[WalkForwardSplit]:
    """Replay test windows from deterministic walk-forward splits."""
    logger = logging.getLogger("replay")
    rows = _fetch_ordered_snapshot_rows(
        underlying=underlying,
        start_ts=start_ts,
        end_ts=end_ts,
        lineage_prefix=lineage_prefix,
    )
    splits = build_walk_forward_splits(
        rows,
        train_size=train_size,
        test_size=test_size,
        step_size=step_size,
    )
    logger.info("walk_forward_splits=%s", len(splits))
    if execute_test_replay:
        for split in splits:
            for snapshot_id in split.test_snapshot_ids:
                compute_for_snapshot(snapshot_id, purge_existing=purge_existing)
        logger.info("walk-forward replay complete")
    else:
        logger.info("walk-forward planning complete (no replay execution)")
    return splits


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
