---
title: Setup Recognition Patterns
tags:
  - finding-opportunities
  - iv-rank
  - pattern-recognition
  - trade-entry
  - premium-selling
  - volatility
status: draft
aliases:
  - High-Probability Setups
  - Options Setup Patterns
related:
  - "[[IV-Rank]]"
  - "[[Earnings-Overview]]"
  - "[[Market-Condition-Classification]]"
  - "[[Implied-Volatility]]"
  - "[[Iron-Condor]]"
  - "[[Short-Straddle]]"
  - "[[Gamma-Walls-Call-Put]]"
  - "[[Gamma-Regime-and-GEX]]"
---

# Setup Recognition Patterns

Recognizing a setup before it fully develops separates reactive trading from anticipatory trading. The five patterns below each carry a mechanical trigger, a preferred structure, and a known failure mode. They are asymmetric probability filters — conditions where reward-to-risk skews favorably enough to justify a defined-risk position.

> [!note]
> "High-probability" means the setup resolves in the expected direction more often than not — not that individual trades are guaranteed. Always size for the full loss.

---

## 1. IV Compression Coil

**Trigger:** [[IV-Rank]] falls below 20, then turns upward on 2+ consecutive sessions. Price action is coiling (narrowing ATR or Bollinger Bands).

**Strategy:** Buy a [[Short-Straddle]] or ATM debit spread, 30–45 DTE. Long vega is the primary edge — the trade profits from volatility expansion regardless of direction.

**Outcome (rule of thumb):** When IV rank breaks above 25 after spending time below 15, expansion tends to continue in liquid index underlyings. Less reliable for single-name equities.

![[chart-iv-compression-coil.png]]

> [!warning]
> Low-vol regimes can persist for months. A coil entered too early bleeds theta with no payoff. Avoid this pattern when [[Market-Condition-Classification]] reads "calm trending."

---

## 2. Mean-Reversion After Spike

**Trigger:** Underlying moves more than 2 ATR in one session on elevated volume. [[IV-Rank]] is above 70. No pending binary event (if earnings-related, use [[Earnings-Overview]] instead).

**Strategy:** Sell premium into the spike — short strangle or iron condor. Elevated IV and likely price mean-reversion are dual tailwinds. Data-backed for index products; less reliable for single-name equities with idiosyncratic catalysts.

> [!warning]
> If the spike starts a trend rather than an overreaction, short premium in the direction of the move produces runaway losses. Use defined-risk spreads unless you have a hard stop-loss protocol in place.

---

## 3. Support/Resistance Hold

**Trigger:** Underlying tests a price level (prior swing, round number) three or more times without breaking. IV rank is moderate (30–60).

**Strategy:** Sell puts at or just below support, or calls at or just above resistance. Target 0.20–0.30 delta strikes, 21–35 DTE. Rule of thumb: multi-touch levels carry more technical weight than single-touch levels.

> [!warning]
> Levels break — often violently on the fourth touch, as stop clusters accumulate there. Define maximum loss at strike selection, not after the break.

---

## 4. Pre-Earnings IV Accumulation

**Trigger:** [[IV-Rank]] crosses 50 and is rising, with earnings confirmed 10–14 days out. The earnings expiry carries at least 5 IV points of premium over the next expiry.

**Strategy:** Enter a defined-risk [[Iron-Condor]] or iron butterfly 7–10 DTE before the announcement, collecting at least 1/3 of the wing width. You are selling the progressive IV build, not the event itself.

> [!warning]
> Earnings dates shift. If the event moves outside your expiry, the structure no longer brackets it. Confirm the date from two sources before entry. IV can also keep rising after entry, producing mark-to-market losses even if the thesis is correct.

---

## 5. Post-Earnings IV Crush Recovery

**Trigger:** Earnings session closes. IV drops 40–60% (the crush). IV rank is still above 30 — residual elevation persists.

**Strategy:** Sell short-dated premium in the next clean expiry (7–14 DTE), not the one that contained the event. Short strangle or narrow iron condor. The window is 1–2 sessions; the edge dissipates quickly as residual IV normalizes.

> [!warning]
> A secondary catalyst hitting within the 7–14 DTE window — analyst action, sector news, macro shock — can re-inflate IV and reverse a newly established short-premium position. Check the economic calendar before entry.

---

## Summary

| Pattern | IV Rank | Primary Edge | DTE Target |
|---|---|---|---|
| IV Compression Coil | < 20, turning up | Long vega | 30–45 |
| Mean-Reversion Spike | > 70 at spike | IV decay + price reversion | 21–35 |
| Support/Resistance Hold | 30–60 | Theta + containment | 21–35 |
| Pre-Earnings Accumulation | > 50, rising | Sell pre-event IV build | 7–10 before event |
| Post-Earnings Crush Recovery | > 30, residual | Residual IV decay | 7–14 |

> [!tip]
> Screen systematically: use the [[IV-Rank]] scanner and [[Market-Condition-Classification]] regime filter to narrow the universe to 5–10 candidates before evaluating chart patterns. Experienced traders filter first, study second.

## Layer 0 — Gamma Regime Check

Before applying any of the five patterns above, check the GEX regime. Pattern 2 (Mean-Reversion Spike) and Pattern 3 (Support/Resistance Hold) rely on price containing within a range. In a **negative gamma** environment (SPX below the HVL), dealer hedging amplifies moves rather than reverting them — both patterns have lower reliability.

In **positive gamma**, patterns 2 and 3 are reinforced: dealer flows actively push price back toward the center. The [[Gamma-Walls-Call-Put|Call Wall and Put Wall]] provide strike-level anchors for spread placement.

Check the GEX regime daily at market open. See [[Gamma-Regime-and-GEX]] for the full framework.
