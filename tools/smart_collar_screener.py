#!/usr/bin/env python3
"""
Smart Collar Screener — find LEAP collar opportunities with positive downside floor.

Strategy:
  Long 100 shares
  Long 1 ITM put (K_p > spot)
  Short 1 OTM call (K_c > K_p > spot)

At expiry:
  S_T ≤ K_p → value = K_p per share (put floor)
  K_p < S_T < K_c → value = S_T per share
  S_T ≥ K_c → value = K_c per share (call cap)

We require min return (below put strike) to be positive, i.e.
  K_p > S_0 + put_mid − call_mid

Ranking: annualized_max_return / ((K_c − S_0) / S_0)

Usage:
  python tools/smart_collar_screener.py --test                           # SPY only
  python tools/smart_collar_screener.py --top 10                        # full universe, top 10
  python tools/smart_collar_screener.py --tickers AAPL MSFT             # specific
  python tools/smart_collar_screener.py --min-dte 200 --max-dte 365     # DTE range
  python tools/smart_collar_screener.py --per-expiry --top 5            # top 5 per expiry
  python tools/smart_collar_screener.py --rerun-top 20                  # drill into top 20 tickers by maxR%
  python tools/smart_collar_screener.py --max-spot 1000                 # skip expensive tickers (e.g. BRK-A)

The ticker summary (one best collar per ticker) is auto-saved to smart_collar_tickers.csv
after each run. Use --rerun-top N on a subsequent run to screen only the top N tickers
by max return — avoids re-scanning low-opportunity tickers.
"""

from __future__ import annotations

import argparse
import csv
import math
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

import pandas as pd

# ── Ticker universe sources ─────────────────────────────────────────────────────


def _fetch_wikipedia_table(url: str, table_index: int = 0) -> list[str]:
    """Scrape a Wikipedia table for ticker symbols (first column)."""
    import json
    import urllib.request

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        raw = urllib.request.urlopen(req, timeout=15).read().decode("utf-8")
    except Exception:
        return []

    # Quick parse: extract <table class="wikitable"> ... </table>
    import re

    tables = re.findall(r"<table[^>]*wikitable[^>]*>(.*?)</table>", raw, re.DOTALL)
    if not tables:
        return []
    table_html = tables[min(table_index, len(tables) - 1)]
    rows = re.findall(r"<tr>(.*?)</tr>", table_html, re.DOTALL)

    tickers: list[str] = []
    for row in rows:
        cells = re.findall(r"<td>(.*?)</td>", row, re.DOTALL)
        if cells:
            raw_ticker = re.sub(r"<[^>]+>", "", cells[0]).strip()
            raw_ticker = raw_ticker.replace("&amp;", "&").split("/")[0].strip()
            # yfinance tickers: handle BRK.B → BRK-B, BF.B → BF-B, etc.
            raw_ticker = raw_ticker.replace(".", "-")
            if raw_ticker and raw_ticker not in ("^", "", "Symbol"):
                # Skip non-ticker stuff
                if len(raw_ticker) <= 5 and raw_ticker.isalnum() or "-" in raw_ticker:
                    tickers.append(raw_ticker)
    return tickers


NDX_WIKI = "https://en.wikipedia.org/wiki/Nasdaq-100"
SP500_WIKI = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"

TOP_20_ETFS = [
    "SPY", "IVV", "VOO", "VTI", "QQQ", "IWM", "VEA", "VWO",
    "AGG", "BND", "GLD", "SLV", "TLT", "IEFA", "EEM", "EFA",
    "HYG", "LQD", "XLF", "XLE",
]


def build_ticker_universe() -> list[str]:
    tickers: set[str] = set()

    ndx = _fetch_wikipedia_table(NDX_WIKI, table_index=4)
    sp5 = _fetch_wikipedia_table(SP500_WIKI, table_index=0)
    tickers.update(ndx)
    tickers.update(sp5)
    tickers.update(TOP_20_ETFS)

    # Remove known non-stock entries
    bad = {"", "^", "—", "Symbol", "Ticker", "Name", "Security"}
    tickers -= bad

    result = sorted(tickers)
    print(f"Universe: {len(result)} tickers (NDX {len(ndx)} + SPX {len(sp5)} + ETFs {len(TOP_20_ETFS)}, deduped)", file=sys.stderr)
    return result


# ── yfinance helpers ────────────────────────────────────────────────────────────


def _safe_float(val: Any) -> float:
    try:
        v = float(val)
        return v if math.isfinite(v) else 0.0
    except (TypeError, ValueError, OverflowError):
        return 0.0


def get_spot_and_chains(
    ticker: str, min_dte: int = 170, max_dte: int = 0
) -> list[dict[str, Any]]:
    """Get spot + all option chains with DTE in [min_dte, max_dte] for a ticker.

    max_dte=0 means no upper bound.
    Returns list of dicts:
      {expiry, dte, spot, calls: DataFrame, puts: DataFrame}
    or empty list on failure.
    """
    try:
        import yfinance as yf
    except ImportError:
        print("yfinance not installed", file=sys.stderr)
        return []

    yf_ticker = yf.Ticker(ticker)
    spot = 0.0

    # Try fast_info first
    try:
        fi = yf_ticker.fast_info
        spot = _safe_float(getattr(fi, "last_price", 0) or fi.get("regularMarketPrice", 0) or fi.get("lastPrice", 0))
    except Exception:
        pass

    # Fallback: 1d history
    if spot <= 0:
        try:
            hist = yf_ticker.history(period="1d")
            if not hist.empty:
                spot = float(hist["Close"].iloc[-1])
        except Exception:
            pass
    if spot <= 0:
        return []

    # Get available expiries
    try:
        raw_expiries: list[str] = list(yf_ticker.options)
    except Exception:
        return []
    if not raw_expiries:
        return []

    today = date.today()
    chains: list[dict[str, Any]] = []

    for expiry_str in raw_expiries:
        expiry_date = date.fromisoformat(expiry_str)
        dte = (expiry_date - today).days
        if dte < min_dte:
            continue
        if max_dte > 0 and dte > max_dte:
            continue

        try:
            chain = yf_ticker.option_chain(expiry_str)
        except Exception:
            continue
        if chain.calls is None or chain.puts is None:
            continue
        if chain.calls.empty or chain.puts.empty:
            continue

        chains.append({
            "expiry": expiry_str,
            "dte": dte,
            "spot": spot,
            "calls": chain.calls,
            "puts": chain.puts,
        })

    return chains


# ── Smart collar analysis ───────────────────────────────────────────────────────


def analyze_collar_for_chain(chain: dict[str, Any]) -> list[dict[str, Any]]:
    """Analyze all put/call strike combinations for one expiry chain.

    Returns list of candidate dicts sorted by ratio descending.
    """
    spot = chain["spot"]
    calls_df: pd.DataFrame = chain["calls"]
    puts_df: pd.DataFrame = chain["puts"]
    dte = chain["dte"]
    expiry = chain["expiry"]

    candidates: list[dict[str, Any]] = []

    # Get valid ITM put strikes (strike > spot), limit to 50% ITM
    put_rows = puts_df[
        (puts_df["strike"] > spot) & (puts_df["strike"] <= spot * 1.50)
    ].copy()
    if put_rows.empty:
        return []

    # Get valid OTM call strikes (strike > spot), limit to 100% OTM  
    call_rows = calls_df[
        (calls_df["strike"] > spot) & (calls_df["strike"] <= spot * 2.0)
    ].copy()
    if call_rows.empty:
        return []

    # Sort for deterministic iteration
    put_rows = put_rows.sort_values("strike")
    call_rows = call_rows.sort_values("strike")

    for _, put_row in put_rows.iterrows():
        put_strike = _safe_float(put_row["strike"])
        put_bid = _safe_float(put_row["bid"])
        put_ask = _safe_float(put_row["ask"])
        if put_bid > 0 and put_ask > 0:
            put_mid = (put_bid + put_ask) / 2.0
        elif put_bid > 0 or put_ask > 0:
            put_mid = _safe_float(put_row.get("lastPrice", 0))
        else:
            continue
        if put_mid <= 0:
            continue

        for _, call_row in call_rows.iterrows():
            call_strike = _safe_float(call_row["strike"])
            if call_strike <= put_strike:
                continue

            call_bid = _safe_float(call_row["bid"])
            call_ask = _safe_float(call_row["ask"])
            if call_bid > 0 and call_ask > 0:
                call_mid = (call_bid + call_ask) / 2.0
            elif call_bid > 0 or call_ask > 0:
                call_mid = _safe_float(call_row.get("lastPrice", 0))
            else:
                continue
            if call_mid <= 0:
                continue

            result = _collar_metrics(
                spot=spot,
                put_strike=put_strike,
                put_mid=put_mid,
                call_strike=call_strike,
                call_mid=call_mid,
                dte=dte,
                expiry=expiry,
            )
            if result is not None:
                candidates.append(result)

    candidates.sort(key=lambda c: c["ratio"], reverse=True)
    return candidates


def _collar_metrics(
    spot: float,
    put_strike: float,
    put_mid: float,
    call_strike: float,
    call_mid: float,
    dte: int,
    expiry: str,
) -> dict[str, Any] | None:
    """Compute smart collar P&L metrics.

    Position: +100 shares @ spot, +1 ITM put, -1 OTM call (per share basis)
    Net cost per share = spot + put_mid - call_mid
    """
    net_cost_per_share = spot + put_mid - call_mid
    if net_cost_per_share <= 0:
        return None

    # Sanity: net cost must be at least 10% of spot (avoid mid-price artifacts
    # where deep ITM put + far OTM call mid-prices create near-zero cost)
    if net_cost_per_share < 0.10 * spot:
        return None

    # Min return: at expiry S_T <= put_strike → value = put_strike
    min_return = (put_strike - net_cost_per_share) / net_cost_per_share
    if min_return <= 0:
        return None

    # Max return: at expiry S_T >= call_strike → value = call_strike
    max_return = (call_strike - net_cost_per_share) / net_cost_per_share

    # Annualized max return (compound)
    years = dte / 365.0
    annualized_return = (1.0 + max_return) ** (1.0 / years) - 1.0

    # Cap annualized at 100% — beyond that it's a data artifact
    if annualized_return > 1.0:
        return None

    # Call OTM % above current price (must be at least 0.1% to avoid div-by-zero)
    call_otm_pct = (call_strike - spot) / spot
    if call_otm_pct < 0.001:
        return None

    # Ratio: annualized return per unit of upside cap
    ratio = annualized_return / call_otm_pct

    return {
        "ticker": "",
        "expiry": expiry,
        "dte": dte,
        "spot": spot,
        "put_strike": round(put_strike, 2),
        "put_mid": round(put_mid, 2),
        "call_strike": round(call_strike, 2),
        "call_mid": round(call_mid, 2),
        "net_cost_per_share": round(net_cost_per_share, 2),
        "min_return_pct": round(min_return * 100, 2),
        "max_return_pct": round(max_return * 100, 2),
        "annualized_return_pct": round(annualized_return * 100, 2),
        "call_otm_pct": round(call_otm_pct * 100, 2),
        "ratio": round(ratio, 4),
    }


# ── Per-ticker screening ────────────────────────────────────────────────────────


def screen_ticker(
    ticker: str, min_dte: int = 170, max_dte: int = 0, delay: float = 0.0,
    min_spot: float = 0.0, max_spot: float = 0.0,
) -> list[dict[str, Any]]:
    """Screen one ticker for all smart collar opportunities."""
    if delay > 0:
        time.sleep(delay)
    chains = get_spot_and_chains(ticker, min_dte=min_dte, max_dte=max_dte)
    if not chains:
        return []
    spot = chains[0]["spot"]
    if min_spot > 0 and spot < min_spot:
        return []
    if max_spot > 0 and spot > max_spot:
        return []

    all_candidates: list[dict[str, Any]] = []
    for chain in chains:
        candidates = analyze_collar_for_chain(chain)
        for c in candidates:
            c["ticker"] = ticker
        all_candidates.extend(candidates)

    all_candidates.sort(key=lambda c: c["ratio"], reverse=True)
    return all_candidates


# ── Reporting ───────────────────────────────────────────────────────────────────


def print_results(results: list[dict[str, Any]], top_n: int = 0) -> None:
    """Print formatted results table."""
    if top_n > 0:
        results = results[:top_n]

    if not results:
        print("\nNo smart collar opportunities found.")
        return

    header = (
        f"{'Ticker':<7} {'Expiry':<12} {'DTE':>4} {'Spot':>8} "
        f"{'PutStr':>8} {'Put$':>7} {'CallStr':>8} {'Call$':>7} "
        f"{'NetCost':>8} {'MinR%':>7} {'MaxR%':>7} {'AnnR%':>7} "
        f"{'OTM%':>7} {'Ratio':>7}"
    )
    sep = "─" * len(header.expandtabs())
    print(f"\n{header}")
    print(sep)

    for r in results:
        print(
            f"{r['ticker']:<7} {r['expiry']:<12} {r['dte']:>4} {r['spot']:>8.2f} "
            f"{r['put_strike']:>8.2f} {r['put_mid']:>7.2f} {r['call_strike']:>8.2f} {r['call_mid']:>7.2f} "
            f"{r['net_cost_per_share']:>8.2f} {r['min_return_pct']:>7.2f} {r['max_return_pct']:>7.2f} "
            f"{r['annualized_return_pct']:>7.2f} {r['call_otm_pct']:>7.2f} {r['ratio']:>7.4f}"
        )

    print(f"\n{len(results)} opportunities shown.")


# ── Main ────────────────────────────────────────────────────────────────────────


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Smart Collar LEAP Screener",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--test", action="store_true", help="Test mode: SPY only"
    )
    parser.add_argument(
        "--tickers", nargs="+", help="Specific tickers to screen"
    )
    parser.add_argument(
        "--top", type=int, default=10, help="Show top N results (default: 10)"
    )
    parser.add_argument(
        "--min-dte", type=int, default=170, help="Minimum DTE (default: 170)"
    )
    parser.add_argument(
        "--max-dte", type=int, default=0,
        help="Maximum DTE (default: 0 = no upper bound)"
    )
    parser.add_argument(
        "--per-expiry", action="store_true",
        help="Show top N results per expiry instead of globally"
    )
    parser.add_argument(
        "--rerun-top", type=int, default=0,
        help="Re-run only the top N tickers by max return from the previous run's saved ranking (reads smart_collar_tickers.csv)"
    )
    parser.add_argument(
        "--min-spot", type=float, default=0,
        help="Minimum spot price (default: 0 = no filter)"
    )
    parser.add_argument(
        "--max-spot", type=float, default=0,
        help="Maximum spot price (default: 0 = no filter)"
    )
    parser.add_argument(
        "--max-workers", type=int, default=4,
        help="Parallel fetch workers (default: 4)"
    )
    parser.add_argument(
        "--ticker-delay", type=float, default=0.25,
        help="Delay in seconds between ticker submissions to avoid rate limits (default: 0.25)"
    )
    args = parser.parse_args()

    # Build ticker list
    if args.tickers:
        tickers = args.tickers
    elif args.test:
        tickers = ["SPY"]
        print("TEST MODE: SPY only\n", file=sys.stderr)
    else:
        tickers = build_ticker_universe()

    # --rerun-top: load previous ticker ranking, keep only the top N by maxR%
    ticker_summary_path = Path(__file__).parent / "smart_collar_tickers.csv"
    if args.rerun_top > 0:
        if not ticker_summary_path.exists():
            print(f"ERROR: {ticker_summary_path} not found — run a full screen first to build a ranking.", file=sys.stderr)
            sys.exit(1)
        ranked: list[tuple[str, float]] = []
        with open(ticker_summary_path, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                ticker = row.get("ticker", "").strip()
                maxr = float(row.get("best_maxR_pct", 0) or 0)
                if ticker:
                    ranked.append((ticker, maxr))
        if not ranked:
            print("ERROR: ticker summary file is empty.", file=sys.stderr)
            sys.exit(1)
        ranked.sort(key=lambda x: x[1], reverse=True)
        top_tickers = [t for t, _ in ranked[:args.rerun_top]]
        print(f"Rerun mode: {len(tickers)} in universe → keeping only top {len(top_tickers)} by maxR% from {ticker_summary_path.name}", file=sys.stderr)
        tickers = top_tickers

    max_dte_str = f" | max DTE: {args.max_dte}" if args.max_dte else ""
    spot_str = ""
    if args.min_spot:
        spot_str += f" | min spot: ${args.min_spot:,.0f}"
    if args.max_spot:
        spot_str += f" | max spot: ${args.max_spot:,.0f}"
    print(f" Screening {len(tickers)} tickers | min DTE: {args.min_dte}{max_dte_str}{spot_str} | workers: {args.max_workers} | delay: {args.ticker_delay}s\n", file=sys.stderr)

    all_results: list[dict[str, Any]] = []
    start = time.time()

    with ThreadPoolExecutor(max_workers=args.max_workers) as pool:
        fut_map: dict[Any, str] = {}
        for t in tickers:
            fut = pool.submit(screen_ticker, t, args.min_dte, args.max_dte, args.ticker_delay, args.min_spot, args.max_spot)
            fut_map[fut] = t
            if args.ticker_delay > 0:
                time.sleep(args.ticker_delay)
        done = 0
        for f in as_completed(fut_map):
            t = fut_map[f]
            done += 1
            try:
                cands = f.result()
                if cands:
                    all_results.extend(cands)
                    best = cands[0]
                    print(
                        f"  [{done}/{len(tickers)}] {t}: {len(cands)} collar(s), "
                        f"best ratio={best['ratio']:.4f} annR={best['annualized_return_pct']:.2f}% "
                        f"exp={best['expiry']}",
                        file=sys.stderr,
                    )
                else:
                    print(f"  [{done}/{len(tickers)}] {t}: no collars pass", file=sys.stderr)
            except Exception as e:
                print(f"  [{done}/{len(tickers)}] {t}: ERROR {e}", file=sys.stderr)

    elapsed = time.time() - start

    # Sort all by ratio
    all_results.sort(key=lambda c: c["ratio"], reverse=True)

    print(f"\n{'='*80}", file=sys.stderr)
    print(f" Total collars found: {len(all_results)} across all tickers", file=sys.stderr)
    print(f" Elapsed: {elapsed:.1f}s", file=sys.stderr)

    if args.per_expiry:
        # Group by expiry, show top N per expiry
        from itertools import groupby
        all_results.sort(key=lambda c: (c["expiry"], -c["ratio"]))
        print(f"\n═══ TOP {args.top} PER EXPIRY ═══")
        for exp, group in groupby(all_results, key=lambda c: c["expiry"]):
            group_list = list(group)
            print(f"\n── {exp} (DTE {group_list[0]['dte']}) [{len(group_list)} collars] ──")
            print_results(group_list, top_n=args.top)
    elif args.top:
        # Top N collars displayed in AnnR% buckets, sorted by ratio within each bucket
        bucket_ceilings = [(100, "≥ 90%"), (90, "80–90%"), (80, "70–80%"), (70, "60–70%"),
                           (60, "50–60%"), (50, "40–50%"), (40, "30–40%"), (30, "20–30%"),
                           (20, "10–20%"), (10, "0–10%")]
        top_results = all_results[:args.top]
        print(f"\n═══ TOP {args.top} SMART COLLAR OPPORTUNITIES (bucketed by AnnR%) ═══")
        header = (
            f"{'Ticker':<7} {'Expiry':<12} {'DTE':>4} {'Spot':>8} "
            f"{'PutStr':>8} {'Put$':>7} {'CallStr':>8} {'Call$':>7} "
            f"{'NetCost':>8} {'MinR%':>7} {'MaxR%':>7} {'AnnR%':>7} "
            f"{'OTM%':>7} {'Ratio':>7}"
        )
        for ceil, label in bucket_ceilings:
            lo = ceil - 10 if ceil < 100 else 90
            bucket = [r for r in top_results if lo <= r["annualized_return_pct"] < ceil]
            if not bucket:
                continue
            print(f"\n── AnnR% {label} ({len(bucket)} collar{'s' if len(bucket) > 1 else ''}) ──")
            print(header)
            print("─" * len(header.expandtabs()))
            for r in bucket:
                print(
                    f"{r['ticker']:<7} {r['expiry']:<12} {r['dte']:>4} {r['spot']:>8.2f} "
                    f"{r['put_strike']:>8.2f} {r['put_mid']:>7.2f} {r['call_strike']:>8.2f} {r['call_mid']:>7.2f} "
                    f"{r['net_cost_per_share']:>8.2f} {r['min_return_pct']:>7.2f} {r['max_return_pct']:>7.2f} "
                    f"{r['annualized_return_pct']:>7.2f} {r['call_otm_pct']:>7.2f} {r['ratio']:>7.4f}"
                )
    else:
        print_results(all_results)

    # ── Ticker-level summary (for CSV save) ───────────────────────────────────
    ticker_best: dict[str, dict[str, Any]] = {}
    for r in all_results:
        t = r["ticker"]
        if t not in ticker_best or r["ratio"] > ticker_best[t]["ratio"]:
            ticker_best[t] = r

    # ── Save ticker summary to CSV (read by --rerun-top) ─────────────────────
    with open(ticker_summary_path, "w", newline="") as f:
        fieldnames = [
            "ticker", "best_maxR_pct", "best_annR_pct", "best_ratio",
            "expiry", "dte", "spot",
            "put_strike", "put_mid", "call_strike", "call_mid",
            "net_cost_per_share", "min_return_pct",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in ticker_best.values():
            writer.writerow({
                "ticker": r["ticker"],
                "best_maxR_pct": r["max_return_pct"],
                "best_annR_pct": r["annualized_return_pct"],
                "best_ratio": r["ratio"],
                "expiry": r["expiry"],
                "dte": r["dte"],
                "spot": r["spot"],
                "put_strike": r["put_strike"],
                "put_mid": r["put_mid"],
                "call_strike": r["call_strike"],
                "call_mid": r["call_mid"],
                "net_cost_per_share": r["net_cost_per_share"],
                "min_return_pct": r["min_return_pct"],
            })
    print(f"\nTicker summary saved to {ticker_summary_path} ({len(ticker_best)} tickers)", file=sys.stderr)


if __name__ == "__main__":
    main()
