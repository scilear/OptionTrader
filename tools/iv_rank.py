#!/usr/bin/env python3
"""
iv_rank.py — IV rank, IV percentile, and ATM term structure for any ticker.

Uses yfinance for historical data (RV proxy) and option chains.
IB Gateway used for live spot price if available.

Signals:
  IV rank > 75  → elevated   — good time to sell premium
  IV rank < 25  → depressed  — good time to buy premium

Usage:
    python tools/iv_rank.py --ticker GLD
    python tools/iv_rank.py --ticker SPX --lookback 252
    python tools/iv_rank.py --ticker AAPL --output json
    python tools/iv_rank.py --ticker GLD --no-cache
    python tools/iv_rank.py --ticker GLD --no-ib
"""

from __future__ import annotations

import argparse
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

from src.core.iv_solve import solve_iv

# ── Constants ──────────────────────────────────────────────────────────────────
RATE = 0.05
CACHE_DIR = repo_root / "data" / "cache"
CACHE_TTL_SECS = 86400  # 1 day

DTE_BUCKETS = [14, 21, 30, 60, 90]
RV_WINDOW = 21  # rolling window for realized vol computation

IV_RANK_ELEVATED = 75.0
IV_RANK_DEPRESSED = 25.0

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


# ── Helpers ────────────────────────────────────────────────────────────────────
def _safe_float(val) -> float:
    try:
        f = float(val)
        return f if not math.isnan(f) else 0.0
    except (TypeError, ValueError):
        return 0.0


def _host_reachable(host: str, port: int, timeout: float = 2.0) -> bool:
    import socket

    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


# ── Cache ──────────────────────────────────────────────────────────────────────
def _cache_path(ticker: str) -> Path:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    return CACHE_DIR / f"iv_rank_{ticker.lower()}.json"


def _load_cache(ticker: str) -> Optional[list[float]]:
    """Return cached closing prices or None if stale/missing."""
    path = _cache_path(ticker)
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text())
        if time.time() - data.get("ts", 0) > CACHE_TTL_SECS:
            return None
        return data.get("closes")
    except Exception:
        return None


def _save_cache(ticker: str, closes: list[float]) -> None:
    try:
        _cache_path(ticker).write_text(
            json.dumps({"ts": time.time(), "closes": closes})
        )
    except Exception:
        pass


# ── Historical RV series ────────────────────────────────────────────────────────
def _compute_rv_series(closes: list[float]) -> list[float]:
    """Rolling 21-day annualized realized vol from daily closes (oldest first)."""
    log_rets = [math.log(closes[i] / closes[i - 1]) for i in range(1, len(closes))]
    rv = []
    for i in range(RV_WINDOW - 1, len(log_rets)):
        window = log_rets[i - RV_WINDOW + 1 : i + 1]
        mean = sum(window) / len(window)
        variance = sum((x - mean) ** 2 for x in window) / len(window)
        rv.append(math.sqrt(variance * 252))
    return rv


def _get_closes(
    ticker: str, lookback_days: int, use_cache: bool
) -> Optional[list[float]]:
    """Return list of closing prices oldest-first, using cache when available."""
    if use_cache:
        cached = _load_cache(ticker)
        if cached:
            return cached
    try:
        import yfinance as yf

        yf_sym = _YF_SYMBOL_MAP.get(ticker, ticker)
        hist = yf.Ticker(yf_sym).history(period=f"{lookback_days}d")
        if hist.empty or len(hist) < 50:
            return None
        closes = [float(v) for v in hist["Close"]]
        if use_cache:
            _save_cache(ticker, closes)
        return closes
    except Exception:
        return None


# ── Spot via IB ────────────────────────────────────────────────────────────────
def _spot_from_ib(ticker: str, config: dict) -> Optional[float]:
    try:
        from ib_insync import IB, Index, Stock
    except ImportError:
        return None

    ib_cfg = config.get("ib", {})
    hosts = list(ib_cfg.get("hosts", []))
    preferred_hosts = ["wendy", "100.125.138.42"]
    for preferred_host in reversed(preferred_hosts):
        if preferred_host in hosts:
            hosts.remove(preferred_host)
        if "localhost" in hosts:
            localhost_idx = hosts.index("localhost") + 1
            hosts.insert(localhost_idx, preferred_host)
        else:
            hosts.append(preferred_host)
    port = ib_cfg.get("port", 7496)
    client_id = ib_cfg.get("client_id", 10) + 5
    timeout_secs = ib_cfg.get("timeout_seconds", 10)

    host = next((h for h in hosts if _host_reachable(h, port)), None)
    if host is None:
        return None

    ib = IB()
    try:
        ib.connect(host, port, clientId=client_id, timeout=timeout_secs, readonly=True)
        upper = ticker.upper()
        if upper in _IB_INDEX_INFO:
            exchange, currency = _IB_INDEX_INFO[upper]
            underlying = Index(upper, exchange, currency)
        else:
            underlying = Stock(upper, "SMART", "USD")
        ib.qualifyContracts(underlying)
        [t] = ib.reqTickers(underlying)
        for val in (t.marketPrice(), t.last, t.close):
            v = _safe_float(val)
            if v > 0:
                return v
    except Exception:
        pass
    finally:
        try:
            ib.disconnect()
        except Exception:
            pass
    return None


# ── ATM IV for a single expiry ──────────────────────────────────────────────────
def _atm_iv_from_chain(yf_ticker, expiry_str: str, spot: float) -> Optional[float]:
    """Fetch ATM call IV for an exact expiry string via a pre-created yf.Ticker."""
    try:
        chain = yf_ticker.option_chain(expiry_str)
        calls = chain.calls
        if calls is None or calls.empty:
            return None
        strikes = calls["strike"].tolist()
        if not strikes:
            return None
        atm_strike = min(strikes, key=lambda s: abs(s - spot))
        row = calls[calls["strike"] == atm_strike].iloc[0]

        bid = _safe_float(row.get("bid", 0))
        ask = _safe_float(row.get("ask", 0))
        last = _safe_float(row.get("lastPrice", 0))
        mid = (bid + ask) / 2.0 if bid + ask > 0 else last
        if mid <= 0:
            return None

        expiry_date = date.fromisoformat(expiry_str)
        t_years = max((expiry_date - date.today()).days, 0) / 365.0
        if t_years <= 0:
            return None

        iv_result = solve_iv(mid, spot, float(atm_strike), RATE, 0.0, t_years, "C")
        if iv_result and iv_result.iv and iv_result.iv > 0:
            return iv_result.iv
    except Exception:
        pass
    return None


# ── Data containers ────────────────────────────────────────────────────────────
@dataclass
class TermPoint:
    dte_target: int
    expiry: str
    dte_actual: int
    atm_iv: Optional[float]


@dataclass
class IVRankResult:
    ticker: str
    spot: float
    source: str
    lookback_days: int
    atm_iv_30d: Optional[float]
    iv_rank: Optional[float]  # (current - min) / (max - min) * 100
    iv_percentile: Optional[float]  # % of RV observations below current ATM IV
    rv_min: Optional[float]
    rv_max: Optional[float]
    rv_current: Optional[float]  # most recent rolling 21D RV
    term_structure: list[TermPoint]
    signal: str  # "elevated" | "depressed" | "neutral" | "n/a"


# ── Core computation ────────────────────────────────────────────────────────────
def compute(
    ticker: str,
    lookback_days: int,
    use_ib: bool,
    use_cache: bool,
    config: dict,
) -> IVRankResult:
    upper = ticker.upper()
    source = "yfinance"

    # ── Spot price ─────────────────────────────────────────────────────────────
    spot = 0.0
    if use_ib:
        spot = _spot_from_ib(upper, config) or 0.0
        if spot > 0:
            source = "ib"

    if spot <= 0:
        try:
            import yfinance as yf

            yf_sym = _YF_SYMBOL_MAP.get(upper, ticker)
            yf_t = yf.Ticker(yf_sym)
            fast = getattr(yf_t, "fast_info", None)
            if fast:
                v = fast.get("last_price")
                if v:
                    spot = _safe_float(v)
            if spot <= 0:
                hist = yf_t.history(period="2d")
                if not hist.empty:
                    spot = float(hist["Close"].iloc[-1])
        except Exception:
            pass

    if spot <= 0:
        raise RuntimeError(f"Cannot determine spot price for {ticker}")

    # ── Historical RV series ───────────────────────────────────────────────────
    closes = _get_closes(upper, lookback_days, use_cache)
    rv_series = _compute_rv_series(closes) if closes else []

    rv_min = float(min(rv_series)) if rv_series else None
    rv_max = float(max(rv_series)) if rv_series else None
    rv_current = float(rv_series[-1]) if rv_series else None

    # ── Option chains via yfinance ─────────────────────────────────────────────
    atm_iv_30d: Optional[float] = None
    term_structure: list[TermPoint] = []

    try:
        import yfinance as yf

        yf_sym = _YF_SYMBOL_MAP.get(upper, ticker)
        yf_t = yf.Ticker(yf_sym)
        available_dates = [date.fromisoformat(e) for e in yf_t.options]
        today = date.today()

        if available_dates:
            # 30D ATM IV for rank computation
            target_30d = today + timedelta(days=30)
            closest_30d = min(available_dates, key=lambda d: abs((d - target_30d).days))
            atm_iv_30d = _atm_iv_from_chain(yf_t, closest_30d.isoformat(), spot)

            # Term structure for each DTE bucket
            for dte_target in DTE_BUCKETS:
                target_date = today + timedelta(days=dte_target)
                closest = min(
                    available_dates, key=lambda d: abs((d - target_date).days)
                )
                expiry_str = closest.isoformat()
                dte_actual = (closest - today).days
                atm_iv = _atm_iv_from_chain(yf_t, expiry_str, spot)
                term_structure.append(
                    TermPoint(
                        dte_target=dte_target,
                        expiry=expiry_str,
                        dte_actual=dte_actual,
                        atm_iv=atm_iv,
                    )
                )
    except Exception:
        pass

    # ── IV rank and percentile ─────────────────────────────────────────────────
    iv_rank: Optional[float] = None
    iv_percentile: Optional[float] = None

    if atm_iv_30d and rv_series:
        lo, hi = min(rv_series), max(rv_series)
        if hi > lo:
            iv_rank = max(0.0, min(100.0, (atm_iv_30d - lo) / (hi - lo) * 100.0))
        n_below = sum(1 for v in rv_series if v < atm_iv_30d)
        iv_percentile = n_below / len(rv_series) * 100.0

    # ── Signal ─────────────────────────────────────────────────────────────────
    if iv_rank is None:
        signal = "n/a"
    elif iv_rank >= IV_RANK_ELEVATED:
        signal = "elevated"
    elif iv_rank <= IV_RANK_DEPRESSED:
        signal = "depressed"
    else:
        signal = "neutral"

    return IVRankResult(
        ticker=upper,
        spot=spot,
        source=source,
        lookback_days=lookback_days,
        atm_iv_30d=atm_iv_30d,
        iv_rank=iv_rank,
        iv_percentile=iv_percentile,
        rv_min=rv_min,
        rv_max=rv_max,
        rv_current=rv_current,
        term_structure=term_structure,
        signal=signal,
    )


# ── Output formatters ──────────────────────────────────────────────────────────
_SIGNAL_LABEL = {
    "elevated": " ▲  elevated  — good time to sell premium",
    "depressed": " ▼  depressed — good time to buy premium",
    "neutral": " —  neutral",
    "n/a": "",
}


def _print_table(result: IVRankResult) -> None:
    def pct(v: Optional[float], d: int = 1) -> str:
        return f"{v * 100:.{d}f}%" if v is not None else "n/a"

    def rank_str(v: Optional[float]) -> str:
        return f"{v:.1f}%" if v is not None else "n/a"

    print(f"\n{'=' * 52}")
    print(f"  IV Rank  |  {result.ticker}  |  Source: {result.source}")
    print(f"{'=' * 52}")
    print(f"  Spot:               {result.spot:.2f}")
    print(f"  30D ATM IV:         {pct(result.atm_iv_30d)}")
    print(
        f"  IV Rank  (RV px):   {rank_str(result.iv_rank)}{_SIGNAL_LABEL.get(result.signal, '')}"
    )
    print(f"  IV Pctile (RV px):  {rank_str(result.iv_percentile)}")
    if result.rv_min is not None:
        print(
            f"  RV Range ({result.lookback_days}d):    "
            f"{result.rv_min * 100:.1f}% – {result.rv_max * 100:.1f}%"
            f"  (cur: {result.rv_current * 100:.1f}%)"  # type: ignore[operator]
        )
    print()

    if result.term_structure:
        print(f"  {'DTE':>6}  {'Expiry':<12}  {'Act DTE':>7}  {'ATM IV':>8}")
        print(f"  {'-' * 6}  {'-' * 12}  {'-' * 7}  {'-' * 8}")
        for tp in result.term_structure:
            iv_str = f"{tp.atm_iv * 100:.1f}%" if tp.atm_iv else "n/a"
            print(
                f"  {tp.dte_target:>6}  {tp.expiry:<12}  {tp.dte_actual:>7}  {iv_str:>8}"
            )
    print()


def _print_json(result: IVRankResult) -> None:
    print(json.dumps(asdict(result), indent=2))


# ── Entry point ────────────────────────────────────────────────────────────────
def main() -> None:
    parser = argparse.ArgumentParser(
        description="IV rank, IV percentile, and ATM term structure",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--ticker", required=True, help="Ticker symbol (e.g. GLD, SPX, AAPL)"
    )
    parser.add_argument(
        "--lookback",
        type=int,
        default=365,
        help="Lookback in calendar days for RV history (default: 365)",
    )
    parser.add_argument(
        "--output",
        choices=["table", "json"],
        default="table",
        help="Output format (default: table)",
    )
    parser.add_argument(
        "--no-ib", action="store_true", help="Skip IB, use yfinance only"
    )
    parser.add_argument(
        "--no-cache", action="store_true", help="Re-fetch history, bypass cache"
    )
    args = parser.parse_args()

    try:
        from src.core.config import load_config

        config = load_config()
    except Exception:
        config = {}

    try:
        result = compute(
            ticker=args.ticker,
            lookback_days=args.lookback,
            use_ib=not args.no_ib,
            use_cache=not args.no_cache,
            config=config,
        )
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)

    if args.output == "table":
        _print_table(result)
    else:
        _print_json(result)


if __name__ == "__main__":
    main()
