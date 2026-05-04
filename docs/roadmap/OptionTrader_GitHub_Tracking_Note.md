# OptionTrader GitHub Tracking Note

Date: 2026-05-03
Status: Active project protocol

## Purpose

Use GitHub as the tactical execution tracker (issues/tasks/PRs) and keep roadmap markdown files as
the strategic source of truth.

## Tracking Model

- Strategic planning source:
  - `docs/roadmap/OptionTrader_Next_Level_Plan.md`
  - sprint execution plans and sprint ticket sheets in `docs/roadmap/`
- Tactical execution source:
  - GitHub issues (one issue per ticket or subtask)
  - pull requests linked to issues
  - optional GitHub Project board for status view

## Required Convention

1. Every sprint ticket (`Sx-yy`) should have one GitHub issue.
2. Every PR must reference issue(s), for example:
   - `Closes #123`
   - `Refs #123`
3. Issue title format:
   - `[S4-02] Event and stress proxy input wiring`
4. Keep roadmap docs and issue status synchronized at ticket boundaries.

## Labels and Milestones

Recommended labels:

- `sprint:s3.2`, `sprint:s4`, `sprint:s5`
- `area:regime`, `area:schema`, `area:alerts`, `area:docs`
- `type:feature`, `type:bug`, `type:tech-debt`, `type:ops`
- `status:blocked`, `status:needs-data`, `status:ready`

Recommended milestones:

- `Sprint 3.2 Closure`
- `Sprint 4 Regime Independence`

## gh CLI Workflow (Default)

Use `gh` for all GitHub tracking operations.

Create issue:

```bash
gh issue create \
  --title "[S4-01] Multi-signal regime scoring engine" \
  --label "sprint:s4,area:regime,type:feature,status:ready" \
  --milestone "Sprint 4 Regime Independence" \
  --body-file /tmp/issue_body.md
```

List sprint issues:

```bash
gh issue list --label "sprint:s4" --limit 200
```

View one issue:

```bash
gh issue view 123
```

Create PR linked to issue:

```bash
gh pr create --title "S4-01: implement multi-signal regime scoring" --body-file /tmp/pr_body.md
```

## Session Refresh Protocol

At start of a new working session, refresh context from both sources:

1. Read current sprint docs in `docs/roadmap/`.
2. Query GitHub sprint issues with `gh issue list`.
3. Reconcile drift (if any) between doc status and issue status.

## Decision Rule

- If there is conflict:
  - roadmap files define intended scope and acceptance,
  - GitHub issues define current execution state,
  - update both immediately when scope/status changes.
