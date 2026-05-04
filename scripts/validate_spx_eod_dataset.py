from __future__ import annotations

import argparse
from pathlib import Path
import sys

repo_root = Path(__file__).resolve().parents[1]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from src.core.bootstrap import ensure_repo_root_on_path

ensure_repo_root_on_path()

import duckdb


def _bool_icon(value: bool) -> str:
    return "PASS" if value else "FAIL"


def validate_eod_dataset(db_path: Path) -> dict:
    conn = duckdb.connect(str(db_path))
    try:
        tables = {row[0] for row in conn.execute("SHOW TABLES").fetchall()}
        has_snapshots = "snapshots" in tables
        has_quotes = "option_quotes" in tables

        snapshot_count = conn.execute("SELECT COUNT(*) FROM snapshots").fetchone()[0] if has_snapshots else 0
        quote_count = conn.execute("SELECT COUNT(*) FROM option_quotes").fetchone()[0] if has_quotes else 0

        malformed_dates = 0
        crossed_quotes = 0
        missing_bidask = 0
        invalid_right = 0
        orphan_quotes = 0
        duplicate_quotes = 0

        if has_quotes:
            malformed_dates = conn.execute(
                "SELECT COUNT(*) FROM option_quotes WHERE expiry IS NULL"
            ).fetchone()[0]
            crossed_quotes = conn.execute(
                "SELECT COUNT(*) FROM option_quotes WHERE bid > ask"
            ).fetchone()[0]
            missing_bidask = conn.execute(
                "SELECT COUNT(*) FROM option_quotes WHERE bid IS NULL OR ask IS NULL"
            ).fetchone()[0]
            invalid_right = conn.execute(
                "SELECT COUNT(*) FROM option_quotes WHERE option_right NOT IN ('C','P')"
            ).fetchone()[0]
            orphan_quotes = conn.execute(
                """
                SELECT COUNT(*)
                FROM option_quotes q
                LEFT JOIN snapshots s ON s.snapshot_id = q.snapshot_id
                WHERE s.snapshot_id IS NULL
                """
            ).fetchone()[0]
            duplicate_quotes = conn.execute(
                """
                SELECT COALESCE(SUM(cnt - 1), 0)
                FROM (
                  SELECT snapshot_id, expiry, strike, option_right, COUNT(*) AS cnt
                  FROM option_quotes
                  GROUP BY 1,2,3,4
                  HAVING COUNT(*) > 1
                )
                """
            ).fetchone()[0]

        snapshot_by_day = []
        if has_snapshots:
            snapshot_by_day = conn.execute(
                """
                SELECT CAST(ts AS DATE) AS ds, COUNT(*)
                FROM snapshots
                GROUP BY 1
                ORDER BY 1
                """
            ).fetchall()

        quote_stats = (0, 0, 0.0, 0.0)
        if has_quotes:
            quote_stats = conn.execute(
                """
                SELECT
                  MIN(bid),
                  MAX(ask),
                  AVG(CASE WHEN bid > 0 AND ask > 0 THEN (ask - bid) / ((ask + bid) / 2.0) END),
                  SUM(CASE WHEN bid = 0 THEN 1 ELSE 0 END) * 1.0 / COUNT(*)
                FROM option_quotes
                """
            ).fetchone()

        hard_checks = {
            "tables_present": has_snapshots and has_quotes,
            "non_empty_snapshots": snapshot_count > 0,
            "non_empty_quotes": quote_count > 0,
            "no_crossed_quotes": crossed_quotes == 0,
            "no_missing_bidask": missing_bidask == 0,
            "valid_option_rights": invalid_right == 0,
            "no_orphan_quotes": orphan_quotes == 0,
            "no_duplicate_natural_keys": duplicate_quotes == 0,
            "no_null_expiry": malformed_dates == 0,
        }
        hard_pass = all(hard_checks.values())

        result = {
            "db_path": str(db_path),
            "snapshot_count": int(snapshot_count),
            "quote_count": int(quote_count),
            "hard_checks": hard_checks,
            "hard_pass": hard_pass,
            "counts": {
                "crossed_quotes": int(crossed_quotes),
                "missing_bidask": int(missing_bidask),
                "invalid_right": int(invalid_right),
                "orphan_quotes": int(orphan_quotes),
                "duplicate_quotes": int(duplicate_quotes),
                "null_expiry": int(malformed_dates),
            },
            "soft_stats": {
                "min_bid": float(quote_stats[0]) if quote_stats[0] is not None else None,
                "max_ask": float(quote_stats[1]) if quote_stats[1] is not None else None,
                "avg_relative_spread": float(quote_stats[2]) if quote_stats[2] is not None else None,
                "zero_bid_ratio": float(quote_stats[3]) if quote_stats[3] is not None else None,
            },
            "snapshot_by_day": [(str(day), int(count)) for day, count in snapshot_by_day],
        }
        return result
    finally:
        conn.close()


def render_report(result: dict) -> str:
    lines = [
        "# OptionTrader S4-03 EOD Validation Report",
        "",
        f"DB path: `{result['db_path']}`",
        f"Snapshot count: `{result['snapshot_count']}`",
        f"Quote count: `{result['quote_count']}`",
        "",
        "## Hard Checks",
        "",
    ]
    for key, value in result["hard_checks"].items():
        lines.append(f"- `{key}`: {_bool_icon(bool(value))}")

    lines.extend(
        [
            "",
            "## Issue Counts",
            "",
        ]
    )
    for key, value in result["counts"].items():
        lines.append(f"- `{key}`: `{value}`")

    lines.extend(
        [
            "",
            "## Soft Stats",
            "",
        ]
    )
    for key, value in result["soft_stats"].items():
        lines.append(f"- `{key}`: `{value}`")

    lines.extend(
        [
            "",
            "## Snapshot Density by Date",
            "",
            "| date | snapshot_count |",
            "| --- | ---: |",
        ]
    )
    for day, count in result["snapshot_by_day"]:
        lines.append(f"| {day} | {count} |")

    lines.extend(
        [
            "",
            "## Gate",
            "",
            f"- `hard_pass`: {_bool_icon(bool(result['hard_pass']))}",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate ingested SPX EOD dataset")
    parser.add_argument("--db-path", required=True)
    parser.add_argument("--report", required=True)
    args = parser.parse_args()

    result = validate_eod_dataset(Path(args.db_path))
    report = render_report(result)
    report_path = Path(args.report)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report, encoding="utf-8")
    print(f"hard_pass={result['hard_pass']}")
    print(f"report_written={report_path}")


if __name__ == "__main__":
    main()
