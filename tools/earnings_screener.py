#!/usr/bin/env python3
"""
Batch earnings vol screener.

Usage:
    python tools/earnings_screener.py --tickers MSFT GOOGL AMZN META AAPL --dte 9
    python tools/earnings_screener.py --tickers MSFT GOOGL --dte 9 --mode full

Modes:
    summary  — IV rank, IV%, front IV, RV, implied move, signal (default)
    full     — summary + straddle price detail
"""
import argparse
import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed


def fetch_iv_rank(ticker):
    r = subprocess.run(
        [sys.executable, "tools/iv_rank.py", "--ticker", ticker, "--output", "json"],
        capture_output=True, text=True
    )
    lines = r.stdout.splitlines()
    start = next((i for i, l in enumerate(lines) if l.strip().startswith("{")), 0)
    return json.loads("\n".join(lines[start:]))


def fetch_straddle(ticker, dte):
    """Returns (straddle_mid, implied_move_pct, call_iv, front_iv_dte) or None."""
    cmd = [sys.executable, "tools/option_chain.py", "--ticker", ticker, "--dte", str(dte), "--output", "json"]
    r = subprocess.run(cmd, capture_output=True, text=True)
    lines = r.stdout.splitlines()
    start = next((i for i, l in enumerate(lines) if l.strip().startswith("{")), 0)
    try:
        data = json.loads("\n".join(lines[start:]))
    except Exception:
        return None

    # Stale IB detection
    bids = [row["bid"] for row in data.get("rows", []) if "bid" in row]
    if bids and sum(1 for b in bids if b == -1.0) / len(bids) > 0.8:
        cmd.append("--no-ib")
        r = subprocess.run(cmd, capture_output=True, text=True)
        lines = r.stdout.splitlines()
        start = next((i for i, l in enumerate(lines) if l.strip().startswith("{")), 0)
        try:
            data = json.loads("\n".join(lines[start:]))
        except Exception:
            return None

    spot = data["spot"]

    def _clean(right):
        return sorted(
            [row for row in data["rows"] if row["right"] == right
             and row.get("iv") and row["iv"] < 5 and not row.get("wide_spread")],
            key=lambda row: abs(row["strike"] - spot)
        )

    calls, puts = _clean("C"), _clean("P")
    if not calls or not puts:
        return None

    call, put = calls[0], puts[0]
    mid = call["mid"] + put["mid"]
    return {
        "straddle_mid": mid,
        "implied_move_pct": mid / spot * 100,
        "call_iv": call.get("iv", 0),
        "put_iv": put.get("iv", 0),
        "call_strike": call["strike"],
        "put_strike": put["strike"],
        "expiry": data["expiry"],
        "spot": spot,
    }


def analyze_ticker(ticker, dte):
    try:
        iv = fetch_iv_rank(ticker)
        straddle = fetch_straddle(ticker, dte)
        return ticker, iv, straddle, None
    except Exception as e:
        return ticker, None, None, str(e)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tickers", nargs="+", required=True)
    parser.add_argument("--dte", type=int, default=9)
    parser.add_argument("--mode", choices=["summary", "full"], default="summary")
    parser.add_argument("--sort", choices=["iv_rank", "implied_move", "ticker"], default="iv_rank")
    args = parser.parse_args()

    print(f"Screening {len(args.tickers)} tickers | DTE target: {args.dte} | fetching...\n")

    results = []
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = {pool.submit(analyze_ticker, t, args.dte): t for t in args.tickers}
        for f in as_completed(futures):
            results.append(f.result())

    # Sort
    def sort_key(r):
        ticker, iv, straddle, err = r
        if err or not iv:
            return 999
        if args.sort == "iv_rank":
            return iv.get("iv_rank", 999)
        if args.sort == "implied_move":
            return -(straddle["implied_move_pct"] if straddle else 0)
        return ticker

    results.sort(key=sort_key)

    # Header
    if args.mode == "summary":
        print(f"{'Ticker':<7} {'Spot':>8} {'IVR':>5} {'IV%':>5} {'FrontIV':>8} {'RV':>7} {'IV/RV':>6} {'±Move':>7} {'Signal':<10} {'Expiry'}")
        print("-" * 90)
    else:
        print(f"{'Ticker':<7} {'Spot':>8} {'IVR':>5} {'IV%':>5} {'FrontIV':>8} {'RV':>7} {'IV/RV':>6} {'±Move':>7} {'Straddle':>9} {'Signal':<10} {'Expiry'}")
        print("-" * 100)

    for ticker, iv, straddle, err in results:
        if err:
            print(f"{ticker:<7}  ERROR: {err}")
            continue
        if not iv:
            print(f"{ticker:<7}  no IV data")
            continue

        spot = iv.get("spot", 0)
        ivr = iv.get("iv_rank", 0)
        ivpct = iv.get("iv_percentile", 0)
        rv = iv.get("rv_current", 0)
        signal = iv.get("signal", "")

        # Front IV from term structure (nearest DTE)
        ts = iv.get("term_structure", [])
        front = min(ts, key=lambda x: abs(x["dte_actual"] - args.dte)) if ts else None
        front_iv = front["atm_iv"] if front else None
        iv_rv = (front_iv / rv) if front_iv and rv else None

        move = straddle["implied_move_pct"] if straddle else None
        expiry = straddle["expiry"] if straddle else "—"

        if args.mode == "summary":
            print(
                f"{ticker:<7} {spot:>8.2f} {ivr:>5.1f} {ivpct:>5.1f} "
                f"{front_iv:>7.1%} {rv:>7.1%} "
                f"{iv_rv:>6.2f} "
                f"{'±'+f'{move:.1f}%' if move else '—':>7} "
                f"{signal:<10} {expiry}"
            )
        else:
            sm = straddle["straddle_mid"] if straddle else None
            print(
                f"{ticker:<7} {spot:>8.2f} {ivr:>5.1f} {ivpct:>5.1f} "
                f"{front_iv:>7.1%} {rv:>7.1%} "
                f"{iv_rv:>6.2f} "
                f"{'±'+f'{move:.1f}%' if move else '—':>7} "
                f"{'$'+f'{sm:.2f}' if sm else '—':>9} "
                f"{signal:<10} {expiry}"
            )

    print()
    print("IVR=IV Rank (0-100) | IV%=IV Percentile | IV/RV=front IV over realized vol")
    print("Pre-earnings long vol gate: IVR ≤ 60. IV/RV < 1.2 = vol not overpriced.")


if __name__ == "__main__":
    main()
