---
title: US Tax Treatment of Options Trades
tags:
  - tax
  - options
  - capital-gains
  - section-1256
  - wash-sale
  - record-keeping
aliases:
  - Options Tax
  - Tax Treatment of Options
status: draft
related:
  - "[[CSP-Cash-Secured-Put]]"
  - "[[Covered-Call]]"
  - "[[LEAPS]]"
  - "[[Zero-Risk-Collar]]"
  - "[[Broker-Comparison]]"
---

# US Tax Treatment of Options Trades

> [!warning]
> This note is educational only and does not constitute tax advice. Tax law is complex and changes frequently. Consult a CPA or tax attorney for your specific situation before filing or making strategy decisions based on tax considerations.

---

## 1. Default Rule — Short-Term Capital Gains

Most equity options (calls and puts on individual stocks, ETFs such as [[Covered-Call|SPY or QQQ]]) are taxed under the **standard capital gains framework**:

- Held **under 12 months** → short-term capital gain or loss, taxed at **ordinary income rates** (up to 37% federal in 2024).
- Held **12 months or more** → long-term capital gain, taxed at preferential rates (0%, 15%, or 20% depending on income bracket).

Because most options expire in weeks or months, the vast majority of options trades produce **short-term gains**. This is the starting point; every rule below is an exception.

---

## 2. Section 1256 — The 60/40 Rule for Index Options

> [!note]
> Section 1256 of the Internal Revenue Code grants favorable tax treatment to certain exchange-traded contracts. This is one of the most important tax advantages available to index options traders and is data-backed by IRS Publication 550 and the text of the code itself.

Contracts that qualify under Section 1256 are taxed as **60% long-term / 40% short-term capital gains regardless of how long you held them** — even if you opened and closed a trade on the same day.

**Qualifying instruments** (rule of thumb: broad cash-settled indexes):
- SPX, XSP, NDX, RUT options
- Futures and futures options (e.g., /ES, /NQ, /MES)
- Certain currency contracts

**Do NOT qualify:**
- SPY and QQQ options (ETF shares, not indexes)
- Individual equity options (AAPL, TSLA, etc.)
- Any option on an ETF

At a 37% marginal rate, the blended effective rate on a Section 1256 gain is approximately **26.8%** versus 37% on a pure short-term gain — a meaningful edge for active index traders. Mark-to-market rules also apply: open Section 1256 positions are treated as sold on December 31 each year, and losses can be carried back up to three years.

---

## 3. LEAPS and the Qualified Covered Call Rules

[[LEAPS]] (options with expirations beyond one year) held for more than 12 months qualify for **long-term capital gains** treatment on sale or expiration.

> [!tip]
> Writing short-dated [[Covered-Call|covered calls]] against a LEAPS long can disqualify the LEAPS holding period under the **qualified covered call (QCC) rules** (IRC §1092). A call is "unqualified" if its strike is too deep in the money relative to the underlying. When that happens, the holding-period clock on the long LEAPS is suspended for the duration the unqualified call is open. Always verify the QCC strike threshold with a CPA before layering calls over a LEAPS position you intend to hold long-term.

---

## 4. Wash Sale Rule

The wash sale rule (IRC §1091) disallows a loss when you sell a security at a loss and buy a "substantially identical" security within **30 days before or after** the sale.

Key applications for options traders:

- Closing a losing option position and re-opening a similar option (same underlying, similar strike/expiry) within the 30-day window triggers a wash sale. The disallowed loss is added to the cost basis of the replacement position.
- Selling stock at a loss **and selling a put** on the same stock may constitute a wash sale (the put obligates you to buy shares — the IRS can treat this as acquiring substantially identical property).
- [[Zero-Risk-Collar|Collars]] and similar hedging structures deserve careful review.

> [!warning]
> Wash sale tracking across options is notoriously difficult. Some brokers (see [[Broker-Comparison]]) report wash sale adjustments on 1099-B; others do not catch all option-to-option cases. Manual verification is the trader's responsibility.

---

## 5. Assignment Tax Treatment

When an option is exercised or assigned, the premium is folded into the cost basis or proceeds of the stock transaction — it is not a separate taxable event at assignment.

| Scenario | Tax treatment |
|---|---|
| [[CSP-Cash-Secured-Put]] assigned (you buy stock) | Cost basis = **strike price − premium received** |
| [[Covered-Call]] assigned (you sell stock) | Proceeds = **strike price + premium received** |
| Long call exercised (you buy stock) | Cost basis = **strike price + premium paid** |
| Long put exercised (you sell stock) | Proceeds = **strike price − premium paid** |

The holding period of the resulting stock position begins on the **assignment date**, not the option open date. This matters for determining short- vs. long-term treatment on the stock eventually sold.

---

## 6. Record Keeping for Schedule D

For every options trade, capture:

1. **Ticker and description** (underlying, option type, strike, expiry)
2. **Open date and close/expiry/assignment date**
3. **Number of contracts**
4. **Premium paid or received** (per-contract and total)
5. **Commissions and fees** (reduce gain or increase loss)
6. **Outcome**: closed, expired worthless, assigned, or exercised
7. **Section 1256 flag** if applicable
8. **Wash sale adjustments** if a loss was disallowed

Most brokers provide a **1099-B** by mid-February. Cross-reference it against your own trade log — broker 1099s frequently contain errors on options, particularly for multi-leg spreads, assignments, and wash sales. See [[Broker-Comparison]] for notes on which brokers produce cleaner tax reporting.

> [!tip]
> Export your trade history to a spreadsheet at year-end. Software such as TradeLog or GainsKeeper can reconcile broker data and apply wash sale rules across accounts — worth the cost for active traders with dozens of positions.

---

*Related: [[CSP-Cash-Secured-Put]] · [[Covered-Call]] · [[LEAPS]] · [[Zero-Risk-Collar]] · [[Broker-Comparison]]*
