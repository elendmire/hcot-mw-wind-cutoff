#!/usr/bin/env python3
"""Generate graphical abstract for HCOT-MW paper (300 DPI)."""

from pathlib import Path
import warnings
warnings.filterwarnings("ignore")

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import numpy as np
import pandas as pd

ROOT    = Path(__file__).parent
ANA_DIR = ROOT / "analysis"
DATA_DIR= ROOT / "data"
FIG_DIR = ROOT / "figures"
FIG_DIR.mkdir(exist_ok=True)

# ── Palette ────────────────────────────────────────────────────────────────
BG      = "#FAFAFA"
ACCENT  = "#1A5276"
RED     = "#C0392B"
ORANGE  = "#E67E22"
GREEN   = "#27AE60"
GRAY    = "#7F8C8D"
DJF     = "#2980B9"
OTHER   = "#AED6F1"
THRESH  = "#E74C3C"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size":   8,
    "axes.spines.top":   False,
    "axes.spines.right": False,
    "figure.facecolor":  BG,
})

# ── Data ───────────────────────────────────────────────────────────────────
def load():
    ev = pd.read_csv(ANA_DIR / "cutoff_events_with_losses.csv")
    ev["datetime"] = pd.to_datetime(ev["datetime"], utc=True)

    wrf = pd.read_csv(DATA_DIR / "wrf_wind_march2025.csv")
    wrf["datetime"] = pd.to_datetime(wrf["datetime"])
    return ev, wrf


def monthly_counts(ev):
    idx = pd.date_range("2022-01", "2025-05", freq="MS")
    obs = ev.groupby(ev["datetime"].dt.to_period("M")).size()
    obs.index = obs.index.to_timestamp()
    s = obs.reindex(idx, fill_value=0)
    df = pd.DataFrame({"date": s.index, "n": s.values})
    df["djf"] = df["date"].dt.month.isin([12, 1, 2])
    return df


# ── Panel helpers ──────────────────────────────────────────────────────────
def draw_kpi_row(ax):
    ax.axis("off")
    kpis = [
        ("249",      "hard\ncut-off events",  ACCENT),
        ("43",       "wind farms\naffected",   GREEN),
        ("39M TL",   "revenue loss\n≈USD 1.6M", ORANGE),
        ("27.4 m/s", "WRF hub-height\npeak wind", RED),
    ]
    for i, (num, label, color) in enumerate(kpis):
        x = (i + 0.5) / 4
        box = FancyBboxPatch(
            (x - 0.112, 0.04), 0.224, 0.92,
            boxstyle="round,pad=0.02", lw=1.2,
            edgecolor=color, facecolor=color + "12",
            transform=ax.transAxes,
        )
        ax.add_patch(box)
        ax.text(x, 0.68, num, ha="center", va="center",
                fontsize=13, fontweight="bold", color=color,
                transform=ax.transAxes)
        ax.text(x, 0.25, label, ha="center", va="center",
                fontsize=6.5, color="#333", linespacing=1.3,
                transform=ax.transAxes)


def draw_map(ax, ev):
    COORDS = {
        "SAROS RES":                         (40.68, 26.55),
        "EVRENCİK RES":                      (41.52, 27.74),
        "YAHYALI RES(BAK)":                  (38.10, 35.35),
        "GÖKTEPE RES":                       (40.55, 29.25),
        "İSTANBUL RES":                      (41.18, 28.35),
        "ÜÇPINAR RES":                       (39.68, 28.10),
        "TAŞPINAR RES(GALATA WİND)":         (41.12, 28.42),
        "KIYIKÖY RES":                       (41.62, 28.10),
        "GÜLPINAR RES":                      (39.48, 26.08),
        "KOCATEPE RES(İzdem)":               (38.15, 27.15),
        "KANGAL RES":                        (39.25, 37.38),
        "BAĞLAR RES (BAĞLAR ELK.ÜRT.A.Ş.)": (40.25, 28.85),
        "SÜLOĞLU RES":                       (41.78, 26.91),
        "ZONGULDAK RES":                     (40.72, 31.18),
        "TATLIPINAR RES":                    (39.75, 28.15),
        "KOCAELI RES":                       (40.85, 29.92),
        "SOMA RES(SOMA ENR.)":               (39.18, 27.61),
        "AYAS RES":                          (40.02, 32.55),
        "EBER RES":                          (38.58, 31.50),
    }

    turkey_drawn = False
    try:
        import geopandas as gpd
        world = gpd.read_file(
            "https://naciscdn.org/naturalearth/110m/cultural/ne_110m_admin_0_countries.zip"
        )
        nbrs = world[world["NAME"].isin([
            "Greece", "Bulgaria", "Georgia", "Armenia",
            "Azerbaijan", "Iran", "Iraq", "Syria", "Lebanon",
        ])]
        nbrs.plot(ax=ax, color="#EAECEE", edgecolor="#CCC", lw=0.4, zorder=1)
        world[world["NAME"] == "Turkey"].plot(
            ax=ax, color="#F0F3F4", edgecolor="#555", lw=0.7, zorder=2
        )
        turkey_drawn = True
    except Exception:
        from matplotlib.patches import FancyBboxPatch as FBP
        ax.add_patch(FBP(
            (25.5, 35.8), 19.5, 7.0, boxstyle="round,pad=0.3",
            edgecolor="#555", facecolor="#F0F3F4", lw=0.7, zorder=2,
            transform=ax.transData,
        ))

    per_plant = ev.groupby("plant_name").size()
    cmap = plt.cm.YlOrRd
    for plant, (lat, lon) in COORDS.items():
        n = per_plant.get(plant, 0)
        if n == 0:
            ax.scatter(lon, lat, s=8, c="#CCC", zorder=4,
                       edgecolors="#AAA", linewidths=0.3, alpha=0.6)
        else:
            ax.scatter(lon, lat, s=15 + n * 3, zorder=5,
                       c=[cmap(min(n / 40, 1.0))],
                       edgecolors="#333", linewidths=0.4, alpha=0.9)

    for plant, offset in [
        ("SAROS RES",       (-1.8, -0.7)),
        ("İSTANBUL RES",    (-2.5,  0.3)),
        ("YAHYALI RES(BAK)",(0.3,   0.3)),
    ]:
        coords = COORDS.get(plant)
        if coords:
            lat, lon = coords
            name = plant.split("(")[0].strip()
            ax.annotate(name, (lon, lat),
                        xytext=(lon + offset[0], lat + offset[1]),
                        fontsize=5.5, color=ACCENT, fontweight="bold",
                        arrowprops=dict(arrowstyle="-", color=GRAY, lw=0.5),
                        zorder=7)

    ax.set_xlim(24.5, 45.5)
    ax.set_ylim(35.5, 43.0)
    ax.set_xlabel("Longitude °E", fontsize=7)
    ax.set_ylabel("Latitude °N",  fontsize=7)
    ax.set_title("Spatial distribution of hard cut-off events",
                 fontsize=8, fontweight="bold", pad=4)
    ax.tick_params(labelsize=6.5)

    from matplotlib.cm import ScalarMappable
    from matplotlib.colors import Normalize
    sm = ScalarMappable(cmap="YlOrRd", norm=Normalize(0, 40))
    sm.set_array([])
    cb = plt.colorbar(sm, ax=ax, fraction=0.028, pad=0.02, shrink=0.75)
    cb.set_label("Events / farm", fontsize=6.5)
    cb.ax.tick_params(labelsize=6)


def draw_timeline(ax, monthly):
    colors = [DJF if d else OTHER for d in monthly["djf"]]
    ax.bar(range(len(monthly)), monthly["n"], color=colors,
           edgecolor="none", width=0.9)

    yr_ticks = [i for i, d in enumerate(monthly["date"]) if d.month == 1]
    ax.set_xticks(yr_ticks)
    ax.set_xticklabels(
        [monthly["date"].iloc[i].strftime("%Y") for i in yr_ticks], fontsize=7
    )
    ax.set_ylabel("Events", fontsize=7)
    ax.set_title("Monthly events (Jan 2022 – Apr 2025)",
                 fontsize=8, fontweight="bold")
    ax.tick_params(axis="y", labelsize=6.5)

    # Annotate Mar 2025
    sel = monthly[(monthly["date"].dt.year == 2025) & (monthly["date"].dt.month == 3)]
    if not sel.empty:
        pos = sel.index[0] - monthly.index[0]
        v   = sel["n"].iloc[0]
        ax.annotate("Mar '25\n14 simultaneous",
                    xy=(pos, v),
                    xytext=(pos - 8, v + 3),
                    arrowprops=dict(arrowstyle="->", color=RED, lw=0.7),
                    fontsize=6, color=RED, fontweight="bold")

    ax.legend(
        handles=[mpatches.Patch(color=DJF, label="DJF winter"),
                 mpatches.Patch(color=OTHER, label="Other")],
        fontsize=6, frameon=False, loc="upper left",
    )
    ax.set_xlim(-0.5, len(monthly) - 0.5)
    ax.set_ylim(0, monthly["n"].max() * 1.45)


def draw_top_farms(ax, ev):
    top = (
        ev.groupby("plant_name").size()
        .sort_values(ascending=True).tail(7)
    )
    labels = [
        n.replace(" RES","").replace("(GALATA WİND)","")
         .replace("(BAK)","").replace("(İzdem)","").strip()
        for n in top.index
    ]
    colors = [RED if "SAROS" in l else ACCENT for l in labels]
    bars = ax.barh(range(len(top)), top.values, color=colors,
                   edgecolor="none", height=0.7)
    ax.set_yticks(range(len(top)))
    ax.set_yticklabels(labels, fontsize=7)
    ax.set_xlabel("Events", fontsize=7)
    ax.set_title("Top 7 affected farms", fontsize=8, fontweight="bold")
    ax.tick_params(axis="x", labelsize=6.5)
    for bar, val in zip(bars, top.values):
        ax.text(bar.get_width() + 0.4, bar.get_y() + bar.get_height() / 2,
                str(val), va="center", fontsize=6.5, color=GRAY)
    ax.set_xlim(0, top.max() * 1.20)


def draw_wrf(ax, wrf):
    plant_col = "plant"
    candidates = wrf[plant_col].unique()
    ist = wrf[wrf[plant_col].str.contains("ISTANBUL|İSTANBUL", case=False, na=False)]
    if ist.empty:
        ist = wrf[wrf[plant_col] == candidates[0]]
    ist = ist.sort_values("datetime").reset_index(drop=True)

    x = range(len(ist))
    ax.plot(x, ist["ws100"], color=ACCENT, lw=1.4, label="100 m (hub)")
    ax.plot(x, ist["ws10"],  color=GREEN,  lw=0.9, ls="--", label="10 m")
    ax.axhline(25, color=THRESH, lw=1.1, ls=":", label="25 m/s cut-out")
    ax.fill_between(x, 25, ist["ws100"].clip(lower=25),
                    color=THRESH, alpha=0.18)

    ticks = list(range(0, len(ist), 24))
    labels = [ist["datetime"].iloc[t].strftime("%-d\nMar") for t in ticks]
    ax.set_xticks(ticks)
    ax.set_xticklabels(labels, fontsize=6.5)
    ax.set_ylabel("Wind speed (m/s)", fontsize=7)
    ax.set_title("WRF 100 m wind — İSTANBUL RES (14–18 Mar 2025)",
                 fontsize=8, fontweight="bold")
    ax.tick_params(axis="y", labelsize=6.5)
    ax.legend(fontsize=6, frameon=False, loc="upper right", ncol=3)

    pk_i = int(ist["ws100"].idxmax())
    pk_v = ist["ws100"].max()
    ax.annotate(f"{pk_v:.1f} m/s",
                xy=(pk_i, pk_v),
                xytext=(pk_i + 5, pk_v + 1.5),
                arrowprops=dict(arrowstyle="->", color=RED, lw=0.7),
                fontsize=6.5, color=RED, fontweight="bold")


# ── Layout & save ──────────────────────────────────────────────────────────
def main():
    ev, wrf = load()
    monthly = monthly_counts(ev)

    # 14" × 8" → at 150 DPI = 2100×1200 px; save at 300 DPI for crisp output
    fig = plt.figure(figsize=(14, 8), facecolor=BG)

    # Outer: header row + body
    outer = gridspec.GridSpec(
        2, 1, figure=fig,
        height_ratios=[1.1, 8.9],
        hspace=0.08,
        left=0.04, right=0.97, top=0.96, bottom=0.06,
    )

    # ── Header ──
    ax_hdr = fig.add_subplot(outer[0])
    ax_hdr.axis("off")
    ax_hdr.text(
        0.5, 0.78,
        "Detection and Economic Quantification of Hard Wind Cut-Off Events "
        "in Turkish Wind Farms",
        ha="center", va="center",
        fontsize=11, fontweight="bold", color=ACCENT,
        transform=ax_hdr.transAxes,
    )
    ax_hdr.text(
        0.5, 0.18,
        "Jan 2022 – Apr 2025  •  161 licensed YEKDEM plants  •  "
        "EPİAŞ real-time data  •  WRF ARW 4.6.0  •  XGBoost early warning",
        ha="center", va="center",
        fontsize=8, color=GRAY, transform=ax_hdr.transAxes,
    )

    # ── Body: 3 columns ──
    body = gridspec.GridSpecFromSubplotSpec(
        1, 3, subplot_spec=outer[1],
        width_ratios=[4.5, 3.5, 3.5],
        wspace=0.32,
    )

    # Left column: map
    ax_map = fig.add_subplot(body[0])

    # Centre column: KPI strip (top) + timeline (bottom)
    centre = gridspec.GridSpecFromSubplotSpec(
        2, 1, subplot_spec=body[1],
        height_ratios=[1.2, 3.8],
        hspace=0.45,
    )
    ax_kpi  = fig.add_subplot(centre[0])
    ax_time = fig.add_subplot(centre[1])

    # Right column: top farms (top) + WRF (bottom)
    right = gridspec.GridSpecFromSubplotSpec(
        2, 1, subplot_spec=body[2],
        height_ratios=[2.2, 2.8],
        hspace=0.50,
    )
    ax_farms = fig.add_subplot(right[0])
    ax_wrf   = fig.add_subplot(right[1])

    draw_map(ax_map, ev)
    draw_kpi_row(ax_kpi)
    draw_timeline(ax_time, monthly)
    draw_top_farms(ax_farms, ev)
    draw_wrf(ax_wrf, wrf)

    out = FIG_DIR / "Fig0_graphical_abstract.png"
    fig.savefig(out, dpi=300, bbox_inches="tight", facecolor=BG)
    plt.close(fig)
    size_kb = out.stat().st_size // 1024
    print(f"Saved: {out}  ({size_kb} KB)")


if __name__ == "__main__":
    main()
