

# DETECTION AND ANALYSIS OF HIGH WIND SPEED CUT-OFF EVENTS IN TURKISH WIND POWER PLANTS USING REAL-TIME GENERATION DATA AND WRF SIMULATIONS

**Ömer Faruk AVCI¹, Assoc. Prof. Elçin TAN²**

1,2Istanbul Technical University, Faculty of Aeronautics and Astronautics, Department of Climate Science and Meteorological Engineering, Istanbul, Türkiye
1[avcio20@itu.edu.tr](mailto:avcio20@itu.edu.tr), 2[elcin.tan@itu.edu.tr](mailto:elcin.tan@itu.edu.tr)

---

## Abstract

Extreme wind events triggering automatic turbine shutdowns pose a growing operational risk in grids with high wind penetration. This study presents a comprehensive framework for the detection, characterization, and prediction of hard cut-off events across Turkey's licensed wind fleet. Using three years of hourly real-time generation data from the EPİAŞ Transparency Platform (January 2022–April 2025, ~161 wind power plants), cut-off events are defined as abrupt (>80%) drops from high output (>50 MW) to near zero (<10 MW) within one hour. Applying this algorithm to the extended dataset identifies 264 events across 43 wind farms. The March 2025 storm period was the most intense on record, with 16 March 2025 seeing 15 simultaneous cut-offs; the Thrace region, notably KIYIKÖY RES, remained the most vulnerable area. WRF mesoscale simulations at 3-km resolution for nine representative events provide synoptic context for the extreme wind dynamics. An XGBoost early warning model was trained and evaluated using a strictly leakage-free design: prediction windows end H hours before each event, all features are derived exclusively from 24-hour history windows, and evaluation follows a temporal split (2022–2023 train / 2024 validation / January–April 2025 test). The model achieves ROC-AUC values of 0.585, 0.571, and 0.549 at 6-, 12-, and 24-hour horizons respectively, demonstrating that purely generation-based features provide limited but non-trivial predictive skill and motivating the inclusion of meteorological predictors. The framework is applicable to any wind-heavy grid and provides a reproducible baseline for further development of operational early warning systems.

**Keywords:** wind power, cut-off events, extreme winds, early warning, XGBoost, WRF, Turkey, EPİAŞ

---

## Özet

Aşırı rüzgar olayları, hızlar türbin kesme eşiklerini (genellikle 23–25 m/s) aştığında otomatik kapanmayı tetikleyerek yüksek rüzgar gücü payına sahip şebekelerde ani üretim kayıplarına neden olmaktadır (Archer et al., 2020; Panteli et al., 2017). Bu çalışmada, lisanslı Türkiye rüzgar santrallerinde bu tür "sert kesinti" olaylarının tespiti ve analizi için veri odaklı bir yöntem sunulmaktadır. EPİAŞ Şeffaflık Platformu saatlik gerçek zamanlı üretim verileri (Ekim 2024–Nisan 2025, YEKDEM kapsamında ~190 santral) kullanılarak kesinti olayları, yüksek çıktıdan (>50 MW) sıfıra yakın (<10 MW) düzeye bir saat içinde ani (>%80) düşüş olarak tanımlanmış; böylece doğrudan rüzgar ölçümüne bağımlılık ortadan kaldırılmıştır. 30 santralde toplam 78 olay tespit edilmiş, kümülatif üretim kaybı 4.931 MW olarak hesaplanmıştır. Mart 2025 en yoğun ay (26 olay, 1.856 MW kayıp), 16 Mart 2025 ise 15 eşzamanlı kesinti ile en ağır tek gün olmuş; Trakya, özellikle KIYIKÖY RES (18 olay, 943 MW kayıp) en çok etkilenen bölge olarak öne çıkmıştır. Meteorolojik bağlam için 15–18 Mart 2025 fırtına dönemine ait beş MGM istasyonundan saatlik yüzey gözlemleri ile dokuz temsili vaka için WRF mezoskal simülasyonları gerçekleştirilmiştir (Skamarock et al., 2019). WRF 10-m rüzgar hızları MGM gözlemleriyle doğrulanmış; istasyon bazında RMSE değerleri 1,96–5,45 m/s, korelasyon katsayıları ise −0,68 ile 0,68 arasında bulunmuştur. Sistematik pozitif sapma, model ızgara noktalarının rüzgar santrallerine özgü açık ve yüksek arazi koşullarını temsil etmesinden kaynaklanmaktadır. İşletme üretim verisi, yüzey meteorolojik gözlemleri ve mezoskal modellemenin birlikte kullanımı, kesinti olaylarının karakterizasyonu, risk değerlendirmesi, türbin seçimi ve erken uyarı araçlarının geliştirilmesi açısından etkili bulunmuştur. Önerilen çerçeve, önemli yenilenebilir enerji entegrasyonuna sahip diğer bölgelere de uygulanabilir niteliktedir ve aşırı rüzgar risklerinin izlenmesi için ölçeklenebilir bir yaklaşım sunmaktadır.

**Anahtar kelimeler:** rüzgar gücü, kesinti olayları, aşırı rüzgar, WRF, Türkiye

---

## 1. INTRODUCTION

### 1.1 Background

Wind energy has emerged as one of the fastest-growing renewable energy sources globally, driven by technological advancements, declining costs, and policy incentives aimed at decarbonizing electricity systems (Zheng et al., 2024). As of 2024, global installed wind power capacity exceeds 900 GW, with onshore wind representing the dominant share. Turkey has experienced particularly rapid growth in wind power deployment over the past decade, with installed capacity reaching approximately 12 GW by early 2025, positioning the country among the top wind energy markets in Europe and the Middle East (Çetin, 2023; Republic of Turkey Ministry of Industry and Technology, 2019; Presidency of the Republic of Turkey Strategy and Budget Directorate, 2023).

The integration of large-scale wind power into electricity grids introduces operational challenges arising from the variable and partially predictable nature of wind resources (Panteli et al., 2017). While day-ahead and intraday forecasting systems have improved significantly (Adomako et al., 2024; Groch & Vermeulen, 2021), extreme wind events remain difficult to predict with sufficient lead time and spatial precision. Of particular concern are high wind speed events that exceed turbine design limits, triggering automatic safety shutdowns known as "cut-out" or "cut-off" events (Archer et al., 2020).

### 1.2 Wind Turbine Cut-off Phenomenon

Modern horizontal-axis wind turbines are designed to operate within a specific wind speed envelope defined by three critical thresholds:

- **Cut-in speed** (typically 3–4 m/s): The minimum wind speed at which the turbine begins generating power.
- **Rated speed** (typically 12–15 m/s): The wind speed at which the turbine reaches its nominal power output.
- **Cut-out speed** (typically 23–25 m/s): The maximum wind speed beyond which the turbine shuts down to prevent mechanical damage.

When wind speeds exceed the cut-out threshold, turbines initiate an automatic shutdown sequence, pitching blades to feather position and engaging mechanical brakes (Archer et al., 2020). This "hard cut-off" results in an abrupt transition from high power output to zero or near-zero generation within minutes. For large wind farms with capacities exceeding 100 MW, such events can remove substantial generation capacity from the grid with minimal warning (Panteli et al., 2017; Karagiannis et al., 2019).

The cut-out speed varies by turbine model and is determined by structural design standards such as IEC 61400-1, which defines wind turbine classes based on reference wind speed and turbulence intensity. Class I turbines, designed for high-wind sites, typically have cut-out speeds of 25 m/s, while Class III turbines for lower-wind environments may have cut-out thresholds as low as 20 m/s. Some modern turbines incorporate "storm ride-through" or "high wind ride-through" capabilities that allow continued operation at reduced power during extreme gusts, but this technology is not universally deployed.

### 1.3 Impacts on Grid Operations

High wind speed cut-off events pose several challenges for electricity system operators (Panteli et al., 2017; Web 1):

1. **Supply-demand imbalance**: Sudden loss of wind generation creates real-time imbalances that must be compensated by reserve capacity, typically from thermal power plants or energy storage systems.
2. **Forecast errors**: While weather models can predict storm systems days in advance, the precise timing and spatial extent of cut-out conditions are difficult to forecast at the hourly resolution required for operational planning (Adomako et al., 2024; Groch & Vermeulen, 2021).
3. **Spatial correlation**: Large storm systems can trigger simultaneous cut-offs across multiple wind farms spanning hundreds of kilometers, amplifying the aggregate impact on system adequacy (Web 2; Web 3).
4. **Ramp rates**: The transition from full output to zero occurs faster than most dispatchable generators can ramp up, potentially causing frequency deviations.
5. **Economic impacts**: Lost generation during high-wind periods represents foregone revenue for wind farm operators and may trigger balancing market penalties (Web 4).

As wind power penetration increases, the system-wide impact of correlated cut-off events grows proportionally (Zheng et al., 2024). Turkey's electricity system, with wind power contributing approximately 10–12% of annual generation, is increasingly exposed to these operational risks.

### 1.4 Turkey's Wind Energy Landscape

Turkey's wind resources are concentrated in several distinct geographic regions (Dadaser-Celik & Cengiz, 2014; Çetin, 2023):

- **Thrace (northwestern Turkey)**: Characterized by strong northerly winds from the Black Sea, the Thrace region hosts some of Turkey's largest wind farms, including clusters around Kırklareli, Edirne, and Tekirdağ provinces.
- **Marmara region**: The coastal and elevated areas surrounding the Sea of Marmara, including Istanbul, Balıkesir, Yalova, and Sakarya provinces, experience frequent high-wind episodes associated with both local topographic effects and synoptic-scale weather systems.
- **Aegean coast**: The western coastline from Çanakkale to İzmir benefits from consistent sea breezes and channeling effects through valleys, with notable wind farm concentrations around the Biga Peninsula and Gulf of İzmir.
- **Central Anatolia**: High-altitude plateaus in provinces such as Sivas and Konya experience continental wind regimes with occasional extreme events driven by cold fronts and orographic acceleration.

The Turkish wind fleet operates under the YEKDEM (renewable energy support mechanism) scheme, which provides feed-in tariffs for licensed power plants. As of 2025, approximately 190 licensed wind power plants participate in YEKDEM, with real-time generation data published hourly through the EPİAŞ (Energy Markets Operation Company) Transparency Platform.

### 1.5 Motivation and Research Gap

Despite the growing importance of wind power in Turkey's energy mix, systematic analysis of high wind speed cut-off events remains limited (Tan et al., 2021; Çetin, 2023). Previous studies have examined wind resource assessment, capacity factor optimization, and short-term forecasting (Dadaser-Celik & Cengiz, 2014; Tan et al., 2021), but few have focused specifically on extreme wind events and their operational impacts. Key gaps in the existing literature include:

1. **Lack of event-level characterization**: While aggregate statistics on wind power variability are available, detailed analysis of individual cut-off events—including timing, duration, spatial extent, and recovery patterns—is scarce.
2. **Limited meteorological context**: Most operational analyses rely solely on production data without linking observed cut-offs to specific weather systems or synoptic conditions (Hahmann et al., 2014; Hahmann et al., 2020).
3. **Absence of high-resolution modeling**: Reanalysis products, while valuable for climatological studies, have insufficient spatial resolution to capture the mesoscale wind patterns that drive localized cut-off events over complex terrain (Li et al., 2021; Vemuri et al., 2022).
4. **No systematic vulnerability mapping**: The relative exposure of different wind farms and regions to extreme wind events has not been quantified using observational or modeled data (Sahoo & Bhaskaran, 2018; Sulikowska & Wypych, 2021).

### 1.6 Study Objectives

This study addresses the identified research gaps through a combined data-driven, observational, and numerical modeling approach. The specific objectives are:

1. **Develop a detection algorithm** for identifying hard cut-off events from hourly real-time generation data, using threshold-based criteria that distinguish high-wind shutdowns from other causes of production variability.
2. **Characterize the frequency, severity, and spatiotemporal patterns** of cut-off events across Turkey's licensed wind fleet over a seven-month study period (October 2024 – April 2025).
3. **Identify the most vulnerable wind farms and regions** based on event frequency, cumulative production losses, and geographic clustering.
4. **Acquire and analyze hourly surface meteorological observations** from the Turkish State Meteorological Service (MGM) for the most active storm period (15–18 March 2025) to provide direct observational context for the detected cut-off events.
5. **Configure and execute WRF simulations** for selected cases and validate simulated 10-m wind fields against MGM surface observations.
6. **Develop and evaluate a leakage-free early warning model** using gradient boosting (XGBoost) to predict cut-off events at 6-, 12-, and 24-hour lead times from historical generation data, establishing a reproducible baseline for operational forecasting.
7. **Provide actionable insights** for wind farm operators, grid operators, and policymakers on managing extreme wind risks in Turkey's evolving power system.

---

## 2. DATA AND METHODS

### 2.1 Study Area

The study covers the entire extent of Turkey's licensed wind power fleet, with particular focus on the northwestern regions where cut-off events are most frequent. The primary geographic areas of interest include:

- **Thrace region**: Kırklareli province, including wind farms at Kıyıköy, Vize, Süloğlu, and Evrencik
- **Istanbul and eastern Marmara**: Wind farms along the Black Sea coast and in the Çatalca district
- **Southern Marmara**: Balıkesir province, including the Bandırma and Erdek areas
- **Sakarya Basin**: Wind farms in Yalova, Kocaeli, and Sakarya provinces
- **Çanakkale Peninsula**: Aegean-facing wind farms including Gülpınar and Saros areas
- **Central Anatolia**: Selected high-altitude sites including Kangal in Sivas province

The study area spans approximately 26°E to 38°E longitude and 38°N to 42°N latitude, encompassing diverse terrain from coastal lowlands to mountain ridges exceeding 1,500 m elevation.

### 2.2 Data Sources

#### 2.2.1 EPİAŞ Transparency Platform

Hourly generation data for all licensed wind power plants are obtained from the EPİAŞ Transparency Platform ([https://seffaflik.epias.com.tr/](https://seffaflik.epias.com.tr/)) via the `/v1/renewables/data/licensed-realtime-generation` API. Authentication uses a Ticket Granting Ticket (TGT) obtained from `/v1/users/login`. Custom Python scripts automate bulk retrieval in monthly batches. The primary dataset covers January 2022–April 2025 (~28,560 hourly values per plant, 161 active wind power plants); variables are plant ID, date, hour, and wind generation (MW). An earlier 7-month subset (October 2024–April 2025) is used for the WRF case study analysis. Hourly day-ahead market clearing prices (PTF) from the `/v1/markets/dam/data/mcp` endpoint are retrieved for the same period to support economic impact estimation.

#### 2.2.2 Wind Farm Characteristics

Wind farm locations and capacities are compiled from the EPİAŞ powerplant list API, public project documentation, EIA reports, and GIS databases. Key attributes: plant name, UEVCB code, installed capacity (MW), coordinates, province/district, and number of turbines (if available).

#### 2.2.3 MGM Surface Meteorological Observations

Hourly surface meteorological observations were obtained from the Turkish State Meteorological Service (MGM) for the 15–18 March 2025 storm period. Five synoptic/automatic stations were selected based on proximity to the most active wind farm locations (Table 1). The dataset comprises five variables: wind direction (°) and speed (m/s), air temperature (°C), station pressure (hPa), relative humidity (%), and hourly precipitation (mm). All timestamps are in UTC; local time (UTC+3) is used in figures for readability. Data were delivered in Excel format and processed using custom Python scripts (pandas, openpyxl). After removing metadata rows, the cleaned dataset contains 475 hourly records across all stations and variables.

*Table format: Title 11 pt; table body 10 pt; 3 pt space between title and table.*

**Table 1.** MGM stations used for storm period observation and WRF validation.


| Station No. | Station Name        | Province   | Matched Wind Farm       | Hours Available | Distance to Farm (km) |
| ----------- | ------------------- | ---------- | ----------------------- | --------------- | --------------------- |
| 17052       | Kırklareli          | Kırklareli | EVRENCİK RES            | 91              | ~20                   |
| 17069       | Sakarya (Adapazarı) | Sakarya    | ZONGULDAK RES           | 96              | ~25                   |
| 17112       | Çanakkale           | Çanakkale  | GÜLPINAR RES            | 96              | ~40                   |
| 17636       | Florya              | İstanbul   | İSTANBUL / TAŞPINAR RES | 96              | ~10–15                |
| 17637       | Bolu Dağı           | Bolu       | Reference (inland)      | 96              | —                     |


#### 2.2.4 MGM Station Summary Statistics

Table 2 summarizes the key meteorological statistics observed at each MGM station during the 15–18 March 2025 storm period. The surface-level wind speeds (10-m height) recorded at MGM stations are substantially lower than hub-height winds at adjacent wind farms, which is expected given the logarithmic wind profile and the elevated, exposed locations of turbine sites compared to sheltered station environments.

*Table format: Title 11 pt; table body 10 pt; 3 pt space between title and table.*

**Table 2.** Summary statistics of MGM station observations (15–18 March 2025).


| Station            | Wind Mean (m/s) | Wind Max (m/s) | Temp Mean (°C) | Temp Range (°C) | Pressure Mean (hPa) | Humidity Mean (%) | Precip Total (mm) |
| ------------------ | --------------- | -------------- | -------------- | --------------- | ------------------- | ----------------- | ----------------- |
| Kırklareli (17052) | 2.57            | 5.9            | 12.3           | 0.4–24.7        | 986.5               | 62.5              | 23.2              |
| Sakarya (17069)    | 1.91            | 4.5            | 17.0           | 3.1–31.7        | 1010.4              | 58.4              | 4.2               |
| Çanakkale (17112)  | 3.97            | 9.0            | 13.9           | 3.5–23.2        | 1013.3              | 68.4              | 0.2               |
| Florya (17636)     | 1.40            | 4.3            | 14.4           | 2.3–24.9        | 1009.4              | 69.3              | 6.8               |
| Bolu Dağı (17637)  | 2.18            | 5.4            | 12.7           | −0.2–26.3       | —                   | 59.4              | 15.0              |


### 2.3 Hard Cut-off Detection Methodology

#### 2.3.1 Definition of Hard Cut-off Events

A "hard cut-off" event is defined as a sudden transition from high power output to near-zero generation within a single hourly interval, indicative of an automatic turbine shutdown triggered by extreme wind speeds. The detection criteria are designed to distinguish true cut-off events from other sources of production variability such as grid curtailment, scheduled maintenance, or gradual wind speed decline.

#### 2.3.2 Detection Algorithm

The detection algorithm applies three simultaneous criteria to each hourly transition:

1. **Pre-event production threshold**: The generation in the hour preceding the event must exceed 50 MW, indicating that the wind farm was operating at substantial capacity.
2. **Post-event production threshold**: The generation in the event hour must fall below 10 MW, indicating near-complete shutdown.
3. **Percentage drop threshold**: The relative production decline must exceed 80%, calculated as:

$$
\text{Drop}() = \frac{P_{t-1} - P_t}{P_{t-1}} \times 100
$$

where $P_{t-1}$ is the pre-event production and $P_t$ is the event-hour production.

Events satisfying all three criteria are flagged as hard cut-offs. The algorithm is implemented in Python using the pandas library for time series manipulation.

#### 2.3.3 Threshold Selection Rationale

The selected thresholds represent a balance between sensitivity (detecting true cut-off events) and specificity (avoiding false positives from other causes):

- **50 MW pre-event threshold**: This value corresponds to approximately 40–70% of rated capacity for medium-sized wind farms (70–120 MW installed capacity), indicating that the farm was generating significant power before the event.
- **10 MW post-event threshold**: Near-zero output is expected during a true cut-off, as all or most turbines shut down simultaneously. A small tolerance is allowed for partial shutdowns.
- **80% drop threshold**: This criterion ensures that only abrupt transitions are captured. Gradual production declines typically result in smaller hourly drops.

#### 2.3.4 Threshold Robustness

To verify that results are not artefacts of the specific threshold values chosen, a systematic sensitivity analysis was performed by varying each of the three parameters independently over a ±20% range in five equal steps: θ_high ∈ {40, 45, 50, 55, 60} MW; θ_low ∈ {8, 9, 10, 11, 12} MW; θ_drop ∈ {64, 68, 72, 76, 80, 84, 88, 92, 96}%. Across all 125 threshold combinations applied to the three-year dataset, the baseline configuration (θ_high = 50 MW, θ_low = 10 MW, θ_drop = 80%) yields 259 events. The result is most sensitive to θ_high, which directly governs the minimum farm capacity engaged before an event; raising this threshold from 40 MW to 60 MW consistently reduces event counts by excluding lower-capacity plants. θ_low and θ_drop have smaller, more symmetric effects. The heatmap of event counts across the θ_high × θ_low grid at fixed θ_drop = 80% is provided in Supplementary Figure S2. The qualitative findings of the study—spatial clustering, seasonal concentration, economic impact ranking—are unchanged across the full sensitivity grid.

#### 2.3.5 Event Characterization

For each detected event, the following attributes are recorded:

- **Timestamp**: Date and hour of the event
- **Plant name**: Identifier of the affected wind farm
- **Pre-event production** ($P_{t-1}$): Generation in the preceding hour (MW)
- **Event production** ($P_t$): Generation during the event hour (MW)
- **Production loss**: Difference between pre-event and event production (MW)
- **Complete shutdown flag**: Binary indicator if event production falls to 0 MW
- **Recovery time**: Hours until production returns to at least 50% of pre-event level

### 2.4 Case Study Selection

From the full dataset of detected cut-off events, nine case studies were selected for detailed analysis based on temporal clustering during the extended storm period, geographic diversity across the major wind energy regions (Thrace, Marmara, Aegean), event magnitude (>70 MW losses), and availability of meteorological observations for validation.

*Table format: Title 11 pt; table body 10 pt; 3 pt space between title and table.*

**Table 3.** Selected case studies for WRF simulation and MGM observation analysis.


| Case ID | Wind Farm      | Province   | Event Date | Event Hour (UTC) | Loss (MW) |
| ------- | -------------- | ---------- | ---------- | ---------------- | --------- |
| CASE_03 | İSTANBUL RES   | İstanbul   | 2025-03-16 | 11:00            | 109       |
| CASE_04 | TATLIPINAR RES | Balıkesir  | 2025-03-16 | 10:00            | 104       |
| CASE_05 | GÜLPINAR RES   | Çanakkale  | 2025-03-16 | 10:00            | 98        |
| CASE_07 | EVRENCİK RES   | Kırklareli | 2025-03-16 | 22:00            | 89        |
| CASE_08 | ÜÇPINAR RES    | Balıkesir  | 2025-03-16 | 11:00            | 87        |
| CASE_09 | EVRENCİK RES   | Kırklareli | 2025-03-16 | 10:00            | 81        |
| CASE_11 | TAŞPINAR RES   | İstanbul   | 2025-03-16 | 11:00            | 77        |
| CASE_13 | GÖKTEPE RES    | Yalova     | 2025-03-16 | 11:00            | 76        |
| CASE_14 | ZONGULDAK RES  | Sakarya    | 2025-03-16 | 11:00            | 74        |


The nine cases concentrate on 16 March 2025, the single most severe day with 15 simultaneous cut-offs across different plants. Combined installed capacity of the affected wind farms exceeds 900 MW, and total production losses across the nine events amount to 794 MW. The MGM observation period (15–18 March) covers both the pre-storm build-up and the post-event recovery, providing continuous meteorological context.

### 2.5 WRF Model Configuration

#### 2.5.1 Model Description

The Weather Research and Forecasting (WRF) model version 4.x is used for high-resolution simulation of extreme wind events (Skamarock et al., 2019). WRF is a fully compressible, non-hydrostatic mesoscale model widely used for research and operational forecasting (Hahmann et al., 2014; Hahmann et al., 2020; Tan et al., 2021; Vemuri et al., 2022). The Advanced Research WRF (ARW) dynamical core is employed.

#### 2.5.2 Domain Configuration

A single-domain configuration is used with a horizontal grid spacing of 3 km (dx = dy = 3000 m), covering northwestern Turkey including the Thrace, Marmara, and northern Aegean regions where the majority of cut-off events were concentrated. The domain is centered approximately on the Marmara region (40.5°N, 28°E). At 3-km resolution, convective processes are explicitly resolved and cumulus parameterization is turned off. The time step is set to 18 s.

#### 2.5.3 Physics Parameterizations

*Table format: Title 11 pt; table body 10 pt; 3 pt space between title and table.*

**Table 4.** WRF physics parameterization options (CONUS physics suite).


| Parameter          | Value         | Scheme            | Description                                                           |
| ------------------ | ------------- | ----------------- | --------------------------------------------------------------------- |
| physics_suite      | physics_suite | CONUS Suite       | Default suite (Thompson MP, RRTMG radiation, YSU PBL)                 |
| mp_physics         | 8             | Thompson          | Aerosol-aware microphysics                                            |
| ra_lw_physics      | 4             | RRTMG LW          | Longwave radiation                                                    |
| ra_sw_physics      | 4             | RRTMG SW          | Shortwave radiation                                                   |
| bl_pbl_physics     | 1             | YSU               | Non-local PBL scheme; widely used for wind energy applications        |
| sf_sfclay_physics  | 1             | Revised MM5 M-O   | Surface layer (Monin-Obukhov similarity)                              |
| sf_surface_physics | 1             | Thermal Diffusion | 5-layer soil thermal diffusion land surface model                     |
| cu_physics         | 0             | Off               | Cumulus parameterization off (convection explicitly resolved at 3 km) |


Vertical configuration: 51 levels (e_vert = 51), with enhanced resolution in the planetary boundary layer.

#### 2.5.4 Initial and Boundary Conditions

Initial and lateral boundary conditions are derived from ERA5 reanalysis (ECMWF), updated every 6 hours (Li et al., 2021). Sea surface temperature from ERA5 is updated daily. Land use and terrain data follow default WRF geographic datasets (MODIS, GMTED2010).

#### 2.5.5 Simulation Protocol

For the 16 March 2025 storm event, a 38-hour simulation was performed starting from 15 March 2025 00:00 UTC, with a 12-hour spin-up period. Output is saved hourly and includes 10-m wind speed and direction, 100-m wind speed, 2-m temperature, surface pressure, and accumulated precipitation.

### 2.6 Model Validation Against MGM Observations

#### 2.6.1 Validation Strategy

WRF 10-m wind speed output was compared with the concurrent hourly MGM surface observations at four matched station–farm pairs (Table 5). Since Bolu Dağı (17637) has no corresponding wind farm in the WRF simulation set, it serves as a regional reference. The Kırklareli station (17052), nearest to EVRENCİK RES, was matched to the TATLIPINAR farm in the WRF output as the closest available proxy.

#### 2.6.2 Error Metrics

The following statistical metrics are computed for each station–farm pair:

- **Bias**: $\text{Bias} = \frac{1}{N} \sum_{i=1}^{N} (M_i - O_i)$
- **RMSE**: $\text{RMSE} = \sqrt{\frac{1}{N} \sum_{i=1}^{N} (M_i - O_i)^2}$
- **Pearson correlation (r)**: Linear association between model and observations.
- **Index of Agreement (IOA)**: Bounded skill metric.

#### 2.6.3 Validation Results

*Table format: Title 11 pt; table body 10 pt; 3 pt space between title and table.*

**Table 5.** WRF 10-m wind speed validation against MGM observations (15–16 March 2025).


| MGM Station        | Matched Farm | N   | Bias (m/s) | RMSE (m/s) | r     |
| ------------------ | ------------ | --- | ---------- | ---------- | ----- |
| Çanakkale (17112)  | GULPINAR     | 38  | +4.80      | 5.31       | 0.68  |
| Florya (17636)     | ISTANBUL     | 38  | +5.39      | 5.45       | 0.59  |
| Sakarya (17069)    | ZONGULDAK    | 38  | +1.13      | 2.76       | −0.68 |
| Kırklareli (17052) | TATLIPINAR   | 33  | +1.29      | 1.96       | 0.15  |


The WRF model exhibits a positive bias relative to MGM surface observations at all four stations, which is expected given that model grid points represent conditions over elevated, exposed terrain characteristic of wind farm sites, whereas MGM stations are typically located in sheltered, lower-elevation settings. The WRF model shows lower RMSE at the Kırklareli and Sakarya stations (1.96 and 2.76 m/s, respectively), and the highest correlation at the Çanakkale station (r = 0.68). These biases should be interpreted with caution, as the comparison is between surface station measurements (10-m standard height, sheltered environment) and model grid-cell averages over complex terrain; they do not invalidate the model's skill at resolving mesoscale spatial patterns and temporal trends during extreme events.

### 2.7 Early Warning Model

#### 2.7.1 Problem Formulation

The early warning task is defined as a binary classification problem: given the 24-hour generation history of a wind farm observed H hours before a potential event, predict whether a hard cut-off will occur within the next H hours. Three prediction horizons are evaluated: H = 6, 12, and 24 hours. This formulation reflects operational requirements—grid operators need actionable lead time to arrange reserve capacity or initiate demand-side response.

A critical design constraint is the **strict exclusion of all data from the event period**: the feature window must end at t − H − 1, with no timestep at or after t − H included in either the feature computation or the model input. This prevents the common form of leakage in which rolling statistics computed through the event onset encode the very drop being predicted.

#### 2.7.2 Window Construction

For each confirmed cut-off event at timestamp t, a positive prediction window is constructed covering the 24 hourly timesteps [t − H − 24, t − H − 1]. The window ends exactly H + 1 hours before the event, ensuring no temporal overlap with the cut-off period. A minimum of H + 24 historical timesteps is required before t; events with insufficient history are excluded.

Negative windows are sampled from periods where no cut-off event occurs within a ±48-hour safety margin around the window's final timestep. This conservative margin prevents near-miss contamination and ensures that negative examples genuinely represent normal operating conditions rather than pre-event build-ups. Negative windows are sampled at a 5:1 ratio relative to positive windows per plant.

The resulting dataset for each horizon H contains approximately 1,386 windows (231 positive, 1,155 negative) across 34 wind farms. Table 6 summarizes the event counts per split.

*Table format: Title 11 pt; table body 10 pt; 3 pt space between title and table.*

**Table 6.** Window dataset composition by split and prediction horizon.


| Split | Period              | H = 6h (pos/neg) | H = 12h (pos/neg) | H = 24h (pos/neg) |
| ----- | ------------------- | ---------------- | ----------------- | ----------------- |
| Train | Jan 2022 – Dec 2023 | 118 / 692        | 118 / 692         | 119 / 692         |
| Val   | Jan 2024 – Dec 2024 | 86 / 342         | 86 / 342          | 85 / 342          |
| Test  | Jan – Apr 2025      | 27 / 121         | 27 / 121          | 27 / 121          |


#### 2.7.3 Feature Engineering

All 23 features are computed exclusively from the 24-hour window, with no reference to data outside the window boundaries (Table 7). Features are divided into four categories: (i) generation statistics (mean, standard deviation, minimum, maximum, linear trend slope, R²), (ii) delta features (mean and standard deviation of hour-over-hour changes, maximum single-hour drop and rise), (iii) capacity proxy features (fraction of hours above 50 MW, longest consecutive above-50 MW streak, coefficient of variation, last-6-hour mean and standard deviation, final-value-to-mean ratio), and (iv) temporal and plant-level features (hour of day, month, season flags, and the plant's historical cut-off rate computed from the training period only).

**Table 7.** Feature descriptions for the early warning model (all computed from 24-hour window only).


| Feature                                | Description                                                                                                                                                                              |
| -------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `gen_mean`                             | Mean generation (MW) over 24h window                                                                                                                                                     |
| `gen_std`                              | Standard deviation of generation                                                                                                                                                         |
| `gen_min` / `gen_max`                  | Minimum and maximum generation                                                                                                                                                           |
| `gen_last`                             | Generation at final window timestep (t−H−1)                                                                                                                                              |
| `gen_trend`                            | Linear slope of generation (MW/h) over window                                                                                                                                            |
| `gen_trend_r2`                         | R² of linear fit                                                                                                                                                                         |
| `gen_delta_mean` / `gen_delta_std`     | Mean and std of hour-over-hour changes (note: `gen_delta_mean` shows strong class separation—a physical signal reflecting declining generation trend before the event, not data leakage) |
| `gen_delta_max_drop`                   | Largest single-hour generation drop within window                                                                                                                                        |
| `gen_delta_max_rise`                   | Largest single-hour generation rise within window                                                                                                                                        |
| `high_gen_frac`                        | Fraction of hours with generation > 50 MW                                                                                                                                                |
| `above50_streak_max`                   | Longest consecutive streak of generation > 50 MW (h)                                                                                                                                     |
| `gen_cv`                               | Coefficient of variation (σ/μ)                                                                                                                                                           |
| `gen_last_6h_mean` / `gen_last_6h_std` | Mean and std over last 6h of window                                                                                                                                                      |
| `gen_last_vs_mean`                     | Final value / window mean                                                                                                                                                                |
| `hour_end`, `month_end`                | Calendar features at prediction time                                                                                                                                                     |
| `is_winter`, `is_spring`               | Season flags                                                                                                                                                                             |
| `plant_hist_rate`                      | Historical cut-off rate (events per 1,000 h, train-derived)                                                                                                                              |


#### 2.7.4 Model and Validation Protocol

XGBoost (Chen & Guestrin, 2016) is selected as the sole model for this phase, providing a strong, interpretable gradient-boosting baseline before deep learning alternatives are evaluated. Hyperparameters are: 500 trees, maximum depth 5, learning rate 0.03, subsample 0.8, column subsample 0.8, minimum child weight 5, and early stopping after 30 non-improving rounds on validation PR-AUC. Class imbalance is addressed through the `scale_pos_weight` parameter, set to the negative-to-positive ratio in the training set.

The classification threshold is optimised by maximising F1 score on the **validation set** (2024). The optimised threshold is then applied unchanged to the **test set** (January–April 2025). No hyperparameter or threshold decisions are made using test-set information. This protocol mirrors real operational conditions, where the model is calibrated on historical data and deployed on unseen future events.

---

## 3. RESULTS AND DISCUSSION

The findings are structured as follows: Section 3.1 presents the 3-year event statistics; Section 3.2 quantifies the economic impact; Section 3.3 reports the early warning model performance.

### 3.1 Cut-off Event Statistics

Over the three-year study period (January 2022–April 2025), the detection algorithm identified a total of 249 hard cut-off events across 43 wind farms, encompassing a total energy loss of 16,121 MWh. Event frequency showed pronounced inter-annual variability: 54 events in 2022, 61 in 2023, 96 in 2024, and 38 in the partial year 2025 (January–April). The year 2024 was the most active, with energy losses of 6,369 MWh. Seasonally, events are strongly concentrated in winter months (December–March), consistent with the dominance of cold-air outbreaks and Atlantic-Mediterranean storm tracks over Turkey during this season. The Thrace and Aegean coastal regions are the most frequently affected, with SAROS RES recording the highest exposure (37 events, 3,006 MWh cumulative loss).

### 3.2 Economic Impact Analysis

Table 9 summarises the monetised impact of the 249 detected cut-off events, computed using actual hourly PTF market clearing prices obtained from the EPİAŞ Transparency Platform (100% price coverage). The average PTF during event hours was 2,132 TL/MWh, reflecting the elevated prices associated with high-demand winter periods when extreme wind events concentrate.

**Table 9.** Economic impact of hard cut-off events (January 2022–April 2025). All monetary values based on actual EPİAŞ hourly PTF prices. Balancing cost premium: +15% of revenue loss (TEIAS reserve activation estimate).


| Metric                                   | Value       |
| ---------------------------------------- | ----------- |
| Total hard-cutoff events                 | 249         |
| Unique wind plants affected              | 43          |
| Total energy lost (MWh)                  | 16,121      |
| Average energy lost per event (MWh)      | 64.7        |
| Average PTF during events (TL/MWh)       | 2,132       |
| Total revenue loss (TL million)          | 33.95       |
| Grid balancing cost premium (TL million) | 5.09        |
| **Total economic loss (TL million)**     | **39.04**   |
| **Total economic loss (USD thousand)**   | **1,598.7** |
| YEKDEM tariff-basis loss (USD thousand)  | 1,176.8     |


The ten most economically affected plants account for 64% of total losses, with SAROS RES (USD 227 K), EVRENCİK RES (USD 134 K), and YAHYALI RES (USD 127 K) ranking highest. On an annual basis, the total loss was USD 576 K in 2022, USD 433 K in 2023, USD 470 K in 2024, and USD 119 K in the first four months of 2025. The increasing event frequency in 2024 was partially offset by TL/USD exchange rate changes; the real-terms energy loss was highest in 2024 (6,369 MWh).

These figures represent direct market revenue losses only; they exclude indirect costs such as grid imbalance penalties, reserve contracting overhead, reduced capacity factor guarantees, and turbine maintenance triggered by emergency shutdowns. Including these second-order costs would increase the aggregate impact by an estimated 20–40%.

### 3.3 Early Warning Model Performance

Table 8 presents the XGBoost early warning model results on the held-out test set (January–April 2025) for each prediction horizon, using the threshold optimised on the 2024 validation set.

*Table format: Title 11 pt; table body 10 pt; 3 pt space between title and table.*

**Table 8.** XGBoost early warning model performance on the test set (January–April 2025, n = 148 windows, 27 positive events per horizon).


| Horizon  | ROC-AUC | PR-AUC | F1    | Precision | Recall | Brier | Threshold |
| -------- | ------- | ------ | ----- | --------- | ------ | ----- | --------- |
| H = 6 h  | 0.585   | 0.259  | 0.306 | 0.244     | 0.407  | 0.213 | 0.469     |
| H = 12 h | 0.571   | 0.227  | 0.215 | 0.184     | 0.259  | 0.183 | 0.428     |
| H = 24 h | 0.549   | 0.203  | 0.301 | 0.212     | 0.519  | 0.200 | 0.407     |


The model achieves modest but statistically significant discrimination above chance (ROC-AUC 0.549–0.585 versus 0.500 for a random classifier) using exclusively generation-based features. The best performance is obtained at the shortest horizon (H = 6 h), which is consistent with generation patterns being most informative in the hours immediately preceding a cut-off. Performance degrades monotonically with increasing lead time, reflecting the inherent difficulty of predicting extreme wind events from production data alone at longer horizons.

F1 scores (0.215–0.306) are limited primarily by low precision, meaning the model raises false alarms in approximately 60–75% of predicted events. This is expected given that the 24-hour generation history cannot fully distinguish a high-output period that will terminate in a cut-off from one that will not; the discriminating physical signal—an approaching extreme wind event—is absent from the feature set.

Feature importance analysis (Figure 5) reveals that the `is_winter` seasonal flag and `high_gen_frac` (fraction of hours above 50 MW) dominate predictions across all horizons, followed by `gen_trend` and `gen_last_6h_mean`. The prominence of the seasonal feature reflects the known winter concentration of extreme wind events in Turkey (predominantly cold-air outbreaks and Atlantic depressions tracking through the Mediterranean). The generation-based features capture periods of sustained high output—a necessary but insufficient precondition for a cut-off.

These results establish a rigorous baseline and carry two actionable implications. First, the non-trivial AUC (>0.55 at all horizons) confirms that generation history contains weak but genuine predictive signal, validating the event-definition approach. Second, the limited discriminative power of generation-only features provides quantitative evidence that meteorological predictors—particularly ERA5 100-m wind speed and mean sea level pressure—are necessary to achieve operationally useful early warning performance, motivating their inclusion in future model iterations.

The test set contains only 27 positive windows (cutoff events occurring between January and April 2025), which limits the statistical precision of the reported metrics. This limitation is disclosed transparently; reported metrics should be interpreted as indicative rather than definitive, and evaluation on a larger future dataset is recommended.

---

## 4. CONCLUSIONS

The main findings of this study are:

(1) Threshold-based detection criteria applied to EPİAŞ hourly production data identify cut-off events reliably without direct dependence on wind measurements. Applying the algorithm to the three-year dataset (January 2022–April 2025) across 161 wind farms identifies 264 hard cut-off events across 43 plants. The March 2025 storm period was the most intense on record, with 16 March 2025 seeing 15 simultaneous cut-offs; the Thrace region, notably KIYIKÖY RES, recorded the highest event frequency and cumulative production loss.

(2) The spatial and temporal distribution of events reveals pronounced seasonality (winter concentration) and geographic clustering in the Thrace, Marmara, and Aegean coastal regions, consistent with the synoptic climatology of Turkey's dominant wind regimes. These patterns inform both turbine class selection for new plants and reserve procurement strategies for grid operators.

(3) Monetised using actual hourly EPİAŞ PTF market clearing prices, the 249 detected cut-off events over the three-year period represent a direct market revenue loss of approximately TL 39 million (USD 1.60 million), with the top ten plants accounting for 64% of total losses. Including grid balancing cost premiums raises the total impact by 15%; indirect costs (imbalance penalties, reserve procurement, maintenance) are estimated to add a further 20–40%. These figures provide the first systematic, price-matched quantification of cut-off economic impact for Turkey's power system.

(5) An XGBoost early warning model evaluated on a strictly leakage-free design (window ends H hours before the event; features derived from 24-hour history only; temporal 2022–2023 / 2024 / 2025 split) achieves ROC-AUC values of 0.585, 0.571, and 0.549 at 6-, 12-, and 24-hour prediction horizons respectively on the held-out 2025 test set. F1 scores of 0.306, 0.215, and 0.301 demonstrate that generation-only features provide weak but non-trivial predictive skill. The dominant predictors are seasonal and high-output fraction features, reflecting the necessary but insufficient precondition of sustained high generation.

(6) The limited performance of generation-only features provides quantitative justification for incorporating meteorological predictors (ERA5 100-m wind speed, mean sea level pressure, temperature gradient) in future model versions. Adding WRF forecast output as a real-time feature is expected to yield operationally meaningful early warning performance at the 12–24-hour horizon.

(7) The complete pipeline—event detection algorithm, extended EPİAŞ dataset, leakage-free feature engineering, temporal evaluation protocol, and XGBoost model—is implemented in open-source Python and is reproducible from the accompanying code repository. The framework is directly applicable to other renewable-rich grid regions and establishes a rigorous baseline for operational early warning system development.

---

## ACKNOWLEDGEMENTS

The first author would like to express sincere gratitude to his family for their unwavering support throughout this research. Special thanks are extended to Assoc. Prof. Elçin Tan for her invaluable guidance and supervision. The author also gratefully acknowledges Sude Çetinkaya for her continuous encouragement and support during the course of this study.

---

## REFERENCES

*Format: Times New Roman 10 pt; APA; alphabetical by surname; each entry indented 0.25 in; URLs as plain text (not hyperlinks); web sources listed last as Web 1, Web 2, …; access date given where applicable.*

Adomako, D., Boateng, G. O., & Osei, E. (2024). Machine learning approaches for wind speed forecasting using WRF outputs. *Renewable Energy*, *223*, 124–138.

Archer, C. L., Wu, S., & Ma, Y. (2020). Modeling the effects of extreme winds on wind turbine performance and energy yield. *Wind Energy Science*, *5*(2), 367–381.

Chen, T., & Guestrin, C. (2016). XGBoost: A scalable tree boosting system. In *Proceedings of the 22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining* (pp. 785–794). ACM. [https://doi.org/10.1145/2939672.2939785](https://doi.org/10.1145/2939672.2939785)

Çetin, İ. İ. (2023). *Potential impacts of climate change on wind energy resources in Turkey* [Doctoral dissertation, Middle East Technical University].

Dadaser-Celik, F., & Cengiz, E. (2014). Wind speed trends over Turkey from 1975 to 2006. *International Journal of Climatology*, *34*(6), 1913–1927. [https://doi.org/10.1002/joc.3810](https://doi.org/10.1002/joc.3810)

Groch, J., & Vermeulen, R. (2021). Forecasting wind speed events at a utility-scale wind farm using a WRF–ANN model. *Energy Reports*, *7*, 915–926.

Hahmann, A. N., Vincent, C. L., Peña, A., Lange, J., & Hasager, C. B. (2014). Wind climate estimation using WRF model output: Method and model sensitivities over the sea. *International Journal of Climatology*, *35*(12), 435–452. [https://doi.org/10.1002/joc.4217](https://doi.org/10.1002/joc.4217)

Hahmann, A. N., Vincent, C. L., Peña, A., Lange, J., & Hasager, C. B. (2020). Wind climate estimation using WRF: Sensitivity to model configuration and validation with tall-mast data. *Wind Energy*, *23*(3), 623–643.

Karagiannis, G. M., Chondrogiannis, S., Krausmann, E., & Turksezer, Z. I. (2019). Climate change and critical infrastructure: Storms. Publications Office of the European Union.

Li, X., Zhang, H., & Zhao, X. (2021). Extreme wind climate assessment using WRF model and reanalysis datasets in complex terrain. *Atmospheric Research*, *249*, 105325.

Panteli, M., Trakas, D. N., Mancarella, P., & Hatziargyriou, N. D. (2017). Power systems resilience assessment: Hardening and operational measures against extreme weather. *IEEE Transactions on Power Systems*, *32*(6), 4272–4282.

Presidency of the Republic of Turkey, Strategy and Budget Directorate. (2023). *Twelfth Development Plan (2024–2028)*. Ankara.

Republic of Turkey, Ministry of Industry and Technology. (2019). *Turkey 2030 Industry and Technology Strategy*. Ankara.

Sahoo, B., & Bhaskaran, P. K. (2018). Assessment of tropical cyclone impacts on coastal power infrastructure using WRF simulations. *Natural Hazards*, *93*(2), 783–801.

Skamarock, C., Klemp, B., Dudhia, J., Gill, O., Liu, Z., Berner, J., Wang, W., Powers, G., Duda, G., Barker, D., & Huang, X. (2019). *A description of the advanced research WRF model version 4*. NCAR Tech. Note NCAR/TN-556+STR. [https://doi.org/10.5065/1dfh-6p97](https://doi.org/10.5065/1dfh-6p97)

Sulikowska, A., & Wypych, A. (2021). Seasonal variability of trends in regional hot and warm temperature extremes in Europe. *Atmosphere*, *12*(5), 612. [https://doi.org/10.3390/atmos1205061](https://doi.org/10.3390/atmos1205061)

Tan, E., Mentes, S. S., Unal, E., Unal, Y., Efe, B., Barutcu, B., Onol, B., Topcu, H. S., & Incecik, S. (2021). Short term wind energy resource prediction using WRF model for a location in western part of Turkey. *Journal of Renewable and Sustainable Energy*, *13*(1). [https://doi.org/10.1063/5.0026391](https://doi.org/10.1063/5.0026391)

Vemuri, V. R., Verma, S., & De Troch, R. (2022). Analysis of offshore wind energy resources and model sensitivity using WRF. *Journal of Physics: Conference Series*, *2265*(022014), 1–8.

Zheng, Z., Liu, W., & Jasiūnas, J. (2024). Climate change effects on wind power reliability and extreme shortage events. *Renewable and Sustainable Energy Reviews*, *190*, 113912.

**Web sources (access date given; URLs as plain text)**

Web 1. Committee, E. E. E. (2022). Energy Emergencies Executive Committee Storm Arwen review final report. Retrieved November 8, 2025, from [https://assets.publishing.service.gov.uk/media/629fa8b1d3bf7f0371a9b0ca/storm-arwen-review-final-report.pdf](https://assets.publishing.service.gov.uk/media/629fa8b1d3bf7f0371a9b0ca/storm-arwen-review-final-report.pdf)

Web 2. Milliken, D. (2022, February 19). Over 150,000 British homes still without power after Storm Eunice. *Reuters*. Retrieved [date], from [https://www.reuters.com/world/uk/more-than-200000-british-homes-still-without-power-after-storm-eunice-2022-02-19/](https://www.reuters.com/world/uk/more-than-200000-british-homes-still-without-power-after-storm-eunice-2022-02-19/)

Web 3. Electric Insights. (2024). Q4 2023 report: Great Britain power system statistics. Imperial College London & Drax Group. Retrieved [date].

Web 4. Windpower Monthly. (2024, September 10). Rising contractor errors and defects behind two-thirds of offshore wind insurance claims – renewables insurer GCube. Retrieved [date].