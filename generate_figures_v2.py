#!/usr/bin/env python3
"""
Q1-Quality Figure Generator — v2 (3-year dataset, Jan 2022–Apr 2025)

Figures produced (300 DPI, colorblind-friendly):
  fig1_event_timeline.png          – monthly event count + cumulative
  fig2_seasonal_heatmap.png        – month × year heatmap of events
  fig3_economic_impact.png         – economic loss by year + top-10 plants
  fig4_model_roc_pr.png            – ROC and PR curves for H=6/12/24h
  fig5_feature_importance.png      – XGBoost feature importances (mean gain)
  fig6_sensitivity_heatmap.png     – threshold sensitivity (copy from figures/)
  fig7_event_magnitude_dist.png    – distribution of energy lost per event
  fig8_framework_schematic.png     – HCOT-MW 3-layer framework diagram
"""

import warnings
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings("ignore")

PROJECT = Path(__file__).parent
DATA_DIR = PROJECT / "data"
ANALYSIS_DIR = PROJECT / "analysis"
FIG_DIR = PROJECT / "figures"
FIG_DIR.mkdir(exist_ok=True)

DPI = 300
CB = ["#0072B2", "#E69F00", "#009E73", "#CC79A7", "#56B4E9", "#D55E00", "#F0E442"]

plt.rcParams.update({
    "font.size": 11, "axes.titlesize": 12, "axes.labelsize": 11,
    "xtick.labelsize": 9, "ytick.labelsize": 9, "legend.fontsize": 9,
    "figure.dpi": DPI, "savefig.dpi": DPI, "savefig.bbox": "tight",
    "font.family": "DejaVu Sans",
})


# ── helpers ────────────────────────────────────────────────────────────────────
def load_events():
    f = ANALYSIS_DIR / "cutoff_events_with_losses.csv"
    if not f.exists():
        raise FileNotFoundError(f"Run run_economic_analysis.py first: {f}")
    df = pd.read_csv(f, parse_dates=["datetime"])
    df["datetime"] = pd.to_datetime(df["datetime"], utc=True, errors="coerce")
    df["month"] = df["datetime"].dt.month
    df["year"] = df["datetime"].dt.year
    df["month_dt"] = df["datetime"].dt.to_period("M")
    return df


def savefig(name):
    p = FIG_DIR / name
    plt.savefig(p, dpi=DPI, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {p.name}")


# ── Fig 1: Monthly event count + cumulative ────────────────────────────────────
def fig1_timeline(ev):
    monthly = ev.groupby("month_dt").size().reset_index(name="n")
    monthly["month_dt"] = monthly["month_dt"].dt.to_timestamp()
    monthly = monthly.sort_values("month_dt")
    monthly["cumulative"] = monthly["n"].cumsum()

    fig, ax1 = plt.subplots(figsize=(12, 4))
    ax2 = ax1.twinx()

    ax1.bar(monthly["month_dt"], monthly["n"], width=20, color=CB[0], alpha=0.75, label="Events per month")
    ax2.plot(monthly["month_dt"], monthly["cumulative"], color=CB[1], lw=2, marker="o", ms=4, label="Cumulative events")

    ax1.set_xlabel("Month"); ax1.set_ylabel("Events per month", color=CB[0])
    ax2.set_ylabel("Cumulative events", color=CB[1])
    ax1.set_title("Hard cut-off events: monthly count and cumulative total (Jan 2022–Apr 2025)")
    ax1.tick_params(axis="x", rotation=45)

    lines1, labs1 = ax1.get_legend_handles_labels()
    lines2, labs2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labs1 + labs2, loc="upper left")
    plt.tight_layout()
    savefig("fig1_event_timeline.png")


# ── Fig 2: Month × Year heatmap ────────────────────────────────────────────────
def fig2_seasonal(ev):
    pivot = ev.pivot_table(index="month", columns="year", values="drop", aggfunc="count", fill_value=0)
    month_names = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

    fig, ax = plt.subplots(figsize=(7, 5))
    im = ax.imshow(pivot.values, cmap="YlOrRd", aspect="auto")
    ax.set_xticks(range(len(pivot.columns))); ax.set_xticklabels(pivot.columns)
    ax.set_yticks(range(len(pivot.index))); ax.set_yticklabels([month_names[m-1] for m in pivot.index])
    plt.colorbar(im, ax=ax, label="Number of events")
    for i in range(pivot.shape[0]):
        for j in range(pivot.shape[1]):
            ax.text(j, i, str(pivot.values[i, j]), ha="center", va="center", fontsize=9)
    ax.set_title("Hard cut-off events: month × year distribution")
    ax.set_xlabel("Year"); ax.set_ylabel("Month")
    plt.tight_layout()
    savefig("fig2_seasonal_heatmap.png")


# ── Fig 3: Economic impact ─────────────────────────────────────────────────────
def fig3_economic(ev):
    annual = ev.groupby("year").agg(
        total_usd=("total_loss_usd", "sum"),
        n_events=("drop", "count"),
    ).reset_index()

    by_plant = (
        ev.groupby("plant_name")["total_loss_usd"].sum()
        .nlargest(10).reset_index()
    )
    by_plant["total_loss_usd_K"] = by_plant["total_loss_usd"] / 1e3
    # truncate long names
    by_plant["short_name"] = by_plant["plant_name"].apply(lambda s: s[:18] if len(s) > 18 else s)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))

    # Annual bars
    bars = ax1.bar(annual["year"].astype(str), annual["total_usd"] / 1e3,
                   color=CB[:len(annual)], edgecolor="k", linewidth=0.6)
    for bar, n in zip(bars, annual["n_events"]):
        ax1.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 5,
                 f"n={n}", ha="center", va="bottom", fontsize=9)
    ax1.set_xlabel("Year"); ax1.set_ylabel("Total economic loss (USD thousand)")
    ax1.set_title("Annual direct market revenue loss")
    ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:.0f}K"))

    # Top-10 plant horizontal bars
    colors_p = [CB[0]] * 10; colors_p[0] = CB[5]
    ax2.barh(by_plant["short_name"][::-1], by_plant["total_loss_usd_K"][::-1],
             color=CB[0], edgecolor="k", linewidth=0.5)
    ax2.set_xlabel("Total economic loss (USD thousand)")
    ax2.set_title("Top 10 plants by direct revenue loss")

    plt.tight_layout()
    savefig("fig3_economic_impact.png")


# ── Fig 4: ROC + PR curves ─────────────────────────────────────────────────────
def fig4_roc_pr():
    """Load saved model probabilities and plot curves."""
    from sklearn.metrics import roc_curve, auc, precision_recall_curve, average_precision_score

    horizons = [6, 12, 24]
    results = {}
    for H in horizons:
        f = ANALYSIS_DIR / "models" / "v2" / f"xgb_H{H}_probs.csv"
        if f.exists():
            d = pd.read_csv(f)
            results[H] = d
        else:
            print(f"  Missing {f.name} — will regenerate from model")

    if not results:
        print("  No model probability files found, skipping fig4.")
        return

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    for i, H in enumerate(horizons):
        if H not in results:
            continue
        d = results[H]
        y_true, y_prob = d["y_true"], d["y_prob"]

        fpr, tpr, _ = roc_curve(y_true, y_prob)
        roc_auc = auc(fpr, tpr)
        ax1.plot(fpr, tpr, color=CB[i], lw=1.8, label=f"H={H}h (AUC={roc_auc:.3f})")

        prec, rec, _ = precision_recall_curve(y_true, y_prob)
        ap = average_precision_score(y_true, y_prob)
        ax2.plot(rec, prec, color=CB[i], lw=1.8, label=f"H={H}h (AP={ap:.3f})")

    ax1.plot([0, 1], [0, 1], "k--", lw=1, label="Random")
    ax1.set_xlabel("False Positive Rate"); ax1.set_ylabel("True Positive Rate")
    ax1.set_title("ROC curves — XGBoost early warning model"); ax1.legend()

    ax2.set_xlabel("Recall"); ax2.set_ylabel("Precision")
    ax2.set_title("Precision-Recall curves — XGBoost early warning model"); ax2.legend()

    plt.tight_layout()
    savefig("fig4_model_roc_pr.png")


# ── Fig 5: Feature importance ──────────────────────────────────────────────────
def fig5_feature_importance():
    import pickle
    horizons = [6, 12, 24]
    importances = {}
    feature_names = None

    for H in horizons:
        mp = ANALYSIS_DIR / "models" / "v2" / f"xgb_H{H}.pkl"
        if mp.exists():
            with open(mp, "rb") as fh:
                saved = pickle.load(fh)
            model = saved["model"] if isinstance(saved, dict) else saved
            scores = model.get_booster().get_score(importance_type="gain")
            importances[H] = scores
            if feature_names is None:
                feature_names = list(scores.keys())

    if not importances:
        print("  No model files found, skipping fig5.")
        return

    # union of features, mean gain across horizons
    all_feats = sorted(set(k for d in importances.values() for k in d))
    mean_gain = {f: np.mean([importances[H].get(f, 0) for H in horizons]) for f in all_feats}
    top_feats = sorted(mean_gain, key=mean_gain.get, reverse=True)[:15]

    fig, ax = plt.subplots(figsize=(9, 6))
    ys = range(len(top_feats))
    bars = ax.barh(ys, [mean_gain[f] for f in top_feats], color=CB[0], edgecolor="k", lw=0.5)
    ax.set_yticks(ys); ax.set_yticklabels(top_feats, fontsize=9)
    ax.invert_yaxis()
    ax.set_xlabel("Mean gain (averaged across H=6/12/24h)")
    ax.set_title("XGBoost feature importances — top 15 features")
    plt.tight_layout()
    savefig("fig5_feature_importance.png")


# ── Fig 7: Energy-lost distribution ───────────────────────────────────────────
def fig7_magnitude(ev):
    fig, ax = plt.subplots(figsize=(8, 5))
    bins = np.logspace(np.log10(ev["energy_lost_mwh"].min() + 0.1),
                       np.log10(ev["energy_lost_mwh"].max() + 1), 25)
    ax.hist(ev["energy_lost_mwh"], bins=bins, color=CB[0], edgecolor="k", lw=0.5, alpha=0.8)
    ax.set_xscale("log"); ax.set_xlabel("Energy lost per event (MWh, log scale)")
    ax.set_ylabel("Frequency")
    ax.set_title("Distribution of hard cut-off event magnitudes (Jan 2022–Apr 2025)")
    ax.axvline(ev["energy_lost_mwh"].median(), color=CB[1], lw=2, ls="--",
               label=f"Median: {ev['energy_lost_mwh'].median():.0f} MWh")
    ax.axvline(ev["energy_lost_mwh"].mean(), color=CB[5], lw=2, ls=":",
               label=f"Mean: {ev['energy_lost_mwh'].mean():.0f} MWh")
    ax.legend()
    plt.tight_layout()
    savefig("fig7_event_magnitude_dist.png")


# ── Fig 8: Framework schematic ─────────────────────────────────────────────────
def fig8_framework():
    fig, ax = plt.subplots(figsize=(11, 6))
    ax.set_xlim(0, 11); ax.set_ylim(0, 6); ax.axis("off")
    ax.set_facecolor("white")

    def box(x, y, w, h, label, sublabel="", color="#D6EAF8", fontsize=9):
        rect = mpatches.FancyBboxPatch((x, y), w, h,
                                       boxstyle="round,pad=0.1",
                                       facecolor=color, edgecolor="#2C3E50", lw=1.5)
        ax.add_patch(rect)
        ax.text(x + w / 2, y + h * 0.65, label, ha="center", va="center",
                fontsize=fontsize, fontweight="bold", wrap=True)
        if sublabel:
            ax.text(x + w / 2, y + h * 0.3, sublabel, ha="center", va="center",
                    fontsize=7.5, color="#555")

    def arrow(x1, y1, x2, y2):
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="->", color="#2C3E50", lw=1.5))

    # Layer 1 — Data
    ax.text(5.5, 5.55, "HCOT-MW Framework — Data → Detection → Analysis", ha="center",
            fontsize=12, fontweight="bold")
    box(0.3, 3.9, 3.2, 1.4, "Layer 1: Data",
        "EPİAŞ hourly generation\nERA5 reanalysis\nPTF market prices", color="#D6EAF8")

    # Layer 2 — Detection
    box(3.9, 3.9, 3.2, 1.4, "Layer 2: Detection",
        "Hard cut-off algorithm\n(θ_high/θ_low/θ_drop)\n249 events, 43 plants", color="#D5F5E3")

    # Layer 3 — Analysis
    box(7.5, 3.9, 3.2, 1.4, "Layer 3: Analysis",
        "Economic quantification\nSeasonal & spatial analysis\nXGBoost early warning", color="#FDEBD0")

    # Sub-boxes
    box(0.3, 0.5, 1.5, 2.8, "EPİAŞ\nAPI", "161 plants\nJan 2022–Apr 2025", color="#AED6F1")
    box(2.1, 0.5, 1.5, 2.8, "ERA5\nCDS API", "Surface & 100m\n0.25° × 0.25°", color="#AED6F1")
    box(3.9, 0.5, 1.5, 2.8, "Event\nDetector", "Python/pandas\nThreshold rules", color="#A9DFBF")
    box(5.7, 0.5, 1.5, 2.8, "Sensitivity\nAnalysis", "±20% grid\n125 combos", color="#A9DFBF")
    box(7.5, 0.5, 1.5, 2.8, "Economic\nImpact", "PTF prices\nUSD 1.6M", color="#FAD7A0")
    box(9.3, 0.5, 1.5, 2.8, "XGBoost\nWarning", "H=6/12/24h\nLeak-free", color="#FAD7A0")

    # Arrows
    for x1, x2 in [(1.9, 3.9), (3.7, 5.5), (5.5, 7.5)]:
        arrow(x1, 4.6, x2, 4.6)

    plt.tight_layout()
    savefig("fig8_framework_schematic.png")


if __name__ == "__main__":
    print("Loading events…")
    ev = load_events()
    print(f"  {len(ev)} events loaded")

    print("Fig 1: Event timeline…"); fig1_timeline(ev)
    print("Fig 2: Seasonal heatmap…"); fig2_seasonal(ev)
    print("Fig 3: Economic impact…"); fig3_economic(ev)
    print("Fig 4: ROC / PR curves…"); fig4_roc_pr()
    print("Fig 5: Feature importance…"); fig5_feature_importance()
    print("Fig 7: Magnitude distribution…"); fig7_magnitude(ev)
    print("Fig 8: Framework schematic…"); fig8_framework()

    print(f"\nAll figures saved to: {FIG_DIR}")
