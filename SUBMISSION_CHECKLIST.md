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

### Figures (10 total, 300 DPI)

- fig1_study_area_map.png (280 KB, 300 DPI)
- fig2_framework_diagram.png (321 KB, 300 DPI)
- fig3_cutoff_timeseries.png (239 KB, 300 DPI)
- fig4_heatmap_top_plants.png (406 KB, 300 DPI)
- fig5_synoptic_patterns.png (214 KB, 300 DPI)
- fig6_vulnerability_map.png (358 KB, 300 DPI)
- fig7_wrf_validation.png (392 KB, 300 DPI)
- fig8_economic_impact.png (307 KB, 300 DPI)
- fig9_model_comparison.png (321 KB, 300 DPI)
- fig10_compound_events.png (683 KB, 300 DPI)
- All figures: colorblind-friendly palette (viridis/CB-palette)
- All figures: referenced in text
- All figures: independent captions

### Tables (8 total)

- Table 1: MGM observation stations
- Table 2: MGM summary statistics
- Table 3: WRF configuration
- Table 4: Monthly cutoff summary
- Table 5: Top 10 affected wind farms
- Table 6: Economic impact summary
- Table 7: WRF validation metrics
- Table 8: Early warning model comparison
- Research gaps summary table (Table in Lit Review)

### Analysis Code & Data

- `fetch_extended_data.py` — EPİAŞ extended data fetcher (2022–2025)
- `era5_downloader.py` — CDS API ERA5 downloader
- `economic_impact.py` — PTF × MW economic calculator
- `analysis/data_qc.py` — QC pipeline
- `analysis/synoptic_classifier.py` — ERA5 K-means classifier
- `analysis/vulnerability_index.py` — CVI calculator
- `analysis/tft_early_warning.py` — TFT + XGBoost model
- `generate_figures.py` — all 10 figures
- `requirements.txt` — updated with all dependencies
- `analysis/qc_report.txt` — QC report
- `analysis/qc_tables/` — QC tables
- GitHub repository (to be created upon acceptance)

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

1. **Expand references to 50–70**: Add TFT energy papers (3–4), Turkey wind papers (3–4), compound events (3–4), economic impact studies (3–4), EPİAŞ/YEKDEM papers (2–3)
2. **Extended EPİAŞ data**: Fetch 2022–2024 data when credentials available → re-run detection → update event statistics
3. **ERA5 download**: Complete 2022–2025 ERA5 dataset → run synoptic classifier with full ERA5 → update Fig 5
4. **TFT full training**: Train TFT on 3-year EPİAŞ dataset → get actual ROC-AUC, Brier Score, F1 → update Table 8 and Fig 9
5. **Author contributions** (CRediT): Conceptualization, Methodology, Software, Formal analysis, Investigation, Writing

### Medium Priority

1. **Threshold sensitivity analysis** (Supplementary S2)
2. **WRF namelist** (Supplementary S4)
3. **Updated README** with full project description
4. **geopandas basemap**: Install cartopy or use natural earth for proper study area map (Fig 1)

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