from __future__ import annotations

import sys
from pathlib import Path

repo_root = Path(__file__).resolve().parents[1]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from src.core.bootstrap import ensure_repo_root_on_path

ensure_repo_root_on_path()

from datetime import datetime, timezone
import logging
import subprocess

from src.core.config import load_config_with_digest
from src.core.logging_utils import setup_logging
from src.db.connection import connect
from src.core.compute_snapshot import compute_for_snapshot
from src.core.regime import compute_regime_state
from src.db.init_db import init_db
from src.ingest.dispatcher import run_ingest


def _latest_snapshot_id(run_id: int) -> int | None:
    conn = connect()
    try:
        row = conn.execute(
            "SELECT MAX(snapshot_id) FROM snapshots WHERE run_id = ?",
            (run_id,),
        ).fetchone()
        return int(row[0]) if row and row[0] is not None else None
    finally:
        conn.close()


def _resolve_code_version() -> str:
    try:
        sha = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repo_root,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        if not sha:
            return "unknown"
        dirty = subprocess.run(
            ["git", "status", "--porcelain", "--untracked-files=no"],
            cwd=repo_root,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        return f"{sha}-dirty" if dirty else sha
    except Exception:
        return "unknown"


def _create_pipeline_run(config_hash: str, code_version: str) -> int:
    conn = connect()
    try:
        started_at = datetime.now(timezone.utc)
        row = conn.execute(
            """
            INSERT INTO pipeline_runs (
                run_id, started_at, finished_at, status, config_hash, code_version, error_message
            ) VALUES (DEFAULT, ?, NULL, ?, ?, ?, NULL)
            RETURNING run_id
            """,
            (started_at, "started", config_hash, code_version),
        ).fetchone()
        if not row:
            raise RuntimeError("Failed to create pipeline run")
        return int(row[0])
    finally:
        conn.close()


def _finish_pipeline_run(run_id: int, status: str, error_message: str | None = None) -> None:
    conn = connect()
    try:
        finished_at = datetime.now(timezone.utc)
        conn.execute(
            """
            UPDATE pipeline_runs
            SET finished_at = ?, status = ?, error_message = ?
            WHERE run_id = ?
            """,
            (finished_at, status, error_message, run_id),
        )
    finally:
        conn.close()


def run_pipeline() -> None:
    setup_logging()
    logger = logging.getLogger("pipeline")
    logger.info("starting pipeline")
    init_db()
    logger.info("database initialized")
    _, digest = load_config_with_digest()
    code_version = _resolve_code_version()
    run_id = _create_pipeline_run(config_hash=digest, code_version=code_version)
    logger.info("created pipeline run_id=%s", run_id)
    error_message: str | None = None
    status = "success"
    try:
        run_ingest(run_id=run_id)
        logger.info("ingest complete")
        compute_regime_state()
        logger.info("regime computed")
        snapshot_id = _latest_snapshot_id(run_id)
        if snapshot_id is None:
            raise RuntimeError(f"No snapshot found after ingestion for run_id={run_id}")
        logger.info("computing metrics for snapshot_id=%s run_id=%s", snapshot_id, run_id)
        compute_for_snapshot(snapshot_id)
        logger.info("pipeline complete")
    except Exception as exc:
        status = "failed"
        error_message = str(exc) or exc.__class__.__name__
        raise
    finally:
        _finish_pipeline_run(run_id, status=status, error_message=error_message)


if __name__ == "__main__":
    run_pipeline()
