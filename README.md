# HCOT-MW: Hard Cutoff Observatory for Turkish Wind Farms

**Fleet-Wide Detection, Meteorological Attribution, and Economic Quantification of Hard Cutoff Events in Turkish Wind Power Plants**

*Q1 Scopus Paper — Target: Renewable Energy (IF ~8.7) / Applied Energy (IF ~11.4)*

---

## Overview

This repository contains the full analysis pipeline for the HCOT-MW framework, which systematically characterizes **hard cutoff events** in Turkey's licensed wind power fleet using data from the EPİAŞ Transparency Platform.

**Key findings (Jan 2022 – Apr 2025, leakage-free pipeline):**

- **249 hard cutoff events** identified across 43 wind farms (3-year dataset)
- **16,121 MWh** total energy lost (~64.7 MWh per event average)
- **39.04 million TL / USD 1.60 million** total economic impact (actual PTF prices, 100% coverage)
- **SAROS RES** (Thrace): Most economically impacted plant (37 events; USD 227 K)
- **XGBoost early warning (leakage-free)**: ROC-AUC 0.549–0.585 at H=6/12/24h horizons

---

## Repository Structure

```
epias_wind_cutoff/
├── ARTICLE_Q1_v1.md          ← Full manuscript (~8,400 words; expand to ~11,700)
├── SUBMISSION_CHECKLIST.md   ← Pre-submission QC checklist
├── requirements.txt          ← Python dependencies
│
├── # Core analysis scripts
├── run_economic_analysis.py   ← 3-year PTF × MW economic impact (249 events)
├── run_sensitivity.py         ← Threshold sensitivity grid (125 combinations)
├── export_model_probs.py      ← Extract test probabilities for ROC/PR curves
├── fetch_extended_data.py     ← EPİAŞ 2022-2025 extended data fetcher
├── era5_downloader.py         ← CDS API ERA5 downloader
├── generate_figures_v2.py     ← 7 Q1-quality figures (300 DPI, Wong CB palette)
│
├── # Detection infrastructure
├── epias_client.py            ← EPİAŞ Transparency API client
├── hard_cutoff_detector.py    ← Core detection algorithm
├── res_cutoff_scanner.py      ← Per-plant fleet scanner
├── fetch_res_plants.py        ← Plant list fetcher
│
├── analysis/
│   ├── train_v2.py            ← Leakage-free XGBoost pipeline (H=6/12/24h)
│   ├── audit_pipeline.py      ← Data leakage diagnostic (reference)
│   ├── data_qc.py             ← QC pipeline
│   ├── synoptic_classifier.py ← ERA5 K-means synoptic classification (pending)
│   ├── vulnerability_index.py ← Composite Vulnerability Index (pending)
│   ├── models/v2/             ← Saved XGBoost models + test probabilities
│   ├── economic_impact_summary.csv
│   ├── cutoff_events_with_losses.csv
│   ├── sensitivity_table.csv
│   └── sensitivity_report.txt
│
├── figures/                   ← 7 figures @ 300 DPI (Wong CB-palette)
│   ├── fig1_event_timeline.png
│   ├── fig2_seasonal_heatmap.png
│   ├── fig3_economic_impact.png
│   ├── fig4_model_roc_pr.png
│   ├── fig5_feature_importance.png
│   ├── fig6_sensitivity_heatmap.png  ← Supplementary S2
│   ├── fig7_event_magnitude_dist.png
│   └── fig8_framework_schematic.png
│   ├── fig6_vulnerability_map.png
│   ├── fig7_wrf_validation.png
│   ├── fig8_economic_impact.png
│   ├── fig9_model_comparison.png
│   └── fig10_compound_events.png
│
├── data/
│   ├── all_cutoffs_2024_2025.csv   ← 78 events, 30 plants
│   ├── era5/                        ← ERA5 reanalysis (downloaded)
│   └── [monthly cutoff CSVs]
│
└── canakkale_res_export/
    └── output/canakkale_region_res_hourly_last6m.csv  ← 14 plants, 6 months
```

---

## Installation

```bash
# Clone and set up environment
cd epias_wind_cutoff
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# macOS: Install OpenMP for XGBoost
brew install libomp
```

---

## Usage

### 1. Fetch Extended EPİAŞ Data (requires credentials)

```bash
export EPIAS_USERNAME='your@email.com'
export EPIAS_PASSWORD='yourpassword'

# Fetch 2022-2025 per-plant wind generation + PTF prices
python fetch_extended_data.py --mode all --start 2022-01-01 --end 2025-04-30
```

### 2. Download ERA5 Reanalysis (requires ~/.cdsapirc)

```bash
# Storm period (already downloaded)
python era5_downloader.py --vars storm

# Full 2022-2025 dataset (for extended analysis)
python era5_downloader.py --vars all --years 2022 2023 2024 2025
```

### 3. Run Full Analysis Pipeline

```bash
# QC
python analysis/data_qc.py

# Economic impact
python economic_impact.py

# Synoptic classification
python analysis/synoptic_classifier.py

# Vulnerability index
python analysis/vulnerability_index.py

# Early warning model
python analysis/tft_early_warning.py --mode train

# Generate all 10 figures (300 DPI)
python generate_figures.py
```

---

## Data Sources


| Source                      | Data                                      | Access                                                                                      |
| --------------------------- | ----------------------------------------- | ------------------------------------------------------------------------------------------- |
| EPİAŞ Transparency Platform | Hourly YEKDEM wind generation, PTF prices | [https://seffaflik.epias.com.tr/](https://seffaflik.epias.com.tr/) (API, free registration) |
| ERA5 (ECMWF/Copernicus)     | 100m wind, MSLP, T2m (0.25°, hourly)      | [https://cds.climate.copernicus.eu/](https://cds.climate.copernicus.eu/) (free API)         |
| WRF Model                   | 3 km, 38h simulation, March 2025          | Output file: `faruk_wrfoutput_20250316`                                                     |


---

## Key Results

### Hard Cutoff Events (Jan 2022 – Apr 2025, full 3-year dataset)


| Year          | Events | Energy Lost (MWh) | Economic Loss (USD K) |
| ------------- | ------ | ----------------- | --------------------- |
| 2022          | 54     | 3,372             | 576                   |
| 2023          | 61     | 3,344             | 433                   |
| 2024          | 96     | 6,369             | 470                   |
| 2025 (Jan–Apr)| 38     | 3,036             | 119                   |
| **Total**     | **249**| **16,121**        | **1,599**             |

Top affected plant: **SAROS RES** — 37 events, ~3,006 MWh cumulative loss.
Worst single day: **16 March 2025** — 14 simultaneous cut-offs.

### Early Warning Model Performance (Leakage-free XGBoost v2)


| Horizon | ROC-AUC | PR-AUC | F1    | Design                           |
| ------- | ------- | ------ | ----- | -------------------------------- |
| H = 6h  | 0.585   | 0.259  | 0.306 | Window ends at t−H−1, no leakage |
| H = 12h | 0.571   | 0.227  | 0.215 | Window ends at t−H−1, no leakage |
| H = 24h | 0.549   | 0.203  | 0.301 | Window ends at t−H−1, no leakage |

*Note: Earlier versions of the pipeline reported inflated metrics (ROC-AUC > 0.99) due to data leakage. These results are the corrected, leakage-free baseline.*


---

## Citation

> Avci, Ö.F., & Tan, E. (2026). Fleet-Wide Detection, Meteorological Attribution, and Economic Quantification of Hard Cutoff Events in Turkish Wind Power Plants: The HCOT-MW Framework. *Renewable Energy*. [Under review]

---

## License

MIT License. Data from EPİAŞ and ERA5 are subject to their respective terms of use.