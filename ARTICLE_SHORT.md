<!--
FORMATTING (Word/PDF export): Font: Times New Roman. Body: 12 pt, line spacing 1, justified, 1 line space between paragraphs. Abstract: 11 pt. Title: 13 pt, ALL CAPS. Authors: 11 pt. Table titles & figure captions: 11 pt. Table body: 10 pt. References: 10 pt. First page ≤1 page; total ≤10 pages. Main headings: 12 pt ALL CAPS. Subheading–text: 6 pt space; no space between subheading and following text. Figure/table: 3 pt above caption; 1 line space after caption. No paragraph indent in Introduction.
-->

# DETECTION AND ANALYSIS OF HIGH WIND SPEED CUT-OFF EVENTS IN TURKISH WIND POWER PLANTS USING REAL-TIME GENERATION DATA AND WRF SIMULATIONS

**Ömer Faruk AVCI¹, Assoc. Prof. Elçin TAN²**

<sup>1,2</sup>Istanbul Technical University, Faculty of Aeronautics and Astronautics, Department of Climate Science and Meteorological Engineering, Istanbul, Türkiye
<sup>1</sup>avcio20@itu.edu.tr, <sup>2</sup>elcin.tan@itu.edu.tr

---

## Abstract

Extreme wind events can trigger automatic turbine shutdowns when speeds exceed cut-out thresholds (typically 23–25 m/s), causing sudden generation losses in grids with high wind penetration (Archer et al., 2020; Panteli et al., 2017). This study presents a data-driven method to detect and analyze such "hard cut-off" events across licensed Turkish wind farms. Using hourly real-time production data from the EPİAŞ Transparency Platform (October 2024–April 2025, ~190 plants under YEKDEM), cut-off events are defined as abrupt (>80%) drops from high output (>50 MW) to near zero (<10 MW) within one hour. A total of 78 events were identified across 30 wind farms, with cumulative production losses of 4,931 MW. March 2025 was the most active month (26 events, 1,856 MW lost), and 16 March 2025 the most severe single day with 15 simultaneous cut-offs; Thrace was hit hardest, notably KIYIKÖY RES (18 events, 943 MW lost). Hourly surface observations from five MGM stations were acquired for the 15–18 March 2025 storm period, alongside WRF mesoscale simulations for nine representative cases. WRF 10-m wind speeds were validated against MGM observations, yielding RMSE values of 1.96–5.45 m/s. The combination of operational generation data, surface observations, and mesoscale modeling effectively characterizes cut-off events and supports risk assessment, turbine selection, and the development of early warning tools for grid operators.

**Keywords:** wind power, cut-off events, extreme winds, WRF, Turkey

---

## Özet

Aşırı rüzgar olayları, hızlar türbin kesme eşiklerini (genellikle 23–25 m/s) aştığında otomatik kapanmayı tetikleyerek yüksek rüzgar gücü payına sahip şebekelerde ani üretim kayıplarına neden olmaktadır (Archer et al., 2020; Panteli et al., 2017). Bu çalışmada, lisanslı Türkiye rüzgar santrallerinde bu tür "sert kesinti" olaylarının tespiti ve analizi için veri odaklı bir yöntem sunulmaktadır. EPİAŞ Şeffaflık Platformu saatlik gerçek zamanlı üretim verileri (Ekim 2024–Nisan 2025, YEKDEM kapsamında ~190 santral) kullanılarak kesinti olayları, yüksek çıktıdan (>50 MW) sıfıra yakın (<10 MW) düzeye bir saat içinde ani (>%80) düşüş olarak tanımlanmıştır. 30 santralde toplam 78 olay tespit edilmiş, kümülatif üretim kaybı 4.931 MW olarak hesaplanmıştır. Mart 2025 en yoğun ay (26 olay, 1.856 MW kayıp), 16 Mart 2025 ise 15 eşzamanlı kesinti ile en ağır tek gün olmuş; Trakya, özellikle KIYIKÖY RES (18 olay, 943 MW kayıp) en çok etkilenen bölge olarak öne çıkmıştır. Meteorolojik bağlam için 15–18 Mart 2025 fırtına dönemine ait beş MGM istasyonundan saatlik yüzey gözlemleri ile dokuz temsili vaka için WRF mezoskal simülasyonları gerçekleştirilmiştir. WRF 10-m rüzgar hızları MGM gözlemleriyle doğrulanmış; RMSE değerleri 1,96–5,45 m/s bulunmuştur. İşletme üretim verisi, yüzey gözlemleri ve mezoskal modellemenin birlikte kullanımı, kesinti olaylarının karakterizasyonu, risk değerlendirmesi, türbin seçimi ve erken uyarı araçlarının geliştirilmesi açısından etkili bulunmuştur.

**Anahtar kelimeler:** rüzgar gücü, kesinti olayları, aşırı rüzgar, WRF, Türkiye

---

## 1. INTRODUCTION

### 1.1 Background and Motivation

Wind energy has emerged as one of the fastest-growing renewable sources globally, with Turkey reaching approximately 12 GW installed capacity by early 2025 (Çetin, 2023). The integration of large-scale wind power into grids introduces operational challenges, particularly from extreme wind events that exceed turbine design limits, triggering automatic safety shutdowns known as "cut-off" events (Archer et al., 2020; Panteli et al., 2017).

Modern wind turbines operate within a specific wind speed envelope: cut-in (~3–4 m/s), rated (~12–15 m/s), and cut-out (~23–25 m/s). When wind speeds exceed cut-out thresholds, turbines initiate automatic shutdown, resulting in abrupt transitions from high output to near-zero generation within minutes. For large wind farms exceeding 100 MW, such events remove substantial capacity from the grid with minimal warning (Karagiannis et al., 2019).

These events pose several challenges for grid operators: sudden supply-demand imbalances requiring reserve activation, forecast errors at the hourly resolution needed for operational planning, spatial correlation of simultaneous cut-offs across multiple farms during large storm systems, and economic impacts from lost generation and balancing market penalties (Panteli et al., 2017; Zheng et al., 2024).

### 1.2 Turkey's Wind Energy Landscape

Turkey's wind resources are concentrated in the Thrace region (strong northerly Black Sea winds), the Marmara region (topographic effects around the Sea of Marmara), the Aegean coast (sea breezes and valley channeling from Çanakkale to İzmir), and Central Anatolia (high-altitude continental wind regimes). Approximately 190 licensed plants participate in the YEKDEM scheme, with hourly generation data published through the EPİAŞ Transparency Platform (Dadaser-Celik & Cengiz, 2014; Çetin, 2023).

### 1.3 Study Objectives

Despite the growing importance of wind power in Turkey, systematic analysis of high-wind cut-off events remains limited. This study addresses this gap through:

1. Developing a detection algorithm for hard cut-off events from hourly generation data.
2. Characterizing the frequency, severity, and spatiotemporal patterns of cut-off events across Turkey's wind fleet (October 2024–April 2025).
3. Identifying the most vulnerable wind farms and regions.
4. Analyzing MGM surface observations during the most active storm period (15–18 March 2025).
5. Configuring WRF simulations for selected cases and validating against MGM observations.

---

## 2. DATA AND METHODS

### 2.1 Data Sources

**EPİAŞ Transparency Platform.** Hourly generation data for all licensed wind plants were obtained via the EPİAŞ API for October 2024–April 2025 (~5,100 hourly values per plant, ~190 plants).

**MGM Surface Observations.** Hourly meteorological data were obtained from five MGM stations for the 15–18 March 2025 storm period (Table 1). Variables include wind speed/direction, temperature, pressure, humidity, and precipitation.

**Table 1.** MGM stations used for storm period observation and WRF validation.

| Station No. | Station Name | Province | Matched Wind Farm | Distance to Farm (km) |
|-------------|-------------|----------|-------------------:|---------------------:|
| 17052 | Kırklareli | Kırklareli | EVRENCİK RES | ~20 |
| 17069 | Sakarya | Sakarya | ZONGULDAK RES | ~25 |
| 17112 | Çanakkale | Çanakkale | GÜLPINAR RES | ~40 |
| 17636 | Florya | İstanbul | TAŞPINAR RES | ~10–15 |
| 17637 | Bolu Dağı | Bolu | Reference (inland) | — |

### 2.2 Hard Cut-off Detection Methodology

A "hard cut-off" event is defined as a sudden transition from high power output to near-zero generation within a single hourly interval. The detection algorithm applies three simultaneous criteria:

1. **Pre-event production** > 50 MW (substantial operating capacity).
2. **Post-event production** < 10 MW (near-complete shutdown).
3. **Percentage drop** > 80%, calculated as:

$$
\text{Drop}(\%) = \frac{P_{t-1} - P_t}{P_{t-1}} \times 100
$$

These thresholds balance sensitivity and specificity: 50 MW corresponds to ~40–70% of rated capacity for medium-sized farms, 10 MW allows tolerance for partial shutdowns, and the 80% criterion ensures only abrupt transitions are captured. The algorithm is implemented in Python using the pandas library.

### 2.3 Case Study Selection

Nine cases were selected for detailed WRF analysis based on temporal clustering, geographic diversity, and event magnitude (Table 2). All concentrate on 16 March 2025, the most severe day with 15 simultaneous cut-offs. Combined losses across the nine events amount to 794 MW.

**Table 2.** Selected case studies for WRF simulation.

| Case ID | Wind Farm | Province | Event Hour (UTC) | Loss (MW) |
|---------|-----------|----------|:---:|---:|
| CASE_03 | İSTANBUL RES | İstanbul | 11:00 | 109 |
| CASE_04 | TATLIPINAR RES | Balıkesir | 10:00 | 104 |
| CASE_05 | GÜLPINAR RES | Çanakkale | 10:00 | 98 |
| CASE_07 | EVRENCİK RES | Kırklareli | 22:00 | 89 |
| CASE_08 | ÜÇPINAR RES | Balıkesir | 11:00 | 87 |
| CASE_09 | EVRENCİK RES | Kırklareli | 10:00 | 81 |
| CASE_11 | TAŞPINAR RES | İstanbul | 11:00 | 77 |
| CASE_13 | GÖKTEPE RES | Yalova | 11:00 | 76 |
| CASE_14 | ZONGULDAK RES | Sakarya | 11:00 | 74 |

### 2.4 WRF Model Configuration

The WRF model version 4.x (Skamarock et al., 2019) was used with a single-domain configuration at 3-km horizontal resolution (dx = dy = 3000 m) covering northwestern Turkey. At 3-km resolution, convective processes are explicitly resolved. The time step is 18 s. Physics parameterizations follow the CONUS suite (Table 3).

**Table 3.** WRF physics parameterization options (CONUS physics suite).

| Parameter | Value | Scheme | Description |
|-----------|-------|--------|-------------|
| physics_suite | physics_suite | CONUS Suite | Default suite (Thompson MP, RRTMG radiation, YSU PBL) |
| mp_physics | 8 | Thompson | Aerosol-aware microphysics |
| ra_lw_physics | 4 | RRTMG LW | Longwave radiation |
| ra_sw_physics | 4 | RRTMG SW | Shortwave radiation |
| bl_pbl_physics | 1 | YSU | Non-local PBL scheme; widely used for wind energy applications |
| sf_sfclay_physics | 1 | Revised MM5 M-O | Surface layer (Monin-Obukhov similarity) |
| sf_surface_physics | 1 | Thermal Diffusion | 5-layer soil thermal diffusion land surface model |
| cu_physics | 0 | Off | Cumulus parameterization off (convection explicitly resolved at 3 km) |

Vertical configuration: 51 levels (e_vert = 51), with enhanced resolution in the planetary boundary layer. Initial and lateral boundary conditions from ERA5 reanalysis (6-hourly updates); SST updated daily. A 38-hour simulation was performed starting 15 March 2025 00:00 UTC with 12-hour spin-up.

### 2.5 Model Validation

WRF 10-m wind speed was validated against MGM observations at four matched station–farm pairs using bias, RMSE, and Pearson correlation (Table 4).

**Table 4.** WRF 10-m wind speed validation against MGM observations (15–16 March 2025).

| MGM Station | Matched Farm | Bias (m/s) | RMSE (m/s) | r |
|-------------|-------------|---:|---:|---:|
| Çanakkale (17112) | GULPINAR | +4.80 | 5.31 | 0.68 |
| Florya (17636) | ISTANBUL | +5.39 | 5.45 | 0.59 |
| Sakarya (17069) | ZONGULDAK | +1.13 | 2.76 | −0.68 |
| Kırklareli (17052) | TATLIPINAR | +1.29 | 1.96 | 0.15 |

The WRF model exhibits a positive bias at all stations, which is expected given that model grid points represent exposed wind farm terrain, whereas MGM stations are typically in sheltered, lower-elevation settings.

---

## 3. RESULTS AND DISCUSSION

### 3.1 Cut-off Event Statistics

Over the seven-month study period, the detection algorithm identified 78 hard cut-off events across 30 wind farms, with cumulative production losses of 4,931 MW. March 2025 was the most active month (26 events, 1,856 MW lost). The single most severe day was 16 March 2025 with 15 simultaneous cut-offs. Geographically, the Thrace region was most affected, with KIYIKÖY RES recording the highest exposure (18 events, 943 MW cumulative loss).

### 3.2 Meteorological Context: MGM Observations

Hourly surface observations during the 15–18 March 2025 period reveal the storm system evolution. Kırklareli recorded the lowest mean station pressure (986.5 hPa, minimum 976.8 hPa), highest precipitation (23.2 mm), and moderate winds (mean 2.57 m/s, max 5.9 m/s at 10 m). Çanakkale registered the highest surface winds (mean 3.97 m/s, max 9.0 m/s), consistent with its exposed coastal position.

Figure 1 presents the meteorological overview showing the concurrent evolution of wind speed, wind direction, temperature, station pressure, and precipitation. The sharp pressure drop at Kırklareli on 16 March, accompanied by a directional shift and temperature change, marks the cold front passage associated with the mass cut-off event.

![Figure 1](mgm_analysis/figures/fig2_meteorological_overview.png)

**Figure 1.** Five-panel meteorological overview of the 15–18 March 2025 storm period: (a) wind speed, (b) wind direction, (c) air temperature, (d) station pressure, (e) hourly precipitation. Data from five MGM stations.

### 3.3 WRF Validation

Time series comparisons show that the WRF model captures general temporal trends but overestimates 10-m wind speeds relative to sheltered MGM stations, with biases of +1.13 to +5.39 m/s. This systematic overestimation is physically consistent with wind farm grid points being located on exposed ridges, whereas MGM stations occupy valley or lowland environments. The scatter comparison (Figure 2) confirms the positive bias pattern, with the strongest agreement at Çanakkale (r = 0.68). WRF at 3-km resolution captures mesoscale features—terrain channeling, coastal convergence, and frontal dynamics—relevant for characterizing cut-off conditions.

![Figure 2](mgm_analysis/figures/fig8_scatter_wrf_era5_vs_mgm.png)

**Figure 2.** Scatter plot of WRF simulated vs. MGM observed 10-m wind speed at four matched station–farm pairs during 15–16 March 2025.

### 3.4 Surface Observations and Cut-off Relationship

While MGM 10-m surface wind speeds did not reach the turbine cut-out threshold (25 m/s), this is consistent with vertical wind shear: hub-height winds (80–100 m) are typically 1.5–2.5 times surface values. WRF 100-m simulations show wind speeds exceeding 15 m/s at several farm locations, and extrapolation to hub height at exposed farm sites yields values consistent with cut-out conditions.

---

## 4. CONCLUSIONS

(1) Threshold-based detection applied to EPİAŞ hourly data identifies cut-off events reliably without direct wind measurements. Over seven months, 78 events were detected across 30 plants, with total losses of 4,931 MW.

(2) The March 2025 storm period accounted for the highest event count and losses, with 16 March 2025 as the most severe single day (15 simultaneous cut-offs). Thrace, notably Kıyıköy, showed the highest cut-off frequency and loss magnitude.

(3) MGM surface observations from five stations during 15–18 March 2025 provide direct meteorological context. The sharp pressure drop at Kırklareli (minimum 976.8 hPa) and elevated Aegean coastal winds (max 9.0 m/s at Çanakkale) characterize the synoptic forcing behind the mass cut-off.

(4) WRF simulations validated against MGM observations show RMSE values of 1.96–5.45 m/s. The systematic positive bias is physically interpretable as the difference between exposed farm-site and sheltered station environments.

(5) The methodology yields actionable insights for early warning tools, turbine selection, and wind farm siting. Extension to longer time series and real-time implementation is recommended for future work.

---

## ACKNOWLEDGEMENTS

The first author would like to express sincere gratitude to his family for their unwavering support throughout this research. Special thanks are extended to Assoc. Prof. Elçin Tan for her invaluable guidance and supervision. The author also gratefully acknowledges Sude Çetinkaya for her continuous encouragement and support during the course of this study.

---

## REFERENCES

*Format: Times New Roman 10 pt; APA; alphabetical by surname; each entry indented 0.25 in; URLs as plain text (not hyperlinks); web sources listed last as Web 1, Web 2, …; access date given where applicable.*

Adomako, D., Boateng, G. O., & Osei, E. (2024). Machine learning approaches for wind speed forecasting using WRF outputs. *Renewable Energy*, *223*, 124–138.

Archer, C. L., Wu, S., & Ma, Y. (2020). Modeling the effects of extreme winds on wind turbine performance and energy yield. *Wind Energy Science*, *5*(2), 367–381.

Çetin, İ. İ. (2023). *Potential impacts of climate change on wind energy resources in Turkey* [Doctoral dissertation, Middle East Technical University].

Dadaser-Celik, F., & Cengiz, E. (2014). Wind speed trends over Turkey from 1975 to 2006. *International Journal of Climatology*, *34*(6), 1913–1927. https://doi.org/10.1002/joc.3810

Groch, J., & Vermeulen, R. (2021). Forecasting wind speed events at a utility-scale wind farm using a WRF–ANN model. *Energy Reports*, *7*, 915–926.

Hahmann, A. N., Vincent, C. L., Peña, A., Lange, J., & Hasager, C. B. (2014). Wind climate estimation using WRF model output: Method and model sensitivities over the sea. *International Journal of Climatology*, *35*(12), 435–452. https://doi.org/10.1002/joc.4217

Hahmann, A. N., Vincent, C. L., Peña, A., Lange, J., & Hasager, C. B. (2020). Wind climate estimation using WRF: Sensitivity to model configuration and validation with tall-mast data. *Wind Energy*, *23*(3), 623–643.

Karagiannis, G. M., Chondrogiannis, S., Krausmann, E., & Turksezer, Z. I. (2019). Climate change and critical infrastructure: Storms. Publications Office of the European Union.

Li, X., Zhang, H., & Zhao, X. (2021). Extreme wind climate assessment using WRF model and reanalysis datasets in complex terrain. *Atmospheric Research*, *249*, 105325.

Panteli, M., Trakas, D. N., Mancarella, P., & Hatziargyriou, N. D. (2017). Power systems resilience assessment: Hardening and operational measures against extreme weather. *IEEE Transactions on Power Systems*, *32*(6), 4272–4282.

Presidency of the Republic of Turkey, Strategy and Budget Directorate. (2023). *Twelfth Development Plan (2024–2028)*. Ankara.

Republic of Turkey, Ministry of Industry and Technology. (2019). *Turkey 2030 Industry and Technology Strategy*. Ankara.

Sahoo, B., & Bhaskaran, P. K. (2018). Assessment of tropical cyclone impacts on coastal power infrastructure using WRF simulations. *Natural Hazards*, *93*(2), 783–801.

Skamarock, C., Klemp, B., Dudhia, J., Gill, O., Liu, Z., Berner, J., Wang, W., Powers, G., Duda, G., Barker, D., & Huang, X. (2019). *A description of the advanced research WRF model version 4*. NCAR Tech. Note NCAR/TN-556+STR. https://doi.org/10.5065/1dfh-6p97

Sulikowska, A., & Wypych, A. (2021). Seasonal variability of trends in regional hot and warm temperature extremes in Europe. *Atmosphere*, *12*(5), 612. https://doi.org/10.3390/atmos1205061

Tan, E., Mentes, S. S., Unal, E., Unal, Y., Efe, B., Barutcu, B., Onol, B., Topcu, H. S., & Incecik, S. (2021). Short term wind energy resource prediction using WRF model for a location in western part of Turkey. *Journal of Renewable and Sustainable Energy*, *13*(1). https://doi.org/10.1063/5.0026391

Vemuri, V. R., Verma, S., & De Troch, R. (2022). Analysis of offshore wind energy resources and model sensitivity using WRF. *Journal of Physics: Conference Series*, *2265*(022014), 1–8.

Zheng, Z., Liu, W., & Jasiūnas, J. (2024). Climate change effects on wind power reliability and extreme shortage events. *Renewable and Sustainable Energy Reviews*, *190*, 113912.

**Web sources (access date given; URLs as plain text)**

Web 1. Committee, E. E. E. (2022). Energy Emergencies Executive Committee Storm Arwen review final report. Retrieved November 8, 2025, from https://assets.publishing.service.gov.uk/media/629fa8b1d3bf7f0371a9b0ca/storm-arwen-review-final-report.pdf

Web 2. Milliken, D. (2022, February 19). Over 150,000 British homes still without power after Storm Eunice. *Reuters*. Retrieved [date], from https://www.reuters.com/world/uk/more-than-200000-british-homes-still-without-power-after-storm-eunice-2022-02-19/

Web 3. Electric Insights. (2024). Q4 2023 report: Great Britain power system statistics. Imperial College London & Drax Group. Retrieved [date].

Web 4. Windpower Monthly. (2024, September 10). Rising contractor errors and defects behind two-thirds of offshore wind insurance claims – renewables insurer GCube. Retrieved [date].
