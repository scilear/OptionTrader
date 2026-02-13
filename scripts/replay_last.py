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
from src.core.replay import replay_snapshots


def main() -> None:
    setup_logging()
    logger = logging.getLogger("replay")
    count = replay_snapshots(limit=20)
    logger.info("replayed_count=%s", count)


if __name__ == "__main__":
    main()
