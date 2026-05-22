from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path
import sys

repo_root = Path(__file__).resolve().parents[1]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from src.core.bootstrap import ensure_repo_root_on_path

ensure_repo_root_on_path()

from src.strategy_sim.config import load_simulation_config
from src.strategy_sim.engine import run_simulation


def main() -> None:
    parser = argparse.ArgumentParser(description="Run short straddle + put spread simulation")
    parser.add_argument("--config", default="config/shortstraddle_sim.yaml")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
    config, raw, digest = load_simulation_config(args.config)
    result = run_simulation(config=config, raw_config=raw, config_digest=digest)
    payload = {
        "run_id": result.run_id,
        "output_dir": str(result.output_dir),
        "trade_count": result.trade_count,
        "daily_rows": result.daily_rows,
    }
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
