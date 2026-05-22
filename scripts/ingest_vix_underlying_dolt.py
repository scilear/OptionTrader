from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
import sys

repo_root = Path(__file__).resolve().parents[1]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from src.core.bootstrap import ensure_repo_root_on_path

ensure_repo_root_on_path()

import pandas as pd

from src.strategy_sim.data_contracts import ensure_strategy_tables


def _load_csv(path: Path, required_columns: set[str]) -> pd.DataFrame:
    frame = pd.read_csv(path)
    missing = required_columns - set(frame.columns)
    if missing:
        raise ValueError(f"{path} missing columns: {', '.join(sorted(missing))}")
    return frame


from src.strategy_sim.dolt import execute_dolt_statement


def _sql_value(value: object) -> str:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return "NULL"
    if isinstance(value, (int, float)):
        return str(value)
    text = str(value).replace("'", "''")
    return f"'{text}'"


def _replace_table_rows(
    repo_path: str,
    table_name: str,
    columns: list[str],
    frame: pd.DataFrame,
    chunk_size: int = 500,
) -> int:
    execute_dolt_statement(repo_path, f"DELETE FROM {table_name}")
    rows = frame[columns].to_dict(orient="records")
    inserted = 0
    for start in range(0, len(rows), chunk_size):
        chunk = rows[start : start + chunk_size]
        values_sql = ",\n".join(
            "(" + ", ".join(_sql_value(row[column]) for column in columns) + ")"
            for row in chunk
        )
        statement = (
            f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES\n"
            f"{values_sql}"
        )
        execute_dolt_statement(repo_path, statement)
        inserted += len(chunk)
    return inserted


def main() -> None:
    parser = argparse.ArgumentParser(description="Idempotent VIX and underlying ingestion into Dolt")
    parser.add_argument("--repo-path", default="/mnt/Data/dolt_data/options")
    parser.add_argument("--vix-csv", required=True)
    parser.add_argument("--underlying-csv", required=True)
    parser.add_argument("--source", default="csv_import")
    args = parser.parse_args()

    ensure_strategy_tables(args.repo_path)
    vix_frame = _load_csv(Path(args.vix_csv), {"date", "close"})
    under_frame = _load_csv(Path(args.underlying_csv), {"date", "act_symbol", "close"})

    ingested_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    vix_frame = vix_frame.copy()
    vix_frame["date"] = pd.to_datetime(vix_frame["date"]).dt.date.astype(str)
    vix_frame["close"] = vix_frame["close"].astype(float)
    vix_frame["source"] = args.source
    vix_frame["ingested_at"] = ingested_at
    vix_frame = vix_frame[["date", "close", "source", "ingested_at"]]

    under_frame = under_frame.copy()
    under_frame["date"] = pd.to_datetime(under_frame["date"]).dt.date.astype(str)
    under_frame["act_symbol"] = under_frame["act_symbol"].astype(str).str.upper()
    under_frame["close"] = under_frame["close"].astype(float)
    under_frame["source"] = args.source
    under_frame["ingested_at"] = ingested_at
    under_frame = under_frame[["date", "act_symbol", "close", "source", "ingested_at"]]

    vix_count = _replace_table_rows(
        repo_path=args.repo_path,
        table_name="vix_daily",
        columns=["date", "close", "source", "ingested_at"],
        frame=vix_frame,
    )
    under_count = _replace_table_rows(
        repo_path=args.repo_path,
        table_name="underlying_prices_daily",
        columns=["date", "act_symbol", "close", "source", "ingested_at"],
        frame=under_frame,
    )
    print(
        {
            "repo_path": args.repo_path,
            "vix_rows_upserted": vix_count,
            "underlying_rows_upserted": under_count,
        }
    )


if __name__ == "__main__":
    main()
