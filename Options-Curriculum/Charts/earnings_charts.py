"""
earnings_charts.py — Earnings IV Educational Charts
====================================================
Generates 4 educational charts covering earnings-related IV concepts:
  1. IV crush pattern (30-day window centred on earnings day 0)
  2. Implied vs actual earnings moves scatter (synthetic data)
  3. Earnings Iron Condor P&L diagram (AAPL, AAPL_SPOT=200)
  4. IVP distribution 5 days before earnings (synthetic histogram)

Usage:
    python earnings_charts.py
"""

import sys
from pathlib import Path

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np

# Allow running from any CWD while importing sibling constants.py
sys.path.insert(0, str(Path(__file__).parent))
from constants import COLORS, FIG_STANDARD, FIG_WIDE, AAPL_SPOT, DPI


# ── 1. IV Crush Line Chart ────────────────────────────────────────────────────

def plot_earnings_iv_crush(save_dir: Path) -> None:
    """
    Line chart of ATM IV over a 30-day window centred on earnings (day 0).

    Data source: Illustrative synthetic data, not backtested.
    Method: Hand-crafted piecewise trajectory:
      - Days -15 to -2: gradual linear ramp from ~25% to ~45%
      - Day -1: spike to ~55%
      - Day 0: IV crush to ~22%
      - Days +1 to +15: slow mean-reversion from ~22% upward
    """
    days = np.arange(-15, 16)  # -15 to +15 inclusive

    iv = np.zeros(len(days))
    earnings_idx = np.where(days == 0)[0][0]  # index 15

    rng = np.random.default_rng(seed=42)

    # Pre-earnings ramp: day -15 → day -2 (indices 0..13)
    pre_indices = np.where(days < -1)[0]
    iv[pre_indices] = (
        np.linspace(25.0, 45.0, len(pre_indices))
        + rng.normal(0, 0.6, len(pre_indices))
    )

    # Day -1 spike (index 14)
    iv[earnings_idx - 1] = 55.0

    # Day 0: crush (index 15)
    iv[earnings_idx] = 22.0

    # Post-earnings: days +1 to +15 (indices 16..30)
    post_indices = np.where(days > 0)[0]
    iv[post_indices] = (
        np.linspace(22.0, 30.0, len(post_indices))
        + rng.normal(0, 0.5, len(post_indices))
    )

    fig, ax = plt.subplots(figsize=FIG_STANDARD)
    ax.set_facecolor(COLORS["bg"])
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # Main IV line
    ax.plot(days, iv, color=COLORS["primary"], linewidth=2.5, label="ATM IV (%)")

    # Earnings vertical line
    ax.axvline(0, color=COLORS["loss"], linestyle="--", linewidth=1.8,
               label="Earnings announcement")

    # Annotate "IV Crush" with arrow pointing to the post-earnings drop
    ax.annotate(
        "IV Crush",
        xy=(1, iv[earnings_idx + 1]),
        xytext=(6, iv[earnings_idx + 1] + 14),
        arrowprops=dict(arrowstyle="->", color=COLORS["loss"], lw=1.5),
        color=COLORS["loss"], fontsize=10, fontweight="bold", ha="center",
    )

    ax.set_xlabel("Days Relative to Earnings", fontsize=11)
    ax.set_ylabel("Implied Volatility (%)", fontsize=11)
    ax.set_title("ATM IV Around Earnings: The IV Crush Pattern", fontsize=14, pad=12)
    ax.set_xlim(-15, 15)
    ax.legend(fontsize=10)
    ax.tick_params(labelsize=9)

    plt.tight_layout()
    plt.savefig(save_dir / "chart-earnings-iv-crush.png", dpi=DPI, bbox_inches="tight")
    plt.close(fig)


# ── 2. Implied vs Actual Earnings Moves Scatter ───────────────────────────────

def plot_earnings_move_comparison(save_dir: Path) -> None:
    """
    Scatter plot comparing implied earnings move (x) to actual move (y).

    Data source: Illustrative synthetic data, not backtested.
    Method: ~50 events generated with numpy seed=42.
      - Implied moves drawn from uniform 3–15%.
      - Actual moves: ~60% of events have actual < implied (premium overstatement).
        For those, actual = implied * U(0.3, 0.95).
        For the remaining ~40%, actual = implied * U(1.0, 1.6).
    Points coloured green where actual < implied, red otherwise.
    """
    rng = np.random.default_rng(seed=42)
    n = 50

    implied = rng.uniform(3.0, 15.0, n)

    # Determine which events have actual < implied (~60%)
    under = rng.random(n) < 0.60
    ratio = np.where(under, rng.uniform(0.30, 0.95, n), rng.uniform(1.00, 1.60, n))
    actual = implied * ratio

    colors = np.where(under, COLORS["profit"], COLORS["loss"])

    fig, ax = plt.subplots(figsize=FIG_STANDARD)
    ax.set_facecolor(COLORS["bg"])
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # 45-degree "priced correctly" reference line
    max_val = max(implied.max(), actual.max()) * 1.05
    ax.plot([0, max_val], [0, max_val], color=COLORS["neutral"], linewidth=1.5,
            linestyle="--", label='45° "priced correctly" line', zorder=1)

    # Scatter points
    for xi, yi, ci in zip(implied, actual, colors):
        ax.scatter(xi, yi, color=ci, s=60, alpha=0.80, zorder=2)

    # Legend patches
    profit_patch = mpatches.Patch(color=COLORS["profit"], label="Actual < Implied (premium seller wins)")
    loss_patch   = mpatches.Patch(color=COLORS["loss"],   label="Actual > Implied (buyer wins)")
    ref_line     = mpatches.Patch(color=COLORS["neutral"], label='45° "priced correctly" line')
    ax.legend(handles=[profit_patch, loss_patch, ref_line], fontsize=9, loc="upper left")

    # Annotation: ~60% of events
    ax.annotate(
        "~60% of events:\nactual < implied move",
        xy=(6.0, 3.0),
        xytext=(10.0, 2.0),
        arrowprops=dict(arrowstyle="->", color=COLORS["neutral"], lw=1.2),
        color=COLORS["neutral"], fontsize=9, ha="center",
    )

    # Watermark
    ax.text(0.98, 0.02, "Illustrative synthetic data",
            transform=ax.transAxes, fontsize=8, color=COLORS["neutral"],
            ha="right", va="bottom", style="italic")

    ax.set_xlabel("Implied Move (%)", fontsize=11)
    ax.set_ylabel("Actual Move (%)", fontsize=11)
    ax.set_title("Implied vs Actual Earnings Moves", fontsize=14, pad=12)
    ax.set_xlim(0, max_val)
    ax.set_ylim(0, max_val)
    ax.tick_params(labelsize=9)

    plt.tight_layout()
    plt.savefig(save_dir / "chart-earnings-move-comparison.png", dpi=DPI, bbox_inches="tight")
    plt.close(fig)


# ── 3. Earnings Iron Condor P&L Diagram ───────────────────────────────────────

def plot_earnings_ic_example(save_dir: Path) -> None:
    """
    P&L diagram for an earnings Iron Condor on AAPL at expiry.

    Data source: Illustrative synthetic data, not backtested.
    Structure (AAPL_SPOT = 200):
      - Short $195 put  / Long $192.50 put  (put spread, $2.50 wide)
      - Short $205 call / Long $207.50 call (call spread, $2.50 wide)
      - Net credit received: $1.25 (= max profit)
      - Max loss per side: $2.50 - $1.25 = $1.25

    Method: piecewise linear P&L function computed over price range 182–218.
    Expected move boundaries drawn at ±5% ($190 and $210).
    """
    spot = AAPL_SPOT  # 200

    # Strike levels
    put_long  = 192.50
    put_short = 195.00
    call_short = 205.00
    call_long  = 207.50

    credit = 1.25
    wing_width = 2.50  # each wing

    prices = np.linspace(182, 218, 500)

    def ic_pnl(S: np.ndarray) -> np.ndarray:
        """Iron condor P&L at expiry per share."""
        # Put spread: short put_short, long put_long
        put_spread_pnl = (
            np.maximum(put_short - S, 0) - np.maximum(put_long - S, 0)
        )
        # Call spread: short call_short, long call_long
        call_spread_pnl = (
            np.maximum(S - call_short, 0) - np.maximum(S - call_long, 0)
        )
        # Credit received nets out the spreads (short spreads cost premium)
        return credit - put_spread_pnl - call_spread_pnl

    pnl = ic_pnl(prices)

    # Breakeven prices
    be_low  = put_short - credit   # 195 - 1.25 = 193.75
    be_high = call_short + credit  # 205 + 1.25 = 206.25

    # Expected move boundaries (±5%)
    em_low  = spot * 0.95   # 190
    em_high = spot * 1.05   # 210

    fig, ax = plt.subplots(figsize=FIG_WIDE)
    ax.set_facecolor(COLORS["bg"])
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # Fill profit zone (between breakevens)
    ax.fill_between(prices, pnl, 0,
                    where=(pnl > 0),
                    color=COLORS["profit"], alpha=0.25, label="Profit zone")

    # Fill loss zones (outside breakevens)
    ax.fill_between(prices, pnl, 0,
                    where=(pnl < 0),
                    color=COLORS["loss"], alpha=0.25, label="Loss zone")

    # Main P&L curve
    ax.plot(prices, pnl, color=COLORS["primary"], linewidth=2.5, label="IC P&L at expiry")
    ax.axhline(0, color=COLORS["neutral"], linewidth=1.0)

    # Max profit / max loss horizontal dashed lines
    ax.axhline(credit, color=COLORS["profit"], linestyle="--", linewidth=1.4,
               label=f"Max profit: +${credit:.2f}")
    ax.axhline(-credit, color=COLORS["loss"], linestyle="--", linewidth=1.4,
               label=f"Max loss: −${credit:.2f}")

    # Breakeven vertical lines
    ax.axvline(be_low,  color=COLORS["neutral"], linestyle="--", linewidth=1.2,
               label=f"Breakevens: ${be_low:.2f} / ${be_high:.2f}")
    ax.axvline(be_high, color=COLORS["neutral"], linestyle="--", linewidth=1.2)

    # Expected move boundaries
    ax.axvline(em_low,  color=COLORS["highlight"], linestyle="--", linewidth=1.4,
               label=f"Expected move ±5%: ${em_low:.0f} / ${em_high:.0f}")
    ax.axvline(em_high, color=COLORS["highlight"], linestyle="--", linewidth=1.4)

    # Zone labels
    ax.text(spot, credit * 0.55, "IV crush\nprofit zone",
            ha="center", va="center", fontsize=9, color=COLORS["profit"], fontweight="bold")
    ax.text(put_long - 2, -credit * 0.65, "danger\nzone",
            ha="center", va="center", fontsize=9, color=COLORS["loss"], fontweight="bold")
    ax.text(call_long + 2, -credit * 0.65, "danger\nzone",
            ha="center", va="center", fontsize=9, color=COLORS["loss"], fontweight="bold")

    ax.set_xlabel("AAPL Price at Expiry ($)", fontsize=11)
    ax.set_ylabel("P&L per Share ($)", fontsize=11)
    ax.set_title(
        f"Earnings Iron Condor — AAPL (Spot ${spot})\n"
        f"Sell ${put_short}/${put_long:.2f}P + ${call_short}/${call_long:.2f}C  |  ${credit:.2f} credit",
        fontsize=13, pad=12,
    )
    ax.legend(fontsize=9, loc="lower center", ncol=2)
    ax.tick_params(labelsize=9)
    ax.set_xlim(182, 218)

    plt.tight_layout()
    plt.savefig(save_dir / "chart-earnings-ic-example.png", dpi=DPI, bbox_inches="tight")
    plt.close(fig)


# ── 4. IVP Distribution 5 Days Before Earnings ───────────────────────────────

def plot_iv_preearnings_distribution(save_dir: Path) -> None:
    """
    Histogram of IVP values 5 days before earnings across 100 synthetic events.

    Data source: Illustrative synthetic data, not backtested.
    Method: IVP drawn from a beta distribution (alpha=5, beta=2) scaled to
    0–100, which produces a distribution skewed toward the 60–90 range,
    reflecting the empirical tendency for pre-earnings IV to be elevated.
    numpy seed=42.
    """
    rng = np.random.default_rng(seed=42)
    # Beta(5,2) skews right (toward high values)
    ivp_values = rng.beta(5, 2, size=100) * 100

    bins = np.arange(0, 105, 5)
    counts, edges = np.histogram(ivp_values, bins=bins)
    median_ivp = float(np.median(ivp_values))

    fig, ax = plt.subplots(figsize=FIG_STANDARD)
    ax.set_facecolor(COLORS["bg"])
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # Color bars by IVP threshold
    for left, right, count in zip(edges[:-1], edges[1:], counts):
        midpoint = (left + right) / 2.0
        bar_color = COLORS["profit"] if midpoint >= 50 else COLORS["loss"]
        ax.bar(left, count, width=(right - left), color=bar_color,
               edgecolor="white", linewidth=0.8, align="edge", alpha=0.85)

    # Median annotation
    ax.axvline(median_ivp, color=COLORS["primary"], linestyle="--", linewidth=1.8,
               label=f"Median IVP: {median_ivp:.0f}")
    ax.text(median_ivp + 1.5, counts.max() * 0.92,
            f"Median\n{median_ivp:.0f}",
            color=COLORS["primary"], fontsize=9, va="top")

    # Threshold line
    ax.axvline(50, color=COLORS["neutral"], linestyle=":", linewidth=1.2,
               label="IVP = 50 threshold")

    # Legend patches
    sell_patch = mpatches.Patch(color=COLORS["profit"], alpha=0.85,
                                label="IVP ≥ 50 — elevated (sell-side)")
    low_patch  = mpatches.Patch(color=COLORS["loss"],   alpha=0.85,
                                label="IVP < 50 — depressed (avoid)")
    ax.legend(handles=[sell_patch, low_patch], fontsize=9, loc="upper left")

    # Explanatory annotation
    ax.text(
        0.98, 0.96,
        "Pre-earnings IV tends to be elevated\n— most tickers already in 'sell' territory",
        transform=ax.transAxes, fontsize=8.5, color=COLORS["neutral"],
        ha="right", va="top", style="italic",
        bbox=dict(boxstyle="round,pad=0.4", facecolor=COLORS["bg"],
                  edgecolor=COLORS["neutral"], alpha=0.7),
    )

    ax.set_xlabel("IV Percentile (IVP %)", fontsize=11)
    ax.set_ylabel("Count (events)", fontsize=11)
    ax.set_title("IVP Distribution 5 Days Before Earnings", fontsize=14, pad=12)
    ax.set_xlim(0, 100)
    ax.tick_params(labelsize=9)

    plt.tight_layout()
    plt.savefig(save_dir / "chart-iv-preearnings-distribution.png", dpi=DPI, bbox_inches="tight")
    plt.close(fig)


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    save_dir = Path(__file__).parent / "outputs"
    save_dir.mkdir(exist_ok=True)

    plot_earnings_iv_crush(save_dir)
    plot_earnings_move_comparison(save_dir)
    plot_earnings_ic_example(save_dir)
    plot_iv_preearnings_distribution(save_dir)

    print("Generated 4 earnings charts")


if __name__ == "__main__":
    main()
