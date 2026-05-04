from __future__ import annotations

import argparse
import csv
import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import sys

repo_root = Path(__file__).resolve().parents[1]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from src.core.bootstrap import ensure_repo_root_on_path

ensure_repo_root_on_path()

from src.core.config import load_config
from src.core.qc import evaluate_quote
from src.db.connection import connect
from src.db.init_db import init_db


@dataclass
class IngestSummary:
    files_processed: int = 0
    rows_read: int = 0
    snapshots_inserted: int = 0
    snapshots_reused: int = 0
    quotes_inserted: int = 0
    quotes_rejected: int = 0


def _normalize_header(value: str) -> str:
    return value.strip().strip("[]").strip().lower()


def _parse_float(value: str | None) -> float | None:
    if value is None:
        return None
    text = str(value).strip()
    if text == "":
        return None
    try:
        return float(text)
    except ValueError:
        return None


def _parse_int(value: str | None) -> int:
    parsed = _parse_float(value)
    if parsed is None:
        return 0
    return int(parsed)


def _parse_size(value: str | None) -> tuple[int, int]:
    if value is None:
        return 0, 0
    text = str(value).strip()
    if "x" not in text:
        return 0, 0
    left, right = text.split("x", 1)
    return _parse_int(left), _parse_int(right)


def _iter_quote_rows(file_path: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    with file_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle, skipinitialspace=True)
        raw_header = next(reader, None)
        if raw_header is None:
            return rows
        header = [_normalize_header(column) for column in raw_header]
        for raw in reader:
            if not raw:
                continue
            if len(raw) < len(header):
                raw = raw + [""] * (len(header) - len(raw))
            rows.append({header[idx]: raw[idx].strip() for idx in range(len(header))})
    return rows


def _snapshot_key(quote_readtime: str, spot: float) -> tuple[str, float]:
    return quote_readtime, round(float(spot), 6)


def _load_existing_snapshots(
    conn,
    underlying: str,
    source_tag: str,
    session_tag: str,
) -> dict[tuple[str, float], int]:
    rows = conn.execute(
        """
        SELECT snapshot_id, ts, spot
        FROM snapshots
        WHERE underlying = ?
          AND source = ?
          AND session_tag = ?
        ORDER BY snapshot_id
        """,
        (underlying, source_tag, session_tag),
    ).fetchall()
    mapping: dict[tuple[str, float], int] = {}
    for snapshot_id, ts, spot in rows:
        key = _snapshot_key(ts.strftime("%Y-%m-%d %H:%M"), float(spot))
        mapping[key] = int(snapshot_id)
    return mapping


def _resolve_snapshot(
    conn,
    snapshots_by_key: dict[tuple[str, float], int],
    cleared_snapshot_ids: set[int],
    summary: IngestSummary,
    *,
    quote_readtime: str,
    ts: datetime,
    underlying: str,
    spot: float,
    source_tag: str,
    session_tag: str,
) -> int:
    key = _snapshot_key(quote_readtime, spot)
    existing = snapshots_by_key.get(key)
    if existing is not None:
        summary.snapshots_reused += 1
        if existing not in cleared_snapshot_ids:
            conn.execute("DELETE FROM option_quotes WHERE snapshot_id = ?", (existing,))
            cleared_snapshot_ids.add(existing)
        return existing

    row = conn.execute(
        """
        INSERT INTO snapshots (
            snapshot_id, run_id, ts, underlying, spot, source, session_tag, notes
        ) VALUES (DEFAULT, NULL, ?, ?, ?, ?, ?, ?)
        RETURNING snapshot_id
        """,
        (ts, underlying, spot, source_tag, session_tag, "eod_import"),
    ).fetchone()
    snapshot_id = int(row[0])
    snapshots_by_key[key] = snapshot_id
    summary.snapshots_inserted += 1
    return snapshot_id


def ingest_spx_eod_option_data(
    input_dir: Path,
    glob_pattern: str,
    underlying: str,
    source_tag: str = "eod",
    session_tag: str = "eod",
    max_files: int | None = None,
) -> IngestSummary:
    config = load_config()
    allow_zero_bid = bool(config["quality"]["allow_zero_bid"])
    spread_gate_pct = float(config["quality"]["spread_gate_pct"])

    file_paths = sorted(input_dir.glob(glob_pattern))
    if max_files is not None:
        file_paths = file_paths[:max_files]

    init_db()
    summary = IngestSummary()
    conn = connect()
    try:
        snapshots_by_key = _load_existing_snapshots(conn, underlying, source_tag, session_tag)
        cleared_snapshot_ids: set[int] = set()

        for file_path in file_paths:
            rows = _iter_quote_rows(file_path)
            summary.files_processed += 1
            for row in rows:
                summary.rows_read += 1
                quote_readtime = row.get("quote_readtime")
                expiry_raw = row.get("expire_date")
                strike = _parse_float(row.get("strike"))
                spot = _parse_float(row.get("underlying_last"))
                if not quote_readtime or not expiry_raw or strike is None or spot is None:
                    continue
                try:
                    ts = datetime.strptime(quote_readtime, "%Y-%m-%d %H:%M")
                    expiry = datetime.strptime(expiry_raw, "%Y-%m-%d").date()
                except ValueError:
                    continue

                snapshot_id = _resolve_snapshot(
                    conn,
                    snapshots_by_key,
                    cleared_snapshot_ids,
                    summary,
                    quote_readtime=quote_readtime,
                    ts=ts,
                    underlying=underlying,
                    spot=spot,
                    source_tag=source_tag,
                    session_tag=session_tag,
                )

                for right in ("C", "P"):
                    bid = _parse_float(row.get(f"{right.lower()}_bid"))
                    ask = _parse_float(row.get(f"{right.lower()}_ask"))
                    if bid is None or ask is None:
                        summary.quotes_rejected += 1
                        continue
                    is_valid, flags = evaluate_quote(
                        bid=bid,
                        ask=ask,
                        allow_zero_bid=allow_zero_bid,
                        spread_gate_pct=spread_gate_pct,
                    )
                    if not is_valid:
                        summary.quotes_rejected += 1
                        continue
                    bid_size, ask_size = _parse_size(row.get(f"{right.lower()}_size"))
                    conn.execute(
                        """
                        INSERT INTO option_quotes (
                            quote_id, snapshot_id, expiry, strike, option_right,
                            bid, ask, last, bid_size, ask_size, oi, volume, flags
                        ) VALUES (DEFAULT, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            snapshot_id,
                            expiry,
                            strike,
                            right,
                            bid,
                            ask,
                            _parse_float(row.get(f"{right.lower()}_last")) or 0.0,
                            bid_size,
                            ask_size,
                            0,
                            _parse_int(row.get(f"{right.lower()}_volume")),
                            json.dumps(flags, sort_keys=True),
                        ),
                    )
                    summary.quotes_inserted += 1
    finally:
        conn.close()

    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest SPX EOD option data into OptionTrader DB")
    parser.add_argument("--input-dir", required=True)
    parser.add_argument("--glob", default="spx_eod_*.txt")
    parser.add_argument("--underlying", default="SPX")
    parser.add_argument("--source-tag", default="eod")
    parser.add_argument("--session-tag", default="eod")
    parser.add_argument("--max-files", type=int, default=None)
    args = parser.parse_args()

    summary = ingest_spx_eod_option_data(
        input_dir=Path(args.input_dir),
        glob_pattern=args.glob,
        underlying=args.underlying,
        source_tag=args.source_tag,
        session_tag=args.session_tag,
        max_files=args.max_files,
    )
    print(json.dumps(summary.__dict__, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
