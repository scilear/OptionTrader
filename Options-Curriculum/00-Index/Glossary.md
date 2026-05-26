---
title: Glossary
tags: [glossary, reference]
status: draft
---

# Options Trading Glossary

Alphabetical reference of core options trading terms, Greeks, strategy names, and key concepts.

---

**Assignment** — The obligation triggered when an options seller is selected to fulfill a contract; a put seller must buy shares at the strike, a call seller must sell shares at the strike.

**ATM (At-the-Money)** — A strike price equal or very close to the current price of the underlying asset. ATM options have the highest theta decay rate in percentage terms.

**Backspread** — A ratio strategy where more options are bought than sold, producing net long premium and positive vega; opposite of a ratio spread.

**Bear Call Spread** — A defined-risk credit spread: sell a call at a lower strike, buy a call at a higher strike. Profits when the underlying stays below the short strike. See [[Bear-Call-Spread]].

**Bid-Ask Spread** — The difference between the highest price a buyer will pay (bid) and the lowest price a seller will accept (ask). Wide spreads increase transaction costs and reduce edge.

**Breakeven** — The underlying price at which a position produces neither profit nor loss at expiration, accounting for premium received or paid.

**Bull Put Spread** — A defined-risk credit spread: sell a put at a higher strike, buy a put at a lower strike. Profits when the underlying stays above the short strike. See [[Bull-Put-Spread]].

**Butterfly (Fly)** — A three-strike, four-leg spread combining a bull spread and a bear spread. The body (short strikes) is at or near ATM; the wings are equidistant. Maximum profit at expiration equals the body strike price. See [[Butterfly]].

**Calendar Spread** — A two-leg position selling a near-term option and buying a further-dated option at the same strike. Profits from time decay differential and IV term structure. See [[Calendar-Spread]].

**Call** — A contract giving the buyer the right, but not the obligation, to purchase the underlying at the strike price on or before expiration.

**CC (Covered Call)** — Selling a call against 100 shares of stock owned. Generates premium income; caps upside above the short strike. See [[Covered-Call]].

**Collar** — Buying a protective put and selling a covered call against a stock position, limiting both downside and upside. See [[Zero-Risk-Collar]] and [[Advanced-Collar]].

**Credit** — Premium received when opening a position. The maximum profit for a credit trade is the net credit received.

**Credit Spread** — Any spread where premium is received net (sold spread). Includes bull put spreads and bear call spreads. See [[Bull-Put-Spread]], [[Bear-Call-Spread]].

**CSP (Cash-Secured Put)** — Selling a put while holding enough cash to buy the shares if assigned. Generates income; obligates the seller to purchase stock at the strike. See [[CSP-Cash-Secured-Put]].

**Debit** — Premium paid when opening a position. The maximum loss for a debit trade is the net debit paid.

**Debit Spread** — Any spread where premium is paid net (bought spread). Risk is limited to the debit; profit potential is capped.

**Defined Risk** — A position where the maximum possible loss is known before entry. Credit spreads, iron condors, and butterflies are defined-risk strategies.

**Delta** — The rate of change of an option's price per $1 move in the underlying. Also approximates the probability that the option expires in-the-money. Range: 0 to 1 for calls, -1 to 0 for puts.

**Delta-Neutral** — A position constructed so that the combined delta is near zero, minimizing directional exposure. Used to isolate volatility or theta as the primary P&L driver.

**Diagonal Spread** — A two-leg spread with different strikes and different expirations. Combines elements of a vertical and a calendar spread. See [[Diagonal-Spread]].

**DTE (Days to Expiration)** — Number of calendar days until an option contract expires. A key variable in theta decay; 21–45 DTE is the most common range for premium selling.

**Expected Move** — The market-implied one standard deviation price range for the underlying over a given period, derived from ATM straddle price: EM ≈ ATM straddle price × 0.68.

**Exercise** — The act of using an option contract's right: a call buyer exercises to buy shares; a put buyer exercises to sell shares.

**Fly** — Common shorthand for Butterfly. See **Butterfly**.

**Gamma** — The rate of change of delta per $1 move in the underlying. Gamma is highest for ATM options near expiration. Short gamma positions lose money from large moves; long gamma positions benefit.

**Historical Volatility (HV)** — The annualized standard deviation of actual past price returns, typically measured over 20, 30, or 252 days. Compared to IV to assess whether options are rich or cheap.

**IC (Iron Condor)** — A four-leg, defined-risk trade combining a bull put spread and a bear call spread. Profits when the underlying stays inside the tent (between short strikes). See [[Iron-Condor]].

**Implied Volatility (IV)** — The market's forward-looking estimate of annualized price volatility, back-solved from an option's market price using Black-Scholes. Rising IV increases option prices; falling IV decreases them.

**IV Crush** — The sharp drop in implied volatility that typically follows a binary event (earnings, FOMC). Option sellers profit; option buyers are harmed. See [[IV-Crush-Mechanics]].

**IV Percentile** — The percentage of daily IV observations in the lookback window that are below the current IV. Similar to IV rank but less sensitive to outliers.

**IV Rank (IVR)** — A 0–100 measure of where current IV sits relative to its 52-week high and low: IVR = (IV_current − IV_low) / (IV_high − IV_low) × 100. IVR > 50 favors selling premium.

**Iron Fly (Iron Butterfly)** — An iron condor with both spreads sharing the same body strike. Maximum premium collected; narrower profit zone than a standard IC. See [[Iron-Fly]].

**ITM (In-the-Money)** — A call is ITM when its strike is below the current price; a put is ITM when its strike is above the current price. ITM options have intrinsic value.

**LEAPS** — Long-term Equity Anticipation Securities; options with expirations greater than one year. Used as stock substitutes or for leveraged long exposure. See [[LEAPS]] and [[LEAPS-Investing]].

**Liquidity** — The ease with which a contract can be bought or sold without significantly moving the market. High open interest and volume, and tight bid-ask spreads, indicate good liquidity.

**Max Loss** — The worst-case loss possible in a position, achieved at expiration when the underlying is at the least favorable extreme. For credit spreads: spread width minus credit received.

**Max Profit** — The best-case profit possible in a position. For credit trades: the net credit received. For debit trades: the spread width minus the debit paid.

**Moneyness** — Describes the relationship between the option's strike and the underlying price: ITM, ATM, or OTM.

**Net Premium** — The net cash flow from opening a position: credit received minus debit paid (for credit spreads), or debit paid (for long positions).

**0DTE (Zero Days to Expiration)** — Options expiring on the same trading day. Extremely high gamma and theta; require intraday discipline and tight risk rules. See [[0DTE-Overview]].

**Open Interest (OI)** — The total number of outstanding option contracts not yet settled or exercised. High OI is a proxy for liquidity and market participant activity.

**OTM (Out-of-the-Money)** — A call is OTM when its strike is above the current price; a put is OTM when its strike is below. OTM options have no intrinsic value, only time value.

**PMCC (Poor Man's Covered Call)** — Buying a deep-ITM LEAPS call as a stock substitute and selling short-dated OTM calls against it. Lower capital requirement than a true covered call. See [[PMCC]] and [[PMCC-Income]].

**Put** — A contract giving the buyer the right, but not the obligation, to sell the underlying at the strike price on or before expiration.

**Ratio Spread** — A spread where more options are sold than bought, generating additional credit but introducing uncapped risk on one side.

**Rho** — The rate of change of an option's price per 1% change in risk-free interest rates. Generally small for short-dated options; more relevant for LEAPS.

**Roll** — Closing an existing option position and reopening it at a different strike or expiration to extend duration, collect additional credit, or move the position away from the current price. See [[Rolling-Basics]].

**Spread Width** — The distance in dollars between the two strikes in a vertical spread. Determines maximum risk and maximum reward for defined-risk spreads.

**Stop-Loss** — A predetermined exit trigger based on position loss (e.g., 2× credit received) used to cap drawdowns before expiration. See [[Stop-Loss-Strategies]].

**Straddle** — Buying (or selling) both a call and a put at the same strike and expiration. Long straddles profit from large moves; short straddles profit from the underlying staying near the strike.

**Strangle** — Buying (or selling) an OTM call and an OTM put at different strikes with the same expiration. Lower premium than a straddle; wider breakevens. See [[Earnings-Straddle-Strangle]].

**Strike Price** — The fixed price at which an option contract can be exercised. Also called the exercise price.

**Superfly** — A leveraged butterfly variant using wider wing ratios or extra legs for a higher potential payout at a specific price target; common in 0DTE SPX trading. See [[Superfly]].

**Theta** — The rate at which an option loses value per day due to the passage of time (time decay). Theta is negative for option buyers and positive for option sellers. Decay accelerates as DTE approaches zero.

**Theta Decay** — The erosion of an option's extrinsic value as time passes, all else equal. The primary profit driver for premium-selling strategies.

**Undefined Risk** — A position where the maximum loss is theoretically unlimited or very large (e.g., short naked calls, short strangles without hedging legs).

**Vega** — The rate of change of an option's price per 1-point (1%) change in implied volatility. Long vega positions profit when IV rises; short vega positions profit when IV falls.

**Vega-Positive** — A position that benefits when implied volatility increases. Long straddles, strangles, and calendars are vega-positive.

**Vertical Spread** — A two-leg spread at the same expiration but different strikes. Can be a credit spread (net premium received) or debit spread (net premium paid).

**Volume** — The number of option contracts traded on a given day. High volume confirms liquidity; low volume may signal difficulty entering or exiting at fair prices.

**Wheel Strategy** — A systematic cycle: sell a CSP until assigned stock, then sell covered calls until the stock is called away, then repeat. See [[Wheel-Strategy]].
