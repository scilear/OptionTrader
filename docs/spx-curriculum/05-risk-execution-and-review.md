# Module 5 - Risk, Execution, and Review

## Learning Objectives

- Build robust pre-trade and post-trade discipline.
- Reduce process drift under stress conditions.
- Convert outcomes into improved rules.

## 1) Pre-Trade Risk Controls

Mandatory before entry:

- explicit max loss,
- size rule tied to account and correlation exposure,
- invalidation condition,
- decision label and rationale documented.

If any item is missing, no trade.

## 2) Execution Controls

Execution checklist:

1. check current spread condition vs expected,
2. check liquidity consistency across intended legs,
3. confirm expected slippage does not consume thesis edge,
4. avoid forced entries during unstable data quality windows.

## 3) In-Trade Monitoring

Track:

- whether core signal condition persists,
- whether execution conditions deteriorate,
- whether invalidation is reached.

Do not improvise new thesis mid-trade unless fully documented.

## 4) Post-Trade Review Loop

For each outcome, classify:

- thesis right / execution right,
- thesis right / execution wrong,
- thesis wrong / execution right,
- thesis wrong / execution wrong.

This avoids simplistic "PnL good means process good" thinking.

## 5) Monthly Process Audit

Audit items:

- rule breaches count,
- false-positive trade rate,
- high-quality rejection rate,
- outcomes by alert family,
- repeated failure pattern and corresponding rule updates.

## 6) Drill

Review last 20 decisions and produce:

- top 3 repeated errors,
- one rule change per repeated error,
- evidence that next decisions adopted those changes.
