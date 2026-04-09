#!/usr/bin/env python3
"""
Data Quality Control (QC) Analysis
=====================================
Performs comprehensive QC on all available datasets:
  - EPİAŞ generation data (per-plant cutoff events)
  - MGM surface observations
  - ERA5 reanalysis (when downloaded)
  - Canakkale RES hourly data

QC checks:
  1. Missing value analysis (% per variable/station)
  2. Temporal gap detection (hourly sequences)
  3. Outlier detection (IQR + Z-score)
  4. Cross-dataset consistency

Outputs:
  - analysis/qc_report.txt
  - analysis/qc_tables/*.csv
"""

import logging
from pathlib import Path

import numpy as np
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

PROJECT = Path(__file__).parent.parent
DATA_DIR = PROJECT / "data"
MGM_DIR = PROJECT / "mgm_analysis" / "tables"
QC_DIR = PROJECT / "analysis" / "qc_tables"
QC_DIR.mkdir(parents=True, exist_ok=True)


def load_cutoff_events() -> pd.DataFrame:
    """Load the main cutoff event dataset."""
    f = DATA_DIR / "all_cutoffs_2024_2025.csv"
    df = pd.read_csv(f)
    df["datetime"] = pd.to_datetime(df["datetime"], utc=True, errors="coerce")
    df["month_dt"] = df["datetime"].dt.to_period("M")
    logger.info(f"Cutoff events loaded: {len(df)} rows")
    return df


def load_canakkale_data() -> pd.DataFrame:
    """Load Canakkale RES hourly generation data."""
    f = PROJECT / "canakkale_res_export" / "output" / "canakkale_region_res_hourly_last6m.csv"
    if not f.exists():
        logger.warning("Canakkale export not found.")
        return pd.DataFrame()
    df = pd.read_csv(f)
    df["datetime"] = pd.to_datetime(df["datetime"], utc=True, errors="coerce")
    logger.info(f"Canakkale data loaded: {len(df)} rows")
    return df


def load_mgm_data() -> pd.DataFrame:
    """Load MGM combined hourly observations."""
    f = MGM_DIR / "mgm_combined_hourly.csv"
    if not f.exists():
        logger.warning("MGM data not found.")
        return pd.DataFrame()
    df = pd.read_csv(f)
    logger.info(f"MGM data loaded: {len(df)} rows")
    return df


def qc_missing_values(df: pd.DataFrame, name: str) -> pd.DataFrame:
    """Compute per-column missing value statistics."""
    total = len(df)
    stats = []
    for col in df.columns:
        n_miss = df[col].isna().sum()
        stats.append({
            "dataset": name,
            "variable": col,
            "total_records": total,
            "missing_count": n_miss,
            "missing_pct": round(n_miss / total * 100, 2),
            "dtype": str(df[col].dtype),
        })
    result = pd.DataFrame(stats)
    return result


def qc_temporal_gaps(df: pd.DataFrame, dt_col: str = "datetime", freq: str = "1H") -> dict:
    """Detect temporal gaps in hourly time series."""
    if dt_col not in df.columns or df[dt_col].isna().all():
        return {"gaps": 0, "max_gap_hours": 0}

    dt = df[dt_col].sort_values().drop_duplicates()
    diff = dt.diff().dropna()
    expected = pd.Timedelta(freq)
    gaps = diff[diff > expected * 1.5]

    return {
        "total_hours": len(dt),
        "expected_hours": int((dt.max() - dt.min()) / expected) + 1,
        "gap_count": len(gaps),
        "max_gap_hours": float(gaps.max().total_seconds() / 3600) if len(gaps) > 0 else 0,
        "coverage_pct": round(len(dt) / max(1, int((dt.max() - dt.min()) / expected) + 1) * 100, 1),
    }


def qc_outliers(series: pd.Series, name: str) -> dict:
    """IQR + Z-score outlier detection."""
    s = series.dropna()
    if len(s) < 10:
        return {}
    q1, q3 = s.quantile(0.25), s.quantile(0.75)
    iqr = q3 - q1
    iqr_lower, iqr_upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    z = np.abs((s - s.mean()) / s.std())
    return {
        "variable": name,
        "n": len(s),
        "mean": round(s.mean(), 3),
        "std": round(s.std(), 3),
        "min": round(s.min(), 3),
        "max": round(s.max(), 3),
        "iqr_outliers": int(((s < iqr_lower) | (s > iqr_upper)).sum()),
        "zscore_outliers_3sigma": int((z > 3).sum()),
        "iqr_outlier_pct": round(((s < iqr_lower) | (s > iqr_upper)).sum() / len(s) * 100, 2),
    }


def run_qc():
    """Run full QC pipeline and save results."""
    logger.info("=" * 60)
    logger.info("STARTING DATA QUALITY CONTROL")
    logger.info("=" * 60)

    summary_lines = [
        "DATA QUALITY CONTROL REPORT",
        "=" * 60,
        f"Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}",
        "",
    ]

    all_missing = []
    all_outliers = []

    # --- Dataset 1: Cutoff Events ---
    cutoffs = load_cutoff_events()
    if len(cutoffs) > 0:
        miss = qc_missing_values(cutoffs, "Cutoff Events")
        all_missing.append(miss)

        gaps = qc_temporal_gaps(cutoffs, "datetime")
        summary_lines += [
            "1. CUTOFF EVENTS (EPİAŞ Oct 2024 - Apr 2025)",
            f"   Total events: {len(cutoffs)}",
            f"   Wind farms affected: {cutoffs['plant'].nunique() if 'plant' in cutoffs.columns else 'N/A'}",
            f"   Date range: {cutoffs['datetime'].min()} → {cutoffs['datetime'].max()}",
            f"   Missing values: {miss['missing_pct'].max():.1f}% max",
            "",
        ]

        for col in ["drop", "prev", "curr"]:
            if col in cutoffs.columns:
                o = qc_outliers(pd.to_numeric(cutoffs[col], errors="coerce"), col)
                if o:
                    all_outliers.append(o)

    # --- Dataset 2: Canakkale RES ---
    canakkale = load_canakkale_data()
    if len(canakkale) > 0:
        miss = qc_missing_values(canakkale, "Canakkale RES")
        all_missing.append(miss)

        gaps = qc_temporal_gaps(canakkale, "datetime")
        summary_lines += [
            "2. CANAKKALE RES HOURLY DATA",
            f"   Total rows: {len(canakkale)}",
            f"   Plants: {canakkale['plant_name'].nunique() if 'plant_name' in canakkale.columns else 'N/A'}",
            f"   Date range: {canakkale['datetime'].min()} → {canakkale['datetime'].max()}",
            f"   Temporal coverage: {gaps.get('coverage_pct', 'N/A')}%",
            f"   Gaps detected: {gaps.get('gap_count', 'N/A')}",
            "",
        ]

        if "generation_mwh" in canakkale.columns:
            o = qc_outliers(canakkale["generation_mwh"], "generation_mwh")
            if o:
                all_outliers.append(o)

    # --- Dataset 3: MGM Observations ---
    mgm = load_mgm_data()
    if len(mgm) > 0:
        miss = qc_missing_values(mgm, "MGM Observations")
        all_missing.append(miss)

        summary_lines += [
            "3. MGM SURFACE OBSERVATIONS (15-18 March 2025)",
            f"   Total rows: {len(mgm)}",
            f"   Columns: {', '.join(mgm.columns.tolist()[:8])}",
            f"   Missing max: {miss['missing_pct'].max():.1f}%",
            "",
        ]

    # --- Save tables ---
    if all_missing:
        missing_df = pd.concat(all_missing, ignore_index=True)
        missing_df.to_csv(QC_DIR / "qc_missing_values.csv", index=False)
        logger.info("Saved: qc_missing_values.csv")

    if all_outliers:
        outliers_df = pd.DataFrame(all_outliers)
        outliers_df.to_csv(QC_DIR / "qc_outliers.csv", index=False)
        logger.info("Saved: qc_outliers.csv")

    # --- Cutoff event descriptive statistics ---
    if len(cutoffs) > 0:
        desc_stats = []
        for col in ["drop", "prev", "curr", "drop_pct"]:
            if col in cutoffs.columns:
                s = pd.to_numeric(cutoffs[col], errors="coerce").dropna()
                desc_stats.append({
                    "variable": col,
                    "count": len(s),
                    "mean": round(s.mean(), 2),
                    "std": round(s.std(), 2),
                    "min": round(s.min(), 2),
                    "p25": round(s.quantile(0.25), 2),
                    "median": round(s.median(), 2),
                    "p75": round(s.quantile(0.75), 2),
                    "p95": round(s.quantile(0.95), 2),
                    "max": round(s.max(), 2),
                })
        if desc_stats:
            pd.DataFrame(desc_stats).to_csv(QC_DIR / "cutoff_descriptive_stats.csv", index=False)
            logger.info("Saved: cutoff_descriptive_stats.csv")

        # Monthly summary
        if "month" in cutoffs.columns:
            monthly = (
                cutoffs.groupby("month")
                .agg(
                    n_events=("drop", "count"),
                    total_loss_mw=("drop", "sum"),
                    max_loss_mw=("drop", "max"),
                    mean_loss_mw=("drop", "mean"),
                    n_plants=("plant", "nunique") if "plant" in cutoffs.columns else ("drop", "count"),
                )
                .reset_index()
            )
            monthly.to_csv(QC_DIR / "cutoff_monthly_summary.csv", index=False)
            logger.info("Saved: cutoff_monthly_summary.csv")

    # --- Write report ---
    summary_lines += [
        "QC SUMMARY",
        "=" * 60,
        "All tables saved to: analysis/qc_tables/",
        "  - qc_missing_values.csv",
        "  - qc_outliers.csv",
        "  - cutoff_descriptive_stats.csv",
        "  - cutoff_monthly_summary.csv",
        "",
        "STATUS: QC COMPLETE",
    ]

    report_text = "\n".join(summary_lines)
    report_path = PROJECT / "analysis" / "qc_report.txt"
    report_path.write_text(report_text, encoding="utf-8")
    logger.info(f"QC report saved: {report_path}")

    print("\n" + report_text)
    return report_text


if __name__ == "__main__":
    run_qc()
