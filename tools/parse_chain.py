#!/usr/bin/env python3
"""
Parse option chain JSON output from option_chain.py.

Usage:
    python tools/parse_chain.py --ticker TSLA --dte 11 [--width 0.15] [--mode atm|straddle|all]
    python tools/parse_chain.py --file /path/to/chain.json [--width 0.15] [--mode atm|straddle|all]

Modes:
    atm       — ATM strikes ± width% (default 15%), tabular output
    straddle  — ATM straddle price + implied move
    all       — Both
"""
import argparse
import json
import math
import subprocess
import sys
from pathlib import Path


def load_chain(ticker=None, dte=None, file=None, no_ib=False):
    if file:
        text = Path(file).read_text()
    else:
        def _fetch(force_no_ib=False):
            cmd = [sys.executable, "tools/option_chain.py", "--ticker", ticker, "--dte", str(dte), "--output", "json"]
            if force_no_ib:
                cmd.append("--no-ib")
            return subprocess.run(cmd, capture_output=True, text=True).stdout

        text = _fetch(force_no_ib=no_ib)
        if not no_ib:
            lines = text.splitlines()
            start = next((i for i, l in enumerate(lines) if l.strip().startswith("{")), 0)
            try:
                probe = json.loads("\n".join(lines[start:]))
                sample_bids = [r["bid"] for r in probe.get("rows", []) if "bid" in r]
                stale = sample_bids and sum(1 for b in sample_bids if b == -1.0) / len(sample_bids) > 0.8
                if stale:
                    print("IB data stale (market closed) — retrying with yfinance", file=sys.stderr)
                    text = _fetch(force_no_ib=True)
            except Exception:
                pass
    lines = text.splitlines()
    start = next((i for i, l in enumerate(lines) if l.strip().startswith("{")), 0)
    return json.loads("\n".join(lines[start:]))


def atm_table(data, width=0.15):
    spot = data["spot"]
    lo, hi = spot * (1 - width), spot * (1 + width)
    rows = [
        r for r in data["rows"]
        if lo <= r["strike"] <= hi
        and r.get("iv") and r["iv"] < 5
        and not r.get("wide_spread")
    ]
    rows.sort(key=lambda x: (x["strike"], x["right"]))
    header = f"{'Strike':>8} {'Type':>5} {'Bid':>7} {'Ask':>7} {'Mid':>7} {'IV':>7} {'Delta':>7} {'OI':>6} {'Vol':>6}"
    lines = [
        f"Spot: {spot:.2f}  |  Expiry: {data['expiry']}  |  Source: {data['source']}",
        "",
        header,
    ]
    for r in rows:
        lines.append(
            f"{r['strike']:>8.0f} {r['right']:>5} {r['bid']:>7.2f} {r['ask']:>7.2f} {r['mid']:>7.2f} "
            f"{r['iv']:>7.1%} {(r['delta'] or 0):>7.3f} {r['oi']:>6} {r['volume']:>6}"
        )
    return "\n".join(lines)


def straddle_summary(data):
    spot = data["spot"]
    strikes = sorted(set(r["strike"] for r in data["rows"]))
    def _clean(right):
        return sorted(
            [r for r in data["rows"] if r["right"] == right and r.get("iv") and r["iv"] < 5 and not r.get("wide_spread")],
            key=lambda r: abs(r["strike"] - spot)
        )

    calls = _clean("C")
    puts = _clean("P")
    if not calls or not puts:
        return "Could not find any strike with clean call+put IV"

    call = calls[0]
    put = puts[0]
    atm_strike = call["strike"]

    straddle_mid = call["mid"] + put["mid"]
    straddle_bid = call["bid"] + put["bid"]
    straddle_ask = call["ask"] + put["ask"]
    implied_move_pct = straddle_mid / spot * 100
    implied_move_pts = straddle_mid

    # 1-SD expected move approximation: straddle ≈ 0.68 * spot * IV * sqrt(T)
    call_iv = call.get("iv", 0)
    dte = data.get("dte_actual") or 11  # fallback

    strike_note = f"{call['strike']:.0f}C / {put['strike']:.0f}P" if call["strike"] != put["strike"] else f"{atm_strike:.0f}"
    lines = [
        f"ATM Straddle — {data['ticker']} | Expiry: {data['expiry']} | Spot: {spot:.2f}",
        f"  ATM Strike:      {strike_note}",
        f"  Straddle mid:    ${straddle_mid:.2f}  (bid ${straddle_bid:.2f} / ask ${straddle_ask:.2f})",
        f"  Implied move:    ±{implied_move_pct:.1f}%  (±${implied_move_pts:.2f})",
        f"  Call IV:         {call_iv:.1%}  |  Put IV: {put.get('iv', 0):.1%}",
        f"  Call delta:      {call.get('delta', 0):.3f}  |  Put delta: {put.get('delta', 0):.3f}",
    ]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ticker", default=None)
    parser.add_argument("--dte", type=int, default=11)
    parser.add_argument("--file", default=None)
    parser.add_argument("--width", type=float, default=0.15, help="ATM band ±% (default 0.15)")
    parser.add_argument("--mode", choices=["atm", "straddle", "all"], default="all")
    parser.add_argument("--no-ib", action="store_true", help="Skip IB, use yfinance only")
    args = parser.parse_args()

    if not args.ticker and not args.file:
        print("ERROR: provide --ticker or --file", file=sys.stderr)
        sys.exit(1)

    data = load_chain(ticker=args.ticker, dte=args.dte, file=args.file, no_ib=args.no_ib)
    if "ticker" not in data and args.ticker:
        data["ticker"] = args.ticker

    if args.mode in ("straddle", "all"):
        print(straddle_summary(data))
        print()
    if args.mode in ("atm", "all"):
        print(atm_table(data, width=args.width))


if __name__ == "__main__":
    main()
