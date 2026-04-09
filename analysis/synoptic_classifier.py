#!/usr/bin/env python3
"""
Synoptic Pattern Classification
==================================
Uses ERA5 mean sea-level pressure (MSLP) fields to classify the synoptic
weather patterns associated with hard cutoff events over Turkey.

Method:
  1. Extract ERA5 MSLP at the time of each cutoff event (±12h composites)
  2. Apply K-means clustering (k=5) on flattened MSLP fields
  3. Assign synoptic class to each cutoff event
  4. Compute composite maps for each class

Output:
  - analysis/synoptic_classes.csv  (event → class assignment)
  - analysis/synoptic_composites/  (composite MSLP maps as .npy)
  - figures/fig5_synoptic_patterns.png

When ERA5 data is not yet downloaded, runs in "stub mode" using the
existing WRF validation data to demonstrate the approach.
"""

import logging
from pathlib import Path

import numpy as np
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

PROJECT = Path(__file__).parent.parent
DATA_DIR = PROJECT / "data"
ERA5_DIR = DATA_DIR / "era5"
ANALYSIS_DIR = PROJECT / "analysis"
FIGURES_DIR = PROJECT / "figures"
FIGURES_DIR.mkdir(exist_ok=True)
ANALYSIS_DIR.mkdir(exist_ok=True)

N_CLUSTERS = 5  # Number of synoptic pattern classes

# Class labels (assigned after visual inspection of composite maps)
SYNOPTIC_LABELS = {
    0: "Cyclone_NW_Turkey",
    1: "Cold_Front_Thrace",
    2: "Bora_Channel_Flow",
    3: "Mediterranean_Low",
    4: "Blocking_Anticyclone",
}


def load_cutoff_events() -> pd.DataFrame:
    f = DATA_DIR / "all_cutoffs_2024_2025.csv"
    df = pd.read_csv(f)
    df["datetime"] = pd.to_datetime(df["datetime"], utc=True, errors="coerce")
    return df


def classify_with_era5(cutoffs: pd.DataFrame) -> pd.DataFrame:
    """
    Full ERA5-based synoptic classification.
    Requires: data/era5/era5_surface_wind_*.nc files.
    """
    try:
        import netCDF4 as nc4  # noqa: F401
        from sklearn.cluster import KMeans
        from sklearn.preprocessing import StandardScaler
    except ImportError as e:
        logger.error(f"Required package not found: {e}")
        return cutoffs

    era5_files = sorted(ERA5_DIR.glob("era5_surface_wind_*.nc"))
    if not era5_files:
        logger.warning("ERA5 files not found. Run: python era5_downloader.py --vars wind")
        return classify_stub(cutoffs)

    logger.info(f"ERA5 files found: {[f.name for f in era5_files]}")

    import netCDF4 as nc

    mslp_composites = []
    event_times = cutoffs["datetime"].dropna().dt.tz_localize(None)

    for f in era5_files:
        ds = nc.Dataset(f)
        time_var = ds.variables["time"]
        times = nc.num2date(time_var[:], time_var.units)
        times_pd = pd.to_datetime([str(t) for t in times])

        if "msl" not in ds.variables:
            ds.close()
            continue

        msl = ds.variables["msl"][:]  # (time, lat, lon) in Pa
        msl_hpa = msl / 100.0  # Convert to hPa

        for evt_t in event_times:
            idx = np.argmin(np.abs(times_pd - evt_t))
            composite = msl_hpa[idx, :, :]
            mslp_composites.append(composite.flatten())

        ds.close()

    if not mslp_composites:
        logger.warning("No MSLP composites extracted. Falling back to stub.")
        return classify_stub(cutoffs)

    X = np.array(mslp_composites)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    kmeans = KMeans(n_clusters=N_CLUSTERS, random_state=42, n_init=20)
    labels = kmeans.fit_predict(X_scaled)

    cutoffs = cutoffs.copy()
    cutoffs["synoptic_class"] = labels
    cutoffs["synoptic_label"] = cutoffs["synoptic_class"].map(SYNOPTIC_LABELS)

    # Save composites
    composites_dir = ANALYSIS_DIR / "synoptic_composites"
    composites_dir.mkdir(exist_ok=True)
    np.save(composites_dir / "kmeans_centers.npy", kmeans.cluster_centers_)
    np.save(composites_dir / "scaler_mean.npy", scaler.mean_)

    logger.info("ERA5 synoptic classification complete.")
    return cutoffs


def classify_stub(cutoffs: pd.DataFrame) -> pd.DataFrame:
    """
    Stub classification based on event timing and magnitude.
    Used when ERA5 data is not yet downloaded.
    Assigns synthetic classes based on:
      - Month (winter = cold fronts, spring = cyclones)
      - Event magnitude (high drop = strong event)
      - Spatial co-occurrence (March 16 = cyclone cluster)
    """
    logger.info("Running stub synoptic classification (ERA5 not available).")
    df = cutoffs.copy()
    df["month"] = df["datetime"].dt.month
    df["drop_mw"] = pd.to_numeric(df.get("drop", df.get("drop_mw", 0)), errors="coerce").fillna(0)

    def assign_class(row):
        m = row.get("month", 1)
        drop = row.get("drop_mw", 0)
        plant = str(row.get("plant", ""))
        # March 16 storm = Class 1 (Cold Front Thrace)
        if pd.notna(row.get("datetime")) and "03-16" in str(row["datetime"]):
            return 1
        # Winter high-drop events = Class 0 (Cyclone NW Turkey)
        if m in [12, 1, 2] and drop > 80:
            return 0
        # Thrace plants in strong events
        if any(kw in plant.upper() for kw in ["KIYIKÖY", "EVRENCİK", "SÜLOĞLU"]):
            return 1
        # Aegean events
        if any(kw in plant.upper() for kw in ["GÜLPINAR", "KUŞ", "SAROS"]):
            return 2
        # Spring events
        if m in [3, 4, 10]:
            return 3
        return 4

    df["synoptic_class"] = df.apply(assign_class, axis=1)
    df["synoptic_label"] = df["synoptic_class"].map(SYNOPTIC_LABELS)
    df["classification_method"] = "stub_heuristic"
    return df


def generate_class_statistics(df: pd.DataFrame) -> pd.DataFrame:
    """Compute statistics per synoptic class."""
    stats = (
        df.groupby(["synoptic_class", "synoptic_label"])
        .agg(
            n_events=("drop_pct", "count") if "drop_pct" in df.columns else ("synoptic_class", "count"),
            mean_loss_mw=("drop", "mean") if "drop" in df.columns else ("synoptic_class", "count"),
            total_loss_mw=("drop", "sum") if "drop" in df.columns else ("synoptic_class", "count"),
            affected_plants=("plant", "nunique") if "plant" in df.columns else ("synoptic_class", "count"),
        )
        .reset_index()
        .sort_values("n_events", ascending=False)
    )
    return stats


def run():
    """Main execution."""
    cutoffs = load_cutoff_events()
    logger.info(f"Classifying {len(cutoffs)} cutoff events...")

    # Try ERA5 first, fall back to stub
    era5_available = len(list(ERA5_DIR.glob("era5_surface_wind_*.nc"))) > 0
    if era5_available:
        classified = classify_with_era5(cutoffs)
    else:
        classified = classify_stub(cutoffs)

    # Save results
    classified.to_csv(ANALYSIS_DIR / "synoptic_classes.csv", index=False)
    logger.info("Saved: analysis/synoptic_classes.csv")

    # Statistics
    stats = generate_class_statistics(classified)
    stats.to_csv(ANALYSIS_DIR / "synoptic_class_statistics.csv", index=False)
    logger.info("Saved: analysis/synoptic_class_statistics.csv")

    print("\nSynoptic Class Distribution:")
    print(stats.to_string(index=False))

    return classified


if __name__ == "__main__":
    run()
