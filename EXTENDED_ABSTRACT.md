# EXTENDED ABSTRACT

---

## Detection and Analysis of High Wind Speed Cut-off Events in Turkish Wind Power Plants Using Real-Time Generation Data and WRF Simulations

**Faruk Avcı**

Istanbul Technical University, Department of Meteorological Engineering  
Email: avcio20@itu.edu.tr

---

### Abstract

This study develops a data-driven framework to detect and characterize high wind speed cut-off events across licensed wind power plants in Turkey using hourly real-time generation data from the EPİAŞ Transparency Platform, combined with high-resolution Weather Research and Forecasting (WRF) model simulations. Over a seven-month period (October 2024 – April 2025), 78 hard cut-off events affecting 30 wind farms are identified, with a cumulative production loss of 4,931 MW. Nine representative case studies from an extended storm period (March 16–24, 2025) are selected for WRF simulations using a two-domain nested configuration (9 km and 3 km resolution) to resolve mesoscale wind patterns over northwestern Turkey.

**Keywords:** wind power, cut-off events, extreme winds, EPİAŞ, Turkey, WRF, grid reliability

---

### 1. Introduction

Wind energy has become a cornerstone of Turkey's electricity system, with installed capacity reaching approximately 12 GW by 2025 and contributing 10–12% of annual generation. The integration of large-scale wind power introduces operational challenges, particularly during extreme wind events that exceed turbine design limits. Modern wind turbines operate within a specific wind speed envelope: cut-in speed (3–4 m/s), rated speed (12–15 m/s), and cut-out speed (23–25 m/s). When wind speeds exceed the cut-out threshold, turbines initiate automatic shutdown sequences to prevent mechanical damage, resulting in abrupt transitions from full power output to zero generation.

These "hard cut-off" events pose significant challenges for electricity system operators. Sudden loss of wind generation creates real-time supply-demand imbalances that must be compensated by reserve capacity. Large storm systems can trigger simultaneous cut-offs across multiple wind farms spanning hundreds of kilometers, amplifying the aggregate impact on system adequacy. The transition from full output to zero occurs faster than most dispatchable generators can ramp up, potentially causing frequency deviations.

Despite the growing importance of wind power in Turkey's energy mix, systematic analysis of high wind speed cut-off events remains limited. Previous studies have examined wind resource assessment and short-term forecasting, but few have focused specifically on extreme wind events and their operational impacts. Key gaps include lack of event-level characterization, limited meteorological context, and absence of high-resolution modeling to capture mesoscale wind patterns over complex terrain.

This study addresses these gaps through a combined data-driven and numerical modeling approach with the following objectives: (1) develop a detection algorithm for identifying hard cut-off events from hourly generation data; (2) characterize the frequency, severity, and spatiotemporal patterns of cut-off events across Turkey's wind fleet; (3) identify the most vulnerable wind farms and regions; and (4) apply WRF simulations to selected case studies to characterize extreme wind conditions at high spatial resolution.

---

### 2. Data and Methods

**Study Area and Data Sources:** The study covers approximately 190 licensed wind power plants under the YEKDEM renewable energy support scheme in Turkey. Real-time generation data are retrieved from the EPİAŞ Transparency Platform via REST API for the period October 2024 – April 2025, providing over 5,000 hourly observations per plant. Supplementary data include wind farm characteristics (installed capacity, geographic coordinates) from EPİAŞ and publicly available documentation. Surface meteorological observations from the Turkish State Meteorological Service (MGM) network are used for model validation. ERA5 reanalysis data from ECMWF at 0.25° × 0.25° resolution provide initial and lateral boundary conditions for WRF simulations.

**Cut-off Detection Algorithm:** A threshold-based detection algorithm identifies hard cut-off events by applying three simultaneous criteria to each hourly transition: (1) pre-event production exceeding 50 MW, indicating substantial capacity utilization; (2) post-event production below 10 MW, indicating near-complete shutdown; and (3) relative production decline exceeding 80%. Events satisfying all three criteria are flagged as hard cut-offs. This approach enables systematic detection without direct access to nacelle-level wind speed measurements, leveraging production patterns as a proxy for extreme wind conditions.

**Case Study Selection:** Nine case studies representing cut-off events during an extended storm period from March 16–24, 2025 are selected for detailed WRF modeling. These cases span a geographic corridor from the Aegean coast (Çanakkale) through the Marmara region (Balıkesir, İstanbul, Yalova, Sakarya) to Thrace (Kırklareli). The selected wind farms—TATLIPINAR, GÜLPINAR, EVRENCİK, İSTANBUL, ÜÇPINAR, TAŞPINAR, GÖKTEPE, and ZONGULDAK RES—represent a combined installed capacity exceeding 900 MW and production losses of 794 MW during the study period.

**WRF Model Configuration:** The Weather Research and Forecasting (WRF) model version 4.x with the ARW dynamical core is employed. A two-domain nested configuration is designed with 9 km (D01) and 3 km (D02) horizontal resolution. The domains are centered on the Marmara region (40.5°N, 28°E) to ensure coverage of all case study wind farms. Physics parameterizations include Thompson microphysics, RRTMG radiation, MYNN Level 2.5 PBL scheme, and Noah-MP land surface model. For each case, 48-hour simulations are performed with 12-hour spin-up, 24-hour pre-event, and 12-hour post-event periods. Output includes 10-m and hub-height (80-100 m) wind fields at hourly intervals.

---

### 3. Results

**Climatological Analysis:** Over the seven-month study period, 78 distinct hard cut-off events are detected, affecting 30 wind farms with a cumulative production loss of 4,931 MW. Strong seasonal clustering is observed, with March 2025 accounting for 33% of all events (26 cut-offs, 1,856 MW loss). The most extreme storm day, March 16, 2025, recorded 15 simultaneous cut-offs across geographically dispersed facilities within a 12-hour window.

**Regional Vulnerability:** Geographic analysis identifies the Thrace region as the most vulnerable area. KIYIKÖY RES alone experienced 18 events (23% of total) with 943 MW cumulative production loss. Other highly affected wind farms include TAŞPINAR RES (6 events, 393 MW), EVRENCİK RES (4 events, 290 MW), and KANGAL RES (3 events, 283 MW). The largest individual event occurred at KANGAL RES on December 14, 2024, with a complete shutdown from 121 MW to 0 MW.

**Monthly Distribution:** Cut-off frequency shows clear monthly variation: October 2024 (8 events), November 2024 (9 events), December 2024 (15 events), January 2025 (7 events), February 2025 (1 event), March 2025 (26 events), and April 2025 (12 events). February emerges as the calmest month, while March exhibits the highest extreme wind activity.

**Storm Event Characterization:** The March 16–24, 2025 storm period demonstrates the spatial evolution of extreme winds across northwestern Turkey. WRF simulations capture the propagation of the weather system from the Aegean coast eastward through the Marmara basin, with sequential cut-off events corresponding to the passage of the storm front. High-resolution wind fields reveal terrain-induced acceleration over ridge lines and coastal convergence zones that amplify wind speeds to cut-out thresholds.

---

### 4. Conclusions

This study demonstrates the value of combining transparency platform data with mesoscale numerical weather prediction for operational monitoring and retrospective analysis of extreme wind impacts on power systems. The methodology provides a scalable approach for identifying high-risk wind farms, characterizing seasonal and spatial patterns of cut-off exposure, and linking production anomalies to synoptic-scale weather systems.

Key findings include: (1) 78 hard cut-off events over seven months with 4,931 MW cumulative losses; (2) strong seasonal clustering with March 2025 as the most active month; (3) Thrace region as the most vulnerable area with KIYIKÖY RES experiencing 23% of all events; (4) the March 16, 2025 storm as an exceptional event with 15 simultaneous cut-offs; and (5) WRF simulations at 3 km resolution successfully capturing the spatial extent and temporal evolution of extreme wind conditions.

These findings support improved wind farm siting decisions, turbine selection based on regional wind climatology, and development of early warning systems for grid operators managing high wind power penetration scenarios. Future work will expand the WRF analysis to additional case studies and develop probabilistic forecasting tools for cut-off event prediction.

---

### References

1. EPİAŞ Transparency Platform. https://seffaflik.epias.com.tr/
2. IEC 61400-1: Wind turbines – Part 1: Design requirements.
3. Skamarock, W.C., et al. (2019). A Description of the Advanced Research WRF Model Version 4. NCAR Technical Note.
4. Hersbach, H., et al. (2020). The ERA5 global reanalysis. Q.J.R. Meteorol. Soc., 146, 1999-2049.

---

*Word Count: ~1,150 words (approximately 2 A4 pages with standard formatting)*

