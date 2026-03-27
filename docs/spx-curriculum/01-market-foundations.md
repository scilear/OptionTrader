# Module 1 — SPX Options: Structural Factors That Create Opportunity

## Learning Objectives

- Understand the structural features of SPX options that make vol surface signals possible and persistent.
- Understand why execution quality is not a secondary concern — it often dominates whether an edge is realizable.
- Build the right mental model before interpreting tool outputs.

---

## 1) What Makes SPX Options Different

SPX options are cash-settled European-exercise options on the S&P 500 index. These are not small details — they shape strategy design in direct ways.

**Cash settlement** means there is no assignment risk. When an SPX option expires in-the-money, you receive (or pay) the cash value of the intrinsic payoff. You never get assigned stock. This simplifies position management but also means SPX options do not benefit from early-exercise value, which is why European-exercise works cleanly.

**European exercise** means you cannot exercise early. For strategies built on implied vol signals rather than directional payoffs, this is largely irrelevant — you're rarely planning to hold to expiry anyway. But it matters when comparing SPX to SPY or ES options, which have American or futures-style exercise.

**Weekly and monthly expiries coexist.** SPXW contracts expire every Friday (and sometimes mid-week). Monthly SPX contracts expire on the third Friday. This creates a rich but uneven term structure: front-week expiries can be extremely sensitive to near-term events, while monthly expirations have a smoother vol surface. OptionTrader groups quotes into DTE buckets (21D, 30D, 45D by default) to smooth over this complexity, but understanding it helps interpret term structure anomalies.

---

## 2) The Structural Factors That Create the Vol Surface's Shape

Understanding *why* the vol surface has its characteristic shape is the prerequisite for understanding when that shape is distorted.

**Persistent left skew.** SPX puts are structurally more expensive than equidistant calls. This is not because the market expects a crash — it's because large institutional investors own equity portfolios and need to buy put protection. This demand for downside insurance is large, relatively inelastic, and continuous. The option sellers who absorb it demand a premium. The result is a persistent negative risk reversal (RR25 < 0). It has been a stable feature of equity index options for decades. It is not a pricing error; it is compensation for structural risk.

**Smile curvature.** Both wings tend to be elevated relative to ATM. This reflects the market's acknowledgment that actual returns have fat tails — large moves (in either direction) are more probable than a normal distribution would predict. It also reflects uncertainty about future volatility levels: if you don't know whether vol will be 15% or 30%, you price options to be safe against both scenarios, which inflates wings relative to a simple ATM estimate.

**Event-driven term structure.** Near-dated IV spikes around known risk events (FOMC, CPI, earnings seasons). The front of the term structure absorbs this premium; the back remains anchored to longer-run uncertainty. After the event passes, front vol decays rapidly. This creates recurring patterns in term slope behavior that OptionTrader's TERM_KINK alert is designed to identify.

---

## 3) Where Edge Actually Comes From

OptionTrader is not a directional tool. It does not forecast whether the S&P will rise or fall. It looks for *relative-value dislocations* within the vol surface — moments when one dimension of the surface is significantly stretched relative to its own recent history.

The edge candidates are:

- **Skew dislocations** (RR25 extreme): put wing or call wing repriced unusually relative to the other.
- **Convexity dislocations** (FLY25 extreme): both wings priced unusually relative to ATM.
- **Term structure dislocations** (TERM kink): a specific maturity is out of line with its neighbors.

Crucially, **the edge is not "signal seen." The edge is "signal survived all friction and process gates."** A strong z-score in a sparse dataset, or an extreme RR25 when spreads are 20% wide, is not edge — it is an artifact. The multi-gate architecture of OptionTrader (z-score → persistence → worst-case → regime) exists to separate real dislocations from noise.

---

## 4) Why Execution Quality Dominates

Options on SPX are liquid by equity standards, but individual strikes and expiries vary enormously. A 25-delta put in a 30-day expiry on a normal day might be quoted at a 1% spread. A 10-delta put in the front week around a volatile event might have a 10–20% spread. If your strategy requires collecting a vol edge of 2%, a 10% spread renders that edge unreal.

This is why OptionTrader computes both `*_mid` and `*_worst` versions of every metric. Mid is theoretical. Worst-case is what you actually get if every fill is at the adverse side. The worst-case gate in alert logic exists specifically to catch cases where the signal is real at mid but not executable at real prices.

When a signal's z-score on the worst-case metric is as large as the mid-metric z-score, the edge is robust to execution. When worst-case significantly underperforms mid, the dislocation may exist only in the quoted spread, not in the tradeable market.

---

## 5) The IB/yfinance Source Context

OptionTrader ingests from Interactive Brokers (primary) or yfinance (fallback). This distinction matters for interpretation:

**IB data** is live intraday quote data from real market makers. It reflects current bid/ask and real-time IV. It is higher quality for execution analysis but requires TWS or Gateway to be running.

**yfinance data** is delayed and based on the last trade or composite quote. Spread quality information is less reliable. Worst-case metrics computed from yfinance data are less trustworthy because the bid/ask may be stale.

When you see a source transition in the Metric Explorer chart (a color change in the source indicator), treat any apparent signal around that transition with extra skepticism. The shape you see may reflect a data quality change, not a market move.

---

## 6) Practical Checklist Before Any Analysis

Before interpreting any alert or chart move:

1. Check source context: is this IB or yfinance data? Was there a source transition near the move?
2. Check coverage: are all expected expiry buckets present? (`metrics_rows`, `iv_points` in pipeline logs)
3. Check cadence: is the chart shape built from many closely-spaced points, or from a few sparse ones? (Chart caption: `Points`, `median gap`, `max gap`)
4. Check the worst-case variant: does `*_worst` confirm the direction and magnitude seen in `*_mid`?

If any of these checks fail, the signal is in a research-only state until the data context clarifies.

---

## 7) Drill

Take three historical alerts from OptionTrader and for each one answer:

1. What was the data source, and was there any source transition near the alert?
2. How many points built the signal window? Was the chart dense or sparse?
3. Did the worst-case metric confirm the mid metric signal? By how much?
4. Which of these three factors — coverage, cadence, or execution quality — would have been most likely to invalidate this alert if it had failed?
