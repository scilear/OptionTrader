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
        surface_qc_passed=True,
        surface_qc_reasons=[],
        surface_quality_score=0.9,
        regime_hash_mismatch=False,
        lifecycle={
            "signal_state": "ExecutionReady",
            "transition_reason_code": "execution_ready",
            "quality_blockers": [],
            "execution_blockers": [],
            "worst_case_coherent": True,
            "uncertainty_score": 0.0,
        },
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
        "surface_qc",
        "worst_case_coherence",
        "regime_hash",
    }
    assert all(gate["status"] == "PASS" for gate in decoded["gates"].values())
    assert decoded["lifecycle"]["signal_state"] == "ExecutionReady"


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
        surface_qc_passed=False,
        surface_qc_reasons=["degraded_surface_fit"],
        surface_quality_score=0.1,
        regime_hash_mismatch=True,
        lifecycle={
            "signal_state": "Candidate",
            "transition_reason_code": "surface_qc_failed",
            "quality_blockers": ["surface_qc_failed"],
            "execution_blockers": [],
            "worst_case_coherent": False,
            "uncertainty_score": 1.0,
        },
    )

    assert payload["gates"]["zscore"]["status"] == "FAIL"
    assert payload["gates"]["persistence"]["status"] == "FAIL"
    assert payload["gates"]["data_tier_quality"]["status"] == "FAIL"
    assert payload["gates"]["regime"]["status"] == "FAIL"
    assert payload["gates"]["tradability"]["status"] == "FAIL"
    assert payload["gates"]["surface_qc"]["status"] == "FAIL"
    assert payload["gates"]["worst_case_coherence"]["status"] == "FAIL"
    assert payload["gates"]["regime_hash"]["status"] == "FAIL"
