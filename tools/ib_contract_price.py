#!/usr/bin/env python3
"""
ib_contract_price.py — Fetch live bid/ask/Greeks for specific option contracts from IB.

Usage:
    python tools/ib_contract_price.py --ticker SPX --legs "2025-06-20|4800|C,2025-06-20|4900|P"
    python tools/ib_contract_price.py --ticker SPY --legs "2025-06-20|450|C"

Output: JSON array with bid/ask/mid/last/iv/delta/gamma/vega/theta per leg.
"""

from __future__ import annotations

import json
import math
import os
import socket
import sys
import time
from datetime import date
from pathlib import Path
from typing import Any

repo_root = Path(__file__).resolve().parents[1]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from src.core.iv_solve import solve_iv, bs_greeks

import logging
logging.getLogger("ib_insync.wrapper").setLevel(logging.CRITICAL)
logging.getLogger("ib_insync.ib").setLevel(logging.CRITICAL)

# Constants matching option_chain.py
RATE = 0.05
MAX_CLIENT_ID_RETRIES = 8
BATCH_SIZE = 30

_IB_INDEX_INFO: dict[str, tuple[str, str]] = {
    "ESTX50": ("EUREX", "EUR"),
    "DAX": ("EUREX", "EUR"),
    "CAC40": ("MONEP", "EUR"),
    "Z": ("ICEEU", "GBP"),
    "SMI": ("EUREX", "CHF"),
    "EOE": ("FTA", "EUR"),
    "IBEX": ("MEFFRV", "EUR"),
    "SPX": ("CBOE", "USD"),
    "NDX": ("NASDAQ", "USD"),
    "RUT": ("RUSSELL", "USD"),
    "VIX": ("CBOE", "USD"),
    "XSP": ("CBOE", "USD"),
}
_IB_INDEX_ALIASES: dict[str, str] = {
    "SX5E": "ESTX50",
    "EUROSTOXX": "ESTX50",
    "EUROSTOXX50": "ESTX50",
    "FTSE": "Z",
    "FTSE100": "Z",
    "UKX": "Z",
    "AEX": "EOE",
    "IBEX35": "IBEX",
}

def _safe_float(val: Any) -> float:
    try:
        f = float(val)
        return f if not math.isnan(f) else 0.0
    except (TypeError, ValueError):
        return 0.0

def _host_reachable(host: str, port: int, timeout: float = 2.0) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False

def _client_id_candidates(base_id: int, attempts: int) -> list[int]:
    if attempts <= 1:
        return [base_id]
    seed = ((os.getpid() << 8) ^ int(time.time() * 1000)) & 0x7FFFFFFF
    alt_start = 100 + (seed % 20000)
    ids = [base_id]
    ids.extend(alt_start + i for i in range(attempts - 1))
    return ids

def _parse_legs(legs_arg: str) -> list[dict[str, Any]]:
    legs: list[dict[str, Any]] = []
    for part in legs_arg.split(","):
        part = part.strip()
        fields = part.split("|")
        if len(fields) != 3:
            print(f"Invalid leg: {part}", file=sys.stderr)
            continue
        expiry_str, strike_str, right = fields
        legs.append({
            "expiry": expiry_str.strip(),
            "strike": float(strike_str.strip()),
            "right": right.strip().upper(),
        })
    return legs

def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="Fetch IB prices for specific option contracts")
    parser.add_argument("--ticker", required=True, help="Underlying ticker")
    parser.add_argument("--legs", required=True, help="Comma-separated legs: expiry|strike|right,expiry|strike|right")
    parser.add_argument("--spot", type=float, default=None, help="Spot price (will fetch from IB if not provided)")
    args = parser.parse_args()

    legs = _parse_legs(args.legs)
    if not legs:
        print(json.dumps({"error": "No valid legs", "prices": []}))
        sys.exit(1)

    from ib_insync import IB, Index, Stock, Option

    ib_config = {
        "hosts": ["wendy", "100.125.138.42", "localhost"],
        "port": 7496,
        "client_id": 15,
        "timeout_seconds": 15,
    }

    hosts: list[str] = list(ib_config.get("hosts", []))
    port: int = ib_config.get("port", 7496)
    client_id: int = ib_config.get("client_id", 10) + 5
    timeout_secs: int = ib_config.get("timeout_seconds", 15)

    host_used = next((h for h in hosts if _host_reachable(h, port, timeout=2.0)), None)
    if host_used is None:
        print(json.dumps({"error": "No IB host reachable", "prices": []}))
        sys.exit(1)

    ib: IB | None = None
    try:
        connect_errors: list[str] = []
        for trial_client_id in _client_id_candidates(client_id, MAX_CLIENT_ID_RETRIES):
            ib = IB()
            try:
                ib.connect(host_used, port, clientId=trial_client_id, timeout=timeout_secs, readonly=True)
                break
            except Exception as exc:
                connect_errors.append(f"clientId {trial_client_id}: {exc}")
                try:
                    ib.disconnect()
                except Exception:
                    pass
                ib = None

        if ib is None or not ib.isConnected():
            err_msg = "IB connect retries exhausted: " + " | ".join(connect_errors) if connect_errors else "IB not connected"
            print(json.dumps({"error": err_msg, "prices": []}))
            sys.exit(1)

        ib.reqMarketDataType(3)

        upper = args.ticker.upper()
        index_symbol = _IB_INDEX_ALIASES.get(upper, upper)
        if index_symbol in _IB_INDEX_INFO:
            exchange, currency = _IB_INDEX_INFO[index_symbol]
            underlying = Index(index_symbol, exchange, currency)
            sec_type = "IND"
        else:
            underlying = Stock(upper, "SMART", "USD")
            index_symbol = upper
            currency = "USD"
            sec_type = "STK"

        ib.qualifyContracts(underlying)

        # Get spot if not provided
        spot = args.spot
        if spot is None or spot <= 0:
            [uticker] = ib.reqTickers(underlying)
            spot = 0.0
            for val in (uticker.marketPrice(), uticker.last, uticker.close):
                v = _safe_float(val)
                if v > 0:
                    spot = v
                    break
            if spot <= 0:
                print(json.dumps({"error": "Could not get spot price from IB", "prices": []}))
                sys.exit(1)

        # Get chain definitions once
        try:
            chains = ib.reqSecDefOptParams(index_symbol, "", sec_type, underlying.conId)
        except Exception:
            chains = []

        # Pick best chain (SMART preferred, then exact trading class match)
        exchange = "SMART"
        chain = None
        if chains:
            smart_chains = [c for c in chains if getattr(c, "exchange", "") == "SMART"]
            candidate_pool = smart_chains or chains
            if sec_type == "STK":
                exact_class = [c for c in candidate_pool if str(getattr(c, "tradingClass", "") or "").upper() == index_symbol]
                if exact_class:
                    candidate_pool = exact_class
            chain = min(candidate_pool, key=lambda c: (
                len(list(getattr(c, "expirations", []) or [])),
                -len(list(getattr(c, "strikes", []) or [])),
            )) if candidate_pool else None
            if chain:
                exchange = chain.exchange

        # Group legs by expiry to get chain definitions
        expiry_groups: dict[str, list[dict[str, Any]]] = {}
        for leg in legs:
            expiry_groups.setdefault(leg["expiry"], []).append(leg)

        results: list[dict[str, Any]] = []
        for expiry_iso, group_legs in expiry_groups.items():
            try:
                target_date = date.fromisoformat(expiry_iso)
            except ValueError:
                print(f"Skipping invalid expiry: {expiry_iso}", file=sys.stderr)
                continue

            # Map target expiry to nearest available IB expiry
            ib_expiry_str = expiry_iso
            if chain and chain.expirations:
                expirations_list = list(chain.expirations)
                closest_exp = min(
                    expirations_list,
                    key=lambda e: abs(
                        (date(int(e[:4]), int(e[4:6]), int(e[6:8])) - target_date).days
                    ),
                )
                ib_expiry_str = f"{closest_exp[:4]}-{closest_exp[4:6]}-{closest_exp[6:8]}"
                ib_expiry = closest_exp
            else:
                ib_expiry = target_date.strftime("%Y%m%d")

            # Create contracts for each leg
            contracts = [
                Option(index_symbol, ib_expiry, leg["strike"], leg["right"], exchange, currency=currency)
                for leg in group_legs
            ]

            qualified: list = []
            for i in range(0, len(contracts), BATCH_SIZE):
                batch = ib.qualifyContracts(*contracts[i : i + BATCH_SIZE])
                qualified.extend(batch)
                if i + BATCH_SIZE < len(contracts):
                    time.sleep(0.1)

            if not qualified:
                continue

            all_tickers = []
            for i in range(0, len(qualified), BATCH_SIZE):
                batch = qualified[i : i + BATCH_SIZE]
                tickers = ib.reqTickers(*batch)
                all_tickers.extend(tickers)
                if i + BATCH_SIZE < len(qualified):
                    time.sleep(0.5)

            for t in all_tickers:
                c = t.contract
                strike = float(c.strike)
                right = c.right
                bid = _safe_float(t.bid)
                ask = _safe_float(t.ask)
                last = _safe_float(t.last)
                mid = (bid + ask) / 2.0 if bid > 0 and ask > 0 else (last if last > 0 else 0.0)
                if mid <= 0 and bid <= 0 and ask <= 0 and last <= 0:
                    mid = 0.0

                # IV and Greeks
                t_years = max((target_date - date.today()).days / 365.0, 1 / 365)

                iv = 0.0
                if mid > 0.01:
                    try:
                        result = solve_iv(mid, spot, strike, RATE, 0.0, t_years, right)
                        if result.iv is not None:
                            iv = result.iv
                    except Exception:
                        iv = 0.0

                delta = gamma = vega = theta = 0.0
                if iv > 0.01:
                    try:
                        greeks = bs_greeks(spot, strike, RATE, 0.0, t_years, iv, right)
                        delta = greeks.get("delta", 0.0)
                        gamma = greeks.get("gamma", 0.0)
                        vega = greeks.get("vega", 0.0)
                        theta = greeks.get("theta", 0.0)
                    except Exception:
                        pass

                results.append({
                    "strike": strike,
                    "right": right,
                    "expiry": expiry_iso,
                    "bid": round(bid, 4),
                    "ask": round(ask, 4),
                    "mid": round(mid, 4),
                    "last": round(last, 4),
                    "iv": round(iv, 6),
                    "delta": round(delta, 4),
                    "gamma": round(gamma, 4),
                    "vega": round(vega, 4),
                    "theta": round(theta, 4),
                })

        print(json.dumps({"prices": results, "spot": round(spot, 2)}))

    except Exception as exc:
        print(json.dumps({"error": str(exc), "prices": []}))
        sys.exit(1)
    finally:
        try:
            if ib is not None:
                ib.disconnect()
        except Exception:
            pass

if __name__ == "__main__":
    main()
