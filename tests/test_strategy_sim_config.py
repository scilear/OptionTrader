from __future__ import annotations

from pathlib import Path

import yaml

from src.strategy_sim.config import load_simulation_config, simulation_config_digest


def test_load_simulation_config_success(tmp_path: Path) -> None:
    payload = yaml.safe_load(Path("config/shortstraddle_sim.yaml").read_text())
    payload["run"]["output_root"] = str(tmp_path / "artifacts")
    cfg_path = tmp_path / "sim.yaml"
    cfg_path.write_text(yaml.safe_dump(payload, sort_keys=False))

    config, raw, digest = load_simulation_config(cfg_path)
    assert config.run.symbols
    assert config.run.start_date <= config.run.end_date
    assert raw["run"]["output_root"] == str(tmp_path / "artifacts")
    assert digest == simulation_config_digest(raw)


def test_load_simulation_config_rejects_invalid_ranges(tmp_path: Path) -> None:
    payload = yaml.safe_load(Path("config/shortstraddle_sim.yaml").read_text())
    payload["run"]["max_margin_utilization"] = 1.5
    cfg_path = tmp_path / "bad.yaml"
    cfg_path.write_text(yaml.safe_dump(payload, sort_keys=False))

    try:
        load_simulation_config(cfg_path)
        assert False, "expected ValueError"
    except ValueError as exc:
        assert "max_margin_utilization" in str(exc)
