from __future__ import annotations

import sys
from pathlib import Path

repo_root = Path(__file__).resolve().parents[1]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from src.core.bootstrap import ensure_repo_root_on_path

ensure_repo_root_on_path()

from src.db.init_db import init_db
from src.db.connection import connect
from src.ingest.ingest_yfinance import run_ingest
from src.core.compute_snapshot import compute_for_snapshot


def _latest_snapshot_id() -> int | None:
    conn = connect()
    try:
        row = conn.execute("SELECT MAX(snapshot_id) FROM snapshots").fetchone()
        return int(row[0]) if row and row[0] is not None else None
    finally:
        conn.close()


def run_pipeline() -> None:
    init_db()
    run_ingest()
    snapshot_id = _latest_snapshot_id()
    if snapshot_id is None:
        raise RuntimeError("No snapshot found after ingestion")
    compute_for_snapshot(snapshot_id)


if __name__ == "__main__":
    run_pipeline()
