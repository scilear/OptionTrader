from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
import statistics
import sys
from typing import Any

repo_root = Path(__file__).resolve().parents[1]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from src.core.bootstrap import ensure_repo_root_on_path

ensure_repo_root_on_path()

from src.db.connection import connect
from src.db.init_db import init_db


DEFAULT_START_TS = "2010-01-01T00:00:00Z"
DEFAULT_END_TS = "2023-12-31T23:59:59Z"
DEFAULT_UNDERLYING = "SPX"
DEFAULT_BASELINE_LINEAGE = "3b024c9"
DEFAULT_CANDIDATE_LINEAGE = "5128e8e"
DEFAULT_CONFIG_PATH = "config/config-eod-truth.yaml"
DEFAULT_ARTIFACT_PATH = "docs/roadmap/OptionTrader_Sprint_6_Replay_Artifact.md"
DEFAULT_BASELINE_CAPTURE_PATH = "docs/roadmap/OptionTrader_Sprint_6_Baseline_Capture_v1.json"


def _run_meta(underlying: str, start_ts: str, end_ts: str, lineage_prefix: str) -> dict[str, Any]:
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


def _safe_json(value: str | None) -> dict[str, Any]:
    if not value:
        return {}
    try:
        parsed = json.loads(value)
    except Exception:
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _lineage_stats(
    *,
    underlying: str,
    start_ts: str,
    end_ts: str,
    lineage_prefix: str,
) -> dict[str, Any]:
    conn = connect()
    try:
        alert_state_rows = conn.execute(
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
            (underlying, start_ts, end_ts, f"{lineage_prefix}%"),
        ).fetchall()
        idea_rows = conn.execute(
            """
            SELECT a.signal_state, ti.template, ti.scenarios
            FROM trade_ideas ti
            JOIN alerts a ON a.alert_id = ti.alert_id
            JOIN snapshots s ON s.snapshot_id = a.snapshot_id
            JOIN pipeline_runs pr ON pr.run_id = s.run_id
            WHERE s.underlying = ?
              AND s.ts >= ?
              AND s.ts <= ?
              AND pr.code_version LIKE ?
            ORDER BY ti.trade_id
            """,
            (underlying, start_ts, end_ts, f"{lineage_prefix}%"),
        ).fetchall()
    finally:
        conn.close()

    alerts_by_state = {str(state): int(count) for state, count in alert_state_rows}

    ideas_total = len(idea_rows)
    ranking_rows = 0
    promote_eligible_count = 0
    blocked_reason_counts: dict[str, int] = {}
    non_positive_edge_count = 0
    execution_ready_with_non_positive_edge = 0
    monotonic_size_violations = 0
    edge_after_cost_values: list[float] = []
    stability_pairs: list[tuple[float, float]] = []

    for signal_state, _template, scenarios_json in idea_rows:
        payload = _safe_json(scenarios_json)
        ranking = payload.get("ranking") if isinstance(payload.get("ranking"), dict) else None
        if ranking is None:
            continue
        ranking_rows += 1
        promote_eligible = bool(ranking.get("promote_eligible"))
        if promote_eligible:
            promote_eligible_count += 1

        blocked_reason = ranking.get("blocked_reason")
        if blocked_reason:
            key = str(blocked_reason)
            blocked_reason_counts[key] = blocked_reason_counts.get(key, 0) + 1

        edge_after_cost = ranking.get("edge_after_cost")
        total_friction_cost = ranking.get("total_friction_cost")
        if isinstance(edge_after_cost, (int, float)):
            edge_after_cost_values.append(float(edge_after_cost))
            if float(edge_after_cost) <= 0.0:
                non_positive_edge_count += 1
                if str(signal_state) == "ExecutionReady":
                    execution_ready_with_non_positive_edge += 1
        if isinstance(edge_after_cost, (int, float)) and isinstance(total_friction_cost, (int, float)):
            perturbed = float(edge_after_cost) - 0.02 * float(total_friction_cost)
            stability_pairs.append((float(edge_after_cost), perturbed))

        points = ranking.get("size_sensitivity")
        if isinstance(points, list) and len(points) >= 2:
            costs: list[float] = []
            for point in points:
                if not isinstance(point, dict):
                    continue
                cost_value = point.get("total_friction_cost")
                if isinstance(cost_value, (int, float)):
                    costs.append(float(cost_value))
            if any(costs[idx] > costs[idx + 1] for idx in range(len(costs) - 1)):
                monotonic_size_violations += 1

    mean_edge_after_cost = statistics.mean(edge_after_cost_values) if edge_after_cost_values else None
    median_edge_after_cost = statistics.median(edge_after_cost_values) if edge_after_cost_values else None

    baseline_rank = [x[0] for x in stability_pairs]
    perturbed_rank = [x[1] for x in stability_pairs]
    stable_rank_fraction = None
    if baseline_rank:
        unchanged = 0
        for idx, base in enumerate(baseline_rank):
            if idx >= len(perturbed_rank):
                continue
            if abs(base - perturbed_rank[idx]) <= max(1e-9, abs(base) * 0.02):
                unchanged += 1
        stable_rank_fraction = unchanged / len(baseline_rank)

    return {
        "alerts_by_state": alerts_by_state,
        "alerts_total": int(sum(alerts_by_state.values())),
        "ideas_total": ideas_total,
        "ideas_with_cost_decomposition": ranking_rows,
        "promote_eligible_count": promote_eligible_count,
        "blocked_reason_counts": blocked_reason_counts,
        "non_positive_edge_count": non_positive_edge_count,
        "execution_ready_with_non_positive_edge": execution_ready_with_non_positive_edge,
        "monotonic_size_violations": monotonic_size_violations,
        "mean_edge_after_cost": mean_edge_after_cost,
        "median_edge_after_cost": median_edge_after_cost,
        "stable_rank_fraction": stable_rank_fraction,
    }


def _summary(
    *,
    underlying: str,
    start_ts: str,
    end_ts: str,
    baseline_lineage: str,
    candidate_lineage: str,
    config_path: str,
) -> dict[str, Any]:
    baseline = _lineage_stats(
        underlying=underlying,
        start_ts=start_ts,
        end_ts=end_ts,
        lineage_prefix=baseline_lineage,
    )
    candidate = _lineage_stats(
        underlying=underlying,
        start_ts=start_ts,
        end_ts=end_ts,
        lineage_prefix=candidate_lineage,
    )
    baseline_meta = _run_meta(underlying, start_ts, end_ts, baseline_lineage)
    candidate_meta = _run_meta(underlying, start_ts, end_ts, candidate_lineage)

    decomposition_coverage_pass = (
        candidate["ideas_total"] > 0
        and candidate["ideas_with_cost_decomposition"] == candidate["ideas_total"]
    )
    non_positive_edge_gate_pass = candidate["execution_ready_with_non_positive_edge"] == 0
    monotonic_size_gate_pass = candidate["monotonic_size_violations"] == 0
    stability_gate_pass = (
        candidate["stable_rank_fraction"] is not None
        and float(candidate["stable_rank_fraction"]) >= 0.95
    )
    overall_pass = all(
        [
            decomposition_coverage_pass,
            non_positive_edge_gate_pass,
            monotonic_size_gate_pass,
            stability_gate_pass,
        ]
    )

    return {
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "window": {
            "underlying": underlying,
            "start_ts": start_ts,
            "end_ts": end_ts,
        },
        "contract": {
            "id": "S6-CONTRACT-v1",
            "baseline_lineage": baseline_lineage,
            "candidate_lineage": candidate_lineage,
            "config_path": config_path,
        },
        "lineage_metadata": {
            "baseline": baseline_meta,
            "candidate": candidate_meta,
        },
        "baseline": baseline,
        "candidate": candidate,
        "gates": {
            "decomposition_coverage_pass": decomposition_coverage_pass,
            "executionready_non_positive_edge_pass": non_positive_edge_gate_pass,
            "monotonic_size_impact_pass": monotonic_size_gate_pass,
            "ranking_stability_pass": stability_gate_pass,
            "overall_pass": overall_pass,
        },
        "recommendation": "promotable" if overall_pass else "not_promotable",
    }


def _render(summary: dict[str, Any], command: str) -> str:
    gates = summary["gates"]
    lines = [
        "# OptionTrader Sprint 6 Replay Artifact",
        "",
        f"Generated at: {summary['generated_at']}",
        "Source script: `scripts/generate_s6_replay_artifact.py`",
        "",
        "## Contract",
        "",
        f"- Contract ID: `{summary['contract']['id']}`",
        f"- Underlying: `{summary['window']['underlying']}`",
        f"- Start: `{summary['window']['start_ts']}`",
        f"- End: `{summary['window']['end_ts']}`",
        f"- Baseline lineage: `{summary['contract']['baseline_lineage']}`",
        f"- Candidate lineage: `{summary['contract']['candidate_lineage']}`",
        f"- Config path: `{summary['contract']['config_path']}`",
        "",
        "## Gate Evaluation",
        "",
        f"- Decomposition coverage gate: {'PASS' if gates['decomposition_coverage_pass'] else 'FAIL'}",
        (
            "- ExecutionReady non-positive edge gate: "
            f"{'PASS' if gates['executionready_non_positive_edge_pass'] else 'FAIL'}"
        ),
        f"- Monotonic size impact gate: {'PASS' if gates['monotonic_size_impact_pass'] else 'FAIL'}",
        f"- Ranking stability gate: {'PASS' if gates['ranking_stability_pass'] else 'FAIL'}",
        f"- Overall gate: {'PASS' if gates['overall_pass'] else 'FAIL'}",
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
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Sprint 6 replay artifact")
    parser.add_argument("--start-ts", default=DEFAULT_START_TS)
    parser.add_argument("--end-ts", default=DEFAULT_END_TS)
    parser.add_argument("--underlying", default=DEFAULT_UNDERLYING)
    parser.add_argument("--baseline-lineage", default=DEFAULT_BASELINE_LINEAGE)
    parser.add_argument("--candidate-lineage", default=DEFAULT_CANDIDATE_LINEAGE)
    parser.add_argument("--config-path", default=DEFAULT_CONFIG_PATH)
    parser.add_argument("--artifact-path", default=DEFAULT_ARTIFACT_PATH)
    parser.add_argument("--baseline-capture-path", default=DEFAULT_BASELINE_CAPTURE_PATH)
    args = parser.parse_args()

    os.environ["OPTIONTRADER_CONFIG"] = args.config_path
    init_db()

    summary = _summary(
        underlying=args.underlying,
        start_ts=args.start_ts,
        end_ts=args.end_ts,
        baseline_lineage=args.baseline_lineage,
        candidate_lineage=args.candidate_lineage,
        config_path=args.config_path,
    )
    command = (
        f"python scripts/generate_s6_replay_artifact.py --config-path {args.config_path} "
        f"--start-ts {args.start_ts} --end-ts {args.end_ts} "
        f"--underlying {args.underlying} --baseline-lineage {args.baseline_lineage} "
        f"--candidate-lineage {args.candidate_lineage}"
    )
    artifact_text = _render(summary, command)

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
    capture_path = Path(args.baseline_capture_path)
    capture_path.parent.mkdir(parents=True, exist_ok=True)
    capture_path.write_text(
        json.dumps(baseline_capture, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    print(json.dumps(summary, indent=2, sort_keys=True))
    print(f"artifact_written={artifact_path}")
    print(f"baseline_capture_written={capture_path}")


if __name__ == "__main__":
    main()
