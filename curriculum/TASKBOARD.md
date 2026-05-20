---
title: Options Trading Curriculum — Build Taskboard
tags: [curriculum, taskboard, meta]
status: active
created: 2026-05-20
---

# Options Trading Curriculum — Build Taskboard

## Complexity / Model Map

| Level | Model | When to use |
|-------|-------|-------------|
| 1 | Haiku | Definitions, templates, short factual notes |
| 2 | Sonnet | Strategy mechanics, practical guides, analysis |
| 3 | Opus | Complex strategies, nuanced risk, chart code, backtested rules |

## Global Prompt Prefix (prepend to every task prompt)

> You are building an Obsidian vault options trading curriculum. Write one atomic Markdown note. Requirements:
> - YAML frontmatter: `title`, `tags`, `aliases`, `status: draft`, `related` (list of [[WikiLinks]])
> - Use `[[WikiLinks]]` throughout the body for cross-references
> - Be practical and tested — state clearly when advice is data-backed vs rule-of-thumb
> - Always include a `> [!warning]` callout for key risks
> - No ASCII art. Reference charts by filename: `![[chart-name.png]]`
> - Target length: 400–700 words unless specified otherwise

---

## Vault Folder Structure

```
Options-Curriculum/                   ← Obsidian vault root
├── 00-Index/
│   ├── Home.md
│   ├── MOC-Finding-Opportunities.md
│   ├── MOC-Entry-Exit.md
│   ├── MOC-Strategies.md
│   ├── MOC-Risk-Management.md
│   ├── MOC-Advanced.md
│   └── Glossary.md
├── 01-Foundations/
│   ├── Options-Basics.md
│   ├── Greeks-Overview.md
│   ├── Delta.md
│   ├── Gamma.md
│   ├── Theta-Decay.md
│   ├── Vega.md
│   ├── IV-vs-HV.md
│   ├── IV-Rank.md
│   └── IV-Percentile.md
├── 02-Finding-Opportunities/
│   ├── Ticker-Selection-System.md
│   ├── Ticker-Criteria-Technical.md
│   ├── Ticker-Criteria-Fundamental.md
│   ├── Earnings-Calendar-System.md
│   ├── Screener-Setup.md
│   ├── High-Probability-Setup-Checklist.md
│   └── Setup-Recognition-Patterns.md
├── 03-Entry-Exit/
│   ├── Best-Days-of-Week.md
│   ├── Intraday-Timing-Open.md
│   ├── Intraday-Timing-Midday.md
│   ├── Intraday-Timing-Power-Hour.md
│   ├── Entry-Confirmation-Signals.md
│   ├── When-Not-To-Trade.md
│   └── Building-Discipline.md
├── 04-Strategies/
│   ├── Set-and-Forget/
│   │   ├── CSP-Cash-Secured-Put.md
│   │   ├── Covered-Call.md
│   │   ├── Wheel-Strategy.md
│   │   ├── LEAPS.md
│   │   └── PMCC.md
│   ├── Income/
│   │   ├── Bull-Put-Spread.md
│   │   ├── Bear-Call-Spread.md
│   │   ├── Iron-Condor.md
│   │   ├── Iron-Fly.md
│   │   ├── Butterfly.md
│   │   ├── Diagonal-Spread.md
│   │   └── Calendar-Spread.md
│   ├── Long-Term/
│   │   ├── LEAPS-Investing.md
│   │   ├── PMCC-Income.md
│   │   ├── Zero-Risk-Collar.md
│   │   ├── Advanced-Collar.md
│   │   └── Portfolio-Margin.md
│   └── 0DTE/
│       ├── 0DTE-Overview.md
│       ├── SPX-vs-QQQ-0DTE.md
│       ├── 0DTE-Entry-Timing.md
│       ├── 0DTE-Credit-Spread.md
│       ├── 0DTE-Iron-Condor.md
│       ├── 0DTE-Butterfly.md
│       └── Superfly.md
├── 05-Market-Conditions/
│   ├── Market-Condition-Classification.md
│   ├── High-IV-Playbook.md
│   ├── Low-IV-Playbook.md
│   ├── Trending-Market-Strategies.md
│   └── Range-Bound-Strategies.md
├── 06-Risk-Management/
│   ├── Position-Sizing.md
│   ├── Portfolio-Allocation.md
│   ├── Max-Risk-Per-Trade.md
│   ├── Stop-Loss-Strategies.md
│   ├── Drawdown-Management.md
│   └── Portfolio-Performance-Metrics.md
├── 07-Profit-Taking/
│   ├── 50pct-vs-Expiry.md
│   └── Scaling-Out-of-Winners.md
├── 08-Adjustments/
│   ├── Adjust-vs-Close.md
│   ├── Rolling-Basics.md
│   ├── Rolling-Credit-Spreads.md
│   ├── Rolling-Iron-Condors.md
│   ├── PMCC-Adjustments.md
│   ├── 0DTE-Adjustments.md
│   └── Losing-Trade-Mindset.md
├── 09-Earnings/
│   ├── Earnings-Overview.md
│   ├── Earnings-Ticker-Selection.md
│   ├── IV-Crush-Mechanics.md
│   ├── Earnings-IC-Playbook.md
│   ├── Earnings-Straddle-Strangle.md
│   ├── Earnings-Strategy-Matching.md
│   ├── Earnings-Tools.md
│   └── Earnings-Execution-Playbook.md
├── Charts/
│   ├── README.md
│   ├── pnl_diagrams.py
│   ├── iv_charts.py
│   ├── timing_charts.py
│   ├── risk_charts.py
│   ├── earnings_charts.py
│   └── outputs/
└── Templates/
    ├── Strategy-Note-Template.md
    ├── Concept-Note-Template.md
    └── Playbook-Note-Template.md
```

---

## Task Registry

### INFRASTRUCTURE

---

#### TASK-001 · Vault Templates
**Complexity:** 1 — Haiku | **Output:** `Templates/Strategy-Note-Template.md`, `Templates/Concept-Note-Template.md`, `Templates/Playbook-Note-Template.md`

**Prompt:**
> Create three Obsidian note templates for an options trading curriculum vault.
> **Template 1 — Strategy Note** (`Strategy-Note-Template.md`): frontmatter fields: title, tags, aliases, status, strategy-type (income/set-and-forget/0DTE/long-term), legs, max-profit, max-loss, breakeven, ideal-IV-rank, ideal-DTE, related. Body sections: Structure, Entry Conditions, Management Rules, Exit Rules, Risk Profile, Adjustments, Chart, Links.
> **Template 2 — Concept Note** (`Concept-Note-Template.md`): frontmatter: title, tags, aliases, status, related. Body sections: Definition, Why It Matters, How to Apply, Example, Links.
> **Template 3 — Playbook Note** (`Playbook-Note-Template.md`): frontmatter: title, tags, aliases, status, related. Body sections: When to Use This Playbook, Step-by-Step, Entry Criteria Table, Management Rules, What Can Go Wrong, Links.
> Use `{{placeholders}}` for fillable fields. Include a `> [!warning]` callout placeholder in each.

---

#### TASK-002 · Home MOC
**Complexity:** 1 — Haiku | **Output:** `00-Index/Home.md`

**Prompt:**
> Write the Home Map of Content (MOC) note for an Obsidian options trading curriculum vault titled "Everything You Need to Become a Successful Options Trader".
> Link to all six module MOCs: [[MOC-Finding-Opportunities]], [[MOC-Entry-Exit]], [[MOC-Strategies]], [[MOC-Risk-Management]], [[MOC-Advanced]], and [[Glossary]].
> Include a one-paragraph mission statement about learning options trading with practical, tested strategies. Add a "Start Here" section that recommends the reading order for beginners. Keep it under 300 words — this is a navigation hub, not content.

---

#### TASK-003 · Module MOCs (6 notes)
**Complexity:** 1 — Haiku | **Output:** `00-Index/MOC-*.md` (6 files)

**Prompt:**
> Write six Map of Content notes for an options trading Obsidian vault. Each MOC links to all notes within its module. Modules:
> 1. **MOC-Finding-Opportunities** — links to all notes in `02-Finding-Opportunities/`
> 2. **MOC-Entry-Exit** — links to all notes in `03-Entry-Exit/`
> 3. **MOC-Strategies** — links to all notes in `04-Strategies/` (organized by sub-type: Set & Forget, Income, Long-Term, 0DTE)
> 4. **MOC-Risk-Management** — links to notes in `06-Risk-Management/` and `07-Profit-Taking/` and `08-Adjustments/`
> 5. **MOC-Advanced** — links to `09-Earnings/` and advanced Long-Term notes
> 6. **Glossary** — an alphabetical list of key options terms, each a short definition (2 sentences max) with [[links]] to detailed notes where they exist
> Each MOC has a 2-sentence description of the module's purpose.

---

#### TASK-004 · Charts README and Setup
**Complexity:** 2 — Sonnet | **Output:** `Charts/README.md`

**Prompt:**
> Write a README for the `Charts/` folder of an options trading curriculum. This folder contains Python scripts that generate charts embedded in Obsidian notes.
> Include: (1) prerequisites (`pip install plotly matplotlib numpy pandas`), (2) how to run each script and where output goes (`outputs/` folder), (3) naming convention for output files (e.g., `pnl-iron-condor.png`), (4) how charts are embedded in Obsidian notes (`![[filename.png]]`), (5) a table listing each script and what charts it generates.
> Charts use `plotly` for interactive HTML and `matplotlib` for static PNG (Obsidian embeds). Every script saves both formats.

---

#### TASK-005 · Glossary
**Complexity:** 1 — Haiku | **Output:** `00-Index/Glossary.md`

**Prompt:**
> Write a concise options trading glossary as an Obsidian note. Alphabetical. Include 50+ terms: all Greeks (delta, gamma, theta, vega, rho, vanna, charm), strategy names (CSP, CC, IC, fly, condor, PMCC, LEAPS, 0DTE, calendar, diagonal), and key concepts (IV rank, IV percentile, IV crush, expected move, historical volatility, implied volatility, bid-ask spread, open interest, volume, liquidity, assignment, exercise, roll, breakeven, max loss, max profit, credit, debit, net premium, days to expiration DTE, moneyness — ITM/ATM/OTM).
> Each entry: term in bold, 1-2 sentence definition, [[WikiLink]] to full note where one exists. Frontmatter: title, tags: [glossary, reference], status: draft.

---

### MODULE 1: FOUNDATIONS

---

#### TASK-006 · Options Basics
**Complexity:** 1 — Haiku | **Output:** `01-Foundations/Options-Basics.md`

**Prompt:**
> Write a foundational Obsidian note explaining what options are for someone new to options but not new to investing. Cover: calls vs puts, buyer vs seller perspective, intrinsic vs extrinsic value, why sellers have the edge (theta decay, probability), the concept of defined vs undefined risk. Include a table showing the four basic positions (long call, short call, long put, short put) with their max profit, max loss, and when to use them. Link to [[Greeks-Overview]], [[IV-Rank]], [[Theta-Decay]]. Use the Concept Note template structure.

---

#### TASK-007 · Greeks Overview
**Complexity:** 2 — Sonnet | **Output:** `01-Foundations/Greeks-Overview.md`

**Prompt:**
> Write an Obsidian note giving a practical overview of options Greeks for active traders. Not academic — focus on what each Greek means for trade management decisions. Cover delta, gamma, theta, vega; mention rho briefly. For each: one-sentence definition, practical implication (e.g., "If delta is 0.30, option moves $0.30 for every $1 move in the stock"), how it affects entry/exit decisions. Include a table: Greek | What it measures | High = | Low = | Key decision. Link to individual Greek notes: [[Delta]], [[Gamma]], [[Theta-Decay]], [[Vega]]. Add chart reference: `![[chart-greeks-sensitivity.png]]`.

---

#### TASK-008 · Delta Note
**Complexity:** 1 — Haiku | **Output:** `01-Foundations/Delta.md`

**Prompt:**
> Write an atomic Obsidian note on delta for options traders. Cover: definition (rate of change of option price vs underlying), delta as probability proxy (30-delta ≈ 30% chance of expiring ITM), directional exposure (long call = positive delta, long put = negative delta), delta neutral strategies. Include practical rules: preferred delta ranges for CSP (0.20–0.30), credit spreads (short leg 0.25–0.35), 0DTE trades (0.10–0.20). Link to [[Greeks-Overview]], [[CSP-Cash-Secured-Put]], [[Bull-Put-Spread]].

---

#### TASK-009 · Theta Decay Note
**Complexity:** 2 — Sonnet | **Output:** `01-Foundations/Theta-Decay.md`

**Prompt:**
> Write an Obsidian note on theta decay for options sellers. Explain: definition, the theta acceleration curve (non-linear — accelerates in the last 21–30 DTE), why sellers benefit from theta, the "sweet spot" DTE range (21–45 DTE for most income strategies), theta vs vega tradeoff (further OTM = less theta but also less vega risk). Include practical rules: when to close (50% profit = captures most theta without holding through gamma risk). Add chart reference: `![[chart-theta-decay-curve.png]]`. Link to [[Greeks-Overview]], [[50pct-vs-Expiry]], [[IV-Rank]].

---

#### TASK-010 · Vega Note
**Complexity:** 1 — Haiku | **Output:** `01-Foundations/Vega.md`

**Prompt:**
> Write an atomic Obsidian note on vega for options traders. Cover: definition (sensitivity to IV changes), long vega (long options benefit from IV expansion), short vega (short options hurt by IV expansion), how IV rank determines whether selling or buying options has edge. Practical rules: only sell premium when IV rank > 30–40%; buy premium (long vega) when IV rank < 20%. Link to [[IV-Rank]], [[IV-vs-HV]], [[High-IV-Playbook]], [[Low-IV-Playbook]].

---

#### TASK-011 · Gamma Note
**Complexity:** 2 — Sonnet | **Output:** `01-Foundations/Gamma.md`

**Prompt:**
> Write an Obsidian note on gamma for options traders focused on risk management. Cover: definition (rate of change of delta), why gamma is the primary risk for short options sellers (especially near expiration), gamma explosion near expiration (0DTE risk), gamma risk vs theta reward tradeoff, how to manage gamma by closing positions early. Include a `> [!warning]` callout: "Gamma risk is highest for 0DTE and same-week trades — positions can move against you faster than you can react." Add chart reference: `![[chart-gamma-vs-dte.png]]`. Link to [[Greeks-Overview]], [[0DTE-Overview]], [[50pct-vs-Expiry]].

---

#### TASK-012 · IV vs HV
**Complexity:** 2 — Sonnet | **Output:** `01-Foundations/IV-vs-HV.md`

**Prompt:**
> Write an Obsidian note contrasting implied volatility (IV) and historical volatility (HV) for options traders. Cover: IV definition (market's forecast of future volatility embedded in option price), HV definition (realized volatility over past N days), why IV typically exceeds HV (volatility risk premium — the fundamental edge of options sellers), how to use the IV-HV spread to confirm edge (sell when IV >> HV), limitations (IV can spike and HV can catch up). Include a practical rule: "IV should be at least 5–10 vol points above 20-day HV before selling premium." Link to [[IV-Rank]], [[IV-Percentile]], [[Vega]], [[High-IV-Playbook]].

---

#### TASK-013 · IV Rank
**Complexity:** 2 — Sonnet | **Output:** `01-Foundations/IV-Rank.md`

**Prompt:**
> Write an Obsidian note on IV Rank (IVR) for options traders. Cover: formula (IVR = (current IV - 52w low) / (52w high - 52w low) × 100), interpretation (0–100 scale), practical thresholds (IVR > 50 = elevated, sell premium; IVR < 30 = depressed, avoid selling or buy premium), difference from IV percentile, how to find IVR (thinkorswim, Barchart, Market Chameleon, tastytrade). Include a table: IVR Range | Market Condition | Preferred Strategy Type. Add chart reference: `![[chart-ivr-distribution.png]]`. Link to [[IV-Percentile]], [[IV-vs-HV]], [[Screener-Setup]], [[High-IV-Playbook]].

---

#### TASK-014 · IV Percentile
**Complexity:** 1 — Haiku | **Output:** `01-Foundations/IV-Percentile.md`

**Prompt:**
> Write an atomic Obsidian note on IV Percentile (IVP) for options traders. Cover: formula (% of days in past year where IV was lower than current IV), difference from IV Rank (IVP is less distorted by outlier IV spikes), which metric to prefer (IVP more reliable for stocks that had single large spikes like post-earnings), practical thresholds (IVP > 50 = good for selling, IVP < 30 = avoid selling). Link to [[IV-Rank]], [[IV-vs-HV]].

---

### MODULE 2: FINDING PROFITABLE OPPORTUNITIES

---

#### TASK-015 · Ticker Selection System
**Complexity:** 2 — Sonnet | **Output:** `02-Finding-Opportunities/Ticker-Selection-System.md`

**Prompt:**
> Write an Obsidian note describing a complete system for selecting tickers for options trading in under 10 minutes. This is an overview note linking to the detailed criteria notes. Cover: the two-filter funnel (technical criteria first, fundamental/liquidity second), how to use screeners to generate candidates, how to apply the checklist to narrow to 2–5 high-probability setups per week. Include a flowchart-style decision tree in text: "Does the ticker meet liquidity criteria? → No: eliminate. Yes → Does IV rank qualify? → No: watch list. Yes → Technical setup confirmed? → Trade." Link to [[Ticker-Criteria-Technical]], [[Ticker-Criteria-Fundamental]], [[Screener-Setup]], [[High-Probability-Setup-Checklist]], [[IV-Rank]].

---

#### TASK-016 · Ticker Criteria — Technical
**Complexity:** 2 — Sonnet | **Output:** `02-Finding-Opportunities/Ticker-Criteria-Technical.md`

**Prompt:**
> Write an Obsidian playbook note on technical criteria for selecting options trading tickers. Cover: (1) Trend: stock must be in a clear trend or defined range — avoid choppy stocks, (2) Support/Resistance: identify key levels where you'd sell puts (support) or calls (resistance), (3) Moving averages as dynamic support (20/50/200 SMA), (4) Volume: minimum 1M average daily share volume, (5) Price range: $20–$500 for most retail traders (avoid penny stocks and very high-priced stocks), (6) Avoid: earnings within 14 days (unless specifically doing an earnings trade), recent gap-up/gap-down stocks. Use a checklist format. Include specific examples: AAPL, NVDA, SPY, GLD as model tickers meeting criteria. Link to [[Ticker-Criteria-Fundamental]], [[Ticker-Selection-System]], [[Entry-Confirmation-Signals]].

---

#### TASK-017 · Ticker Criteria — Fundamental/Liquidity
**Complexity:** 1 — Haiku | **Output:** `02-Finding-Opportunities/Ticker-Criteria-Fundamental.md`

**Prompt:**
> Write an Obsidian note on fundamental and liquidity criteria for selecting options trading tickers. Cover: (1) Options liquidity — minimum open interest: 500+ contracts on target strike, bid-ask spread < $0.10 for options under $1, < 1% of mid-price for larger options; (2) underlying liquidity — minimum 500K average daily volume, market cap > $1B; (3) avoid binary events (FDA, court rulings, M&A) unless specifically trading them; (4) prefer ETFs for defined-risk strategies (SPY, QQQ, GLD, TLT, IWM). Include a pass/fail table for quick reference. Link to [[Ticker-Selection-System]], [[Screener-Setup]].

---

#### TASK-018 · Screener Setup Guide
**Complexity:** 2 — Sonnet | **Output:** `02-Finding-Opportunities/Screener-Setup.md`

**Prompt:**
> Write an Obsidian playbook note on setting up options screeners to find trade opportunities in minutes. Cover three platforms: (1) **Barchart Options Screener** — filters: IV rank > 50, volume > 500K, OI > 500 at target strikes; (2) **Market Chameleon** — IV rank screener, earnings calendar with expected move data, term structure; (3) **thinkorswim (ToS)** — Stock Hacker with IV Rank scan (scan filter: ImpVolatility_Hist_Pct > 50). For each: step-by-step setup instructions, what to look for in results, how to export to watchlist. Add a "Weekly Workflow" section: Monday — run screeners, build watchlist; Tuesday–Thursday — monitor setups and enter; Friday — manage existing positions only. Link to [[Ticker-Selection-System]], [[IV-Rank]], [[High-Probability-Setup-Checklist]].

---

#### TASK-019 · High-Probability Setup Checklist
**Complexity:** 2 — Sonnet | **Output:** `02-Finding-Opportunities/High-Probability-Setup-Checklist.md`

**Prompt:**
> Write an Obsidian note containing the definitive checklist for confirming a high-probability options setup before entering a trade. Format as a markdown checklist (- [ ] items). Categories: **Volatility** (IV rank > 40 for selling, < 25 for buying; IVP confirms), **Liquidity** (OI > 500 at target strike, spread < 10% of mid), **Technical** (not in earnings window, trend confirmed, key level identified), **Strategy fit** (strategy matches market condition, DTE in optimal range), **Risk check** (position size within allocation limit, max loss acceptable). Include a scoring system: 12/12 = trade; 10–11 = trade with reduced size; < 10 = pass. Add a `> [!tip]` callout: "When in doubt, pass. There will always be another setup." Link to [[Ticker-Selection-System]], [[Position-Sizing]], [[Market-Condition-Classification]].

---

#### TASK-020 · Setup Recognition Patterns
**Complexity:** 3 — Opus | **Output:** `02-Finding-Opportunities/Setup-Recognition-Patterns.md`

**Prompt:**
> Write an advanced Obsidian note on recognizing high-probability options setups before they develop. Cover five specific pattern types with entry logic: (1) **IV compression coil** — IV rank drops below 20 then starts expanding; signals volatility expansion trade (buy straddle or debit spread); (2) **Mean-reversion after spike** — stock > 2 ATR move on high IV, IV rank > 70; sell premium into the spike; (3) **Support/Resistance hold** — stock tests key level 3+ times without breaking; sell puts at support or calls at resistance; (4) **Pre-earnings IV accumulation** — IV rank rising 2–3 weeks before earnings; enter IC or IC spread 7–10 DTE before earnings announcement; (5) **Post-earnings IV crush recovery** — IV drops 40–60% post-earnings; sell premium on residual elevated IV. For each pattern: entry trigger, strategy to deploy, typical outcome. Include `> [!warning]` for pattern failure conditions. Add chart reference: `![[chart-iv-compression-coil.png]]`. Link to [[IV-Rank]], [[Earnings-Overview]], [[Market-Condition-Classification]].

---

### MODULE 3: ENTRY & EXIT

---

#### TASK-021 · Best Days of the Week
**Complexity:** 2 — Sonnet | **Output:** `03-Entry-Exit/Best-Days-of-Week.md`

**Prompt:**
> Write an Obsidian note on the best days of the week for different options strategies, based on market microstructure patterns. Cover: **Monday** — avoid new entries (weekend gap risk still settling, low commitment); **Tuesday** — best day to enter weekly credit spreads and IC (3–4 days of theta decay ahead, vol usually normalizes); **Wednesday** — enter 0DTE trades on SPX (Wed/Fri expiry); **Thursday** — last day to enter weekly trades, roll or adjust positions expiring Friday; **Friday** — manage and close only, do not open new weekly positions, 0DTE is available but highest gamma risk. Include a table: Day | Open New Positions? | Strategy Types | Notes. Add specific rule: "Enter 21–45 DTE income trades on Tuesday–Wednesday for best theta capture." Link to [[Intraday-Timing-Open]], [[0DTE-Overview]], [[Building-Discipline]].

---

#### TASK-022 · Intraday Timing — Open
**Complexity:** 2 — Sonnet | **Output:** `03-Entry-Exit/Intraday-Timing-Open.md`

**Prompt:**
> Write an Obsidian note on market open dynamics for options traders (9:30–10:30 AM ET). Cover: why the first 15–30 minutes are dangerous (wide spreads, low liquidity, price discovery, algorithmic activity), when to start watching (10:00–10:30 AM for most strategies), exceptions where open matters (earnings gap plays, 0DTE SPX where entry at open can be appropriate if gap is large), how to use the VIX open to calibrate — if VIX opens > 5% above prior close, reduce position size or avoid selling. Include a `> [!warning]`: "Never chase a gap at open with naked premium selling — wait for price stabilization." Practical rule: "For non-0DTE trades, place orders between 10:00–10:30 AM. For 0DTE, evaluate at 9:45 and again at 10:15." Link to [[Intraday-Timing-Power-Hour]], [[0DTE-Entry-Timing]], [[When-Not-To-Trade]].

---

#### TASK-023 · Intraday Timing — Power Hour
**Complexity:** 1 — Haiku | **Output:** `03-Entry-Exit/Intraday-Timing-Power-Hour.md`

**Prompt:**
> Write an Obsidian note on power hour (3:00–4:00 PM ET) for options traders. Cover: why volume and volatility spike (institutional rebalancing, ETF flows, 0DTE gamma effects), opportunities (closing profitable 0DTE positions before pin risk, entering next-day positions at elevated IV), risks (rapid moves, wide spreads late in session), specific rule for 0DTE: close all 0DTE positions by 3:45 PM to avoid overnight or expiration-hour risk. Add `> [!tip]`: "Power hour can refill IC premium on 0DTE — but only if you're delta neutral and the move is contained." Link to [[0DTE-Entry-Timing]], [[Intraday-Timing-Open]], [[0DTE-Credit-Spread]].

---

#### TASK-024 · Intraday Timing — Midday
**Complexity:** 1 — Haiku | **Output:** `03-Entry-Exit/Intraday-Timing-Midday.md`

**Prompt:**
> Write an atomic Obsidian note on midday trading (11:00 AM–2:00 PM ET) for options. Cover: why midday is typically the lowest volatility and lowest volume period, advantages for limit orders (tighter spreads, more price stability), best use — entering 21–45 DTE income trades (IC, credit spreads, CSP), avoiding 0DTE entries during midday (low movement means theta is working but so is boredom-driven risk), the concept of "midday drift" — stocks tend to continue their morning trend or revert. Practical rule: "If a morning trend is clear by 11:00 AM, midday is the ideal time to enter a directional credit spread with the trend." Link to [[Intraday-Timing-Open]], [[Best-Days-of-Week]].

---

#### TASK-025 · Entry Confirmation Signals
**Complexity:** 2 — Sonnet | **Output:** `03-Entry-Exit/Entry-Confirmation-Signals.md`

**Prompt:**
> Write an Obsidian playbook note on entry confirmation signals for options trades. Cover five confirmation signals before pressing the button: (1) **IV rank confirmed** — screener check, current vs yesterday; (2) **Price at or near a key technical level** — don't sell puts in the middle of a range, wait for price to come to support; (3) **No catalysts within 14 days** — check earnings calendar (Earnings Whispers, Market Chameleon), FDA dates, Fed meetings; (4) **VIX context** — if VIX > 30, use defined-risk only (no CSP on individual stocks); (5) **Spread confirmed** — actually check the bid-ask spread at your target strike right now, not yesterday's data. Format: checklist with specific numbers. Add a section "What to do if you're not sure" — the answer is always to paper trade or reduce size to 25% until confidence builds. Link to [[High-Probability-Setup-Checklist]], [[When-Not-To-Trade]], [[IV-Rank]].

---

#### TASK-026 · When NOT to Trade
**Complexity:** 2 — Sonnet | **Output:** `03-Entry-Exit/When-Not-To-Trade.md`

**Prompt:**
> Write an Obsidian note — arguably the most important note in the vault — on when NOT to trade options. This note should have more weight than any entry signal. Cover: (1) **FOMC meetings and Fed decision days** — avoid entering new positions on decision day, close short-gamma positions morning of; (2) **CPI/Jobs report days** — same rule, vol spikes unpredictably; (3) **Earnings within 14 days** — never sell naked premium within 14 days of earnings unless it IS an earnings trade with defined risk; (4) **VIX > 35** — undefined risk strategies off the table entirely; (5) **Your own emotional state** — fear, greed, revenge trading after a loss; (6) **Illiquid markets** — holidays, low volume days. Format as a numbered list with `> [!warning]` callouts for the highest-stakes items. Quote tastyworks research: "The biggest gains come from staying out of bad trades, not finding more trades." Link to [[Building-Discipline]], [[Entry-Confirmation-Signals]], [[Drawdown-Management]].

---

#### TASK-027 · Building Discipline
**Complexity:** 2 — Sonnet | **Output:** `03-Entry-Exit/Building-Discipline.md`

**Prompt:**
> Write an Obsidian note on building the discipline to wait for your setup and manage emotions in options trading. Cover: (1) The pre-trade ritual — run checklist [[High-Probability-Setup-Checklist]] before every trade, no exceptions; (2) The trading journal — what to log (entry reason, exit reason, outcome, what you learned), weekly review process; (3) FOMO management — "The position I didn't take can't hurt me"; (4) After-loss protocol — close the platform, wait 24 hours before entering a new position after a max-loss event; (5) Position sizing as discipline tool — if you're risking the right amount, losses don't feel catastrophic. Add a `> [!tip]` callout: "Your edge is not just the strategy — it's your ability to execute it consistently over 100+ trades." Link to [[When-Not-To-Trade]], [[Max-Risk-Per-Trade]], [[Losing-Trade-Mindset]].

---

### MODULE 4: CORE STRATEGIES

---

#### TASK-028 · Cash Secured Put (CSP)
**Complexity:** 2 — Sonnet | **Output:** `04-Strategies/Set-and-Forget/CSP-Cash-Secured-Put.md`

**Prompt:**
> Write an Obsidian strategy note for the Cash Secured Put (CSP) using the Strategy Note template. Cover: **Structure** — sell one put, hold cash collateral equal to strike × 100; **Best conditions** — bullish to neutral outlook, IV rank > 40, stock you'd be happy to own; **Entry rules** — sell 0.20–0.30 delta put, 21–45 DTE, on a stock at or near support; **Max profit** — premium received; **Max loss** — strike price minus premium (stock goes to zero); **Breakeven** — strike minus premium; **Management** — close at 50% profit, roll down and out if tested with ≥21 DTE remaining; **Exit** — 50% profit or 21 DTE, whichever comes first; **Ideal tickers** — high-quality stocks or ETFs you want to own (AAPL, MSFT, SPY, GLD). Add `> [!warning]`: "CSP carries full downside of stock ownership below the strike. Size accordingly — never use more than 5% of portfolio on one CSP." Add chart reference: `![[pnl-csp.png]]`. Link to [[Covered-Call]], [[Wheel-Strategy]], [[Delta]], [[IV-Rank]], [[Rolling-Credit-Spreads]].

---

#### TASK-029 · Covered Call (CC)
**Complexity:** 2 — Sonnet | **Output:** `04-Strategies/Set-and-Forget/Covered-Call.md`

**Prompt:**
> Write an Obsidian strategy note for the Covered Call (CC). Structure: own 100 shares, sell 1 OTM call. Best conditions: neutral to mildly bullish, IV rank > 30, stock held long-term (not trying to sell it). Entry: sell 0.25–0.35 delta call, 21–45 DTE, at resistance. Max profit: premium + (strike - purchase price) if assigned. Max loss: stock drops to zero minus premium received. Management: close at 50% profit; if stock rallies through strike, decide: roll up and out for credit, or let it get called away (acceptable). Tax consideration callout: "Covered calls on long-term holdings can convert long-term gains to short-term — consult your tax advisor." Add chart: `![[pnl-covered-call.png]]`. Link to [[CSP-Cash-Secured-Put]], [[Wheel-Strategy]], [[PMCC]].

---

#### TASK-030 · Wheel Strategy
**Complexity:** 3 — Opus | **Output:** `04-Strategies/Set-and-Forget/Wheel-Strategy.md`

**Prompt:**
> Write a comprehensive Obsidian strategy note on the Wheel Strategy. The Wheel is a three-phase cycle: Phase 1 (Sell CSP) → Phase 2 (Assigned, own stock) → Phase 3 (Sell CC against stock). Cover each phase with precise rules: **Phase 1 CSP**: sell 0.20–0.30 delta put, 21–45 DTE, on stock you'd own long-term; close at 50% profit; if assigned, move to Phase 2. **Phase 2 Stock Ownership**: immediately sell CC at or above your cost basis for the strike, 21–45 DTE, 0.25–0.35 delta. **Phase 3 CC**: close CC at 50% profit; if assigned (stock called away), return to Phase 1. **Ticker selection**: the most critical part — only wheel high-quality tickers (AAPL, MSFT, SPY, GLD, AMZN). Never wheel meme stocks or biotech. **When the wheel breaks**: stock drops 20%+ below put strike — do not keep selling calls below your cost basis hoping for recovery; may need to sell the stock and accept loss. Add `> [!warning]` about capital requirements and true max loss. Add chart: `![[pnl-wheel-cycle.png]]`. Link to [[CSP-Cash-Secured-Put]], [[Covered-Call]], [[Ticker-Criteria-Technical]], [[Rolling-Credit-Spreads]].

---

#### TASK-031 · Bull Put Spread
**Complexity:** 2 — Sonnet | **Output:** `04-Strategies/Income/Bull-Put-Spread.md`

**Prompt:**
> Write an Obsidian strategy note on the Bull Put Credit Spread. Structure: sell OTM put, buy further OTM put (same expiry). This is a defined-risk, bullish-to-neutral income trade. Entry: sell 0.25–0.35 delta put, buy 5–10 points lower (for SPX) or appropriate width for the underlying, 21–45 DTE, IV rank > 40. Credit received: typical target 25–33% of spread width. Max profit: net credit. Max loss: spread width minus credit. Breakeven: short strike minus net credit. Management: close at 50% profit; close at 200% loss (2x credit received). Strike selection: sell at a technical support level. Include a specific example: SPX at 5000, sell 4850 put / buy 4800 put for $15 credit on a $50-wide spread. Add chart: `![[pnl-bull-put-spread.png]]`. Link to [[Bear-Call-Spread]], [[Iron-Condor]], [[Rolling-Credit-Spreads]], [[IV-Rank]].

---

#### TASK-032 · Bear Call Spread
**Complexity:** 2 — Sonnet | **Output:** `04-Strategies/Income/Bear-Call-Spread.md`

**Prompt:**
> Write an Obsidian strategy note on the Bear Call Credit Spread. Mirror of [[Bull-Put-Spread]] but for bearish-to-neutral outlook. Structure: sell OTM call, buy further OTM call (same expiry). Entry: sell 0.25–0.35 delta call, buy 5–10 points above (for SPX), 21–45 DTE, IV rank > 40, at resistance. Credit: target 25–33% of spread width. Max profit: credit. Max loss: spread width minus credit. Management: same as bull put — close at 50% profit, close at 200% loss. Specific example: SPX at 5000, sell 5150 call / buy 5200 call for $15 credit. Note: combining a bull put and bear call on the same underlying and expiry creates an [[Iron-Condor]]. Add chart: `![[pnl-bear-call-spread.png]]`. Link to [[Bull-Put-Spread]], [[Iron-Condor]], [[Rolling-Credit-Spreads]].

---

#### TASK-033 · Iron Condor
**Complexity:** 3 — Opus | **Output:** `04-Strategies/Income/Iron-Condor.md`

**Prompt:**
> Write a comprehensive Obsidian strategy note on the Iron Condor (IC). Structure: simultaneously sell an OTM put spread and an OTM call spread on the same underlying and expiry. **Ideal conditions**: IV rank > 50, range-bound market, no catalysts within the trade window. **Entry rules**: Short strikes at 0.16–0.25 delta (1-SD to 1.3-SD); wing width: 50 points for SPX, 5–10% of stock price for equities; DTE: 21–45 days; collect at least 25–33% of the spread width as credit. **Expected move**: use the EM to size the condor — short strikes should be outside 1 expected move. **Management**: (1) close entire IC at 50% profit; (2) roll untested side in if IV drops (take in more credit); (3) if one side is tested, evaluate adjustment — don't just watch it become a loser. **Adjustment triggers**: delta of short strike reaches 0.30+, or unrealized loss > 1× credit received. Include specific SPX example with real numbers. Add `> [!warning]`: "An IC profits in ~68% of cases mathematically, but a single black swan can wipe multiple wins. Always use defined risk." Add chart: `![[pnl-iron-condor.png]]`. Link to [[Bull-Put-Spread]], [[Bear-Call-Spread]], [[Rolling-Iron-Condors]], [[Market-Condition-Classification]], [[Adjust-vs-Close]].

---

#### TASK-034 · Iron Fly
**Complexity:** 2 — Sonnet | **Output:** `04-Strategies/Income/Iron-Fly.md`

**Prompt:**
> Write an Obsidian strategy note on the Iron Fly (Iron Butterfly). Structure: sell ATM straddle (ATM call + ATM put), buy OTM call and OTM put as wings. Compared to IC: higher credit, narrower profit zone, profits when stock pins near current price. Entry: ATM short strikes, wings 1–2 standard deviations away, 21–30 DTE, IV rank > 50. Credit: typically 40–50% of wing width. Max profit: full credit (stock pins at strike). Max loss: wing width minus credit. Management: close at 25–50% profit (profit zone is narrow, don't be greedy); defend at 25% of credit remaining. When to prefer over IC: when you want higher credit and can tolerate narrower profit zone; when IV is very elevated and you expect a pin near current price. Add chart: `![[pnl-iron-fly.png]]`. Link to [[Iron-Condor]], [[Butterfly]], [[Fly-vs-IC]].

---

#### TASK-035 · Butterfly
**Complexity:** 2 — Sonnet | **Output:** `04-Strategies/Income/Butterfly.md`

**Prompt:**
> Write an Obsidian strategy note on the Butterfly spread (call and put versions). Structure: buy 1 lower strike, sell 2 middle strikes, buy 1 higher strike (all same expiry). This is a debit trade that profits when stock pins at the middle strike. Variations: (1) Long call butterfly — bullish target; (2) Long put butterfly — bearish target; (3) Broken-wing butterfly — bias to one side by making wings asymmetric. Entry for income: 21–35 DTE, place middle strike at expected pin (resistance for bearish fly, support for bullish fly), cost typically 20–30% of wing width. Max profit: wing width minus debit. Max loss: debit paid. Management: close at 100% return on debit (2× debit), or close with 7 DTE to avoid pin risk. Advantage over IC: defined debit risk, works better in low-IV environments. Add chart: `![[pnl-butterfly.png]]`. Link to [[Iron-Fly]], [[Iron-Condor]], [[Fly-vs-IC]].

---

#### TASK-036 · Fly vs IC — When to Use Each
**Complexity:** 3 — Opus | **Output:** `04-Strategies/Income/Fly-vs-IC.md`

**Prompt:**
> Write an Obsidian decision note comparing Iron Condor vs Iron Fly vs Butterfly — when to use each. Use a structured comparison. Cover: (1) P&L structure differences (IC has wider profit zone but less credit; fly/iron fly have higher credit but narrower zone); (2) IV environment (high IV > 50 favors Iron Fly for maximum premium; IC is better for moderate IV 35–60 with a defined range); (3) Directional bias (use call or put butterfly for directional targets; IC is neutral); (4) Management complexity (IC easier to adjust one-sided; fly harder to defend); (5) Capital efficiency (flies often higher ROC). Include a decision matrix: conditions × best strategy. Add chart: `![[pnl-fly-vs-ic-comparison.png]]`. Link to [[Iron-Condor]], [[Iron-Fly]], [[Butterfly]], [[Market-Condition-Classification]].

---

#### TASK-037 · Calendar Spread
**Complexity:** 2 — Sonnet | **Output:** `04-Strategies/Income/Calendar-Spread.md`

**Prompt:**
> Write an Obsidian strategy note on the Calendar Spread (also called time spread or horizontal spread). Structure: sell near-term option (shorter DTE), buy same-strike further-term option (longer DTE), both same type (call or call, put or put). This is a vega-positive, theta-positive trade — profits from IV expansion and time decay differential. Entry: place near-term sale at ATM or near ATM, DTE of short leg: 21–30 days, DTE of long leg: 45–60 days. IV requirements: works best when near-term IV > long-term IV (inverted term structure) OR when IV is low overall (buying cheap long-term optionality). Profit zone: stock stays near the strike. Management: close when near-term option expires or at 50–75% profit. Risk: if stock makes a large move, loses on both legs. Add chart: `![[pnl-calendar-spread.png]]`. Add `> [!warning]`: "Calendars have non-trivial vega risk — a drop in IV hurts the position even if the stock doesn't move." Link to [[Diagonal-Spread]], [[IV-vs-HV]], [[Theta-Decay]].

---

#### TASK-038 · Diagonal Spread
**Complexity:** 2 — Sonnet | **Output:** `04-Strategies/Income/Diagonal-Spread.md`

**Prompt:**
> Write an Obsidian strategy note on the Diagonal Spread. Structure: like a calendar but with different strikes — sell near-term OTM option, buy further-term option at a different (typically deeper ITM) strike. The Poor Man's Covered Call (PMCC) is a call diagonal. Compared to calendar: diagonal has directional bias (the different strikes add delta exposure); can be structured to collect a net credit if the near-term option is priced high enough. Entry for income: buy 70–80 delta LEAPS call (long leg), sell 0.30 delta short-term call (short leg). Roll the short call monthly. Management: close entire position if delta of long leg drops below 60, or roll the long leg out when it has less than 90 DTE remaining. Add chart: `![[pnl-diagonal-spread.png]]`. Link to [[Calendar-Spread]], [[PMCC]], [[LEAPS]].

---

#### TASK-039 · LEAPS Overview
**Complexity:** 2 — Sonnet | **Output:** `04-Strategies/Set-and-Forget/LEAPS.md`

**Prompt:**
> Write an Obsidian note on LEAPS (Long-term Equity Anticipation Securities) for options traders. Cover: definition (options with >1 year to expiration), why LEAPS are used (stock replacement, long-term bullish exposure with defined risk, PMCC foundation), how LEAPS behave differently from short-term options (lower theta decay rate, high vega sensitivity, less responsive to short-term news). Entry: buy 70–80 delta LEAPS call (or put for bearish) with 1–2 years to expiration, on a stock you're bullish on long-term. Cost basis vs. stock: LEAPS typically cost 20–30% of owning 100 shares. Risk: time value decays even for deep ITM LEAPS if stock stagnates; assignment risk is minimal as a buyer. When to use: replace a long stock position with defined risk; as the foundation for PMCC. Add chart: `![[chart-leaps-vs-stock.png]]`. Link to [[PMCC]], [[Diagonal-Spread]], [[LEAPS-Investing]].

---

#### TASK-040 · PMCC — Poor Man's Covered Call
**Complexity:** 3 — Opus | **Output:** `04-Strategies/Set-and-Forget/PMCC.md`

**Prompt:**
> Write a comprehensive Obsidian strategy note on the Poor Man's Covered Call (PMCC). Structure: buy a deep ITM LEAPS call (70–80 delta, 1–2 years out) as a stock substitute, then sell short-term OTM calls (0.25–0.35 delta, 21–45 DTE) against it. Goal: income from the short calls funds the LEAPS position over time. Entry rules: (1) LEAPS leg: buy 70+ delta call with ≥1 year remaining; extrinsic value should be reasonable (< 10% of stock price); (2) Short call: sell at a strike where the credit collected minus debit of LEAPS is positive on an annualized basis; never sell the short call at a strike below your LEAPS strike (this creates a debit spread with capped upside). Management: roll short call every 21–30 DTE; if stock rallies through short call, roll up and out for credit; if stock drops significantly, stop selling short calls and let the LEAPS ride or close. Full position cost vs. stock ownership: PMCC uses ~20–30% of capital of owning 100 shares. Add `> [!warning]`: "If the short call goes deep ITM before you can roll, you may be forced to close the spread at a loss. Monitor delta of short call: when it reaches 0.70+, roll immediately." Add chart: `![[pnl-pmcc.png]]`. Link to [[LEAPS]], [[Diagonal-Spread]], [[Covered-Call]], [[PMCC-Adjustments]], [[PMCC-Income]].

---

### MODULE 5: MARKET CONDITIONS

---

#### TASK-041 · Market Condition Classification
**Complexity:** 2 — Sonnet | **Output:** `05-Market-Conditions/Market-Condition-Classification.md`

**Prompt:**
> Write an Obsidian note describing a practical system for classifying market conditions for options strategy selection. Four conditions: (1) **High IV + Trending** — VIX > 25, SPX making directional moves > 1% daily; (2) **High IV + Range-Bound** — VIX > 25, SPX oscillating within 3–5% range; (3) **Low IV + Trending** — VIX < 15, clear directional trend; (4) **Low IV + Range-Bound** — VIX < 15, SPX moving < 0.5% daily. For each: preferred strategies, strategies to avoid, position size guidance. Include a 2×2 matrix: rows = IV level (High/Low), columns = trend (Trending/Range-bound), cells = best strategies. Link to [[High-IV-Playbook]], [[Low-IV-Playbook]], [[Trending-Market-Strategies]], [[Range-Bound-Strategies]], [[Iron-Condor]], [[Bull-Put-Spread]].

---

#### TASK-042 · High IV Playbook
**Complexity:** 2 — Sonnet | **Output:** `05-Market-Conditions/High-IV-Playbook.md`

**Prompt:**
> Write an Obsidian playbook note for trading in high IV environments (IV rank > 50, VIX > 20). Cover: (1) Why high IV is good for sellers (elevated premium, mean reversion tendency); (2) Strategies to deploy: IC on indices (SPY, QQQ), CSP on quality stocks you want to own, bull put spreads; (3) Strike selection in high IV: widen your condor wings, go further OTM (market can move further); (4) Size down: high IV means the market is pricing in big moves — reduce position size 25–50% vs normal; (5) Avoid: undefined risk, calendars (vega hurt if IV drops suddenly), new LEAPS purchases (expensive). Include timing: enter when IV rank is elevated but has started to plateau or pull back. Add `> [!warning]`: "High IV environments correlate with volatile markets — your IC can still lose even at wide strikes." Link to [[Iron-Condor]], [[Bull-Put-Spread]], [[IV-Rank]], [[Market-Condition-Classification]].

---

#### TASK-043 · Low IV Playbook
**Complexity:** 2 — Sonnet | **Output:** `05-Market-Conditions/Low-IV-Playbook.md`

**Prompt:**
> Write an Obsidian playbook note for trading in low IV environments (IV rank < 25, VIX < 15). Cover: (1) Why low IV is bad for sellers (thin premium, not worth the risk); (2) Strategies to deploy: LEAPS purchases (cheap long-term optionality), calendars and diagonals (long vega benefits from eventual IV expansion), debit spreads with good risk/reward; (3) What to avoid: naked premium selling, IC, CSP (insufficient premium to justify risk); (4) Patience rule: if IV rank < 20, the default is to hold cash and wait for opportunities; (5) Earnings plays become more attractive (buy pre-earnings for IV expansion). Practical threshold: "If the credit on a 0.25 delta CSP is less than 1% of the stock price, skip it." Link to [[High-IV-Playbook]], [[Calendar-Spread]], [[LEAPS]], [[Earnings-Overview]], [[Market-Condition-Classification]].

---

#### TASK-044 · Trending Market Strategies
**Complexity:** 2 — Sonnet | **Output:** `05-Market-Conditions/Trending-Market-Strategies.md`

**Prompt:**
> Write an Obsidian note on options strategies for trending markets (clear directional momentum, SPX making consistent higher highs or lower lows). Cover: (1) Uptrend: sell put credit spreads / CSP at pullback support levels; buy call debit spreads for defined-risk participation; avoid IC (one side will likely be tested); (2) Downtrend: sell call credit spreads at resistance; buy put debit spreads; avoid IC; (3) Trend identification: 20-day SMA slope, consecutive higher highs/lower lows; (4) Position sizing: increase size on the trend side, not full IC; (5) When the trend ends: be ready to exit directional positions quickly when price crosses 20-day SMA. Include a rule: "In a strong uptrend, only sell puts — never sell calls against a rising stock." Link to [[Bull-Put-Spread]], [[Bear-Call-Spread]], [[Market-Condition-Classification]], [[Range-Bound-Strategies]].

---

#### TASK-045 · Range-Bound Strategies
**Complexity:** 2 — Sonnet | **Output:** `05-Market-Conditions/Range-Bound-Strategies.md`

**Prompt:**
> Write an Obsidian note on options strategies for range-bound markets (stock or index oscillating within defined support and resistance). Cover: (1) Identification: Bollinger Bands contracting, ATR declining, stock bouncing between same levels 3+ times; (2) Best strategies: IC (short strikes at range boundaries), Iron Fly (if range is very tight), Butterfly (middle strike at midpoint of range); (3) Confirmation: sell at range extremes only, not in the middle; (4) Failure mode: breakout — define your stop at the range boundary, close IC if range breaks; (5) Expected DTE: trade ranges with 21–35 DTE so you don't have to monitor as the range resolves. Link to [[Iron-Condor]], [[Iron-Fly]], [[Market-Condition-Classification]], [[Adjust-vs-Close]].

---

### MODULE 6: RISK MANAGEMENT

---

#### TASK-046 · Position Sizing
**Complexity:** 2 — Sonnet | **Output:** `06-Risk-Management/Position-Sizing.md`

**Prompt:**
> Write an Obsidian note on position sizing for options traders. The single most important risk management skill. Cover: (1) The core rule: never risk more than 2–5% of total portfolio on a single trade (max loss basis); (2) How to calculate: for a $50-wide IC collecting $15, max loss = $35 × 100 = $3,500; on a $100K portfolio, max 2 contracts (2 × $3,500 = $7,000 = 7%); (3) For CSP: collateral requirement is the position size; 5% rule means max 5% of portfolio per CSP; (4) Scaling by IV: in high IV environments, reduce size 25–50%; (5) Correlation: never have more than 3–4 correlated positions (e.g., 3 SPY/SPX positions count as one); (6) The "sleep test": if a position loss would cause you to lose sleep, it's too big. Include a calculation table for a $100K portfolio. Add chart reference: `![[chart-position-sizing.png]]`. Link to [[Portfolio-Allocation]], [[Max-Risk-Per-Trade]], [[Drawdown-Management]].

---

#### TASK-047 · Portfolio Allocation
**Complexity:** 3 — Opus | **Output:** `06-Risk-Management/Portfolio-Allocation.md`

**Prompt:**
> Write an Obsidian note on portfolio-level allocation for an options income portfolio. Cover: (1) The three buckets: (a) Core income (IC, CSP, CC, Wheel) — 50–60% of capital; (b) Long-term growth (LEAPS, PMCC) — 20–30% of capital; (c) Speculative/0DTE — max 10–15% of capital; (2) Sector diversification: no more than 25% allocated to one sector; (3) Beta weighting: if all positions are correlated to SPX, you have concentrated market risk — use index trades to hedge; (4) Cash buffer: keep 20–30% in cash for opportunities and margin cushion; (5) Monthly review process: rebalance when any bucket drifts > 10% from target. Include a sample allocation table for a $200K portfolio. Include `> [!warning]`: "Options portfolios can appear diversified by ticker but be fully correlated by beta — check your total delta exposure." Link to [[Position-Sizing]], [[Max-Risk-Per-Trade]], [[Drawdown-Management]].

---

#### TASK-048 · Max Risk Per Trade
**Complexity:** 1 — Haiku | **Output:** `06-Risk-Management/Max-Risk-Per-Trade.md`

**Prompt:**
> Write a concise Obsidian reference note on maximum risk rules per trade type. Format as a table: Strategy | Max Risk per Trade (% of portfolio) | Notes. Entries: CSP (5%), Covered Call (notional of stock, size stock position to 5–10%), Bull Put / Bear Call Spread (2%), Iron Condor (2–3%), Iron Fly (2%), Butterfly (1%), Calendar (1%), PMCC (5% on LEAPS leg), 0DTE Credit Spread (0.5–1%), 0DTE IC (1%), Earnings trade (1–2%). Add section: "What counts as max loss" — for credit spreads: spread width minus credit; for CSP: strike minus premium; for LEAPS: full debit. Note: these are per-position limits, not total portfolio usage. Link to [[Position-Sizing]], [[Portfolio-Allocation]].

---

#### TASK-049 · Stop Loss Strategies
**Complexity:** 3 — Opus | **Output:** `06-Risk-Management/Stop-Loss-Strategies.md`

**Prompt:**
> Write a nuanced Obsidian note on stop loss strategies for options trades. This is nuanced because options stops differ from equity stops. Cover: (1) **P&L-based stops** — close when loss reaches 200% of credit received (the most common rule, e.g., if you collected $1.00 in credit, close when the spread is worth $3.00); (2) **Delta-based stops** — close when the short option's delta exceeds 0.50 (has gone from 0.25 OTM to near the money); (3) **Time-based stops** — close all positions with < 21 DTE regardless of P&L to avoid gamma risk; (4) **When NOT to use stops** — on defined-risk trades with small position sizes, sometimes it's better to let the trade expire worthless than to stop out at the worst moment; (5) **The 2x credit rule vs. the 3x rule** — research comparison: tastytrade recommends 2x close (tested on 10,000+ trades), others use 3x to allow recovery. Cover the tradeoff: smaller stop = more small losses but prevents catastrophic loss. Include `> [!warning]`: "Hard stops on options can trigger at the worst time — during a spike that immediately reverses. Consider conditional orders instead of hard stops." Link to [[Position-Sizing]], [[Adjust-vs-Close]], [[Drawdown-Management]].

---

#### TASK-050 · Drawdown Management
**Complexity:** 3 — Opus | **Output:** `06-Risk-Management/Drawdown-Management.md`

**Prompt:**
> Write a comprehensive Obsidian note on managing portfolio drawdowns for options traders. Cover: (1) Expected drawdown for an income strategy: even well-run IC portfolios can experience 10–20% drawdowns in volatile markets; (2) Drawdown tiers and responses: Tier 1 (5–10% drawdown) — review all positions, tighten entry criteria; Tier 2 (10–15%) — reduce all position sizes by 50%, take no new trades for 1 week; Tier 3 (> 15%) — stop all new trades, close all undefined risk positions, hold cash until conditions normalize; (3) Recovery math: a 20% drawdown requires a 25% gain to recover — the asymmetry argues for preserving capital above all; (4) Correlation analysis: during drawdowns, verify that losses aren't all correlated to one factor (beta, sector); (5) Psychological drawdown protocol: journal every day during a drawdown, do not deviate from the plan, expect 30–90 days recovery for a 15% drawdown. Add chart: `![[chart-drawdown-recovery.png]]`. Link to [[Position-Sizing]], [[Stop-Loss-Strategies]], [[Building-Discipline]], [[Portfolio-Allocation]].

---

#### TASK-051 · Portfolio Performance Metrics
**Complexity:** 2 — Sonnet | **Output:** `06-Risk-Management/Portfolio-Performance-Metrics.md`

**Prompt:**
> Write an Obsidian reference note on key performance metrics for an options income portfolio. Cover: (1) **Win rate** — target > 65% for income strategies; (2) **Average win vs. average loss** — acceptable to have average win < average loss if win rate compensates (e.g., 70% win rate with 0.5 win/loss ratio is profitable); (3) **Return on capital** — target 2–4% per month on deployed capital; (4) **Theta/Day** — how much theta your portfolio generates per calendar day; (5) **Max drawdown** — track rolling 6-month max drawdown; (6) **Sharpe ratio** — target > 1.0; (7) **Beta-weighted delta** — your net market exposure; (8) **Premium collected vs. premium returned** — what % of premium did you keep. How to track: use a spreadsheet or tastytrade's built-in tracker. Monthly review checklist. Link to [[Portfolio-Allocation]], [[Drawdown-Management]].

---

### MODULE 7: PROFIT TAKING

---

#### TASK-052 · 50% Profit vs. Holding to Expiry
**Complexity:** 3 — Opus | **Output:** `07-Profit-Taking/50pct-vs-Expiry.md`

**Prompt:**
> Write an Obsidian note on the data-backed case for closing trades at 50% profit vs. holding to expiry. Reference tastytrade research (10,000+ backtested trades). Cover: (1) The case for 50% close: same win rate, lower theta exposure, capital freed for next trade, avoids gamma risk in final weeks; (2) The math: a 45-DTE IC closed at 50% profit in ~15–20 DTE captures roughly 85% of max theta without holding through high-gamma period; (3) Variations by strategy: CSP (hold to 50% then close), IC (50% profit target), 0DTE (25–30% profit target because timeframe is compressed), calendars (75% profit target given longer holding period); (4) Counter-argument: holding to expiry maximizes per-trade profit but increases variance and drawdowns; (5) The opportunity cost argument: redeploying capital after 50% close into a fresh trade often yields more total return over a year. Add chart: `![[chart-50pct-vs-expiry.png]]`. Link to [[Iron-Condor]], [[CSP-Cash-Secured-Put]], [[Theta-Decay]], [[Scaling-Out-of-Winners]].

---

#### TASK-053 · Scaling Out of Winners
**Complexity:** 2 — Sonnet | **Output:** `07-Profit-Taking/Scaling-Out-of-Winners.md`

**Prompt:**
> Write an Obsidian note on scaling out of profitable options positions. Cover: (1) Why scale out: reduces risk while keeping some upside, reduces emotional attachment; (2) Practical rule for multi-contract positions: close 50% of contracts at 50% profit, let the remaining run to 75% profit or expiry; (3) For single-contract positions: close the entire position at 50% (can't split); (4) Rolling winners: taking profit and immediately re-entering at new strikes resets the theta clock — compare to simply closing and redeploying; (5) Profit-taking discipline: set limit orders when entering the trade (e.g., enter IC for $2.00 credit, immediately place a GTC close order at $1.00). Add `> [!tip]`: "Place your profit-taking order at the same time you enter the trade. Don't wait until you're in profit to decide what to do — emotion distorts judgment." Link to [[50pct-vs-Expiry]], [[Building-Discipline]].

---

### MODULE 8: ADJUSTMENTS & ROLLING

---

#### TASK-054 · Adjust vs. Close
**Complexity:** 3 — Opus | **Output:** `08-Adjustments/Adjust-vs-Close.md`

**Prompt:**
> Write a decision-framework Obsidian note on when to adjust vs. close losing options positions. This is the hardest decision in options trading. Cover: (1) Default rule: "When in doubt, close" — adjustments should only be made when there's a clear, logical reason; (2) Criteria for adjusting: DTE > 21, IV has not expanded dramatically (otherwise rolling often locks in losses), the underlying trend is still intact; (3) Criteria for closing: DTE < 14, IV has spiked (rolling is expensive), the trade thesis is broken (e.g., you sold a put because stock was at support — support broke), you've already hit max loss; (4) The "sunk cost" trap: never adjust to avoid realizing a loss — adjust only if the NEW trade would be worth putting on fresh; (5) Decision tree: DTE > 21? → IV normal? → Thesis intact? → Adjust. Any "No" → Close. Include `> [!warning]`: "Most losing adjustments are made to avoid admitting a mistake. Ask: 'Would I put this new trade on fresh right now?' If not, close." Link to [[Rolling-Basics]], [[Stop-Loss-Strategies]], [[Building-Discipline]].

---

#### TASK-055 · Rolling Basics
**Complexity:** 2 — Sonnet | **Output:** `08-Adjustments/Rolling-Basics.md`

**Prompt:**
> Write an Obsidian note on the basics of rolling options positions. Cover: (1) What rolling means: closing the current position and opening a new one simultaneously (single transaction); (2) Rolling out: same strike, later expiry — collects additional credit if IV allows; (3) Rolling out and up/down: later expiry + new strike — used when underlying has moved against you; (4) Rolling for credit vs. rolling for debit: always try to roll for a net credit or at worst breakeven — rolling for a debit compounds the loss; (5) Rolling rules: only roll when ≥21 DTE remain in original trade; if new expiry would be > 60 DTE, consider whether that's the trade you want; (6) Maximum number of rolls: set a limit (e.g., 2 rolls maximum before closing the position). Include a step-by-step example: you sold a put at $50 strike, stock drops to $48, with 30 DTE — roll the $50 put to the $47 put next month for a net credit of $0.20. Link to [[Rolling-Credit-Spreads]], [[Rolling-Iron-Condors]], [[Adjust-vs-Close]].

---

#### TASK-056 · Rolling Credit Spreads
**Complexity:** 2 — Sonnet | **Output:** `08-Adjustments/Rolling-Credit-Spreads.md`

**Prompt:**
> Write an Obsidian playbook note on rolling credit spreads (bull put and bear call). Cover: (1) When to roll a bull put spread: short put delta > 0.40, unrealized loss > 1.5× credit received, DTE > 21; (2) How to roll: buy back the spread, sell a new spread further OTM and/or in the next expiry, targeting a net credit; (3) Rolling down (for bull put): move both strikes lower to increase distance from stock; (4) Rolling out (for bull put): same strikes, next monthly expiry; (5) Rolling down and out: the most powerful adjustment — gains both time and distance; (6) Example: bull put $190/$185 tested when stock falls to $192, roll to $185/$180 next month for $0.15 credit. Include a decision table: Scenario | Action. Add `> [!warning]`: "Never roll a spread for a debit — this compounds your maximum loss." Link to [[Rolling-Basics]], [[Bull-Put-Spread]], [[Bear-Call-Spread]], [[Adjust-vs-Close]].

---

#### TASK-057 · Rolling Iron Condors
**Complexity:** 3 — Opus | **Output:** `08-Adjustments/Rolling-Iron-Condors.md`

**Prompt:**
> Write an Obsidian playbook note on adjusting and rolling Iron Condors. This is the most complex rolling scenario. Cover: (1) Rolling the untested side in: when one side is far OTM and winning, roll that winning spread closer to collect more credit — offsetting loss on the tested side; (2) Rolling the tested side out: close the losing spread and reopen further OTM + next expiry, collect net credit; (3) Converting to a condor to a one-sided trade: if one side is clearly going to lose, close the winning side and let the losing side ride (now a straight credit spread); (4) The inverted condor (broken IC): if both sides are tested, the IC has become inverted — close immediately, this is the worst-case scenario; (5) When not to adjust: if DTE < 14, just take the loss — don't roll a short-dated IC into a longer-dated position; (6) Practical examples with SPX numbers. Include a decision tree diagram in text. Link to [[Iron-Condor]], [[Rolling-Basics]], [[Adjust-vs-Close]], [[Stop-Loss-Strategies]].

---

#### TASK-058 · PMCC Adjustments
**Complexity:** 3 — Opus | **Output:** `08-Adjustments/PMCC-Adjustments.md`

**Prompt:**
> Write an Obsidian playbook note on adjusting the Poor Man's Covered Call (PMCC) when the trade moves against you. Cover four scenarios: (1) **Short call goes deep ITM** (stock rallies hard): roll the short call up and out to a higher strike in the next month for credit — never let the short call get deeper ITM than the LEAPS; (2) **LEAPS decays or loses value** (stock stagnant/down): evaluate rolling the LEAPS out 6–12 months when it has < 90 DTE; consider if the stock thesis is still valid; (3) **Stock drops 20%+**: stop selling short calls, let the LEAPS ride or close the position — do not sell calls below the LEAPS strike; (4) **IV collapse on LEAPS**: LEAPS loses value to vega — this is a risk when IV was high at entry; consider closing and waiting for IV normalization. Include specific decision thresholds (delta levels, DTE levels). Link to [[PMCC]], [[Rolling-Basics]], [[Adjust-vs-Close]], [[LEAPS]].

---

#### TASK-059 · 0DTE Adjustments
**Complexity:** 3 — Opus | **Output:** `08-Adjustments/0DTE-Adjustments.md`

**Prompt:**
> Write an Obsidian playbook note on managing 0DTE (same-day expiry) positions when they move against you. Key principle: 0DTE adjustments must be fast and decisive — you have no time. Cover: (1) **When the IC gets one-sided tested** (stock moves to one wing): close the entire IC immediately if the short strike delta > 0.40 — do not hope for a reversal; (2) **Converting to a hedge** (tested side): close the winning side, use the credit to widen the losing side's long strike to reduce max loss; (3) **Stop rules**: hard rule — never hold a 0DTE position past 3:45 PM if it's a loser; (4) **The reversal play**: if you're tested and convinced the move is exhausted (price action, volume drying up), close the short option on the tested side and hold the long — but this is speculative; (5) **Pre-defined exit levels**: before entering any 0DTE, know your stop level — write it down. Add `> [!warning]`: "0DTE gamma can move positions from safe to max loss in minutes. There is no 'wait and see' — have a plan before entering." Link to [[0DTE-Overview]], [[0DTE-Credit-Spread]], [[0DTE-Iron-Condor]], [[Adjust-vs-Close]].

---

#### TASK-060 · Losing Trade Mindset
**Complexity:** 1 — Haiku | **Output:** `08-Adjustments/Losing-Trade-Mindset.md`

**Prompt:**
> Write a short Obsidian note on the mindset for managing losing options trades without emotion. Cover: (1) Losses are part of the business — a 70% win rate means 30 losses per 100 trades; (2) The process is the edge — follow the rules, not your feelings; (3) A trade that loses is not a mistake if you followed the rules — a mistake is breaking the rules; (4) After-loss protocol: close the losing trade, journal what happened (market moved, not your error), take a 24-hour break from new trades; (5) Distinguish between: bad trade (violated rules) vs. bad outcome (followed rules but lost — acceptable). Include two quotes from professional traders. Link to [[Building-Discipline]], [[Drawdown-Management]], [[Adjust-vs-Close]].

---

### MODULE 9: 0DTE STRATEGIES

---

#### TASK-061 · 0DTE Overview
**Complexity:** 2 — Sonnet | **Output:** `04-Strategies/0DTE/0DTE-Overview.md`

**Prompt:**
> Write an Obsidian overview note on 0DTE (same-day expiry) options trading. Cover: (1) What 0DTE is: SPX options expire M/W/F, QQQ options expire M/W/F — daily expiry creates a new opportunity each day; (2) Why 0DTE is different: extreme theta decay, explosive gamma, high bid-ask spreads in illiquid strikes; (3) Who should use 0DTE: experienced traders only — not for beginners, requires active monitoring all day; (4) Advantages: fast premium collection, no overnight risk, defined entry/exit within single day; (5) Risks: gamma can cause rapid loss, easy to over-trade, addictive nature; (6) Capital requirements: use defined-risk only (credit spreads, IC, butterfly) — never sell naked 0DTE; (7) Daily loss limit: set a hard daily max loss (e.g., 1% of portfolio) and stop trading for the day if hit. Add `> [!warning]`: "0DTE trading is NOT passive income — it requires active monitoring and fast decision-making. Do not participate on days you cannot watch the screen." Link to [[0DTE-Credit-Spread]], [[0DTE-Iron-Condor]], [[0DTE-Butterfly]], [[Superfly]], [[SPX-vs-QQQ-0DTE]].

---

#### TASK-062 · SPX vs. QQQ for 0DTE
**Complexity:** 2 — Sonnet | **Output:** `04-Strategies/0DTE/SPX-vs-QQQ-0DTE.md`

**Prompt:**
> Write an Obsidian note comparing SPX and QQQ for 0DTE options trading. Cover: (1) SPX advantages: cash-settled (no assignment risk), 60/40 tax treatment, European exercise, higher liquidity on liquid strikes, larger expected moves provide more room; (2) SPX disadvantages: expensive — one SPX spread can be $500–$5,000 capital requirement, can be 2–10% wide in thin strikes; (3) QQQ advantages: lower capital requirement per spread, American exercise (risk of early assignment — prefer to trade European-style SPXW or XSP instead), more correlated to tech news; (4) QQQ disadvantages: American exercise risk, slightly less liquid than SPX, not cash-settled; (5) Recommendation: SPX or XSP (mini-SPX, 1/10 size) for 0DTE — avoid QQQ American-style assignment risk. Include a comparison table. Link to [[0DTE-Overview]], [[0DTE-Credit-Spread]], [[0DTE-Iron-Condor]].

---

#### TASK-063 · 0DTE Entry Timing
**Complexity:** 3 — Opus | **Output:** `04-Strategies/0DTE/0DTE-Entry-Timing.md`

**Prompt:**
> Write an Obsidian playbook note on 0DTE entry timing for SPX options. This is the most critical skill for 0DTE trading. Cover: (1) **Opening gap plays** (9:30–9:45 AM): if SPX gaps significantly (>0.5%), wait for first 15 minutes to settle before entering; if gap fills by 9:45, the range is likely set — enter an IC; (2) **Mid-morning entries** (10:00–11:00 AM): the ideal window — market has found its level, IV is normalized, IV crush from the open has already occurred; enter IC or credit spread; (3) **Midday entries** (11:00 AM–1:00 PM): lower priority — less premium, less volatility; only if a clear range has formed; (4) **Afternoon entries** (1:00–2:00 PM): aggressive theta decay is working — some traders enter IC with targets of 10–20% profit by close; (5) **Entry triggers**: use 5-minute chart, wait for a consolidation candle (narrow range) before entering; VIX should be stable or declining; (6) **Delta guidance for 0DTE**: IC wings at 0.10–0.15 delta = more premium but higher risk; 0.05 delta = less premium but very high probability. Include a time-of-day decision table. Add chart: `![[chart-0dte-ivx-by-time.png]]`. Link to [[0DTE-Overview]], [[0DTE-Iron-Condor]], [[Intraday-Timing-Open]].

---

#### TASK-064 · 0DTE Credit Spread
**Complexity:** 3 — Opus | **Output:** `04-Strategies/0DTE/0DTE-Credit-Spread.md`

**Prompt:**
> Write an Obsidian playbook note for 0DTE SPX credit spreads (bull put or bear call). This is the entry-level 0DTE strategy. Cover: (1) **Entry**: 10:00–11:00 AM, SPX credit spread, short leg at 0.10–0.15 delta, width $25–$50 depending on daily range, target credit 20–25% of width; (2) **Strike selection**: use the expected move (EM) as your guide — short strike should be outside 0.75× EM; (3) **Directional bias**: if SPX is clearly trending intraday, sell credit on the tested side only (don't fight the trend with a spread); (4) **Management**: close at 50% profit OR close by 3:30 PM; loss stop at 200% credit; (5) **Sizing**: maximum 1% portfolio per spread, 2 contracts for a $100K portfolio; (6) Specific example: SPX at 5000, expected move $30, sell 4940 put / buy 4915 put for $7.50 credit on $25-wide spread. Include `> [!warning]`: "Never hold a 0DTE loser past 3:45 PM — gamma will accelerate losses exponentially in the final minutes." Link to [[0DTE-Overview]], [[0DTE-Entry-Timing]], [[0DTE-Iron-Condor]], [[Bull-Put-Spread]].

---

#### TASK-065 · 0DTE Iron Condor
**Complexity:** 3 — Opus | **Output:** `04-Strategies/0DTE/0DTE-Iron-Condor.md`

**Prompt:**
> Write an Obsidian playbook note on 0DTE Iron Condors on SPX. Cover: (1) Setup: sell both a put spread and call spread on SPX for same-day expiry, total structure captures both sides of expected move range; (2) When to use: low-volatility days (VIX < 20), clear range established by 10:00 AM, no major news catalysts afternoon; (3) Strike selection: call spread short strike at 0.10–0.15 delta, put spread short strike at 0.10–0.15 delta, both $25–$50 wide; (4) Credit target: 15–25% of total wing width combined; (5) Management: close entire IC at 50% profit; if one side is tested (delta > 0.30), close entire IC — do not try to leg out on 0DTE; (6) Hard stop: close at 200% credit loss OR 3:45 PM, whichever first; (7) Example: SPX 5000, VIX 15, EM $25; sell 4960/4935 put spread and 5040/5065 call spread for $8 credit on $25-wide wings. Add chart: `![[pnl-0dte-ic.png]]`. Link to [[0DTE-Overview]], [[0DTE-Entry-Timing]], [[0DTE-Adjustments]], [[Iron-Condor]].

---

#### TASK-066 · 0DTE Butterfly
**Complexity:** 3 — Opus | **Output:** `04-Strategies/0DTE/0DTE-Butterfly.md`

**Prompt:**
> Write an Obsidian playbook note on 0DTE butterfly spreads on SPX. The butterfly is a directional bet on where SPX will pin by close — higher reward than IC but narrower profit zone. Cover: (1) Structure: buy 1 lower call, sell 2 ATM calls, buy 1 higher call — or put version; (2) When to use: when you have a specific price target for end of day (e.g., SPX is at 5000 and you expect it to close near 5000 — ATM fly); (3) Entry: 10:00–11:00 AM, center the fly at the likely EOD price (ATM or at strong support/resistance); (4) Cost: typically $3–$10 debit for a $25–$50 wide fly; (5) Target: close at 100%–200% profit on debit; (6) Management: close if underlying moves more than half the wing width from center; (7) Sizing: limit to 0.5% portfolio risk; (8) Specific example: SPX at 5000, buy 4975/5000/5025 call fly for $5 debit; max profit $20 at expiry if SPX = 5000. Add `> [!warning]`: "Butterflies require precise pinning — they can expire nearly worthless even if you're right directionally but off by 10 points." Link to [[0DTE-Overview]], [[Butterfly]], [[0DTE-Iron-Condor]], [[Superfly]].

---

#### TASK-067 · Superfly
**Complexity:** 3 — Opus | **Output:** `04-Strategies/0DTE/Superfly.md`

**Prompt:**
> Write an Obsidian strategy note on the Superfly — a 0DTE strategy targeting 100–300% returns in minutes using OTM butterfly spreads on SPX. This is a high-risk, low-probability trade — describe it accurately, including all risks. Cover: (1) Structure: buy an OTM butterfly centered near a key intraday support/resistance level — the bet is that SPX will reach that level by close; (2) Cost: typically $0.50–$2.00 debit for a $25-wide fly centered 20–40 points OTM; (3) Payout: if SPX hits the center strike at close, the fly is worth $25 — a 10–50× return; (4) Entry criteria: market is trending toward a specific level, VIX elevated (more movement expected), enter 30–60 minutes before close for best risk/reward; (5) Position sizing: maximum 0.25% portfolio — this is a lottery ticket, not a core strategy; (6) What makes this work: gamma explosion near expiry dramatically reprices OTM flies as stock approaches the center strike — the value can multiply 5–10× before the strike is actually reached. Add prominent `> [!warning]`: "This trade expires worthless 85–95% of the time. Only use small speculative allocation. It is NOT a reliable income strategy." Add chart: `![[chart-superfly-gamma.png]]`. Link to [[0DTE-Butterfly]], [[0DTE-Overview]], [[Gamma]], [[Portfolio-Allocation]].

---

### MODULE 10: EARNINGS STRATEGIES

---

#### TASK-068 · Earnings Overview
**Complexity:** 2 — Sonnet | **Output:** `09-Earnings/Earnings-Overview.md`

**Prompt:**
> Write an Obsidian overview note on earnings options trading — a data-driven approach that profits regardless of the earnings outcome. Cover: (1) The core insight: options IV rises dramatically before earnings (IV accumulation) and collapses after (IV crush) — this is the fundamental edge; (2) Two approaches: (a) sell premium before earnings (capture IV crush), (b) buy premium before earnings (bet on a larger-than-expected move); (3) The data-driven edge: historical comparison of implied earnings move vs. actual earnings move — stocks often move less than options predicted (IV overestimates moves ~60% of the time); (4) Timing: enter 1–5 days before earnings, exit next morning at open; (5) Risk: binary outcome — stock can gap far beyond the expected move; (6) Strategy selection framework: when to sell (IC, strangle), when to buy (straddle or debit spreads). Add chart: `![[chart-earnings-iv-crush.png]]`. Link to [[Earnings-Ticker-Selection]], [[IV-Crush-Mechanics]], [[Earnings-IC-Playbook]], [[Earnings-Tools]].

---

#### TASK-069 · IV Crush Mechanics
**Complexity:** 3 — Opus | **Output:** `09-Earnings/IV-Crush-Mechanics.md`

**Prompt:**
> Write a detailed Obsidian note on IV crush mechanics for earnings trading. Cover: (1) Why IV spikes before earnings: uncertainty premium — market makers widen spreads and IV increases to compensate for binary risk; (2) Why IV collapses after earnings: the uncertainty is resolved — regardless of outcome, the event risk disappears; (3) Typical IV crush magnitude: 30–60% drop in ATM IV overnight post-earnings; (4) How to measure expected IV crush: compare IV of options expiring the week of earnings vs. options expiring after — the difference is the "earnings premium"; (5) How to use this: sell the near-term IV (earnings options) and buy the next-expiry IV (calendar spread captures crush); (6) When IV crush is NOT enough: stock gaps beyond the expected move — the loss on delta more than offsets the IV crush gain; (7) Straddle price as expected move: the at-the-money straddle price ≈ the expected move; if straddle = $5 and stock is at $100, market expects ±5% move. Add chart: `![[chart-iv-crush-pattern.png]]`. Link to [[Earnings-Overview]], [[Earnings-IC-Playbook]], [[Earnings-Straddle-Strangle]].

---

#### TASK-070 · Earnings Ticker Selection
**Complexity:** 2 — Sonnet | **Output:** `09-Earnings/Earnings-Ticker-Selection.md`

**Prompt:**
> Write an Obsidian playbook note on selecting the right tickers for earnings options trades. Cover: (1) **Historical IV crush rate**: use Market Chameleon or Earnings Whispers to find stocks where the implied move has historically exceeded the actual move (IV overestimates) — target > 60% of earnings where actual < implied; (2) **Liquidity filter**: options volume must spike before earnings — avoid earnings plays on thinly traded stocks; minimum bid-ask of $0.05 or less on ATM options; (3) **Implied move size**: too small (< 3%) or too large (> 15%) earnings moves are harder to trade profitably; ideal range: 4–10% implied move; (4) **Avoiding binary event risk**: skip biotech, drug approvals, clinical trials — these are binary with fat tails; (5) **Best candidates**: mega-cap tech (AAPL, MSFT, NVDA, META, GOOGL, AMZN), large financial (JPM, GS), and liquid ETFs that report (e.g., XLP). Include a screening workflow using Market Chameleon's earnings screener. Link to [[Earnings-Overview]], [[Earnings-Tools]], [[Earnings-IC-Playbook]].

---

#### TASK-071 · Earnings IC Playbook
**Complexity:** 3 — Opus | **Output:** `09-Earnings/Earnings-IC-Playbook.md`

**Prompt:**
> Write an Obsidian playbook note on the earnings Iron Condor — selling an IC before earnings to capture IV crush. This is the primary earnings trade for income traders. Cover: (1) **Entry timing**: enter 1–3 days before earnings announcement, using the shortest-dated expiry that includes the earnings date; (2) **Strike selection**: short strikes at 1× to 1.5× the implied earnings move; if EM = $5 on a $100 stock, sell the $95/$92.50 put spread and $105/$107.50 call spread; (3) **Credit target**: collect at least 25–30% of wing width; (4) **Exit**: close at the next market open after earnings — do not hold through the second day; (5) **Risk scenario**: stock moves beyond the expected move — define your max loss (spread width minus credit) before entering; (6) **Position sizing**: max 1–2% portfolio due to binary risk; (7) **Historical edge**: this trade wins when actual move < implied move — historically ~55–65% of the time for high-IV stocks; (8) **Example with AAPL numbers**: AAPL at $200, EM = $8, sell $190/$187.50 put spread + $210/$212.50 call spread for $1.50 credit on $2.50-wide wings. Add `> [!warning]`: "This trade can lose 3–5× the credit received in a single gap. Always use defined risk (never a naked short strangle on earnings)." Add chart: `![[chart-earnings-ic-example.png]]`. Link to [[IV-Crush-Mechanics]], [[Iron-Condor]], [[Earnings-Ticker-Selection]], [[Earnings-Execution-Playbook]].

---

#### TASK-072 · Earnings Straddle/Strangle
**Complexity:** 3 — Opus | **Output:** `09-Earnings/Earnings-Straddle-Strangle.md`

**Prompt:**
> Write an Obsidian strategy note on buying straddles or strangles before earnings — the opposite bet (profiting from a move larger than expected). Cover: (1) **Straddle**: buy ATM call and put — profits if stock moves more than the straddle cost in either direction; breakeven = strike ± straddle premium; (2) **Strangle**: buy OTM call and OTM put — cheaper than straddle but requires a bigger move; (3) **When to buy (not sell) earnings**: when historical data shows the actual move has repeatedly exceeded the implied move for this specific stock; use Market Chameleon data; (4) **Entry timing**: 5–7 days before earnings (before IV fully inflates); (5) **Risk**: IV crush wipes out a large portion of value even if stock moves — you need the move to exceed the full implied move to profit; (6) **Alternative: debit spread**: buy a call spread or put spread directionally if you have a conviction on direction — reduces vega exposure; (7) **Exit**: always exit before or immediately after earnings — holding through earnings on a long straddle can be profitable but also risky if IV drops more than stock moves. Link to [[IV-Crush-Mechanics]], [[Earnings-IC-Playbook]], [[Earnings-Overview]].

---

#### TASK-073 · Earnings Strategy Matching
**Complexity:** 3 — Opus | **Output:** `09-Earnings/Earnings-Strategy-Matching.md`

**Prompt:**
> Write an Obsidian decision note on matching the right earnings strategy to the right situation. Cover a decision framework: (1) Is historical IV overestimating the actual move? (> 60% of past earnings) → Sell premium (IC or IC spread); (2) Is historical IV underestimating? (< 40% of past earnings) → Buy premium (straddle, strangle, or debit spread); (3) Do I have directional conviction? → Yes: buy a debit spread (defined risk, directional); No: use IC or straddle; (4) Is the implied move unusually large vs. history? → Sell (IV elevated, crush will be large); Is it unusually small? → Buy (potential for bigger actual move); (5) What's the stock volatility profile? → High-growth volatile (NVDA, TSLA) = be careful selling; blue-chip (AAPL, MSFT) = safer to sell. Include a decision matrix. Add: "The playbook is only as good as your data — always check historical earnings move vs. implied move before every trade." Link to [[Earnings-IC-Playbook]], [[Earnings-Straddle-Strangle]], [[Earnings-Tools]].

---

#### TASK-074 · Earnings Tools
**Complexity:** 2 — Sonnet | **Output:** `09-Earnings/Earnings-Tools.md`

**Prompt:**
> Write an Obsidian reference note on tools for earnings options research. Cover: (1) **Market Chameleon** (marketchameleon.com): earnings history (implied move vs actual), IV rank before/after earnings, earnings calendar; how to pull the data, what columns matter (implied move %, actual move %, beat/miss rate); (2) **Earnings Whispers** (earningswhispers.com): earnings calendar, whisper numbers, after-hours gappers; (3) **Barchart**: options IV chart showing IV spike pre-earnings and crush post-earnings; (4) **ThinkorSwim** earnings calendar: how to set up a watchlist filtered by upcoming earnings in 1–14 days; (5) **ORATS** (more advanced): historical earnings move data, backtesting capabilities; (6) **Free option**: Yahoo Finance / Finviz earnings calendars for basic scheduling. For each tool: what it's best for, what it costs, what data to extract. Link to [[Earnings-Overview]], [[Earnings-Ticker-Selection]], [[Screener-Setup]].

---

#### TASK-075 · Earnings Execution Playbook
**Complexity:** 2 — Sonnet | **Output:** `09-Earnings/Earnings-Execution-Playbook.md`

**Prompt:**
> Write an Obsidian step-by-step execution playbook for earnings trades. The workflow is: research → setup → enter → monitor → exit. Cover each step with specifics: (1) **Monday/Tuesday**: pull Market Chameleon earnings calendar for the week, identify candidates meeting [[Earnings-Ticker-Selection]] criteria; (2) **Day before earnings** (before close): confirm the setup — check current IV rank, check straddle price for EM, run [[High-Probability-Setup-Checklist]]; enter the trade 30–60 minutes before market close; (3) **Earnings night**: do nothing — the trade is on; (4) **Next morning** (earnings day): at market open (9:30–9:45 AM), close the trade at market. Do not use limit orders at open — use market orders to guarantee fill; (5) **P&L review**: compare outcome to expected, log in journal. Include `> [!tip]`: "Set an alarm for 9:25 AM on the earnings day. Your job is to close the trade at open, not to evaluate it — you'll evaluate it later." Link to [[Earnings-IC-Playbook]], [[Earnings-Straddle-Strangle]], [[Building-Discipline]].

---

### MODULE 11: LONG-TERM INVESTING

---

#### TASK-076 · LEAPS Investing
**Complexity:** 2 — Sonnet | **Output:** `04-Strategies/Long-Term/LEAPS-Investing.md`

**Prompt:**
> Write an Obsidian strategy note on LEAPS as a long-term investing tool (not for PMCC — purely for directional long-term exposure). Cover: (1) LEAPS as stock replacement: buy a 70–80 delta call LEAPS to participate in a stock's upside with 70–80% of the capital and defined max loss; (2) How to size: LEAPS replaces 100 shares — calculate equivalent stock exposure; (3) Strike selection: deep ITM (70–80 delta) gives stock-like behavior; ATM LEAPS gives cheaper entry with more leverage but more time decay exposure; (4) DTE: buy 1.5–2 years out — gives time for the thesis to play out and reduces daily theta drag; (5) Exit planning: roll to the next year when 6–9 months remain; (6) Best tickers: use on high-conviction stock or ETF picks where you want long-term bullish exposure without tying up full capital; (7) Tax treatment: LEAPS held > 1 year qualify for long-term capital gains if structured as long options (not as a covered call). Add chart: `![[chart-leaps-vs-stock.png]]`. Link to [[LEAPS]], [[PMCC]], [[PMCC-Income]], [[Zero-Risk-Collar]].

---

#### TASK-077 · PMCC for Income (Long-Term)
**Complexity:** 3 — Opus | **Output:** `04-Strategies/Long-Term/PMCC-Income.md`

**Prompt:**
> Write an Obsidian strategy note on using the PMCC as a long-term income engine (distinct from the mechanics note [[PMCC]] which covers structure). Cover: (1) The compounding effect: model how 24 monthly short call sales on a LEAPS position can eventually pay for the LEAPS entirely; include a numerical example with AAPL or MSFT; (2) Target annual return: aim to collect 15–25% of LEAPS cost annually via short calls; (3) Strike discipline over time: don't chase yield by selling calls too close to money — maintain at least 5% OTM to allow for stock appreciation; (4) LEAPS replacement strategy: when to roll the LEAPS to the next year and how to do it for a net debit that is covered by accumulated short call credit; (5) Portfolio allocation: how many PMCC positions make sense in a $100K–$500K portfolio; (6) Risks: the LEAPS decays if the stock stagnates — it is not a free lunch; (7) Comparison to traditional covered call: capital efficiency advantage. Include numerical table showing year 1, 2, 3 income projections. Link to [[PMCC]], [[LEAPS-Investing]], [[Covered-Call]].

---

#### TASK-078 · Zero Risk Collar
**Complexity:** 2 — Sonnet | **Output:** `04-Strategies/Long-Term/Zero-Risk-Collar.md`

**Prompt:**
> Write an Obsidian strategy note on the Zero Risk Collar — a strategy for protecting an existing stock position at no net cost. Structure: own stock, buy OTM put (downside protection), sell OTM call (finances the put). When the premiums are equal, the collar is "zero cost." Cover: (1) How to construct: for a stock at $100, buy the $90 put and sell the $110 call — if both cost $3, net cost is zero; (2) Tradeoff: you give up upside above $110 to fund downside protection below $90; (3) When to use: you own a stock with large unrealized gains that you cannot or do not want to sell (tax reasons, company stock, etc.); (4) DTE: 3–6 months to allow meaningful protection; (5) Delta matching: the put and call don't need to be the same delta — adjust strikes to achieve zero net cost; (6) Tax considerations: collars on long-term holdings do not trigger taxable events (typically) but consult a tax advisor; (7) Active management: roll both legs annually. Add `> [!warning]`: "Collars cap your upside — you will underperform if the stock rallies strongly." Add chart: `![[pnl-zero-risk-collar.png]]`. Link to [[Advanced-Collar]], [[Covered-Call]], [[CSP-Cash-Secured-Put]].

---

#### TASK-079 · Advanced Collar
**Complexity:** 3 — Opus | **Output:** `04-Strategies/Long-Term/Advanced-Collar.md`

**Prompt:**
> Write an Obsidian strategy note on the Advanced Collar — a version that amplifies upside while maintaining downside protection. This is a nuanced multi-leg structure. Cover: (1) The problem with standard collar: hard cap on upside; (2) Advanced collar solution: use a call spread instead of a single short call — sell the lower call strike, buy a higher call strike, creating a call spread that gives you partial participation in a rally above the sold strike; (3) Structure example: stock at $100, buy $90 put, sell $110/$120 call spread — net cost may be a small debit but you now participate in moves from $110–$120; (4) Variation: use proceeds from the call spread to fund a ratio put backspread for increased downside protection; (5) When to use: on a concentrated long stock position where you want tax-efficient protection with some upside participation; (6) Risk: more complex, harder to manage, potential for small net debit; (7) Management: roll annually, evaluate whether the additional complexity justified the outcome. Add chart: `![[pnl-advanced-collar.png]]`. Link to [[Zero-Risk-Collar]], [[Covered-Call]], [[Portfolio-Margin]].

---

#### TASK-080 · Portfolio Margin
**Complexity:** 3 — Opus | **Output:** `04-Strategies/Long-Term/Portfolio-Margin.md`

**Prompt:**
> Write an Obsidian note on portfolio margin for advanced options traders. Cover: (1) What portfolio margin is: risk-based margin calculation that considers the net portfolio delta and vega, rather than individual position rules (Reg-T); (2) Requirements: typically requires $100K–$125K minimum portfolio, 2+ years options trading experience; (3) Capital efficiency: a hedged portfolio (e.g., stock with protective put) can require 50–70% less margin than Reg-T; (4) How to apply: request from broker, demonstrate options knowledge; (5) Risks: leverage is available to increase position size — this amplifies both gains AND losses; (6) Practical use for collars and PMCC: a delta-neutral or low-delta portfolio uses very little margin, enabling more capital to be deployed; (7) Risk management with PM: calculate stress test scenarios (what happens if market drops 20% overnight?), maintain a cash buffer; (8) Brokers: Interactive Brokers (most capital-efficient PM), tastytrade, TD Ameritrade. Include `> [!warning]`: "Portfolio margin is a tool, not a license to increase leverage. The extra buying power should be used for hedging, not speculation." Link to [[Advanced-Collar]], [[Zero-Risk-Collar]], [[Portfolio-Allocation]].

---

### MODULE 12: CHARTS

---

#### TASK-081 · P&L Diagrams Script
**Complexity:** 3 — Opus | **Output:** `Charts/pnl_diagrams.py`

**Prompt:**
> Write a well-documented Python script (`pnl_diagrams.py`) that generates P&L diagrams for all major options strategies and saves them as both PNG (for Obsidian embedding) and HTML (interactive). Use `matplotlib` for PNG and `plotly` for HTML.
>
> Strategies to generate: (1) long call, (2) short put (CSP), (3) covered call, (4) bull put credit spread, (5) bear call credit spread, (6) iron condor, (7) iron fly, (8) butterfly (call), (9) calendar spread (simplified, at expiry of short leg), (10) collar, (11) PMCC (at short call expiry).
>
> For each diagram: x-axis = underlying price at expiry, y-axis = P&L in dollars, show breakeven line(s), max profit line, max loss line. Use a clean style (no grid clutter). Add the strategy name as title. Use realistic sample inputs (e.g., SPX IC with $50-wide spreads collecting $15 credit).
>
> Script structure: each strategy is a function `def plot_[strategy](save_dir)`. A `main()` function calls all of them. Include docstrings on every function documenting the formula used. Include `if __name__ == "__main__": main()`.
>
> Output files: `outputs/pnl-csp.png`, `outputs/pnl-covered-call.png`, `outputs/pnl-bull-put-spread.png`, `outputs/pnl-iron-condor.png`, etc.

---

#### TASK-082 · IV Charts Script
**Complexity:** 3 — Opus | **Output:** `Charts/iv_charts.py`

**Prompt:**
> Write a documented Python script (`iv_charts.py`) that generates implied volatility educational charts. Use `matplotlib` for PNG and `plotly` for HTML.
>
> Charts to generate:
> (1) **Theta decay curve** (`chart-theta-decay-curve.png`): theta of an ATM option vs. DTE (from 90 to 0 DTE), showing the acceleration in the last 30 days;
> (2) **IV rank distribution** (`chart-ivr-distribution.png`): histogram of IVR values for a sample universe of stocks, with color bands (low/mid/high IVR zones);
> (3) **IV crush pattern** (`chart-iv-crush-pattern.png`): simulated IV trajectory going into earnings (rising) and post-earnings (crushing), 30-day window;
> (4) **IV term structure** (`chart-iv-term-structure.png`): two lines — normal (upward sloping) and inverted (post-spike) IV curves across expirations;
> (5) **Gamma vs DTE** (`chart-gamma-vs-dte.png`): gamma of an ATM option as a function of DTE, showing gamma explosion near expiry.
>
> Use Black-Scholes Greeks formulas. Include scipy.stats.norm in calculations. Docstring every function with the formula used. Use realistic parameters (SPX-like: spot 5000, risk-free 5%, realistic IV levels).

---

#### TASK-083 · Timing Charts Script
**Complexity:** 2 — Sonnet | **Output:** `Charts/timing_charts.py`

**Prompt:**
> Write a documented Python script (`timing_charts.py`) that generates educational charts on options trading timing patterns. Use `matplotlib` for PNG.
>
> Charts to generate:
> (1) **Intraday VIX pattern** (`chart-0dte-ivx-by-time.png`): simulated intraday VIX/IV index level through a typical day (9:30 AM to 4:00 PM), showing the open spike, midday calm, and afternoon activity;
> (2) **Intraday SPX volume pattern** (`chart-intraday-volume.png`): typical intraday volume curve showing U-shape (high at open, low midday, high at close);
> (3) **Expected earnings move vs actual** (`chart-earnings-ic-example.png`): bar chart for a sample of 20 earnings events, showing implied move (blue bar) vs actual move (orange bar), highlighting how often actual < implied;
> (4) **Superfly gamma profile** (`chart-superfly-gamma.png`): OTM butterfly value vs underlying price for 4 time scenarios (30 min, 60 min, 120 min, 240 min before expiry), showing gamma explosion near strikes.
>
> Use synthetic/realistic data (clearly label as illustrative). Docstring every function.

---

#### TASK-084 · Risk Charts Script
**Complexity:** 3 — Opus | **Output:** `Charts/risk_charts.py`

**Prompt:**
> Write a documented Python script (`risk_charts.py`) that generates portfolio risk management educational charts. Use `matplotlib` and `numpy`.
>
> Charts to generate:
> (1) **Drawdown recovery curve** (`chart-drawdown-recovery.png`): bar chart showing required return to recover from various drawdown levels (10%, 15%, 20%, 25%, 30%, 40%, 50%), illustrating asymmetry;
> (2) **50% profit close vs expiry** (`chart-50pct-vs-expiry.png`): two simulated equity curves over 100 trades — one closing at 50% profit, one holding to expiry — showing risk-adjusted return comparison;
> (3) **Win rate vs profit factor** (`chart-winrate-profit-factor.png`): heatmap of expected value across combinations of win rates (50%–80%) and win/loss ratios (0.3–2.0), color-coded positive/negative EV;
> (4) **Position sizing impact** (`chart-position-sizing.png`): simulation of 200 trades showing portfolio growth curves for 1%, 2%, 5%, and 10% risk-per-trade sizing.
>
> Use Monte Carlo simulation for equity curves (1000 paths). Docstring every function with the statistical method used.

---

#### TASK-085 · Earnings Charts Script
**Complexity:** 2 — Sonnet | **Output:** `Charts/earnings_charts.py`

**Prompt:**
> Write a documented Python script (`earnings_charts.py`) that generates earnings-related educational charts for the options curriculum. Use `matplotlib` and `plotly`.
>
> Charts to generate:
> (1) **Earnings IV crush pattern** (`chart-earnings-iv-crush.png`): line chart showing ATM IV over a 30-day window centered on an earnings date — IV accumulation pre-earnings, spike on day-before, crush post-announcement;
> (2) **Implied vs actual earnings moves** (`chart-earnings-move-comparison.png`): scatter plot with implied move on x-axis, actual move on y-axis, showing the distribution of moves relative to implied — with the 45-degree "priced right" line;
> (3) **Earnings IC P&L at expiry** (`chart-earnings-ic-example.png`): P&L diagram for a sample earnings IC, with zones labeled: "IV crush profits here", "stock move hurts here", "max loss zone";
> (4) **IV percentile before earnings histogram** (`chart-iv-preearnings-distribution.png`): distribution of IVP values 5 days before earnings for a sample of 100 earnings events.
>
> Use synthetic but realistic data clearly labeled as illustrative. Document each function with data source assumptions.

---

## Progress Tracker

| Task | Title | Complexity | Status |
|------|-------|-----------|--------|
| TASK-001 | Vault Templates | 1 | ☐ |
| TASK-002 | Home MOC | 1 | ☐ |
| TASK-003 | Module MOCs | 1 | ☐ |
| TASK-004 | Charts README | 2 | ☐ |
| TASK-005 | Glossary | 1 | ☐ |
| TASK-006 | Options Basics | 1 | ☐ |
| TASK-007 | Greeks Overview | 2 | ☐ |
| TASK-008 | Delta | 1 | ☐ |
| TASK-009 | Theta Decay | 2 | ☐ |
| TASK-010 | Vega | 1 | ☐ |
| TASK-011 | Gamma | 2 | ☐ |
| TASK-012 | IV vs HV | 2 | ☐ |
| TASK-013 | IV Rank | 2 | ☐ |
| TASK-014 | IV Percentile | 1 | ☐ |
| TASK-015 | Ticker Selection System | 2 | ☐ |
| TASK-016 | Ticker Criteria Technical | 2 | ☐ |
| TASK-017 | Ticker Criteria Fundamental | 1 | ☐ |
| TASK-018 | Screener Setup | 2 | ☐ |
| TASK-019 | High-Probability Checklist | 2 | ☐ |
| TASK-020 | Setup Recognition Patterns | 3 | ☐ |
| TASK-021 | Best Days of Week | 2 | ☐ |
| TASK-022 | Intraday Timing — Open | 2 | ☐ |
| TASK-023 | Intraday Timing — Power Hour | 1 | ☐ |
| TASK-024 | Intraday Timing — Midday | 1 | ☐ |
| TASK-025 | Entry Confirmation Signals | 2 | ☐ |
| TASK-026 | When NOT to Trade | 2 | ☐ |
| TASK-027 | Building Discipline | 2 | ☐ |
| TASK-028 | CSP — Cash Secured Put | 2 | ☐ |
| TASK-029 | Covered Call | 2 | ☐ |
| TASK-030 | Wheel Strategy | 3 | ☐ |
| TASK-031 | Bull Put Spread | 2 | ☐ |
| TASK-032 | Bear Call Spread | 2 | ☐ |
| TASK-033 | Iron Condor | 3 | ☐ |
| TASK-034 | Iron Fly | 2 | ☐ |
| TASK-035 | Butterfly | 2 | ☐ |
| TASK-036 | Fly vs IC | 3 | ☐ |
| TASK-037 | Calendar Spread | 2 | ☐ |
| TASK-038 | Diagonal Spread | 2 | ☐ |
| TASK-039 | LEAPS Overview | 2 | ☐ |
| TASK-040 | PMCC | 3 | ☐ |
| TASK-041 | Market Condition Classification | 2 | ☐ |
| TASK-042 | High IV Playbook | 2 | ☐ |
| TASK-043 | Low IV Playbook | 2 | ☐ |
| TASK-044 | Trending Market Strategies | 2 | ☐ |
| TASK-045 | Range-Bound Strategies | 2 | ☐ |
| TASK-046 | Position Sizing | 2 | ☐ |
| TASK-047 | Portfolio Allocation | 3 | ☐ |
| TASK-048 | Max Risk Per Trade | 1 | ☐ |
| TASK-049 | Stop Loss Strategies | 3 | ☐ |
| TASK-050 | Drawdown Management | 3 | ☐ |
| TASK-051 | Portfolio Performance Metrics | 2 | ☐ |
| TASK-052 | 50% vs Expiry | 3 | ☐ |
| TASK-053 | Scaling Out of Winners | 2 | ☐ |
| TASK-054 | Adjust vs Close | 3 | ☐ |
| TASK-055 | Rolling Basics | 2 | ☐ |
| TASK-056 | Rolling Credit Spreads | 2 | ☐ |
| TASK-057 | Rolling Iron Condors | 3 | ☐ |
| TASK-058 | PMCC Adjustments | 3 | ☐ |
| TASK-059 | 0DTE Adjustments | 3 | ☐ |
| TASK-060 | Losing Trade Mindset | 1 | ☐ |
| TASK-061 | 0DTE Overview | 2 | ☐ |
| TASK-062 | SPX vs QQQ 0DTE | 2 | ☐ |
| TASK-063 | 0DTE Entry Timing | 3 | ☐ |
| TASK-064 | 0DTE Credit Spread | 3 | ☐ |
| TASK-065 | 0DTE Iron Condor | 3 | ☐ |
| TASK-066 | 0DTE Butterfly | 3 | ☐ |
| TASK-067 | Superfly | 3 | ☐ |
| TASK-068 | Earnings Overview | 2 | ☐ |
| TASK-069 | IV Crush Mechanics | 3 | ☐ |
| TASK-070 | Earnings Ticker Selection | 2 | ☐ |
| TASK-071 | Earnings IC Playbook | 3 | ☐ |
| TASK-072 | Earnings Straddle/Strangle | 3 | ☐ |
| TASK-073 | Earnings Strategy Matching | 3 | ☐ |
| TASK-074 | Earnings Tools | 2 | ☐ |
| TASK-075 | Earnings Execution Playbook | 2 | ☐ |
| TASK-076 | LEAPS Investing | 2 | ☐ |
| TASK-077 | PMCC Income (Long-Term) | 3 | ☐ |
| TASK-078 | Zero Risk Collar | 2 | ☐ |
| TASK-079 | Advanced Collar | 3 | ☐ |
| TASK-080 | Portfolio Margin | 3 | ☐ |
| TASK-081 | P&L Diagrams Script | 3 | ☐ |
| TASK-082 | IV Charts Script | 3 | ☐ |
| TASK-083 | Timing Charts Script | 2 | ☐ |
| TASK-084 | Risk Charts Script | 3 | ☐ |
| TASK-085 | Earnings Charts Script | 2 | ☐ |

**Total: 85 tasks** | Complexity 1: 17 | Complexity 2: 40 | Complexity 3: 28

---

## Suggested Build Order

1. **Week 1** — Infrastructure first: TASK-001 through TASK-005 (templates, MOCs, glossary)
2. **Week 2** — Foundations: TASK-006 through TASK-014 (Greeks, IV concepts)
3. **Week 3** — Finding opportunities + Entry/Exit: TASK-015 through TASK-027
4. **Week 4** — Core income strategies: TASK-028 through TASK-040
5. **Week 5** — Market conditions + Risk management: TASK-041 through TASK-053
6. **Week 6** — Adjustments + 0DTE: TASK-054 through TASK-067
7. **Week 7** — Earnings strategies: TASK-068 through TASK-075
8. **Week 8** — Long-term strategies: TASK-076 through TASK-080
9. **Week 9** — All charts: TASK-081 through TASK-085, then embed chart references into all notes
