from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

repo_root = Path(__file__).resolve().parents[1]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from src.core.bootstrap import ensure_repo_root_on_path

ensure_repo_root_on_path()

from src.strategy_sim.config import load_simulation_config
from src.strategy_sim.data_contracts import (
    build_data_quality_reports,
    ensure_strategy_tables,
    validate_data_contracts,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate strategy data contracts and write audits")
    parser.add_argument("--config", default="config/shortstraddle_sim.yaml")
    parser.add_argument("--output-dir", default="artifacts/data_quality")
    args = parser.parse_args()

    settings, _, _ = load_simulation_config(args.config)
    ensure_strategy_tables(settings.run.data_repo_path)
    validate_data_contracts(settings.run.data_repo_path)
    reports = build_data_quality_reports(
        repo_path=settings.run.data_repo_path,
        symbols=settings.run.symbols,
        start_date=settings.run.start_date,
        end_date=settings.run.end_date,
        target_dte=settings.straddle.target_dte,
        dte_tolerance=settings.straddle.dte_tolerance,
        output_dir=args.output_dir,
    )
    print(json.dumps({k: str(v) for k, v in reports.items()}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
