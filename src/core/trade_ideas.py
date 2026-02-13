from __future__ import annotations

import json


def build_trade_ideas(alert_type: str, expiry_bucket: str) -> list[dict]:
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
        idea["price_mid"] = None
        idea["price_worst"] = None
        idea["greeks"] = json.dumps({})
        idea["scenarios"] = json.dumps({})
        idea["risk_flags"] = json.dumps(idea["risk_flags"])
        idea["legs"] = json.dumps(idea["legs"])

    return ideas
