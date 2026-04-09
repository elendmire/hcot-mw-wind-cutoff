<!--
FORMATTING (Word/PDF export): Font: Times New Roman. Body: 12 pt, line spacing 1, justified, 1 line space between paragraphs. Abstract: 11 pt. Title: 13 pt, ALL CAPS. Authors: 11 pt. Table titles & figure captions: 11 pt. Table body: 10 pt. References: 10 pt. First page ≤1 page; total ≤10 pages. Main headings: 12 pt ALL CAPS. Subheading–text: 6 pt space; no space between subheading and following text. Figure/table: 3 pt above caption; 1 line space after caption. No paragraph indent in Introduction.
-->

# DETECTION AND ANALYSIS OF HIGH WIND SPEED CUT-OFF EVENTS IN TURKISH WIND POWER PLANTS USING REAL-TIME GENERATION DATA AND WRF SIMULATIONS

**Ömer Faruk AVCI¹, Assoc. Prof. Elçin TAN²**

<sup>1,2</sup>Istanbul Technical University, Faculty of Aeronautics and Astronautics, Department of Climate Science and Meteorological Engineering, Istanbul, Türkiye
<sup>1</sup>avcio20@itu.edu.tr, <sup>2</sup>elcin.tan@itu.edu.tr

---

## Abstract

Extreme wind events can trigger automatic turbine shutdowns when speeds exceed cut-out thresholds (typically 23–25 m/s), causing sudden generation losses in grids with high wind penetration (Archer et al., 2020; Panteli et al., 2017). This study presents a data-driven method to detect and analyze such "hard cut-off" events across licensed Turkish wind farms. Using hourly real-time production data from the EPİAŞ Transparency Platform (October 2024–April 2025, ~190 plants under YEKDEM), cut-off events are defined as abrupt (>80%) drops from high output (>50 MW) to near zero (<10 MW) within one hour, avoiding direct reliance on wind measurements. A total of 78 events were identified across 30 wind farms, with cumulative production losses of 4,931 MW. March 2025 was the most active month (26 events, 1,856 MW lost), and 16 March 2025 the most severe single day, with 15 simultaneous cut-offs; Thrace was hit hardest, notably KIYIKÖY RES (18 events, 943 MW lost). For meteorological context, hourly surface observations from five Turkish State Meteorological Service (MGM) stations were acquired for the 15–18 March 2025 storm period, alongside WRF mesoscale simulations for nine representative cases (Skamarock et al., 2019). WRF 10-m wind speeds were validated against MGM observations, yielding RMSE values of 1.96–5.45 m/s. The combination of operational generation data, surface meteorological observations, and mesoscale modeling effectively characterizes cut-off events and supports risk assessment, turbine selection, wind farm siting, and the development of early warning tools for grid operators. The proposed framework is applicable to other regions with significant renewable integration and offers a scalable approach for monitoring extreme wind risks.

**Keywords:** wind power, cut-off events, extreme winds, WRF, Turkey

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

6. **Provide actionable insights** for wind farm operators, grid operators, and policymakers on managing extreme wind risks in Turkey's evolving power system.

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

Hourly generation data for all licensed wind power plants are obtained from the EPİAŞ Transparency Platform (https://seffaflik.epias.com.tr/) via the `/v1/renewables/data/licensed-realtime-generation` API. Authentication uses a Ticket Granting Ticket (TGT). Custom scripts automate retrieval and processing. The dataset covers October 2024–April 2025 (~5,100 hourly values per plant, ~190 plants); variables are plant ID, date, hour, and generation (MW).

#### 2.2.2 Wind Farm Characteristics

Wind farm locations and capacities are compiled from the EPİAŞ powerplant list API, public project documentation, EIA reports, and GIS databases. Key attributes: plant name, UEVCB code, installed capacity (MW), coordinates, province/district, and number of turbines (if available).

#### 2.2.3 MGM Surface Meteorological Observations

Hourly surface meteorological observations were obtained from the Turkish State Meteorological Service (MGM) for the 15–18 March 2025 storm period. Five synoptic/automatic stations were selected based on proximity to the most active wind farm locations (Table 1). The dataset comprises five variables: wind direction (°) and speed (m/s), air temperature (°C), station pressure (hPa), relative humidity (%), and hourly precipitation (mm). All timestamps are in UTC; local time (UTC+3) is used in figures for readability. Data were delivered in Excel format and processed using custom Python scripts (pandas, openpyxl). After removing metadata rows, the cleaned dataset contains 475 hourly records across all stations and variables.

*Table format: Title 11 pt; table body 10 pt; 3 pt space between title and table.*

**Table 1.** MGM stations used for storm period observation and WRF validation.

| Station No. | Station Name | Province | Matched Wind Farm | Hours Available | Distance to Farm (km) |
|-------------|-------------|----------|-------------------|----------------:|---------------------:|
| 17052 | Kırklareli | Kırklareli | EVRENCİK RES | 91 | ~20 |
| 17069 | Sakarya (Adapazarı) | Sakarya | ZONGULDAK RES | 96 | ~25 |
| 17112 | Çanakkale | Çanakkale | GÜLPINAR RES | 96 | ~40 |
| 17636 | Florya | İstanbul | İSTANBUL / TAŞPINAR RES | 96 | ~10–15 |
| 17637 | Bolu Dağı | Bolu | Reference (inland) | 96 | — |

#### 2.2.4 MGM Station Summary Statistics

Table 2 summarizes the key meteorological statistics observed at each MGM station during the 15–18 March 2025 storm period. The surface-level wind speeds (10-m height) recorded at MGM stations are substantially lower than hub-height winds at adjacent wind farms, which is expected given the logarithmic wind profile and the elevated, exposed locations of turbine sites compared to sheltered station environments.

*Table format: Title 11 pt; table body 10 pt; 3 pt space between title and table.*

**Table 2.** Summary statistics of MGM station observations (15–18 March 2025).

| Station | Wind Mean (m/s) | Wind Max (m/s) | Temp Mean (°C) | Temp Range (°C) | Pressure Mean (hPa) | Humidity Mean (%) | Precip Total (mm) |
|---------|---:|---:|---:|---:|---:|---:|---:|
| Kırklareli (17052) | 2.57 | 5.9 | 12.3 | 0.4–24.7 | 986.5 | 62.5 | 23.2 |
| Sakarya (17069) | 1.91 | 4.5 | 17.0 | 3.1–31.7 | 1010.4 | 58.4 | 4.2 |
| Çanakkale (17112) | 3.97 | 9.0 | 13.9 | 3.5–23.2 | 1013.3 | 68.4 | 0.2 |
| Florya (17636) | 1.40 | 4.3 | 14.4 | 2.3–24.9 | 1009.4 | 69.3 | 6.8 |
| Bolu Dağı (17637) | 2.18 | 5.4 | 12.7 | −0.2–26.3 | — | 59.4 | 15.0 |

### 2.3 Hard Cut-off Detection Methodology

#### 2.3.1 Definition of Hard Cut-off Events

A "hard cut-off" event is defined as a sudden transition from high power output to near-zero generation within a single hourly interval, indicative of an automatic turbine shutdown triggered by extreme wind speeds. The detection criteria are designed to distinguish true cut-off events from other sources of production variability such as grid curtailment, scheduled maintenance, or gradual wind speed decline.

#### 2.3.2 Detection Algorithm

The detection algorithm applies three simultaneous criteria to each hourly transition:

1. **Pre-event production threshold**: The generation in the hour preceding the event must exceed 50 MW, indicating that the wind farm was operating at substantial capacity.

2. **Post-event production threshold**: The generation in the event hour must fall below 10 MW, indicating near-complete shutdown.

3. **Percentage drop threshold**: The relative production decline must exceed 80%, calculated as:

$$
\text{Drop}(\%) = \frac{P_{t-1} - P_t}{P_{t-1}} \times 100
$$

where $P_{t-1}$ is the pre-event production and $P_t$ is the event-hour production.

Events satisfying all three criteria are flagged as hard cut-offs. The algorithm is implemented in Python using the pandas library for time series manipulation.

#### 2.3.3 Threshold Selection Rationale

The selected thresholds represent a balance between sensitivity (detecting true cut-off events) and specificity (avoiding false positives from other causes):

- **50 MW pre-event threshold**: This value corresponds to approximately 40–70% of rated capacity for medium-sized wind farms (70–120 MW installed capacity), indicating that the farm was generating significant power before the event.

- **10 MW post-event threshold**: Near-zero output is expected during a true cut-off, as all or most turbines shut down simultaneously. A small tolerance is allowed for partial shutdowns.

- **80% drop threshold**: This criterion ensures that only abrupt transitions are captured. Gradual production declines typically result in smaller hourly drops.

#### 2.3.4 Event Characterization

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

| Case ID | Wind Farm | Province | Event Date | Event Hour (UTC) | Loss (MW) |
|---------|-----------|----------|------------|-----------------|----------:|
| CASE_03 | İSTANBUL RES | İstanbul | 2025-03-16 | 11:00 | 109 |
| CASE_04 | TATLIPINAR RES | Balıkesir | 2025-03-16 | 10:00 | 104 |
| CASE_05 | GÜLPINAR RES | Çanakkale | 2025-03-16 | 10:00 | 98 |
| CASE_07 | EVRENCİK RES | Kırklareli | 2025-03-16 | 22:00 | 89 |
| CASE_08 | ÜÇPINAR RES | Balıkesir | 2025-03-16 | 11:00 | 87 |
| CASE_09 | EVRENCİK RES | Kırklareli | 2025-03-16 | 10:00 | 81 |
| CASE_11 | TAŞPINAR RES | İstanbul | 2025-03-16 | 11:00 | 77 |
| CASE_13 | GÖKTEPE RES | Yalova | 2025-03-16 | 11:00 | 76 |
| CASE_14 | ZONGULDAK RES | Sakarya | 2025-03-16 | 11:00 | 74 |

The nine cases concentrate on 16 March 2025, the single most severe day with 15 simultaneous cut-offs across different plants. Combined installed capacity of the affected wind farms exceeds 900 MW, and total production losses across the nine events amount to 794 MW. The MGM observation period (15–18 March) covers both the pre-storm build-up and the post-event recovery, providing continuous meteorological context.

### 2.5 WRF Model Configuration

#### 2.5.1 Model Description

The Weather Research and Forecasting (WRF) model version 4.x is used for high-resolution simulation of extreme wind events (Skamarock et al., 2019). WRF is a fully compressible, non-hydrostatic mesoscale model widely used for research and operational forecasting (Hahmann et al., 2014; Hahmann et al., 2020; Tan et al., 2021; Vemuri et al., 2022). The Advanced Research WRF (ARW) dynamical core is employed.

#### 2.5.2 Domain Configuration

A single-domain configuration is used with a horizontal grid spacing of 3 km (dx = dy = 3000 m), covering northwestern Turkey including the Thrace, Marmara, and northern Aegean regions where the majority of cut-off events were concentrated. The domain is centered approximately on the Marmara region (40.5°N, 28°E). At 3-km resolution, convective processes are explicitly resolved and cumulus parameterization is turned off. The time step is set to 18 s.

#### 2.5.3 Physics Parameterizations

*Table format: Title 11 pt; table body 10 pt; 3 pt space between title and table.*

**Table 4.** WRF physics parameterization options (CONUS physics suite).

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

| MGM Station | Matched Farm | N | Bias (m/s) | RMSE (m/s) | r |
|-------------|-------------|--:|---:|---:|---:|
| Çanakkale (17112) | GULPINAR | 38 | +4.80 | 5.31 | 0.68 |
| Florya (17636) | ISTANBUL | 38 | +5.39 | 5.45 | 0.59 |
| Sakarya (17069) | ZONGULDAK | 38 | +1.13 | 2.76 | −0.68 |
| Kırklareli (17052) | TATLIPINAR | 33 | +1.29 | 1.96 | 0.15 |

The WRF model exhibits a positive bias relative to MGM surface observations at all four stations, which is expected given that model grid points represent conditions over elevated, exposed terrain characteristic of wind farm sites, whereas MGM stations are typically located in sheltered, lower-elevation settings. The WRF model shows lower RMSE at the Kırklareli and Sakarya stations (1.96 and 2.76 m/s, respectively), and the highest correlation at the Çanakkale station (r = 0.68). These biases should be interpreted with caution, as the comparison is between surface station measurements (10-m standard height, sheltered environment) and model grid-cell averages over complex terrain; they do not invalidate the model's skill at resolving mesoscale spatial patterns and temporal trends during extreme events.

---

## 3. RESULTS AND DISCUSSION

The cut-off detection algorithm and MGM observations together provide a comprehensive picture of the 15–18 March 2025 storm period. The findings are presented below before any figure or table, in accordance with formatting guidelines.

### 3.1 Cut-off Event Statistics

Over the seven-month study period (October 2024–April 2025), the detection algorithm identified a total of 78 hard cut-off events across 30 wind farms, with cumulative production losses of 4,931 MW. March 2025 was the most active month, accounting for 26 events and 1,856 MW of lost production. The single most severe day was 16 March 2025, when 15 simultaneous cut-offs were observed across different plants. Geographically, the Thrace region was the most affected, with KIYIKÖY RES recording the highest exposure (18 events, 943 MW cumulative loss).

### 3.2 Meteorological Context: MGM Observations

Hourly surface observations from five MGM stations during the 15–18 March 2025 period reveal the synoptic evolution of the storm system. The Kırklareli station, located in the most heavily affected Thrace region, recorded the lowest mean station pressure (986.5 hPa, minimum 976.8 hPa), the highest total precipitation (23.2 mm), and moderate wind speeds (mean 2.57 m/s, max 5.9 m/s at 10-m height). The Çanakkale station on the Aegean coast registered the highest surface wind speeds (mean 3.97 m/s, max 9.0 m/s), consistent with its exposed coastal position near the Dardanelles. Florya (Istanbul) and Sakarya exhibited lower surface winds but recorded significant pressure drops, indicating the passage of the frontal system.

Figure 1 presents the hourly wind speed evolution at all five stations, with the 20 m/s and 25 m/s thresholds marked. Although surface-level (10-m) measurements at MGM stations are expectedly lower than hub-height conditions at wind farm sites, the temporal patterns—particularly the wind acceleration beginning on 15 March and peaking on 16 March—correlate with the timing of the observed cut-off events.

![Figure 1](mgm_analysis/figures/fig1_wind_speed_timeseries.png)

**Figure 1.** Hourly 10-m wind speed at five MGM stations during the 15–18 March 2025 storm period. Dashed red line: turbine cut-out threshold (25 m/s); dotted orange line: warning level (20 m/s). All times in local time (UTC+3).

Figure 2 presents a five-panel meteorological overview showing the concurrent evolution of wind speed, wind direction, temperature, station pressure, and precipitation. The sharp pressure drop at Kırklareli on 16 March, accompanied by a directional shift and temperature change, marks the passage of the cold front associated with the mass cut-off event. Bolu Dağı, serving as an inland reference, shows elevated precipitation (15.0 mm total) and lower temperatures, reflecting orographic enhancement.

![Figure 2](mgm_analysis/figures/fig2_meteorological_overview.png)

**Figure 2.** Five-panel meteorological overview of the 15–18 March 2025 storm period: (a) wind speed, (b) wind direction, (c) air temperature, (d) station pressure, (e) hourly precipitation. Data from five MGM stations.

Figure 3 provides a zoomed view of 16 March 2025, the most severe day, highlighting the hourly wind speed and pressure at each station during the period when 15 simultaneous cut-offs occurred.

![Figure 3](mgm_analysis/figures/fig5_march16_detail.png)

**Figure 3.** Hourly wind speed (a) and station pressure (b) on 16 March 2025, the day with the highest number of simultaneous cut-off events (15 plants). Local time (UTC+3).

### 3.3 WRF Validation Against MGM Observations

The WRF model was validated against MGM surface observations for the overlapping 15–16 March 2025 period at four matched station–farm pairs (Table 5). Time series comparisons (Figure 7) show that the WRF model captures the general temporal trends but overestimates 10-m wind speeds relative to the sheltered MGM stations, with biases of +1.13 to +5.39 m/s. This systematic overestimation is physically consistent with the fact that wind farm grid points are located on exposed ridges and elevated terrain, whereas MGM stations occupy valley or lowland environments.

The scatter comparison (Figure 4) confirms the positive bias pattern for WRF relative to MGM observations across all stations. The strongest agreement is observed at the Çanakkale station (r = 0.68), while the Sakarya station shows the weakest correlation (r = −0.68), likely reflecting the greater distance and terrain complexity between the MGM station and the matched wind farm location. Overall, WRF at 3-km resolution captures mesoscale features—terrain channeling, coastal convergence, and frontal dynamics—that are relevant for characterizing the wind conditions leading to turbine cut-off events.

![Figure 4](mgm_analysis/figures/fig8_scatter_wrf_era5_vs_mgm.png)

**Figure 4.** Scatter plot of WRF simulated vs. MGM observed 10-m wind speed at four matched station–farm pairs during 15–16 March 2025. Overall bias, RMSE, and correlation are shown in the inset.

### 3.4 Relationship Between Surface Observations and Cut-off Events

While the MGM 10-m surface wind speeds did not reach the turbine cut-out threshold (25 m/s) during the observation period, this finding is consistent with the well-documented vertical wind shear effect: hub-height winds (80–100 m) are typically 1.5–2.5 times surface values, depending on atmospheric stability and terrain roughness (Hahmann et al., 2020). The WRF 100-m simulations for the corresponding period show wind speeds exceeding 15 m/s at several farm locations, with the model's 10-m output already averaging 3–9 m/s (compared to MGM observed 1–5 m/s). Extrapolating the WRF wind profile to hub height at the exposed farm sites would yield values consistent with cut-out conditions.

---

## 4. CONCLUSIONS

The main findings of this study are:

(1) Threshold-based detection criteria applied to EPİAŞ hourly production data identify cut-off events reliably without direct dependence on wind measurements. Over the seven-month study period, 78 events were detected across 30 plants, with total losses of 4,931 MW.

(2) The prolonged storm period in March 2025 accounted for the highest number of events and the largest losses, with 16 March 2025 as the single most severe day (15 simultaneous cut-offs). Thrace, notably the Kıyıköy area, was identified as the region with the highest cut-off frequency and loss magnitude.

(3) Hourly MGM surface observations from five stations during the 15–18 March 2025 period provide direct meteorological context for the detected events. The sharp pressure drop at Kırklareli (minimum 976.8 hPa), elevated Aegean coastal wind speeds (max 9.0 m/s at Çanakkale), and significant precipitation (23.2 mm at Kırklareli, 15.0 mm at Bolu Dağı) characterize the synoptic forcing behind the mass cut-off event.

(4) WRF simulations, validated against MGM observations at four matched station–farm pairs, show RMSE values of 1.96–5.45 m/s for 10-m wind speed. The systematic positive bias is physically interpretable as the difference between exposed farm-site and sheltered station environments. WRF at 3-km resolution captures mesoscale dynamics relevant to cut-off prediction.

(5) The methodology yields actionable insights for grid operators in terms of early warning tools, turbine class selection, and wind farm siting. Extension to longer time series, additional stations with anemometric mast data, and real-time implementation of the detection algorithm is recommended for future work.

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
