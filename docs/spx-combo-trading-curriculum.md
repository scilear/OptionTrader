# SPX Option Combo Trading Curriculum — Navigation Hub

This hub links to the modular curriculum in `docs/spx-curriculum/`. Start here for orientation; go to the module files for actual learning content.

## Who This Is For

- Traders who understand basic options but want a systematic, signal-driven SPX process.
- Analysts moving from statistical signals to executable trade decisions.
- Anyone who needs a shared framework for reviewing and post-morteming decisions made with OptionTrader.

## Prerequisites

- Basic options vocabulary: calls, puts, spreads, expiry, moneyness.
- Comfort reading time series charts.
- Willingness to keep a written decision log.

## Learning Path

The curriculum is organized in four phases. Complete them in order. Do not skip to combo playbooks before you understand what the metrics actually measure and why.

### Phase 1 — Foundations (why these markets, why these metrics)

These modules build the conceptual model before any tool usage. If you skip them, you will pattern-match alerts without understanding what they represent.

| Module | File | What you will understand |
|--------|------|--------------------------|
| 1 | [01-market-foundations.md](spx-curriculum/01-market-foundations.md) | Why SPX vol surface has persistent shape; where edge actually comes from; why execution quality is not secondary |
| 2 | [02-surface-metrics-deep-dive.md](spx-curriculum/02-surface-metrics-deep-dive.md) | Why RR25/FLY25/TERM are the right decomposition; what each captures economically; why delta-based, why 25Δ, why z-scores not absolute thresholds; why worst-case gate matters |

### Phase 2 — Reading the Tool

These modules bridge from the concepts to what OptionTrader actually shows you.

| Module | File | What you will understand |
|--------|------|--------------------------|
| 3 | [03-alert-to-trade-process.md](spx-curriculum/03-alert-to-trade-process.md) | The five-gate decision process; how to trace an alert through signal → data → regime → execution → risk gates |
| 4 | [04-combo-playbooks.md](spx-curriculum/04-combo-playbooks.md) | Mapping validated alerts to structure families; when *not* to map; branch selection before structure |
| 5 | [05-risk-execution-and-review.md](spx-curriculum/05-risk-execution-and-review.md) | Position-level and process-level risk rules; post-trade review loops |
| 5b | [05b-greeks-and-position-management.md](spx-curriculum/05b-greeks-and-position-management.md) | Greek profiles per template; portfolio aggregation; what-if scenarios; adjustment triggers |

### Phase 3 — Metric Workbooks (numerical practice)

Deep-dive workbooks for each metric family. Work through these once you have finished Phase 1 and 2.

| Module | File | Content |
|--------|------|---------|
| 7 | [07-rr25-numerical-workbook.md](spx-curriculum/07-rr25-numerical-workbook.md) | RR25 numerical scenarios; end-to-end tool workflow; decision archetypes |
| 8 | [08-fly25-shape-atlas.md](spx-curriculum/08-fly25-shape-atlas.md) | FLY25 shape atlas; wing-led vs center-led decomposition |
| 9 | [09-term-kink-event-framework.md](spx-curriculum/09-term-kink-event-framework.md) | TERM kink identification; event calendar interaction |

### Phase 4 — Practice and Case Studies

| Module | File | Content |
|--------|------|---------|
| 6 | [06-case-studies-and-drills.md](spx-curriculum/06-case-studies-and-drills.md) | Structured drills against real alerts |
| 10 | [10-decision-assistant-blueprint.md](spx-curriculum/10-decision-assistant-blueprint.md) | Blueprint for consistent decision capture |
| 11 | [11-real-world-casebook.md](spx-curriculum/11-real-world-casebook.md) | Annotated real-market examples |
| 12 | [12-strategy-handbook.md](spx-curriculum/12-strategy-handbook.md) | Reference handbook for all structure templates |
| 13 | [13-continuation-strategy-cards.md](spx-curriculum/13-continuation-strategy-cards.md) | Quick-reference cards for each signal family |

## Companion Documents

- **Pattern recognition playbook** (chart shape triage + data-quality decision tree): [optiontrader-pattern-playbook.md](optiontrader-pattern-playbook.md)
- **QuantConnect validator guide**: [quantconnect-validator.md](quantconnect-validator.md)
- **Decision scorecard templates**: `docs/templates/decision-scorecard-template.md` / `.csv`

## Study Method

For each module:
1. Read the whole module before using the tool.
2. Do the drill exercise before moving on.
3. Write one short takeaway in your decision journal.

Progress rule: do not move to live structure selection until your last 20 documented decisions show consistent use of all five gates.

## Track Checkpoints

**Beginner** (Phase 1 complete):
- Can explain what RR25, FLY25, and TERM capture economically (not just their formulas).
- Can explain why SPX skew is persistently negative and what that means for signals.
- Can correctly classify 10 historical alerts by metric family.

**Intermediate** (Phase 2 complete):
- Can run the full five-gate process on a live alert and produce a written gate evidence card.
- Has at least three documented high-quality rejections (where no-trade was the right call).

**Advanced** (Phases 3 and 4 in progress):
- Can decompose RR25 moves into wing-led vs spread-led.
- Produces monthly pattern-performance reviews.
- Has updated at least one decision rule from review evidence.
