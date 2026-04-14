# Journal Submission Checklist

## HCOT-MW Paper — Q1 Scopus Target

**Target Journal:** Renewable Energy (IF ~8.7) — Primary  
**Alternative:** Applied Energy (IF ~11.4)  
**Submission Status:** In preparation

---

## Pre-Submission Checklist

### Manuscript

- English language, academic register
- Title: clear, specific, contains key terms
- Abstract: ~250 words, structured (background, methods, results, conclusions)
- Keywords: 7 terms including key concepts
- Introduction: problem statement, literature gaps, objectives, contributions
- Literature Review: comprehensive with research gaps table
- Data & Study Area: complete with tables and statistics
- Methodology: detailed enough for reproducibility (Algorithm 1 format)
- Results: all numerical results presented in tables and figures
- Discussion: comparison with literature, limitations, policy implications
- Conclusions: summary of all 6 main findings, future work
- Acknowledgements
- Data Availability statement
- References: 28 references (target: expand to 50–70)
- Author contributions statement (CRediT format)
- Conflict of interest declaration
- Funding statement

### Figures (7 generated, 300 DPI, Wong CB palette)

- fig1_event_timeline.png — monthly count + cumulative
- fig2_seasonal_heatmap.png — month × year event heatmap
- fig3_economic_impact.png — annual loss + top-10 plants
- fig4_model_roc_pr.png — ROC & PR curves for H=6/12/24h
- fig5_feature_importance.png — XGBoost top-15 features
- fig6_sensitivity_heatmap.png — threshold sensitivity grid (Supplementary S2)
- fig7_event_magnitude_dist.png — energy lost per event distribution
- fig8_framework_schematic.png — HCOT-MW 3-layer framework
- fig_study_area_map.png — Turkey RES locations (needs geopandas/cartopy)
- All figures: 300 DPI, colorblind-friendly (Wong CB palette) ✓
- All figures: referenced in text ✓

### Tables (current)

- Table 1: WRF configuration
- Table 2: Data sources summary (no MGM)
- Table 3: Monthly cutoff summary (3-year)
- Table 4: Top 10 affected wind farms
- Table 5: Window dataset composition (Table 6 in draft)
- Table 6: Feature descriptions (Table 7 in draft)
- Table 7: XGBoost results H=6/12/24h (Table 8 in draft)
- Table 8: Economic impact summary (Table 9 in draft) ✓ NEW
- Research gaps summary table (in Lit Review)

### Analysis Code & Data

- `fetch_extended_data.py` — EPİAŞ extended data fetcher (2022–2025)
- `era5_downloader.py` — CDS API ERA5 downloader
- `run_economic_analysis.py` — PTF × MW economic calculator (3-year, 249 events)
- `run_sensitivity.py` — threshold sensitivity analysis (125 combinations)
- `analysis/audit_pipeline.py` — leakage audit (diagnostic)
- `analysis/train_v2.py` — leakage-free XGBoost pipeline (H=6/12/24h)
- `export_model_probs.py` — extract test probabilities for ROC/PR curves
- `generate_figures_q1.py` — 8 Q1 figures (300 DPI, all in `figures/Fig*.png`)
- `requirements.txt` — all dependencies
- `analysis/economic_impact_summary.csv` — monetised impact table
- `analysis/sensitivity_table.csv` + `sensitivity_report.txt`
- `analysis/models/v2/` — saved XGBoost models + probs
- GitHub repository: [https://github.com/oavci/epias_wind_cutoff](https://github.com/oavci/epias_wind_cutoff)
- `analysis/synoptic_classifier.py` — pending ERA5 data
- `analysis/vulnerability_index.py` — pending

### Supplementary Materials

- S1: QC report (analysis/qc_report.txt)
- S2: Threshold sensitivity analysis
- S3: Full cutoff event list (data/all_cutoffs_2024_2025.csv)
- S4: WRF namelist.input
- S5: XGBoost feature importance (from model training)
- S6: PTF estimates and exchange rates (economic_impact.py)

---

## Pending Before Submission

### High Priority

1. **Expand references to 50–70**: Add XGBoost/ML energy papers (3–4), Turkey wind papers (3–4), compound events (3–4), economic impact studies (3–4), EPİAŞ/YEKDEM papers (2–3) — currently ~30 refs
2. **ERA5 download**: Complete 2022–2025 ERA5 → run synoptic classifier → update seasonal patterns section
3. **WRF results**: Awaiting server agent output (okyanus.itu.edu.tr) — add to methodology once available
4. **Author contributions** (CRediT): Conceptualization, Methodology, Software, Formal analysis, Investigation, Writing
5. **Study area map** (fig_study_area_map): needs geopandas + cartopy

### Medium Priority

1. **WRF namelist** (Supplementary S4) — `wrf/namelist.input.2dom` already prepared
2. **Grammarly / language check** on full manuscript
3. **Journal-specific formatting** (Elsevier template, line numbers)
4. **Cover letter draft**

### Low Priority

1. **Grammarly language check** on full manuscript
2. **Journal-specific formatting**: Elsevier template, line numbers, font requirements
3. **Cover letter draft**

---

## Word Count Target


| Section           | Current    | Target      |
| ----------------- | ---------- | ----------- |
| Introduction      | ~1,400     | 1,800       |
| Literature Review | ~900       | 1,200       |
| Data & Study Area | ~1,100     | 1,300       |
| Methodology       | ~900       | 2,200       |
| Results           | ~1,500     | 2,800       |
| Discussion        | ~900       | 1,800       |
| Conclusions       | ~400       | 600         |
| **Total**         | **~8,400** | **~11,700** |


*Remaining expansion needed: ~3,300 words, primarily in Methodology and Results sections*

---

## Reference Strategy

Current: 28 references  
Target: 50–70 references (Q1 standard)

**Priority categories:**

- TFT deep learning energy applications (Applied Energy 2023–2025): +4
- Turkey wind energy system studies: +5
- EPİAŞ/YEKDEM market analysis: +3
- Compound extreme events (ECMWF/Copernicus): +3
- WRF wind energy validation studies: +3
- Economic impact of renewable variability: +4
- Grid resilience under extreme weather: +3
- Hard cutoff / cut-out event analysis: +4

**Total to add: ~29 references → target: 57 total**