"""
iv_charts.py — Implied Volatility Educational Charts
=====================================================
Generates 7 educational charts covering IV concepts:
  1. Theta decay curve (Black-Scholes theta vs DTE)
  2. IVR distribution histogram
  3. IV crush pattern around earnings
  4. IV term structure (normal vs stressed)
  5. Gamma explosion vs DTE (Black-Scholes gamma)
  6. Greeks quick-reference table
  7. IV compression coil and breakout

Usage:
    python iv_charts.py
"""

import sys
from pathlib import Path

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import norm

# Allow running from any CWD while importing sibling constants.py
sys.path.insert(0, str(Path(__file__).parent))
from constants import COLORS, DPI, FIG_STANDARD, FIG_WIDE, SPX_SPOT

# ── Standard Black-Scholes parameters ────────────────────────────────────────
S = SPX_SPOT   # 5 000
K = 5_000      # ATM strike
r = 0.04       # risk-free rate
sigma = 0.18   # implied volatility (~VIX 18)


def _bs_d1_d2(S: float, K: float, r: float, sigma: float, T: float):
    """Return (d1, d2) for Black-Scholes."""
    d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    return d1, d2


# ── 1. Theta decay curve ──────────────────────────────────────────────────────

def plot_theta_decay_curve(save_dir: Path) -> None:
    """
    Plot Black-Scholes theta of an ATM call vs DTE (90 → 1).

    Formula (per calendar day):
        theta = -(S * N'(d1) * sigma) / (2 * sqrt(T)) - r * K * exp(-r*T) * N(d2)
    where T = DTE / 365.
    """
    dte = np.arange(90, 0, -1)
    T = dte / 365.0

    d1, d2 = _bs_d1_d2(S, K, r, sigma, T)
    n_prime_d1 = norm.pdf(d1)
    N_d2 = norm.cdf(d2)

    # Annualised theta → daily theta (divide by 365)
    theta_annual = (
        -(S * n_prime_d1 * sigma) / (2 * np.sqrt(T))
        - r * K * np.exp(-r * T) * N_d2
    )
    theta_daily = theta_annual / 365.0

    fig, ax = plt.subplots(figsize=FIG_STANDARD)
    ax.set_facecolor(COLORS["bg"])
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # Main theta curve
    ax.plot(dte, theta_daily, color=COLORS["primary"], linewidth=2.5,
            label="Daily Theta (ATM call)")

    # Sweet-spot zone 21–45 DTE
    zone_mask = (dte >= 21) & (dte <= 45)
    ax.fill_between(dte, theta_daily, where=zone_mask,
                    color=COLORS["warning"], alpha=0.30, label="Sweet-spot entry zone (21–45 DTE)")
    ax.axvline(21,  color=COLORS["warning"], linestyle="--", linewidth=1.2)
    ax.axvline(45,  color=COLORS["warning"], linestyle="--", linewidth=1.2)
    ax.annotate(
        "Sweet-spot\n21–45 DTE",
        xy=(33, theta_daily[np.where(dte == 33)[0][0]]),
        xytext=(50, theta_daily[np.where(dte == 33)[0][0]] * 0.6),
        arrowprops=dict(arrowstyle="->", color=COLORS["warning"]),
        color=COLORS["warning"], fontsize=9, ha="center",
    )

    ax.set_xlabel("Days to Expiration (DTE)", fontsize=11)
    ax.set_ylabel("Daily Theta ($ per contract per day)", fontsize=11)
    ax.set_title("Theta Decay: ATM Option — Daily Theta vs DTE", fontsize=14, pad=12)
    ax.invert_xaxis()   # left = many DTE, right = expiry
    ax.legend(fontsize=10)
    ax.tick_params(labelsize=9)

    plt.tight_layout()
    plt.savefig(save_dir / "chart-theta-decay-curve.png", dpi=DPI, bbox_inches="tight")
    plt.close(fig)


# ── 2. IVR distribution histogram ────────────────────────────────────────────

def plot_ivr_distribution(save_dir: Path) -> None:
    """
    Histogram of simulated IVR values for a 50-stock universe.

    IVR = (current_IV - 52w_low) / (52w_high - 52w_low) * 100
    Simulated with a beta distribution (alpha=2, beta=2) scaled to 0–100.
    """
    rng = np.random.default_rng(seed=42)
    ivr_values = rng.beta(2, 2, size=200) * 100   # 200 observations, IVR 0–100

    bins = np.arange(0, 105, 5)   # 5-point bins

    fig, ax = plt.subplots(figsize=FIG_STANDARD)
    ax.set_facecolor(COLORS["bg"])
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # Color each bin according to IVR zone
    counts, edges = np.histogram(ivr_values, bins=bins)
    for left, right, count in zip(edges[:-1], edges[1:], counts):
        midpoint = (left + right) / 2
        if midpoint < 30:
            color = COLORS["loss"]
        elif midpoint < 50:
            color = COLORS["neutral"]
        elif midpoint < 75:
            color = COLORS["warning"]
        else:
            color = COLORS["profit"]
        ax.bar(left, count, width=right - left, color=color, edgecolor="white",
               linewidth=0.8, align="edge")

    # Zone vertical lines
    ax.axvline(30, color=COLORS["neutral"], linestyle="--", linewidth=1.5, label="IVR = 30")
    ax.axvline(50, color=COLORS["primary"], linestyle="--", linewidth=1.5, label="IVR = 50")
    ax.axvline(75, color=COLORS["profit"],  linestyle="--", linewidth=1.5, label="IVR = 75")

    # Zone labels
    ax.text(15, counts.max() * 0.92, "Low IV\n(avoid selling)", ha="center",
            color=COLORS["loss"], fontsize=8)
    ax.text(40, counts.max() * 0.92, "Neutral",   ha="center",
            color=COLORS["neutral"], fontsize=8)
    ax.text(62, counts.max() * 0.92, "Elevated",  ha="center",
            color=COLORS["warning"], fontsize=8)
    ax.text(87, counts.max() * 0.92, "High IV\n(sell premium)", ha="center",
            color=COLORS["profit"], fontsize=8)

    # Legend patches
    patches = [
        mpatches.Patch(color=COLORS["loss"],    label="IVR < 30  — low"),
        mpatches.Patch(color=COLORS["neutral"], label="30–50   — neutral"),
        mpatches.Patch(color=COLORS["warning"], label="50–75   — elevated"),
        mpatches.Patch(color=COLORS["profit"],  label="> 75    — high"),
    ]
    ax.legend(handles=patches, fontsize=9, loc="upper left")

    ax.set_xlabel("IV Rank (IVR %)", fontsize=11)
    ax.set_ylabel("Count", fontsize=11)
    ax.set_title("IVR Distribution — 50-Stock Universe (simulated)", fontsize=14, pad=12)
    ax.set_xlim(0, 100)
    ax.tick_params(labelsize=9)

    plt.tight_layout()
    plt.savefig(save_dir / "chart-ivr-distribution.png", dpi=DPI, bbox_inches="tight")
    plt.close(fig)


# ── 3. IV crush pattern ───────────────────────────────────────────────────────

def plot_iv_crush_pattern(save_dir: Path) -> None:
    """
    Simulated ATM IV trajectory over 30 days centred on an earnings date.

    Phases:
      - Days -15 to -2: gradual IV build-up (linear ramp)
      - Day -1: IV spikes to peak
      - Day 0 (earnings): IV crushes 40–60%
      - Days 1 to 14: slow mean-reversion
    """
    rng = np.random.default_rng(seed=7)

    days = np.arange(-15, 16)    # -15 to +15 relative to earnings
    earnings_day = 0

    # Pre-earnings ramp
    base_iv = 20.0
    pre_mask  = days < 0
    post_mask = days > 0

    iv = np.zeros(len(days))
    # Day 0 (index 15 since days start at -15)
    earnings_idx = np.where(days == 0)[0][0]

    # Pre-earnings: linear ramp + small noise
    iv[pre_mask] = (
        base_iv
        + np.linspace(0, 22, pre_mask.sum())
        + rng.normal(0, 0.8, pre_mask.sum())
    )
    # Day -1 spike: highest point
    iv[earnings_idx - 1] = iv[pre_mask][-1] + 8.0

    # Earnings day: crush 50%
    iv[earnings_idx] = iv[earnings_idx - 1] * 0.50

    # Post-earnings: slow recovery toward base
    post_start = iv[earnings_idx]
    iv[post_mask] = (
        post_start
        + np.linspace(0, base_iv * 0.7, post_mask.sum())
        + rng.normal(0, 0.5, post_mask.sum())
    )

    fig, ax = plt.subplots(figsize=FIG_STANDARD)
    ax.set_facecolor(COLORS["bg"])
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    ax.plot(days, iv, color=COLORS["primary"], linewidth=2.5, label="ATM IV (%)")

    # Earnings vertical line
    ax.axvline(earnings_day, color=COLORS["loss"], linestyle="--", linewidth=1.8,
               label="Earnings announcement")

    # IV crush annotation
    crush_x = 1
    crush_y = iv[earnings_idx + 1]
    peak_y  = iv[earnings_idx - 1]
    ax.annotate(
        "IV crush\n(−40–60%)",
        xy=(crush_x, crush_y),
        xytext=(5, crush_y + 12),
        arrowprops=dict(arrowstyle="->", color=COLORS["loss"]),
        color=COLORS["loss"], fontsize=9, ha="center",
    )

    ax.set_xlabel("Days Relative to Earnings (0 = announcement)", fontsize=11)
    ax.set_ylabel("ATM Implied Volatility (%)", fontsize=11)
    ax.set_title("IV Crush Pattern Around Earnings", fontsize=14, pad=12)
    ax.legend(fontsize=10)
    ax.tick_params(labelsize=9)

    plt.tight_layout()
    plt.savefig(save_dir / "chart-iv-crush-pattern.png", dpi=DPI, bbox_inches="tight")
    plt.close(fig)


# ── 4. IV term structure ──────────────────────────────────────────────────────

def plot_iv_term_structure(save_dir: Path) -> None:
    """
    Two ATM IV term structure curves:
      - Normal (contango):  short-dated IV < long-dated IV
      - Inverted/Stressed:  short-dated IV > long-dated IV (fear premium in front month)
    """
    expirations = np.array([7, 14, 21, 30, 45, 60, 90])   # DTE

    # Normal: modest upward slope starting from ~16% at 7 DTE
    iv_normal = np.array([16.0, 17.0, 17.8, 18.5, 19.2, 19.8, 20.5])

    # Stressed/inverted: front-month premium, flattening further out
    iv_stressed = np.array([32.0, 30.0, 28.5, 27.0, 25.5, 24.5, 23.5])

    fig, ax = plt.subplots(figsize=FIG_STANDARD)
    ax.set_facecolor(COLORS["bg"])
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    ax.plot(expirations, iv_normal,   color=COLORS["primary"], linewidth=2.5,
            marker="o", markersize=7, label="Normal (contango)")
    ax.plot(expirations, iv_stressed, color=COLORS["loss"],    linewidth=2.5,
            marker="s", markersize=7, linestyle="--", label="Inverted / Stressed")

    ax.fill_between(expirations, iv_normal, iv_stressed,
                    where=(iv_stressed > iv_normal),
                    color=COLORS["loss"], alpha=0.12, label="Inversion premium")

    ax.set_xticks(expirations)
    ax.set_xticklabels([f"{d}d" for d in expirations], fontsize=9)
    ax.set_xlabel("Days to Expiration (DTE)", fontsize=11)
    ax.set_ylabel("ATM Implied Volatility (%)", fontsize=11)
    ax.set_title("IV Term Structure: Normal vs. Inverted/Stressed", fontsize=14, pad=12)
    ax.legend(fontsize=10)
    ax.tick_params(labelsize=9)

    plt.tight_layout()
    plt.savefig(save_dir / "chart-iv-term-structure.png", dpi=DPI, bbox_inches="tight")
    plt.close(fig)


# ── 5. Gamma vs DTE ───────────────────────────────────────────────────────────

def plot_gamma_vs_dte(save_dir: Path) -> None:
    """
    Black-Scholes gamma of an ATM option vs DTE (90 → 1).

    Formula:
        gamma = N'(d1) / (S * sigma * sqrt(T))
    where T = DTE / 365.
    Gamma explodes as DTE → 0 because sqrt(T) → 0 in the denominator.
    """
    dte = np.arange(90, 0, -1)
    T = dte / 365.0

    d1, _ = _bs_d1_d2(S, K, r, sigma, T)
    n_prime_d1 = norm.pdf(d1)

    gamma = n_prime_d1 / (S * sigma * np.sqrt(T))

    fig, ax = plt.subplots(figsize=FIG_STANDARD)
    ax.set_facecolor(COLORS["bg"])
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    ax.plot(dte, gamma, color=COLORS["primary"], linewidth=2.5, label="ATM Gamma")

    # Gamma explosion zone (last 7 DTE)
    explosion_mask = dte <= 7
    ax.fill_between(dte, gamma, where=explosion_mask,
                    color=COLORS["loss"], alpha=0.30)

    # Annotation with arrow
    exp_dte   = 4
    exp_gamma = gamma[np.where(dte == exp_dte)[0][0]]
    ax.annotate(
        "Gamma explosion\nzone (≤ 7 DTE)",
        xy=(exp_dte, exp_gamma),
        xytext=(25, exp_gamma * 0.85),
        arrowprops=dict(arrowstyle="->", color=COLORS["loss"]),
        color=COLORS["loss"], fontsize=9, ha="center",
    )

    ax.set_xlabel("Days to Expiration (DTE)", fontsize=11)
    ax.set_ylabel("Gamma (Δ per $1 move per contract unit)", fontsize=11)
    ax.set_title("Gamma vs DTE: ATM Option — Explosion Near Expiry", fontsize=14, pad=12)
    ax.invert_xaxis()
    ax.legend(fontsize=10)
    ax.tick_params(labelsize=9)

    plt.tight_layout()
    plt.savefig(save_dir / "chart-gamma-vs-dte.png", dpi=DPI, bbox_inches="tight")
    plt.close(fig)


# ── 6. Greeks quick-reference table ──────────────────────────────────────────

def plot_greeks_sensitivity(save_dir: Path) -> None:
    """
    Styled matplotlib table: Greeks quick reference.

    Columns: Greek | Measures | High = | Low = | Key Decision
    Rows: Delta, Gamma, Theta, Vega, Rho
    Alternating row colors using COLORS['bg'] and white.
    """
    columns = ["Greek", "Measures", "High value =", "Low value =", "Key Decision"]
    rows = [
        ["Delta (Δ)",  "Directional\nexposure",      "Moves like stock",       "Minimal direction\nbias",    "Hedge with\nshares/futures"],
        ["Gamma (Γ)",  "Rate of Δ change\nvs price",  "Δ unstable;\nrisk near expiry", "Stable Δ;\nfar from expiry", "Avoid short gamma\n< 7 DTE"],
        ["Theta (Θ)",  "Time decay\n($/day)",          "Collect premium\nquickly",  "Slow decay;\nlong time value", "Sell 21–45 DTE\nfor theta"],
        ["Vega (ν)",   "IV sensitivity\n(per 1% IV)",  "Profits if IV rises",    "Profits if IV falls",     "Match IVR to\nvega exposure"],
        ["Rho (ρ)",    "Interest rate\nsensitivity",   "Calls benefit\nfrom ↑ rates", "Puts benefit\nfrom ↓ rates", "Matters for\nLEAPS only"],
    ]

    fig, ax = plt.subplots(figsize=FIG_WIDE)
    ax.axis("off")
    ax.set_facecolor(COLORS["bg"])

    # Alternating row colors
    cell_colors = []
    for i in range(len(rows)):
        row_color = COLORS["bg"] if i % 2 == 0 else "#FFFFFF"
        cell_colors.append([row_color] * len(columns))

    # Header row color
    header_colors = [COLORS["primary"]] * len(columns)

    tbl = ax.table(
        cellText=rows,
        colLabels=columns,
        cellLoc="center",
        loc="center",
        cellColours=cell_colors,
    )

    # Style header
    for col_idx in range(len(columns)):
        header_cell = tbl[0, col_idx]
        header_cell.set_facecolor(COLORS["primary"])
        header_cell.set_text_props(color="white", fontweight="bold", fontsize=10)

    # Style all data cells
    for row_idx in range(1, len(rows) + 1):
        for col_idx in range(len(columns)):
            cell = tbl[row_idx, col_idx]
            cell.set_text_props(fontsize=9)
            cell.set_edgecolor("#E0E0E0")
            if col_idx == 0:
                cell.set_text_props(fontweight="bold", fontsize=9)

    tbl.auto_set_font_size(False)
    tbl.scale(1, 2.6)   # stretch rows for wrapped text

    ax.set_title("Greeks Quick Reference", fontsize=14, pad=18, fontweight="bold")
    fig.patch.set_facecolor(COLORS["bg"])

    plt.tight_layout()
    plt.savefig(save_dir / "chart-greeks-sensitivity.png", dpi=DPI, bbox_inches="tight")
    plt.close(fig)


# ── 7. IV compression coil ────────────────────────────────────────────────────

def plot_iv_compression_coil(save_dir: Path) -> None:
    """
    IVR over 60 days:
      - Days 0–39: compression (IVR falls from 65 → 20)
      - Days 40–59: sharp expansion (IVR rises from 20 → 70)

    Annotate the "entry signal zone" (IVR low, about to expand) with
    a shaded rectangle and an arrow labelled "IV coil — watch for breakout".
    """
    rng = np.random.default_rng(seed=13)

    days = np.arange(60)

    # Compression phase: 0–39
    compress = np.linspace(65, 20, 40) + rng.normal(0, 1.5, 40)
    # Expansion phase: 40–59
    expand   = np.linspace(20, 70, 20) + rng.normal(0, 2.0, 20)

    ivr = np.concatenate([compress, expand])

    fig, ax = plt.subplots(figsize=FIG_STANDARD)
    ax.set_facecolor(COLORS["bg"])
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    ax.plot(days, ivr, color=COLORS["primary"], linewidth=2.5, label="IVR (%)")

    # Entry signal zone: days 33–42, IVR 15–30
    entry_rect = mpatches.FancyBboxPatch(
        (33, 12), 12, 20,
        boxstyle="round,pad=0.5",
        linewidth=1.5,
        edgecolor=COLORS["profit"],
        facecolor=COLORS["profit"],
        alpha=0.18,
        label="Entry signal zone",
    )
    ax.add_patch(entry_rect)

    # Arrow + label: IV coil
    ax.annotate(
        "IV coil —\nwatch for breakout",
        xy=(42, ivr[42]),
        xytext=(50, 50),
        arrowprops=dict(arrowstyle="->", color=COLORS["profit"], lw=1.5),
        color=COLORS["profit"], fontsize=9, ha="center", fontweight="bold",
    )

    # Zone label inside rectangle
    ax.text(39, 22, "Entry\nsignal zone", ha="center", va="bottom",
            color=COLORS["profit"], fontsize=8, fontweight="bold")

    # Reference lines
    ax.axhline(30, color=COLORS["neutral"], linestyle=":", linewidth=1.2,
               label="IVR = 30 threshold")
    ax.axhline(50, color=COLORS["warning"], linestyle=":", linewidth=1.2,
               label="IVR = 50 threshold")

    ax.set_xlabel("Day", fontsize=11)
    ax.set_ylabel("IV Rank (IVR %)", fontsize=11)
    ax.set_title("IV Compression Coil: Build-Up and Breakout", fontsize=14, pad=12)
    ax.set_ylim(0, 85)
    ax.legend(fontsize=9, loc="upper right")
    ax.tick_params(labelsize=9)

    plt.tight_layout()
    plt.savefig(save_dir / "chart-iv-compression-coil.png", dpi=DPI, bbox_inches="tight")
    plt.close(fig)


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    save_dir = Path(__file__).parent / "outputs"
    save_dir.mkdir(exist_ok=True)

    plot_theta_decay_curve(save_dir)
    plot_ivr_distribution(save_dir)
    plot_iv_crush_pattern(save_dir)
    plot_iv_term_structure(save_dir)
    plot_gamma_vs_dte(save_dir)
    plot_greeks_sensitivity(save_dir)
    plot_iv_compression_coil(save_dir)

    print(f"Generated 7 IV charts in {save_dir}")


if __name__ == "__main__":
    main()
