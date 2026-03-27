# Module 4 - Combo Playbooks (Hypothesis to Structure)

## Learning Objectives

- Map validated alerts to structure families with clear rationale.
- Understand when not to map a signal to a live structure.
- Keep strategy complexity proportional to evidence quality.

## Playbook A - RR Dislocation

### Hypothesis

Skew asymmetry is temporarily stretched and may normalize.

### Typical structure family

- risk-defined skew-sensitive spread (keep leg count minimal).

Current system template link (`src/core/trade_ideas.py`):

- `SkewFade_PutSpread`
- legs: sell `-0.25P`, buy `-0.10P`

Rationale link:

- if put wing is unusually rich vs call wing and thesis is normalization,
- a defined-risk put spread can express partial skew fade while bounding tail exposure.

### Best context

- strong mid + worst agreement,
- stable data integrity,
- acceptable spread/tradability,
- no contradictory regime suppression.

### Failure modes

- skew keeps steepening in stress,
- persistence collapses quickly (false burst),
- execution friction erodes expected edge.

Validation process before using this template:

1. `rr25_mid` and `rr25_worst` both extreme in same direction,
2. persistence satisfied,
3. tradability score acceptable,
4. regime/event context does not justify continuing skew expansion.

## Playbook B - FLY Dislocation

### Hypothesis

Smile convexity (wings vs ATM) is misaligned and may normalize.

### Typical structure family

- fly-oriented defined-risk structure.

Current system template link (`src/core/trade_ideas.py`):

- `Fly_1x2x1`
- example legs around put wing/ATM put region

Rationale link:

- if wings are mispriced relative to center, fly-type payoff can target convexity normalization.

### Best context

- multi-snapshot persistence,
- no severe spread degradation,
- neighboring buckets provide partial confirmation.

### Failure modes

- one-sided acceleration continues,
- event repricing justifies sustained convexity distortion.

Validation process:

1. verify decomposition (`W = 0.5*(C25+P25)`, `A = ATM`) and identify wing-led vs center-led move,
2. confirm `fly25_worst` consistency,
3. reject if spread quality makes multi-leg execution fragile.

## Playbook C - TERM Kink

### Hypothesis

Front-vs-back maturity relation is temporarily distorted.

### Typical structure family

- calendar/diagonal family with tight risk controls.

Current system template link (`src/core/trade_ideas.py`):

- `ATM_Calendar`
- conceptually: short front ATM, long back ATM

Rationale link:

- if front/back ATM relation is temporarily distorted, calendar logic can express expected slope normalization.

### Best context

- coherent maturity-pair behavior,
- no immediate event shock that explains persistent front premium,
- realistic carry/slippage assumptions.

### Failure modes

- event-driven term premium remains structurally elevated,
- carry and spread costs dominate expected normalization.

Validation process:

1. verify event context (pre/post-event) before assuming mean reversion,
2. confirm `term_slope_worst` and persistence,
3. estimate carry/slippage burden.

## Structure Selection Rubric

Choose the simplest structure that passes all of these:

1. expresses the core hypothesis,
2. has explicit max loss,
3. remains viable under realistic execution,
4. can be monitored with clear invalidation criteria.

## Signal-to-Strategy Mapping Table (Process, not recipe)

| Signal family | Primary question | Candidate strategy branch | What confirms | What blocks |
|---|---|---|---|---|
| RR_EXTREME | is skew temporary mispricing or structural stress? | reversion skew-fade, continuation stance, or no-trade | worst-case + persistence + tradability + regime coherence | stress acceleration, weak execution, poor data integrity |
| FLY_EXTREME | is convexity dislocation temporary or event-justified? | fly normalization, continuation hold-off, or no-trade | decomposition clarity + worst-case + stable data | one-point outlier, center-led event repricing, wide spreads |
| TERM_KINK | is front/back mismatch transient or justified by calendar? | calendar normalization, event-aware delay, or no-trade | post-event confirmation + worst-case + carry viability | pre-event risk concentration, persistent justified front premium |

This table is intentionally conditional. It maps reasoning to structures; it does not output automatic trades.

## Branch Selection Rule (Explicit)

For each alert family, choose one branch before choosing a structure:

1. **Reversion branch**: dislocation likely temporary and conditions stable.
2. **Continuation branch**: distortion likely structural or still accelerating.
3. **No-trade branch**: signal exists but integrity/execution/risk gates are weak.

Only branch 1 should proceed directly to a template trade idea.

## Drill

For each alert family, draft two candidates:

- one conservative structure,
- one advanced structure.

Then explain why the conservative one should usually be default unless extra evidence exists.
