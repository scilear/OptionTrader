from __future__ import annotations

import json


def build_trade_export(alert: dict, idea: dict) -> dict:
    return {
        "alert": {
            "alert_id": alert.get("alert_id"),
            "alert_type": alert.get("alert_type"),
            "expiry_bucket": alert.get("expiry_bucket"),
            "severity": alert.get("severity"),
            "regime_label": alert.get("regime_label"),
            "confidence_tier": alert.get("confidence_tier"),
            "explain": alert.get("explain"),
        },
        "idea": {
            "template": idea.get("template"),
            "legs": idea.get("legs"),
            "risk_flags": idea.get("risk_flags"),
            "price_mid": idea.get("price_mid"),
            "price_worst": idea.get("price_worst"),
            "greeks": idea.get("greeks"),
            "scenarios": idea.get("scenarios"),
        },
    }


def export_to_json(payload: dict) -> str:
    return json.dumps(payload, indent=2)


def export_df_to_csv(df) -> str:
    return df.to_csv(index=False)
