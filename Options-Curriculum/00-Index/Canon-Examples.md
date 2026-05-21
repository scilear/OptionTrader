---
title: Canon Examples Reference Sheet
tags: [meta, reference]
aliases: []
status: meta
related: []
---

# Canon Examples Reference Sheet

This document defines the standard example parameters used consistently across ALL curriculum notes. Every note that uses numerical examples must draw from these values — do not invent your own numbers.

## Underlyings

| Ticker | Price | Type | Notes |
|--------|-------|------|-------|
| SPX | 5000 | Index (cash-settled, European) | Tax-favorable (60/40 long-term treatment) |
| SPY | 500 | ETF (American exercise) | Tracks SPX 1/10 scale |
| AAPL | 200 | Large-cap equity | Tech sector proxy |
| MSFT | 400 | Large-cap equity | Tech sector proxy |
| NVDA | 900 | Large-cap equity | High-beta tech |
| GLD | 200 | Commodity ETF | Gold proxy |
| QQQ | 430 | Tech-heavy ETF | Leveraged to tech |

## IV Conditions

Use these labels and values consistently across all examples:

| Label | VIX | IVR (IV Rank) | IVP (IV Percentile) | Interpretation |
|-------|-----|---------------|-------------------|-----------------|
| **Calm** | 13 | 18% | 20% | Low volatility regime, complacent |
| **Normal** | 18 | 42% | 50% | Mean volatility, neutral regime |
| **Elevated** | 25 | 65% | 72% | Above-average vol, uncertainty |
| **Stressed** | 35 | 82% | 88% | High vol, risk-off, crisis-like |

## Standard DTE Scenarios

Use these DTE buckets consistently:

- **0DTE** — Same-day expiration (extreme gamma, theta burn)
- **7DTE** — 1-week expiration (short-term tactical)
- **21DTE** — 3-week expiration (standard short premium entry)
- **45DTE** — 6-7 week expiration (balanced gamma/theta)
- **90DTE** — 3-month expiration (lower theta, longer hold)
- **365DTE** — 1-year LEAPS (stock-replacement scale)

## Standard Spread Widths

### Index (SPX)

| Width | Purpose | Credit Ratio |
|-------|---------|--------------|
| $25-wide | Narrow (tight delta targets, high %ret) | Higher |
| $50-wide | Standard (balanced risk/reward) | Medium |
| $100-wide | Wide (low pin risk, lower credit) | Lower |

### Equity (SPY, AAPL, MSFT, NVDA, GLD, QQQ)

| Width | Purpose | Credit Ratio |
|--------|---------|--------------|
| $2.50-wide | Narrow (tight delta targets) | Higher |
| $5.00-wide | Standard (typical IC wings) | Medium |
| $10.00-wide | Wide (lower credit, defensive) | Lower |

## Standard Credit Targets

| Structure | Credit Target | Calculation |
|-----------|---------------|-------------|
| **Iron Condor (IC)** | 25% of total wing width | Sum both sides; credit = 0.25 × (put width + call width) |
| **Credit Spread (one-sided)** | 33% of spread width | Standard debit: 1/3 of max loss |
| **Cash-Secured Put (CSP)** | 1% of strike price per month minimum | Strike × DTE/365 × 0.01 |

## Standard Delta Targets at Entry

| Structure & Leg | Target Delta | Notes |
|-----------------|---------------|-------|
| CSP short put | 0.25Δ | 75% probability of expiring worthless |
| Credit spread short leg | 0.30Δ | ~70% win rate target |
| IC short legs (both sides) | 0.16Δ | ~84% PoE for each side |
| 0DTE IC short legs | 0.10Δ | Tighter pins for gamma risk |
| PMCC LEAPS long leg | 0.75Δ | Stock-replacement synthetic |
| PMCC short call | 0.30Δ | Roll consistently against long |
| LEAPS stock replacement | 0.75Δ | Replaces 75 shares synthetic value |

## Portfolio Parameters

### Account Size

**Standard portfolio size for all examples: $100,000**

### Position Limits

| Limit | Value | Purpose |
|-------|-------|---------|
| Max risk per trade | 2% of portfolio = **$2,000** | Drawdown control, compounding safety |
| Max notional per CSP | 5% of portfolio = **$5,000** | Cash collateral per single position |
| 0DTE max risk per trade | 0.5% = **$500** | Gamma safety margin |
| Max positions open | 3–5 | Manage concentration, monitor burden |

## Earnings Expected Move Examples

Use these for earnings-specific notes (actual history in parentheses):

| Stock | Implied Move | Historical Average | Notes |
|-------|--------------|-------------------|-------|
| AAPL | ±4.0% | ±3.2% | Larger expected post-guidance |
| NVDA | ±9.0% | ±8.5% | Sector volatility, market sentiment |
| MSFT | ±3.5% | ±2.8% | Lower than mega-cap peers |

## Standard Example Trade (Base Iron Condor)

Use this as the template IC in all examples unless explicitly stated otherwise:

### Setup
- **Underlying:** SPX at 5000
- **DTE:** 45 DTE
- **IV Condition:** Normal (VIX=18, IVR=42%)
- **Structure:** Iron Condor

### Legs

| Leg | Strike | Contract | Position | Quantity |
|-----|--------|----------|----------|----------|
| Put spread short | 4850 | SPX 45DTE | Sell | 1 put |
| Put spread long | 4800 | SPX 45DTE | Buy | 1 put |
| Call spread short | 5150 | SPX 45DTE | Sell | 1 call |
| Call spread long | 5200 | SPX 45DTE | Buy | 1 call |

### Metrics

| Metric | Value | Formula/Notes |
|--------|-------|---------------|
| **Max Width (each side)** | $50 | 4850 − 4800 = 50; 5200 − 5150 = 50 |
| **Credit Received** | $12.50 | $6.25 per side (25% IC rule) |
| **Max Loss** | $37.50 per spread | $50 width − $12.50 credit |
| **Max Profit** | $12.50 | Credit received (if both sides expire worthless) |
| **Profit Target** | $6.25 (50% of credit) | Exit at 50% max profit |
| **Stop Loss** | $25.00 (2× credit) | Hard exit at 2× loss |
| **Probability of Profit (PoE)** | ~68% | 0.16Δ targets ≈ 84% each side |

### Collateral & Risk

| Item | Value |
|------|-------|
| **Notional Collateral** | $5,000 per contract (SPX $50 × 100) |
| **Max Account Risk** | $3,750 per contract (2% of $100k portfolio) |
| **Account % Risk** | 3.75% | Well within 2% position limit |
| **% Return on Risk** | 33% | $12.50 credit ÷ $37.50 max loss |

---

## How to Use This Note

1. **Before writing any example:** Check this note for the underlying price, IV condition, DTE, and delta targets. Do not invent new values.

2. **Linking examples:** When you reference the standard IC trade, use [[Canon-Examples#Standard Example Trade (Base Iron Condor)|Standard IC 45DTE SPX]].

3. **Consistency across curriculum:** All notes should use the same underlying prices, IV labels, and delta targets. This creates a coherent learning arc without numerical confusion.

4. **When to deviate:** If a note requires a specific example (e.g., earnings trades, 0DTE tactics), note the deviation explicitly and explain why.

5. **Cross-reference:** Use [[WikiLink-Map]] to maintain logical flows between notes. Canon Examples should be linked from the introduction of every strategy note.

---

**Last updated:** 2026-05-20  
**Author:** Curriculum Lead  
**Status:** Reference (meta)
