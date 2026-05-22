"""
pnl_diagrams.py
===============
Generate P&L-at-expiry diagrams for all major options strategies.

Each strategy function:
  - Computes the payoff array over a price grid (per-share, no 100x multiplier)
  - Saves a static PNG (for Obsidian embedding) via matplotlib
  - Saves an interactive HTML via plotly

Run:
    python Charts/pnl_diagrams.py

Outputs land in Charts/outputs/ (created if absent).

Import note: `constants.py` must be on sys.path.  The script adds its own
directory to sys.path so it can be run from any working directory.
"""

from __future__ import annotations

import sys
from pathlib import Path

# ── Make `from constants import …` work regardless of cwd ────────────────────
_HERE = Path(__file__).parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

import matplotlib
matplotlib.use("Agg")  # non-interactive backend — must precede pyplot import

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import plotly.graph_objects as go

from constants import (
    COLORS,
    FIG_STANDARD,
    FIG_WIDE,
    SPX_SPOT,
    AAPL_SPOT,
    DPI,
    apply_style,
    MAIN_LW,
    REF_LW,
    FILL_ALPHA,
    TITLE_SIZE,
    LABEL_SIZE,
    TICK_SIZE,
    LEGEND_SIZE,
)

# ── Shared helpers ─────────────────────────────────────────────────────────────

XLABEL = "Underlying Price at Expiry ($)"
YLABEL = "P&L per Share ($)"


def _price_grid(center: float, pct: float = 0.12, n: int = 500) -> np.ndarray:
    """Return a fine price grid ±pct around center."""
    lo = center * (1 - pct)
    hi = center * (1 + pct)
    return np.linspace(lo, hi, n)


def _fill_pnl(ax: plt.Axes, prices: np.ndarray, pnl: np.ndarray) -> None:
    """Fill profit zone green, loss zone red."""
    ax.fill_between(prices, pnl, 0, where=pnl >= 0,
                    color=COLORS["profit"], alpha=FILL_ALPHA, label="_nolegend_")
    ax.fill_between(prices, pnl, 0, where=pnl < 0,
                    color=COLORS["loss"], alpha=FILL_ALPHA, label="_nolegend_")


def _hline(ax: plt.Axes, y: float, color: str, label: str,
           linestyle: str = "--", lw: float = REF_LW) -> None:
    ax.axhline(y, color=color, linestyle=linestyle, linewidth=lw, label=label)


def _vline(ax: plt.Axes, x: float, color: str, label: str,
           linestyle: str = "--", lw: float = REF_LW) -> None:
    ax.axvline(x, color=color, linestyle=linestyle, linewidth=lw, label=label)


def _save_matplotlib(fig: plt.Figure, save_dir: Path, name: str) -> None:
    fig.savefig(save_dir / name, dpi=DPI, bbox_inches="tight")
    plt.close(fig)


def _plotly_from_mpl(
    prices: np.ndarray,
    pnl: np.ndarray,
    title: str,
    breakevens: list[float],
    max_profit: float | None = None,
    max_loss: float | None = None,
    extra_traces: list[dict] | None = None,
) -> go.Figure:
    """
    Build a plotly Figure from price/pnl arrays with standard annotations.
    extra_traces: list of dicts with keys 'prices', 'pnl', 'name', 'color'
    """
    fig = go.Figure()

    # Profit fill (positive)
    pos_mask = pnl >= 0
    fig.add_trace(go.Scatter(
        x=np.concatenate([prices[pos_mask], prices[pos_mask][::-1]]),
        y=np.concatenate([pnl[pos_mask], np.zeros(pos_mask.sum())]),
        fill="toself",
        fillcolor=f"rgba(76, 175, 80, {FILL_ALPHA})",
        line=dict(width=0),
        showlegend=False,
        hoverinfo="skip",
    ))
    # Loss fill (negative)
    neg_mask = pnl < 0
    fig.add_trace(go.Scatter(
        x=np.concatenate([prices[neg_mask], prices[neg_mask][::-1]]),
        y=np.concatenate([pnl[neg_mask], np.zeros(neg_mask.sum())]),
        fill="toself",
        fillcolor=f"rgba(244, 67, 54, {FILL_ALPHA})",
        line=dict(width=0),
        showlegend=False,
        hoverinfo="skip",
    ))

    # Main P&L curve
    fig.add_trace(go.Scatter(
        x=prices, y=pnl,
        mode="lines",
        name="P&L",
        line=dict(color=COLORS["primary"], width=MAIN_LW),
    ))

    # Extra overlay curves
    if extra_traces:
        for tr in extra_traces:
            fig.add_trace(go.Scatter(
                x=tr["prices"], y=tr["pnl"],
                mode="lines",
                name=tr["name"],
                line=dict(color=tr.get("color", COLORS["highlight"]),
                          width=MAIN_LW, dash="dot"),
            ))

    # Zero line
    fig.add_hline(y=0, line=dict(color=COLORS["neutral"], dash="dash", width=REF_LW))

    # Breakeven verticals
    for be in breakevens:
        fig.add_vline(x=be, line=dict(color=COLORS["neutral"], dash="dash", width=REF_LW),
                      annotation_text=f"BE {be:,.0f}", annotation_position="top left")

    # Max profit / max loss horizontals
    if max_profit is not None:
        fig.add_hline(y=max_profit,
                      line=dict(color=COLORS["profit"], dash="dash", width=REF_LW),
                      annotation_text=f"Max profit {max_profit:+.2f}",
                      annotation_position="right")
    if max_loss is not None:
        fig.add_hline(y=max_loss,
                      line=dict(color=COLORS["loss"], dash="dash", width=REF_LW),
                      annotation_text=f"Max loss {max_loss:+.2f}",
                      annotation_position="right")

    fig.update_layout(
        title=dict(text=title, font=dict(size=TITLE_SIZE)),
        xaxis_title=XLABEL,
        yaxis_title=YLABEL,
        plot_bgcolor=COLORS["bg"],
        paper_bgcolor="white",
        legend=dict(font=dict(size=LEGEND_SIZE)),
        width=900, height=500,
    )
    return fig


def _save_plotly(pfig: go.Figure, save_dir: Path, png_name: str) -> None:
    html_name = png_name.replace(".png", ".html")
    pfig.write_html(save_dir / html_name)


# ── 1. Cash-Secured Put (CSP) ─────────────────────────────────────────────────

def plot_csp(save_dir: Path) -> None:
    """
    Short put P&L at expiry.

    Payoff = premium - max(strike - S, 0)
      - Max profit = premium (when S >= strike)
      - Max loss   = strike - premium (when S = 0)
      - Breakeven  = strike - premium

    Parameters: spot=5000, strike=4850, premium=15
    """
    strike, premium = 4850, 15.0
    prices = _price_grid(SPX_SPOT)
    pnl = premium - np.maximum(strike - prices, 0)
    be = strike - premium          # 4835
    max_profit = premium           # 15
    max_loss = -(strike - premium) # -4835 (theoretical, S→0)

    fig, ax = plt.subplots(figsize=FIG_STANDARD)
    _fill_pnl(ax, prices, pnl)
    ax.plot(prices, pnl, color=COLORS["primary"], linewidth=MAIN_LW, label="CSP P&L")
    _hline(ax, 0, COLORS["neutral"], "Zero", "-")
    _hline(ax, max_profit, COLORS["profit"], f"Max profit ${max_profit:.0f}")
    _vline(ax, be, COLORS["neutral"], f"BE ${be:,.0f}")
    _vline(ax, strike, COLORS["loss"], f"Strike ${strike:,}", ":")
    apply_style(ax, "Cash-Secured Put (Short Put)", XLABEL, YLABEL)
    ax.legend(fontsize=LEGEND_SIZE)
    _save_matplotlib(fig, save_dir, "pnl-csp.png")

    pfig = _plotly_from_mpl(prices, pnl, "Cash-Secured Put (Short Put)",
                            breakevens=[be], max_profit=max_profit, max_loss=None)
    _save_plotly(pfig, save_dir, "pnl-csp.png")


# ── 2. Covered Call ────────────────────────────────────────────────────────────

def plot_covered_call(save_dir: Path) -> None:
    """
    Long stock + short call P&L at expiry.

    Payoff = (S - spot_cost) - max(S - strike, 0) + premium
           = premium + min(S, strike) - spot_cost
      - Max profit = strike - spot_cost + premium  (when S >= strike, stock capped)
      - Breakeven  = spot_cost - premium
      - Max loss   = -(spot_cost - premium)  (when S = 0)

    Simplification: assume stock purchased at SPX_SPOT (5000).
    Strike=5100, premium=12.
    """
    spot_cost = SPX_SPOT   # 5000 — cost basis for stock
    strike, premium = 5100, 12.0
    prices = _price_grid(SPX_SPOT)
    stock_pnl = prices - spot_cost
    short_call = premium - np.maximum(prices - strike, 0)
    pnl = stock_pnl + short_call

    be = spot_cost - premium                    # 4988
    max_profit = strike - spot_cost + premium   # 112

    fig, ax = plt.subplots(figsize=FIG_STANDARD)
    _fill_pnl(ax, prices, pnl)
    ax.plot(prices, pnl, color=COLORS["primary"], linewidth=MAIN_LW, label="Covered Call P&L")
    _hline(ax, 0, COLORS["neutral"], "Zero", "-")
    _hline(ax, max_profit, COLORS["profit"], f"Max profit ${max_profit:.0f}")
    _vline(ax, be, COLORS["neutral"], f"BE ${be:,.0f}")
    _vline(ax, strike, COLORS["highlight"], f"Strike ${strike:,}", ":")
    apply_style(ax, "Covered Call (Long Stock + Short Call)", XLABEL, YLABEL)
    ax.legend(fontsize=LEGEND_SIZE)
    _save_matplotlib(fig, save_dir, "pnl-covered-call.png")

    pfig = _plotly_from_mpl(prices, pnl, "Covered Call (Long Stock + Short Call)",
                            breakevens=[be], max_profit=max_profit)
    _save_plotly(pfig, save_dir, "pnl-covered-call.png")


# ── 3. Wheel Cycle ────────────────────────────────────────────────────────────

def plot_wheel_cycle(save_dir: Path) -> None:
    """
    Simplified Wheel: two-panel diagram.

    Left panel: CSP phase — sell put at 4850, premium=$15.
      P&L = 15 - max(4850 - S, 0); assignment at S < 4850.

    Right panel: Covered Call phase — stock assigned at 4850,
      sell call at 5000, premium=$12.
      P&L (relative to assignment cost 4850) = (S - 4850) - max(S-5000,0) + 12.

    Breakeven (CSP phase) = 4835; Breakeven (CC phase) = 4838.
    """
    # CSP phase
    csp_strike, csp_prem = 4850, 15.0
    prices_csp = _price_grid(csp_strike, pct=0.06)
    pnl_csp = csp_prem - np.maximum(csp_strike - prices_csp, 0)

    # CC phase (cost basis = assignment price = 4850)
    cc_strike, cc_prem = 5000, 12.0
    assignment_price = csp_strike
    prices_cc = _price_grid(cc_strike, pct=0.06)
    pnl_cc = (prices_cc - assignment_price) - np.maximum(prices_cc - cc_strike, 0) + cc_prem

    fig, axes = plt.subplots(1, 2, figsize=FIG_WIDE)

    # Left: CSP
    ax = axes[0]
    be_csp = csp_strike - csp_prem
    _fill_pnl(ax, prices_csp, pnl_csp)
    ax.plot(prices_csp, pnl_csp, color=COLORS["primary"], linewidth=MAIN_LW)
    _hline(ax, 0, COLORS["neutral"], "Zero", "-")
    _hline(ax, csp_prem, COLORS["profit"], f"Max profit ${csp_prem:.0f}")
    _vline(ax, be_csp, COLORS["neutral"], f"BE ${be_csp:,.0f}")
    apply_style(ax, "Phase 1: Cash-Secured Put", XLABEL, YLABEL)
    ax.axvspan(ax.get_xlim()[0] if ax.get_xlim()[0] > 0 else prices_csp[0],
               csp_strike, alpha=0.05, color=COLORS["warning"], label="Assignment zone")
    ax.legend(fontsize=LEGEND_SIZE - 1)

    # Right: Covered Call
    ax = axes[1]
    be_cc = assignment_price - cc_prem
    max_profit_cc = cc_strike - assignment_price + cc_prem
    _fill_pnl(ax, prices_cc, pnl_cc)
    ax.plot(prices_cc, pnl_cc, color=COLORS["primary"], linewidth=MAIN_LW)
    _hline(ax, 0, COLORS["neutral"], "Zero", "-")
    _hline(ax, max_profit_cc, COLORS["profit"], f"Max profit ${max_profit_cc:.0f}")
    _vline(ax, be_cc, COLORS["neutral"], f"BE ${be_cc:,.0f}")
    apply_style(ax, "Phase 2: Covered Call (assigned @ 4850)", XLABEL, YLABEL)
    ax.legend(fontsize=LEGEND_SIZE - 1)

    fig.suptitle("The Wheel Strategy — Two Phases", fontsize=TITLE_SIZE + 1, y=1.01)
    fig.tight_layout()
    _save_matplotlib(fig, save_dir, "pnl-wheel-cycle.png")

    # Single HTML with both traces on one chart (approximate overlay)
    pfig = go.Figure()
    pfig.add_trace(go.Scatter(x=prices_csp, y=pnl_csp, name="CSP Phase",
                              line=dict(color=COLORS["primary"], width=MAIN_LW)))
    pfig.add_trace(go.Scatter(x=prices_cc, y=pnl_cc, name="CC Phase",
                              line=dict(color=COLORS["highlight"], width=MAIN_LW, dash="dot")))
    pfig.add_hline(y=0, line=dict(color=COLORS["neutral"], dash="dash", width=REF_LW))
    pfig.update_layout(
        title="The Wheel Strategy — CSP Phase vs Covered Call Phase",
        xaxis_title=XLABEL, yaxis_title=YLABEL,
        plot_bgcolor=COLORS["bg"], paper_bgcolor="white",
        width=900, height=500,
    )
    _save_plotly(pfig, save_dir, "pnl-wheel-cycle.png")


# ── 4. Bull Put Spread ────────────────────────────────────────────────────────

def plot_bull_put_spread(save_dir: Path) -> None:
    """
    Bull Put Spread: sell higher put, buy lower put.

    Payoff = credit - max(K_short - S, 0) + max(K_long - S, 0)
      credit = net premium received
      K_short = 4850 (sold), K_long = 4800 (bought)
      credit = 12.50

    Max profit = credit            (S >= K_short)
    Max loss   = -(width - credit) = -(50 - 12.50) = -37.50
    Breakeven  = K_short - credit  = 4837.50
    """
    k_short, k_long, credit = 4850, 4800, 12.50
    width = k_short - k_long
    prices = _price_grid(SPX_SPOT)
    pnl = credit - np.maximum(k_short - prices, 0) + np.maximum(k_long - prices, 0)
    be = k_short - credit
    max_profit = credit
    max_loss = -(width - credit)

    fig, ax = plt.subplots(figsize=FIG_STANDARD)
    _fill_pnl(ax, prices, pnl)
    ax.plot(prices, pnl, color=COLORS["primary"], linewidth=MAIN_LW, label="Bull Put Spread P&L")
    _hline(ax, 0, COLORS["neutral"], "Zero", "-")
    _hline(ax, max_profit, COLORS["profit"], f"Max profit ${max_profit:.2f}")
    _hline(ax, max_loss, COLORS["loss"], f"Max loss ${max_loss:.2f}")
    _vline(ax, be, COLORS["neutral"], f"BE ${be:,.2f}")
    _vline(ax, k_short, COLORS["highlight"], f"Short ${k_short:,}", ":")
    _vline(ax, k_long, COLORS["loss"], f"Long ${k_long:,}", ":")
    apply_style(ax, "Bull Put Spread (Sell 4850 / Buy 4800 Put)", XLABEL, YLABEL)
    ax.legend(fontsize=LEGEND_SIZE)
    _save_matplotlib(fig, save_dir, "pnl-bull-put-spread.png")

    pfig = _plotly_from_mpl(prices, pnl, "Bull Put Spread (Sell 4850 / Buy 4800 Put)",
                            breakevens=[be], max_profit=max_profit, max_loss=max_loss)
    _save_plotly(pfig, save_dir, "pnl-bull-put-spread.png")


# ── 5. Bear Call Spread ───────────────────────────────────────────────────────

def plot_bear_call_spread(save_dir: Path) -> None:
    """
    Bear Call Spread: sell lower call, buy higher call.

    Payoff = credit - max(S - K_short, 0) + max(S - K_long, 0)
      K_short = 5150 (sold), K_long = 5200 (bought)
      credit = 12.50

    Max profit = credit             (S <= K_short)
    Max loss   = -(width - credit)  = -(50 - 12.50) = -37.50
    Breakeven  = K_short + credit   = 5162.50
    """
    k_short, k_long, credit = 5150, 5200, 12.50
    width = k_long - k_short
    prices = _price_grid(SPX_SPOT)
    pnl = credit - np.maximum(prices - k_short, 0) + np.maximum(prices - k_long, 0)
    be = k_short + credit
    max_profit = credit
    max_loss = -(width - credit)

    fig, ax = plt.subplots(figsize=FIG_STANDARD)
    _fill_pnl(ax, prices, pnl)
    ax.plot(prices, pnl, color=COLORS["primary"], linewidth=MAIN_LW, label="Bear Call Spread P&L")
    _hline(ax, 0, COLORS["neutral"], "Zero", "-")
    _hline(ax, max_profit, COLORS["profit"], f"Max profit ${max_profit:.2f}")
    _hline(ax, max_loss, COLORS["loss"], f"Max loss ${max_loss:.2f}")
    _vline(ax, be, COLORS["neutral"], f"BE ${be:,.2f}")
    _vline(ax, k_short, COLORS["highlight"], f"Short ${k_short:,}", ":")
    _vline(ax, k_long, COLORS["loss"], f"Long ${k_long:,}", ":")
    apply_style(ax, "Bear Call Spread (Sell 5150 / Buy 5200 Call)", XLABEL, YLABEL)
    ax.legend(fontsize=LEGEND_SIZE)
    _save_matplotlib(fig, save_dir, "pnl-bear-call-spread.png")

    pfig = _plotly_from_mpl(prices, pnl, "Bear Call Spread (Sell 5150 / Buy 5200 Call)",
                            breakevens=[be], max_profit=max_profit, max_loss=max_loss)
    _save_plotly(pfig, save_dir, "pnl-bear-call-spread.png")


# ── 6. Iron Condor ────────────────────────────────────────────────────────────

def plot_iron_condor(save_dir: Path) -> None:
    """
    Iron Condor: bull put spread + bear call spread.

    Put spread: sell 4850, buy 4800 put.
    Call spread: sell 5150, buy 5200 call.
    Total credit = 12.50 (combined, per spec).

    Payoff = credit
             - max(K_ps - S, 0) + max(K_pl - S, 0)   [put spread]
             - max(S - K_cs, 0) + max(S - K_cl, 0)   [call spread]

    Max profit = credit              (4850 <= S <= 5150)
    Max loss   = -(50 - 12.50)      (-37.50) on either side (50-pt wings)
    Breakevens = K_ps - credit/2, K_cs + credit/2 (symmetrical, approximate)
      Exact: put BE = K_ps - credit = 4837.50; call BE = K_cs + credit = 5162.50
      (Here credit is the full IC credit, so each side's effective credit = full credit)
    """
    k_ps, k_pl = 4850, 4800     # put spread (short, long)
    k_cs, k_cl = 5150, 5200     # call spread (short, long)
    credit = 12.50
    width = 50

    prices = _price_grid(SPX_SPOT)
    put_spread = -np.maximum(k_ps - prices, 0) + np.maximum(k_pl - prices, 0)
    call_spread = -np.maximum(prices - k_cs, 0) + np.maximum(prices - k_cl, 0)
    pnl = credit + put_spread + call_spread

    be_lo = k_ps - credit
    be_hi = k_cs + credit
    max_profit = credit
    max_loss = -(width - credit)

    fig, ax = plt.subplots(figsize=FIG_STANDARD)
    _fill_pnl(ax, prices, pnl)
    ax.plot(prices, pnl, color=COLORS["primary"], linewidth=MAIN_LW, label="Iron Condor P&L")
    _hline(ax, 0, COLORS["neutral"], "Zero", "-")
    _hline(ax, max_profit, COLORS["profit"], f"Max profit ${max_profit:.2f}")
    _hline(ax, max_loss, COLORS["loss"], f"Max loss ${max_loss:.2f}")
    _vline(ax, be_lo, COLORS["neutral"], f"BE ${be_lo:,.2f}")
    _vline(ax, be_hi, COLORS["neutral"], f"BE ${be_hi:,.2f}")
    apply_style(ax, "Iron Condor (4800/4850 Put | 5150/5200 Call)", XLABEL, YLABEL)
    ax.legend(fontsize=LEGEND_SIZE)
    _save_matplotlib(fig, save_dir, "pnl-iron-condor.png")

    pfig = _plotly_from_mpl(prices, pnl, "Iron Condor (4800/4850 Put | 5150/5200 Call)",
                            breakevens=[be_lo, be_hi],
                            max_profit=max_profit, max_loss=max_loss)
    _save_plotly(pfig, save_dir, "pnl-iron-condor.png")


# ── 7. Iron Fly ───────────────────────────────────────────────────────────────

def plot_iron_fly(save_dir: Path) -> None:
    """
    Iron Butterfly: sell ATM straddle, buy OTM wings.

    Short straddle: sell 5000 put + sell 5000 call.
    Long wings: buy 4900 put, buy 5100 call.
    Total credit = 45.

    Payoff = credit
             - max(K_atm - S, 0) + max(K_pw - S, 0)   [put side]
             - max(S - K_atm, 0) + max(S - K_cw, 0)   [call side]

    Max profit = credit            (S = K_atm = 5000)
    Max loss   = -(wing_width - credit) = -(100 - 45) = -55
    Breakevens = K_atm ± credit = 4955, 5045
    """
    k_atm = 5000
    k_pw, k_cw = 4900, 5100    # long put wing, long call wing
    credit = 45.0
    wing_width = k_atm - k_pw  # 100

    prices = _price_grid(SPX_SPOT)
    put_side = -np.maximum(k_atm - prices, 0) + np.maximum(k_pw - prices, 0)
    call_side = -np.maximum(prices - k_atm, 0) + np.maximum(prices - k_cw, 0)
    pnl = credit + put_side + call_side

    be_lo = k_atm - credit
    be_hi = k_atm + credit
    max_profit = credit
    max_loss = -(wing_width - credit)

    fig, ax = plt.subplots(figsize=FIG_STANDARD)
    _fill_pnl(ax, prices, pnl)
    ax.plot(prices, pnl, color=COLORS["primary"], linewidth=MAIN_LW, label="Iron Fly P&L")
    _hline(ax, 0, COLORS["neutral"], "Zero", "-")
    _hline(ax, max_profit, COLORS["profit"], f"Max profit ${max_profit:.0f}")
    _hline(ax, max_loss, COLORS["loss"], f"Max loss ${max_loss:.0f}")
    _vline(ax, be_lo, COLORS["neutral"], f"BE ${be_lo:,.0f}")
    _vline(ax, be_hi, COLORS["neutral"], f"BE ${be_hi:,.0f}")
    _vline(ax, k_atm, COLORS["highlight"], f"ATM ${k_atm:,}", ":")
    apply_style(ax, "Iron Butterfly (Short 5000 Straddle | Long 4900/5100 Wings)", XLABEL, YLABEL)
    ax.legend(fontsize=LEGEND_SIZE)
    _save_matplotlib(fig, save_dir, "pnl-iron-fly.png")

    pfig = _plotly_from_mpl(prices, pnl,
                            "Iron Butterfly (Short 5000 Straddle | Long 4900/5100 Wings)",
                            breakevens=[be_lo, be_hi],
                            max_profit=max_profit, max_loss=max_loss)
    _save_plotly(pfig, save_dir, "pnl-iron-fly.png")


# ── 8. Long Call Butterfly ────────────────────────────────────────────────────

def plot_butterfly(save_dir: Path) -> None:
    """
    Long Call Butterfly: buy low call, sell 2x middle call, buy high call.

    Buy 4900 call, sell 2 × 5000 calls, buy 5100 call.
    Net debit = 5.

    Payoff = -debit
             + max(S - K_lo, 0)
             - 2 * max(S - K_mid, 0)
             + max(S - K_hi, 0)

    Max profit = wing_width - debit = 100 - 5 = 95  (at S = K_mid)
    Max loss   = -debit = -5
    Breakevens = K_lo + debit, K_hi - debit = 4905, 5095
    """
    k_lo, k_mid, k_hi = 4900, 5000, 5100
    debit = 5.0
    wing_width = k_mid - k_lo   # 100

    prices = _price_grid(SPX_SPOT)
    pnl = (
        -debit
        + np.maximum(prices - k_lo, 0)
        - 2 * np.maximum(prices - k_mid, 0)
        + np.maximum(prices - k_hi, 0)
    )

    be_lo = k_lo + debit
    be_hi = k_hi - debit
    max_profit = wing_width - debit
    max_loss = -debit

    fig, ax = plt.subplots(figsize=FIG_STANDARD)
    _fill_pnl(ax, prices, pnl)
    ax.plot(prices, pnl, color=COLORS["primary"], linewidth=MAIN_LW, label="Long Call Fly P&L")
    _hline(ax, 0, COLORS["neutral"], "Zero", "-")
    _hline(ax, max_profit, COLORS["profit"], f"Max profit ${max_profit:.0f}")
    _hline(ax, max_loss, COLORS["loss"], f"Max loss ${max_loss:.0f}")
    _vline(ax, be_lo, COLORS["neutral"], f"BE ${be_lo:,.0f}")
    _vline(ax, be_hi, COLORS["neutral"], f"BE ${be_hi:,.0f}")
    _vline(ax, k_mid, COLORS["highlight"], f"Mid ${k_mid:,}", ":")
    apply_style(ax, "Long Call Butterfly (Buy 4900 / Sell 2×5000 / Buy 5100)", XLABEL, YLABEL)
    ax.legend(fontsize=LEGEND_SIZE)
    _save_matplotlib(fig, save_dir, "pnl-butterfly.png")

    pfig = _plotly_from_mpl(prices, pnl,
                            "Long Call Butterfly (Buy 4900 / Sell 2×5000 / Buy 5100)",
                            breakevens=[be_lo, be_hi],
                            max_profit=max_profit, max_loss=max_loss)
    _save_plotly(pfig, save_dir, "pnl-butterfly.png")


# ── 9. Calendar Spread ────────────────────────────────────────────────────────

def plot_calendar_spread(save_dir: Path) -> None:
    """
    ATM Calendar Spread: buy far-dated call, sell near-dated call (same strike).

    Simplified at near-expiry: the near call expires worthless or ITM;
    the far call is treated as retaining its purchase price as a fixed sunk
    cost (time value ignored — illustrates the structural risk profile only).

    Strike = 5000 (ATM).
    Near call premium collected = 20 (sold).
    Far call premium paid = 35 (bought); at near expiry, value approximated
    as intrinsic value = max(S - K, 0) — simplified, ignores remaining theta.

    P&L at near expiry = near_premium_collected
                         - max(S - K, 0)         [near call obligation]
                         + max(S - K, 0) - far_debit   [far call approx value - cost]
                       = near_premium - far_debit
                       = 20 - 35 = -15  [constant approximation when both deep ITM/OTM]

    Better approximation used here: model the net as
        P&L = near_premium - max(S - K, 0) + theta_residual * max(S-K+buffer, 0)
    For clarity, use a Gaussian-shaped P&L centered on K to capture the
    time-value hump that calendars exhibit at near-expiry.

    Net debit = far_premium - near_premium = 35 - 20 = 15.
    Max profit (at-the-money) ≈ remaining time value of far leg - net debit.
    Breakevens: symmetric around K, approx K ± 50.
    """
    k = 5000
    near_prem, far_prem = 20.0, 35.0
    net_debit = far_prem - near_prem   # 15

    prices = _price_grid(SPX_SPOT)

    # Simplified piecewise: at S=K (ATM) max benefit; declines away from K.
    # Model: near expires worthless (good if S=K); far call worth near_prem + intrinsic.
    # Net P&L ≈ time_value_remaining_far - net_debit
    # We model time value remaining as near_prem * Gaussian envelope (educational approx).
    sigma_approx = 80.0   # ~1.6% of spot — approximate 45-DTE remaining stdev
    time_value_far_remaining = near_prem * np.exp(-0.5 * ((prices - k) / sigma_approx) ** 2)
    # Near leg P&L: collected near_prem, now must pay intrinsic
    near_leg_pnl = near_prem - np.maximum(prices - k, 0)
    # Far leg P&L: paid far_prem, now worth intrinsic + remaining time value
    far_leg_value = np.maximum(prices - k, 0) + time_value_far_remaining
    far_leg_pnl = far_leg_value - far_prem

    pnl = near_leg_pnl + far_leg_pnl

    max_profit = float(pnl.max())
    be_approx_lo = k - sigma_approx * np.sqrt(-2 * np.log(net_debit / near_prem + 1e-9))
    be_approx_hi = k + sigma_approx * np.sqrt(-2 * np.log(net_debit / near_prem + 1e-9))

    fig, ax = plt.subplots(figsize=FIG_STANDARD)
    _fill_pnl(ax, prices, pnl)
    ax.plot(prices, pnl, color=COLORS["primary"], linewidth=MAIN_LW, label="Calendar Spread P&L")
    _hline(ax, 0, COLORS["neutral"], "Zero", "-")
    _hline(ax, max_profit, COLORS["profit"], f"Max profit ~${max_profit:.0f}")
    _hline(ax, -net_debit, COLORS["loss"], f"Max loss ~${-net_debit:.0f}")
    _vline(ax, k, COLORS["highlight"], f"Strike ${k:,}", ":")
    ax.annotate("Simplified: far leg\ntime value approx.",
                xy=(k + 200, -net_debit + 2), fontsize=8,
                color=COLORS["neutral"])
    apply_style(ax,
                "ATM Calendar Spread (Sell Near / Buy Far, Strike 5000)\n"
                "[Near-expiry P&L — far-leg time value approximated]",
                XLABEL, YLABEL)
    ax.legend(fontsize=LEGEND_SIZE)
    _save_matplotlib(fig, save_dir, "pnl-calendar-spread.png")

    pfig = _plotly_from_mpl(prices, pnl,
                            "ATM Calendar Spread (Near-Expiry, Approx.)",
                            breakevens=[],
                            max_profit=max_profit, max_loss=-net_debit)
    _save_plotly(pfig, save_dir, "pnl-calendar-spread.png")


# ── 10. Diagonal Spread ───────────────────────────────────────────────────────

def plot_diagonal_spread(save_dir: Path) -> None:
    """
    Diagonal Spread: buy far-dated deep ITM call, sell near-dated OTM call.

    Far leg: buy 4800 call (deep ITM), premium paid = 220 (intrinsic ~200 + theta 20).
    Near leg: sell 5100 call (OTM), premium received = 18.
    Net debit = 220 - 18 = 202.

    At near expiry, simplified P&L:
      Far leg value ≈ max(S - 4800, 0) + residual_theta
        residual_theta = Gaussian envelope around S=4800 (far leg has more time left)
      Near leg: collected 18, must pay max(S - 5100, 0)

    P&L = [max(S - 4800, 0) + residual_theta - 220] + [18 - max(S - 5100, 0)]

    Simplified: residual_theta modelled as 20 * Gaussian(center=4800, σ=200).
    """
    k_far, prem_far = 4800, 220.0   # long deep ITM call (far expiry)
    k_near, prem_near = 5100, 18.0  # short OTM call (near expiry)
    net_debit = prem_far - prem_near  # 202

    prices = _price_grid(SPX_SPOT)
    theta_far = 20.0 * np.exp(-0.5 * ((prices - k_far) / 200.0) ** 2)
    far_value = np.maximum(prices - k_far, 0) + theta_far
    far_pnl = far_value - prem_far
    near_pnl = prem_near - np.maximum(prices - k_near, 0)
    pnl = far_pnl + near_pnl

    max_profit = float(pnl.max())

    fig, ax = plt.subplots(figsize=FIG_STANDARD)
    _fill_pnl(ax, prices, pnl)
    ax.plot(prices, pnl, color=COLORS["primary"], linewidth=MAIN_LW, label="Diagonal Spread P&L")
    _hline(ax, 0, COLORS["neutral"], "Zero", "-")
    _hline(ax, max_profit, COLORS["profit"], f"Max profit ~${max_profit:.0f}")
    _vline(ax, k_far, COLORS["highlight"], f"Long leg ${k_far:,}", ":")
    _vline(ax, k_near, COLORS["highlight"], f"Short leg ${k_near:,}", "-.")
    ax.annotate("[Far-leg time value approximated]", xy=(prices[10], pnl[10] + 5),
                fontsize=8, color=COLORS["neutral"])
    apply_style(ax,
                "Diagonal Spread (Long 4800 Call far / Short 5100 Call near)\n"
                "[Near-expiry P&L — far-leg residual theta approximated]",
                XLABEL, YLABEL)
    ax.legend(fontsize=LEGEND_SIZE)
    _save_matplotlib(fig, save_dir, "pnl-diagonal-spread.png")

    pfig = _plotly_from_mpl(prices, pnl,
                            "Diagonal Spread (Long far 4800C / Short near 5100C)",
                            breakevens=[], max_profit=max_profit)
    _save_plotly(pfig, save_dir, "pnl-diagonal-spread.png")


# ── 11. Zero-Cost Collar ──────────────────────────────────────────────────────

def plot_zero_risk_collar(save_dir: Path) -> None:
    """
    Zero-Cost Collar: long stock + long OTM put + short OTM call.

    The call premium received exactly offsets the put premium paid (zero net cost).

    Long stock purchased at SPX_SPOT = 5000.
    Long 4800 put, premium = 20 (protection floor).
    Short 5200 call, premium = 20 (upside cap, zero-cost).

    P&L = (S - spot_cost) + max(4800 - S, 0) - 20 - max(S - 5200, 0) + 20
        = (S - 5000) + max(4800 - S, 0) - max(S - 5200, 0)

    Max profit = 5200 - 5000 = 200  (S >= 5200)
    Max loss   = -(5000 - 4800) = -200  (S <= 4800)
    Breakeven  = 5000 (spot cost, since net premium = 0)
    """
    spot_cost = SPX_SPOT   # 5000
    k_put, k_call = 4800, 5200
    put_prem, call_prem = 20.0, 20.0   # zero-cost: equal premiums

    prices = _price_grid(SPX_SPOT, pct=0.14)
    stock_pnl = prices - spot_cost
    long_put = np.maximum(k_put - prices, 0) - put_prem
    short_call = call_prem - np.maximum(prices - k_call, 0)
    pnl = stock_pnl + long_put + short_call

    be = spot_cost   # zero-cost collar, be = cost basis
    max_profit = k_call - spot_cost
    max_loss = -(spot_cost - k_put)

    fig, ax = plt.subplots(figsize=FIG_STANDARD)
    _fill_pnl(ax, prices, pnl)
    ax.plot(prices, pnl, color=COLORS["primary"], linewidth=MAIN_LW, label="Zero-Cost Collar P&L")
    _hline(ax, 0, COLORS["neutral"], "Zero", "-")
    _hline(ax, max_profit, COLORS["profit"], f"Max profit ${max_profit:.0f}")
    _hline(ax, max_loss, COLORS["loss"], f"Max loss ${max_loss:.0f}")
    _vline(ax, be, COLORS["neutral"], f"BE ${be:,}")
    _vline(ax, k_put, COLORS["loss"], f"Put floor ${k_put:,}", ":")
    _vline(ax, k_call, COLORS["highlight"], f"Call cap ${k_call:,}", ":")
    apply_style(ax, "Zero-Cost Collar (Long 4800 Put / Short 5200 Call)", XLABEL, YLABEL)
    ax.legend(fontsize=LEGEND_SIZE)
    _save_matplotlib(fig, save_dir, "pnl-zero-risk-collar.png")

    pfig = _plotly_from_mpl(prices, pnl,
                            "Zero-Cost Collar (Long 4800 Put / Short 5200 Call)",
                            breakevens=[be], max_profit=max_profit, max_loss=max_loss)
    _save_plotly(pfig, save_dir, "pnl-zero-risk-collar.png")


# ── 12. Advanced Collar (slight debit) ────────────────────────────────────────

def plot_advanced_collar(save_dir: Path) -> None:
    """
    Advanced Collar: long stock + long OTM put + short less-OTM call (slight debit).

    The put protects more tightly; the call strikes are closer together.
    Net result is a slight debit paid for better protection.

    Long stock at 5000.
    Long 4900 put, premium = 28 (tighter protection).
    Short 5150 call, premium = 15 (closer OTM cap).
    Net debit = 28 - 15 = 13.

    P&L = (S - 5000) + max(4900 - S, 0) - 28 + 15 - max(S - 5150, 0)
        = (S - 5000) - 13 + max(4900 - S, 0) - max(S - 5150, 0)

    Max profit = 5150 - 5000 - 13 = 137
    Max loss   = -(5000 - 4900) - 13 = -113
    Breakeven  = 5000 + 13 = 5013
    """
    spot_cost = SPX_SPOT   # 5000
    k_put, k_call = 4900, 5150
    put_prem, call_prem = 28.0, 15.0
    net_debit = put_prem - call_prem   # 13

    prices = _price_grid(SPX_SPOT, pct=0.14)
    stock_pnl = prices - spot_cost
    long_put = np.maximum(k_put - prices, 0) - put_prem
    short_call = call_prem - np.maximum(prices - k_call, 0)
    pnl = stock_pnl + long_put + short_call

    be = spot_cost + net_debit
    max_profit = k_call - spot_cost - net_debit
    max_loss = -(spot_cost - k_put) - net_debit

    fig, ax = plt.subplots(figsize=FIG_STANDARD)
    _fill_pnl(ax, prices, pnl)
    ax.plot(prices, pnl, color=COLORS["primary"], linewidth=MAIN_LW, label="Advanced Collar P&L")
    _hline(ax, 0, COLORS["neutral"], "Zero", "-")
    _hline(ax, max_profit, COLORS["profit"], f"Max profit ${max_profit:.0f}")
    _hline(ax, max_loss, COLORS["loss"], f"Max loss ${max_loss:.0f}")
    _vline(ax, be, COLORS["neutral"], f"BE ${be:,}")
    _vline(ax, k_put, COLORS["loss"], f"Put ${k_put:,}", ":")
    _vline(ax, k_call, COLORS["highlight"], f"Call ${k_call:,}", ":")
    apply_style(ax,
                "Advanced Collar (Long 4900 Put / Short 5150 Call, $13 debit)",
                XLABEL, YLABEL)
    ax.legend(fontsize=LEGEND_SIZE)
    _save_matplotlib(fig, save_dir, "pnl-advanced-collar.png")

    pfig = _plotly_from_mpl(prices, pnl,
                            "Advanced Collar (Long 4900 Put / Short 5150 Call, $13 debit)",
                            breakevens=[be], max_profit=max_profit, max_loss=max_loss)
    _save_plotly(pfig, save_dir, "pnl-advanced-collar.png")


# ── 13. Poor Man's Covered Call (PMCC) ───────────────────────────────────────

def plot_pmcc(save_dir: Path) -> None:
    """
    Poor Man's Covered Call: long deep ITM LEAPS call + short near OTM call.

    Long LEAPS: buy 4500 call (deep ITM), premium = 530 (mostly intrinsic).
    Short near: sell 5100 call, premium = 18.
    Net debit = 530 - 18 = 512.

    At near expiry, simplified P&L (same approximation as diagonal):
      LEAPS value ≈ max(S - 4500, 0) + residual_theta
      residual_theta = large Gaussian (LEAPS still has many months left)

    P&L = [max(S - 4500, 0) + residual_theta - 530] + [18 - max(S - 5100, 0)]

    Max profit ≈ 5100 - 4500 - (net_debit - residual_at_K_short) + near_prem
    Breakeven  ≈ 4500 + net_debit - near_prem ≈ 4500 + 512 (ignoring residual theta)
    """
    k_leaps, prem_leaps = 4500, 530.0   # long deep ITM LEAPS
    k_near, prem_near = 5100, 18.0      # short near OTM call
    net_debit = prem_leaps - prem_near  # 512

    prices = _price_grid(SPX_SPOT, pct=0.15)
    # LEAPS residual theta at near expiry: still substantial (LEAPS have 12+ months left)
    theta_leaps = 60.0 * np.exp(-0.5 * ((prices - k_leaps) / 400.0) ** 2)
    leaps_value = np.maximum(prices - k_leaps, 0) + theta_leaps
    leaps_pnl = leaps_value - prem_leaps
    near_pnl = prem_near - np.maximum(prices - k_near, 0)
    pnl = leaps_pnl + near_pnl

    max_profit = float(pnl.max())

    fig, ax = plt.subplots(figsize=FIG_STANDARD)
    _fill_pnl(ax, prices, pnl)
    ax.plot(prices, pnl, color=COLORS["primary"], linewidth=MAIN_LW, label="PMCC P&L")
    _hline(ax, 0, COLORS["neutral"], "Zero", "-")
    _hline(ax, max_profit, COLORS["profit"], f"Max profit ~${max_profit:.0f}")
    _vline(ax, k_leaps, COLORS["highlight"], f"LEAPS ${k_leaps:,}", ":")
    _vline(ax, k_near, COLORS["highlight"], f"Short call ${k_near:,}", "-.")
    ax.annotate("[LEAPS residual theta approximated]",
                xy=(prices[20], pnl[20] + 5), fontsize=8, color=COLORS["neutral"])
    apply_style(ax,
                "PMCC — Poor Man's Covered Call\n"
                "(Long 4500 LEAPS / Short 5100 near call)",
                XLABEL, YLABEL)
    ax.legend(fontsize=LEGEND_SIZE)
    _save_matplotlib(fig, save_dir, "pnl-pmcc.png")

    pfig = _plotly_from_mpl(prices, pnl,
                            "PMCC (Long 4500 LEAPS / Short 5100 near call)",
                            breakevens=[], max_profit=max_profit)
    _save_plotly(pfig, save_dir, "pnl-pmcc.png")


# ── 14. Iron Fly vs Iron Condor Comparison ────────────────────────────────────

def plot_fly_vs_ic(save_dir: Path) -> None:
    """
    Overlay comparison: Iron Condor vs Iron Butterfly on the same chart.

    Iron Condor (IC): 4800/4850 put spread + 5150/5200 call spread, credit 12.50.
    Iron Butterfly (IF): short 5000 straddle + long 4900/5100 wings, credit 45.

    Both structures illustrated on the same price axis for direct comparison.

    Key trade-off:
      - IF has higher max profit (45 vs 12.50) but narrower profit zone
      - IC has wider profit range but lower max credit
    """
    # Iron Condor
    k_ps, k_pl = 4850, 4800
    k_cs, k_cl = 5150, 5200
    credit_ic = 12.50
    prices = _price_grid(SPX_SPOT)
    ic_pnl = (credit_ic
              - np.maximum(k_ps - prices, 0) + np.maximum(k_pl - prices, 0)
              - np.maximum(prices - k_cs, 0) + np.maximum(prices - k_cl, 0))

    # Iron Fly
    k_atm = 5000
    k_pw_if, k_cw_if = 4900, 5100
    credit_if = 45.0
    if_pnl = (credit_if
              - np.maximum(k_atm - prices, 0) + np.maximum(k_pw_if - prices, 0)
              - np.maximum(prices - k_atm, 0) + np.maximum(prices - k_cw_if, 0))

    fig, ax = plt.subplots(figsize=FIG_STANDARD)
    ax.plot(prices, ic_pnl, color=COLORS["primary"], linewidth=MAIN_LW,
            label=f"Iron Condor (credit ${credit_ic})")
    ax.plot(prices, if_pnl, color=COLORS["highlight"], linewidth=MAIN_LW,
            linestyle="--", label=f"Iron Fly (credit ${credit_if})")
    # Combined fill: shade only IC profit zone (less cluttered)
    ax.fill_between(prices, ic_pnl, 0, where=ic_pnl >= 0,
                    color=COLORS["primary"], alpha=0.08)
    ax.fill_between(prices, if_pnl, 0, where=if_pnl >= 0,
                    color=COLORS["highlight"], alpha=0.08)
    _hline(ax, 0, COLORS["neutral"], "Zero", "-")
    apply_style(ax,
                "Iron Condor vs Iron Butterfly — P&L Comparison",
                XLABEL, YLABEL)
    ax.legend(fontsize=LEGEND_SIZE)
    _save_matplotlib(fig, save_dir, "pnl-fly-vs-ic-comparison.png")

    pfig = go.Figure()
    pfig.add_trace(go.Scatter(x=prices, y=ic_pnl,
                              mode="lines", name=f"Iron Condor (credit ${credit_ic})",
                              line=dict(color=COLORS["primary"], width=MAIN_LW)))
    pfig.add_trace(go.Scatter(x=prices, y=if_pnl,
                              mode="lines", name=f"Iron Fly (credit ${credit_if})",
                              line=dict(color=COLORS["highlight"], width=MAIN_LW, dash="dot")))
    pfig.add_hline(y=0, line=dict(color=COLORS["neutral"], dash="dash", width=REF_LW))
    pfig.update_layout(
        title="Iron Condor vs Iron Butterfly — P&L Comparison",
        xaxis_title=XLABEL, yaxis_title=YLABEL,
        plot_bgcolor=COLORS["bg"], paper_bgcolor="white",
        width=900, height=500,
        legend=dict(font=dict(size=LEGEND_SIZE)),
    )
    _save_plotly(pfig, save_dir, "pnl-fly-vs-ic-comparison.png")


# ── 15. LEAPS Call vs Stock Ownership ────────────────────────────────────────

def plot_leaps_vs_stock(save_dir: Path) -> None:
    """
    LEAPS Call vs Stock Ownership at expiry — AAPL example.

    Stock: long 100 shares at AAPL_SPOT = 200; P&L = S - 200 per share.
    LEAPS call: buy 180-strike call (deep ITM, ~25 delta at far expiry),
                premium = 30 per share.
    LEAPS P&L at expiry = max(S - 180, 0) - 30.

    Key comparison points:
      - LEAPS max loss = -30 (premium paid), stock max loss = -200.
      - LEAPS breakeven = 180 + 30 = 210; stock breakeven = 200.
      - Above breakeven: LEAPS profits dollar-for-dollar with stock.
      - Capital efficiency: LEAPS costs 30, stock costs 200 (6.7x leverage).
    """
    spot = AAPL_SPOT          # 200
    k_leaps = 180
    prem_leaps = 30.0

    prices = _price_grid(spot, pct=0.20)
    stock_pnl = prices - spot
    leaps_pnl = np.maximum(prices - k_leaps, 0) - prem_leaps

    be_stock = spot
    be_leaps = k_leaps + prem_leaps   # 210
    max_loss_leaps = -prem_leaps
    max_loss_stock = -spot

    fig, ax = plt.subplots(figsize=FIG_STANDARD)
    ax.plot(prices, stock_pnl, color=COLORS["neutral"], linewidth=MAIN_LW,
            linestyle="--", label=f"Long Stock (cost ${spot:.0f})")
    ax.plot(prices, leaps_pnl, color=COLORS["primary"], linewidth=MAIN_LW,
            label=f"LEAPS 180 Call (prem ${prem_leaps:.0f})")
    ax.fill_between(prices, leaps_pnl, 0, where=leaps_pnl >= 0,
                    color=COLORS["profit"], alpha=FILL_ALPHA)
    ax.fill_between(prices, leaps_pnl, 0, where=leaps_pnl < 0,
                    color=COLORS["loss"], alpha=FILL_ALPHA)
    _hline(ax, 0, COLORS["neutral"], "Zero", "-", lw=1.0)
    _hline(ax, max_loss_leaps, COLORS["loss"], f"LEAPS max loss ${max_loss_leaps:.0f}")
    _vline(ax, be_leaps, COLORS["primary"], f"LEAPS BE ${be_leaps:.0f}")
    _vline(ax, be_stock, COLORS["neutral"], f"Stock BE ${be_stock:.0f}", "-.")
    apply_style(ax,
                "LEAPS Call vs Stock Ownership at Expiry (AAPL)\n"
                "LEAPS 180 Call ($30 premium) vs Long Stock ($200)",
                XLABEL, YLABEL)
    ax.legend(fontsize=LEGEND_SIZE)
    _save_matplotlib(fig, save_dir, "chart-leaps-vs-stock.png")

    pfig = go.Figure()
    pfig.add_trace(go.Scatter(x=prices, y=stock_pnl,
                              mode="lines", name=f"Long Stock (${spot:.0f})",
                              line=dict(color=COLORS["neutral"], width=MAIN_LW, dash="dot")))
    pfig.add_trace(go.Scatter(x=prices, y=leaps_pnl,
                              mode="lines", name=f"LEAPS 180 Call (${prem_leaps:.0f})",
                              line=dict(color=COLORS["primary"], width=MAIN_LW)))
    pfig.add_hline(y=0, line=dict(color=COLORS["neutral"], dash="dash", width=REF_LW))
    pfig.add_vline(x=be_leaps,
                   line=dict(color=COLORS["primary"], dash="dash", width=REF_LW),
                   annotation_text=f"LEAPS BE {be_leaps:.0f}",
                   annotation_position="top left")
    pfig.add_hline(y=max_loss_leaps,
                   line=dict(color=COLORS["loss"], dash="dash", width=REF_LW),
                   annotation_text=f"LEAPS max loss {max_loss_leaps:.0f}",
                   annotation_position="right")
    pfig.update_layout(
        title="LEAPS Call vs Stock Ownership at Expiry (AAPL)",
        xaxis_title=XLABEL, yaxis_title=YLABEL,
        plot_bgcolor=COLORS["bg"], paper_bgcolor="white",
        width=900, height=500,
        legend=dict(font=dict(size=LEGEND_SIZE)),
    )
    _save_plotly(pfig, save_dir, "chart-leaps-vs-stock.png")


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    save_dir = Path(__file__).parent / "outputs"
    save_dir.mkdir(exist_ok=True)

    strategies = [
        plot_csp,
        plot_covered_call,
        plot_wheel_cycle,
        plot_bull_put_spread,
        plot_bear_call_spread,
        plot_iron_condor,
        plot_iron_fly,
        plot_butterfly,
        plot_calendar_spread,
        plot_diagonal_spread,
        plot_zero_risk_collar,
        plot_advanced_collar,
        plot_pmcc,
        plot_fly_vs_ic,
        plot_leaps_vs_stock,
    ]

    for fn in strategies:
        fn(save_dir)

    n = len(strategies)
    print(f"Generated {n} charts ({n} PNG + {n} HTML) in {save_dir}")


if __name__ == "__main__":
    main()
