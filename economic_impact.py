#!/usr/bin/env python3
"""
Economic Impact Calculator
============================
Quantifies the monetary losses from hard cutoff events using:
  - EPİAŞ PTF (Piyasa Takas Fiyatı) market clearing prices
  - YEKDEM feed-in tariff rates (if PTF unavailable)
  - Estimated capacity factor impact

When PTF prices are not yet downloaded, this module uses:
  - YEKDEM RES tariff: 73 USD/MWh (2021 contract rate, ~2400 TL/MWh at 2024 rates)
  - Average Türkiye electricity market price (historical average ~1800-2500 TL/MWh)

Outputs:
  - analysis/economic_impact_summary.csv
  - analysis/economic_impact_by_plant.csv
  - analysis/economic_impact_by_month.csv
"""

import logging
from pathlib import Path

import numpy as np
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

PROJECT = Path(__file__).parent
DATA_DIR = PROJECT / "data"
ANALYSIS_DIR = PROJECT / "analysis"
ANALYSIS_DIR.mkdir(exist_ok=True)

# YEKDEM wind tariff (USD/MWh, valid 2021-2031 contracts)
YEKDEM_USD_PER_MWH = 73.0

# Exchange rate approximations (TL/USD) for the study period
# Source: TCMB historical rates (approximate annual averages)
TL_USD_RATES = {
    2022: 16.5,
    2023: 23.0,
    2024: 32.5,
    2025: 36.0,
}

# Average PTF (TL/MWh) estimates when actual data unavailable
# Source: EPİAŞ Transparency Platform historical reports
ESTIMATED_PTF_TL = {
    "2024-10": 2800,
    "2024-11": 2650,
    "2024-12": 2900,
    "2025-01": 3100,
    "2025-02": 2950,
    "2025-03": 2750,
    "2025-04": 2600,
}

# Grid balancing cost estimate (reserve activation)
# Turkish TEIAS balancing market: ~10-20% premium over PTF during events
BALANCING_PREMIUM_PCT = 15.0


def load_cutoff_events() -> pd.DataFrame:
    """Load the main cutoff dataset."""
    f = DATA_DIR / "all_cutoffs_2024_2025.csv"
    df = pd.read_csv(f)
    df["datetime"] = pd.to_datetime(df["datetime"], utc=True, errors="coerce")
    df["year"] = df["datetime"].dt.year
    df["month_str"] = df["datetime"].dt.strftime("%Y-%m")
    return df


def load_ptf_prices() -> pd.DataFrame:
    """Load actual PTF prices if available, else return empty DataFrame."""
    ptf_files = list(DATA_DIR.glob("ptf_prices_*.csv"))
    if ptf_files:
        dfs = [pd.read_csv(f) for f in ptf_files]
        df = pd.concat(dfs, ignore_index=True)
        logger.info(f"PTF prices loaded: {len(df)} records from {len(ptf_files)} files")
        return df
    logger.info("No PTF price files found; using estimated values.")
    return pd.DataFrame()


def assign_ptf_prices(cutoffs: pd.DataFrame, ptf: pd.DataFrame) -> pd.DataFrame:
    """Assign PTF price to each cutoff event."""
    cutoffs = cutoffs.copy()

    if len(ptf) > 0:
        # Attempt to merge on datetime
        # Normalize PTF datetime column
        dt_col = next((c for c in ptf.columns if "date" in c.lower() or "saat" in c.lower()), None)
        price_col = next(
            (c for c in ptf.columns if "price" in c.lower() or "fiyat" in c.lower() or "mcp" in c.lower()),
            None,
        )
        if dt_col and price_col:
            ptf["datetime_utc"] = pd.to_datetime(ptf[dt_col], utc=True, errors="coerce")
            ptf["ptf_tl_mwh"] = pd.to_numeric(
                ptf[price_col].astype(str).str.replace(",", "."), errors="coerce"
            )
            ptf_hourly = ptf[["datetime_utc", "ptf_tl_mwh"]].dropna()
            cutoffs = cutoffs.merge(ptf_hourly, left_on="datetime", right_on="datetime_utc", how="left")
    else:
        cutoffs["ptf_tl_mwh"] = cutoffs["month_str"].map(ESTIMATED_PTF_TL)
        cutoffs["ptf_source"] = "estimated"
        logger.info("Using estimated PTF prices (YEKDEM reference rates).")

    # Fill remaining NaN with month estimate
    cutoffs["ptf_tl_mwh"] = cutoffs["ptf_tl_mwh"].fillna(
        cutoffs["month_str"].map(ESTIMATED_PTF_TL)
    )

    return cutoffs


def calculate_economic_impact(cutoffs: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate economic impact metrics for each cutoff event.

    Formula:
        Revenue loss (TL) = Drop (MW) × 1 hour × PTF (TL/MWh)
        Balancing cost (TL) = Revenue loss × BALANCING_PREMIUM_PCT / 100
        Total loss (TL) = Revenue loss + Balancing cost

    For USD equivalent:
        Total loss (USD) = Total loss (TL) / TL_USD_rate(year)
    """
    df = cutoffs.copy()

    # Energy lost = MW × 1 hour = MWh
    df["energy_lost_mwh"] = pd.to_numeric(df["drop"], errors="coerce").fillna(0)

    # Revenue loss
    df["revenue_loss_tl"] = df["energy_lost_mwh"] * df["ptf_tl_mwh"]

    # Balancing cost (TEIAS reserve activation premium)
    df["balancing_cost_tl"] = df["revenue_loss_tl"] * (BALANCING_PREMIUM_PCT / 100)

    # Total economic loss
    df["total_loss_tl"] = df["revenue_loss_tl"] + df["balancing_cost_tl"]

    # USD equivalent
    df["tl_usd_rate"] = df["year"].map(TL_USD_RATES).fillna(32.0)
    df["total_loss_usd"] = df["total_loss_tl"] / df["tl_usd_rate"]

    # YEKDEM tariff basis (what wind farm operator loses from YEKDEM guarantee)
    df["yekdem_loss_usd"] = df["energy_lost_mwh"] * YEKDEM_USD_PER_MWH

    return df


def generate_summary_tables(df: pd.DataFrame):
    """Generate and save economic impact summary tables."""

    # Overall summary
    total_energy = df["energy_lost_mwh"].sum()
    total_revenue = df["revenue_loss_tl"].sum()
    total_balancing = df["balancing_cost_tl"].sum()
    total_loss_tl = df["total_loss_tl"].sum()
    total_loss_usd = df["total_loss_usd"].sum()
    total_yekdem_usd = df["yekdem_loss_usd"].sum()

    summary = {
        "Metric": [
            "Total cutoff events",
            "Total energy lost (MWh)",
            "Average loss per event (MWh)",
            "Total revenue loss (TL million)",
            "Balancing cost premium (TL million)",
            "Total economic loss (TL million)",
            "Total economic loss (USD thousand)",
            "YEKDEM tariff basis loss (USD thousand)",
            "Study period",
            "Wind farms affected",
        ],
        "Value": [
            f"{len(df)}",
            f"{total_energy:.0f}",
            f"{total_energy / max(len(df), 1):.1f}",
            f"{total_revenue / 1e6:.2f}",
            f"{total_balancing / 1e6:.2f}",
            f"{total_loss_tl / 1e6:.2f}",
            f"{total_loss_usd / 1e3:.1f}",
            f"{total_yekdem_usd / 1e3:.1f}",
            f"{df['datetime'].min()} to {df['datetime'].max()}",
            f"{df['plant'].nunique() if 'plant' in df.columns else 'N/A'}",
        ],
        "Notes": [
            "",
            "1 hour × MW drop per event",
            "",
            f"Based on estimated PTF rates",
            f"TEIAS reserve: +{BALANCING_PREMIUM_PCT}% of revenue loss",
            "",
            "",
            f"YEKDEM rate: {YEKDEM_USD_PER_MWH} USD/MWh",
            "",
            "",
        ],
    }
    pd.DataFrame(summary).to_csv(ANALYSIS_DIR / "economic_impact_summary.csv", index=False)

    # Monthly breakdown
    monthly = (
        df.groupby("month_str")
        .agg(
            n_events=("energy_lost_mwh", "count"),
            energy_lost_mwh=("energy_lost_mwh", "sum"),
            revenue_loss_tl=("revenue_loss_tl", "sum"),
            total_loss_tl=("total_loss_tl", "sum"),
            total_loss_usd=("total_loss_usd", "sum"),
            yekdem_loss_usd=("yekdem_loss_usd", "sum"),
            ptf_avg=("ptf_tl_mwh", "mean"),
        )
        .reset_index()
    )
    monthly["revenue_loss_tl_million"] = monthly["revenue_loss_tl"] / 1e6
    monthly["total_loss_tl_million"] = monthly["total_loss_tl"] / 1e6
    monthly.to_csv(ANALYSIS_DIR / "economic_impact_by_month.csv", index=False)

    # Plant-level breakdown
    if "plant" in df.columns:
        by_plant = (
            df.groupby("plant")
            .agg(
                n_events=("energy_lost_mwh", "count"),
                total_energy_lost_mwh=("energy_lost_mwh", "sum"),
                total_loss_tl=("total_loss_tl", "sum"),
                total_loss_usd=("total_loss_usd", "sum"),
                yekdem_loss_usd=("yekdem_loss_usd", "sum"),
                max_single_loss_mwh=("energy_lost_mwh", "max"),
            )
            .reset_index()
            .sort_values("total_energy_lost_mwh", ascending=False)
        )
        by_plant.to_csv(ANALYSIS_DIR / "economic_impact_by_plant.csv", index=False)

    logger.info("Economic impact tables saved to analysis/")

    # Print summary
    print("\n" + "=" * 65)
    print("ECONOMIC IMPACT SUMMARY")
    print("=" * 65)
    print(f"Total cutoff events      : {len(df)}")
    print(f"Total energy lost        : {total_energy:,.0f} MWh")
    print(f"Revenue loss             : {total_revenue/1e6:.2f} million TL")
    print(f"  + Balancing premium    : {total_balancing/1e6:.2f} million TL")
    print(f"Total economic loss      : {total_loss_tl/1e6:.2f} million TL")
    print(f"                         = {total_loss_usd/1e3:.1f} thousand USD")
    print(f"YEKDEM basis loss        : {total_yekdem_usd/1e3:.1f} thousand USD")
    print("=" * 65)

    return df


def run():
    logger.info("Running economic impact analysis...")
    cutoffs = load_cutoff_events()
    ptf = load_ptf_prices()
    cutoffs = assign_ptf_prices(cutoffs, ptf)
    cutoffs = calculate_economic_impact(cutoffs)
    result = generate_summary_tables(cutoffs)
    cutoffs.to_csv(ANALYSIS_DIR / "cutoffs_with_economic_impact.csv", index=False)
    logger.info("Saved: analysis/cutoffs_with_economic_impact.csv")
    return result


if __name__ == "__main__":
    run()
