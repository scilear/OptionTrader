#!/usr/bin/env python3
"""
option_chain.py — Fetch an option chain for any ticker with full Greeks and IV rank.

Data source: IB Gateway (primary, via ib_insync), yfinance fallback.

Usage:
    python tools/option_chain.py --ticker GLD --dte 21
    python tools/option_chain.py --ticker SPX --expiry 2025-04-17 --delta-range 0.10 0.35
    python tools/option_chain.py --ticker AAPL --dte 30 --output csv > chain.csv
    python tools/option_chain.py --ticker GLD --dte 21 --output json
    python tools/option_chain.py --ticker SPX --dte 21 --no-ib
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import sys
import time
from dataclasses import asdict, dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import Optional

repo_root = Path(__file__).resolve().parents[1]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from src.core.iv_solve import solve_iv, bs_greeks


# Inlined from ingest_ib to avoid pulling in db/duckdb dependencies
def _host_reachable(host: str, port: int, timeout: float = 2.0) -> bool:
    import socket
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def _safe_float(val) -> float:
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

# ── Constants ──────────────────────────────────────────────────────────────────
RATE = 0.05           # approximate risk-free rate
WIDE_SPREAD_PCT = 0.15
BATCH_SIZE = 50

# Known index underlyings: IB uses secType=IND; yfinance needs ^ prefix
_IB_INDEX_INFO: dict[str, tuple[str, str]] = {
    "SPX": ("CBOE", "USD"),
    "NDX": ("NASDAQ", "USD"),
    "RUT": ("CBOE", "USD"),
    "VIX": ("CBOE", "USD"),
    "XSP": ("CBOE", "USD"),
}
_YF_SYMBOL_MAP: dict[str, str] = {
    "SPX": "^SPX",
    "NDX": "^NDX",
    "RUT": "^RUT",
    "VIX": "^VIX",
    "GSPC": "^GSPC",
}


# ── Data type ─────────────────────────────────────────────────────────────────
@dataclass
class OptionRow:
    expiry: str
    strike: float
    right: str              # "C" or "P"
    bid: float
    ask: float
    mid: float
    last: float
    iv: Optional[float]
    delta: Optional[float]
    gamma: Optional[float]
    vega: Optional[float]
    theta: Optional[float]  # points per calendar day
    oi: int
    volume: int
    stale: bool             # bid=0 or ask=0
    wide_spread: bool       # spread > 15% of mid
    iv_solve_status: str


# ── Math helpers ───────────────────────────────────────────────────────────────
def _ncdf(x: float) -> float:
    return 0.5 * math.erfc(-x / math.sqrt(2))


def _npdf(x: float) -> float:
    return math.exp(-0.5 * x * x) / math.sqrt(2 * math.pi)


def _bs_theta(
    spot: float,
    strike: float,
    rate: float,
    div: float,
    t_years: float,
    vol: float,
    right: str,
) -> float:
    """Black-Scholes theta in option points per calendar day."""
    if t_years <= 0 or vol <= 0:
        return 0.0
    fwd = spot * math.exp((rate - div) * t_years)
    vol_sqrt = vol * math.sqrt(t_years)
    d1 = (math.log(fwd / strike) + 0.5 * vol * vol * t_years) / vol_sqrt
    d2 = d1 - vol_sqrt
    base = -spot * math.exp(-div * t_years) * _npdf(d1) * vol / (2 * math.sqrt(t_years))
    if right == "C":
        theta = (
            base
            - rate * strike * math.exp(-rate * t_years) * _ncdf(d2)
            + div * spot * math.exp(-div * t_years) * _ncdf(d1)
        )
    else:
        theta = (
            base
            + rate * strike * math.exp(-rate * t_years) * _ncdf(-d2)
            - div * spot * math.exp(-div * t_years) * _ncdf(-d1)
        )
    return theta / 365.0


def _build_row(
    expiry: str,
    strike: float,
    right: str,
    bid: float,
    ask: float,
    last: float,
    oi: int,
    volume: int,
    spot: float,
    rate: float,
    div: float,
) -> OptionRow:
    mid = (bid + ask) / 2.0 if bid + ask > 0 else 0.0
    stale = bid <= 0 or ask <= 0
    wide_spread = mid > 0 and (ask - bid) / mid > WIDE_SPREAD_PCT

    expiry_date = date.fromisoformat(expiry)
    t_years = max((expiry_date - date.today()).days, 0) / 365.0

    price_for_iv = mid if mid > 0 else last
    iv_result = None
    if price_for_iv > 0 and t_years > 0:
        iv_result = solve_iv(price_for_iv, spot, strike, rate, div, t_years, right)

    iv = iv_result.iv if iv_result else None
    status = iv_result.status if iv_result else "no_price"

    delta = gamma = vega = theta = None
    if iv:
        greeks = bs_greeks(spot, strike, rate, div, t_years, iv, right)
        delta = greeks["delta"]
        gamma = greeks["gamma"]
        vega = greeks["vega"]
        theta = _bs_theta(spot, strike, rate, div, t_years, iv, right)

    return OptionRow(
        expiry=expiry,
        strike=strike,
        right=right,
        bid=bid,
        ask=ask,
        mid=mid,
        last=last,
        iv=iv,
        delta=delta,
        gamma=gamma,
        vega=vega,
        theta=theta,
        oi=oi,
        volume=volume,
        stale=stale,
        wide_spread=wide_spread,
        iv_solve_status=status,
    )


# ── IB fetch ──────────────────────────────────────────────────────────────────
def _fetch_ib(
    ticker: str, target_expiry: str, config: dict
) -> tuple[float, list[OptionRow]] | None:
    """Fetch option chain from IB. Returns (spot, rows) or None if unavailable."""
    try:
        from ib_insync import IB, Index, Stock, Option
    except ImportError:
        return None

    ib_cfg = config.get("ib", {})
    hosts: list[str] = ib_cfg.get("hosts", [])
    port: int = ib_cfg.get("port", 7496)
    # Use client_id+5 to avoid conflicting with the running pipeline (client_id 10)
    client_id: int = ib_cfg.get("client_id", 10) + 5
    timeout_secs: int = ib_cfg.get("timeout_seconds", 10)
    strike_pct_range: float = ib_cfg.get("strike_pct_range", 0.25)

    host_used = next((h for h in hosts if _host_reachable(h, port, timeout=2.0)), None)
    if host_used is None:
        return None

    ib = IB()
    try:
        ib.connect(host_used, port, clientId=client_id, timeout=timeout_secs, readonly=True)

        upper = ticker.upper()
        if upper in _IB_INDEX_INFO:
            exchange, currency = _IB_INDEX_INFO[upper]
            underlying = Index(upper, exchange, currency)
            sec_type = "IND"
        else:
            underlying = Stock(upper, "SMART", "USD")
            sec_type = "STK"

        ib.qualifyContracts(underlying)

        # Spot price
        [uticker] = ib.reqTickers(underlying)
        spot = 0.0
        for val in (uticker.marketPrice(), uticker.last, uticker.close):
            v = _safe_float(val)
            if v > 0:
                spot = v
                break
        if spot <= 0:
            return None

        # Option chain definition
        chains = ib.reqSecDefOptParams(upper, "", sec_type, underlying.conId)
        chain = next((c for c in chains if c.exchange == "SMART"), None)
        if chain is None and chains:
            chain = chains[0]
        if chain is None:
            return None

        # Find expiry closest to target
        target_date = date.fromisoformat(target_expiry)
        ib_expiry = min(
            chain.expirations,
            key=lambda e: abs((date(int(e[:4]), int(e[4:6]), int(e[6:8])) - target_date).days),
        )

        lo = spot * (1 - strike_pct_range)
        hi = spot * (1 + strike_pct_range)
        valid_strikes = sorted(s for s in chain.strikes if lo <= s <= hi)

        contracts = [
            Option(upper, ib_expiry, strike, right, "SMART", currency="USD")
            for strike in valid_strikes
            for right in ("C", "P")
        ]

        qualified: list = []
        for i in range(0, len(contracts), BATCH_SIZE):
            batch = ib.qualifyContracts(*contracts[i : i + BATCH_SIZE])
            qualified.extend(batch)
            if i + BATCH_SIZE < len(contracts):
                time.sleep(0.1)

        if not qualified:
            return None

        all_tickers = []
        for i in range(0, len(qualified), BATCH_SIZE):
            batch = qualified[i : i + BATCH_SIZE]
            tickers = ib.reqTickers(*batch)
            all_tickers.extend(tickers)
            if i + BATCH_SIZE < len(qualified):
                time.sleep(0.5)

        expiry_iso = f"{ib_expiry[:4]}-{ib_expiry[4:6]}-{ib_expiry[6:8]}"
        rows = []
        for t in all_tickers:
            c = t.contract
            rows.append(
                _build_row(
                    expiry_iso,
                    float(c.strike),
                    c.right,
                    _safe_float(t.bid),
                    _safe_float(t.ask),
                    _safe_float(t.last),
                    0,  # OI not available via reqTickers snapshot
                    _safe_int(getattr(t, "volume", 0)),
                    spot,
                    RATE,
                    0.0,
                )
            )

        return spot, rows

    except Exception as exc:
        print(f"IB fetch failed: {exc}", file=sys.stderr)
        return None
    finally:
        try:
            ib.disconnect()
        except Exception:
            pass


# ── yfinance fetch ────────────────────────────────────────────────────────────
def _fetch_yf(
    ticker: str, target_expiry: str
) -> tuple[float, list[OptionRow]] | None:
    """Fetch option chain from yfinance. Returns (spot, rows) or None."""
    try:
        import yfinance as yf
    except ImportError:
        return None

    yf_sym = _YF_SYMBOL_MAP.get(ticker.upper(), ticker)
    t = yf.Ticker(yf_sym)

    spot = 0.0
    fast_info = getattr(t, "fast_info", None)
    if fast_info:
        v = fast_info.get("last_price")
        if v:
            try:
                spot = float(v)
            except (TypeError, ValueError):
                pass
    if spot <= 0:
        hist = t.history(period="1d")
        if not hist.empty:
            spot = float(hist["Close"].iloc[-1])
    if spot <= 0:
        return None

    available = [date.fromisoformat(e) for e in t.options]
    if not available:
        return None
    target_date = date.fromisoformat(target_expiry)
    closest = min(available, key=lambda d: abs((d - target_date).days))
    expiry_str = closest.isoformat()

    chain = t.option_chain(expiry_str)
    rows = []

    def _f(x) -> float:
        try:
            v = float(x)
            return 0.0 if math.isnan(v) else v
        except Exception:
            return 0.0

    def _i(x) -> int:
        try:
            v = float(x)
            return 0 if math.isnan(v) else int(v)
        except Exception:
            return 0

    for right, df in (("C", chain.calls), ("P", chain.puts)):
        if df is None or df.empty:
            continue
        for _, row in df.iterrows():
            rows.append(
                _build_row(
                    expiry_str,
                    _f(row.get("strike", 0)),
                    right,
                    _f(row.get("bid", 0)),
                    _f(row.get("ask", 0)),
                    _f(row.get("lastPrice", 0)),
                    _i(row.get("openInterest", 0)),
                    _i(row.get("volume", 0)),
                    spot,
                    RATE,
                    0.0,
                )
            )

    return spot, rows


# ── IV rank (RV proxy) ────────────────────────────────────────────────────────
def _compute_iv_rank(ticker: str, atm_iv: float) -> Optional[float]:
    """
    IV rank as percentile of current ATM IV vs 1-year of rolling 21-day realized vol.

    Uses realized vol as a proxy for historical IV — reasonable for most underlyings
    and avoids needing a stored IV history. Returns 0–100 or None if insufficient data.
    """
    try:
        import yfinance as yf

        yf_sym = _YF_SYMBOL_MAP.get(ticker.upper(), ticker)
        hist = yf.Ticker(yf_sym).history(period="1y")
        if len(hist) < 50:
            return None
        log_ret = (hist["Close"] / hist["Close"].shift(1)).map(math.log).dropna()
        rv_series = log_ret.rolling(21).std() * math.sqrt(252)
        rv_series = rv_series.dropna()
        if rv_series.empty:
            return None
        lo, hi = float(rv_series.min()), float(rv_series.max())
        if hi <= lo:
            return None
        rank = (atm_iv - lo) / (hi - lo) * 100.0
        return max(0.0, min(100.0, rank))
    except Exception:
        return None


# ── Delta filter ──────────────────────────────────────────────────────────────
def _filter_delta(
    rows: list[OptionRow], delta_min: float, delta_max: float
) -> list[OptionRow]:
    return [r for r in rows if r.delta is not None and delta_min <= abs(r.delta) <= delta_max]


# ── Output formatters ─────────────────────────────────────────────────────────
def _fmt_f(val: Optional[float], spec: str = ".4f", none: str = "—") -> str:
    return none if val is None else format(val, spec)


def _print_table(
    rows: list[OptionRow], spot: float, iv_rank: Optional[float], source: str
) -> None:
    rank_str = f"{iv_rank:.1f}%" if iv_rank is not None else "n/a"
    print(f"\nSpot: {spot:.2f}  |  IV Rank (RV proxy): {rank_str}  |  Source: {source}\n")

    col_w = [12, 9, 5, 7, 7, 7, 7, 7, 9, 8, 9, 8, 8, 10]
    headers = ["Expiry", "Strike", "Side", "Bid", "Ask", "Mid", "IV%", "Delta", "Gamma", "Vega", "Theta", "OI", "Vol", "Flags"]
    sep = "  ".join("-" * w for w in col_w)
    hdr = "  ".join(h.ljust(w) for h, w in zip(headers, col_w))
    print(hdr)
    print(sep)

    for r in rows:
        flags = []
        if r.stale:
            flags.append("STALE")
        if r.wide_spread:
            flags.append("WIDE")
        cols = [
            r.expiry,
            f"{r.strike:.1f}",
            r.right,
            f"{r.bid:.2f}",
            f"{r.ask:.2f}",
            f"{r.mid:.2f}",
            _fmt_f(r.iv * 100 if r.iv else None, ".1f"),
            _fmt_f(r.delta, ".3f"),
            _fmt_f(r.gamma, ".5f"),
            _fmt_f(r.vega, ".3f"),
            _fmt_f(r.theta, ".4f"),
            str(r.oi),
            str(r.volume),
            ",".join(flags),
        ]
        print("  ".join(c.ljust(w) for c, w in zip(cols, col_w)))

    print(f"\n{len(rows)} contracts")


def _print_json(
    rows: list[OptionRow],
    spot: float,
    iv_rank: Optional[float],
    ticker: str,
    expiry: str,
    source: str,
) -> None:
    print(
        json.dumps(
            {
                "ticker": ticker,
                "expiry": expiry,
                "spot": spot,
                "iv_rank_rv_proxy": iv_rank,
                "source": source,
                "count": len(rows),
                "rows": [asdict(r) for r in rows],
            },
            indent=2,
        )
    )


def _print_csv(rows: list[OptionRow], spot: float, iv_rank: Optional[float]) -> None:
    writer = csv.writer(sys.stdout)
    writer.writerow([
        "expiry", "strike", "right", "bid", "ask", "mid", "last",
        "iv", "delta", "gamma", "vega", "theta",
        "oi", "volume", "stale", "wide_spread", "iv_solve_status",
    ])
    for r in rows:
        writer.writerow([
            r.expiry, r.strike, r.right,
            r.bid, r.ask, r.mid, r.last,
            r.iv, r.delta, r.gamma, r.vega, r.theta,
            r.oi, r.volume, r.stale, r.wide_spread, r.iv_solve_status,
        ])


# ── ATM IV helper ─────────────────────────────────────────────────────────────
def _atm_iv(rows: list[OptionRow], spot: float) -> Optional[float]:
    """Return IV of the call or put strike closest to spot."""
    candidates = [r for r in rows if r.iv and not r.stale]
    if not candidates:
        return None
    closest = min(candidates, key=lambda r: abs(r.strike - spot))
    return closest.iv


# ── Main ──────────────────────────────────────────────────────────────────────
def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fetch option chain with Greeks and IV rank",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--ticker", required=True, help="Ticker symbol (e.g. GLD, SPX, AAPL)")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dte", type=int, help="Target DTE in calendar days")
    group.add_argument("--expiry", help="Specific expiry date YYYY-MM-DD")
    parser.add_argument(
        "--delta-range",
        nargs=2,
        type=float,
        metavar=("MIN", "MAX"),
        help="Filter by abs(delta), e.g. --delta-range 0.10 0.35",
    )
    parser.add_argument(
        "--output",
        choices=["table", "json", "csv"],
        default="table",
        help="Output format (default: table)",
    )
    parser.add_argument("--no-ib", action="store_true", help="Skip IB, use yfinance only")
    args = parser.parse_args()

    ticker = args.ticker.upper()
    target_expiry = args.expiry or (date.today() + timedelta(days=args.dte)).isoformat()

    try:
        from src.core.config import load_config
        config = load_config()
    except Exception:
        config = {}

    source = "unknown"
    result = None

    if not args.no_ib:
        result = _fetch_ib(ticker, target_expiry, config)
        if result is not None:
            source = "ib"

    if result is None:
        if not args.no_ib:
            print("IB unavailable — falling back to yfinance", file=sys.stderr)
        result = _fetch_yf(ticker, target_expiry)
        if result is not None:
            source = "yfinance"

    if result is None:
        print(f"ERROR: could not fetch chain for {ticker}", file=sys.stderr)
        sys.exit(1)

    spot, rows = result

    # Compute IV rank before delta filter so ATM is always in scope
    iv_rank = _compute_iv_rank(ticker, _atm_iv(rows, spot) or 0.0)

    if args.delta_range:
        delta_min, delta_max = sorted(args.delta_range)
        rows = _filter_delta(rows, delta_min, delta_max)

    rows.sort(key=lambda r: (r.expiry, r.strike, r.right))

    expiry_used = rows[0].expiry if rows else target_expiry

    if args.output == "table":
        _print_table(rows, spot, iv_rank, source)
    elif args.output == "json":
        _print_json(rows, spot, iv_rank, ticker, expiry_used, source)
    elif args.output == "csv":
        _print_csv(rows, spot, iv_rank)


if __name__ == "__main__":
    main()
