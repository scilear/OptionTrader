"""Ingest tracking for resumable EOD processing."""

from pathlib import Path
from datetime import datetime
from typing import Set

from src.db.connection import connect


def init_ingest_tracking_table() -> None:
    conn = connect()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS ingest_tracking (
                file_path TEXT PRIMARY KEY,
                glob_pattern TEXT NOT NULL,
                underlying TEXT NOT NULL,
                processed_at TIMESTAMP NOT NULL,
                file_size_bytes INTEGER,
                row_count INTEGER
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


def load_processed_files(
    glob_pattern: str,
    underlying: str,
) -> Set[Path]:
    conn = connect()
    try:
        rows = conn.execute(
            """
            SELECT file_path FROM ingest_tracking
            WHERE glob_pattern = ? AND underlying = ?
            """,
            (glob_pattern, underlying),
        ).fetchall()
        return {Path(row[0]) for row in rows}
    finally:
        conn.close()


def mark_file_complete(
    file_path: Path,
    glob_pattern: str,
    underlying: str,
    file_size_bytes: int,
    row_count: int,
) -> None:
    conn = connect()
    try:
        conn.execute(
            """
            INSERT OR REPLACE INTO ingest_tracking
            (file_path, glob_pattern, underlying, processed_at, file_size_bytes, row_count)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                str(file_path),
                glob_pattern,
                underlying,
                datetime.now(),
                file_size_bytes,
                row_count,
            ),
        )
        conn.commit()
    finally:
        conn.close()