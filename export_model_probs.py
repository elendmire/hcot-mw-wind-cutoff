#!/usr/bin/env python3
"""Export test-set probabilities from saved v2 XGBoost models for ROC/PR curves."""
import pickle
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent / "analysis"))

from train_v2 import (
    load_and_label, build_windows, build_feature_matrix, temporal_split,
    TRAIN_END, HORIZONS, FEAT_COLS,
)

PROJECT   = Path(__file__).parent
MODEL_DIR = PROJECT / "analysis" / "models" / "v2"


def get_plant_rates(df):
    train_df = df[df["datetime"] <= TRAIN_END]
    total_hours  = train_df.groupby("plant_name").size()
    cutoff_hours = train_df.groupby("plant_name")["is_cutoff"].sum()
    return (cutoff_hours / total_hours * 1000).to_dict()


if __name__ == "__main__":
    print("Loading data…")
    df = load_and_label()

    # Same eligibility filter as main()
    train_period = df[df["datetime"] <= TRAIN_END]
    eligible = (
        train_period.groupby("plant_name")["is_cutoff"].sum()
        .pipe(lambda s: s[s >= 1].index)
    )
    df = df[df["plant_name"].isin(eligible)].copy()
    plant_rates = get_plant_rates(df)

    for H in HORIZONS:
        print(f"\nH={H}h …")
        meta = build_windows(df, H=H)
        feat_df = build_feature_matrix(meta, plant_rates)
        _, _, te = temporal_split(feat_df)

        avail = [f for f in FEAT_COLS if f in te.columns]
        X_te = te[avail].values
        y_te = te["label"].values

        mp = MODEL_DIR / f"xgb_H{H}.pkl"
        if not mp.exists():
            print(f"  Model not found: {mp} — skipping")
            continue

        with open(mp, "rb") as fh:
            saved = pickle.load(fh)

        clf = saved["model"] if isinstance(saved, dict) else saved
        saved_feats = saved.get("features", avail) if isinstance(saved, dict) else avail
        X_te_aligned = te[[f for f in saved_feats if f in te.columns]].values
        y_prob = clf.predict_proba(X_te_aligned)[:, 1]
        out = MODEL_DIR / f"xgb_H{H}_probs.csv"
        pd.DataFrame({"y_true": y_te, "y_prob": y_prob}).to_csv(out, index=False)
        print(f"  Saved: {out.name}  (n={len(y_te)}, pos={int(y_te.sum())})")
