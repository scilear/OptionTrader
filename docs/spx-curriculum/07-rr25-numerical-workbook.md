# Module 7 - RR25 Decision Workflow (Tool-Driven)

## Learning Objectives

- Move from verbal RR25 intuition to numeric interpretation.
- Understand how the same RR25 can come from different wing dynamics.
- Use OptionTrader outputs to move from RR signal to trade decision.
- Map validated RR conditions to structure selection with explicit rationale.

## 1) Formula Refresher

For maturity `T`:

- `RR25(T) = sigma(+0.25, T) - sigma(-0.25, T)`

Where:

- `sigma(+0.25, T)` is 25-delta call IV,
- `sigma(-0.25, T)` is 25-delta put IV.

In OptionTrader:

- midpoint estimate: `rr25_mid`
- pessimistic estimate: `rr25_worst`

## 2) Numerical Scenarios

### Scenario A - Baseline skewed market

- `sigma(+0.25, T) = 0.18`
- `sigma(-0.25, T) = 0.22`
- `RR25 = 0.18 - 0.22 = -0.04`

Interpretation:

- put wing richer than call wing,
- typical left-skew behavior for SPX.

### Scenario B - Strong fear repricing

- `sigma(+0.25, T) = 0.19`
- `sigma(-0.25, T) = 0.29`
- `RR25 = -0.10`

Interpretation:

- skew steepened materially,
- could be stress or temporary panic extension.

Decision implication:

- do not auto-mean-revert,
- require worst/persistence/regime checks.

### Scenario C - Skew flattening

- `sigma(+0.25, T) = 0.21`
- `sigma(-0.25, T) = 0.23`
- `RR25 = -0.02`

Interpretation:

- skew still negative but flatter,
- could reflect fear normalization or call-side demand increase.

### Scenario D - Apparent inversion

- `sigma(+0.25, T) = 0.24`
- `sigma(-0.25, T) = 0.22`
- `RR25 = +0.02`

Interpretation:

- unusual for many SPX states,
- can occur in localized regime shifts.

Decision implication:

- treat as context-sensitive,
- verify data integrity and event context before any continuation thesis.

## 3) Same RR25, Different Story

Target RR25: `-0.05`

Case 1:

- call `0.17`, put `0.22` -> `-0.05`
- narrative: call side soft, put side stable.

Case 2:

- call `0.24`, put `0.29` -> `-0.05`
- narrative: both wings elevated in stress, put still richer.

Both have same RR25, but regime and execution implications differ.

Process rule:

- always inspect absolute wing levels and recent wing trajectories, not only RR spread.

## 4) RR25 Decision Grid (Process-First)

Evaluate each RR candidate on these five dimensions:

1. **Extremeness** (relative to recent RR distribution)
2. **Robustness** (`rr25_worst` confirms)
3. **Persistence** (condition holds over required snapshots)
4. **Integrity** (coverage/cadence/source checks pass)
5. **Coherence** (regime/event context matches thesis)

Suggested action mapping:

- 5/5 strong: `Trade` candidate
- 3-4/5: `Watch`
- <=2/5: `Research` or `Reject`

## 5) End-to-End Tool Workflow (From Alert to Trade Prep)

This section replaces toy exercises with the actual operator flow.

### Step 1 - Confirm signal quality in Metric Explorer

In `Metric Explorer`:

1. Select metric `rr25_mid` and target bucket (`21D`, `30D`, or `45D`).
2. Check whether the latest move is extreme vs recent behavior.
3. Switch to `rr25_worst` and confirm same directional story.

Decision note:

- If `mid` and `worst` diverge, stop and downgrade to `Research`.

### Step 2 - Validate data integrity before interpreting shape

Still in chart view:

1. Read caption (`Points`, `median gap`, `max gap`).
2. Compare `Timeline` vs `Snapshot sequence` view.
3. Inspect source coloring for `IB`/`yfinance` transitions.

Decision note:

- If shape depends on sparse gaps or source switch artifacts, do not map directly to structure.

### Step 3 - Confirm alert context and gates in Alert Detail

In `Alert Detail`:

1. Verify `alert_type = RR_EXTREME`.
2. Confirm `zscore_mid`, `zscore_worst`, `persistence_count`.
3. Check `regime_label`, `tradability_score`, and `confidence_tier`.

Decision note:

- Strong candidate requires signal pass + acceptable tradability + no regime contradiction.

### Step 4 - Choose thesis before structure

Pick one explicit thesis:

- **Reversion thesis:** skew likely to normalize from extreme.
- **Continuation thesis:** skew likely to remain stressed.
- **No-trade thesis:** signal is not executable or not trustworthy.

If thesis is unclear, label `Watch` (not `Trade`).

### Step 5 - Map thesis to strategy family

For current system templates (`src/core/trade_ideas.py`):

- RR template: `SkewFade_PutSpread` (sell -0.25P, buy -0.10P).

Why this mapping exists:

- It expresses put-wing richening normalization in defined risk form.

When to avoid this mapping:

- stress continuation context,
- weak tradability,
- unresolved data integrity concerns.

### Step 6 - Prepare trade only after risk definition

Before any execution decision, write:

- max loss,
- invalidation trigger,
- size rule,
- what must improve if currently `Watch`.

Only then label one of: `Trade now`, `Watch`, `Research`, `Reject`.

## 6) RR Signal -> Strategy Mapping With Rationale

| RR condition | Interpretation | Candidate action | Why |
|---|---|---|---|
| extreme negative, worst confirms, persistence holds, execution acceptable | skew dislocation likely tradable | evaluate `SkewFade_PutSpread` | captures skew normalization with bounded risk |
| extreme negative but worst weak or execution weak | statistical move not executable | `Research` / `Watch` | protects from friction-dominated trades |
| less negative rebound with strong confirmation | skew normalization already underway | watch for better entry or skip | avoids late entry after major move |
| inversion/abnormal regime with event pressure | possible regime shift, not simple mean reversion | `Watch` / `Reject` | prevents forcing historical assumptions into new regime |

## 7) Validation Process for RR Trade Candidates

Use this checklist in order:

1. Signal validity (`zscore_mid`, `zscore_worst`, persistence)
2. Data validity (coverage, cadence, source continuity)
3. Context validity (regime + event narrative)
4. Execution validity (tradability + spread burden)
5. Risk validity (max loss + invalidation + size)

If any of 3-5 fails, do not promote to `Trade now`.

## 8) Real-World RR Decision Archetypes (Not Only Mean Reversion)

### Archetype A - Panic skew expansion (continuation risk high)

Observed pattern:

- RR becomes sharply more negative over multiple snapshots,
- put wing levels rise rapidly,
- regime context is stress-like.

Decision tendency:

- default to `Watch` or `Reject` for naive skew-fade,
- continuation or defensive stance may be more coherent than immediate reversion.

Why this matters:

- forcing mean reversion in accelerating stress is a common failure mode.

### Archetype B - Post-shock normalization (reversion probability improves)

Observed pattern:

- RR was extreme negative,
- then stops accelerating,
- worst-case and persistence remain valid while execution stabilizes.

Decision tendency:

- skew-fade structure becomes more plausible,
- still require explicit invalidation and size discipline.

### Archetype C - Call-side chase / skew flattening regime

Observed pattern:

- RR rebounds toward zero (or positive),
- call wing repricing dominates,
- event narrative favors upside demand.

Decision tendency:

- avoid automatically fading the move,
- continuation framing or no-trade can be more appropriate.

### Archetype D - Data artifact masquerading as RR dislocation

Observed pattern:

- isolated RR jump with sparse points,
- large cadence gaps or source transition near move,
- weak worst-case confirmation.

Decision tendency:

- `Research` until data integrity confirms.

## 9) Worked Exercise: Compute and Interpret RR25

For each row, compute RR25 and write a one-sentence interpretation. Include: is the level extreme or ordinary for SPX? What market narrative is consistent with it?

| Call 25d IV | Put 25d IV | RR25 | Interpretation |
|---|---|---|---|
| 0.19 | 0.24 |  |  |
| 0.22 | 0.25 |  |  |
| 0.26 | 0.27 |  |  |
| 0.25 | 0.22 |  |  |

Then for each row add:

- one data-quality check you would make before trusting this reading,
- one invalidation condition for a trade based on this level,
- one decision label (`Trade`, `Watch`, `Research`, `Reject`) with one-sentence rationale.

## 10) Common RR25 Reasoning Errors

- Treating absolute RR25 levels as universal rules (the same level is extreme in calm markets and ordinary in stress).
- Ignoring `rr25_worst` disagreement — divergence between mid and worst often means the signal is a spread artifact, not a real dislocation.
- Ignoring sparse cadence: a large RR25 move built on two or three data points in a wide gap window may be a sampling artifact.
- Assuming all large negative RR25 values are mean-reversion opportunities — stress continuation is also a valid regime and often the more dangerous mistake to fight.

## 10) Missing Tool Features and Workflow Plan (RR Module)

Current gaps that limit decision automation:

- No single screen that auto-renders all gate evidence for one alert.
- No explicit thesis selector (`reversion` vs `continuation` vs `no-trade`) in UI.
- No strategy mapping explainer panel that shows "why this template".
- No built-in invalidation/risk worksheet linked to each proposed trade idea.

Planned workflow enhancements:

1. **Decision Summary panel** in Alert Detail:
   - auto-populate gate evidence,
   - output suggested label (`Trade/Watch/Research/Reject`).
2. **Thesis selector + rationale capture**:
   - force explicit thesis before exporting idea.
3. **Strategy rationale block**:
   - show mapping from RR condition to template with blockers.
4. **Risk worksheet integration**:
   - require max loss/invalidation/size before trade export.

## 11) Integration with the Tool

In the app:

1. review `rr25_mid` and `rr25_worst` in Metric Explorer,
2. inspect gap statistics and source coloring,
3. check alert persistence and regime/tradability in Alert Detail,
4. define thesis and risk fields,
5. complete scorecard before any live decision.
