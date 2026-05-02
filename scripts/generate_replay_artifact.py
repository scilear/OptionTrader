from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import sys
from typing import Any

repo_root = Path(__file__).resolve().parents[1]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from src.core.bootstrap import ensure_repo_root_on_path

ensure_repo_root_on_path()

from src.db.connection import connect


LOCKED_UNDERLYING = "SPX"
LOCKED_START_TS = "2026-04-01T00:00:00Z"
LOCKED_END_TS = "2026-04-15T23:59:59Z"
LOCKED_BASELINE_COMMIT = "3b024c9"
LOCKED_CANDIDATE_COMMIT = "5128e8e"
DEFAULT_ARTIFACT_PATH = (
    "docs/roadmap/OptionTrader_Sprint_3_2_Replay_Artifact.md"
)


@dataclass(frozen=True)
class SnapshotRow:
    snapshot_id: int
    ts: datetime
    code_version: str | None
    regime_label: str


def _parse_iso8601_utc(value: str) -> datetime:
    normalized = value.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _validate_locked_contract(
    *,
    start_ts: str,
    end_ts: str,
    underlying: str,
) -> None:
    errors: list[str] = []
    if underlying != LOCKED_UNDERLYING:
        errors.append(f"underlying must be {LOCKED_UNDERLYING}")
    if start_ts != LOCKED_START_TS:
        errors.append(f"start-ts must be {LOCKED_START_TS}")
    if end_ts != LOCKED_END_TS:
        errors.append(f"end-ts must be {LOCKED_END_TS}")
    if errors:
        raise ValueError(
            "Locked S3.2 replay contract violation: " + "; ".join(errors)
        )


def _lineage_matches(code_version: str | None, lineage: str) -> bool:
    if not code_version:
        return False
    return code_version.startswith(lineage)


def _fetch_snapshot_rows(
    *,
    underlying: str,
    start_ts: str,
    end_ts: str,
) -> list[SnapshotRow]:
    conn = connect()
    try:
        rows = conn.execute(
            """
            SELECT
              s.snapshot_id,
              s.ts,
              pr.code_version,
              COALESCE(r.regime_label, 'Unknown') AS regime_label
            FROM snapshots s
            LEFT JOIN pipeline_runs pr ON pr.run_id = s.run_id
            LEFT JOIN regime_state r ON r.regime_date = CAST(s.ts AS DATE)
            WHERE s.underlying = ?
              AND s.ts >= ?
              AND s.ts <= ?
            ORDER BY s.ts, s.snapshot_id
            """,
            (underlying, start_ts, end_ts),
        ).fetchall()
    finally:
        conn.close()

    out: list[SnapshotRow] = []
    for snapshot_id, ts, code_version, regime_label in rows:
        if isinstance(ts, datetime):
            ts_value = ts
        else:
            ts_value = _parse_iso8601_utc(str(ts))
        if ts_value.tzinfo is None:
            ts_value = ts_value.replace(tzinfo=timezone.utc)
        out.append(
            SnapshotRow(
                snapshot_id=int(snapshot_id),
                ts=ts_value,
                code_version=code_version,
                regime_label=str(regime_label),
            )
        )
    return out


def _fetch_alert_counts(snapshot_ids: list[int]) -> tuple[int, dict[str, int]]:
    if not snapshot_ids:
        return 0, {}
    placeholders = ", ".join("?" for _ in snapshot_ids)
    conn = connect()
    try:
        total_row = conn.execute(
            f"SELECT COUNT(*) FROM alerts WHERE snapshot_id IN ({placeholders})",
            snapshot_ids,
        ).fetchone()
        family_rows = conn.execute(
            f"""
            SELECT alert_type, COUNT(*)
            FROM alerts
            WHERE snapshot_id IN ({placeholders})
            GROUP BY alert_type
            ORDER BY alert_type
            """,
            snapshot_ids,
        ).fetchall()
    finally:
        conn.close()
    total = int(total_row[0]) if total_row else 0
    by_family = {str(alert_type): int(count) for alert_type, count in family_rows}
    return total, by_family


def _pct_delta(candidate: int, baseline: int) -> str:
    if baseline == 0:
        return "N/A"
    delta = ((candidate - baseline) / baseline) * 100.0
    return f"{delta:+.2f}%"


def _format_markdown_table(headers: list[str], rows: list[list[str]]) -> str:
    header = "| " + " | ".join(headers) + " |"
    divider = "| " + " | ".join(["---"] * len(headers)) + " |"
    body = ["| " + " | ".join(row) + " |" for row in rows]
    return "\n".join([header, divider, *body])


def _build_artifact(
    *,
    start_ts: str,
    end_ts: str,
    underlying: str,
    baseline_commit: str,
    candidate_commit: str,
) -> tuple[str, dict[str, Any]]:
    snapshots = _fetch_snapshot_rows(
        underlying=underlying,
        start_ts=start_ts,
        end_ts=end_ts,
    )
    baseline_ids = [
        row.snapshot_id
        for row in snapshots
        if _lineage_matches(row.code_version, baseline_commit)
    ]
    candidate_ids = [
        row.snapshot_id
        for row in snapshots
        if _lineage_matches(row.code_version, candidate_commit)
    ]

    baseline_alert_count, baseline_by_family = _fetch_alert_counts(baseline_ids)
    candidate_alert_count, candidate_by_family = _fetch_alert_counts(candidate_ids)

    regime_split_counts: dict[str, int] = {}
    for row in snapshots:
        regime_split_counts[row.regime_label] = regime_split_counts.get(row.regime_label, 0) + 1

    all_families = sorted(set(baseline_by_family) | set(candidate_by_family))
    family_rows: list[list[str]] = []
    for family in all_families:
        baseline_count = baseline_by_family.get(family, 0)
        candidate_count = candidate_by_family.get(family, 0)
        family_rows.append(
            [
                family,
                str(baseline_count),
                str(candidate_count),
                _pct_delta(candidate_count, baseline_count),
                "N/A",
                "N/A",
                "N/A",
                "Outcome labels not in v1 schema",
            ]
        )
    if not family_rows:
        family_rows = [["(none)", "0", "0", "N/A", "N/A", "N/A", "N/A", "No alerts in window"]]

    summary: dict[str, Any] = {
        "baseline_commit": baseline_commit,
        "candidate_commit": candidate_commit,
        "baseline_lineage": baseline_commit,
        "candidate_lineage": candidate_commit,
        "start_ts": start_ts,
        "end_ts": end_ts,
        "underlying": underlying,
        "total_snapshots": len(snapshots),
        "regime_split_counts": regime_split_counts,
        "alert_count_baseline": baseline_alert_count,
        "alert_count_candidate": candidate_alert_count,
        "alert_delta_pct": _pct_delta(candidate_alert_count, baseline_alert_count),
        "baseline_snapshot_count": len(baseline_ids),
        "candidate_snapshot_count": len(candidate_ids),
        "precision_status": "not_available_in_v1_schema",
    }

    regime_rows = [[label, str(count)] for label, count in sorted(regime_split_counts.items())]
    if not regime_rows:
        regime_rows = [["(none)", "0"]]

    generated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    md = "\n".join(
        [
            "# OptionTrader Sprint 3.2 Replay Artifact",
            "",
            f"Generated at: {generated_at}",
            "Source script: `scripts/generate_replay_artifact.py`",
            "",
            "## Locked Comparison Contract",
            "",
            f"- `underlying`: `{underlying}`",
            f"- `start_ts`: `{start_ts}`",
            f"- `end_ts`: `{end_ts}`",
            f"- `baseline_commit`: `{baseline_commit}`",
            f"- `candidate_commit`: `{candidate_commit}`",
            "",
            "## Required Summary Fields",
            "",
            "```json",
            json.dumps(summary, indent=2, sort_keys=True),
            "```",
            "",
            "## Regime Split Counts (window total)",
            "",
            _format_markdown_table(["regime_label", "snapshot_count"], regime_rows),
            "",
            "## Per-Family Precision/Volume Summary",
            "",
            _format_markdown_table(
                [
                    "alert_family",
                    "baseline_volume",
                    "candidate_volume",
                    "volume_delta_pct",
                    "baseline_precision",
                    "candidate_precision",
                    "precision_delta",
                    "note",
                ],
                family_rows,
            ),
            "",
            "## Reproducibility",
            "",
            "```bash",
            "source .venv/bin/activate",
            (
                "python scripts/generate_replay_artifact.py "
                "--start-ts 2026-04-01T00:00:00Z --end-ts 2026-04-15T23:59:59Z"
            ),
            "```",
            "",
            "## Notes",
            "",
            "- Precision columns are `N/A` because the current alert schema does not persist realized",
            "  outcome labels required for true precision estimation.",
            "- Volume and regime split are computed directly from persisted snapshots + alerts.",
            "",
        ]
    )
    return md, summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Sprint 3.2 replay artifact")
    parser.add_argument("--start-ts", required=True)
    parser.add_argument("--end-ts", required=True)
    parser.add_argument("--underlying", default=LOCKED_UNDERLYING)
    parser.add_argument("--baseline-commit", default=LOCKED_BASELINE_COMMIT)
    parser.add_argument("--candidate-commit", default=LOCKED_CANDIDATE_COMMIT)
    parser.add_argument("--artifact-path", default=DEFAULT_ARTIFACT_PATH)
    args = parser.parse_args()

    _validate_locked_contract(
        start_ts=args.start_ts,
        end_ts=args.end_ts,
        underlying=args.underlying,
    )

    artifact, summary = _build_artifact(
        start_ts=args.start_ts,
        end_ts=args.end_ts,
        underlying=args.underlying,
        baseline_commit=args.baseline_commit,
        candidate_commit=args.candidate_commit,
    )

    output_path = Path(args.artifact_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(artifact, encoding="utf-8")

    print(json.dumps(summary, indent=2, sort_keys=True))
    print(f"artifact_written={output_path}")


if __name__ == "__main__":
    main()
