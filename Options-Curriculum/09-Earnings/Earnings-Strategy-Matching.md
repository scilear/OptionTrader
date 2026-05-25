---
title: Earnings Strategy Matching
tags:
  - earnings
  - decision-framework
  - options-strategy
  - IV
  - premium
aliases:
  - Earnings Decision Framework
  - Which Earnings Strategy to Use
status: draft
related:
  - "[[Earnings-IC-Playbook]]"
  - "[[Earnings-Straddle-Strangle]]"
  - "[[Earnings-Tools]]"
  - "[[Implied-Move-vs-Actual-Move]]"
  - "[[Iron-Condor]]"
  - "[[Debit-Spreads]]"
  - "[[IV-Rank-and-Percentile]]"
---

# Earnings Strategy Matching

Not every earnings event warrants the same trade. The decision between selling premium and buying premium — or between a directional and a neutral structure — depends on a handful of measurable inputs. This note provides a five-question framework to land on the right structure before every earnings event.

> [!warning]
> Earnings trades carry binary event risk. The stock can gap far beyond the implied move in either direction. No framework eliminates that risk — it only helps you select the structure best suited to the situation. Size all earnings positions at 1–2% of portfolio or less.

---

## The Five-Question Framework

### Q1: Is historical IV overestimating the actual move?

Check what percentage of past earnings produced a realized move smaller than the implied move. Use [[Earnings-Tools]] to pull this data.

- **> 60% of past earnings: implied > realized** → The options market is consistently pricing in too much movement. This is a premium-selling environment. Consider an [[Iron-Condor]] (undefined risk managed) or a defined-risk IC spread. See [[Earnings-IC-Playbook]].
- **< 40% of past earnings: implied > realized** → The stock regularly surprises the market. This is a premium-buying environment. Consider a straddle, strangle, or debit spread. See [[Earnings-Straddle-Strangle]].
- **40–60%: ambiguous** → No strong edge either way. Either reduce size significantly or pass the trade.

> [!note]
> This statistic is sometimes called the "earnings beat rate for options." It is data-backed when computed over at least 8 prior earnings events. Fewer than 8 samples is too noisy to trade mechanically.

### Q2: Do I have directional conviction?

- **Yes** → Use a [[Debit-Spreads|debit spread]] in the direction of the expected move. This caps both your risk and your reward, and keeps the trade defined.
- **No** → Use a neutral structure: IC/IC spread if selling, straddle/strangle if buying.

> [!tip]
> "Directional conviction" means you have a specific reason — earnings surprise expectation, analyst revision trend, sector catalyst — not just a feeling. Conviction without a thesis is noise.

### Q3: Is the implied move unusually large or small vs. history?

Compare today's implied move (derived from ATM straddle price ÷ stock price) to the historical distribution of actual moves. [[Earnings-Tools]] can compute this.

- **Implied move is at the high end of the historical distribution** → IV is elevated relative to history; the post-earnings crush will likely be large. Lean toward selling.
- **Implied move is at the low end** → The market may be underpricing the event. Lean toward buying.

### Q4: What is the stock's volatility profile?

| Profile | Examples | Implication |
|---|---|---|
| High-growth, high-beta | NVDA, TSLA, SMCI | Actual moves regularly exceed implied moves; selling is dangerous |
| Mid-cap growth | CRM, PANW | Mixed history; check data carefully |
| Large-cap blue-chip | AAPL, MSFT, JPM | More mean-reverting; selling is statistically safer |

> [!danger]
> Selling premium on high-growth / high-beta names around earnings is one of the most common ways retail traders blow up a position. A single 20%+ gap in a sold iron condor can erase months of premium income. These names require extra scrutiny or should be avoided entirely for premium-selling strategies.

### Q5: Decision Matrix

| Historical IV overestimates move | Directional conviction | Implied move vs. history | Suggested structure |
|---|---|---|---|
| Yes (>60%) | No | High end | IC or IC Spread |
| Yes (>60%) | Yes | High end | Debit spread (in trend direction) |
| No (<40%) | No | Low end | Straddle or Strangle |
| No (<40%) | Yes | Low end | Debit spread (in direction) |
| Ambiguous (40–60%) | Either | Neutral | Reduce size or pass |

---

## The Meta-Rule

> [!tip]
> The playbook is only as good as your data — always check historical earnings move vs. implied move before every trade. Do not rely on memory or reputation. A stock that was a reliable premium-sell two years ago may have changed its character entirely.

Run the historical check in [[Earnings-Tools]] before every event. Record your findings in a trade journal so you build your own dataset over time.

---

## Related Notes

- [[Earnings-IC-Playbook]] — step-by-step setup and management for earnings iron condors
- [[Earnings-Straddle-Strangle]] — when and how to buy premium around events
- [[Earnings-Tools]] — data sources and workflows for historical move analysis
- [[Implied-Move-vs-Actual-Move]] — how to compute and interpret the implied move
- [[IV-Rank-and-Percentile]] — contextualizing IV elevation before the event
