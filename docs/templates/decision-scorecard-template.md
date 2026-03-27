# Decision Scorecard Template

Use one row per candidate alert/trade decision.

## Candidate Metadata

- Timestamp:
- Alert type:
- Expiry bucket:
- Source context (IB/yfinance):
- Coverage context (`metrics_rows`, `iv_points`):

## Signal and Quality Inputs

- zscore_mid:
- zscore_worst:
- Persistence passed (yes/no):
- Tradability score:
- Regime label:

## Scoring (1-5)

| Category | Score | Notes |
|---|---|---|
| Signal strength |  |  |
| Worst-case robustness |  |  |
| Execution quality |  |  |
| Regime alignment |  |  |
| Payoff clarity |  |  |
| Process discipline |  |  |
| **Total** |  |  |

## Decision

- Decision label: `Trade now` / `Watch` / `Research only` / `Reject`
- Structure candidate:
- Max loss:
- Invalidation condition:

## Outcome Review (fill later)

- Result:
- What went right:
- What failed:
- Rule update:
