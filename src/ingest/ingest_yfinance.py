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
from src.db.connection import connect
from src.db.init_db import init_db


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


def _next_id(conn, table: str, id_col: str) -> int:
    row = conn.execute(f"SELECT MAX({id_col}) FROM {table}").fetchone()
    current = row[0] if row and row[0] is not None else 0
    return int(current) + 1


def _valid_expiry(expiry: str, dte_min: int, dte_max: int) -> bool:
    exp_date = date.fromisoformat(expiry)
    dte = (exp_date - date.today()).days
    return dte_min <= dte <= dte_max


def run_ingest() -> None:
    logger = logging.getLogger("ingest")
    config = load_config()
    source = config["data"]["source"]
    if source != "yfinance":
        raise ValueError("config.data.source must be 'yfinance' for this ingest job")
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

    init_db()
    conn = connect()
    try:
        conn.execute(
            """
            INSERT INTO snapshots (snapshot_id, ts, underlying, spot, source, session_tag, notes)
            VALUES (DEFAULT, ?, ?, ?, ?, ?, ?)
            """,
            (
                timestamp,
                config["data"]["underlying"],
                spot,
                source,
                "mid",
                None,
            ),
        )
        snapshot_id = conn.execute("SELECT MAX(snapshot_id) FROM snapshots").fetchone()[0]

        for expiry in ticker.options:
            if not capture_all and not _valid_expiry(expiry, dte_min, dte_max):
                continue
            logger.info("fetching expiry=%s", expiry)
            chain = ticker.option_chain(expiry)
            for right, df in (("C", chain.calls), ("P", chain.puts)):
                if df is None or df.empty:
                    continue
                for _, row in df.iterrows():
                    bid = float(row.get("bid", 0.0))
                    ask = float(row.get("ask", 0.0))
                    is_valid, flags = evaluate_quote(
                        bid=bid,
                        ask=ask,
                        allow_zero_bid=allow_zero_bid,
                        spread_gate_pct=spread_gate_pct,
                    )
                    if not is_valid:
                        continue
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
                        ),
                    )
    finally:
        conn.close()


if __name__ == "__main__":
    run_ingest()
