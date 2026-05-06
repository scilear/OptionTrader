from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date

from src.core.config import load_config
from src.core.iv_solve import _bs_price, bs_greeks, strike_from_delta
from src.core.tradability import build_size_sensitivity, compute_friction_costs


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
    config: dict | None = None
    alert_severity: float | None = None
    alert_zscore_mid: float | None = None
    tradability_score: float | None = None


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


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def _idea_is_convex(template: str) -> bool:
    return template in {"Fly_1x2x1", "ATM_Calendar"}


def _cost_settings(config: dict) -> dict:
    structures = config.get("structures", {}) if config else {}
    cost_cfg = structures.get("execution_costs", {})
    return {
        "transaction_cost_bps": float(cost_cfg.get("transaction_cost_bps", 5.0)),
        "impact_cost_bps": float(cost_cfg.get("impact_cost_bps", 3.0)),
        "impact_exponent": float(cost_cfg.get("impact_exponent", 1.35)),
        "hedge_turnover_bps": float(cost_cfg.get("hedge_turnover_bps", 2.0)),
        "size_tiers": [float(x) for x in cost_cfg.get("size_tiers", [1.0, 3.0, 5.0])],
    }


def _normalized_components(
    *,
    context: IdeaContext,
    price_mid: float | None,
    price_worst: float | None,
) -> dict:
    severity_component = (
        _clamp(abs(float(context.alert_severity)) / 4.0, 0.0, 1.0)
        if context.alert_severity is not None
        else None
    )
    zscore_component = (
        _clamp(abs(float(context.alert_zscore_mid)) / 4.0, 0.0, 1.0)
        if context.alert_zscore_mid is not None
        else None
    )
    tradability_component = (
        _clamp(float(context.tradability_score), 0.0, 1.0)
        if context.tradability_score is not None
        else None
    )
    pricing_component = None
    if price_mid is not None and price_worst is not None:
        if abs(price_mid) > 1e-12:
            pricing_component = _clamp(abs(price_mid - price_worst) / abs(price_mid), 0.0, 1.0)
        else:
            pricing_component = 0.0
    return {
        "severity": severity_component,
        "zscore": zscore_component,
        "tradability": tradability_component,
        "pricing_spread": pricing_component,
    }


def build_trade_ideas(alert_type: str, expiry_bucket: str, context: IdeaContext | None) -> list[dict]:
    ideas: list[dict] = []
    cfg = context.config if context and context.config else load_config()
    structures = cfg.get("structures", {})
    skew_cfg = structures.get("skew_fade", {})
    fly_cfg = structures.get("fly", {})
    cal_cfg = structures.get("calendar", {})

    skew_short_put_delta = float(skew_cfg.get("short_put_delta", -0.25))
    skew_long_put_delta = float(skew_cfg.get("long_put_delta", -0.10))
    fly_wing_delta = abs(float(fly_cfg.get("wing_delta", 0.25)))
    front_dte_min = int(cal_cfg.get("front_dte_min", 14))
    front_dte_max = int(cal_cfg.get("front_dte_max", 30))
    back_dte_min = int(cal_cfg.get("back_dte_min", 30))
    back_dte_max = int(cal_cfg.get("back_dte_max", 60))

    if alert_type == "RR_EXTREME":
        ideas.append(
            {
                "template": "SkewFade_PutSpread",
                "legs": [
                    {"right": "P", "delta": skew_short_put_delta, "action": "SELL"},
                    {"right": "P", "delta": skew_long_put_delta, "action": "BUY"},
                ],
                "risk_flags": ["tail_risk", "liquidity"],
            }
        )
    elif alert_type == "FLY_EXTREME":
        ideas.append(
            {
                "template": "Fly_1x2x1",
                "legs": [
                    {"right": "P", "delta": -fly_wing_delta, "action": "BUY"},
                    {"right": "P", "delta": -0.50, "action": "SELL", "qty": 2},
                    {"right": "P", "delta": -max(0.10, min(0.45, fly_wing_delta / 2.0)), "action": "BUY"},
                ],
                "risk_flags": ["pin_risk", "liquidity"],
            }
        )
    elif alert_type == "TERM_KINK":
        ideas.append(
            {
                "template": "ATM_Calendar",
                "legs": [
                    {
                        "right": "C",
                        "delta": 0.50,
                        "action": "SELL",
                        "tenor": "front",
                        "dte_min": front_dte_min,
                        "dte_max": front_dte_max,
                    },
                    {
                        "right": "C",
                        "delta": 0.50,
                        "action": "BUY",
                        "tenor": "back",
                        "dte_min": back_dte_min,
                        "dte_max": back_dte_max,
                    },
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

        gross_premium_notional = (
            sum(abs(x) for x in leg_prices_mid) * 100.0 if leg_prices_mid else 0.0
        )
        greeks_mid = _aggregate_greeks(leg_greeks_mid)
        edge_components = _normalized_components(
            context=context if context is not None else IdeaContext(0.0, 0.0, 0.0, 0.0, {}, {}, {}),
            price_mid=price_mid_total,
            price_worst=price_worst_total,
        )

        blocked_reasons: list[str] = []
        if price_mid_total is None or price_worst_total is None:
            blocked_reasons.append("incomplete_edge_inputs")
        if any(value is None for value in edge_components.values()):
            blocked_reasons.append("incomplete_edge_components")

        severity_component = edge_components.get("severity") or 0.0
        zscore_component = edge_components.get("zscore") or 0.0
        tradability_component = edge_components.get("tradability") or 0.0
        pricing_component = edge_components.get("pricing_spread") or 0.0
        raw_edge_score = (
            0.35 * severity_component
            + 0.35 * zscore_component
            + 0.20 * tradability_component
            + 0.10 * pricing_component
        )
        edge_before_cost = max(0.0, raw_edge_score * gross_premium_notional)

        context_for_cost = context if context is not None else IdeaContext(0.0, 0.0, 0.0, 0.0, {}, {}, {})
        settings = _cost_settings(cfg)
        include_hedge_path = _idea_is_convex(idea["template"])
        cost = compute_friction_costs(
            edge_before_cost=edge_before_cost,
            gross_premium_notional=gross_premium_notional,
            net_gamma=float(greeks_mid.get("gamma", 0.0)),
            spot=float(context_for_cost.spot),
            size=1.0,
            transaction_cost_bps=settings["transaction_cost_bps"],
            impact_cost_bps=settings["impact_cost_bps"],
            impact_exponent=settings["impact_exponent"],
            hedge_turnover_bps=settings["hedge_turnover_bps"],
            include_hedge_path=include_hedge_path,
        )
        size_sensitivity = build_size_sensitivity(
            edge_before_cost=edge_before_cost,
            gross_premium_notional=gross_premium_notional,
            net_gamma=float(greeks_mid.get("gamma", 0.0)),
            spot=float(context_for_cost.spot),
            transaction_cost_bps=settings["transaction_cost_bps"],
            impact_cost_bps=settings["impact_cost_bps"],
            impact_exponent=settings["impact_exponent"],
            hedge_turnover_bps=settings["hedge_turnover_bps"],
            include_hedge_path=include_hedge_path,
            size_tiers=settings["size_tiers"],
        )

        total_costs = [point["total_friction_cost"] for point in size_sensitivity]
        if any(
            total_costs[idx] > total_costs[idx + 1]
            for idx in range(len(total_costs) - 1)
        ):
            blocked_reasons.append("non_monotonic_size_impact")

        if cost.edge_after_cost <= 0.0:
            blocked_reasons.append("non_positive_edge_after_cost")

        risk_flags = json.loads(json.dumps(idea["risk_flags"]))
        if include_hedge_path:
            risk_flags.append("hedge_path_estimated")

        ranking = {
            "edge_before_cost": edge_before_cost,
            "transaction_cost": cost.transaction_cost,
            "size_impact_cost": cost.size_impact_cost,
            "hedge_path_cost": cost.hedge_path_cost,
            "total_friction_cost": cost.total_friction_cost,
            "edge_after_cost": cost.edge_after_cost,
            "size_sensitivity": size_sensitivity,
            "blocked_reasons": blocked_reasons,
            "blocked_reason": blocked_reasons[0] if blocked_reasons else None,
            "promote_eligible": not blocked_reasons,
            "normalized_edge_components": edge_components,
        }

        idea["price_mid"] = price_mid_total
        idea["price_worst"] = price_worst_total
        idea["greeks"] = json.dumps(greeks_mid)
        idea["scenarios"] = json.dumps(
            {
                "ranking": ranking,
                "model_assumptions": {
                    "transaction_cost_bps": settings["transaction_cost_bps"],
                    "impact_cost_bps": settings["impact_cost_bps"],
                    "impact_exponent": settings["impact_exponent"],
                    "hedge_turnover_bps": settings["hedge_turnover_bps"],
                    "include_hedge_path": include_hedge_path,
                },
            }
        )
        idea["risk_flags"] = json.dumps(risk_flags)
        idea["legs"] = json.dumps(idea["legs"])

    return ideas
