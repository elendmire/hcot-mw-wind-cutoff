# HCOT-MW: Hard Cutoff Observatory for Turkish Wind Farms

**Fleet-Wide Detection, Meteorological Attribution, and Economic Quantification of Hard Cutoff Events in Turkish Wind Power Plants**

*Q1 Scopus Paper — Target: Renewable Energy (IF ~8.7) / Applied Energy (IF ~11.4)*

---

## Overview

This repository contains the full analysis pipeline for the HCOT-MW framework, which systematically characterizes **hard cutoff events** in Turkey's licensed wind power fleet using data from the EPİAŞ Transparency Platform.

**Key findings:**

- **78 hard cutoff events** identified across 30 wind farms (Oct 2024 – Apr 2025)
- **4,931 MW** cumulative production losses (~63 MW per event average)
- **15.82 million TL** (≈ 458 thousand USD) total economic impact
- **March 16, 2025**: 15 simultaneous shutdowns, 794 MW combined loss (peak storm event)
- **KIYIKÖY RES** (Thrace): Most vulnerable plant (18 events; 943 MW; CVI = 0.83)
- **XGBoost early warning classifier**: ROC-AUC = 0.859

---

## Repository Structure

```
epias_wind_cutoff/
├── ARTICLE_Q1_v1.md          ← Full manuscript (~8,400 words; expand to ~11,700)
├── SUBMISSION_CHECKLIST.md   ← Pre-submission QC checklist
├── requirements.txt          ← Python dependencies
│
├── # Core analysis scripts
├── economic_impact.py         ← PTF × MW economic calculator
├── fetch_extended_data.py     ← EPİAŞ 2022-2025 extended data fetcher
├── era5_downloader.py         ← CDS API ERA5 downloader
├── generate_figures.py        ← All 10 Q1-quality figures (300 DPI)
│
├── # Detection infrastructure (pre-existing)
├── epias_client.py            ← EPİAŞ Transparency API client
├── hard_cutoff_detector.py    ← Core detection algorithm
├── res_cutoff_scanner.py      ← Per-plant fleet scanner
├── fetch_res_plants.py        ← Plant list fetcher
│
├── analysis/
│   ├── data_qc.py             ← Comprehensive QC pipeline
│   ├── synoptic_classifier.py ← ERA5 K-means synoptic classification
│   ├── vulnerability_index.py ← Composite Vulnerability Index (CVI)
│   ├── tft_early_warning.py   ← TFT + XGBoost early warning model
│   ├── model_comparison_table.csv
│   ├── vulnerability_index.csv
│   ├── synoptic_classes.csv
│   ├── economic_impact_*.csv
│   └── qc_tables/
│
├── figures/                   ← 10 figures @ 300 DPI (280-683 KB each)
│   ├── fig1_study_area_map.png
│   ├── fig2_framework_diagram.png
│   ├── fig3_cutoff_timeseries.png
│   ├── fig4_heatmap_top_plants.png
│   ├── fig5_synoptic_patterns.png  ← ERA5 MSLP + 100m wind
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
| MGM (Turkish Met. Service)  | Surface observations (wind, T, P)         | [https://www.mgm.gov.tr/](https://www.mgm.gov.tr/) (on request)                             |
| ERA5 (ECMWF/Copernicus)     | 100m wind, MSLP, T2m (0.25°, hourly)      | [https://cds.climate.copernicus.eu/](https://cds.climate.copernicus.eu/) (free API)         |
| WRF Model                   | 3 km, 38h simulation, March 2025          | Output file: `faruk_wrfoutput_20250316`                                                     |


---

## Key Results

### Hard Cutoff Events (Oct 2024 – Apr 2025)


| Month        | Events | Loss (MW) | Max Event (MW) |
| ------------ | ------ | --------- | -------------- |
| Oct 2024     | 8      | 495       | 89             |
| Nov 2024     | 9      | 470       | 72             |
| Dec 2024     | 15     | 970       | **121**        |
| Jan 2025     | 7      | 433       | 77             |
| Feb 2025     | 1      | 47        | 47             |
| **Mar 2025** | **26** | **1,856** | 109            |
| Apr 2025     | 12     | 661       | 74             |
| **Total**    | **78** | **4,931** | —              |


### Early Warning Model Comparison


| Model        | ROC-AUC   | Type          |
| ------------ | --------- | ------------- |
| Persistence  | 0.500     | Rule-based    |
| ARIMA        | 0.612     | Statistical   |
| XGBoost      | **0.859** | Ensemble ML   |
| TFT (target) | ~0.847    | Deep Learning |


---

## Citation

> Avci, Ö.F., & Tan, E. (2026). Fleet-Wide Detection, Meteorological Attribution, and Economic Quantification of Hard Cutoff Events in Turkish Wind Power Plants: The HCOT-MW Framework. *Renewable Energy*. [Under review]

---

## License

MIT License. Data from EPİAŞ, MGM, and ERA5 are subject to their respective terms of use.