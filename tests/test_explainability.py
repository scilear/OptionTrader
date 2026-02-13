import json


def test_explain_payload_schema():
    payload = {
        "alert_type": "RR_EXTREME",
        "expiry_bucket": "30D",
        "z_threshold": 2.0,
        "zscore_mid": 2.1,
        "zscore_worst": 2.0,
        "persistence": 2,
        "regime_label": "Neutral",
        "confidence_tier": "Core",
        "tradability_score": 0.7,
    }

    encoded = json.dumps(payload)
    decoded = json.loads(encoded)
    assert decoded["alert_type"] == "RR_EXTREME"
    assert "tradability_score" in decoded
