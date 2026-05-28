---
title: Charts — README
status: reference
---

# Charts

This folder contains Python scripts that generate charts embedded in Obsidian notes.

---

## Prerequisites

```bash
pip install plotly matplotlib numpy pandas
```

---

## How to Run Each Script

Run any script from this directory. All output files are written to `Charts/outputs/`.

```bash
cd Charts/

python pnl_diagrams.py
python iv_charts.py
python timing_charts.py
python risk_charts.py
python earnings_charts.py
```

To regenerate all charts at once:

```bash
for script in pnl_diagrams.py iv_charts.py timing_charts.py risk_charts.py earnings_charts.py; do
    python "$script"
done
```

---

## Naming Convention

Output files use **lowercase-hyphenated** names:

- Prefix indicates chart type: `pnl-`, `chart-`
- Words separated by hyphens, no spaces or underscores
- Extension reflects format: `.png` for static, `.html` for interactive

Examples: `pnl-iron-condor.png`, `chart-iv-rank-gauge.png`, `chart-term-structure.html`

---

## Embedding Charts in Obsidian Notes

**Static PNG** (most charts):

```
![[pnl-iron-condor.png]]
```

**Interactive HTML** (Plotly charts with hover/zoom):

```
![[chart-term-structure.html]]
```

Obsidian resolves these links against the vault's attachment search paths. Keep all output files in `Charts/outputs/` and ensure that folder is included in Obsidian's **Files & Links > Attachment folder path** or that the vault is configured to search all subfolders.

---

## Script Inventory

| Script | Charts Generated | Output Format | Consuming Notes |
|---|---|---|---|
| `pnl_diagrams.py` | pnl-csp, pnl-covered-call, pnl-iron-condor, pnl-iron-butterfly, pnl-vertical-spread, pnl-pmcc, pnl-leaps-vs-stock, pnl-fly-vs-ic-comparison, pnl-diagonal-spread | PNG | Cash-Secured Put, Covered Call, Iron Condor, Iron Butterfly, Vertical Spread, PMCC, LEAPS, Fly vs IC, Diagonal Spread notes |
| `iv_charts.py` | chart-iv-rank-gauge, chart-iv-percentile-vs-rank, chart-iv-vs-hv, chart-term-structure, chart-iv-crush, chart-greeks-sensitivity, chart-iv-compression-coil | PNG | IV Rank, IV Percentile, IV vs HV, Term Structure, IV Crush, Greeks notes |
| `timing_charts.py` | chart-intraday-profile, chart-day-of-week-winrate, chart-dte-theta, chart-earnings-move-vs-actual | PNG | Intraday Timing, Day-of-Week Edge, Theta Decay, Earnings notes |
| `risk_charts.py` | chart-position-sizing, chart-drawdown-sim, chart-portfolio-heat | PNG | Position Sizing, Drawdown Management, Portfolio Heat notes |
| `earnings_charts.py` | chart-earnings-move-history, chart-straddle-vs-ic, chart-earnings-ic-example | PNG | Earnings Strategies, Straddle vs IC, Earnings IC notes |

---

## Utility Scripts

These scripts are not chart generators but support the vault build process.

| Script | Purpose |
|---|---|
| `constants.py` | Shared color palette, figure sizes, and example prices. Import this in every chart script for visual consistency. |
| `scaffold_vault.py` | Creates the vault folder structure and stub note files. Run once to initialize a new vault. |
| `validate_vault.py` | Checks WikiLink resolution, frontmatter completeness, and chart embed validity across all notes. |
| `extract_prompts.py` | Extracts task prompts from `TASKBOARD.md` for use in automated or batch workflows. |
