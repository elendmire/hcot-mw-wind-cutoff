#!/usr/bin/env python3
"""
Q1-Quality Figure Generator — Full Suite
=========================================
8 main figures for HCOT-MW paper (Renewable Energy / Applied Energy / Energy Conv. & Mgmt.)
All figures: 300 DPI, Wong (2011) colorblind-friendly palette, Times New Roman / DejaVu Sans

Figure list (with article placement):
  Fig 1 — Study area map + wind farm vulnerability bubbles    [Section 2.1]
  Fig 2 — HCOT-MW framework diagram                          [Section 2, intro]
  Fig 3 — Cut-off event detection exemplar (SAROS RES)       [Section 2.3]
  Fig 4 — Three-year event statistics (4-panel)              [Section 3.1]
  Fig 5 — Spatial vulnerability (province bubble map)        [Section 3.1]
  Fig 6 — 16 March 2025 storm day (concurrent shutdowns)     [Section 3.1 / 2.4]
  Fig 7 — Economic impact (3-panel)                          [Section 3.2]
  Fig 8 — Model performance (ROC + PR + feature imp + calib) [Section 3.3]
  Fig S2 — Threshold sensitivity heatmap                     [Supplementary]
"""

import warnings
warnings.filterwarnings("ignore")
from pathlib import Path
import pickle

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec
import matplotlib.colors as mcolors
import matplotlib.ticker as ticker
from matplotlib.lines import Line2D
import numpy as np
import pandas as pd

# ── project paths ──────────────────────────────────────────────────────────────
PROJECT   = Path(__file__).parent
DATA_DIR  = PROJECT / "data"
ANAL_DIR  = PROJECT / "analysis"
FIG_DIR   = PROJECT / "figures"
FIG_DIR.mkdir(exist_ok=True)

# ── global style ───────────────────────────────────────────────────────────────
DPI = 300
# Wong (2011) colorblind-friendly palette
CB  = ["#0072B2","#E69F00","#009E73","#CC79A7","#56B4E9","#D55E00","#F0E442","#000000"]
GRAY = "#888888"
LIGHT_BLUE = "#D6EAF8"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 10,
    "axes.titlesize": 11,
    "axes.labelsize": 10,
    "xtick.labelsize": 8.5,
    "ytick.labelsize": 8.5,
    "legend.fontsize": 8.5,
    "axes.linewidth": 0.8,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "figure.dpi": DPI,
    "savefig.dpi": DPI,
    "savefig.bbox": "tight",
    "savefig.facecolor": "white",
})

# ── known wind farm province coordinates (deg N / deg E) ──────────────────────
PLANT_COORDS = {
    # plant_name_fragment: (lat, lon, province_label)
    "SAROS":        (40.60, 26.50, "Çanakkale"),
    "EVRENCİK":     (41.45, 27.85, "Kırklareli"),
    "KIYIKÖY":      (41.63, 28.08, "Kırklareli"),
    "TATLIPINAR":   (40.00, 27.00, "Balıkesir"),
    "GÜLPINAR":     (39.53, 26.10, "Çanakkale"),
    "İSTANBUL":     (41.15, 28.90, "İstanbul"),
    "TAŞPINAR":     (41.10, 28.85, "İstanbul"),
    "GÖKTEPE":      (40.65, 29.40, "Yalova"),
    "ZONGULDAK":    (40.73, 30.40, "Sakarya"),
    "ADAPAZARI":    (40.78, 30.39, "Sakarya"),
    "ÜÇPINAR":      (40.05, 27.50, "Balıkesir"),
    "BOZÜYÜK":      (39.90, 30.03, "Bilecik"),
    "YAHYALI":      (38.10, 35.37, "Kayseri"),
    "SOMA":         (39.19, 27.61, "Manisa"),
    "KOCATEPE":     (38.45, 27.20, "İzmir"),
    "BAĞLAR":       (40.40, 29.30, "Kocaeli"),
    "KARABURUN":    (38.62, 26.50, "İzmir"),
    "KAYACIK":      (39.05, 26.90, "Balıkesir"),
    "BANDIRMA":     (40.35, 28.00, "Balıkesir"),
    "BERGAMA":      (39.12, 27.18, "İzmir"),
    "GELIBOLU":     (40.45, 26.70, "Çanakkale"),
    "ÇEŞME":        (38.32, 26.30, "İzmir"),
    "AKBÜK":        (37.35, 27.28, "Muğla"),
    "AKDAĞ":        (38.73, 27.85, "Manisa"),
    "AKKUŞ":        (40.80, 37.02, "Ordu"),
    "GÜZELYURT":    (38.25, 33.57, "Aksaray"),
    "KANGAL":       (39.19, 37.40, "Sivas"),
}

def get_plant_coord(plant_name):
    pn = plant_name.upper()
    for k, v in PLANT_COORDS.items():
        if k in pn:
            return v[0], v[1], v[2]
    # fallback: western Turkey centroid
    return 39.8, 28.5, "Turkey"

# ── helpers ────────────────────────────────────────────────────────────────────
def savefig(name, fig=None):
    p = FIG_DIR / name
    (fig or plt).savefig(p, dpi=DPI, bbox_inches="tight", facecolor="white")
    plt.close("all")
    print(f"  ✓ {name}")

def load_events():
    f = ANAL_DIR / "cutoff_events_with_losses.csv"
    df = pd.read_csv(f, parse_dates=["datetime"])
    df["datetime"] = pd.to_datetime(df["datetime"], utc=True, errors="coerce")
    df["month"] = df["datetime"].dt.month
    df["year"]  = df["datetime"].dt.year
    df["hour"]  = df["datetime"].dt.hour
    df["month_dt"] = df["datetime"].dt.to_period("M")
    return df

def load_generation(plant_name=None):
    f = DATA_DIR / "generation_202201_202504.csv"
    df = pd.read_csv(f, parse_dates=["date"])
    df["datetime"] = pd.to_datetime(df["date"], utc=True, errors="coerce")
    df["gen_mw"]   = pd.to_numeric(df["ruzgar"], errors="coerce").fillna(0)
    df = df[["datetime", "plant_name", "gen_mw"]]
    if plant_name:
        df = df[df["plant_name"].str.upper().str.contains(plant_name.upper())]
    return df


# ══════════════════════════════════════════════════════════════════════════════
# FIGURE 1 — Study Area Map
# ══════════════════════════════════════════════════════════════════════════════
def fig1_study_area(ev):
    try:
        import geopandas as gpd
        world = gpd.read_file(
            "https://naciscdn.org/naturalearth/110m/cultural/ne_110m_admin_0_countries.zip"
        )
        turkey = world[world["NAME"] == "Turkey"]
        neighbors = world[world["NAME"].isin(
            ["Greece","Bulgaria","Georgia","Armenia","Syria","Iraq","Iran"]
        )]
        has_geo = True
    except Exception:
        has_geo = False
        print("  geopandas unavailable, using outline-only map")

    # Build plant stats
    plant_ev = ev.groupby("plant_name").agg(
        n_events=("drop","count"),
        energy_loss=("energy_lost_mwh","sum"),
        econ_loss=("total_loss_usd","sum"),
    ).reset_index()
    plant_ev["lat"] = plant_ev["plant_name"].apply(lambda p: get_plant_coord(p)[0])
    plant_ev["lon"] = plant_ev["plant_name"].apply(lambda p: get_plant_coord(p)[1])

    fig, ax = plt.subplots(figsize=(11, 6))

    if has_geo:
        turkey.plot(ax=ax, color="#F5F5DC", edgecolor="#555", linewidth=0.8, zorder=1)
        neighbors.plot(ax=ax, color="#E8E8E8", edgecolor="#AAA", linewidth=0.5, zorder=0)
    else:
        ax.set_facecolor("#D0E4F4")

    # WRF domain box (approx)
    wrf_box = plt.Polygon(
        [(25.5, 38.5),(32.5, 38.5),(32.5, 42.5),(25.5, 42.5)],
        fill=False, edgecolor=CB[5], linewidth=2, linestyle="--", zorder=4,
        label="WRF domain (3 km)"
    )
    ax.add_patch(wrf_box)

    # Scatter events
    norm = mcolors.Normalize(vmin=0, vmax=plant_ev["n_events"].max())
    cmap = plt.cm.YlOrRd
    scatter = ax.scatter(
        plant_ev["lon"], plant_ev["lat"],
        s=plant_ev["n_events"] * 12 + 20,
        c=plant_ev["n_events"], cmap=cmap, norm=norm,
        edgecolors="k", linewidths=0.5, zorder=5, alpha=0.85
    )

    # Annotate top plants
    top5 = plant_ev.nlargest(5, "n_events")
    for _, row in top5.iterrows():
        short = row["plant_name"].replace(" RES","").replace(" RES(BAK)","")[:12]
        ax.annotate(
            f"{short}\n({int(row['n_events'])})",
            xy=(row["lon"], row["lat"]),
            xytext=(row["lon"] + 0.4, row["lat"] + 0.4),
            fontsize=7, ha="left",
            arrowprops=dict(arrowstyle="-", color="#444", lw=0.6),
            zorder=6
        )

    # Colorbar
    cbar = plt.colorbar(scatter, ax=ax, pad=0.02, fraction=0.025)
    cbar.set_label("Number of cut-off events", fontsize=9)

    # Region labels
    for txt, x, y in [
        ("THRACE", 27.0, 41.8), ("MARMARA", 29.2, 40.5),
        ("AEGEAN", 27.0, 38.7), ("CENTRAL\nANATOLIA", 35.5, 38.5),
    ]:
        ax.text(x, y, txt, fontsize=8, color="#333", fontstyle="italic",
                ha="center", va="center", alpha=0.7, zorder=3)

    ax.set_xlim(25.5, 45)
    ax.set_ylim(35.5, 43)
    ax.set_xlabel("Longitude (°E)", fontsize=9)
    ax.set_ylabel("Latitude (°N)", fontsize=9)
    ax.set_title(
        "Figure 1. Study area: licensed wind power plants in Turkey with hard cut-off event frequency\n"
        "(Jan 2022–Apr 2025). Bubble size and colour indicate number of events per plant. "
        "Dashed box: WRF simulation domain.",
        fontsize=9, loc="left", pad=8
    )
    ax.legend(loc="lower right", fontsize=8)
    ax.grid(True, alpha=0.25, linewidth=0.5)
    plt.tight_layout()
    savefig("Fig1_study_area.png")


# ══════════════════════════════════════════════════════════════════════════════
# FIGURE 2 — HCOT-MW Framework (improved)
# ══════════════════════════════════════════════════════════════════════════════
def fig2_framework():
    fig, ax = plt.subplots(figsize=(13, 7))
    ax.set_xlim(0, 13); ax.set_ylim(0, 7)
    ax.axis("off")

    # ── colour palette ──
    L1C, L2C, L3C = "#AED6F1", "#A9DFBF", "#FAD7A0"
    HC = "#2C3E50"; TXT = "#1A1A2E"

    def rbox(ax, x, y, w, h, title, lines=None, fc="#EEF", radius=0.2, fontsize=9):
        p = mpatches.FancyBboxPatch((x, y), w, h,
            boxstyle=f"round,pad={radius}",
            facecolor=fc, edgecolor=HC, linewidth=1.4, zorder=3)
        ax.add_patch(p)
        ax.text(x + w/2, y + h*0.72, title,
                ha="center", va="center", fontsize=fontsize,
                fontweight="bold", color=TXT, zorder=4)
        if lines:
            ax.text(x + w/2, y + h*0.32, lines,
                    ha="center", va="center", fontsize=7.5,
                    color="#444", zorder=4, linespacing=1.4)

    def arrow(ax, x1, y1, x2, y2, label=""):
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
            arrowprops=dict(arrowstyle="-|>", color=HC, lw=1.5, mutation_scale=14),
            zorder=5)
        if label:
            mx, my = (x1+x2)/2, (y1+y2)/2
            ax.text(mx, my+0.12, label, ha="center", fontsize=7, color=HC)

    # Title
    ax.text(6.5, 6.72, "HCOT-MW Framework — Hard Cutoff Observatory for Turkish Wind Farms",
            ha="center", fontsize=13, fontweight="bold", color=TXT)

    # ── Layer headers ──
    for xi, label, fc in [
        (0.3, "LAYER 1\nDATA", L1C),
        (4.5, "LAYER 2\nDETECTION", L2C),
        (9.0, "LAYER 3\nANALYSIS & FORECAST", L3C),
    ]:
        ax.add_patch(mpatches.FancyBboxPatch((xi, 5.2), 3.6, 1.2,
            boxstyle="round,pad=0.15", facecolor=fc, edgecolor=HC, lw=1.6, zorder=3))
        ax.text(xi+1.8, 5.82, label, ha="center", va="center",
                fontsize=10, fontweight="bold", color=TXT, zorder=4)

    # ── Layer 1: Data boxes ──
    rbox(ax, 0.3, 2.3, 1.7, 2.5, "EPİAŞ\nAPI",
         "161 plants\nHourly gen.\nJan 2022–Apr 2025\nPTF prices", L1C)
    rbox(ax, 2.2, 2.3, 1.7, 2.5, "ERA5\nReanalysis",
         "ECMWF 0.25°\n100m + 10m wind\nMSLP, T₂ₘ\n2022–2025", L1C)

    # ── Layer 2: Detection ──
    rbox(ax, 4.5, 2.3, 3.6, 2.5, "Hard Cut-off\nDetector",
         "θ_high > 50 MW\nθ_low < 10 MW\nθ_drop > 80%\n→ 249 events / 43 plants\n→ 16,121 MWh lost", L2C)

    # ── Layer 3: Analysis ──
    rbox(ax, 9.0, 3.5, 3.7, 1.3, "Economic\nQuantification",
         "Actual PTF prices\nUSD 1.60 M total loss", L3C)
    rbox(ax, 9.0, 2.0, 3.7, 1.3, "Spatial &\nTemporal Analysis",
         "Province clustering\nSeasonality, CVI", L3C)
    rbox(ax, 9.0, 0.5, 3.7, 1.3, "XGBoost\nEarly Warning",
         "H=6/12/24h • Leakage-free\nROC-AUC 0.55–0.59", L3C)

    # ── Arrows ──
    arrow(ax, 2.0, 3.55, 4.5, 3.55, "hourly data")
    arrow(ax, 3.9, 3.55, 4.5, 3.55)
    arrow(ax, 8.1, 4.20, 9.0, 4.15)
    arrow(ax, 8.1, 3.55, 9.0, 2.65)
    arrow(ax, 8.1, 2.90, 9.0, 1.15)

    # ── WRF side box ──
    rbox(ax, 0.3, 0.3, 3.6, 1.6, "WRF Mesoscale\nSimulation",
         "ERA5 → WRF 3 km\n2-domain nesting\nSynoptic context\nfor extreme events", "#E8DAEF")
    arrow(ax, 2.0, 2.3, 2.0, 1.9)
    arrow(ax, 3.9, 1.1, 4.5, 2.5)

    # ── Legend ──
    for xi, label, fc in [(0.3, "Data", L1C), (1.5, "Detection", L2C),
                           (2.7, "Analysis", L3C), (3.9, "Modelling", "#E8DAEF")]:
        ax.add_patch(mpatches.FancyBboxPatch((xi, -0.05), 1.0, 0.28,
            boxstyle="round,pad=0.05", facecolor=fc, edgecolor=HC, lw=0.8, zorder=3))
        ax.text(xi+0.5, 0.09, label, ha="center", fontsize=7.5, color=TXT, zorder=4)
    ax.text(0.0, 0.09, "Legend:", fontsize=7.5, color=TXT)

    plt.tight_layout()
    savefig("Fig2_framework.png")


# ══════════════════════════════════════════════════════════════════════════════
# FIGURE 3 — Cut-off event detection exemplar
# ══════════════════════════════════════════════════════════════════════════════
def fig3_detection_exemplar(ev):
    print("  Loading SAROS RES generation data…")
    gen = load_generation("SAROS")
    if gen.empty:
        print("  SAROS not found, skipping Fig 3")
        return

    # Focus on winter 2024-2025 (most active season)
    mask = (
        (gen["datetime"] >= pd.Timestamp("2024-12-01", tz="UTC")) &
        (gen["datetime"] <= pd.Timestamp("2025-02-28", tz="UTC"))
    )
    g = gen[mask].sort_values("datetime").copy()

    # Get SAROS cutoffs in this period
    saros_ev = ev[
        ev["plant_name"].str.upper().str.contains("SAROS") &
        (ev["datetime"] >= pd.Timestamp("2024-12-01", tz="UTC")) &
        (ev["datetime"] <= pd.Timestamp("2025-02-28", tz="UTC"))
    ]

    fig, axes = plt.subplots(3, 1, figsize=(12, 9), sharex=False)

    # ── Panel (a): Full seasonal overview ──
    ax = axes[0]
    ax.fill_between(g["datetime"], g["gen_mw"], alpha=0.4, color=CB[0])
    ax.plot(g["datetime"], g["gen_mw"], color=CB[0], lw=0.7)
    for _, row in saros_ev.iterrows():
        ax.axvline(row["datetime"], color=CB[5], lw=1.2, alpha=0.8, zorder=5)
    ax.axhline(50, color=CB[1], lw=1.2, ls="--", label="θ_high = 50 MW")
    ax.axhline(10, color=CB[2], lw=1.2, ls=":",  label="θ_low = 10 MW")
    ax.set_ylabel("Generation (MW)")
    ax.set_title("(a) SAROS RES — Dec 2024 – Feb 2025 (full seasonal overview)",
                 fontsize=10, loc="left")
    ax.legend(loc="upper right", framealpha=0.9)
    # Add event count annotation
    ax.text(0.01, 0.92, f"{len(saros_ev)} events in this period",
            transform=ax.transAxes, fontsize=8.5, color=CB[5],
            bbox=dict(boxstyle="round,pad=0.2", fc="white", alpha=0.8))

    # ── Panel (b): Zoom on a 2-week storm cluster ──
    # Find busiest 2-week period
    if not saros_ev.empty:
        peak_date = saros_ev.sort_values("drop", ascending=False)["datetime"].iloc[0]
        z_start = peak_date - pd.Timedelta(days=5)
        z_end   = peak_date + pd.Timedelta(days=9)
    else:
        z_start = pd.Timestamp("2025-01-15", tz="UTC")
        z_end   = pd.Timestamp("2025-01-29", tz="UTC")

    gz = g[(g["datetime"] >= z_start) & (g["datetime"] <= z_end)]
    ez = saros_ev[(saros_ev["datetime"] >= z_start) & (saros_ev["datetime"] <= z_end)]

    ax2 = axes[1]
    ax2.fill_between(gz["datetime"], gz["gen_mw"], alpha=0.4, color=CB[0])
    ax2.plot(gz["datetime"], gz["gen_mw"], color=CB[0], lw=1.2)
    ax2.axhline(50, color=CB[1], lw=1.2, ls="--")
    ax2.axhline(10, color=CB[2], lw=1.2, ls=":")
    for i, (_, row) in enumerate(ez.iterrows()):
        ax2.axvline(row["datetime"], color=CB[5], lw=1.8, alpha=0.9, zorder=5)
        ax2.annotate(
            f"Event\n{row['datetime'].strftime('%d-%b')}\n−{row['drop']:.0f} MW",
            xy=(row["datetime"], 5), xytext=(row["datetime"], 80 + i*30),
            fontsize=7, ha="center", color=CB[5],
            arrowprops=dict(arrowstyle="-|>", color=CB[5], lw=0.8),
        )
    ax2.set_ylabel("Generation (MW)")
    ax2.set_title(f"(b) Zoom: {z_start.strftime('%d %b')} – {z_end.strftime('%d %b %Y')} "
                  f"| {len(ez)} hard cut-off events annotated",
                  fontsize=10, loc="left")

    # ── Panel (c): Single event zoom (most severe) ──
    if not saros_ev.empty:
        worst_event = saros_ev.nlargest(1, "drop")["datetime"].iloc[0]
        w_start = worst_event - pd.Timedelta(hours=12)
        w_end   = worst_event + pd.Timedelta(hours=24)
        gw = g[(g["datetime"] >= w_start) & (g["datetime"] <= w_end)]

        ax3 = axes[2]
        ax3.fill_between(gw["datetime"], gw["gen_mw"], alpha=0.35, color=CB[0])
        ax3.plot(gw["datetime"], gw["gen_mw"], color=CB[0], lw=1.8, marker="o", ms=4)
        ax3.axhline(50, color=CB[1], lw=1.5, ls="--", label="θ_high = 50 MW (detection criterion)")
        ax3.axhline(10, color=CB[2], lw=1.5, ls=":", label="θ_low = 10 MW (detection criterion)")
        ax3.axvline(worst_event, color=CB[5], lw=2, label="Hard cut-off event")

        # Annotate the drop
        row = saros_ev.nlargest(1, "drop").iloc[0]
        ax3.annotate(
            f"Hard cut-off\nP_{{t-1}}={row['prev_gen']:.0f} MW\nP_t={row['gen_mw']:.0f} MW\nDrop={row['drop']:.0f} MW ({row['drop']/row['prev_gen']*100:.0f}%)",
            xy=(worst_event, row["gen_mw"]),
            xytext=(worst_event + pd.Timedelta(hours=4), row["prev_gen"] * 0.5),
            fontsize=8.5,
            bbox=dict(boxstyle="round,pad=0.4", fc=CB[5], alpha=0.2, ec=CB[5]),
            arrowprops=dict(arrowstyle="-|>", color=CB[5], lw=1.2),
        )
        ax3.set_ylabel("Generation (MW)")
        ax3.set_title(
            f"(c) Single-event detail: {worst_event.strftime('%d %b %Y %H:%M UTC')} "
            f"(most severe SAROS event: −{row['drop']:.0f} MW)",
            fontsize=10, loc="left"
        )
        ax3.legend(loc="upper right", framealpha=0.9, fontsize=8)

    plt.suptitle("Figure 3. Hard cut-off event detection exemplar: SAROS RES (Çanakkale) "
                 "during winter 2024–25.\n(a) Three-month overview; (b) 14-day event cluster; "
                 "(c) single-event detail showing abrupt production drop.",
                 fontsize=9, y=1.005, ha="center")
    plt.tight_layout()
    savefig("Fig3_detection_exemplar.png")


# ══════════════════════════════════════════════════════════════════════════════
# FIGURE 4 — Three-year event statistics (4-panel)
# ══════════════════════════════════════════════════════════════════════════════
def fig4_event_statistics(ev):
    fig = plt.figure(figsize=(13, 9))
    gs = gridspec.GridSpec(2, 2, figure=fig, hspace=0.38, wspace=0.32)
    ax1 = fig.add_subplot(gs[0, :])   # span full top row
    ax2 = fig.add_subplot(gs[1, 0])
    ax3 = fig.add_subplot(gs[1, 1])

    # ── (a) Monthly event count + energy loss ──
    monthly = ev.groupby("month_dt").agg(
        n=("drop","count"), energy=("energy_lost_mwh","sum")
    ).reset_index()
    monthly["month_dt"] = monthly["month_dt"].dt.to_timestamp()
    monthly = monthly.sort_values("month_dt")
    monthly["cumul"] = monthly["n"].cumsum()
    monthly["is_winter"] = monthly["month_dt"].dt.month.isin([12,1,2])

    bar_cols = [CB[5] if w else CB[0] for w in monthly["is_winter"]]
    ax1b = ax1.twinx()

    bars = ax1.bar(monthly["month_dt"], monthly["n"],
                   width=20, color=bar_cols, alpha=0.75, zorder=2, label="Monthly events")
    ax1b.plot(monthly["month_dt"], monthly["cumul"],
              color=CB[1], lw=2.5, marker="o", ms=3, zorder=3, label="Cumulative")

    ax1.set_ylabel("Events per month", color=CB[0])
    ax1b.set_ylabel("Cumulative events", color=CB[1])
    ax1.set_title("(a) Monthly hard cut-off event count (Jan 2022–Apr 2025)", loc="left", fontsize=10)
    ax1.tick_params(axis="x", rotation=45)

    handles = [
        mpatches.Patch(color=CB[5], alpha=0.75, label="Winter months (DJF)"),
        mpatches.Patch(color=CB[0], alpha=0.75, label="Other months"),
        Line2D([0],[0], color=CB[1], lw=2, marker="o", ms=4, label="Cumulative events"),
    ]
    ax1.legend(handles=handles, loc="upper left", fontsize=8, framealpha=0.9)
    ax1.set_ylim(0)

    # Year shade bands
    for yr, xstart, xend in [
        (2022, "2022-01-01","2022-12-31"),
        (2023, "2023-01-01","2023-12-31"),
        (2024, "2024-01-01","2024-12-31"),
    ]:
        ax1.axvspan(pd.Timestamp(xstart), pd.Timestamp(xend),
                    alpha=0.04, color="black", zorder=1)
        mid = pd.Timestamp(f"{yr}-07-01")
        ax1.text(mid, ax1.get_ylim()[1]*0.93, str(yr),
                 ha="center", fontsize=8, color="#888", style="italic")

    # ── (b) Seasonal distribution ──
    month_n = ev.groupby("month").size().reindex(range(1,13), fill_value=0)
    month_names = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    winter_mask = [m in [12,1,2] for m in range(1,13)]
    bar_cols2 = [CB[5] if w else CB[0] for w in winter_mask]

    ax2.bar(range(1,13), month_n.values, color=bar_cols2, alpha=0.8, edgecolor="k", lw=0.4)
    ax2.set_xticks(range(1,13)); ax2.set_xticklabels(month_names, rotation=45)
    ax2.set_ylabel("Total events (Jan 2022–Apr 2025)")
    ax2.set_title("(b) Seasonal distribution by calendar month", loc="left", fontsize=10)
    ax2.axvspan(0.5, 2.5, alpha=0.08, color=CB[5])
    ax2.axvspan(11.5, 12.5, alpha=0.08, color=CB[5])
    # Annotate winter total
    win_total = ev[ev["month"].isin([12,1,2])].shape[0]
    ax2.text(6.5, ax2.get_ylim()[1]*0.88,
             f"Winter (DJF): {win_total} events\n= {win_total/len(ev)*100:.0f}% of total",
             ha="center", fontsize=8, color=CB[5],
             bbox=dict(boxstyle="round,pad=0.3", fc="white", ec=CB[5], alpha=0.85))

    # ── (c) Hour-of-day distribution ──
    hour_n = ev.groupby("hour").size().reindex(range(0,24), fill_value=0)
    ax3.bar(range(0,24), hour_n.values, color=CB[2], alpha=0.8, edgecolor="k", lw=0.4)
    ax3.set_xticks([0,6,12,18,23])
    ax3.set_xticklabels(["00:00","06:00","12:00","18:00","23:00"])
    ax3.set_xlabel("Hour of day (UTC)")
    ax3.set_ylabel("Total events")
    ax3.set_title("(c) Diurnal distribution of events", loc="left", fontsize=10)
    ax3.axvspan(6, 14, alpha=0.08, color=CB[0], label="Daytime (06–14 UTC)")
    ax3.legend(fontsize=8)

    plt.suptitle("Figure 4. Three-year hard cut-off event statistics (Jan 2022–Apr 2025, n = 249 events).\n"
                 "(a) Monthly counts with cumulative overlay; "
                 "(b) seasonal distribution; (c) diurnal distribution.",
                 fontsize=9, y=1.01)
    savefig("Fig4_event_statistics.png")


# ══════════════════════════════════════════════════════════════════════════════
# FIGURE 5 — Spatial vulnerability map (Turkey + bubble overlay)
# ══════════════════════════════════════════════════════════════════════════════
def fig5_spatial(ev):
    try:
        import geopandas as gpd
        world = gpd.read_file(
            "https://naciscdn.org/naturalearth/110m/cultural/ne_110m_admin_0_countries.zip"
        )
        turkey = world[world["NAME"] == "Turkey"]
        has_geo = True
    except Exception:
        has_geo = False

    # aggregate per plant
    plant_stats = ev.groupby("plant_name").agg(
        n_events=("drop","count"),
        energy_mwh=("energy_lost_mwh","sum"),
        econ_usd_K=("total_loss_usd", lambda x: x.sum()/1e3),
    ).reset_index()
    plant_stats["lat"] = plant_stats["plant_name"].apply(lambda p: get_plant_coord(p)[0])
    plant_stats["lon"] = plant_stats["plant_name"].apply(lambda p: get_plant_coord(p)[1])
    plant_stats["province"] = plant_stats["plant_name"].apply(lambda p: get_plant_coord(p)[2])

    # Province aggregates
    prov = plant_stats.groupby("province").agg(
        n_events=("n_events","sum"),
        energy_mwh=("energy_mwh","sum"),
        econ_usd_K=("econ_usd_K","sum"),
        lat=("lat","mean"),
        lon=("lon","mean"),
        n_plants=("plant_name","count"),
    ).reset_index()

    fig, (ax_map, ax_bar) = plt.subplots(1, 2, figsize=(14, 6),
                                          gridspec_kw={"width_ratios":[1.6,1]})

    # Map
    if has_geo:
        turkey.plot(ax=ax_map, color="#F5F5DC", edgecolor="#555", lw=0.8, zorder=1)
    else:
        ax_map.set_facecolor("#D0E4F4")

    cmap = plt.cm.OrRd
    norm = mcolors.Normalize(vmin=0, vmax=prov["econ_usd_K"].max())
    sc = ax_map.scatter(
        prov["lon"], prov["lat"],
        s=prov["n_events"] * 8 + 50,
        c=prov["econ_usd_K"], cmap=cmap, norm=norm,
        edgecolors="#333", lw=0.7, zorder=4, alpha=0.9
    )
    for _, row in prov.iterrows():
        ax_map.text(row["lon"], row["lat"] + 0.35, row["province"],
                    ha="center", fontsize=7, color="#222", zorder=5)

    cbar = plt.colorbar(sc, ax=ax_map, pad=0.02, fraction=0.025)
    cbar.set_label("Economic loss (USD thousand)", fontsize=8.5)

    # Bubble size legend
    for n, lbl in [(10,"10 events"),(30,"30 events")]:
        ax_map.scatter([], [], s=n*8+50, color="#888", ec="k", alpha=0.8, label=lbl)
    ax_map.legend(loc="lower right", fontsize=7.5, title="Event count", title_fontsize=7.5)
    ax_map.set_xlim(25.5, 45); ax_map.set_ylim(35.5, 43)
    ax_map.set_xlabel("Longitude (°E)", fontsize=9)
    ax_map.set_ylabel("Latitude (°N)", fontsize=9)
    ax_map.set_title("(a) Provincial vulnerability map\n(bubble = events, colour = USD loss)", fontsize=10, loc="left")
    ax_map.grid(True, alpha=0.2)

    # Bar chart: top-10 plants
    top10 = plant_stats.nlargest(10, "n_events").sort_values("n_events")
    short_names = [n.replace(" RES","").replace(" RES(BAK)","").replace("(İzdem)","")[:14]
                   for n in top10["plant_name"]]
    colors_bar = [cmap(norm(v)) for v in top10["econ_usd_K"]]
    ax_bar.barh(short_names, top10["n_events"], color=colors_bar, edgecolor="k", lw=0.4)
    for i, (_, row) in enumerate(top10.iterrows()):
        ax_bar.text(row["n_events"]+0.3, i,
                    f"${row['econ_usd_K']:.0f}K", va="center", fontsize=7.5)
    ax_bar.set_xlabel("Number of cut-off events")
    ax_bar.set_title("(b) Top 10 plants by event frequency\n(colour = economic loss)", fontsize=10, loc="left")
    ax_bar.grid(axis="x", alpha=0.3)

    plt.suptitle("Figure 5. Spatial vulnerability of Turkish wind farms to hard cut-off events "
                 "(Jan 2022–Apr 2025).\nLeft: provincial bubble map; right: top 10 plants ranked by event frequency.",
                 fontsize=9, y=1.01)
    plt.tight_layout()
    savefig("Fig5_spatial_vulnerability.png")


# ══════════════════════════════════════════════════════════════════════════════
# FIGURE 6 — 16 March 2025 storm day (concurrent shutdowns)
# ══════════════════════════════════════════════════════════════════════════════
def fig6_storm_day(ev):
    # Get all events on 16 March 2025
    storm = ev[
        (ev["datetime"].dt.date == pd.Timestamp("2025-03-16").date()) |
        (ev["datetime"] >= pd.Timestamp("2025-03-14", tz="UTC")) &
        (ev["datetime"] <= pd.Timestamp("2025-03-18", tz="UTC"))
    ].copy()
    storm = storm.sort_values("datetime")

    # Load generation for affected plants
    affected_plants = ev[
        (ev["datetime"] >= pd.Timestamp("2025-03-15", tz="UTC")) &
        (ev["datetime"] <= pd.Timestamp("2025-03-18", tz="UTC"))
    ]["plant_name"].unique()[:12]  # top 12

    print(f"  Storm period: {len(storm)} events, {len(affected_plants)} plants")

    gen = pd.read_csv(DATA_DIR / "generation_202201_202504.csv", parse_dates=["date"])
    gen["datetime"] = pd.to_datetime(gen["date"], utc=True, errors="coerce")
    gen["gen_mw"] = pd.to_numeric(gen["ruzgar"], errors="coerce").fillna(0)
    mask = (
        gen["plant_name"].isin(affected_plants) &
        (gen["datetime"] >= pd.Timestamp("2025-03-14", tz="UTC")) &
        (gen["datetime"] <= pd.Timestamp("2025-03-18", tz="UTC"))
    )
    g = gen[mask].copy()

    # Pivot: rows=datetime, cols=plant
    pivot = g.pivot_table(index="datetime", columns="plant_name", values="gen_mw", aggfunc="max").fillna(0)
    pivot.columns = [c.replace(" RES","").replace("(İzdem)","")[:14] for c in pivot.columns]
    # Sort columns by max generation
    pivot = pivot[pivot.max().sort_values(ascending=False).index]

    # Aggregate total
    total_gen = g.groupby("datetime")["gen_mw"].sum()

    fig, (ax_total, ax_heat) = plt.subplots(2, 1, figsize=(13, 9),
                                             gridspec_kw={"height_ratios":[1,2]})

    # ── (a) Total generation across all affected plants ──
    ax_total.fill_between(total_gen.index, total_gen.values, alpha=0.4, color=CB[0])
    ax_total.plot(total_gen.index, total_gen.values, color=CB[0], lw=1.5)
    # Mark cut-off events
    for _, row in storm.iterrows():
        if row["plant_name"] in g["plant_name"].unique():
            ax_total.axvline(row["datetime"], color=CB[5], lw=0.8, alpha=0.7)
    # Mark peak event day
    ax_total.axvspan(
        pd.Timestamp("2025-03-16 00:00", tz="UTC"),
        pd.Timestamp("2025-03-16 23:59", tz="UTC"),
        alpha=0.12, color=CB[5], label="16 March (peak: 15 simultaneous cut-offs)"
    )
    ax_total.set_ylabel("Total generation (MW)")
    ax_total.set_title("(a) Aggregate wind generation across affected plants (14–18 March 2025)",
                       loc="left", fontsize=10)
    ax_total.legend(fontsize=8.5, loc="upper right")

    # ── (b) Heatmap: per-plant generation ──
    im = ax_heat.imshow(
        pivot.T.values, aspect="auto", cmap="Blues",
        extent=[0, len(pivot), 0, len(pivot.columns)],
        vmin=0, origin="lower"
    )
    ax_heat.set_yticks(np.arange(0.5, len(pivot.columns)))
    ax_heat.set_yticklabels(pivot.columns[::-1], fontsize=7.5)

    # X-axis: datetime labels
    xt_indices = np.linspace(0, len(pivot)-1, 7, dtype=int)
    xt_labels  = [pivot.index[i].strftime("%d-%b\n%H:00") for i in xt_indices]
    ax_heat.set_xticks(xt_indices)
    ax_heat.set_xticklabels(xt_labels, fontsize=8)

    # Mark cut-off events on heatmap
    for _, row in storm.iterrows():
        pname = row["plant_name"].replace(" RES","").replace("(İzdem)","")[:14]
        if pname in list(pivot.columns):
            xi = (row["datetime"] - pivot.index[0]).total_seconds() / 3600
            yi = len(pivot.columns) - list(pivot.columns).index(pname) - 0.5
            ax_heat.plot(xi, yi, "v", color=CB[5], ms=6, mew=0.5, mec="k", zorder=5)

    plt.colorbar(im, ax=ax_heat, label="Generation (MW)", fraction=0.02, pad=0.01)
    ax_heat.set_title("(b) Per-plant generation heatmap (▼ = detected cut-off event)", loc="left", fontsize=10)
    ax_heat.set_xlabel("Date / Hour (UTC)")

    plt.suptitle("Figure 6. The 14–18 March 2025 extreme wind event: concurrent turbine shutdowns "
                 "across northwestern Turkey.\n(a) Aggregate generation collapse; "
                 "(b) per-plant heatmap with cut-off events marked (▼).",
                 fontsize=9, y=1.005)
    plt.tight_layout()
    savefig("Fig6_storm_day.png")


# ══════════════════════════════════════════════════════════════════════════════
# FIGURE 7 — Economic impact (3-panel improved)
# ══════════════════════════════════════════════════════════════════════════════
def fig7_economic(ev):
    fig, axes = plt.subplots(1, 3, figsize=(14, 5))

    # ── (a) Annual energy loss + economic loss ──
    annual = ev.groupby("year").agg(
        energy_mwh=("energy_lost_mwh","sum"),
        econ_usd_K=("total_loss_usd", lambda x: x.sum()/1e3),
        n_events=("drop","count"),
    ).reset_index()
    ax = axes[0]
    ax2 = ax.twinx()
    bars = ax.bar(annual["year"].astype(str), annual["energy_mwh"]/1e3,
                  color=CB[0], alpha=0.75, edgecolor="k", lw=0.5, label="Energy lost (GWh)", width=0.5)
    ax2.plot(annual["year"].astype(str), annual["econ_usd_K"],
             color=CB[1], lw=2.5, marker="s", ms=8, label="Economic loss (USD K)", zorder=5)
    for bar, n in zip(bars, annual["n_events"]):
        ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.01,
                f"n={n}", ha="center", fontsize=8, color="#333")
    ax.set_ylabel("Energy lost (GWh)", color=CB[0])
    ax2.set_ylabel("Economic loss (USD thousand)", color=CB[1])
    ax.set_title("(a) Annual energy & economic loss", fontsize=10, loc="left")
    h1, l1 = ax.get_legend_handles_labels(); h2, l2 = ax2.get_legend_handles_labels()
    ax.legend(h1+h2, l1+l2, fontsize=7.5, loc="upper left")
    ax.set_ylim(0)

    # ── (b) Top-10 plants ──
    by_plant = (
        ev.groupby("plant_name")["total_loss_usd"].sum()
        .nlargest(10).reset_index()
    )
    by_plant["name_short"] = by_plant["plant_name"].apply(
        lambda s: s.replace(" RES","").replace(" RES(BAK)","").replace("(İzdem)","")[:15]
    )
    by_plant["usd_K"] = by_plant["total_loss_usd"] / 1e3
    by_plant = by_plant.sort_values("usd_K")

    cmap2 = plt.cm.YlOrRd
    norm2 = mcolors.Normalize(vmin=0, vmax=by_plant["usd_K"].max())
    colors2 = [cmap2(norm2(v)) for v in by_plant["usd_K"]]
    axes[1].barh(by_plant["name_short"], by_plant["usd_K"],
                 color=colors2, edgecolor="k", lw=0.4)
    for i, v in enumerate(by_plant["usd_K"]):
        axes[1].text(v + 1, i, f"${v:.0f}K", va="center", fontsize=7.5)
    axes[1].set_xlabel("Direct revenue loss (USD thousand)")
    axes[1].set_title("(b) Top 10 plants by economic loss", fontsize=10, loc="left")
    axes[1].grid(axis="x", alpha=0.3)

    # ── (c) PTF distribution during events vs all hours ──
    ax3 = axes[2]
    # Load full PTF dataset for comparison
    ptf_file = DATA_DIR / "ptf_prices_202201_202504.csv"
    ptf_all = pd.read_csv(ptf_file)
    ptf_all["ptf_tl_mwh"] = pd.to_numeric(ptf_all["price"], errors="coerce")
    ptf_all = ptf_all["ptf_tl_mwh"].dropna()

    event_ptf = ev["ptf_tl_mwh"].dropna()
    bins = np.linspace(0, min(ptf_all.max(), 6000), 40)
    ax3.hist(ptf_all, bins=bins, density=True, alpha=0.5, color=CB[3], label="All hours (2022–2025)")
    ax3.hist(event_ptf, bins=bins, density=True, alpha=0.7, color=CB[5], label="Cut-off event hours")
    ax3.axvline(ptf_all.median(), color=CB[3], lw=1.5, ls="--",
                label=f"All-hours median: {ptf_all.median():.0f} TL/MWh")
    ax3.axvline(event_ptf.median(), color=CB[5], lw=1.5, ls="--",
                label=f"Event-hours median: {event_ptf.median():.0f} TL/MWh")
    ax3.set_xlabel("PTF market price (TL/MWh)")
    ax3.set_ylabel("Density")
    ax3.set_title("(c) PTF price: all hours vs cut-off event hours", fontsize=10, loc="left")
    ax3.legend(fontsize=7.5)

    plt.suptitle("Figure 7. Economic impact of hard cut-off events (Jan 2022–Apr 2025, n = 249).\n"
                 "(a) Annual energy and economic losses; (b) top 10 plants; "
                 "(c) market price (PTF) distribution during events vs all hours.",
                 fontsize=9, y=1.01)
    plt.tight_layout()
    savefig("Fig7_economic_impact.png")


# ══════════════════════════════════════════════════════════════════════════════
# FIGURE 8 — Model performance (4-panel)
# ══════════════════════════════════════════════════════════════════════════════
def fig8_model():
    from sklearn.metrics import (
        roc_curve, auc, precision_recall_curve, average_precision_score,
    )
    try:
        from sklearn.calibration import calibration_curve
    except ImportError:
        calibration_curve = None
    MODEL_DIR = ANAL_DIR / "models" / "v2"

    horizons = [6, 12, 24]
    colors_h = {6: CB[0], 12: CB[1], 24: CB[2]}
    results = {}
    for H in horizons:
        f = MODEL_DIR / f"xgb_H{H}_probs.csv"
        if f.exists():
            results[H] = pd.read_csv(f)

    fig = plt.figure(figsize=(14, 9))
    gs = gridspec.GridSpec(2, 2, figure=fig, hspace=0.38, wspace=0.30)
    ax_roc  = fig.add_subplot(gs[0, 0])
    ax_pr   = fig.add_subplot(gs[0, 1])
    ax_feat = fig.add_subplot(gs[1, 0])
    ax_cal  = fig.add_subplot(gs[1, 1])

    # ── ROC curves ──
    for H, d in results.items():
        fpr, tpr, _ = roc_curve(d["y_true"], d["y_prob"])
        roc_auc = auc(fpr, tpr)
        ax_roc.plot(fpr, tpr, color=colors_h[H], lw=2.0,
                    label=f"H={H}h (AUC={roc_auc:.3f})")
    ax_roc.plot([0,1],[0,1],"k--", lw=1, label="Random (AUC=0.500)")
    ax_roc.set_xlabel("False Positive Rate"); ax_roc.set_ylabel("True Positive Rate")
    ax_roc.set_title("(a) Receiver Operating Characteristic (ROC) curves", fontsize=10, loc="left")
    ax_roc.legend(framealpha=0.9); ax_roc.set_xlim(0,1); ax_roc.set_ylim(0,1)
    ax_roc.set_aspect("equal", adjustable="box")

    # ── PR curves ──
    for H, d in results.items():
        prec, rec, _ = precision_recall_curve(d["y_true"], d["y_prob"])
        ap = average_precision_score(d["y_true"], d["y_prob"])
        ax_pr.plot(rec, prec, color=colors_h[H], lw=2.0,
                   label=f"H={H}h (AP={ap:.3f})")
    base_rate = results[6]["y_true"].mean() if results else 0.18
    ax_pr.axhline(base_rate, color="k", ls="--", lw=1,
                  label=f"No-skill (P={base_rate:.2f})")
    ax_pr.set_xlabel("Recall"); ax_pr.set_ylabel("Precision")
    ax_pr.set_title("(b) Precision-Recall (PR) curves", fontsize=10, loc="left")
    ax_pr.legend(framealpha=0.9); ax_pr.set_xlim(0,1); ax_pr.set_ylim(0,1)

    # ── Feature importance comparison ──
    feat_data = {}
    for H in horizons:
        fi_f = MODEL_DIR / f"feature_importance_H{H}.csv"
        if fi_f.exists():
            fi = pd.read_csv(fi_f)
            # try to find feature and importance columns
            fc = [c for c in fi.columns if "feature" in c.lower() or "name" in c.lower()]
            ic = [c for c in fi.columns if "import" in c.lower() or "gain" in c.lower()
                  or "weight" in c.lower() or "score" in c.lower()]
            if not fc or not ic:
                # try first two cols
                fc, ic = [fi.columns[0]], [fi.columns[1] if len(fi.columns)>1 else fi.columns[0]]
            fi = fi.rename(columns={fc[0]: "feature", ic[0]: "importance"})
            fi["importance"] = pd.to_numeric(fi["importance"], errors="coerce").fillna(0)
            feat_data[H] = fi.set_index("feature")["importance"]

    if feat_data:
        all_feats = sorted(set(f for d in feat_data.values() for f in d.index))
        mean_imp = pd.Series({f: np.mean([feat_data[H].get(f, 0) for H in horizons])
                               for f in all_feats})
        top15 = mean_imp.nlargest(15).sort_values()

        y  = range(len(top15))
        w  = 0.25
        for i, (H, fc) in enumerate([(6,CB[0]),(12,CB[1]),(24,CB[2])]):
            vals = [feat_data.get(H, pd.Series()).get(f,0) for f in top15.index]
            ax_feat.barh([yi + (i-1)*w for yi in y], vals,
                         height=w, color=fc, alpha=0.8, label=f"H={H}h")
        ax_feat.set_yticks(list(y)); ax_feat.set_yticklabels(top15.index, fontsize=7.5)
        ax_feat.set_xlabel("Feature importance (gain)")
        ax_feat.set_title("(c) Feature importances by horizon (top 15, mean gain)", fontsize=10, loc="left")
        ax_feat.legend(fontsize=8)

    # ── Calibration curves ──
    if calibration_curve is not None:
        for H, d in results.items():
            prob_true, prob_pred = calibration_curve(
                d["y_true"], d["y_prob"], n_bins=8, strategy="quantile"
            )
            ax_cal.plot(prob_pred, prob_true, color=colors_h[H], lw=2, marker="o", ms=5,
                        label=f"H={H}h")
        ax_cal.plot([0,1],[0,1],"k--", lw=1, label="Perfect calibration")
    else:
        # Fallback: show model metric summary bar chart
        metrics = {
            6:  dict(roc=0.585, pr=0.259, f1=0.306),
            12: dict(roc=0.571, pr=0.227, f1=0.215),
            24: dict(roc=0.549, pr=0.203, f1=0.301),
        }
        x = np.arange(3)
        w = 0.25
        m_names = ["ROC-AUC","PR-AUC","F1"]
        for j, mn in enumerate(m_names):
            vals = [metrics[H][mn[:3].lower()] for H in [6,12,24]]
            ax_cal.bar(x + j*w, vals, width=w, color=[CB[0],CB[1],CB[2]], alpha=0.8,
                       label=mn if j == 0 else "")
        ax_cal.set_xticks(x+w)
        ax_cal.set_xticklabels(["ROC-AUC","PR-AUC","F1"])
        ax_cal.set_ylabel("Score")
        ax_cal.axhline(0.5, color="k", ls="--", lw=1)
        handles = [mpatches.Patch(color=colors_h[H], label=f"H={H}h") for H in [6,12,24]]
        ax_cal.legend(handles=handles, fontsize=8)

    ax_cal.set_xlabel("Mean predicted probability")
    ax_cal.set_ylabel("Fraction of positives")
    ax_cal.set_title("(d) Calibration / metric summary by horizon", fontsize=10, loc="left")
    if calibration_curve is not None:
        ax_cal.legend(framealpha=0.9)
    ax_cal.set_xlim(0, 1); ax_cal.set_ylim(0, 1)

    plt.suptitle("Figure 8. XGBoost early warning model performance (test set: Jan–Apr 2025, n=148 windows).\n"
                 "(a) ROC curves; (b) PR curves; (c) feature importances per prediction horizon; "
                 "(d) probability calibration.",
                 fontsize=9, y=1.01)
    savefig("Fig8_model_performance.png")


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("Loading event data…")
    ev = load_events()
    print(f"  {len(ev)} events loaded\n")

    print("Figure 1: Study area map…");      fig1_study_area(ev)
    print("Figure 2: Framework diagram…");   fig2_framework()
    print("Figure 3: Detection exemplar…");  fig3_detection_exemplar(ev)
    print("Figure 4: Event statistics…");    fig4_event_statistics(ev)
    print("Figure 5: Spatial vulnerability…"); fig5_spatial(ev)
    print("Figure 6: Storm day…");           fig6_storm_day(ev)
    print("Figure 7: Economic impact…");     fig7_economic(ev)
    print("Figure 8: Model performance…");   fig8_model()

    print(f"\nAll figures saved to: {FIG_DIR}/")
    print("Files generated:")
    for f in sorted(FIG_DIR.glob("Fig*.png")):
        size_kb = f.stat().st_size // 1024
        print(f"  {f.name:40s} {size_kb:5d} KB")
