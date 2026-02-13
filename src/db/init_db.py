from __future__ import annotations

from pathlib import Path

import sys
from pathlib import Path

repo_root = Path(__file__).resolve().parents[2]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

import os

from src.core.bootstrap import ensure_repo_root_on_path

ensure_repo_root_on_path()

from src.db.connection import connect


def init_db(schema_path: Path | None = None) -> None:
    path = schema_path or Path("src/db/schema.sql")
    sql = path.read_text()
    conn = connect()
    try:
        if os.getenv("OPTIONTRADER_RESET_DB") == "1":
            conn.execute("DROP TABLE IF EXISTS trade_ideas")
            conn.execute("DROP TABLE IF EXISTS alerts")
            conn.execute("DROP TABLE IF EXISTS surface_metrics")
            conn.execute("DROP TABLE IF EXISTS iv_points")
            conn.execute("DROP TABLE IF EXISTS option_quotes")
            conn.execute("DROP TABLE IF EXISTS regime_state")
            conn.execute("DROP TABLE IF EXISTS snapshots")
        conn.execute(sql)
    finally:
        conn.close()


if __name__ == "__main__":
    init_db()
