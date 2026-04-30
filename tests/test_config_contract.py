from __future__ import annotations

from pathlib import Path

import yaml

from src.core.config import (
    CONTRACT_TEST_COVERAGE,
    HIGH_IMPACT_ACTIVE_KEYS,
    missing_high_impact_test_coverage,
    validate_config_contract,
)


def _load_test_config() -> dict:
    return yaml.safe_load(Path("config/config-test.yaml").read_text())


def test_config_contract_has_full_high_impact_test_coverage() -> None:
    missing = missing_high_impact_test_coverage()
    assert missing == []
    assert set(HIGH_IMPACT_ACTIVE_KEYS).issubset(CONTRACT_TEST_COVERAGE.keys())


def test_unknown_high_impact_key_warns_in_runtime_mode() -> None:
    config = _load_test_config()
    config["alerts"]["not_a_real_field"] = True
    result = validate_config_contract(config, strict_unknown_high_impact=False)
    assert result["unknown_high_impact"] == ["alerts.not_a_real_field"]


def test_unknown_qc_key_warns_in_runtime_mode() -> None:
    config = _load_test_config()
    config.setdefault("qc", {})["not_a_real_field"] = True
    result = validate_config_contract(config, strict_unknown_high_impact=False)
    assert result["unknown_high_impact"] == ["qc.not_a_real_field"]


def test_unknown_qc_variance_key_warns_in_runtime_mode() -> None:
    config = _load_test_config()
    config.setdefault("qc", {})["not_a_real_var_field"] = True
    result = validate_config_contract(config, strict_unknown_high_impact=False)
    assert result["unknown_high_impact"] == ["qc.not_a_real_var_field"]


def test_unknown_high_impact_key_fails_in_strict_mode() -> None:
    config = _load_test_config()
    config["regime"]["unexpected_threshold"] = 99
    try:
        validate_config_contract(config, strict_unknown_high_impact=True)
        assert False, "Expected ValueError for unknown high-impact key"
    except ValueError as exc:
        assert "regime.unexpected_threshold" in str(exc)


def test_deprecated_keys_are_detected() -> None:
    config = _load_test_config()
    result = validate_config_contract(config, strict_unknown_high_impact=False)
    assert "app.mode" in result["deprecated_present"]
    assert "data.snapshot_tags" in result["deprecated_present"]
    assert "storage.engine" in result["deprecated_present"]
