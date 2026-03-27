# Module 8 - FLY25 Shape Atlas

## Learning Objectives

- Understand what FLY25 measures beyond a formula.
- Recognize recurring FLY shape regimes and false positives.
- Use a rationale process for convexity-oriented combo decisions.

## 1) Formula and Meaning

For maturity `T`:

- `FLY25(T) = 0.5 * (sigma(+0.25, T) + sigma(-0.25, T)) - sigma(ATM, T)`

Interpretation:

- positive FLY25: wings are expensive versus ATM,
- negative FLY25: ATM is rich versus wings.

In OptionTrader:

- midpoint signal: `fly25_mid`
- pessimistic signal: `fly25_worst`

## 2) Shape Atlas (Pattern -> Story -> Risk)

### Shape A - Stable slightly positive plateau

- Story: persistent wing premium in calm-to-normal conditions.
- Risk: low standalone edge; often not enough for live trade.

### Shape B - Sudden positive spike then partial reversion

- Story: temporary tail-demand shock or local wing repricing.
- Risk: one-point outlier risk; verify persistence.

### Shape C - Multi-snapshot positive acceleration

- Story: building convexity stress.
- Risk: early mean-reversion entries can be punished.

### Shape D - Cross below baseline then hold negative

- Story: center (ATM) repriced up relative to wings, or wing premium decay.
- Risk: regime transition; old assumptions may fail.

### Shape E - High-frequency alternation around zero

- Story: microstructure noise or unstable inputs.
- Risk: elevated false-positive probability.

## 3) FLY Decomposition Logic

Given:

- `W = 0.5 * (C25 + P25)` (average wings),
- `A = ATM`.

Then:

- `FLY = W - A`.

Interpretation split:

- `W` up with `A` stable -> wing-driven stress,
- `A` up with `W` stable -> center-driven repricing,
- both move -> compare magnitudes before deciding thesis.

Process rule:

- identify whether the distortion is wing-led or center-led before selecting structure.

## 4) No-Magic-Number FLY Decision Process

1. Is current FLY extreme vs its own recent history?
2. Does `fly25_worst` confirm direction and significance?
3. Is persistence satisfied?
4. Are cadence/coverage/source clean?
5. Does regime context support normalization thesis?

If any core gate fails, downgrade to `Watch` or `Research`.

## 5) Mapping FLY to Combo Thinking

When considering a fly-oriented expression:

- ensure max-loss is explicit,
- avoid overfitting strike selection to one snapshot,
- require clear invalidation trigger (signal decay or execution deterioration).

## 6) Worked Micro-Examples

Example 1:

- `C25=0.24`, `P25=0.28`, `ATM=0.23`
- `FLY=0.5*(0.24+0.28)-0.23=0.03`
- reading: wings materially rich vs center.

Example 2:

- `C25=0.20`, `P25=0.23`, `ATM=0.24`
- `FLY=0.5*(0.20+0.23)-0.24=-0.025`
- reading: center rich vs wings.

## 7) Drill

Pick 10 historical `FLY_EXTREME` alerts and classify each as:

- wing-driven,
- center-driven,
- mixed,
- unclear due to data integrity.

For each, assign decision label and one invalidation condition.
