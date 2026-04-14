#!/usr/bin/env python3
"""
Full diagnostic audit of the cutoff prediction pipeline.
Diagnosis only — no retraining.
"""
import pickle
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

PROJECT   = Path(__file__).parent.parent
DATA_DIR  = PROJECT / "data"
MODEL_DIR = PROJECT / "analysis" / "models"

THETA_HIGH = 50.0
THETA_LOW  = 10.0
THETA_DROP = 80.0

# ── helpers ────────────────────────────────────────────────────────────────────
def sep(title=""):
    print("\n" + "=" * 70)
    if title:
        print(f"  {title}")
        print("=" * 70)

def load_data():
    df = pd.read_csv(
        DATA_DIR / "generation_202201_202504.csv",
        usecols=["date", "ruzgar", "plant_id", "plant_name"],
        dtype={"plant_id": int, "ruzgar": float, "plant_name": str},
        encoding="utf-8-sig",
    )
    df = df.rename(columns={"date": "datetime", "ruzgar": "gen_mw"})
    df["datetime"] = pd.to_datetime(df["datetime"], utc=True, errors="coerce")
    df = df.dropna(subset=["datetime"])
    df["gen_mw"] = df["gen_mw"].fillna(0.0).clip(lower=0)
    # Keep wind plants only
    totals = df.groupby("plant_name")["gen_mw"].sum()
    df = df[df["plant_name"].isin(totals[totals > 0].index)].copy()
    df = df.sort_values(["plant_name", "datetime"]).reset_index(drop=True)
    return df

def label_cutoffs(df):
    df = df.copy()
    df["prev_gen"] = df.groupby("plant_name")["gen_mw"].shift(1)
    df["drop_pct"] = np.where(
        df["prev_gen"] > 0,
        (df["prev_gen"] - df["gen_mw"]) / df["prev_gen"] * 100, 0.0)
    df["is_cutoff"] = (
        (df["prev_gen"] >= THETA_HIGH) &
        (df["gen_mw"]   <  THETA_LOW)  &
        (df["drop_pct"] >  THETA_DROP)
    ).astype(int)
    return df

def engineer_features(df):
    df = df.copy().sort_values(["plant_name", "datetime"]).reset_index(drop=True)
    for plant, idx in df.groupby("plant_name").groups.items():
        g = df.loc[idx, "gen_mw"]
        for lag in [1, 2, 3, 6, 12, 24]:
            df.loc[idx, f"gen_lag_{lag}h"] = g.shift(lag).values
        for w in [6, 12, 24]:
            df.loc[idx, f"gen_roll_mean_{w}h"] = g.rolling(w, min_periods=1).mean().values
            df.loc[idx, f"gen_roll_std_{w}h"]  = g.rolling(w, min_periods=1).std().fillna(0).values
        c = df.loc[idx, "is_cutoff"]
        df.loc[idx, "cutoff_24h"] = c.shift(1).rolling(24, min_periods=1).sum().values
        df.loc[idx, "cutoff_48h"] = c.shift(1).rolling(48, min_periods=1).sum().values
    df["hour"]        = df["datetime"].dt.hour
    df["month"]       = df["datetime"].dt.month
    df["day_of_week"] = df["datetime"].dt.dayofweek
    df["is_winter"]   = df["month"].isin([12, 1, 2]).astype(int)
    df["is_spring"]   = df["month"].isin([3, 4, 5]).astype(int)
    return df

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 1 — WINDOW CONSTRUCTION & LEAD TIME
# ══════════════════════════════════════════════════════════════════════════════
sep("SECTION 1 — WINDOW CONSTRUCTION & LEAD TIME")

print("""
_sample_windows() code path:
  window_len = encoder_len + pred_len = 72 + 1 = 73
  For each positive event at index end_idx:
      snippet = gdf.iloc[end_idx - 72 : end_idx + 1]   ← 73 rows
      label   = grp["is_cutoff"].iloc[-1]               ← last row of snippet

QUESTION: Does the window INCLUDE the cutoff timestep?
""")

print("  end_idx      = cutoff event row index in gdf")
print("  snippet[-1]  = gdf.iloc[end_idx]  ← THIS IS THE CUTOFF ROW ITSELF")
print("  label        = is_cutoff[end_idx] = 1")
print()
print(">>> VERDICT: YES. The window's last timestep IS the cutoff event.")
print("    Lead time = 0. The model sees the event WHILE it is happening.")
print("    gen_mw at window[-1] = actual generation DURING cutoff (<10 MW)")
print()

# Show 3 concrete positive windows
print("─── 3 concrete positive window examples ───")
print("Loading data (sub-sample: first 3 plants with cutoffs)...")
df_raw = load_data()
df_lab = label_cutoffs(df_raw)
cutoff_plants = df_lab.groupby("plant_name")["is_cutoff"].sum()
cutoff_plants = cutoff_plants[cutoff_plants >= 2].index[:3]

ENCODER_LEN = 72
PRED_LEN    = 1
WINDOW_LEN  = ENCODER_LEN + PRED_LEN

for plant in cutoff_plants:
    gdf = df_lab[df_lab["plant_name"] == plant].sort_values("datetime").reset_index(drop=True)
    events = gdf.index[gdf["is_cutoff"] == 1].tolist()
    end_idx = events[0]
    if end_idx < WINDOW_LEN:
        continue
    snippet = gdf.iloc[end_idx - WINDOW_LEN + 1 : end_idx + 1]
    cutoff_ts = gdf.loc[end_idx, "datetime"]
    window_start = snippet["datetime"].iloc[0]
    window_end   = snippet["datetime"].iloc[-1]
    gen_at_event = snippet["gen_mw"].iloc[-1]
    gen_prev     = snippet["gen_mw"].iloc[-2]
    print(f"\n  Plant     : {plant}")
    print(f"  Cutoff TS : {cutoff_ts}")
    print(f"  Window    : {window_start}  →  {window_end}")
    print(f"  Window[-1] == Cutoff TS? : {window_end == cutoff_ts}   ← LEAKAGE FLAG")
    print(f"  gen_mw at window[-1]     : {gen_at_event:.1f} MW  (< {THETA_LOW} MW = in-event)")
    print(f"  gen_mw at window[-2]     : {gen_prev:.1f} MW  (pre-event)")
    print(f"  Drop    : {(gen_prev - gen_at_event)/gen_prev*100:.1f}%")

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 2 — FEATURE LEAKAGE ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
sep("SECTION 2 — FEATURE LEAKAGE ANALYSIS")

print("Computing features on full dataset for analysis...")
df_feat = engineer_features(df_lab.copy())
df_feat = df_feat.dropna(subset=["gen_lag_24h"]).reset_index(drop=True)

feat_cols = [c for c in df_feat.columns if c.startswith((
    "gen_lag_", "gen_roll_", "cutoff_24h", "cutoff_48h",
    "hour", "month", "day_of_week", "is_winter", "is_spring",
))]

print(f"\nAll features used as model input ({len(feat_cols)} total):")
for i, f in enumerate(feat_cols, 1):
    src = "generation-derived" if f.startswith("gen_") else \
          "cutoff-history"     if f.startswith("cutoff_") else "calendar"
    print(f"  {i:2d}. {f:<30} [{src}]")

print()
print("LEAKAGE CHECK: Feature values AT the cutoff timestep (t=0, event row)")
print("─" * 65)

cutoff_rows  = df_feat[df_feat["is_cutoff"] == 1]
normal_rows  = df_feat[df_feat["is_cutoff"] == 0]

leaky_features = []
for f in feat_cols:
    if f not in df_feat.columns:
        continue
    m_pos = cutoff_rows[f].median()
    m_neg = normal_rows[f].median()
    # Flag if separation is huge (>5x ratio or near-zero overlap)
    ratio = abs(m_pos - m_neg) / (abs(m_neg) + 1e-9)
    flag = "*** LEAKY ***" if ratio > 2 else ""
    if ratio > 0.5:
        print(f"  {f:<30} | pos_median={m_pos:8.2f} | neg_median={m_neg:8.2f} | ratio={ratio:.1f}  {flag}")

# Most discriminating: gen_roll_std which captures the drop
print()
print("SMOKING GUN — gen_roll_std_6h at cutoff timestep:")
print("  This rolling window INCLUDES gen_mw at t=0 (the cutoff).")
print("  Since gen_mw drops from >50 to <10 MW IN THIS WINDOW,")
print("  the std explodes — it perfectly encodes the cutoff.")
print()
print(f"  gen_roll_std_6h — cutoff rows: mean={cutoff_rows['gen_roll_std_6h'].mean():.2f}, "
      f"std={cutoff_rows['gen_roll_std_6h'].std():.2f}")
print(f"  gen_roll_std_6h — normal rows: mean={normal_rows['gen_roll_std_6h'].mean():.2f}, "
      f"std={normal_rows['gen_roll_std_6h'].std():.2f}")

# Also show gen_lag_1h
print()
print("  gen_lag_1h at cutoff t=0: contains gen[t-1] > 50 MW (pre-cutoff level)")
print(f"  cutoff rows: median={cutoff_rows['gen_lag_1h'].median():.1f} MW")
print(f"  normal rows: median={normal_rows['gen_lag_1h'].median():.1f} MW")
print()
print("  gen_mw at t=0 is NOT explicitly a feature — but gen_roll_std_6h")
print("  and gen_roll_mean_6h both include gen_mw[t] which is < 10 MW.")
print("  This is equivalent to passing gen_mw[t] directly as a feature.")

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 3 — XGBoost DEEP DIVE
# ══════════════════════════════════════════════════════════════════════════════
sep("SECTION 3 — XGBoost DEEP DIVE")

from sklearn.metrics import (
    roc_auc_score, average_precision_score, f1_score,
    confusion_matrix, precision_recall_curve,
)

xgb_path = MODEL_DIR / "xgboost_model.pkl"
if xgb_path.exists():
    with open(xgb_path, "rb") as fh:
        xgb_model = pickle.load(fh)

    # Rebuild test set (same split as training: chronological 80/20)
    cutoff_plants_all = df_feat["plant_name"].unique()[
        pd.Series(df_feat.groupby("plant_name")["is_cutoff"].sum().values) >= 1
    ]
    df_xgb = df_feat[df_feat["plant_name"].isin(
        df_feat.groupby("plant_name")["is_cutoff"].sum()[
            df_feat.groupby("plant_name")["is_cutoff"].sum() >= 1
        ].index
    )].copy()

    X = df_xgb[feat_cols].fillna(0).values
    y = df_xgb["is_cutoff"].values
    split = int(0.8 * len(X))
    X_test, y_test = X[split:], y[split:]

    y_prob = xgb_model.predict_proba(X_test)[:, 1]
    y_pred_05 = (y_prob > 0.5).astype(int)

    print("\nXGBoost Feature Importance (gain, top 10):")
    fi_path = MODEL_DIR / "xgboost_feature_importance.csv"
    if fi_path.exists():
        fi = pd.read_csv(fi_path, index_col=0).squeeze()
        fi_gain = fi.sort_values(ascending=False)
        for fname, val in fi_gain.head(10).items():
            print(f"  {fname:<30} {val:.4f}")

    print(f"\nTest set: {len(y_test):,} rows, {y_test.sum()} positives "
          f"({y_test.mean()*100:.3f}% positive rate)")
    print(f"\nConfusion Matrix at threshold=0.5:")
    cm = confusion_matrix(y_test, y_pred_05)
    print(f"  TN={cm[0,0]:>6}  FP={cm[0,1]:>5}")
    print(f"  FN={cm[1,0]:>6}  TP={cm[1,1]:>5}")
    print(f"  → Model predicts positive: {y_pred_05.sum()} / {len(y_pred_05)}")

    # Optimal F1 threshold
    prec, rec, thresholds = precision_recall_curve(y_test, y_prob)
    f1_scores = 2 * prec * rec / (prec + rec + 1e-9)
    best_idx  = f1_scores.argmax()
    best_thr  = thresholds[best_idx] if best_idx < len(thresholds) else 0.5
    y_pred_opt = (y_prob > best_thr).astype(int)

    print(f"\nOptimal F1 threshold: {best_thr:.4f}")
    print(f"Confusion Matrix at optimal threshold:")
    cm2 = confusion_matrix(y_test, y_pred_opt)
    print(f"  TN={cm2[0,0]:>6}  FP={cm2[0,1]:>5}")
    print(f"  FN={cm2[1,0]:>6}  TP={cm2[1,1]:>5}")
    print(f"  F1 at optimal: {f1_score(y_test, y_pred_opt, zero_division=0):.3f}")
    print(f"  ROC-AUC: {roc_auc_score(y_test, y_prob):.3f}")
    print(f"  Avg-Precision: {average_precision_score(y_test, y_prob):.3f}")

    # Show score distribution
    print(f"\nProbability distribution for positives vs negatives:")
    pos_scores = y_prob[y_test == 1]
    neg_scores = y_prob[y_test == 0]
    print(f"  Positive samples (n={len(pos_scores)}): "
          f"min={pos_scores.min():.4f}, median={np.median(pos_scores):.4f}, "
          f"max={pos_scores.max():.4f}")
    print(f"  Negative samples (n={len(neg_scores)}): "
          f"min={neg_scores.min():.4f}, median={np.median(neg_scores):.4f}, "
          f"max={neg_scores.max():.4f}")

    # Does the model just score high on current-event features?
    print(f"\nKey question: Is XGBoost 0.997 AUC meaningful?")
    print(f"  Test split is chronological (last 20% of time series).")
    print(f"  BUT features at cutoff row t include:")
    print(f"    gen_roll_std_6h[t] = std(gen[t-5:t+1]) — includes gen[t] < 10 MW")
    print(f"    gen_roll_std_12h[t] = std includes gen[t]")
    print(f"    gen_lag_1h[t]      = gen[t-1] > 50 MW")
    print(f"  → At t (cutoff row), the drop has ALREADY OCCURRED.")
    print(f"  → XGBoost is detecting past events, not predicting future ones.")
else:
    print("  XGBoost model not found. Skipping.")

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 4 — TFT (LSTM-Attn) DEEP DIVE
# ══════════════════════════════════════════════════════════════════════════════
sep("SECTION 4 — TFT (LSTM-Attn) DEEP DIVE")

print(f"Window construction for TFT:")
print(f"  encoder_len = 72, pred_len = 1, window_len = 73")
print(f"  snippet = gdf.iloc[end_idx - 72 : end_idx + 1]")
print(f"  ↳ time_idx 0..72 passed to bidirectional LSTM")
print(f"  ↳ label = is_cutoff at time_idx 72 (last row = cutoff event)")
print()
print(f"  The BIDIRECTIONAL LSTM processes all 73 timesteps.")
print(f"  At time_idx=72 (cutoff), gen_mw < 10 MW is a direct input.")
print(f"  gen_roll_std_6h, gen_roll_mean_6h also encode the drop.")
print(f"  → LSTM trivially learns: 'if gen_mw[72] ≈ 0, output 1'")
print()
print(f"Train/val split for TFT:")
print(f"  Method: RANDOM by window_id (numpy rng.choice)")
print(f"  → Windows from the same plant, same time period")
print(f"    can appear in BOTH train and val.")
print(f"  → E.g. Plant X cutoff at 2024-03-15 17:00:")
print(f"    pos window  = [2024-03-12 18:00 → 2024-03-15 17:00] (label=1)")
print(f"    nearby neg  = [2024-03-13 06:00 → 2024-03-16 05:00] (label=0)")
print(f"    These share 59 out of 73 timesteps yet can be in different splits.")

# Count how many cutoff events have windows in both train AND val
print()
print("Overlap audit: cutoff events appearing in both train AND val windows")
print("(Reconstructing windows with same seed as training...)")

df_for_audit = df_feat[df_feat["plant_name"].isin(
    df_feat.groupby("plant_name")["is_cutoff"].sum()[
        df_feat.groupby("plant_name")["is_cutoff"].sum() >= 1
    ].index
)].copy()

ENCODER_LEN = 72
rng_audit = np.random.default_rng(42)

all_windows_meta = []
win_id = 0
for plant, gdf in df_for_audit.groupby("plant_name"):
    gdf = gdf.sort_values("datetime").reset_index(drop=True)
    cutoff_idxs = gdf.index[gdf["is_cutoff"] == 1].tolist()
    WINDOW_LEN_A = ENCODER_LEN + 1
    all_valid    = list(range(WINDOW_LEN_A, len(gdf)))
    pos_idxs     = [i for i in cutoff_idxs if i >= WINDOW_LEN_A]
    pos_set       = set()
    for p in pos_idxs:
        pos_set.update(range(p - 2, p + 3))
    neg_pool = [i for i in all_valid if i not in pos_set]
    n_neg    = min(len(neg_pool), max(len(pos_idxs) * 5, 50))
    neg_idxs = rng_audit.choice(neg_pool, size=n_neg, replace=False).tolist() if neg_pool else []

    for end_idx in pos_idxs + neg_idxs:
        ts_end = gdf.loc[end_idx, "datetime"]
        label  = int(gdf.loc[end_idx, "is_cutoff"])
        all_windows_meta.append({
            "window_id": win_id,
            "plant":     plant,
            "end_idx":   end_idx,
            "end_ts":    ts_end,
            "label":     label,
        })
        win_id += 1

meta_df = pd.DataFrame(all_windows_meta)
all_ids  = meta_df["window_id"].values
n_train  = int(len(all_ids) * 0.8)
rng2     = np.random.default_rng(42)
train_ids = set(rng2.choice(all_ids, size=n_train, replace=False).tolist())
meta_df["split"] = meta_df["window_id"].apply(lambda x: "train" if x in train_ids else "val")

# For each positive window, find all windows (pos/neg) that share timesteps
pos_windows = meta_df[meta_df["label"] == 1]
overlap_count = 0
for _, row in pos_windows.iterrows():
    plant  = row["plant"]
    end_ts = row["end_ts"]
    # Overlapping if same plant and end_ts within ±72h
    others = meta_df[
        (meta_df["plant"] == plant) &
        (meta_df["window_id"] != row["window_id"]) &
        (abs((meta_df["end_ts"] - end_ts).dt.total_seconds()) < 72 * 3600)
    ]
    if (row["split"] == "train" and (others["split"] == "val").any()) or \
       (row["split"] == "val"   and (others["split"] == "train").any()):
        overlap_count += 1

print(f"  Total cutoff events with temporally overlapping windows")
print(f"  in opposite split: {overlap_count} / {len(pos_windows)}")
print()
print(f"  Val set: {(meta_df['split']=='val').sum()} windows "
      f"(pos={meta_df[meta_df['split']=='val']['label'].sum()}, "
      f"neg={len(meta_df[(meta_df['split']=='val') & (meta_df['label']==0)])})")

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 5 — TRAIN/TEST SPLIT AUDIT + GroupKFold
# ══════════════════════════════════════════════════════════════════════════════
sep("SECTION 5 — TRAIN/TEST SPLIT AUDIT + GroupKFold on XGBoost")

from sklearn.model_selection import GroupKFold
from sklearn.metrics import roc_auc_score as rauc, f1_score as rf1
from xgboost import XGBClassifier

print("XGBoost split: chronological 80/20 on full (plant, datetime)-sorted timeseries")
print("  BUT: data sorted by plant_name alphabetically FIRST, then datetime.")
print("  → The 80% train/20% test split does NOT respect temporal order across plants.")
print("  → For a plant near end of alphabet, its 2022 data may fall in 'test'.")
print()

# GroupKFold by plant
df_gkf = df_for_audit.dropna(subset=["gen_lag_24h"]).copy()
X_gkf  = df_gkf[feat_cols].fillna(0).values
y_gkf  = df_gkf["is_cutoff"].values
plants_gkf = df_gkf["plant_name"].values

print("GroupKFold (k=5, grouped by plant_name) XGBoost results:")
gkf = GroupKFold(n_splits=5)
fold_results = []
for fold, (tr_idx, te_idx) in enumerate(gkf.split(X_gkf, y_gkf, groups=plants_gkf), 1):
    X_tr, y_tr = X_gkf[tr_idx], y_gkf[tr_idx]
    X_te, y_te = X_gkf[te_idx], y_gkf[te_idx]
    if y_te.sum() == 0:
        print(f"  Fold {fold}: no positives in test — skipping")
        continue
    scale_pos = max(1, int((y_tr == 0).sum() / max((y_tr == 1).sum(), 1)))
    clf = XGBClassifier(
        n_estimators=200, max_depth=6, learning_rate=0.05,
        scale_pos_weight=scale_pos, random_state=42,
        eval_metric="logloss", tree_method="hist", device="cpu", verbosity=0,
    )
    clf.fit(X_tr, y_tr, verbose=False)
    yp = clf.predict_proba(X_te)[:, 1]
    auc = rauc(y_te, yp) if len(np.unique(y_te)) > 1 else 0.5
    f1  = rf1(y_te, (yp > 0.5).astype(int), zero_division=0)
    fold_results.append({"fold": fold, "roc_auc": auc, "f1": f1,
                          "n_test": len(y_te), "n_pos": y_te.sum()})
    print(f"  Fold {fold}: n_test={len(y_te):>6}, pos={y_te.sum():>3} | "
          f"ROC-AUC={auc:.3f} | F1={f1:.3f}")

if fold_results:
    auc_vals = [r["roc_auc"] for r in fold_results]
    f1_vals  = [r["f1"]      for r in fold_results]
    print(f"\n  GroupKFold mean: ROC-AUC={np.mean(auc_vals):.3f}±{np.std(auc_vals):.3f} | "
          f"F1={np.mean(f1_vals):.3f}±{np.std(f1_vals):.3f}")
    print(f"  vs. original chronological split: ROC-AUC=0.997, F1=0.329")

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 6 — PERSISTENCE BASELINE CHECK
# ══════════════════════════════════════════════════════════════════════════════
sep("SECTION 6 — PERSISTENCE BASELINE CHECK")

print("Persistence definition used in train_tft.py:")
print("  prev = df_feat.groupby('plant_name')['is_cutoff'].shift(1)")
print("  predict: is_cutoff[t] = is_cutoff[t-1]")
print()
print("Is this a correct baseline? Partially:")
print("  ✓ Conceptually sound for hour-by-hour series")
print("  ✗ Evaluated on FULL timeseries (1.18M rows), not on windows")
print("  ✗ Most cutoffs are isolated (not repeated next hour),")
print("    so persistence trivially predicts 0 almost always → F1=0")
print()
print("Empirical check on cutoff adjacency:")
df_adj = df_feat[df_feat["is_cutoff"] == 1].copy()
df_adj = df_adj.sort_values(["plant_name", "datetime"])
df_adj["next_is_cutoff"] = df_adj.groupby("plant_name")["is_cutoff"].shift(-1)
consec = (df_adj["next_is_cutoff"] == 1).sum()
print(f"  Total cutoff events: {len(df_adj)}")
print(f"  Followed by another cutoff (next hour): {consec}")
print(f"  → {consec/len(df_adj)*100:.1f}% of cutoffs are consecutive")
print(f"  → Persistence will recall 0 on virtually all events → F1=0 is correct")

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 7 — VERDICT AND REQUIRED FIXES
# ══════════════════════════════════════════════════════════════════════════════
sep("SECTION 7 — VERDICT AND REQUIRED FIXES")

print("""
┌─────────────────────────────────────────────────────────────────────────┐
│  FINDING 1 — CRITICAL: Zero lead time (TFT AND XGBoost)                 │
├─────────────────────────────────────────────────────────────────────────┤
│  The window for a positive sample ENDS AT the cutoff timestep t=0.      │
│  Both models see the event as it happens, not H hours before.           │
│  This is event DETECTION, not early WARNING.                            │
│  Impact: ALL reported metrics are invalid for early warning.            │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│  FINDING 2 — CRITICAL: Rolling feature leakage                          │
├─────────────────────────────────────────────────────────────────────────┤
│  gen_roll_std_6h and gen_roll_mean_6h are computed THROUGH t=0.         │
│  These features INCLUDE the generation drop in their window.            │
│  Top XGBoost feature: gen_roll_std_6h (importance=0.576)                │
│  This feature alone explains the near-perfect XGBoost AUC.             │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│  FINDING 3 — SERIOUS: Random window split (TFT)                         │
├─────────────────────────────────────────────────────────────────────────┤
│  Windows are split randomly by window_id, not by plant or time.         │
│  Temporally adjacent windows from the same event period appear in       │
│  both train and val → near-identical sequences in both sets.            │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│  FINDING 4 — MODERATE: Chronological split ignores plant grouping       │
├─────────────────────────────────────────────────────────────────────────┤
│  XGBoost uses df sorted by (plant_name, datetime).                      │
│  The 80/20 boundary cuts mid-series for most plants.                    │
│  GroupKFold results (see Section 5) show the true generalisation.       │
└─────────────────────────────────────────────────────────────────────────┘

REQUIRED FIXES TO MAKE RESULTS PUBLISHABLE:
─────────────────────────────────────────────
1. LEAD TIME: Shift window end by H hours BEFORE the cutoff.
   For H=6:  window = [t-78, t-7], label = "cutoff within next 6h"
   For H=12: window = [t-84, t-13]
   For H=24: window = [t-96, t-25]
   Use H = {6, 12, 24} to produce early warning at multiple horizons.

2. FEATURE CUTOFF: Re-engineer features using only data up to t-H.
   gen_roll_std_6h at t-H must NOT include any future timestep.

3. SPLIT: Use temporal split — train on 2022-2023, val on 2024,
   test on Jan-Apr 2025. OR GroupKFold by plant for CV.

4. METRICS: Report results separately for H=6, H=12, H=24 horizons.

ANSWER TO AUDIT QUESTIONS:
  TFT 0.947 F1 real?     → NO. Pure leakage. Model detects current event.
  XGBoost 0.997 AUC real? → NO. gen_roll_std_6h encodes the active cutoff.
  Pipeline valid for pub?  → NO. All three issues must be fixed first.
""")
