from __future__ import annotations

import sys
from pathlib import Path

repo_root = Path(__file__).resolve().parents[1]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from src.core.bootstrap import ensure_repo_root_on_path

ensure_repo_root_on_path()

import logging

from src.core.logging_utils import setup_logging
from src.db.init_db import init_db
from src.db.connection import connect
from src.ingest.ingest_yfinance import run_ingest
from src.core.compute_snapshot import compute_for_snapshot
from src.core.regime import compute_regime_state


def _latest_snapshot_id() -> int | None:
    conn = connect()
    try:
        row = conn.execute("SELECT MAX(snapshot_id) FROM snapshots").fetchone()
        return int(row[0]) if row and row[0] is not None else None
    finally:
        conn.close()


def run_pipeline() -> None:
    setup_logging()
    logger = logging.getLogger("pipeline")
    logger.info("starting pipeline")
    init_db()
    logger.info("database initialized")
    run_ingest()
    logger.info("ingest complete")
    compute_regime_state()
    logger.info("regime computed")
    snapshot_id = _latest_snapshot_id()
    if snapshot_id is None:
        raise RuntimeError("No snapshot found after ingestion")
    logger.info("computing metrics for snapshot_id=%s", snapshot_id)
    compute_for_snapshot(snapshot_id)
    logger.info("pipeline complete")


if __name__ == "__main__":
    run_pipeline()
