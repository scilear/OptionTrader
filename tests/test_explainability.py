import json

from src.core.compute_snapshot import _build_explain_payload


def test_explain_payload_schema_pass_path():
    payload = _build_explain_payload(
        alert={
            "alert_type": "RR_EXTREME",
            "expiry_bucket": "30D",
            "zscore_mid": 2.1,
            "zscore_worst": 2.0,
            "persistence": 2,
        },
        threshold=2.0,
        persistence_required=2,
        tier="Core",
        regime_label="Neutral",
        tradability_score=0.7,
    )

    encoded = json.dumps(payload)
    decoded = json.loads(encoded)
    assert decoded["alert_type"] == "RR_EXTREME"
    assert set(decoded["gates"]) == {
        "zscore",
        "persistence",
        "data_tier_quality",
        "regime",
        "tradability",
    }
    assert all(gate["status"] == "PASS" for gate in decoded["gates"].values())


def test_explain_payload_schema_block_path():
    payload = _build_explain_payload(
        alert={
            "alert_type": "RR_EXTREME",
            "expiry_bucket": "30D",
            "zscore_mid": 1.0,
            "zscore_worst": 1.1,
            "persistence": 1,
        },
        threshold=2.0,
        persistence_required=2,
        tier=None,
        regime_label="Stress",
        tradability_score=0.0,
    )

    assert payload["gates"]["zscore"]["status"] == "FAIL"
    assert payload["gates"]["persistence"]["status"] == "FAIL"
    assert payload["gates"]["data_tier_quality"]["status"] == "FAIL"
    assert payload["gates"]["regime"]["status"] == "FAIL"
    assert payload["gates"]["tradability"]["status"] == "FAIL"
