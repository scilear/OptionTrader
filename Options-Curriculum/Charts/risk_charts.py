"""
risk_charts.py
==============
Generates 4 educational risk-management charts for the Options-Curriculum vault.

Charts produced:
    chart-drawdown-recovery.png     — asymmetry of drawdowns
    chart-50pct-vs-expiry.png       — close at 50% profit vs hold to expiry
    chart-winrate-profit-factor.png — EV heatmap (win rate × win/loss ratio)
    chart-position-sizing.png       — Kelly-style equity curves by risk %

Run from the Charts/ directory:
    python risk_charts.py
"""

import sys
from pathlib import Path

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np

# Allow running from any working directory by adding Charts/ to sys.path
sys.path.insert(0, str(Path(__file__).parent))
from constants import COLORS, DPI, FIG_STANDARD, FIG_WIDE  # noqa: E402


# ── 1. Drawdown Recovery ──────────────────────────────────────────────────────

def chart_drawdown_recovery(save_dir: Path) -> None:
    """
    Horizontal bar chart of the % gain required to recover from a drawdown.

    Statistical method: deterministic formula.
    Assumptions:
        - Recovery is measured from the post-drawdown equity low back to the
          original peak (i.e. "get-whole" gain from the trough).
        - Formula: recovery = 1 / (1 - drawdown) - 1
          Example: a 50% drawdown requires a 100% gain to recover.
    """
    drawdowns = np.array([0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50])
    recoveries = 1.0 / (1.0 - drawdowns) - 1.0

    labels = [f"{int(d * 100)}% drawdown" for d in drawdowns]
    bar_values = recoveries * 100  # express as %

    fig, ax = plt.subplots(figsize=FIG_STANDARD)
    fig.patch.set_facecolor(COLORS["bg"])

    bars = ax.barh(
        labels,
        bar_values,
        color=COLORS["loss"],
        edgecolor="white",
        linewidth=0.6,
        height=0.55,
    )

    # Annotate each bar with the recovery %
    for bar, val in zip(bars, bar_values):
        ax.text(
            bar.get_width() + 0.8,
            bar.get_y() + bar.get_height() / 2,
            f"+{val:.1f}%",
            va="center",
            ha="left",
            fontsize=10,
            fontweight="bold",
            color=COLORS["loss"],
        )

    # Formula annotation
    ax.text(
        0.97,
        0.05,
        "recovery = 1 / (1 − drawdown) − 1",
        transform=ax.transAxes,
        ha="right",
        va="bottom",
        fontsize=9,
        color=COLORS["neutral"],
        style="italic",
        bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor=COLORS["neutral"], alpha=0.7),
    )

    ax.set_title(
        "The Asymmetry of Drawdowns: Recovery Required",
        fontsize=14,
        pad=12,
    )
    ax.set_xlabel("Gain Required to Recover (%)", fontsize=11)
    ax.set_xlim(0, bar_values.max() * 1.18)
    ax.set_facecolor(COLORS["bg"])
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(labelsize=9)

    plt.tight_layout()
    plt.savefig(save_dir / "chart-drawdown-recovery.png", dpi=DPI, bbox_inches="tight")
    plt.close()


# ── 2. Close at 50% vs Hold to Expiry ────────────────────────────────────────

def chart_50pct_vs_expiry(save_dir: Path) -> None:
    """
    Two simulated equity curves over 100 trades: "Close at 50% profit" vs
    "Hold to expiry". Monte Carlo with 1000 paths each.

    Statistical method: Monte Carlo simulation.
    Assumptions:
        Hold to expiry  — win_rate=65%, avg_win=$200, avg_loss=$400
        Close at 50%    — win_rate=68%, avg_win=$100, avg_loss=$250
          (same underlying trades; profit captured earlier, losses cut earlier)
        Starting equity: $10,000 (implicit; curves show cumulative P&L)
        Trades are i.i.d. (no correlation, no position sizing change).
        Percentile bands: 10th and 90th across 1000 paths.
    """
    rng = np.random.default_rng(42)
    n_trades = 100
    n_paths = 1000

    def simulate(win_rate: float, avg_win: float, avg_loss: float) -> np.ndarray:
        """Return (n_paths, n_trades+1) cumulative P&L array."""
        wins = rng.random((n_paths, n_trades)) < win_rate
        pnl = np.where(wins, avg_win, -avg_loss)
        cum = np.cumsum(pnl, axis=1)
        # prepend zero (start of trading)
        return np.hstack([np.zeros((n_paths, 1)), cum])

    hold_paths = simulate(0.65, 200.0, 400.0)
    close50_paths = simulate(0.68, 100.0, 250.0)

    trades = np.arange(n_trades + 1)

    fig, ax = plt.subplots(figsize=FIG_WIDE)
    fig.patch.set_facecolor(COLORS["bg"])

    def plot_strategy(paths: np.ndarray, color: str, label: str) -> None:
        median = np.median(paths, axis=0)
        p10 = np.percentile(paths, 10, axis=0)
        p90 = np.percentile(paths, 90, axis=0)
        ax.fill_between(trades, p10, p90, color=color, alpha=0.15, linewidth=0)
        ax.plot(trades, median, color=color, linewidth=2.5, label=label)

    plot_strategy(hold_paths, COLORS["primary"], "Hold to Expiry (median)")
    plot_strategy(close50_paths, COLORS["profit"], "Close at 50% Profit (median)")

    ax.axhline(0, color=COLORS["neutral"], linewidth=1.2, linestyle="--", zorder=1)

    ax.set_title("Close at 50% Profit vs Hold to Expiry — 100-Trade Monte Carlo", fontsize=14, pad=12)
    ax.set_xlabel("Trade Number", fontsize=11)
    ax.set_ylabel("Cumulative P&L ($)", fontsize=11)
    ax.set_facecolor(COLORS["bg"])
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(labelsize=9)

    # Shaded-band legend entries
    hold_patch = mpatches.Patch(color=COLORS["primary"], alpha=0.20, label="Hold to Expiry (10–90th pct)")
    c50_patch = mpatches.Patch(color=COLORS["profit"], alpha=0.20, label="Close at 50% (10–90th pct)")
    handles, labels_leg = ax.get_legend_handles_labels()
    ax.legend(
        handles + [hold_patch, c50_patch],
        labels_leg + [hold_patch.get_label(), c50_patch.get_label()],
        fontsize=9,
        loc="upper left",
    )

    plt.tight_layout()
    plt.savefig(save_dir / "chart-50pct-vs-expiry.png", dpi=DPI, bbox_inches="tight")
    plt.close()


# ── 3. Win-Rate × Profit-Factor EV Heatmap ───────────────────────────────────

def chart_winrate_profit_factor(save_dir: Path) -> None:
    """
    Heatmap of expected value across win rates and win/loss ratios.

    Statistical method: closed-form expected value.
    Assumptions:
        EV = win_rate * avg_win - (1 - win_rate) * avg_loss
        avg_loss is normalised to 1; avg_win = ratio (the win/loss ratio).
        EV is therefore expressed in units of 1 average loss.
        "Income strategy sweet spot" box: win rate 65–75%, ratio 0.4–0.7.
    """
    win_rates = np.arange(0.50, 0.81, 0.05)   # 50% … 80%
    ratios = np.arange(0.3, 2.01, 0.1)         # 0.3 … 2.0

    # EV matrix: rows = ratios (y), cols = win rates (x)
    WR, R = np.meshgrid(win_rates, ratios)
    ev = WR * R - (1.0 - WR) * 1.0

    fig, ax = plt.subplots(figsize=FIG_WIDE)
    fig.patch.set_facecolor(COLORS["bg"])

    # Build a diverging colormap anchored at zero
    import matplotlib.colors as mcolors

    vmax = np.abs(ev).max()
    norm = mcolors.TwoSlopeNorm(vmin=-vmax, vcenter=0.0, vmax=vmax)
    # Red→white→green custom colormap
    cmap = mcolors.LinearSegmentedColormap.from_list(
        "rv_cmap",
        [COLORS["loss"], "#FFFFFF", COLORS["profit"]],
        N=256,
    )

    pcm = ax.pcolormesh(
        win_rates * 100,  # x axis in %
        ratios,
        ev,
        cmap=cmap,
        norm=norm,
        shading="nearest",
    )

    cbar = fig.colorbar(pcm, ax=ax, pad=0.02)
    cbar.set_label("Expected Value (units of 1 avg loss)", fontsize=10)
    cbar.ax.tick_params(labelsize=8)

    # Zero-EV contour
    ax.contour(
        win_rates * 100,
        ratios,
        ev,
        levels=[0.0],
        colors=[COLORS["neutral"]],
        linewidths=1.5,
        linestyles="--",
    )

    # Annotate cells with EV values
    for i, r in enumerate(ratios):
        for j, wr in enumerate(win_rates):
            val = ev[i, j]
            txt_color = "white" if abs(val) > 0.35 * vmax else "black"
            ax.text(
                wr * 100,
                r,
                f"{val:+.2f}",
                ha="center",
                va="center",
                fontsize=7.5,
                color=txt_color,
                fontweight="bold",
            )

    # "Income strategy sweet spot" rectangle
    # win rate 65–75% → x from 65 to 75; ratio 0.4–0.7 → y from 0.4 to 0.7
    rect = mpatches.FancyBboxPatch(
        (64.5, 0.35),          # lower-left corner (accounting for cell width)
        width=10.0,            # 65→75%
        height=0.35,           # 0.4→0.75 ratio
        boxstyle="round,pad=0.0",
        linewidth=2.2,
        edgecolor=COLORS["highlight"],
        facecolor="none",
        zorder=5,
    )
    ax.add_patch(rect)
    ax.text(
        69.5,
        0.76,
        "Income strategy\nsweet spot",
        ha="center",
        va="bottom",
        fontsize=8.5,
        color=COLORS["highlight"],
        fontweight="bold",
        zorder=6,
    )

    ax.set_title("Expected Value: Win Rate × Win/Loss Ratio", fontsize=14, pad=12)
    ax.set_xlabel("Win Rate (%)", fontsize=11)
    ax.set_ylabel("Win/Loss Ratio (avg_win / avg_loss)", fontsize=11)
    ax.set_xticks(win_rates * 100)
    ax.set_xticklabels([f"{int(w*100)}%" for w in win_rates], fontsize=9)
    ax.set_yticks(ratios)
    ax.set_yticklabels([f"{r:.1f}" for r in ratios], fontsize=8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    plt.tight_layout()
    plt.savefig(save_dir / "chart-winrate-profit-factor.png", dpi=DPI, bbox_inches="tight")
    plt.close()


# ── 4. Position Sizing — Equity Curves ───────────────────────────────────────

def chart_position_sizing(save_dir: Path) -> None:
    """
    Median equity curves for 1%, 2%, 5%, 10% risk per trade over 200 trades.

    Statistical method: Monte Carlo simulation (1000 paths, median reported).
    Assumptions:
        Starting equity: $100,000.
        Win rate: 65%.
        On a win:  gain  = risk_pct * 0.5 * current_equity  (0.5× risk/reward,
                   realistic for income strategies collecting ~50% of max loss).
        On a loss: lose  = risk_pct       * current_equity.
        Compounding: equity updated after each trade.
        Seed: numpy default_rng(42) for reproducibility.
    """
    rng = np.random.default_rng(42)
    n_trades = 200
    n_paths = 1000
    win_rate = 0.65
    starting_equity = 100_000.0

    risk_levels = [0.01, 0.02, 0.05, 0.10]
    colors = [COLORS["profit"], COLORS["primary"], COLORS["highlight"], COLORS["loss"]]
    labels = ["1% risk/trade", "2% risk/trade", "5% risk/trade", "10% risk/trade"]

    fig, ax = plt.subplots(figsize=FIG_WIDE)
    fig.patch.set_facecolor(COLORS["bg"])

    trades = np.arange(n_trades + 1)

    for risk_pct, color, label in zip(risk_levels, colors, labels):
        # Simulate all paths simultaneously
        equity = np.full((n_paths,), starting_equity, dtype=float)
        # Store equity snapshots: shape (n_paths, n_trades+1)
        snapshots = np.empty((n_paths, n_trades + 1))
        snapshots[:, 0] = equity

        wins_matrix = rng.random((n_paths, n_trades)) < win_rate

        for t in range(n_trades):
            wins = wins_matrix[:, t]
            gain = risk_pct * 0.5 * equity * wins
            loss = risk_pct * equity * (~wins)
            equity = equity + gain - loss
            snapshots[:, t + 1] = equity

        median_path = np.median(snapshots, axis=0)
        ax.plot(trades, median_path / 1_000, color=color, linewidth=2.2, label=label)

    ax.axhline(
        starting_equity / 1_000,
        color=COLORS["neutral"],
        linewidth=1.2,
        linestyle="--",
        label="Starting equity",
    )

    # Annotation
    ax.text(
        0.98,
        0.08,
        "Higher risk = higher upside BUT steeper drawdowns",
        transform=ax.transAxes,
        ha="right",
        va="bottom",
        fontsize=9,
        color="#555555",
        style="italic",
        bbox=dict(boxstyle="round,pad=0.35", facecolor="white", edgecolor=COLORS["neutral"], alpha=0.75),
    )

    ax.set_title("Position Sizing: Median Equity Curve by Risk % per Trade (200 Trades)", fontsize=14, pad=12)
    ax.set_xlabel("Trade Number", fontsize=11)
    ax.set_ylabel("Portfolio Value ($k)", fontsize=11)
    ax.set_facecolor(COLORS["bg"])
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(labelsize=9)
    ax.legend(fontsize=9, loc="upper left")

    plt.tight_layout()
    plt.savefig(save_dir / "chart-position-sizing.png", dpi=DPI, bbox_inches="tight")
    plt.close()


# ── Entry point ───────────────────────────────────────────────────────────────

def main() -> None:
    save_dir = Path(__file__).parent / "outputs"
    save_dir.mkdir(exist_ok=True)

    chart_drawdown_recovery(save_dir)
    chart_50pct_vs_expiry(save_dir)
    chart_winrate_profit_factor(save_dir)
    chart_position_sizing(save_dir)

    print("Generated 4 risk charts")


if __name__ == "__main__":
    main()
