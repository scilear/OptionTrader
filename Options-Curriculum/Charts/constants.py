"""
Options-Curriculum Chart Constants
===================================
Shared constants for all chart generation scripts. Import with:
    from constants import COLORS, FIG_STANDARD, FIG_WIDE, FIG_SQUARE, SPX_SPOT, DPI
All chart scripts must use these values for styling and example parameters.
Canonical example values match Options-Curriculum/00-Index/Canon-Examples.md.
"""

# ── Color palette ─────────────────────────────────────────────────────────────
COLORS = {
    "profit":    "#4CAF50",   # green  — profit zones, positive P&L
    "loss":      "#F44336",   # red    — loss zones, negative P&L
    "neutral":   "#9E9E9E",   # gray   — breakeven lines, reference
    "primary":   "#2196F3",   # blue   — main P&L curve, primary series
    "highlight": "#FF9800",   # orange — annotations, secondary series
    "warning":   "#FFC107",   # amber  — warning zones, danger areas
    "bg":        "#FAFAFA",   # near-white background
}

# ── Figure sizes (width, height) in inches ───────────────────────────────────
FIG_STANDARD = (10, 6)
FIG_WIDE     = (14, 6)
FIG_SQUARE   = (8, 8)
FIG_TALL     = (8, 10)

# ── Font settings ─────────────────────────────────────────────────────────────
FONT_FAMILY  = "DejaVu Sans"
TITLE_SIZE   = 14
LABEL_SIZE   = 11
TICK_SIZE    = 9
ANNOT_SIZE   = 9
LEGEND_SIZE  = 10

# ── Line styles ───────────────────────────────────────────────────────────────
MAIN_LW      = 2.5   # main P&L curve
REF_LW       = 1.5   # reference / breakeven lines (use linestyle="--")
FILL_ALPHA   = 0.15  # alpha for profit/loss fill regions

# ── Output settings ───────────────────────────────────────────────────────────
DPI          = 150   # PNG resolution for Obsidian embedding
BBOX_INCHES  = "tight"

# ── Canonical example parameters (from Canon-Examples.md) ────────────────────
SPX_SPOT     = 5000
SPY_SPOT     = 500
AAPL_SPOT    = 200
MSFT_SPOT    = 400
NVDA_SPOT    = 900
GLD_SPOT     = 200
QQQ_SPOT     = 430

RISK_FREE    = 0.05   # 5% annualised
IV_CALM      = 0.13   # VIX ~13
IV_NORMAL    = 0.18   # VIX ~18
IV_ELEVATED  = 0.25   # VIX ~25
IV_STRESSED  = 0.35   # VIX ~35

# Standard IC on SPX (45 DTE, $50-wide wings)
IC_PUT_SHORT  = 4850
IC_PUT_LONG   = 4800
IC_CALL_SHORT = 5150
IC_CALL_LONG  = 5200
IC_CREDIT     = 12.50  # per-spread credit received
IC_WIDTH      = 50     # wing width in points
IC_DTE        = 45

# ── Matplotlib style helper (call at top of each script) ─────────────────────
def apply_style(ax, title: str, xlabel: str, ylabel: str) -> None:
    """Apply standard curriculum style to a matplotlib Axes object."""
    ax.set_title(title, fontsize=TITLE_SIZE, fontfamily=FONT_FAMILY, pad=12)
    ax.set_xlabel(xlabel, fontsize=LABEL_SIZE, fontfamily=FONT_FAMILY)
    ax.set_ylabel(ylabel, fontsize=LABEL_SIZE, fontfamily=FONT_FAMILY)
    ax.tick_params(labelsize=TICK_SIZE)
    ax.set_facecolor(COLORS["bg"])
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
