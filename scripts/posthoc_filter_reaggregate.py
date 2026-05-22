from __future__ import annotations

import argparse
from pathlib import Path
import sys

repo_root = Path(__file__).resolve().parents[1]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from src.core.bootstrap import ensure_repo_root_on_path

ensure_repo_root_on_path()

from src.strategy_sim.posthoc import compute_kept_trade_ids, reaggregate_daily_pnl


def main() -> None:
    parser = argparse.ArgumentParser(description="Post-hoc filter + PnL reaggregation")
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--allow-vix-fail", action="store_true")
    parser.add_argument("--allow-liquidity-fail", action="store_true")
    parser.add_argument("--allow-data-fail", action="store_true")
    parser.add_argument("--allow-margin-fail", action="store_true")
    parser.add_argument("--output", default=None)
    args = parser.parse_args()

    run_dir = Path(args.run_dir)
    eligibility_csv = run_dir / "eligibility_timeseries.csv"
    trades_csv = run_dir / "trades_timeseries.csv"
    daily_csv = run_dir / "daily_pnl_timeseries.csv"

    kept_ids = compute_kept_trade_ids(
        eligibility_csv=eligibility_csv,
        trades_csv=trades_csv,
        require_vix_pass=not args.allow_vix_fail,
        require_liquidity_pass=not args.allow_liquidity_fail,
        require_data_pass=not args.allow_data_fail,
        require_margin_pass=not args.allow_margin_fail,
    )
    aggregated = reaggregate_daily_pnl(daily_pnl_csv=daily_csv, kept_trade_ids=kept_ids)
    output_path = Path(args.output) if args.output else run_dir / "posthoc_reaggregated_pnl.csv"
    aggregated.to_csv(output_path, index=False)
    print({"kept_trade_ids": len(kept_ids), "output": str(output_path)})


if __name__ == "__main__":
    main()
