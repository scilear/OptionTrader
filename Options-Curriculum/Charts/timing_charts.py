"""
timing_charts.py — Options Timing & Entry Window Educational Charts
===================================================================
Generates 4 educational charts covering entry timing concepts:
  1. Intraday VIX/IV level through a 0DTE trading day — ideal entry window
  2. Intraday SPX options volume U-shape — avoid vs preferred entry zones
  3. Earnings implied move vs actual move — grouped bar chart (synthetic)
  4. OTM butterfly value vs underlying at 4 time-to-expiry snapshots (superfly gamma)

Usage:
    python timing_charts.py
"""

import sys
from pathlib import Path

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import norm

# Allow running from any CWD while importing sibling constants.py
sys.path.insert(0, str(Path(__file__).parent))
from constants import COLORS, FIG_STANDARD, FIG_WIDE, DPI


# ── 1. Intraday VIX/IV level (0DTE entry window) ─────────────────────────────

def plot_0dte_ivx_by_time(save_dir: Path) -> None:
    """
    Simulated intraday VIX/IV level through a typical 0DTE trading day.

    Data source: synthetic/illustrative.
    Method: hand-crafted piecewise curve with open spike, midday calm, and
    power-hour uptick using cubic interpolation over 5-minute intervals from
    9:30 AM to 4:00 PM (78 bars).
    """
    # 5-minute intervals: 9:30 → 16:00 = 390 minutes = 78 bars
    n_bars = 78
    minutes = np.linspace(0, 390, n_bars)  # minutes since 9:30

    # Anchor points (minute, IV level)
    # 0 = 9:30, 30 = 10:00, 60 = 10:30, 90 = 11:00, 150 = 12:00,
    # 210 = 13:00, 270 = 14:00, 330 = 15:00, 360 = 15:30, 390 = 16:00
    anchor_min = np.array([0, 10, 25, 30, 60, 90, 150, 210, 270, 330, 360, 390])
    anchor_iv  = np.array([22.5, 26.0, 23.5, 21.0, 18.5, 17.5, 17.0, 17.2, 17.8, 18.5, 19.5, 20.2])

    # Cubic interpolation from anchors onto 5-min grid
    iv = np.interp(minutes, anchor_min, anchor_iv)

    # Add small realistic noise
    rng = np.random.default_rng(seed=7)
    iv = iv + rng.normal(0, 0.15, n_bars)

    # Human-readable x tick labels and positions (in minutes from 9:30)
    tick_minutes = [0, 30, 60, 90, 150, 210, 270, 330, 360, 390]
    tick_labels  = ["9:30", "10:00", "10:30", "11:00", "12:00",
                    "13:00", "14:00", "15:00", "15:30", "16:00"]

    fig, ax = plt.subplots(figsize=FIG_STANDARD)
    ax.set_facecolor(COLORS["bg"])
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # Preferred 0DTE entry window: 10:00–11:00 AM = minutes 30–90
    entry_mask = (minutes >= 30) & (minutes <= 90)
    ax.fill_between(
        minutes, 0, 40,
        where=entry_mask,
        color=COLORS["warning"], alpha=0.18,
        label="Ideal 0DTE entry window (10:00–11:00)",
    )
    # Entry zone boundary lines
    ax.axvline(30,  color=COLORS["warning"], linestyle="--", linewidth=1.2)
    ax.axvline(90,  color=COLORS["warning"], linestyle="--", linewidth=1.2)

    # Main IV curve
    ax.plot(minutes, iv, color=COLORS["primary"], linewidth=2.5, label="Intraday IV level (VIX proxy)")

    # Annotation with arrow pointing into the entry zone
    mid_entry = 60  # 10:30
    iv_at_mid = float(np.interp(mid_entry, minutes, iv))
    ax.annotate(
        "Ideal 0DTE\nentry window",
        xy=(mid_entry, iv_at_mid - 0.5),
        xytext=(mid_entry + 80, iv_at_mid + 3.5),
        arrowprops=dict(arrowstyle="->", color=COLORS["warning"], lw=1.4),
        color=COLORS["warning"], fontsize=9, ha="center", fontweight="bold",
    )

    ax.set_xticks(tick_minutes)
    ax.set_xticklabels(tick_labels, fontsize=9)
    ax.set_xlabel("Time of Day (ET)", fontsize=11)
    ax.set_ylabel("Implied Volatility Level (%)", fontsize=11)
    ax.set_title("Intraday IV / VIX Proxy — Typical 0DTE Trading Day", fontsize=14, pad=12)
    ax.set_ylim(14, 30)
    ax.legend(fontsize=10)
    ax.tick_params(labelsize=9)

    plt.tight_layout()
    plt.savefig(save_dir / "chart-0dte-ivx-by-time.png", dpi=DPI, bbox_inches="tight")
    plt.close(fig)


# ── 2. Intraday SPX options volume (U-shape) ─────────────────────────────────

def plot_intraday_volume(save_dir: Path) -> None:
    """
    Typical intraday SPX options volume curve showing the U-shape pattern.

    Data source: synthetic/illustrative.
    Method: hourly bar chart with manually calibrated volumes reflecting the
    well-known U-shape (high at open, trough at midday, high at close).
    Bars are coloured red (avoid at open), green (preferred entry), and
    neutral (rest of day).
    """
    # Hour-start labels and approximate relative volume (arbitrary units)
    bar_labels = ["9:30", "10:00", "10:30", "11:00", "11:30",
                  "12:00", "13:00", "14:00", "15:00", "15:30"]
    volumes    = [100,    78,      65,      58,      52,
                  45,     50,      60,      85,      110]

    x = np.arange(len(bar_labels))

    # Zone classification per bar
    # avoid: 9:30 (index 0)
    # preferred: 10:00, 10:30, 11:00, 11:30 (indices 1-4)
    # neutral: rest
    avoid_idx     = [0]
    preferred_idx = [1, 2, 3, 4]
    neutral_idx   = [5, 6, 7, 8, 9]

    bar_colors = []
    for i in range(len(bar_labels)):
        if i in avoid_idx:
            bar_colors.append(COLORS["loss"])
        elif i in preferred_idx:
            bar_colors.append(COLORS["profit"])
        else:
            bar_colors.append(COLORS["neutral"])

    fig, ax = plt.subplots(figsize=FIG_STANDARD)
    ax.set_facecolor(COLORS["bg"])
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    bars = ax.bar(x, volumes, color=bar_colors, edgecolor="white", linewidth=0.8, width=0.7)

    # Volume labels on top of bars
    for bar, vol in zip(bars, volumes):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 1.5,
            str(vol),
            ha="center", va="bottom", fontsize=8, color="#444444",
        )

    # Legend patches
    patches = [
        mpatches.Patch(color=COLORS["loss"],    label="Avoid — open chaos (9:30–10:00)"),
        mpatches.Patch(color=COLORS["profit"],  label="Preferred entry (10:00–11:30)"),
        mpatches.Patch(color=COLORS["neutral"], label="Neutral / close surge"),
    ]
    ax.legend(handles=patches, fontsize=9, loc="upper right")

    ax.set_xticks(x)
    ax.set_xticklabels(bar_labels, fontsize=9)
    ax.set_xlabel("Time of Day (ET)", fontsize=11)
    ax.set_ylabel("Relative Options Volume (index)", fontsize=11)
    ax.set_title("Intraday SPX Options Volume — U-Shape Pattern", fontsize=14, pad=12)
    ax.set_ylim(0, 130)
    ax.tick_params(labelsize=9)

    plt.tight_layout()
    plt.savefig(save_dir / "chart-intraday-volume.png", dpi=DPI, bbox_inches="tight")
    plt.close(fig)


# ── 3. Earnings implied move vs actual move ───────────────────────────────────

def plot_earnings_move_vs_actual(save_dir: Path) -> None:
    """
    Grouped bar chart: implied move vs actual move for 20 synthetic earnings events.

    Data source: synthetic/illustrative — numpy random seed=42 for reproducibility.
    Method: implied moves drawn from Uniform(2%, 8%); actual moves drawn from
    a skewed distribution so that roughly 65% of actuals fall below implied
    (consistent with empirical IV-crush literature).
    """
    rng = np.random.default_rng(seed=42)
    n_events = 20

    implied = rng.uniform(2.0, 8.0, n_events)
    # Actual: ~65% of the time actual < implied (IV crush profitable)
    # Model actual as implied * multiplier where multiplier ~ Beta(2, 3) * 1.5
    multiplier = rng.beta(2, 3, n_events) * 1.8 + 0.2
    actual = implied * multiplier

    crush_count = int((actual < implied).sum())  # should be ~13

    event_labels = [f"E{i+1}" for i in range(n_events)]
    x = np.arange(n_events)
    width = 0.38

    fig, ax = plt.subplots(figsize=FIG_WIDE)
    ax.set_facecolor(COLORS["bg"])
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # Implied bars — neutral gray
    ax.bar(x - width / 2, implied, width=width, color=COLORS["neutral"],
           label="Implied move (%)", zorder=2)

    # Actual bars — green if actual < implied (profitable IV crush), red otherwise
    actual_colors = [
        COLORS["profit"] if act < imp else COLORS["loss"]
        for act, imp in zip(actual, implied)
    ]
    ax.bar(x + width / 2, actual, width=width, color=actual_colors, zorder=2,
           label="Actual move (% |return|)")

    # Horizontal line at implied move average
    implied_avg = float(implied.mean())
    ax.axhline(implied_avg, color=COLORS["neutral"], linestyle="--", linewidth=1.5,
               label=f"Avg implied move ({implied_avg:.1f}%)")

    # Legend patches for actual bar coloring
    crush_patch = mpatches.Patch(color=COLORS["profit"], label="Actual < Implied (crush profit)")
    beat_patch  = mpatches.Patch(color=COLORS["loss"],   label="Actual > Implied (crush loss)")
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles=handles + [crush_patch, beat_patch], fontsize=8, loc="upper right")

    # Annotation: crush rate
    ax.annotate(
        f"Actual < Implied in ~{crush_count}/{n_events} events ({crush_count/n_events*100:.0f}%)",
        xy=(n_events - 1, implied_avg + 1.0),
        xytext=(n_events / 2, implied.max() + 1.5),
        arrowprops=dict(arrowstyle="->", color=COLORS["primary"], lw=1.2),
        color=COLORS["primary"], fontsize=9, ha="center",
    )

    # Data disclaimer
    ax.text(
        0.01, 0.97, "Illustrative synthetic data",
        transform=ax.transAxes, fontsize=8, color="#888888",
        va="top", ha="left", style="italic",
    )

    ax.set_xticks(x)
    ax.set_xticklabels(event_labels, fontsize=7, rotation=45, ha="right")
    ax.set_xlabel("Earnings Event", fontsize=11)
    ax.set_ylabel("Move (%)", fontsize=11)
    ax.set_title("Earnings: Implied Move vs Actual Move (20 Events)", fontsize=14, pad=12)
    ax.tick_params(labelsize=9)

    plt.tight_layout()
    plt.savefig(save_dir / "chart-earnings-move-vs-actual.png", dpi=DPI, bbox_inches="tight")
    plt.close(fig)


# ── 4. Superfly gamma — OTM butterfly value vs underlying at 4 time snapshots ─

def plot_superfly_gamma(save_dir: Path) -> None:
    """
    OTM call butterfly value vs underlying price at 4 time-to-expiry snapshots.

    Structure: buy 4950C, sell 2× 5000C, buy 5050C (call butterfly centered at 5000).
    Data source: synthetic/illustrative.
    Method: Black-Scholes pricing via scipy.stats.norm with IV=18%, r=4%.
    Four time snapshots before expiry: 240 min, 120 min, 60 min, 30 min.
    Shows gamma explosion — the value profile sharpens dramatically as expiry
    approaches (narrowing peak width is the manifestation of gamma risk).
    """
    S_range = np.linspace(4850, 5150, 600)

    K_low  = 4950.0
    K_mid  = 5000.0
    K_high = 5050.0

    r      = 0.04
    sigma  = 0.18
    # One trading day ≈ 6.5 hours = 390 minutes

    # Minutes to expiry for each scenario
    minutes_list  = [240, 120, 60, 30]
    T_list        = [m / (252 * 390) for m in minutes_list]  # fraction of year

    line_styles  = ["-", "--", "-.", ":"]
    line_colors  = [COLORS["primary"], COLORS["highlight"], COLORS["profit"], COLORS["loss"]]
    line_widths  = [2.5, 2.2, 2.0, 2.0]

    def bs_call(S: np.ndarray, K: float, r: float, sigma: float, T: float) -> np.ndarray:
        """Black-Scholes call price; handles T → 0 gracefully."""
        if T <= 0:
            return np.maximum(S - K, 0.0)
        d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)
        return S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)

    def butterfly_value(S: np.ndarray, K_l: float, K_m: float, K_h: float,
                        r: float, sigma: float, T: float) -> np.ndarray:
        """Long call butterfly: long K_l, short 2× K_m, long K_h."""
        return bs_call(S, K_l, r, sigma, T) - 2 * bs_call(S, K_m, r, sigma, T) + bs_call(S, K_h, r, sigma, T)

    fig, ax = plt.subplots(figsize=FIG_STANDARD)
    ax.set_facecolor(COLORS["bg"])
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    for T, minutes, ls, color, lw in zip(T_list, minutes_list, line_styles, line_colors, line_widths):
        fly_val = butterfly_value(S_range, K_low, K_mid, K_high, r, sigma, T)
        ax.plot(
            S_range, fly_val,
            color=color, linestyle=ls, linewidth=lw,
            label=f"{minutes} min to expiry",
        )

    # Strike reference lines
    for K, label in [(K_low, "4950"), (K_mid, "5000\n(body)"), (K_high, "5050")]:
        ax.axvline(K, color=COLORS["neutral"], linestyle=":", linewidth=0.9, alpha=0.7)
        ax.text(K, ax.get_ylim()[1] if ax.get_ylim()[1] > 0 else 5,
                label, ha="center", va="bottom", fontsize=7, color="#666666")

    ax.set_xlabel("SPX Underlying Price", fontsize=11)
    ax.set_ylabel("Butterfly Value ($)", fontsize=11)
    ax.set_title(
        "Superfly Gamma: OTM Butterfly Value vs Underlying\n"
        "Buy 4950C / Sell 2× 5000C / Buy 5050C — 4 Time Snapshots",
        fontsize=13, pad=12,
    )
    ax.legend(fontsize=10, loc="upper right")
    ax.tick_params(labelsize=9)
    ax.set_xlim(S_range[0], S_range[-1])

    # Annotation: sharpening peak = gamma explosion
    ax.annotate(
        "Peak sharpens as\nexpiry approaches\n(gamma explosion)",
        xy=(K_mid, butterfly_value(np.array([K_mid]), K_low, K_mid, K_high, r, sigma, T_list[-1])[0]),
        xytext=(K_mid + 55, butterfly_value(np.array([K_mid]), K_low, K_mid, K_high, r, sigma, T_list[-1])[0] * 0.7),
        arrowprops=dict(arrowstyle="->", color=COLORS["loss"], lw=1.4),
        color=COLORS["loss"], fontsize=9, ha="center",
    )

    plt.tight_layout()
    plt.savefig(save_dir / "chart-superfly-gamma.png", dpi=DPI, bbox_inches="tight")
    plt.close(fig)


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    save_dir = Path(__file__).parent / "outputs"
    save_dir.mkdir(exist_ok=True)

    plot_0dte_ivx_by_time(save_dir)
    plot_intraday_volume(save_dir)
    plot_earnings_move_vs_actual(save_dir)
    plot_superfly_gamma(save_dir)

    print("Generated 4 timing charts")


if __name__ == "__main__":
    main()
