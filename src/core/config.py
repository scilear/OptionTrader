from __future__ import annotations

import hashlib
import json
import logging
import os
from pathlib import Path

import yaml


ACTIVE_CONFIG_KEYS = frozenset(
    {
        "logging.level",
        "logging.file",
        "data.underlying",
        "data.symbol",
        "data.dte_min",
        "data.dte_max",
        "data.source",
        "data.capture_all_expiries",
        "ib.hosts",
        "ib.port",
        "ib.client_id",
        "ib.timeout_seconds",
        "ib.strike_pct_range",
        "ib.max_strikes_per_right",
        "storage.path",
        "pricing.rate",
        "pricing.dividend_yield",
        "metrics.delta_points",
        "metrics.zscore_window_days",
        "metrics.expiry_buckets_days",
        "quality.spread_gate_pct",
        "quality.allow_zero_bid",
        "quality.min_valid_points_full",
        "quality.min_valid_points_core",
        "alerts.z_threshold",
        "alerts.persistence_snapshots",
        "alerts.pessimistic_gate",
        "qc.no_arb_epsilon",
        "qc.no_arb_epsilon_iv",
        "qc.no_arb_epsilon_var",
        "regime.vix_pct_calm",
        "regime.vix_pct_stress",
        "regime.rv20_pct_calm",
        "regime.rv20_pct_stress",
        "regime.drawdown_calm",
        "regime.drawdown_stress",
        "regime.event_path",
        "regime.stress_proxy_ticker",
        "regime.weights.vix",
        "regime.weights.rv20",
        "regime.weights.drawdown",
        "regime.weights.event",
        "regime.weights.stress_proxy",
        "structures.skew_fade.short_put_delta",
        "structures.skew_fade.long_put_delta",
        "structures.fly.wing_delta",
        "structures.calendar.front_dte_min",
        "structures.calendar.front_dte_max",
        "structures.calendar.back_dte_min",
        "structures.calendar.back_dte_max",
    }
)

DEPRECATED_CONFIG_KEYS = frozenset(
    {
        "app.mode",
        "data.snapshot_tags",
        "storage.engine",
    }
)

HIGH_IMPACT_TOP_LEVEL_KEYS = frozenset(
    {
        "data",
        "ib",
        "pricing",
        "metrics",
        "quality",
        "alerts",
        "qc",
        "regime",
        "structures",
        "storage",
    }
)

HIGH_IMPACT_ACTIVE_KEYS = frozenset(
    {
        "data.source",
        "metrics.delta_points",
        "metrics.expiry_buckets_days",
        "quality.min_valid_points_full",
        "quality.min_valid_points_core",
        "alerts.pessimistic_gate",
        "qc.no_arb_epsilon",
        "qc.no_arb_epsilon_iv",
        "qc.no_arb_epsilon_var",
        "regime.vix_pct_calm",
        "regime.vix_pct_stress",
        "regime.rv20_pct_calm",
        "regime.rv20_pct_stress",
        "regime.drawdown_calm",
        "regime.drawdown_stress",
        "regime.event_path",
        "regime.stress_proxy_ticker",
        "regime.weights.vix",
        "regime.weights.rv20",
        "regime.weights.drawdown",
        "regime.weights.event",
        "regime.weights.stress_proxy",
        "structures.skew_fade.short_put_delta",
        "structures.skew_fade.long_put_delta",
        "structures.fly.wing_delta",
        "structures.calendar.front_dte_min",
        "structures.calendar.front_dte_max",
        "structures.calendar.back_dte_min",
        "structures.calendar.back_dte_max",
    }
)

CONTRACT_TEST_COVERAGE: dict[str, tuple[str, ...]] = {
    "data.source": ("tests/test_ingest_routing.py",),
    "metrics.delta_points": ("tests/test_tier_logic.py",),
    "metrics.expiry_buckets_days": ("tests/test_streamlit_config.py",),
    "quality.min_valid_points_full": ("tests/test_tier_logic.py",),
    "quality.min_valid_points_core": ("tests/test_tier_logic.py",),
    "alerts.pessimistic_gate": ("tests/test_alerts_logic.py",),
    "qc.no_arb_epsilon": ("tests/test_surface_qc.py",),
    "qc.no_arb_epsilon_iv": ("tests/test_surface_qc.py",),
    "qc.no_arb_epsilon_var": ("tests/test_surface_qc.py",),
    "regime.vix_pct_calm": ("tests/test_regime.py",),
    "regime.vix_pct_stress": ("tests/test_regime.py",),
    "regime.rv20_pct_calm": ("tests/test_regime.py",),
    "regime.rv20_pct_stress": ("tests/test_regime.py",),
    "regime.drawdown_calm": ("tests/test_regime.py",),
    "regime.drawdown_stress": ("tests/test_regime.py",),
    "regime.event_path": ("tests/test_regime.py",),
    "regime.stress_proxy_ticker": ("tests/test_regime.py",),
    "regime.weights.vix": ("tests/test_regime.py",),
    "regime.weights.rv20": ("tests/test_regime.py",),
    "regime.weights.drawdown": ("tests/test_regime.py",),
    "regime.weights.event": ("tests/test_regime.py",),
    "regime.weights.stress_proxy": ("tests/test_regime.py",),
    "structures.skew_fade.short_put_delta": ("tests/test_trade_ideas.py",),
    "structures.skew_fade.long_put_delta": ("tests/test_trade_ideas.py",),
    "structures.fly.wing_delta": ("tests/test_trade_ideas.py",),
    "structures.calendar.front_dte_min": ("tests/test_trade_ideas.py",),
    "structures.calendar.front_dte_max": ("tests/test_trade_ideas.py",),
    "structures.calendar.back_dte_min": ("tests/test_trade_ideas.py",),
    "structures.calendar.back_dte_max": ("tests/test_trade_ideas.py",),
}

EXPECTED_CONFIG_KEYS = ACTIVE_CONFIG_KEYS | DEPRECATED_CONFIG_KEYS


def _flatten_config_keys(config: dict, prefix: str = "") -> set[str]:
    keys: set[str] = set()
    for key, value in config.items():
        full_key = f"{prefix}.{key}" if prefix else key
        if isinstance(value, dict):
            keys.update(_flatten_config_keys(value, full_key))
        else:
            keys.add(full_key)
    return keys


def missing_high_impact_test_coverage() -> list[str]:
    return sorted(k for k in HIGH_IMPACT_ACTIVE_KEYS if k not in CONTRACT_TEST_COVERAGE)


def validate_config_contract(config: dict, strict_unknown_high_impact: bool = False) -> dict[str, list[str]]:
    logger = logging.getLogger("config")
    flattened = _flatten_config_keys(config)
    unknown = sorted(flattened - EXPECTED_CONFIG_KEYS)
    unknown_high_impact = [
        key for key in unknown if key.split(".", 1)[0] in HIGH_IMPACT_TOP_LEVEL_KEYS
    ]
    deprecated_present = sorted(flattened & DEPRECATED_CONFIG_KEYS)

    if unknown_high_impact:
        message = (
            "Unknown high-impact config keys detected: "
            + ", ".join(unknown_high_impact)
        )
        if strict_unknown_high_impact:
            raise ValueError(message)
        logger.warning(message)

    if deprecated_present:
        logger.warning("Deprecated config keys present: %s", ", ".join(deprecated_present))

    return {
        "unknown_high_impact": unknown_high_impact,
        "deprecated_present": deprecated_present,
    }


def get_config_path() -> Path:
    env_path = os.getenv("OPTIONTRADER_CONFIG")
    if env_path:
        return Path(env_path)
    return Path("config/config-v1.yaml")


def load_config(path: Path | None = None) -> dict:
    config_path = path or get_config_path()
    config = yaml.safe_load(config_path.read_text())
    validate_config_contract(config, strict_unknown_high_impact=False)
    return config


def canonical_config_json(config: dict) -> str:
    return json.dumps(config, sort_keys=True, separators=(",", ":"), allow_nan=False)


def config_digest(config: dict) -> str:
    payload = canonical_config_json(config).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def load_config_with_digest(path: Path | None = None) -> tuple[dict, str]:
    config = load_config(path=path)
    return config, config_digest(config)
