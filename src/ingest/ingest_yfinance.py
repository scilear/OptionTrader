from __future__ import annotations

from datetime import date, datetime, timezone
import json

from src.core.bootstrap import ensure_repo_root_on_path

ensure_repo_root_on_path()

import pandas as pd
import logging
import yfinance as yf

from src.core.config import load_config
from src.core.qc import evaluate_quote
from src.db.connection import connect, _is_pg


def to_int(value) -> int:
    if value is None or pd.isna(value):
        return 0
    return int(value)


def _get_spot(ticker: yf.Ticker) -> float:
    fast_info = getattr(ticker, "fast_info", None)
    if fast_info and fast_info.get("last_price"):
        return float(fast_info["last_price"])
    history = ticker.history(period="1d")
    if not history.empty:
        return float(history["Close"].iloc[-1])
    raise ValueError("Unable to fetch spot price")


def _valid_expiry(expiry: str, dte_min: int, dte_max: int) -> bool:
    exp_date = date.fromisoformat(expiry)
    dte = (exp_date - date.today()).days
    return dte_min <= dte <= dte_max


def _build_quote_rows(chain_df, snapshot_id, expiry, right, allow_zero_bid, spread_gate_pct):
    rows = []
    if chain_df is None or chain_df.empty:
        return rows
    for _, row in chain_df.iterrows():
        bid = float(row.get("bid", 0.0))
        ask = float(row.get("ask", 0.0))
        is_valid, flags = evaluate_quote(
            bid=bid, ask=ask,
            allow_zero_bid=allow_zero_bid,
            spread_gate_pct=spread_gate_pct,
        )
        if not is_valid:
            continue
        rows.append((
            snapshot_id,
            expiry,
            float(row.get("strike", 0.0)),
            right,
            bid,
            ask,
            float(row.get("lastPrice", 0.0)),
            to_int(row.get("bidSize", 0)),
            to_int(row.get("askSize", 0)),
            to_int(row.get("openInterest", 0)),
            to_int(row.get("volume", 0)),
            json.dumps(flags),
        ))
    return rows


_INSERT_QUOTE = """
    INSERT INTO option_quotes (
        snapshot_id, expiry, strike, option_right,
        bid, ask, last, bid_size, ask_size, oi, volume, flags
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
"""


def run_ingest(run_id: int | None = None) -> None:
    logger = logging.getLogger("ingest")
    config = load_config()
    symbol = config["data"]["symbol"]
    dte_min = config["data"]["dte_min"]
    dte_max = config["data"]["dte_max"]
    capture_all = config["data"].get("capture_all_expiries", False)
    allow_zero_bid = config["quality"]["allow_zero_bid"]
    spread_gate_pct = config["quality"]["spread_gate_pct"]

    timestamp = datetime.now(timezone.utc)
    logger.info("starting ingest for %s", symbol)
    ticker = yf.Ticker(symbol)
    spot = _get_spot(ticker)
    logger.info("spot=%s", spot)

    conn = connect()
    is_pg = _is_pg(conn)
    try:
        if is_pg:
            row = conn.execute(
                """
                INSERT INTO snapshots (
                    run_id, ts, underlying, spot, source, session_tag, notes
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING snapshot_id
                """,
                (
                    run_id, timestamp, config["data"]["underlying"],
                    spot, "yfinance", "mid", None,
                ),
            ).fetchone()
            snapshot_id = int(row[0])
        else:
            conn.execute(
                """
                INSERT INTO snapshots (
                    run_id, ts, underlying, spot, source, session_tag, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    run_id, timestamp, config["data"]["underlying"],
                    spot, "yfinance", "mid", None,
                ),
            )
            snapshot_id = conn.execute("SELECT MAX(snapshot_id) FROM snapshots").fetchone()[0]

        for expiry in ticker.options:
            if not capture_all and not _valid_expiry(expiry, dte_min, dte_max):
                continue
            logger.info("fetching expiry=%s", expiry)
            chain = ticker.option_chain(expiry)
            all_rows = []
            for right, df in (("C", chain.calls), ("P", chain.puts)):
                all_rows.extend(
                    _build_quote_rows(df, snapshot_id, expiry, right, allow_zero_bid, spread_gate_pct)
                )
            if all_rows:
                if is_pg:
                    conn.copy_quote_rows(all_rows)
                else:
                    for r in all_rows:
                        conn.execute(_INSERT_QUOTE, r)
    finally:
        conn.close()


if __name__ == "__main__":
    run_ingest()
