#!/usr/bin/env python3
"""
Economic Impact Analysis — 3-year dataset (Jan 2022 – Apr 2025)

Workflow:
  1. Load master generation CSV & detect hard cutoffs
  2. Merge with actual PTF prices
  3. Compute revenue / balancing / YEKDEM losses
  4. Save summary + per-plant + monthly tables
"""

from pathlib import Path
import numpy as np
import pandas as pd

PROJECT = Path(__file__).parent
DATA_DIR = PROJECT / "data"
ANALYSIS_DIR = PROJECT / "analysis"
ANALYSIS_DIR.mkdir(exist_ok=True)

# ─── Detection thresholds (same as hard_cutoff_detector.py) ───────────────────
THETA_HIGH = 50.0   # MW  previous hour must exceed this
THETA_LOW  = 10.0   # MW  current hour must be below this
THETA_DROP = 0.80   # fractional drop required

# ─── Economic constants ────────────────────────────────────────────────────────
YEKDEM_USD_PER_MWH = 73.0
TL_USD_RATES = {2022: 16.5, 2023: 23.0, 2024: 32.5, 2025: 36.0}
BALANCING_PREMIUM_PCT = 15.0


# ──────────────────────────────────────────────────────────────────────────────
def load_generation() -> pd.DataFrame:
    f = DATA_DIR / "generation_202201_202504.csv"
    df = pd.read_csv(f, parse_dates=["date"])
    df = df[["date", "ruzgar", "plant_id", "plant_name"]].rename(
        columns={"date": "datetime", "ruzgar": "gen_mw"}
    )
    df["gen_mw"] = pd.to_numeric(df["gen_mw"], errors="coerce").fillna(0)
    df["datetime"] = pd.to_datetime(df["datetime"], utc=True, errors="coerce")
    df = df.sort_values(["plant_id", "datetime"]).reset_index(drop=True)
    return df


def detect_cutoffs(gen: pd.DataFrame) -> pd.DataFrame:
    events = []
    for plant_id, grp in gen.groupby("plant_id"):
        grp = grp.sort_values("datetime").reset_index(drop=True)
        grp["prev_gen"] = grp["gen_mw"].shift(1)
        mask = (
            (grp["prev_gen"] > THETA_HIGH)
            & (grp["gen_mw"] < THETA_LOW)
            & ((grp["prev_gen"] - grp["gen_mw"]) / grp["prev_gen"] >= THETA_DROP)
        )
        hits = grp[mask].copy()
        hits["drop"] = hits["prev_gen"] - hits["gen_mw"]
        hits["plant_name"] = grp["plant_name"].iloc[0]
        events.append(hits)
    if not events:
        return pd.DataFrame()
    ev = pd.concat(events, ignore_index=True)
    ev["year"] = ev["datetime"].dt.year
    ev["month_str"] = ev["datetime"].dt.strftime("%Y-%m")
    return ev[["datetime", "plant_id", "plant_name", "gen_mw", "prev_gen", "drop", "year", "month_str"]]


def load_ptf() -> pd.DataFrame:
    f = DATA_DIR / "ptf_prices_202201_202504.csv"
    df = pd.read_csv(f, parse_dates=["date"])
    df["datetime"] = pd.to_datetime(df["date"], utc=True, errors="coerce")
    df["ptf_tl_mwh"] = pd.to_numeric(df["price"], errors="coerce")
    return df[["datetime", "ptf_tl_mwh"]].dropna()


def merge_ptf(ev: pd.DataFrame, ptf: pd.DataFrame) -> pd.DataFrame:
    ev = ev.merge(ptf, on="datetime", how="left")
    # fallback: use annual median if hour not matched
    medians = ptf.groupby(ptf["datetime"].dt.year)["ptf_tl_mwh"].median()
    ev["ptf_fallback"] = ev["year"].map(medians)
    ev["ptf_tl_mwh"] = ev["ptf_tl_mwh"].fillna(ev["ptf_fallback"])
    ev["ptf_source"] = np.where(ev["ptf_tl_mwh"].notna(), "actual", "estimated")
    return ev


def compute_losses(ev: pd.DataFrame) -> pd.DataFrame:
    ev = ev.copy()
    ev["energy_lost_mwh"] = ev["drop"]
    ev["revenue_loss_tl"] = ev["energy_lost_mwh"] * ev["ptf_tl_mwh"]
    ev["balancing_cost_tl"] = ev["revenue_loss_tl"] * (BALANCING_PREMIUM_PCT / 100)
    ev["total_loss_tl"] = ev["revenue_loss_tl"] + ev["balancing_cost_tl"]
    ev["tl_usd_rate"] = ev["year"].map(TL_USD_RATES).fillna(32.0)
    ev["total_loss_usd"] = ev["total_loss_tl"] / ev["tl_usd_rate"]
    ev["yekdem_loss_usd"] = ev["energy_lost_mwh"] * YEKDEM_USD_PER_MWH
    return ev


def save_tables(ev: pd.DataFrame):
    # ── Overall summary ──────────────────────────────────────────────────────
    n = len(ev)
    plants = ev["plant_name"].nunique()
    energy = ev["energy_lost_mwh"].sum()
    rev_tl = ev["revenue_loss_tl"].sum()
    bal_tl = ev["balancing_cost_tl"].sum()
    tot_tl = ev["total_loss_tl"].sum()
    tot_usd = ev["total_loss_usd"].sum()
    yek_usd = ev["yekdem_loss_usd"].sum()
    avg_ptf = ev["ptf_tl_mwh"].mean()

    summary = pd.DataFrame({
        "Metric": [
            "Total hard-cutoff events (Jan 2022–Apr 2025)",
            "Unique wind plants affected",
            "Total energy lost (MWh)",
            "Average energy lost per event (MWh)",
            "Average PTF during events (TL/MWh)",
            "Total revenue loss (TL million)",
            "Grid balancing cost premium (TL million)",
            "Total economic loss (TL million)",
            "Total economic loss (USD thousand)",
            "YEKDEM tariff-basis loss (USD thousand)",
        ],
        "Value": [
            f"{n}",
            f"{plants}",
            f"{energy:,.0f}",
            f"{energy / max(n, 1):.1f}",
            f"{avg_ptf:,.0f}",
            f"{rev_tl / 1e6:.2f}",
            f"{bal_tl / 1e6:.2f}",
            f"{tot_tl / 1e6:.2f}",
            f"{tot_usd / 1e3:.1f}",
            f"{yek_usd / 1e3:.1f}",
        ],
    })
    out_sum = ANALYSIS_DIR / "economic_impact_summary.csv"
    summary.to_csv(out_sum, index=False)
    print("\n=== ECONOMIC IMPACT SUMMARY ===")
    print(summary.to_string(index=False))
    print(f"\nSaved: {out_sum}")

    # ── Monthly breakdown ────────────────────────────────────────────────────
    monthly = (
        ev.groupby("month_str")
        .agg(
            n_events=("energy_lost_mwh", "count"),
            energy_lost_mwh=("energy_lost_mwh", "sum"),
            revenue_loss_tl_M=("revenue_loss_tl", lambda x: x.sum() / 1e6),
            total_loss_tl_M=("total_loss_tl", lambda x: x.sum() / 1e6),
            total_loss_usd_K=("total_loss_usd", lambda x: x.sum() / 1e3),
            avg_ptf_tl=("ptf_tl_mwh", "mean"),
        )
        .reset_index()
    )
    out_mon = ANALYSIS_DIR / "economic_impact_by_month.csv"
    monthly.to_csv(out_mon, index=False)
    print(f"Saved: {out_mon}")

    # ── Per-plant breakdown ──────────────────────────────────────────────────
    by_plant = (
        ev.groupby(["plant_id", "plant_name"])
        .agg(
            n_events=("energy_lost_mwh", "count"),
            energy_lost_mwh=("energy_lost_mwh", "sum"),
            total_loss_tl_M=("total_loss_tl", lambda x: x.sum() / 1e6),
            total_loss_usd_K=("total_loss_usd", lambda x: x.sum() / 1e3),
            yekdem_loss_usd_K=("yekdem_loss_usd", lambda x: x.sum() / 1e3),
        )
        .sort_values("total_loss_usd_K", ascending=False)
        .reset_index()
    )
    out_plant = ANALYSIS_DIR / "economic_impact_by_plant.csv"
    by_plant.to_csv(out_plant, index=False)
    print(f"Saved: {out_plant}")
    print("\nTop 10 plants by economic loss:")
    print(by_plant.head(10)[["plant_name", "n_events", "energy_lost_mwh",
                              "total_loss_usd_K"]].to_string(index=False))

    # ── Annual breakdown ─────────────────────────────────────────────────────
    annual = (
        ev.groupby("year")
        .agg(
            n_events=("energy_lost_mwh", "count"),
            energy_lost_mwh=("energy_lost_mwh", "sum"),
            total_loss_tl_M=("total_loss_tl", lambda x: x.sum() / 1e6),
            total_loss_usd_K=("total_loss_usd", lambda x: x.sum() / 1e3),
        )
        .reset_index()
    )
    out_ann = ANALYSIS_DIR / "economic_impact_by_year.csv"
    annual.to_csv(out_ann, index=False)
    print(f"\nAnnual breakdown:\n{annual.to_string(index=False)}")
    print(f"Saved: {out_ann}")

    return summary, monthly, by_plant, annual


if __name__ == "__main__":
    print("Loading generation data…")
    gen = load_generation()
    print(f"  {len(gen):,} rows, {gen['plant_id'].nunique()} plants")

    print("Detecting hard cutoffs…")
    ev = detect_cutoffs(gen)
    print(f"  {len(ev)} events detected across {ev['plant_name'].nunique()} plants")

    print("Loading PTF prices…")
    ptf = load_ptf()
    print(f"  {len(ptf):,} hourly PTF records")

    print("Merging PTF prices…")
    ev = merge_ptf(ev, ptf)
    actual_pct = (ev["ptf_source"] == "actual").mean() * 100
    print(f"  Actual PTF matched: {actual_pct:.1f}% of events")

    print("Computing losses…")
    ev = compute_losses(ev)

    save_tables(ev)

    ev.to_csv(ANALYSIS_DIR / "cutoff_events_with_losses.csv", index=False)
    print(f"\nFull detail saved: {ANALYSIS_DIR}/cutoff_events_with_losses.csv")
