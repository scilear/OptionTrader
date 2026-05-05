from __future__ import annotations

from pathlib import Path

import scripts.materialize_s4_tracks_from_eod as materialize_mod


def test_profile_configs_are_distinct() -> None:
    base_config = Path("config/config-eod-truth.yaml")
    baseline_profile = Path("config/profile_s4_baseline.yaml")
    candidate_profile = Path("config/profile_s4_candidate.yaml")

    baseline_cfg_path, baseline_profile_id, baseline_hash = materialize_mod._build_profile_config(
        base_config_path=base_config,
        profile_path=baseline_profile,
    )
    candidate_cfg_path, candidate_profile_id, candidate_hash = materialize_mod._build_profile_config(
        base_config_path=base_config,
        profile_path=candidate_profile,
    )

    try:
        assert baseline_profile_id != candidate_profile_id
        assert baseline_hash != candidate_hash
    finally:
        baseline_cfg_path.unlink(missing_ok=True)
        candidate_cfg_path.unlink(missing_ok=True)
