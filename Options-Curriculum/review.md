# Options Curriculum Review

> **Scope:** Complete review of the `Options-Curriculum` Obsidian vault.
> **Date:** Mon Jun 01 2026
> **Reviewer:** AI Agent

This review covers the curriculum's accuracy, structure, consistency, and offers improvement suggestions. It focuses on both the build infrastructure (`TASKBOARD.md`) and the final educational content within the vault.

---

## 1. Issues and Inaccuracies

### 1.1. Factual Inaccuracies in Prompts (TASKBOARD.md)

While the prompts are instructions for generating content, they contain several factual inaccuracies that will propagate into the final notes if not corrected.

| ID | Issue | Location (TASK) | Details |
|----|-------|-----------------|---------|
| **I-001** | **European/American Exercise Definition** | **062** (SPX vs QQQ) | The prompt states SPX is European-style and QQQ is American-style. While true, it fails to mention that **SPXW (weekly) is also European-style**, which is the primary vehicle for 0DTE trading. QQQ has no European-style equivalent, making the "avoid QQQ" logic for 0DTE slightly flawed or at least incomplete. |
| **I-002** | **0DTE Credit Spread Credit Target** | **064** (0DTE Credit Spread) | A credit target of 20-25% of spread width for 0DTE on SPX is highly optimistic for typical intraday options. 10-15% is a more realistic and achievable target for high-probability, short-duration trades. The prompt sets an unrealistic expectation. |
| **I-003** | **0DTE Iron Condor Credit Example** | **065** (0DTE Iron Condor) | The example describes an IC with $25 wide wings and $8 credit. This is a 32% credit rate. The prompt states the target is 15-25%. The example contradicts its own instructions, potentially confusing the AI or the learner regarding what a realistic 0DTE credit rate is. |
| **I-004** | **Superfly "Gamma Explosion" Misnomer** | **067** (Superfly) | The prompt describes gamma explosion, but a Superfly is a butterfly variant. It profits from the stock *pinning* near the center strike, benefiting from theta decay, not necessarily gamma. Gamma benefits are more relevant for hedging or directional plays near expiration, not a pin strategy. The prompt conflates gamma and theta. |
| **I-005** | **LEAPS Tax Treatment** | **076** (LEAPS Investing) | States LEAPS held > 1 year qualify for long-term capital gains "if structured as long options." This is dangerously vague. Writing calls against LEAPS (PMCC) creates a "straddle" or "constructive sale" risk under IRS rules, which can disqualify the long-term holding period. The prompt should explicitly mention this risk. |
| **I-006** | **Max Risk per Trade Table** | **048** (Prompt) | The table lists `0DTE IC` at 0.5-1%. Standard portfolio risk per trade is typically 1-2% of total capital. For a defined-risk strategy like an IC, 1-2% is more standard. 0.5% is extremely conservative and may be impractical for active traders. The prompt does not explain the rationale for such a low number. |

### 1.2. Inconsistencies Across the Curriculum

Reviewing the generated notes reveals several inconsistencies that suggest a lack of a rigorous internal style guide or fact-checking layer.

| ID | Issue | Location | Details |
|----|-------|----------|---------|
| **C-001** | **Duplicate Note on Calendar Spreads** | `04-Strategies/` | There is `04-Strategies/Calendar-Spreads.md` AND `04-Strategies/Income/Calendar-Spread.md`. The first is a standalone note, the second is part of the `Income` sub-folder. They appear to cover the same topic. One should be a redirect (`MOC`) to the other, or the content should be consolidated to prevent divergence. |
| **C-002** | **Gamma Walls vs. Gamma Scalping** | `02-Finding-Opportunities/Gamma-Walls-Call-Put.md` | This is an extremely advanced topic (dealer hedging, gamma exposure from market makers) placed in the "Finding Opportunities" module, which is typically for beginners. This creates a cognitive mismatch. Either move it to `05-Market-Conditions/` or `08-Adjustments/`, or add a strong prerequisite warning. |
| **C-003** | **Conflicting Risk Management Advice** | `06-Risk-Management/` | `Position-Sizing.md` suggests a 2-5% max loss per trade. `Max-Risk-Per-Trade.md` has a table with `0DTE IC` at 0.5-1%. While not strictly contradictory (one is a guideline, the other a specific table), it creates confusion for the learner about which rule to follow. |
| **C-004** | **Chart-to-Note Mapping Conflicts** | `Charts/` | The chart reference registry is not strictly enforced. For example, `pnl-pmcc.png` is listed as being embedded in `PMCC.md`, but `PMCC.md` also references `chart-leaps-vs-stock.png`, which is mapped to `LEAPS.md` and `LEAPS-Investing.md`. There are no technical errors here, but it highlights a risk of broken links or missing visuals if the script `pnl_diagrams.py` is not run perfectly in sync with the note generation. |

### 1.3. Structural and Pedagogical Weaknesses

| ID | Issue | Location | Details |
|----|-------|----------|---------|
| **S-001** | **Lack of a Master "Strategy Selection Matrix"** | N/A | While `Fly-vs-IC.md` exists, there is no single, unified table that compares ALL strategies (CSP, CC, Wheel, IC, Fly, Calendar, Diagonal, 0DTE) on key dimensions like: Capital Required, Ideal IV, Ideal Market Condition, Max Risk, and Time Commitment. This is the most critical missing piece for a beginner learner. |
| **S-002** | **Missing "How to Use This" Note** | `00-Index/` | The `Home.md` is a navigation hub, but there is no note explaining *how* to consume the material. E.g., "Read 01-Foundations first, then choose a strategy module." This leaves the learner without a clear path. |
| **S-003** | **Missing "Prerequisites" Checklist** | `00-Index/` | There is no checklist for the learner to confirm they have a brokerage account, understand basic stock market mechanics, etc., before starting the options-specific content. |
| **S-004** | **"Inaccurate Descriptions" in Example Trades** | `04-Strategies/` | The example trades (e.g., SPX at 5000, $50-wide IC) are fantastic for clarity, but they are static. If the curriculum is meant to be dynamic (e.g., updated with current market prices), these will date quickly. The prompt should specify that these are *illustrative* and not to be used for live trading without checking current prices. |
| **S-005** | **No "Common Beginner Mistakes" in Strategy Notes** | `04-Strategies/` / `00-Index/` | While `Common-Mistakes.md` (TASK-096) is planned, the individual strategy notes do not consistently highlight the most common pitfall for that specific strategy. For example, `CSP-Cash-Secured-Put.md` should have a dedicated callout for "Don't wheel meme stocks." |

---

## 2. Structure Analysis

### 2.1. Strengths

The curriculum architecture is exceptionally well-designed.

| Strength | Description |
|----------|-------------|
| **Atomic Note Philosophy** | The 400-700 word target per note, enforced by the global prompt, is pedagogically sound. It prevents cognitive overload and makes the vault highly navigable. |
| **Phased Build Order with Dependencies** | The 6-phase build order with explicit `Critical Sequential Chains` (e.g., IV concepts, Ticker funnel) is a masterclass in curriculum design. It prevents logical gaps and ensures prerequisite knowledge is built before complex topics are introduced. |
| **Complexity Tiering** | Mapping content to `Haiku`, `Sonnet`, and `Opus` provides a clear control for generation quality. Simple definitions use a simpler model, complex strategies use a more capable one. This is an efficient use of resources. |
| **Separation of Concerns** | Infrastructure (`Templates`, `Charts`, `Scripts`), Content (`01` through `09`), and Meta (`00-Index`, `Glossary`) are cleanly separated. This makes the repository maintainable. |
| **Chart Generation Pipeline** | The `Charts/` folder with `constants.py` and distinct scripts for different chart types ensures visual consistency and prevents code duplication. |
| **Validator Script (TASK-090)** | Including `validate_vault.py` to check for broken links, missing frontmatter, and missing chart embeds is a critical quality gate. It automates what would otherwise be a manual and error-prone process. |
| **Task Registry with Progress Tracker** | The `TASKBOARD.md` is not just a list of instructions; it is a living document with a progress tracker. This makes the build process transparent and manageable. |
| **Global Prompt Prefix** | Enforcing YAML frontmatter, specific callout types (`[!warning]`, `[!danger]`, `[!tip]`, `[!note]`), and `[[WikiLinks]]` across all notes guarantees a uniform look and feel. |

### 2.2. Weaknesses and Gaps

| Weakness | Description | Impact |
|----------|-------------|--------|
| **No "Strategy Cheat Sheet"** | There is no single-page, printable summary of all strategies, their setups, and key rules. For a learner, this is often the most valuable reference tool. | Learners must navigate multiple notes to get a high-level overview, reducing efficiency for quick lookups during trading. |
| **No Assessment or Quizzes** | There are no "Test Your Knowledge" sections or review questions at the end of modules. | Passive reading is less effective than active recall. The curriculum lacks a mechanism for the learner to self-assess their understanding. |
| **"Meta" Notes are Underutilized** | `TASK-086` (WikiLink Map) and `TASK-087` (Canon Examples) are described as "meta" and not student-facing. However, a learner-facing version of the Canon Examples would be incredibly useful for understanding the assumptions behind the example trades. | The learner is not given insight into the "rules" of the curriculum's universe (e.g., "We always use SPX at 5000"), which can be confusing. |
| **Risk of Content Rot** | The example trades use static numbers (e.g., AAPL at $200). If the curriculum is not updated, these will become dated. | The curriculum will eventually feel stale or irrelevant if the examples do not reflect current market realities, though the underlying principles remain sound. |
| **Lack of "Why Options?" Context** | The curriculum dives straight into options without explaining why options are superior/inferior to other instruments (stocks, futures, ETFs) for specific goals. | A learner might not understand *when* to apply options vs. other financial tools. |

---

## 3. Improvement Suggestions

### 3.1. High Priority (Must-Haves)

| # | Suggestion | Rationale |
|---|------------|-----------|
| **H-001** | **Create a Master "Strategy Selection Guide"** | A single note or printable PDF table comparing all strategies on: Capital Required, Ideal Market Condition, Ideal IV, Time Commitment, Max Risk, and Win Rate. This is the #1 missing piece for a beginner. |
| **H-002** | **Add "How to Use This Curriculum" Note** | A learner-facing guide in `00-Index/` explaining the reading order, how to track progress (checkboxes in Obsidian), and how to use the MOCs (Map of Contents) and Glossary. |
| **H-003** | **Reconcile Duplicate Content** | Either delete `04-Strategies/Calendar-Spreads.md` and make it a redirect to `04-Strategies/Income/Calendar-Spread.md`, or vice versa. Ensure all `related` links point to the canonical version. |
| **H-004** | **Clarify the `200% Loss` Rule** | In all strategy notes involving credit spreads, explicitly define "200% loss" as `2 * Net Credit Received` and provide a concrete example (e.g., "If you collected $1.00 in credit, close the trade if it costs $3.00 to buy back"). This is the #1 source of confusion for beginners. |
| **H-005** | **Add a "Prerequisites Checklist"** | A note in `00-Index/` with checkboxes for: "I have a brokerage account with options approval," "I understand basic stock market mechanics," "I know what a bid/ask spread is." This sets a clear entry barrier and reduces support questions. |

### 3.2. Medium Priority (Should-Haves)

| # | Suggestion | Rationale |
|---|------------|-----------|
| **M-001** | **Add "Test Your Knowledge" to Every Module** | At the end of each module (e.g., `01-Foundations/`), add a note with 3-5 review questions. E.g., "Q: What is the ideal DTE for a bull put spread? A: 21-45 days." This uses active recall to reinforce learning. |
| **M-002** | **Add "Common Pitfalls" to Every Strategy Note** | Each strategy note (e.g., `CSP-Cash-Secured-Put.md`) should have a dedicated "Common Beginner Mistakes" callout. E.g., for CSP: "Mistake: Wheeling a meme stock. Fix: Only wheel high-quality tickers (AAPL, MSFT, SPY)." |
| **M-003** | **Create a "Strategy Cheat Sheet"** | A single-page, downloadable/printable PDF table summarizing all strategies, their entry criteria, and key management rules. This is the most valuable tool a beginner can have at their desk. |
| **M-004** | **Add "Key Takeaways" to the Global Prompt** | Modify the global prompt to require a `> [!tip]` callout at the end of every note summarizing the 3-4 most important points. This acts as a "TL;DR" for quick review. |
| **M-005** | **Clarify Example Trade Disclaimer** | In the `Canon-Examples.md` (TASK-087) and in every note using examples, add a bolded disclaimer: **"All example prices are illustrative and current as of the curriculum's creation. Always verify live prices before trading."** |
| **M-006** | **Move `Gamma-Walls-Call-Put.md`** | Move this extremely advanced note to `05-Market-Conditions/` or `08-Adjustments/`. It is highly confusing to place dealer hedging mechanics in the "Finding Opportunities" module aimed at beginners. |

### 3.3. Low Priority (Nice-to-Haves)

| # | Suggestion | Rationale |
|---|------------|-----------|
| **L-001** | **Add Historical Case Studies** | A note on past market events (e.g., 1987 Black Monday, March 2020, Jan 2025) and how specific options strategies performed or failed. This adds invaluable real-world context. |
| **L-002** | **Create a "VIX Deep Dive" Note** | VIX is referenced throughout, but there is no foundational note explaining what it is, how it is calculated, and its limitations. This is a gap in the `01-Foundations/` module. |
| **L-003** | **Add a "Paper Trading Journal" Template** | While `TASK-095` exists, having a pre-built Obsidian template with dropdowns for strategy, ticker, P&L, and emotional state would make the journaling process much more effective for learners. |
| **L-004** | **Add a "Tiered Edits" Process** | For a curriculum of this scale, a formal review process is needed: 1) AI Draft, 2) Technical Review (options expert), 3) Pedagogical Review (checks for clarity), 4) Final QA (links, formatting). Document this in `AGENTS.md`. |

---

## 4. Conclusion

This curriculum represents a remarkable achievement in both educational design and technical infrastructure. The phased build order, atomic note philosophy, and automated validation pipeline are of exceptionally high quality.

However, to reach its full potential, it requires a **rigorous fact-checking pass** to eliminate the minor inaccuracies present in the source prompts (e.g., unrealistic credit targets, tax ambiguities). It also needs a **unifying "Strategy Selection Guide"** and **prerequisite checklists** to guide the learner effectively.

The most impactful next steps are:
1.  Fix the factual inaccuracies in the source prompts (`TASKBOARD.md`) to prevent them from propagating.
2.  Create a single, comprehensive "Strategy Selection Matrix" note.
3.  Add a "How to Use This" and "Prerequisites" note to `00-Index/`.
4.  Perform a consistency pass to remove duplicate notes and conflicting advice.

With these corrections, this curriculum will be a world-class resource for options education.