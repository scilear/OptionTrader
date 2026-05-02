from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
import sys

repo_root = Path(__file__).resolve().parents[1]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from src.core.bootstrap import ensure_repo_root_on_path

ensure_repo_root_on_path()

from src.db.connection import connect


DEFAULT_START_TS = "2026-04-01T00:00:00Z"
DEFAULT_END_TS = "2026-04-15T23:59:59Z"
DEFAULT_UNDERLYING = "SPX"
DEFAULT_OUTPUT = "docs/roadmap/OptionTrader_Sprint_4_Ablation_Artifact.md"


def _fetch_alert_stats(underlying: str, start_ts: str, end_ts: str) -> tuple[int, dict[str, int]]:
    conn = connect()
    try:
        total = conn.execute(
            """
            SELECT COUNT(*)
            FROM alerts a
            JOIN snapshots s ON s.snapshot_id = a.snapshot_id
            WHERE s.underlying = ?
              AND s.ts >= ?
              AND s.ts <= ?
            """,
            (underlying, start_ts, end_ts),
        ).fetchone()[0]
        by_bucket_rows = conn.execute(
            """
            SELECT COALESCE(a.regime_label, 'Unknown') AS regime_label, COUNT(*)
            FROM alerts a
            JOIN snapshots s ON s.snapshot_id = a.snapshot_id
            WHERE s.underlying = ?
              AND s.ts >= ?
              AND s.ts <= ?
            GROUP BY 1
            ORDER BY 2 DESC, 1
            """,
            (underlying, start_ts, end_ts),
        ).fetchall()
    finally:
        conn.close()

    return int(total), {str(k): int(v) for k, v in by_bucket_rows}


def _pct_delta(candidate: int, baseline: int) -> float | None:
    if baseline == 0:
        return None
    return ((candidate - baseline) / baseline) * 100.0


def _format_gate_result(value: bool | None) -> str:
    if value is True:
        return "PASS"
    if value is False:
        return "FAIL"
    return "N/A"


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Sprint 4 ablation artifact")
    parser.add_argument("--start-ts", default=DEFAULT_START_TS)
    parser.add_argument("--end-ts", default=DEFAULT_END_TS)
    parser.add_argument("--underlying", default=DEFAULT_UNDERLYING)
    parser.add_argument("--output", default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    # v1 operational reality: current DB has one active implementation lineage.
    # Baseline/candidate values are represented as explicit analysis tracks.
    baseline_alert_count = 0
    candidate_alert_count, candidate_buckets = _fetch_alert_stats(
        args.underlying,
        args.start_ts,
        args.end_ts,
    )

    min_sample_pass = candidate_alert_count >= 50 and all(
        count >= 10 for count in candidate_buckets.values()
    )
    precision_delta = None
    precision_gate_pass = False
    volume_delta_pct = _pct_delta(candidate_alert_count, baseline_alert_count)
    volume_gate_pass = False
    transition_fp_worsening = None
    transition_fp_gate_pass = False

    overall_gate_pass = all(
        [
            min_sample_pass,
            precision_gate_pass,
            volume_gate_pass,
            transition_fp_gate_pass,
        ]
    )

    feature_decisions = [
        {
            "feature": "event",
            "status": "disabled",
            "reason": "s4_03_gate_failed",
            "evidence": "insufficient alert sample and no precision labels",
        },
        {
            "feature": "stress_proxy",
            "status": "disabled",
            "reason": "s4_03_gate_failed",
            "evidence": "insufficient alert sample and no precision labels",
        },
    ]

    summary = {
        "window": {
            "start_ts": args.start_ts,
            "end_ts": args.end_ts,
            "underlying": args.underlying,
        },
        "baseline_track": "rv_only_reference",
        "candidate_track": "multi_signal_s4",
        "sample": {
            "alerts_total": candidate_alert_count,
            "alerts_by_regime": candidate_buckets,
        },
        "gates": {
            "min_sample_pass": min_sample_pass,
            "precision_delta": precision_delta,
            "precision_gate_pass": precision_gate_pass,
            "volume_delta_pct": volume_delta_pct,
            "volume_gate_pass": volume_gate_pass,
            "transition_false_positive_density_worsening": transition_fp_worsening,
            "transition_fp_gate_pass": transition_fp_gate_pass,
            "overall_pass": overall_gate_pass,
        },
        "feature_decisions": feature_decisions,
    }

    lines = [
        "# OptionTrader Sprint 4 Ablation Artifact",
        "",
        f"Generated at: {datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')}",
        "Source script: `scripts/generate_regime_ablation_artifact.py`",
        "",
        "## Locked Gate Evaluation",
        "",
        "- Minimum sample gate (`>=50` total and `>=10` per active bucket): "
        + _format_gate_result(min_sample_pass),
        "- Precision lift gate (`>= +0.03`): " + _format_gate_result(precision_gate_pass),
        "- Volume guardrail (`[-15%, +15%]`): " + _format_gate_result(volume_gate_pass),
        "- Transition FP density worsening (`<= +0.02`): " + _format_gate_result(transition_fp_gate_pass),
        "- Overall retention gate: " + _format_gate_result(overall_gate_pass),
        "",
        "## Summary Payload",
        "",
        "```json",
        json.dumps(summary, indent=2, sort_keys=True),
        "```",
        "",
        "## Feature Decisions",
        "",
        "- `event`: disabled in runtime defaults (`regime.weights.event=0.00`).",
        "- `stress_proxy`: disabled in runtime defaults (`regime.weights.stress_proxy=0.00`).",
        "",
        "## Notes",
        "",
        "- This run uses the locked S3.2 window by default.",
        "- Precision and transition false-positive density require outcome labels that are not",
        "  currently persisted in v1 schema; gates are treated as failed until evidence is available.",
    ]

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    print(f"artifact_written={out}")


if __name__ == "__main__":
    main()
