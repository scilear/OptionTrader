from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
import os
from pathlib import Path
import sys
from typing import Any

repo_root = Path(__file__).resolve().parents[1]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from src.core.bootstrap import ensure_repo_root_on_path

ensure_repo_root_on_path()

from scripts.evaluate_alert_outcomes import evaluate_alert_outcomes
from src.db.connection import connect
from src.db.init_db import init_db


DEFAULT_START_TS = "2010-01-01T00:00:00Z"
DEFAULT_END_TS = "2023-12-31T23:59:59Z"
DEFAULT_UNDERLYING = "SPX"
DEFAULT_BASELINE_LINEAGE = "3b024c9"
DEFAULT_CANDIDATE_LINEAGE = "5128e8e"
DEFAULT_HORIZON_DAYS = 5
DEFAULT_MAX_VOLUME_INFLATION_PCT = 15.0
DEFAULT_CONFIG_PATH = "config/config-eod-truth.yaml"
DEFAULT_ARTIFACT_PATH = "docs/roadmap/OptionTrader_Sprint_5_Replay_Artifact.md"
DEFAULT_BASELINE_CAPTURE_PATH = "docs/roadmap/OptionTrader_Sprint_5_Baseline_Capture_v1.json"
VALID_SIGNAL_STATES = {"Candidate", "Validated", "ExecutionReady"}


def _lineage_meta(underlying: str, start_ts: str, end_ts: str, lineage_prefix: str) -> dict[str, Any]:
    conn = connect()
    try:
        row = conn.execute(
            """
            SELECT pr.run_id, pr.code_version, pr.config_hash
            FROM pipeline_runs pr
            JOIN snapshots s ON s.run_id = pr.run_id
            WHERE s.underlying = ?
              AND s.ts >= ?
              AND s.ts <= ?
              AND pr.code_version LIKE ?
            GROUP BY pr.run_id, pr.code_version, pr.config_hash
            ORDER BY pr.run_id DESC
            LIMIT 1
            """,
            (underlying, start_ts, end_ts, f"{lineage_prefix}%"),
        ).fetchone()
    finally:
        conn.close()
    if not row:
        return {
            "run_id": None,
            "code_version": None,
            "config_hash": None,
            "profile_id": None,
        }

    run_id, code_version, config_hash = row
    profile_id = None
    marker = "+profile:"
    code_version_value = str(code_version) if code_version is not None else None
    if code_version_value and marker in code_version_value:
        profile_id = code_version_value.split(marker, 1)[1]
    return {
        "run_id": int(run_id),
        "code_version": code_version_value,
        "config_hash": str(config_hash) if config_hash is not None else None,
        "profile_id": profile_id,
    }


def _fetch_track_stats(
    *,
    underlying: str,
    start_ts: str,
    end_ts: str,
    lineage_prefix: str,
    horizon_days: int,
) -> dict[str, Any]:
    conn = connect()
    try:
        params = (underlying, start_ts, end_ts, f"{lineage_prefix}%")
        snapshot_count = int(
            conn.execute(
                """
                SELECT COUNT(*)
                FROM snapshots s
                JOIN pipeline_runs pr ON pr.run_id = s.run_id
                WHERE s.underlying = ?
                  AND s.ts >= ?
                  AND s.ts <= ?
                  AND pr.code_version LIKE ?
                """,
                params,
            ).fetchone()[0]
        )

        alert_rows = conn.execute(
            """
            SELECT a.signal_state, COUNT(*)
            FROM alerts a
            JOIN snapshots s ON s.snapshot_id = a.snapshot_id
            JOIN pipeline_runs pr ON pr.run_id = s.run_id
            WHERE s.underlying = ?
              AND s.ts >= ?
              AND s.ts <= ?
              AND pr.code_version LIKE ?
            GROUP BY 1
            ORDER BY 1
            """,
            params,
        ).fetchall()
        alerts_by_state = {str(signal_state): int(count) for signal_state, count in alert_rows}
        alerts_total = int(sum(alerts_by_state.values()))

        transition_alerts = int(
            conn.execute(
                """
                SELECT COUNT(*)
                FROM alerts a
                JOIN snapshots s ON s.snapshot_id = a.snapshot_id
                JOIN pipeline_runs pr ON pr.run_id = s.run_id
                WHERE s.underlying = ?
                  AND s.ts >= ?
                  AND s.ts <= ?
                  AND pr.code_version LIKE ?
                  AND COALESCE(a.regime_label, 'Unknown') = 'Transition'
                """,
                params,
            ).fetchone()[0]
        )

        outcome_rows = conn.execute(
            """
            SELECT ao.outcome_label, COALESCE(a.regime_label, 'Unknown') AS regime_label, COUNT(*)
            FROM alert_outcomes ao
            JOIN alerts a ON a.alert_id = ao.alert_id
            JOIN snapshots s ON s.snapshot_id = a.snapshot_id
            JOIN pipeline_runs pr ON pr.run_id = s.run_id
            WHERE s.underlying = ?
              AND s.ts >= ?
              AND s.ts <= ?
              AND pr.code_version LIKE ?
              AND ao.horizon_days = ?
            GROUP BY 1, 2
            """,
            (underlying, start_ts, end_ts, f"{lineage_prefix}%", horizon_days),
        ).fetchall()
    finally:
        conn.close()

    tp = 0
    fp = 0
    transition_fp = 0
    outcomes_observed = 0
    for outcome_label, regime_label, count in outcome_rows:
        c = int(count)
        outcomes_observed += c
        label = str(outcome_label).lower()
        if label == "tp":
            tp += c
            continue
        if label == "fp":
            fp += c
            if str(regime_label) == "Transition":
                transition_fp += c

    precision = (tp / (tp + fp)) if (tp + fp) > 0 else None
    transition_fp_density = (transition_fp / transition_alerts) if transition_alerts > 0 else None
    invalid_states = sorted(state for state in alerts_by_state if state not in VALID_SIGNAL_STATES)

    return {
        "snapshot_count": snapshot_count,
        "alerts_total": alerts_total,
        "alerts_by_state": alerts_by_state,
        "invalid_signal_states": invalid_states,
        "outcomes": {
            "horizon_days": horizon_days,
            "tp": tp,
            "fp": fp,
            "outcomes_observed": outcomes_observed,
            "precision": precision,
            "transition_alerts": transition_alerts,
            "transition_fp": transition_fp,
            "transition_fp_density": transition_fp_density,
        },
    }


def _pct_delta(candidate: int, baseline: int) -> float | None:
    if baseline == 0:
        return None
    return ((candidate - baseline) / baseline) * 100.0


def _build_summary(
    *,
    start_ts: str,
    end_ts: str,
    underlying: str,
    baseline_lineage: str,
    candidate_lineage: str,
    horizon_days: int,
    max_volume_inflation_pct: float,
    config_path: str,
) -> dict[str, Any]:
    baseline_meta = _lineage_meta(underlying, start_ts, end_ts, baseline_lineage)
    candidate_meta = _lineage_meta(underlying, start_ts, end_ts, candidate_lineage)
    baseline = _fetch_track_stats(
        underlying=underlying,
        start_ts=start_ts,
        end_ts=end_ts,
        lineage_prefix=baseline_lineage,
        horizon_days=horizon_days,
    )
    candidate = _fetch_track_stats(
        underlying=underlying,
        start_ts=start_ts,
        end_ts=end_ts,
        lineage_prefix=candidate_lineage,
        horizon_days=horizon_days,
    )

    volume_delta_pct = _pct_delta(candidate["alerts_total"], baseline["alerts_total"])
    volume_guardrail_pass = (
        volume_delta_pct is not None and volume_delta_pct <= max_volume_inflation_pct
    )

    baseline_transition_density = baseline["outcomes"]["transition_fp_density"]
    candidate_transition_density = candidate["outcomes"]["transition_fp_density"]
    transition_density_gate_pass = (
        baseline_transition_density is not None
        and candidate_transition_density is not None
        and float(candidate_transition_density) < float(baseline_transition_density)
    )
    transition_density_blocked_reason = None
    if baseline_transition_density is None or candidate_transition_density is None:
        transition_density_blocked_reason = "missing_transition_alerts"

    min_sample_gate_pass = baseline["alerts_total"] >= 50 and candidate["alerts_total"] >= 50
    precision_non_regression_pass = (
        baseline["outcomes"]["precision"] is not None
        and candidate["outcomes"]["precision"] is not None
        and float(candidate["outcomes"]["precision"]) >= float(baseline["outcomes"]["precision"])
    )

    state_sanity_pass = (
        not baseline["invalid_signal_states"]
        and not candidate["invalid_signal_states"]
        and baseline["alerts_by_state"].get("ExecutionReady", 0) > 0
        and candidate["alerts_by_state"].get("ExecutionReady", 0) > 0
    )

    all_gates_pass = all(
        [
            min_sample_gate_pass,
            volume_guardrail_pass,
            transition_density_gate_pass,
            state_sanity_pass,
            precision_non_regression_pass,
        ]
    )
    recommendation = "promotable" if all_gates_pass else "not_promotable"

    return {
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "window": {
            "underlying": underlying,
            "start_ts": start_ts,
            "end_ts": end_ts,
        },
        "contract": {
            "baseline_lineage": baseline_lineage,
            "candidate_lineage": candidate_lineage,
            "horizon_days": horizon_days,
            "max_volume_inflation_pct": max_volume_inflation_pct,
            "config_path": config_path,
            "transition_fp_density_rule": "candidate < baseline",
            "state_sanity_required_states": sorted(VALID_SIGNAL_STATES),
        },
        "lineage_metadata": {
            "baseline": baseline_meta,
            "candidate": candidate_meta,
        },
        "baseline": baseline,
        "candidate": candidate,
        "gates": {
            "min_sample_gate_pass": min_sample_gate_pass,
            "volume_delta_pct": volume_delta_pct,
            "volume_guardrail_pass": volume_guardrail_pass,
            "transition_fp_density_baseline": baseline_transition_density,
            "transition_fp_density_candidate": candidate_transition_density,
            "transition_fp_density_improved_pass": transition_density_gate_pass,
            "transition_fp_density_blocked_reason": transition_density_blocked_reason,
            "state_distribution_sanity_pass": state_sanity_pass,
            "precision_non_regression_pass": precision_non_regression_pass,
            "overall_pass": all_gates_pass,
        },
        "recommendation": recommendation,
    }


def _format_pct(value: float | None) -> str:
    if value is None:
        return "N/A"
    return f"{value:+.2f}%"


def _format_float(value: float | None) -> str:
    if value is None:
        return "N/A"
    return f"{value:.6f}"


def _format_gate(flag: bool) -> str:
    return "PASS" if flag else "FAIL"


def _render_markdown(summary: dict[str, Any], command: str) -> str:
    gates = summary["gates"]
    baseline = summary["baseline"]
    candidate = summary["candidate"]
    baseline_meta = summary["lineage_metadata"]["baseline"]
    candidate_meta = summary["lineage_metadata"]["candidate"]

    lines = [
        "# OptionTrader Sprint 5 Replay Artifact",
        "",
        f"Generated at: {summary['generated_at']}",
        "Source script: `scripts/generate_s5_replay_artifact.py`",
        "",
        "## Evaluation Contract",
        "",
        f"- Underlying: `{summary['window']['underlying']}`",
        f"- Start: `{summary['window']['start_ts']}`",
        f"- End: `{summary['window']['end_ts']}`",
        f"- Baseline lineage: `{summary['contract']['baseline_lineage']}`",
        f"- Candidate lineage: `{summary['contract']['candidate_lineage']}`",
        f"- Outcome horizon: `{summary['contract']['horizon_days']}` days",
        (
            "- Volume inflation guardrail: "
            f"`<= +{summary['contract']['max_volume_inflation_pct']:.1f}%`"
        ),
        "- Transition FP density rule: `candidate < baseline`",
        "",
        "## Baseline vs Candidate Metadata",
        "",
        (
            "- Baseline run/profile/hash: "
            f"`run_id={baseline_meta['run_id']}` "
            f"`profile={baseline_meta['profile_id']}` "
            f"`config_hash={baseline_meta['config_hash']}`"
        ),
        (
            "- Candidate run/profile/hash: "
            f"`run_id={candidate_meta['run_id']}` "
            f"`profile={candidate_meta['profile_id']}` "
            f"`config_hash={candidate_meta['config_hash']}`"
        ),
        "",
        "## Signal Counts by State",
        "",
        "| State | Baseline | Candidate |",
        "| --- | ---: | ---: |",
    ]
    all_states = sorted(set(baseline["alerts_by_state"]) | set(candidate["alerts_by_state"]))
    if not all_states:
        all_states = ["(none)"]
    for state in all_states:
        lines.append(
            "| "
            f"{state} | {baseline['alerts_by_state'].get(state, 0)} | {candidate['alerts_by_state'].get(state, 0)} |"
        )

    lines.extend(
        [
            "",
            "## Gate Evaluation",
            "",
            f"- Min sample gate (`>=50` alerts/track): {_format_gate(gates['min_sample_gate_pass'])}",
            (
                "- Volume guardrail (`candidate-baseline`): "
                f"{_format_gate(gates['volume_guardrail_pass'])} "
                f"(delta={_format_pct(gates['volume_delta_pct'])})"
            ),
            (
                "- Transition FP density improvement: "
                f"{_format_gate(gates['transition_fp_density_improved_pass'])} "
                f"(baseline={_format_float(gates['transition_fp_density_baseline'])}, "
                f"candidate={_format_float(gates['transition_fp_density_candidate'])}, "
                f"blocked_reason={gates['transition_fp_density_blocked_reason']})"
            ),
            f"- State distribution sanity: {_format_gate(gates['state_distribution_sanity_pass'])}",
            f"- Precision non-regression: {_format_gate(gates['precision_non_regression_pass'])}",
            f"- Overall release gate: {_format_gate(gates['overall_pass'])}",
            "",
            "## Recommendation",
            "",
            f"- Final recommendation: `{summary['recommendation']}`",
            "",
            "## Summary Payload",
            "",
            "```json",
            json.dumps(summary, indent=2, sort_keys=True),
            "```",
            "",
            "## Reproducibility",
            "",
            "```bash",
            "source .venv/bin/activate",
            command,
            "```",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Sprint 5 replay artifact")
    parser.add_argument("--start-ts", default=DEFAULT_START_TS)
    parser.add_argument("--end-ts", default=DEFAULT_END_TS)
    parser.add_argument("--underlying", default=DEFAULT_UNDERLYING)
    parser.add_argument("--baseline-lineage", default=DEFAULT_BASELINE_LINEAGE)
    parser.add_argument("--candidate-lineage", default=DEFAULT_CANDIDATE_LINEAGE)
    parser.add_argument("--horizon-days", type=int, default=DEFAULT_HORIZON_DAYS)
    parser.add_argument(
        "--max-volume-inflation-pct",
        type=float,
        default=DEFAULT_MAX_VOLUME_INFLATION_PCT,
    )
    parser.add_argument("--config-path", default=DEFAULT_CONFIG_PATH)
    parser.add_argument("--artifact-path", default=DEFAULT_ARTIFACT_PATH)
    parser.add_argument("--baseline-capture-path", default=DEFAULT_BASELINE_CAPTURE_PATH)
    parser.add_argument("--skip-outcome-refresh", action="store_true")
    args = parser.parse_args()

    os.environ["OPTIONTRADER_CONFIG"] = args.config_path

    init_db()
    if not args.skip_outcome_refresh:
        evaluate_alert_outcomes(horizon_days=args.horizon_days, overwrite=False)

    summary = _build_summary(
        start_ts=args.start_ts,
        end_ts=args.end_ts,
        underlying=args.underlying,
        baseline_lineage=args.baseline_lineage,
        candidate_lineage=args.candidate_lineage,
        horizon_days=args.horizon_days,
        max_volume_inflation_pct=args.max_volume_inflation_pct,
        config_path=args.config_path,
    )

    command = (
        f"python scripts/generate_s5_replay_artifact.py --config-path {args.config_path} "
        f"--start-ts {args.start_ts} "
        f"--end-ts {args.end_ts} "
        f"--underlying {args.underlying} "
        f"--baseline-lineage {args.baseline_lineage} "
        f"--candidate-lineage {args.candidate_lineage}"
    )

    artifact_text = _render_markdown(summary, command)

    artifact_path = Path(args.artifact_path)
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    artifact_path.write_text(artifact_text + "\n", encoding="utf-8")

    baseline_capture = {
        "captured_at": summary["generated_at"],
        "window": summary["window"],
        "contract": summary["contract"],
        "lineage_metadata": {
            "baseline": summary["lineage_metadata"]["baseline"],
        },
        "baseline": summary["baseline"],
    }
    baseline_capture_path = Path(args.baseline_capture_path)
    baseline_capture_path.parent.mkdir(parents=True, exist_ok=True)
    baseline_capture_path.write_text(
        json.dumps(baseline_capture, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    print(json.dumps(summary, indent=2, sort_keys=True))
    print(f"artifact_written={artifact_path}")
    print(f"baseline_capture_written={baseline_capture_path}")


if __name__ == "__main__":
    main()
