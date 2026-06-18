#!/usr/bin/env python3
"""
ff_ib_batch_pricer.py — Batch IB option pricer for the CSFF trade scanner.

Opens one IB connection and prices all calendar spread candidates in a single
session. Uses batch reqTickers calls instead of one connection per chain.

Input:  JSON on stdin: [{"ticker":"AAPL","front_expiry":"2026-07-18","back_expiry":"2026-08-15"}, ...]
Output: JSON on stdout: {"AAPL": {...price_data...}, ...}

Price data per ticker:
  ok: bool
  spot, strike, front_dte, back_dte
  front_call/put, back_call/put: {bid, ask, mid, iv, volume}
  term_structure: [{dte, expiry, iv}]   (up to 8 points, ATM calls)
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

from src.core.iv_solve import solve_iv

import logging
logging.getLogger("ib_insync.wrapper").setLevel(logging.CRITICAL)
logging.getLogger("ib_insync.ib").setLevel(logging.CRITICAL)

RATE       = 0.05
BATCH_SIZE = 40
MAX_TS_POINTS = 8
TS_MAX_DTE = 185
TS_MIN_DTE = 5

_IB_INDEX_INFO: dict[str, tuple[str, str]] = {
    "ESTX50": ("EUREX", "EUR"),
    "DAX":    ("EUREX", "EUR"),
    "CAC40":  ("MONEP", "EUR"),
    "Z":      ("ICEEU", "GBP"),
    "SMI":    ("EUREX", "CHF"),
    "EOE":    ("FTA",   "EUR"),
    "IBEX":   ("MEFFRV","EUR"),
    "SPX":    ("CBOE",  "USD"),
    "NDX":    ("NASDAQ","USD"),
    "RUT":    ("RUSSELL","USD"),
    "VIX":    ("CBOE",  "USD"),
    "XSP":    ("CBOE",  "USD"),
}
_IB_INDEX_ALIASES: dict[str, str] = {
    "SX5E": "ESTX50", "EUROSTOXX": "ESTX50", "EUROSTOXX50": "ESTX50",
    "FTSE": "Z", "FTSE100": "Z", "UKX": "Z",
    "AEX": "EOE", "IBEX35": "IBEX",
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


def _iv_from_mid(mid: float, spot: float, strike: float, dte: int, right: str) -> float:
    if mid <= 0.01 or dte <= 0:
        return 0.0
    t_years = max(dte / 365.0, 1 / 365)
    try:
        result = solve_iv(mid, spot, strike, RATE, 0.0, t_years, right)
        return result.iv or 0.0
    except Exception:
        return 0.0


def _nearest_ib_exp(target_iso: str, expirations: list[str]) -> str | None:
    """Return closest IB YYYYMMDD expiry to target ISO date."""
    if not expirations:
        return None
    try:
        target = date.fromisoformat(target_iso)
    except ValueError:
        return None
    return min(
        expirations,
        key=lambda e: abs((date(int(e[:4]), int(e[4:6]), int(e[6:8])) - target).days),
    )


def run(candidates: list[dict]) -> dict[str, dict]:
    """
    Price all candidates via a single IB connection.
    Returns {ticker: price_data} — price_data["ok"] = False on failure.
    """
    from ib_insync import IB, Index, Stock, Option

    hosts = ["wendy", "100.125.138.42", "localhost"]
    port  = 7496

    host = next((h for h in hosts if _host_reachable(h, port)), None)
    if host is None:
        print("IB not reachable", file=sys.stderr)
        return {}

    ib = IB()
    connected = False
    seed = ((os.getpid() << 8) ^ int(time.time() * 1000)) & 0x7FFFFFFF
    client_ids = [25] + [200 + (seed % 100) + i for i in range(10)]
    for cid in client_ids:
        try:
            ib.connect(host, port, clientId=cid, timeout=15, readonly=True)
            connected = True
            break
        except Exception:
            try:
                ib.disconnect()
            except Exception:
                pass

    if not connected:
        print("IB connect failed", file=sys.stderr)
        return {}

    ib.reqMarketDataType(3)  # frozen/delayed data when live subs unavailable

    today  = date.today()
    results: dict[str, dict] = {}

    try:
        # ── Phase 1: qualify underlyings + batch spot prices ─────────────────
        und_info: dict[str, dict] = {}  # ticker -> {contract, index_symbol, currency, sec_type}
        for cand in candidates:
            t = cand["ticker"].upper()
            sym = _IB_INDEX_ALIASES.get(t, t)
            if sym in _IB_INDEX_INFO:
                exch, ccy = _IB_INDEX_INFO[sym]
                contract = Index(sym, exch, ccy)
                sec_type = "IND"
            else:
                contract = Stock(t, "SMART", "USD")
                sym, ccy, sec_type = t, "USD", "STK"
            und_info[t] = {
                "contract":     contract,
                "index_symbol": sym,
                "currency":     ccy,
                "sec_type":     sec_type,
            }

        und_contracts = [v["contract"] for v in und_info.values()]
        und_tickers_order = list(und_info.keys())

        qualified_unds: list = []
        for i in range(0, len(und_contracts), BATCH_SIZE):
            q = ib.qualifyContracts(*und_contracts[i : i + BATCH_SIZE])
            qualified_unds.extend(q)

        spot_tickers = ib.reqTickers(*qualified_unds) if qualified_unds else []

        spots: dict[str, float] = {}
        for st in spot_tickers:
            sym = st.contract.symbol
            orig = next(
                (t for t in und_tickers_order if und_info[t]["index_symbol"] == sym),
                sym,
            )
            for val in (st.marketPrice(), _safe_float(st.last), _safe_float(st.close)):
                v = _safe_float(val)
                if v > 0:
                    spots[orig] = v
                    break

        # ── Phase 2: chain params per ticker (sequential, cached) ─────────────
        chain_params: dict[str, dict | None] = {}
        for t, info in und_info.items():
            if t not in spots:
                chain_params[t] = None
                continue
            sym      = info["index_symbol"]
            sec_type = info["sec_type"]
            cid      = info["contract"].conId
            try:
                chains = ib.reqSecDefOptParams(sym, "", sec_type, cid)
                if not chains:
                    chain_params[t] = None
                    continue
                smart = [c for c in chains if getattr(c, "exchange", "") == "SMART"]
                pool  = smart or chains
                if sec_type == "STK":
                    exact = [c for c in pool
                             if str(getattr(c, "tradingClass", "") or "").upper() == sym]
                    if exact:
                        pool = exact
                chain = pool[0]
                chain_params[t] = {
                    "exchange":     chain.exchange,
                    "currency":     info["currency"],
                    "index_symbol": sym,
                    "strikes":      sorted(chain.strikes),
                    "expirations":  sorted(chain.expirations),  # YYYYMMDD
                }
            except Exception as exc:
                print(f"  chain params failed for {t}: {exc}", file=sys.stderr)
                chain_params[t] = None

        # ── Phase 3: build all option contracts ───────────────────────────────
        # contract_map: key -> Option contract object (key used for demuxing after pricing)
        # key format: (ticker, ib_expiry_yyyymmdd, strike, right)
        contract_map: dict[tuple, Any] = {}
        cand_meta: dict[str, dict] = {}  # ticker -> {atm_strike, front_ib, back_ib, ts_exps}

        for cand in candidates:
            t   = cand["ticker"].upper()
            cp  = chain_params.get(t)
            if cp is None or t not in spots:
                continue

            spot        = spots[t]
            strikes     = cp["strikes"]
            expirations = cp["expirations"]
            exch        = cp["exchange"]
            ccy         = cp["currency"]
            sym         = cp["index_symbol"]

            if not strikes or not expirations:
                continue

            atm      = min(strikes, key=lambda s: abs(s - spot))
            front_ib = _nearest_ib_exp(cand["front_expiry"], expirations)
            back_ib  = _nearest_ib_exp(cand["back_expiry"],  expirations)
            if not front_ib or not back_ib:
                continue

            # 4 calendar legs
            for ib_exp, right in [
                (front_ib, "C"), (front_ib, "P"),
                (back_ib,  "C"), (back_ib,  "P"),
            ]:
                key = (t, ib_exp, atm, right)
                if key not in contract_map:
                    contract_map[key] = Option(sym, ib_exp, atm, right, exch, currency=ccy)

            # Term structure (ATM calls, subsample to MAX_TS_POINTS)
            ts_raw = [
                (( date(int(e[:4]), int(e[4:6]), int(e[6:8])) - today ).days, e)
                for e in expirations
                if TS_MIN_DTE <= (date(int(e[:4]), int(e[4:6]), int(e[6:8])) - today).days <= TS_MAX_DTE
            ]
            n = max(1, len(ts_raw) // MAX_TS_POINTS)
            ts_exps = ts_raw[::n][:MAX_TS_POINTS]

            for dte_v, ib_exp in ts_exps:
                key = (t, ib_exp, atm, "C")
                if key not in contract_map:
                    contract_map[key] = Option(sym, ib_exp, atm, "C", exch, currency=ccy)

            cand_meta[t] = {
                "atm_strike":    atm,
                "front_ib":      front_ib,
                "back_ib":       back_ib,
                "front_dte":     (date.fromisoformat(cand["front_expiry"]) - today).days,
                "back_dte":      (date.fromisoformat(cand["back_expiry"])  - today).days,
                "front_expiry":  cand["front_expiry"],
                "back_expiry":   cand["back_expiry"],
                "ts_exps":       ts_exps,
            }

        if not contract_map:
            return {}

        # ── Phase 4: batch qualify all option contracts ───────────────────────
        all_opt_contracts = list(contract_map.values())
        for i in range(0, len(all_opt_contracts), BATCH_SIZE):
            batch = ib.qualifyContracts(*all_opt_contracts[i : i + BATCH_SIZE])
            if i + BATCH_SIZE < len(all_opt_contracts):
                time.sleep(0.05)

        # Build conId → key lookup (contracts were modified in-place by qualifyContracts)
        conid_to_key: dict[int, tuple] = {}
        for key, contract in contract_map.items():
            cid = getattr(contract, "conId", 0) or 0
            if cid > 0:
                conid_to_key[cid] = key

        qualified_opts = [c for c in all_opt_contracts if (getattr(c, "conId", 0) or 0) > 0]
        if not qualified_opts:
            return {}

        # ── Phase 5: batch price all option contracts ─────────────────────────
        all_opt_tickers: list = []
        for i in range(0, len(qualified_opts), BATCH_SIZE):
            batch_t = ib.reqTickers(*qualified_opts[i : i + BATCH_SIZE])
            all_opt_tickers.extend(batch_t)
            if i + BATCH_SIZE < len(qualified_opts):
                time.sleep(0.1)

        # ── Phase 6: build per-ticker price dict from results ─────────────────
        ticker_prices: dict[str, dict[tuple, dict]] = {}  # ticker -> {(ib_exp, strike, right): price}
        for opt_t in all_opt_tickers:
            cid = getattr(opt_t.contract, "conId", 0) or 0
            key = conid_to_key.get(cid)
            if not key:
                continue
            t_name, ib_exp, strike, right = key

            bid  = _safe_float(opt_t.bid)
            ask  = _safe_float(opt_t.ask)
            last = _safe_float(opt_t.last)
            mid  = (bid + ask) / 2 if bid > 0 and ask > 0 else last
            vol  = int(_safe_float(getattr(opt_t, "volume", 0)))

            if t_name not in ticker_prices:
                ticker_prices[t_name] = {}
            ticker_prices[t_name][(ib_exp, strike, right)] = {
                "bid": round(bid, 4),
                "ask": round(ask, 4),
                "mid": round(mid, 4),
                "volume": vol,
            }

        # ── Phase 7: compute IVs, assemble final results ──────────────────────
        for cand in candidates:
            t = cand["ticker"].upper()
            if t not in cand_meta:
                results[t] = {"ok": False, "error": "no chain data"}
                continue

            meta   = cand_meta[t]
            spot   = spots[t]
            atm    = meta["atm_strike"]
            prices = ticker_prices.get(t, {})

            def _leg(ib_exp: str, right: str, dte: int) -> dict:
                p = prices.get((ib_exp, atm, right), {})
                iv = _iv_from_mid(p.get("mid", 0.0), spot, atm, dte, right)
                return {
                    "bid":    p.get("bid",    0.0),
                    "ask":    p.get("ask",    0.0),
                    "mid":    p.get("mid",    0.0),
                    "volume": p.get("volume", 0),
                    "iv":     round(iv, 6),
                }

            front_ib  = meta["front_ib"]
            back_ib   = meta["back_ib"]
            front_dte = meta["front_dte"]
            back_dte  = meta["back_dte"]

            fc = _leg(front_ib, "C", front_dte)
            fp = _leg(front_ib, "P", front_dte)
            bc = _leg(back_ib,  "C", back_dte)
            bp = _leg(back_ib,  "P", back_dte)

            # Term structure
            ts_result = []
            for dte_v, ib_exp in meta["ts_exps"]:
                p = prices.get((ib_exp, atm, "C"), {})
                if p.get("mid", 0) > 0:
                    iv = _iv_from_mid(p["mid"], spot, atm, dte_v, "C")
                    if iv > 0:
                        ts_result.append({
                            "dte":    dte_v,
                            "expiry": f"{ib_exp[:4]}-{ib_exp[4:6]}-{ib_exp[6:8]}",
                            "iv":     round(iv, 6),
                        })

            results[t] = {
                "ok":           True,
                "spot":         round(spot, 4),
                "strike":       atm,
                "front_expiry": meta["front_expiry"],
                "back_expiry":  meta["back_expiry"],
                "front_dte":    front_dte,
                "back_dte":     back_dte,
                "front_call":   fc,
                "front_put":    fp,
                "back_call":    bc,
                "back_put":     bp,
                "term_structure": ts_result,
            }

    except Exception as exc:
        print(f"Batch pricer error: {exc}", file=sys.stderr)
    finally:
        try:
            ib.disconnect()
        except Exception:
            pass

    return results


if __name__ == "__main__":
    input_data = json.load(sys.stdin)
    output = run(input_data)
    print(json.dumps(output))
