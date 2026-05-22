from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd

from src.strategy_sim.dolt import execute_dolt_statement, run_dolt_query


REQUIRED_TABLES = {
    "option_chain",
    "volatility_history",
    "vix_daily",
    "underlying_prices_daily",
}

REQUIRED_COLUMNS: dict[str, set[str]] = {
    "option_chain": {"date", "act_symbol", "expiration", "strike", "call_put", "bid", "ask", "delta"},
    "volatility_history": {"date", "act_symbol", "iv_current", "hv_current"},
    "vix_daily": {"date", "close"},
    "underlying_prices_daily": {"date", "act_symbol", "close"},
}


def ensure_strategy_tables(repo_path: str | Path) -> None:
    """Create strategy support tables if they do not already exist."""
    execute_dolt_statement(
        repo_path,
        """
        CREATE TABLE IF NOT EXISTS vix_daily (
            date DATE PRIMARY KEY,
            close DOUBLE NOT NULL,
            source VARCHAR(64) NOT NULL,
            ingested_at DATETIME
        )
        """,
    )
    execute_dolt_statement(
        repo_path,
        """
        CREATE TABLE IF NOT EXISTS underlying_prices_daily (
            date DATE,
            act_symbol VARCHAR(32),
            close DOUBLE NOT NULL,
            source VARCHAR(64) NOT NULL,
            ingested_at DATETIME,
            PRIMARY KEY (date, act_symbol)
        )
        """,
    )


def _table_names(repo_path: str | Path) -> set[str]:
    tables = run_dolt_query(repo_path, "SHOW TABLES")
    if tables.empty:
        return set()
    first_column = tables.columns[0]
    return {str(value) for value in tables[first_column].tolist()}


def _describe_columns(repo_path: str | Path, table_name: str) -> set[str]:
    description = run_dolt_query(repo_path, f"DESCRIBE {table_name}")
    if description.empty:
        return set()
    return {str(value) for value in description["Field"].tolist()}


def validate_data_contracts(repo_path: str | Path) -> None:
    """Fail fast when required strategy tables or columns are missing."""
    tables = _table_names(repo_path)
    missing_tables = sorted(REQUIRED_TABLES - tables)
    if missing_tables:
        raise ValueError(f"Missing required Dolt tables: {', '.join(missing_tables)}")

    missing_columns: list[str] = []
    for table_name, expected_columns in REQUIRED_COLUMNS.items():
        columns = _describe_columns(repo_path, table_name)
        diff = sorted(expected_columns - columns)
        missing_columns.extend([f"{table_name}.{column}" for column in diff])
    if missing_columns:
        raise ValueError("Missing required Dolt columns: " + ", ".join(missing_columns))


def build_data_quality_reports(
    repo_path: str | Path,
    symbols: tuple[str, ...],
    start_date: date,
    end_date: date,
    target_dte: int,
    dte_tolerance: int,
    output_dir: str | Path,
) -> dict[str, Path]:
    """Build coverage, null diagnostics, and DTE availability CSV reports."""
    symbols_sql = ", ".join(f"'{symbol}'" for symbol in symbols)
    start = start_date.isoformat()
    end = end_date.isoformat()

    coverage_option = run_dolt_query(
        repo_path,
        f"""
        SELECT
          act_symbol AS symbol,
          COUNT(*) AS option_rows,
          MIN(date) AS option_date_min,
          MAX(date) AS option_date_max
        FROM option_chain
        WHERE date >= '{start}'
          AND date <= '{end}'
          AND act_symbol IN ({symbols_sql})
        GROUP BY act_symbol
        ORDER BY act_symbol
        """,
    )
    coverage_vol = run_dolt_query(
        repo_path,
        f"""
        SELECT
          act_symbol AS symbol,
          COUNT(*) AS vol_rows
        FROM volatility_history
        WHERE date >= '{start}'
          AND date <= '{end}'
          AND act_symbol IN ({symbols_sql})
        GROUP BY act_symbol
        ORDER BY act_symbol
        """,
    )
    coverage_underlying = run_dolt_query(
        repo_path,
        f"""
        SELECT
          act_symbol AS symbol,
          COUNT(*) AS underlying_rows
        FROM underlying_prices_daily
        WHERE date >= '{start}'
          AND date <= '{end}'
          AND act_symbol IN ({symbols_sql})
        GROUP BY act_symbol
        ORDER BY act_symbol
        """,
    )
    vix_row_count = run_dolt_query(
        repo_path,
        f"""
        SELECT COUNT(*) AS vix_rows
        FROM vix_daily
        WHERE date >= '{start}'
          AND date <= '{end}'
        """,
    )

    option_nulls = run_dolt_query(
        repo_path,
        f"""
        SELECT
          act_symbol AS symbol,
          COUNT(*) AS total_rows,
          SUM(CASE WHEN bid IS NULL THEN 1 ELSE 0 END) AS bid_null_count,
          SUM(CASE WHEN ask IS NULL THEN 1 ELSE 0 END) AS ask_null_count,
          SUM(CASE WHEN delta IS NULL THEN 1 ELSE 0 END) AS delta_null_count
        FROM option_chain
        WHERE date >= '{start}'
          AND date <= '{end}'
          AND act_symbol IN ({symbols_sql})
        GROUP BY act_symbol
        ORDER BY act_symbol
        """,
    )
    vol_nulls = run_dolt_query(
        repo_path,
        f"""
        SELECT
          act_symbol AS symbol,
          COUNT(*) AS total_rows,
          SUM(CASE WHEN iv_current IS NULL THEN 1 ELSE 0 END) AS iv_null_count,
          SUM(CASE WHEN hv_current IS NULL THEN 1 ELSE 0 END) AS hv_null_count
        FROM volatility_history
        WHERE date >= '{start}'
          AND date <= '{end}'
          AND act_symbol IN ({symbols_sql})
        GROUP BY act_symbol
        ORDER BY act_symbol
        """,
    )

    dte_frame = run_dolt_query(
        repo_path,
        f"""
        SELECT
          date,
          act_symbol AS symbol,
          SUM(
            CASE WHEN ABS(DATEDIFF(expiration, date) - {int(target_dte)}) <= {int(dte_tolerance)}
            THEN 1 ELSE 0 END
          ) AS expirations_near_target
        FROM option_chain
        WHERE date >= '{start}'
          AND date <= '{end}'
          AND act_symbol IN ({symbols_sql})
        GROUP BY date, act_symbol
        ORDER BY date, act_symbol
        """,
    )

    output_root = Path(output_dir)
    output_root.mkdir(parents=True, exist_ok=True)

    coverage_rows: list[dict] = []
    vix_rows = int(vix_row_count.iloc[0]["vix_rows"]) if not vix_row_count.empty else 0
    for symbol in symbols:
        option_row = coverage_option[coverage_option["symbol"] == symbol]
        vol_row = coverage_vol[coverage_vol["symbol"] == symbol]
        under_row = coverage_underlying[coverage_underlying["symbol"] == symbol]

        option_rows = int(option_row.iloc[0]["option_rows"]) if not option_row.empty else 0
        option_min = option_row.iloc[0]["option_date_min"] if not option_row.empty else None
        option_max = option_row.iloc[0]["option_date_max"] if not option_row.empty else None
        vol_rows = int(vol_row.iloc[0]["vol_rows"]) if not vol_row.empty else 0
        under_rows = int(under_row.iloc[0]["underlying_rows"]) if not under_row.empty else 0
        coverage_rows.append(
            {
                "symbol": symbol,
                "option_rows": option_rows,
                "option_date_min": option_min,
                "option_date_max": option_max,
                "vol_rows": vol_rows,
                "underlying_rows": under_rows,
                "vix_rows": vix_rows,
            }
        )

    null_rows: list[dict] = []
    for _, row in option_nulls.iterrows():
        total = int(row["total_rows"])
        if total <= 0:
            continue
        for col, null_col in (
            ("bid", "bid_null_count"),
            ("ask", "ask_null_count"),
            ("delta", "delta_null_count"),
        ):
            null_count = int(row[null_col])
            null_rows.append(
                {
                    "table": "option_chain",
                    "symbol": str(row["symbol"]),
                    "column": col,
                    "null_count": null_count,
                    "null_rate": float(null_count / total),
                }
            )
    for _, row in vol_nulls.iterrows():
        total = int(row["total_rows"])
        if total <= 0:
            continue
        for col, null_col in (("iv_current", "iv_null_count"), ("hv_current", "hv_null_count")):
            null_count = int(row[null_col])
            null_rows.append(
                {
                    "table": "volatility_history",
                    "symbol": str(row["symbol"]),
                    "column": col,
                    "null_count": null_count,
                    "null_rate": float(null_count / total),
                }
            )

    dte_rows: list[dict] = []
    for _, row in dte_frame.iterrows():
        hits = int(row["expirations_near_target"])
        dte_rows.append(
            {
                "date": row["date"],
                "symbol": row["symbol"],
                "expirations_near_target": hits,
                "target_dte": target_dte,
                "tolerance": dte_tolerance,
                "has_target_expiry": hits > 0,
            }
        )

    coverage_path = output_root / "coverage.csv"
    nulls_path = output_root / "null_diagnostics.csv"
    dte_path = output_root / "dte_availability.csv"
    pd.DataFrame(coverage_rows).to_csv(coverage_path, index=False)
    pd.DataFrame(null_rows).to_csv(nulls_path, index=False)
    pd.DataFrame(dte_rows).to_csv(dte_path, index=False)
    return {
        "coverage": coverage_path,
        "null_diagnostics": nulls_path,
        "dte_availability": dte_path,
    }
