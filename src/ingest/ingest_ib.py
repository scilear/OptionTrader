from __future__ import annotations

import json
import logging
import math
import socket
import time
from datetime import date, datetime, timezone

from src.core.bootstrap import ensure_repo_root_on_path

ensure_repo_root_on_path()

from src.core.config import load_config
from src.core.qc import evaluate_quote
from src.db.connection import connect


def _host_reachable(host: str, port: int, timeout: float = 2.0) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def _safe_float(val) -> float:
    """Return float, or 0.0 if None/NaN."""
    try:
        f = float(val)
        return f if not math.isnan(f) else 0.0
    except (TypeError, ValueError):
        return 0.0


def _safe_int(val) -> int:
    try:
        f = float(val)
        return int(f) if not math.isnan(f) else 0
    except (TypeError, ValueError):
        return 0


def _ib_expiry_to_iso(expiry_str: str) -> str:
    """Convert IB expiry format YYYYMMDD to ISO YYYY-MM-DD."""
    return f"{expiry_str[:4]}-{expiry_str[4:6]}-{expiry_str[6:8]}"


def _fetch_spot(ib, underlying) -> float:
    """Fetch SPX spot price, trying multiple fields."""
    [ticker] = ib.reqTickers(underlying)
    for val in (ticker.marketPrice(), ticker.last, ticker.close):
        v = _safe_float(val)
        if v > 0:
            return v
    raise ValueError("Cannot determine spot price from IB")


def _run_ib_ingest(host: str, port: int, config: dict) -> None:
    from ib_insync import IB, Index, Option

    logger = logging.getLogger("ingest.ib")
    symbol = config["data"]["underlying"]  # SPX
    dte_min = config["data"]["dte_min"]
    dte_max = config["data"]["dte_max"]
    allow_zero_bid = config["quality"]["allow_zero_bid"]
    spread_gate_pct = config["quality"]["spread_gate_pct"]
    ib_cfg = config.get("ib", {})
    strike_pct_range = ib_cfg.get("strike_pct_range", 0.25)
    client_id = ib_cfg.get("client_id", 10)
    timeout_secs = ib_cfg.get("timeout_seconds", 10)

    logger.info("connecting to IB at %s:%s (clientId=%s)", host, port, client_id)
    ib = IB()
    ib.connect(host, port, clientId=client_id, timeout=timeout_secs, readonly=True)
    try:
        underlying = Index(symbol, "CBOE", "USD")
        ib.qualifyContracts(underlying)
        spot = _fetch_spot(ib, underlying)
        logger.info("spot=%s", spot)

        chains = ib.reqSecDefOptParams(symbol, "", "IND", underlying.conId)
        chain = next((c for c in chains if c.exchange == "SMART"), None)
        if chain is None and chains:
            chain = chains[0]
        if chain is None:
            raise RuntimeError("No option chain definition returned by IB")

        today = date.today()
        valid_expiries = [
            exp for exp in sorted(chain.expirations)
            if dte_min <= (date(int(exp[:4]), int(exp[4:6]), int(exp[6:8])) - today).days <= dte_max
        ]
        if not valid_expiries:
            raise RuntimeError(f"No expiries in DTE range {dte_min}-{dte_max}")
        logger.info("valid_expiries=%s", valid_expiries)

        lo = spot * (1 - strike_pct_range)
        hi = spot * (1 + strike_pct_range)
        valid_strikes = sorted(s for s in chain.strikes if lo <= s <= hi)
        logger.info("strikes in range: %s", len(valid_strikes))

        contracts = [
            Option(symbol, exp, strike, right, "SMART", currency="USD")
            for exp in valid_expiries
            for strike in valid_strikes
            for right in ("C", "P")
        ]
        logger.info("qualifying %s contracts", len(contracts))

        # Qualify in batches to avoid overwhelming IB
        qualified: list = []
        batch_size = 50
        for i in range(0, len(contracts), batch_size):
            batch = ib.qualifyContracts(*contracts[i : i + batch_size])
            qualified.extend(batch)
            if i + batch_size < len(contracts):
                time.sleep(0.1)

        if not qualified:
            raise RuntimeError("No contracts qualified with IB")
        logger.info("requesting market data snapshots for %s contracts", len(qualified))

        # Request tickers in batches (IB concurrent data limits)
        all_tickers = []
        for i in range(0, len(qualified), batch_size):
            batch = qualified[i : i + batch_size]
            tickers = ib.reqTickers(*batch)
            all_tickers.extend(tickers)
            if i + batch_size < len(qualified):
                time.sleep(0.5)

        timestamp = datetime.now(timezone.utc)
        conn = connect()
        try:
            conn.execute(
                """
                INSERT INTO snapshots (snapshot_id, ts, underlying, spot, source, session_tag, notes)
                VALUES (DEFAULT, ?, ?, ?, ?, ?, ?)
                """,
                (timestamp, symbol, spot, f"ib:{host}", "mid", None),
            )
            snapshot_id = conn.execute("SELECT MAX(snapshot_id) FROM snapshots").fetchone()[0]
            inserted = 0
            for ticker in all_tickers:
                c = ticker.contract
                bid = _safe_float(ticker.bid)
                ask = _safe_float(ticker.ask)
                last = _safe_float(ticker.last)
                bid_size = _safe_int(ticker.bidSize)
                ask_size = _safe_int(ticker.askSize)

                is_valid, flags = evaluate_quote(
                    bid=bid,
                    ask=ask,
                    allow_zero_bid=allow_zero_bid,
                    spread_gate_pct=spread_gate_pct,
                )
                if not is_valid:
                    continue

                raw_expiry = c.lastTradeDateOrContractMonth
                expiry_iso = _ib_expiry_to_iso(raw_expiry)

                conn.execute(
                    """
                    INSERT INTO option_quotes (
                        quote_id, snapshot_id, expiry, strike, option_right,
                        bid, ask, last, bid_size, ask_size, oi, volume, flags
                    ) VALUES (DEFAULT, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        snapshot_id,
                        expiry_iso,
                        float(c.strike),
                        c.right,
                        bid,
                        ask,
                        last,
                        bid_size,
                        ask_size,
                        0,  # OI not available via reqTickers snapshot
                        0,
                        json.dumps(flags),
                    ),
                )
                inserted += 1
            logger.info("inserted %s quotes for snapshot_id=%s", inserted, snapshot_id)
        finally:
            conn.close()
    finally:
        ib.disconnect()


def try_ingest_ib(config: dict) -> bool:
    """Try each configured IB host in order. Returns True on success, False if all fail."""
    logger = logging.getLogger("ingest.ib")
    ib_cfg = config.get("ib", {})
    hosts: list[str] = ib_cfg.get("hosts", [])
    port: int = ib_cfg.get("port", 7496)

    if not hosts:
        logger.info("no IB hosts configured")
        return False

    for host in hosts:
        logger.info("trying IB host %s:%s", host, port)
        if not _host_reachable(host, port, timeout=2.0):
            logger.info("host %s port %s not reachable", host, port)
            continue
        try:
            _run_ib_ingest(host, port, config)
            logger.info("IB ingest succeeded via %s:%s", host, port)
            return True
        except Exception as exc:
            logger.warning("IB ingest failed on %s:%s — %s", host, port, exc)

    return False
