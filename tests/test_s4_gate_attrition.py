from __future__ import annotations

from datetime import datetime

import scripts.report_s4_gate_attrition as attrition_mod


def test_attrition_effective_start_ts_uses_regime_ready_boundary(monkeypatch):
    monkeypatch.setattr(
        attrition_mod,
        "first_regime_ready_date",
        lambda run_id: {
            31: datetime(2010, 4, 5).date(),
            32: datetime(2010, 4, 5).date(),
        }.get(run_id),
    )
    window = attrition_mod._resolve_effective_start_ts(
        requested_start_ts="2010-01-01T00:00:00Z",
        baseline_run_id=31,
        candidate_run_id=32,
    )
    assert window["effective_start_ts"] == "2010-04-05T00:00:00Z"
    assert window["warmup_exclusion_applied"] is True
    assert window["warmup_excluded_days"] == 94


def test_attrition_effective_start_ts_no_shift_when_no_ready_dates(monkeypatch):
    monkeypatch.setattr(attrition_mod, "first_regime_ready_date", lambda _run_id: None)
    window = attrition_mod._resolve_effective_start_ts(
        requested_start_ts="2010-01-01T00:00:00Z",
        baseline_run_id=31,
        candidate_run_id=32,
    )
    assert window["effective_start_ts"] == "2010-01-01T00:00:00Z"
    assert window["warmup_exclusion_applied"] is False
    assert window["warmup_excluded_days"] == 0
