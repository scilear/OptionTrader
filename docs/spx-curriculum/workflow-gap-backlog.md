# Workflow Gap Backlog (Decision Automation)

This backlog tracks product gaps discovered while writing the curriculum.

## Goal

Move from "signal display" to "decision/reflexion assistant" with auditable rationale.

## Priority 1 - Decision Summary in Alert Detail

- Problem: gate evidence is fragmented across charts and detail tables.
- Proposed feature:
  - auto-calculate Signal/Data/Regime/Execution/Risk gate status,
  - display evidence values beside each gate,
  - output suggested decision label.
- Outcome target: reduce subjective inconsistency between analysts.

## Priority 2 - Thesis Capture

- Problem: users jump from alert to structure without explicit thesis.
- Proposed feature:
  - required thesis selector (`reversion` / `continuation` / `no-trade`),
  - required rationale text field,
  - persist thesis with alert decision artifact.
- Outcome target: improve post-mortem explainability.

## Priority 3 - Strategy Mapping Explainability

- Problem: template appears without clear why/how fit.
- Proposed feature:
  - show mapping explanation per alert family,
  - display blockers that should prevent template use,
  - include confidence badge.
- Outcome target: avoid blind template usage.

## Priority 4 - Risk Worksheet Gate

- Problem: trade ideas can be exported before explicit risk definition.
- Proposed feature:
  - require max loss, invalidation, and size inputs,
  - block export if fields missing.
- Outcome target: harden risk discipline.

## Priority 5 - Validation Dashboard

- Problem: no direct feedback loop on decision quality.
- Proposed feature:
  - track decision label outcomes over time,
  - monitor false-positive and missed-opportunity rates,
  - review by alert family/regime.
- Outcome target: evidence-driven process improvement.

## Priority 6 - Real-World Casebook

- Problem: educational modules can still feel abstract without concrete historical examples.
- Proposed feature:
  - add curated case library with timestamped snapshots,
  - include signal decomposition, gate evidence, chosen branch (reversion/continuation/no-trade),
  - include outcome review and lesson.
- Outcome target: teach decision quality with realistic context, not toy scenarios.

Status:

- Initial version delivered in `docs/spx-curriculum/11-real-world-casebook.md`.
- Next step is to automate case generation directly from saved alert outcomes.
