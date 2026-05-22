from __future__ import annotations

import hashlib
import json
from pathlib import Path

import yaml

from src.strategy_sim.types import (
    FilterSettings,
    PutSpreadSettings,
    RunSettings,
    SimulationConfig,
    StraddleSettings,
)


def _require(mapping: dict, key: str) -> object:
    if key not in mapping:
        raise ValueError(f"Missing required config key: {key}")
    return mapping[key]


def _as_date(value: object, field: str):
    from datetime import date

    if isinstance(value, date):
        return value
    if not isinstance(value, str):
        raise ValueError(f"{field} must be an ISO date string")
    return date.fromisoformat(value)


def _as_bool(value: object, field: str) -> bool:
    if not isinstance(value, bool):
        raise ValueError(f"{field} must be boolean")
    return value


def _as_float(value: object, field: str) -> float:
    if not isinstance(value, (int, float)):
        raise ValueError(f"{field} must be numeric")
    return float(value)


def _as_int(value: object, field: str) -> int:
    if not isinstance(value, int):
        raise ValueError(f"{field} must be int")
    return value


def canonical_simulation_config_json(config: dict) -> str:
    return json.dumps(config, sort_keys=True, separators=(",", ":"), allow_nan=False)


def simulation_config_digest(config: dict) -> str:
    payload = canonical_simulation_config_json(config).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _validate_ranges(cfg: SimulationConfig) -> None:
    if cfg.run.start_date > cfg.run.end_date:
        raise ValueError("run.start_date must be <= run.end_date")
    if not cfg.run.symbols:
        raise ValueError("run.symbols must not be empty")
    if cfg.run.contract_multiplier <= 0:
        raise ValueError("run.contract_multiplier must be > 0")
    if cfg.run.initial_equity <= 0:
        raise ValueError("run.initial_equity must be > 0")
    if not 0.0 < cfg.run.max_margin_utilization <= 1.0:
        raise ValueError("run.max_margin_utilization must be in (0, 1]")
    if cfg.straddle.target_dte <= 0:
        raise ValueError("straddle.target_dte must be > 0")
    if cfg.put_credit_spread.target_dte <= 0:
        raise ValueError("put_credit_spread.target_dte must be > 0")
    if not 0.0 < cfg.put_credit_spread.early_profit_take < 1.0:
        raise ValueError("put_credit_spread.early_profit_take must be in (0, 1)")
    if cfg.filters.max_spread_pct <= 0.0:
        raise ValueError("filters.max_spread_pct must be > 0")


def load_simulation_config(path: Path | str | None = None) -> tuple[SimulationConfig, dict, str]:
    config_path = Path(path) if path is not None else Path("config/shortstraddle_sim.yaml")
    raw = yaml.safe_load(config_path.read_text())
    if not isinstance(raw, dict):
        raise ValueError("simulation config must be a mapping")

    run = _require(raw, "run")
    straddle = _require(raw, "straddle")
    put_spread = _require(raw, "put_credit_spread")
    filters = _require(raw, "filters")
    if not isinstance(run, dict) or not isinstance(straddle, dict):
        raise ValueError("run and straddle sections must be mappings")
    if not isinstance(put_spread, dict) or not isinstance(filters, dict):
        raise ValueError("put_credit_spread and filters sections must be mappings")

    settings = SimulationConfig(
        run=RunSettings(
            start_date=_as_date(_require(run, "start_date"), "run.start_date"),
            end_date=_as_date(_require(run, "end_date"), "run.end_date"),
            output_root=str(_require(run, "output_root")),
            symbols=tuple(str(s).upper() for s in _require(run, "symbols")),
            data_repo_path=str(_require(run, "data_repo_path")),
            contract_multiplier=_as_int(_require(run, "contract_multiplier"), "run.contract_multiplier"),
            initial_equity=_as_float(_require(run, "initial_equity"), "run.initial_equity"),
            max_margin_utilization=_as_float(
                _require(run, "max_margin_utilization"),
                "run.max_margin_utilization",
            ),
            transaction_fee_per_contract=_as_float(
                _require(run, "transaction_fee_per_contract"),
                "run.transaction_fee_per_contract",
            ),
            slippage_bps=_as_float(_require(run, "slippage_bps"), "run.slippage_bps"),
            vix_gate_threshold=_as_float(_require(run, "vix_gate_threshold"), "run.vix_gate_threshold"),
            gate_short_straddle=_as_bool(
                _require(run, "gate_short_straddle"),
                "run.gate_short_straddle",
            ),
            gate_put_credit_spread=_as_bool(
                _require(run, "gate_put_credit_spread"),
                "run.gate_put_credit_spread",
            ),
        ),
        straddle=StraddleSettings(
            target_dte=_as_int(_require(straddle, "target_dte"), "straddle.target_dte"),
            dte_tolerance=_as_int(_require(straddle, "dte_tolerance"), "straddle.dte_tolerance"),
            close_dte=_as_int(_require(straddle, "close_dte"), "straddle.close_dte"),
        ),
        put_credit_spread=PutSpreadSettings(
            target_dte=_as_int(_require(put_spread, "target_dte"), "put_credit_spread.target_dte"),
            dte_tolerance=_as_int(
                _require(put_spread, "dte_tolerance"),
                "put_credit_spread.dte_tolerance",
            ),
            short_delta_target=_as_float(
                _require(put_spread, "short_delta_target"),
                "put_credit_spread.short_delta_target",
            ),
            long_delta_target=_as_float(
                _require(put_spread, "long_delta_target"),
                "put_credit_spread.long_delta_target",
            ),
            early_profit_take=_as_float(
                _require(put_spread, "early_profit_take"),
                "put_credit_spread.early_profit_take",
            ),
            close_dte_itm=_as_int(
                _require(put_spread, "close_dte_itm"),
                "put_credit_spread.close_dte_itm",
            ),
        ),
        filters=FilterSettings(
            max_spread_pct=_as_float(_require(filters, "max_spread_pct"), "filters.max_spread_pct"),
        ),
    )
    _validate_ranges(settings)
    return settings, raw, simulation_config_digest(raw)
