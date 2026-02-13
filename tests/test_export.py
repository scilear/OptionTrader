from src.core.export import build_trade_export, export_to_json


def test_export_payload_shape():
    alert = {
        "alert_id": 1,
        "alert_type": "RR_EXTREME",
        "expiry_bucket": "30D",
        "severity": 2.1,
        "regime_label": "Neutral",
        "confidence_tier": "Core",
        "explain": {"persistence": 2},
    }
    idea = {
        "template": "SkewFade_PutSpread",
        "legs": [],
        "risk_flags": ["tail_risk"],
        "price_mid": None,
        "price_worst": None,
        "greeks": {},
        "scenarios": {},
    }

    payload = build_trade_export(alert, idea)
    assert payload["alert"]["alert_id"] == 1
    assert payload["idea"]["template"] == "SkewFade_PutSpread"
    assert export_to_json(payload)
