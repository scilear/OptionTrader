from __future__ import annotations

from src.core.config import canonical_config_json, config_digest
import scripts.run_pipeline as run_pipeline_module


def test_config_digest_is_stable_for_reordered_keys():
    left = {"b": {"y": 2, "x": 1}, "a": [1, 2, 3]}
    right = {"a": [1, 2, 3], "b": {"x": 1, "y": 2}}

    assert canonical_config_json(left) == canonical_config_json(right)
    assert config_digest(left) == config_digest(right)


def test_config_digest_changes_when_value_changes():
    left = {"pricing": {"rate": 0.01, "dividend_yield": 0.0}}
    right = {"pricing": {"rate": 0.02, "dividend_yield": 0.0}}

    assert config_digest(left) != config_digest(right)


def test_code_version_falls_back_when_git_metadata_is_unavailable(monkeypatch):
    def raise_oserror(*_args, **_kwargs):
        raise OSError("git unavailable")

    monkeypatch.setattr(run_pipeline_module.subprocess, "run", raise_oserror)
    assert run_pipeline_module._resolve_code_version() == "unknown"
