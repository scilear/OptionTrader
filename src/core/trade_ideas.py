from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from datetime import date

from src.core.iv_solve import _bs_price, bs_greeks, strike_from_delta


@dataclass
class IdeaContext:
    spot: float
    t_years: float
    rate: float
    div: float
    iv_mid: dict
    iv_bid: dict
    iv_ask: dict
    expiry: date | None = None


def _leg_price(vol: float, context: IdeaContext, right: str, delta: float) -> tuple[float | None, float | None, dict]:
    strike = strike_from_delta(
        spot=context.spot,
        rate=context.rate,
        div=context.div,
        t_years=context.t_years,
        vol=vol,
        target_delta=delta,
        right=right,
    )
    if strike is None:
        return None, None, {"delta": 0.0, "gamma": 0.0, "vega": 0.0}

    price = _bs_price(context.spot, strike, context.rate, context.div, context.t_years, vol, right)
    greeks = bs_greeks(context.spot, strike, context.rate, context.div, context.t_years, vol, right)
    return price, strike, greeks


def _aggregate_greeks(leg_greeks: list[dict]) -> dict:
    out = {"delta": 0.0, "gamma": 0.0, "vega": 0.0}
    for g in leg_greeks:
        out["delta"] += g.get("delta", 0.0)
        out["gamma"] += g.get("gamma", 0.0)
        out["vega"] += g.get("vega", 0.0)
    return out


def build_trade_ideas(alert_type: str, expiry_bucket: str, context: IdeaContext | None) -> list[dict]:
    ideas: list[dict] = []

    if alert_type == "RR_EXTREME":
        ideas.append(
            {
                "template": "SkewFade_PutSpread",
                "legs": [
                    {"right": "P", "delta": -0.25, "action": "SELL"},
                    {"right": "P", "delta": -0.10, "action": "BUY"},
                ],
                "risk_flags": ["tail_risk", "liquidity"],
            }
        )
    elif alert_type == "FLY_EXTREME":
        ideas.append(
            {
                "template": "Fly_1x2x1",
                "legs": [
                    {"right": "P", "delta": -0.25, "action": "BUY"},
                    {"right": "P", "delta": -0.50, "action": "SELL", "qty": 2},
                    {"right": "P", "delta": -0.10, "action": "BUY"},
                ],
                "risk_flags": ["pin_risk", "liquidity"],
            }
        )
    elif alert_type == "TERM_KINK":
        ideas.append(
            {
                "template": "ATM_Calendar",
                "legs": [
                    {"right": "C", "delta": 0.50, "action": "SELL", "tenor": "front"},
                    {"right": "C", "delta": 0.50, "action": "BUY", "tenor": "back"},
                ],
                "risk_flags": ["short_gamma", "event_gap"],
            }
        )

    for idea in ideas:
        idea["expiry_bucket"] = expiry_bucket
        leg_greeks_mid = []
        leg_greeks_worst = []
        leg_prices_mid = []
        leg_prices_worst = []

        if context is not None:
            for leg in idea["legs"]:
                right = leg["right"]
                delta = leg["delta"]
                action = leg["action"]
                qty = leg.get("qty", 1)

                vol_mid = context.iv_mid.get(delta)
                vol_bid = context.iv_bid.get(delta)
                vol_ask = context.iv_ask.get(delta)

                if vol_mid:
                    price_mid, strike_mid, greeks_mid = _leg_price(vol_mid, context, right, delta)
                else:
                    price_mid, strike_mid, greeks_mid = (None, None, {"delta": 0.0, "gamma": 0.0, "vega": 0.0})

                worst_vol = vol_ask if action == "BUY" else vol_bid
                worst_vol = worst_vol or vol_mid
                if worst_vol:
                    price_worst, strike_worst, greeks_worst = _leg_price(worst_vol, context, right, delta)
                else:
                    price_worst, strike_worst, greeks_worst = (None, None, {"delta": 0.0, "gamma": 0.0, "vega": 0.0})

                sign = -1 if action == "SELL" else 1
                leg_prices_mid.append(sign * (price_mid or 0.0) * qty)
                leg_prices_worst.append(sign * (price_worst or 0.0) * qty)
                leg_greeks_mid.append({k: sign * v * qty for k, v in greeks_mid.items()})
                leg_greeks_worst.append({k: sign * v * qty for k, v in greeks_worst.items()})

                leg["strike"] = round(strike_mid) if strike_mid is not None else None
                leg["expiry"] = context.expiry.isoformat() if context.expiry else None

        price_mid_total = sum(leg_prices_mid) if leg_prices_mid else None
        price_worst_total = sum(leg_prices_worst) if leg_prices_worst else None

        idea["price_mid"] = price_mid_total
        idea["price_worst"] = price_worst_total
        idea["greeks"] = json.dumps(_aggregate_greeks(leg_greeks_mid))
        idea["scenarios"] = json.dumps({})
        idea["risk_flags"] = json.dumps(idea["risk_flags"])
        idea["legs"] = json.dumps(idea["legs"])

    return ideas
