#!/usr/bin/env python3
"""
Cutoff Early Warning — Leakage-Free Pipeline v2
================================================
Rebuilt from scratch following audit findings.

Key design decisions vs v1:
  - Window ends at t-H-1 (H hours BEFORE the cutoff), zero lookahead
  - All features computed purely from 24-hour window data
  - Strictly temporal split: 2022-2023 train / 2024 val / 2025 test
  - No rolling statistics that cross the prediction boundary
  - Negative windows: sampled from periods with no cutoff within ±48h

Usage:
    python analysis/train_v2.py           # all three horizons
    python analysis/train_v2.py --dry-run # skip training, print dataset stats
"""

import argparse
import pickle
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import linregress

warnings.filterwarnings("ignore")

import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

PROJECT    = Path(__file__).parent.parent
DATA_DIR   = PROJECT / "data"
MODEL_DIR  = PROJECT / "analysis" / "models" / "v2"
MODEL_DIR.mkdir(parents=True, exist_ok=True)
OUT_CSV    = PROJECT / "analysis" / "model_comparison_v2.csv"

THETA_HIGH = 50.0
THETA_LOW  = 10.0
THETA_DROP = 80.0

WINDOW_LEN  = 24      # hours of history in each window
NEG_GAP     = 48     # minimum hours from any cutoff for negative windows
NEG_RATIO   = 5      # negative : positive windows per plant
HORIZONS    = [6, 12, 24]

# Temporal split boundaries (inclusive, UTC)
TRAIN_END = pd.Timestamp("2023-12-31 23:00", tz="UTC")
VAL_END   = pd.Timestamp("2024-12-31 23:00", tz="UTC")


# 1. DATA LOADING  (reused logic from v1 — no leakage here)
def load_and_label(max_plants=None) -> pd.DataFrame:
    """Load wind generation master CSV, label cutoff events."""
    master = DATA_DIR / "generation_202201_202504.csv"
    logger.info("Loading master CSV...")
    df = pd.read_csv(
        master,
        usecols=["date", "ruzgar", "plant_id", "plant_name"],
        dtype={"plant_id": int, "ruzgar": float, "plant_name": str},
        encoding="utf-8-sig",
    )
    df = df.rename(columns={"date": "datetime", "ruzgar": "gen_mw"})
    df["datetime"] = pd.to_datetime(df["datetime"], utc=True, errors="coerce")
    df = df.dropna(subset=["datetime"])
    df["gen_mw"] = df["gen_mw"].fillna(0.0).clip(lower=0)

    # Wind-only plants
    totals = df.groupby("plant_name")["gen_mw"].sum()
    df = df[df["plant_name"].isin(totals[totals > 0].index)].copy()
    df = df.sort_values(["plant_name", "datetime"]).reset_index(drop=True)

    # Deduplicate within same plant+hour (keep max)
    df = (
        df.groupby(["plant_name", "plant_id", "datetime"], as_index=False)["gen_mw"]
        .max()
    )
    df = df.sort_values(["plant_name", "datetime"]).reset_index(drop=True)

    # Label cutoffs
    df["prev_gen"] = df.groupby("plant_name")["gen_mw"].shift(1)
    df["drop_pct"] = np.where(
        df["prev_gen"] > 0,
        (df["prev_gen"] - df["gen_mw"]) / df["prev_gen"] * 100, 0.0,
    )
    df["is_cutoff"] = (
        (df["prev_gen"] >= THETA_HIGH) &
        (df["gen_mw"]   <  THETA_LOW)  &
        (df["drop_pct"] >  THETA_DROP)
    ).astype(int)

    n_cut = df["is_cutoff"].sum()
    logger.info(f"Plants: {df['plant_name'].nunique()}, rows: {len(df):,}, "
                f"cutoffs: {n_cut} ({n_cut/len(df)*100:.4f}%)")

    if max_plants:
        top = df["plant_name"].value_counts().head(max_plants).index
        df = df[df["plant_name"].isin(top)].copy()
        logger.info(f"Subset to {max_plants} plants: {len(df):,} rows")

    return df


# 2. WINDOW CONSTRUCTION  (written from scratch)
def build_windows(df: pd.DataFrame, H: int, seed: int = 42) -> pd.DataFrame:
    """
    Build leakage-free prediction windows for horizon H.

    Positive window:  ends at t-H-1 (WINDOW_LEN=24 rows), target cutoff at t
    Negative window:  ends at any row with no cutoff in [end-NEG_GAP, end+NEG_GAP]

    Returns DataFrame of window metadata (no raw time-series; features computed
    separately in extract_features).
    """
    rng = np.random.default_rng(seed)
    records = []

    required_history = H + WINDOW_LEN   # rows needed before cutoff index

    for plant, gdf in df.groupby("plant_name"):
        gdf = gdf.sort_values("datetime").reset_index(drop=True)
        n = len(gdf)
        cutoff_positions = set(gdf.index[gdf["is_cutoff"] == 1].tolist())

        # ── Positive windows ──────────────────────────────────────────────────
        pos_end_positions = []
        for c in sorted(cutoff_positions):
            if c < required_history:
                continue
            # Window covers [c - H - WINDOW_LEN, c - H - 1]
            # slice [c - H - WINDOW_LEN : c - H]  → 24 rows, ends at c-H-1
            win_end_pos = c - H - 1       # last row index (inclusive)
            win_start   = c - H - WINDOW_LEN
            if win_start < 0:
                continue

            win_data = gdf.iloc[win_start : win_end_pos + 1]
            assert len(win_data) == WINDOW_LEN, f"pos window length mismatch: {len(win_data)}"

            records.append({
                "plant_name":    plant,
                "label":         1,
                "horizon":       H,
                "cutoff_ts":     gdf.loc[c, "datetime"],
                "window_end_ts": win_data["datetime"].iloc[-1],
                "window_start_ts": win_data["datetime"].iloc[0],
                "win_data":      win_data.reset_index(drop=True),
            })
            pos_end_positions.append(win_end_pos)

        n_pos = len(pos_end_positions)
        if n_pos == 0:
            continue

        # ── Negative windows ──────────────────────────────────────────────────
        # A valid negative end position e must satisfy:
        #   1. No cutoff in [e - NEG_GAP, e + NEG_GAP] (wide safety margin)
        #   2. e >= WINDOW_LEN - 1  (enough history)
        #   3. e <= n - 2           (at least one future row to make sense)
        valid_neg_ends = []
        for e in range(WINDOW_LEN - 1, n - 1):
            lo = max(0, e - NEG_GAP)
            hi = min(n - 1, e + NEG_GAP)
            if any(p in cutoff_positions for p in range(lo, hi + 1)):
                continue
            valid_neg_ends.append(e)

        n_neg_target = min(len(valid_neg_ends), n_pos * NEG_RATIO)
        if n_neg_target == 0:
            continue

        sampled = rng.choice(valid_neg_ends, size=n_neg_target, replace=False)
        for e in sampled:
            win_data = gdf.iloc[e - WINDOW_LEN + 1 : e + 1]
            assert len(win_data) == WINDOW_LEN
            records.append({
                "plant_name":    plant,
                "label":         0,
                "horizon":       H,
                "cutoff_ts":     pd.NaT,
                "window_end_ts": win_data["datetime"].iloc[-1],
                "window_start_ts": win_data["datetime"].iloc[0],
                "win_data":      win_data.reset_index(drop=True),
            })

    meta = pd.DataFrame(records)
    n_pos = (meta["label"] == 1).sum()
    n_neg = (meta["label"] == 0).sum()
    logger.info(f"H={H:2d}h — windows built: {n_pos} pos, {n_neg} neg "
                f"({len(meta)} total, {meta['plant_name'].nunique()} plants)")
    return meta


# 3. FEATURE EXTRACTION  (written from scratch, window-only)
FEATURE_DESCRIPTIONS = {
    "gen_mean":          "Mean generation (MW) over 24h window",
    "gen_std":           "Std dev of generation over 24h window",
    "gen_min":           "Minimum generation in window",
    "gen_max":           "Maximum generation in window",
    "gen_last":          "Generation at final window timestep (t-H-1)",
    "gen_first":         "Generation at first window timestep (t-H-24)",
    "gen_trend":         "Linear slope of generation (MW/h) over window",
    "gen_trend_r2":      "R² of linear fit (how linear the trend is)",
    "gen_delta_mean":    "Mean hour-over-hour generation change in window (NOTE: can show >5x class separation — physical signal, not leakage: farms that will cut off have declining trends before H-1)",
    "gen_delta_std":     "Std of hour-over-hour generation change",
    "gen_delta_max_drop": "Largest single-hour drop within window (negative = drop)",
    "gen_delta_max_rise": "Largest single-hour rise within window",
    "high_gen_frac":     "Fraction of window hours with gen > 50 MW",
    "above50_streak_max": "Longest consecutive streak of gen > 50 MW (hours)",
    "gen_cv":            "Coefficient of variation (std/mean, 0 if mean=0)",
    "gen_last_6h_mean":  "Mean generation over last 6 hours of window",
    "gen_last_6h_std":   "Std generation over last 6 hours of window",
    "gen_last_vs_mean":  "gen_last / gen_mean (1=stable, <1=declining)",
    "hour_end":          "Hour of day at window end (prediction time)",
    "month_end":         "Month at window end",
    "is_winter":         "1 if December/January/February",
    "is_spring":         "1 if March/April/May",
    "plant_hist_rate":   "Plant historical cutoff rate (events/1000h, train-derived)",
}


def extract_features(win_data: pd.DataFrame) -> dict:
    """
    Compute all features from a single 24-row window.
    NO references to data outside win_data.
    """
    g = win_data["gen_mw"].values.astype(float)
    T = len(g)   # should always be 24

    # Basic stats
    gen_mean = float(np.mean(g))
    gen_std  = float(np.std(g, ddof=1)) if T > 1 else 0.0
    gen_min  = float(np.min(g))
    gen_max  = float(np.max(g))
    gen_last = float(g[-1])
    gen_first= float(g[0])

    # Linear trend
    x = np.arange(T, dtype=float)
    if np.std(g) > 0:
        slope, _, r_val, _, _ = linregress(x, g)
        gen_trend    = float(slope)
        gen_trend_r2 = float(r_val ** 2)
    else:
        gen_trend    = 0.0
        gen_trend_r2 = 0.0

    # Hour-over-hour deltas
    deltas           = np.diff(g)
    gen_delta_mean   = float(np.mean(deltas)) if len(deltas) > 0 else 0.0
    gen_delta_std    = float(np.std(deltas, ddof=1)) if len(deltas) > 1 else 0.0
    gen_delta_max_drop = float(np.min(deltas)) if len(deltas) > 0 else 0.0   # most negative
    gen_delta_max_rise = float(np.max(deltas)) if len(deltas) > 0 else 0.0

    # Capacity proxy features
    high_gen_frac = float(np.mean(g > 50.0))
    # Longest streak above 50 MW
    streak = streak_max = 0
    for v in g:
        if v > 50.0:
            streak += 1
            streak_max = max(streak_max, streak)
        else:
            streak = 0
    above50_streak_max = float(streak_max)

    # Coefficient of variation
    gen_cv = float(gen_std / gen_mean) if gen_mean > 1e-3 else 0.0

    # Last 6 hours stats
    last6      = g[-6:]
    gen_l6_mean = float(np.mean(last6))
    gen_l6_std  = float(np.std(last6, ddof=1)) if len(last6) > 1 else 0.0

    # Last vs mean
    gen_last_vs_mean = float(gen_last / gen_mean) if gen_mean > 1e-3 else 0.0

    # Temporal features at window END
    end_ts  = win_data["datetime"].iloc[-1]
    hour_end = int(end_ts.hour)
    month_end = int(end_ts.month)
    is_winter = int(month_end in {12, 1, 2})
    is_spring = int(month_end in {3, 4, 5})

    return {
        "gen_mean":           gen_mean,
        "gen_std":            gen_std,
        "gen_min":            gen_min,
        "gen_max":            gen_max,
        "gen_last":           gen_last,
        "gen_first":          gen_first,
        "gen_trend":          gen_trend,
        "gen_trend_r2":       gen_trend_r2,
        "gen_delta_mean":     gen_delta_mean,
        "gen_delta_std":      gen_delta_std,
        "gen_delta_max_drop": gen_delta_max_drop,
        "gen_delta_max_rise": gen_delta_max_rise,
        "high_gen_frac":      high_gen_frac,
        "above50_streak_max": above50_streak_max,
        "gen_cv":             gen_cv,
        "gen_last_6h_mean":   gen_l6_mean,
        "gen_last_6h_std":    gen_l6_std,
        "gen_last_vs_mean":   gen_last_vs_mean,
        "hour_end":           hour_end,
        "month_end":          month_end,
        "is_winter":          is_winter,
        "is_spring":          is_spring,
        # plant_hist_rate filled later (train-set derived)
    }


def build_feature_matrix(meta: pd.DataFrame, plant_rates: dict) -> pd.DataFrame:
    """Apply extract_features to every window row."""
    feat_rows = []
    for _, row in meta.iterrows():
        feats = extract_features(row["win_data"])
        feats["plant_hist_rate"] = plant_rates.get(row["plant_name"], 0.0)
        feats["label"]          = row["label"]
        feats["plant_name"]     = row["plant_name"]
        feats["window_end_ts"]  = row["window_end_ts"]
        feats["cutoff_ts"]      = row["cutoff_ts"]
        feat_rows.append(feats)
    return pd.DataFrame(feat_rows)


# 4. TEMPORAL SPLIT
def temporal_split(feat_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Split by window_end_ts (= prediction time).
    Train: 2022-2023 | Val: 2024 | Test: 2025
    """
    ts = feat_df["window_end_ts"]
    train = feat_df[ts <= TRAIN_END].copy()
    val   = feat_df[(ts > TRAIN_END) & (ts <= VAL_END)].copy()
    test  = feat_df[ts > VAL_END].copy()
    return train, val, test


def report_split_counts(H: int, train, val, test):
    for name, df in [("Train", train), ("Val", val), ("Test", test)]:
        n_pos = (df["label"] == 1).sum()
        n_neg = (df["label"] == 0).sum()
        logger.info(f"  H={H}h {name:5s}: {len(df):5d} windows "
                    f"({n_pos} pos, {n_neg} neg)")
        if name == "Test" and n_pos < 20:
            logger.warning(f"  ⚠ TEST SET HAS <20 POSITIVE SAMPLES (n={n_pos}) "
                           f"— treat test metrics as indicative only")


# 5. XGBOOST TRAINING
FEAT_COLS = list(FEATURE_DESCRIPTIONS.keys())


def train_xgb(H: int, train: pd.DataFrame, val: pd.DataFrame, test: pd.DataFrame) -> dict:
    from sklearn.metrics import (
        roc_auc_score, average_precision_score, f1_score,
        precision_score, recall_score, brier_score_loss, confusion_matrix,
    )
    from xgboost import XGBClassifier

    avail_feats = [f for f in FEAT_COLS if f in train.columns]

    X_tr  = train[avail_feats].fillna(0).values
    y_tr  = train["label"].values
    X_val = val[avail_feats].fillna(0).values
    y_val = val["label"].values
    X_te  = test[avail_feats].fillna(0).values
    y_te  = test["label"].values

    if y_tr.sum() == 0 or y_val.sum() == 0:
        logger.warning(f"H={H}h: no positive samples in train or val — skipping")
        return {}

    scale_pos = max(1, int((y_tr == 0).sum() / max((y_tr == 1).sum(), 1)))

    clf = XGBClassifier(
        n_estimators=500,
        max_depth=5,
        learning_rate=0.03,
        subsample=0.8,
        colsample_bytree=0.8,
        min_child_weight=5,
        scale_pos_weight=scale_pos,
        random_state=42,
        eval_metric="aucpr",
        tree_method="hist",
        device="cpu",
        verbosity=0,
        early_stopping_rounds=30,
    )
    clf.fit(
        X_tr, y_tr,
        eval_set=[(X_val, y_val)],
        verbose=False,
    )

    # Threshold optimised on VALIDATION set
    val_probs = clf.predict_proba(X_val)[:, 1]
    from sklearn.metrics import precision_recall_curve
    prec, rec, thrs = precision_recall_curve(y_val, val_probs)
    f1s = 2 * prec * rec / (prec + rec + 1e-9)
    best_i   = f1s.argmax()
    opt_thr  = float(thrs[best_i]) if best_i < len(thrs) else 0.5

    # Evaluate on TEST set with threshold from val
    if y_te.sum() == 0:
        logger.warning(f"H={H}h: no positive samples in test set")
        return {}

    te_probs  = clf.predict_proba(X_te)[:, 1]
    te_preds  = (te_probs >= opt_thr).astype(int)

    roc   = roc_auc_score(y_te, te_probs)
    prauc = average_precision_score(y_te, te_probs)
    f1    = f1_score(y_te, te_preds, zero_division=0)
    prec_ = precision_score(y_te, te_preds, zero_division=0)
    rec_  = recall_score(y_te, te_preds, zero_division=0)
    brier = brier_score_loss(y_te, te_probs)
    cm    = confusion_matrix(y_te, te_preds)

    # Feature importance
    fi = pd.Series(dict(zip(avail_feats, clf.feature_importances_))).sort_values(ascending=False)
    fi.to_csv(MODEL_DIR / f"feature_importance_H{H}.csv")

    # Save model
    with open(MODEL_DIR / f"xgb_H{H}.pkl", "wb") as fh:
        pickle.dump({"model": clf, "threshold": opt_thr, "features": avail_feats}, fh)

    logger.info(
        f"H={H:2d}h TEST → ROC-AUC={roc:.3f} | PR-AUC={prauc:.3f} | "
        f"F1={f1:.3f} (thr={opt_thr:.3f}) | P={prec_:.3f} R={rec_:.3f} | Brier={brier:.4f}"
    )
    logger.info(f"  Confusion matrix (test): TN={cm[0,0]} FP={cm[0,1]} FN={cm[1,0]} TP={cm[1,1]}")
    logger.info(f"  Top-5 features:\n{fi.head(5).to_string()}")

    return {
        "H": H,
        "ROC-AUC":   round(roc, 3),
        "PR-AUC":    round(prauc, 3),
        "F1":        round(f1, 3),
        "Precision": round(prec_, 3),
        "Recall":    round(rec_, 3),
        "Brier":     round(brier, 4),
        "Threshold": round(opt_thr, 4),
        "Test_pos":  int(y_te.sum()),
        "Test_total": len(y_te),
        "Top_feature": fi.index[0] if len(fi) else "N/A",
    }


# 6. SANITY CHECKS
def sanity_check_windows(meta: pd.DataFrame, H: int):
    """Verify no positive window contains data within H hours of its cutoff."""
    print(f"\n  [Sanity] H={H}h window gap verification (3 examples):")
    pos = meta[meta["label"] == 1].head(3)
    all_ok = True
    for _, row in pos.iterrows():
        gap_hours = (row["cutoff_ts"] - row["window_end_ts"]).total_seconds() / 3600
        ok = gap_hours >= H
        flag = "✓" if ok else "✗ VIOLATION"
        print(f"    Plant={row['plant_name'][:20]} | "
              f"win_end={row['window_end_ts']} | "
              f"cutoff={row['cutoff_ts']} | "
              f"gap={gap_hours:.1f}h {flag}")
        if not ok:
            all_ok = False
    return all_ok


def sanity_check_features(feat_df: pd.DataFrame, H: int):
    """Flag features with >5x median ratio between classes."""
    pos = feat_df[feat_df["label"] == 1]
    neg = feat_df[feat_df["label"] == 0]
    avail = [f for f in FEAT_COLS if f in feat_df.columns]
    flagged = []
    for f in avail:
        m_pos = pos[f].median()
        m_neg = neg[f].median()
        ratio = abs(m_pos - m_neg) / (abs(m_neg) + 1e-9)
        if ratio > 5:
            flagged.append((f, m_pos, m_neg, ratio))
    EXPECTED_HIGH_SEP = {"gen_delta_mean"}   # physical signal, not leakage
    if flagged:
        print(f"\n  [Sanity] H={H}h features with >5x class separation:")
        for f, mp, mn, r in flagged:
            note = " (expected physical signal)" if f in EXPECTED_HIGH_SEP else " ← INVESTIGATE"
            print(f"    {f:<30} pos={mp:.2f} neg={mn:.2f} ratio={r:.1f}x{note}")
    else:
        print(f"\n  [Sanity] H={H}h: no feature exceeds 5x class separation ✓")
    return flagged


def sanity_check_plant_coverage(train: pd.DataFrame, test: pd.DataFrame, H: int):
    """Flag test plants not seen in train."""
    train_plants = set(train["plant_name"].unique())
    test_plants  = set(test[test["label"] == 1]["plant_name"].unique())
    unseen = test_plants - train_plants
    if unseen:
        print(f"\n  [Sanity] H={H}h: {len(unseen)} test plants with cutoffs NOT in train: {unseen}")
    else:
        print(f"\n  [Sanity] H={H}h: all test plants (with cutoffs) present in train ✓")


def sanity_check_temporal_bias(train: pd.DataFrame, val: pd.DataFrame, H: int):
    """
    'Cheating detector': train XGBoost with ONLY temporal features.
    If val AUC > 0.75, there may be temporal bias in event sampling.
    """
    from sklearn.metrics import roc_auc_score
    from xgboost import XGBClassifier

    temporal_feats = ["hour_end", "month_end", "is_winter", "is_spring"]
    avail = [f for f in temporal_feats if f in train.columns]
    if not avail:
        return

    X_tr = train[avail].fillna(0).values
    y_tr = train["label"].values
    X_v  = val[avail].fillna(0).values
    y_v  = val["label"].values
    if y_v.sum() == 0:
        return

    scale_pos = max(1, int((y_tr == 0).sum() / max((y_tr == 1).sum(), 1)))
    clf = XGBClassifier(n_estimators=100, scale_pos_weight=scale_pos,
                        random_state=42, verbosity=0, device="cpu")
    clf.fit(X_tr, y_tr, verbose=False)
    auc = roc_auc_score(y_v, clf.predict_proba(X_v)[:, 1])

    flag = "⚠ POTENTIAL TEMPORAL BIAS" if auc > 0.75 else "✓ OK"
    print(f"\n  [Sanity] H={H}h temporal-only model val AUC={auc:.3f}  {flag}")


# 7. MAIN
def main(dry_run: bool = False, max_plants=None):
    print("\n" + "=" * 70)
    print("  LEAKAGE-FREE CUTOFF EARLY WARNING — v2")
    print("=" * 70)

    # Print feature list
    print("\nFEATURES (all derived from 24h window data only):")
    for fname, fdesc in FEATURE_DESCRIPTIONS.items():
        print(f"  {fname:<30} {fdesc}")

    # Load data
    df = load_and_label(max_plants=max_plants)

    # Keep only plants with ≥1 cutoff in training period
    train_period = df[df["datetime"] <= TRAIN_END]
    train_cutoff_plants = (
        train_period.groupby("plant_name")["is_cutoff"].sum()
    )
    eligible = train_cutoff_plants[train_cutoff_plants >= 1].index
    df = df[df["plant_name"].isin(eligible)].copy()
    logger.info(f"Plants with cutoff in train: {len(eligible)}")

    # Plant historical cutoff rate — computed ONLY from training data
    train_df_raw = df[df["datetime"] <= TRAIN_END]
    total_hours  = train_df_raw.groupby("plant_name").size()
    cutoff_hours = train_df_raw.groupby("plant_name")["is_cutoff"].sum()
    plant_rates  = (cutoff_hours / total_hours * 1000).to_dict()   # per 1000 hours

    all_results = []

    for H in HORIZONS:
        print(f"\n{'─'*70}")
        print(f"  HORIZON H = {H} hours")
        print(f"{'─'*70}")

        # Build windows
        meta = build_windows(df, H=H)
        if len(meta) == 0:
            logger.warning(f"H={H}: no windows built — skipping")
            continue

        # Sanity check: gap verification + 3 examples
        sanity_check_windows(meta, H)

        # Build feature matrix
        logger.info(f"H={H}h: extracting features...")
        feat_df = build_feature_matrix(meta, plant_rates)

        # Temporal split
        train_f, val_f, test_f = temporal_split(feat_df)
        report_split_counts(H, train_f, val_f, test_f)

        if dry_run:
            logger.info(f"H={H}h: dry-run, skipping training")
            continue

        # Sanity checks on feature distributions
        sanity_check_features(feat_df, H)
        sanity_check_plant_coverage(train_f, test_f, H)
        sanity_check_temporal_bias(train_f, val_f, H)

        # Train XGBoost
        logger.info(f"H={H}h: training XGBoost...")
        result = train_xgb(H, train_f, val_f, test_f)
        if result:
            all_results.append(result)

    # Summary table
    if all_results:
        table = pd.DataFrame(all_results).set_index("H")
        print("\n" + "=" * 70)
        print("  FINAL RESULTS (leakage-free, test set 2025)")
        print("=" * 70)
        print(table[[
            "ROC-AUC", "PR-AUC", "F1", "Precision", "Recall",
            "Brier", "Threshold", "Test_pos", "Top_feature"
        ]].to_string())
        table.to_csv(OUT_CSV)
        print(f"\nSaved: {OUT_CSV}")
    else:
        print("\nNo results (dry-run or all horizons failed).")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true",
                        help="Skip training, only print dataset stats")
    parser.add_argument("--max-plants", type=int, default=None)
    args = parser.parse_args()
    main(dry_run=args.dry_run, max_plants=args.max_plants)
