# Detection and Analysis of High Wind Speed Cut-off Events in Turkish Wind Power Plants Using Real-Time Generation Data and WRF Simulations

## Abstract

Extreme wind events pose significant operational challenges for wind energy systems, triggering automatic turbine shutdowns when wind speeds exceed design cut-out thresholds, typically 23–25 m/s. These hard cut-off events result in sudden production losses across wind farms and represent a critical aspect of grid reliability in regions with high wind power penetration. This study develops a data-driven framework to systematically detect and characterize high wind speed cut-off events across licensed wind power plants in Turkey using hourly real-time generation data from the EPİAŞ (Energy Exchange Istanbul) Transparency Platform, and applies the Weather Research and Forecasting (WRF) model to simulate selected extreme events at high spatial resolution.

A seven-month dataset spanning October 2024 to April 2025 is analyzed, covering approximately 190 wind power plants under the YEKDEM renewable energy support scheme. Hard cut-off events are identified using threshold-based criteria that capture sudden production drops exceeding 80 percent from high-generation states (>50 MW) to near-zero output (<10 MW) within a single hour. This approach enables detection of cut-off events without direct access to nacelle-level wind speed measurements, leveraging production patterns as a proxy for extreme wind conditions.

Results reveal 78 distinct hard cut-off events affecting 30 wind farms, with a cumulative production loss of 4,931 MW over the study period. Strong seasonal clustering is observed, with March 2025 accounting for 33 percent of all events (26 cut-offs, 1,856 MW loss). The most extreme storm day, March 16, 2025, recorded 15 simultaneous cut-offs across geographically dispersed facilities within a 12-hour window, indicating the passage of a large-scale synoptic storm system. Geographic analysis identifies the Thrace region as the most vulnerable area, with KIYIKÖY RES alone experiencing 18 events and 943 MW of cumulative production loss. The largest individual event occurred at KANGAL RES on December 14, 2024, with a complete shutdown from 121 MW to 0 MW.

For high-resolution meteorological analysis, nine case studies representing cut-off events during an extended storm period from March 16–24, 2025 are selected for WRF simulations. These cases span a geographic corridor from the Aegean coast (Çanakkale) through the Marmara region (Balıkesir, İstanbul, Yalova, Sakarya) to Thrace (Kırklareli), capturing the spatial evolution of extreme winds across northwestern Turkey. WRF simulations are configured with two nested domains to resolve mesoscale wind patterns at kilometer-scale resolution, with ERA5 reanalysis data providing boundary conditions. The selected wind farms—including TATLIPINAR, GÜLPINAR, EVRENCİK, İSTANBUL, ÜÇPINAR, TAŞPINAR, GÖKTEPE, and ZONGULDAK RES—represent a combined installed capacity exceeding 900 MW and production losses of 794 MW during the study period. Simulated wind fields are validated against surface meteorological observations and used to characterize the temporal evolution, spatial extent, and intensity of extreme wind conditions associated with each cut-off event.

This study demonstrates the value of combining transparency platform data with mesoscale numerical weather prediction for operational monitoring and retrospective analysis of extreme wind impacts on power systems. The methodology provides a scalable approach for identifying high-risk wind farms, characterizing seasonal and spatial patterns of cut-off exposure, and linking production anomalies to synoptic-scale weather systems. Findings support improved wind farm siting decisions, turbine selection based on regional wind climatology, and development of early warning systems for grid operators managing high wind power penetration scenarios.

---

**Keywords:** wind power, cut-off events, extreme winds, EPİAŞ, Turkey, WRF, wind turbine, grid reliability, renewable energy, mesoscale modeling

---

## 1. Introduction

### 1.1 Background

Wind energy has emerged as one of the fastest-growing renewable energy sources globally, driven by technological advancements, declining costs, and policy incentives aimed at decarbonizing electricity systems. As of 2024, global installed wind power capacity exceeds 900 GW, with onshore wind representing the dominant share. Turkey has experienced particularly rapid growth in wind power deployment over the past decade, with installed capacity reaching approximately 12 GW by early 2025, positioning the country among the top wind energy markets in Europe and the Middle East.

The integration of large-scale wind power into electricity grids introduces operational challenges arising from the variable and partially predictable nature of wind resources. While day-ahead and intraday forecasting systems have improved significantly, extreme wind events remain difficult to predict with sufficient lead time and spatial precision. Of particular concern are high wind speed events that exceed turbine design limits, triggering automatic safety shutdowns known as "cut-out" or "cut-off" events.

### 1.2 Wind Turbine Cut-off Phenomenon

Modern horizontal-axis wind turbines are designed to operate within a specific wind speed envelope defined by three critical thresholds:

- **Cut-in speed** (typically 3–4 m/s): The minimum wind speed at which the turbine begins generating power.
- **Rated speed** (typically 12–15 m/s): The wind speed at which the turbine reaches its nominal power output.
- **Cut-out speed** (typically 23–25 m/s): The maximum wind speed beyond which the turbine shuts down to prevent mechanical damage.

When wind speeds exceed the cut-out threshold, turbines initiate an automatic shutdown sequence, pitching blades to feather position and engaging mechanical brakes. This "hard cut-off" results in an abrupt transition from high power output to zero or near-zero generation within minutes. For large wind farms with capacities exceeding 100 MW, such events can remove substantial generation capacity from the grid with minimal warning.

The cut-out speed varies by turbine model and is determined by structural design standards such as IEC 61400-1, which defines wind turbine classes based on reference wind speed and turbulence intensity. Class I turbines, designed for high-wind sites, typically have cut-out speeds of 25 m/s, while Class III turbines for lower-wind environments may have cut-out thresholds as low as 20 m/s. Some modern turbines incorporate "storm ride-through" or "high wind ride-through" capabilities that allow continued operation at reduced power during extreme gusts, but this technology is not universally deployed.

### 1.3 Impacts on Grid Operations

High wind speed cut-off events pose several challenges for electricity system operators:

1. **Supply-demand imbalance**: Sudden loss of wind generation creates real-time imbalances that must be compensated by reserve capacity, typically from thermal power plants or energy storage systems.

2. **Forecast errors**: While weather models can predict storm systems days in advance, the precise timing and spatial extent of cut-out conditions are difficult to forecast at the hourly resolution required for operational planning.

3. **Spatial correlation**: Large storm systems can trigger simultaneous cut-offs across multiple wind farms spanning hundreds of kilometers, amplifying the aggregate impact on system adequacy.

4. **Ramp rates**: The transition from full output to zero occurs faster than most dispatchable generators can ramp up, potentially causing frequency deviations.

5. **Economic impacts**: Lost generation during high-wind periods represents foregone revenue for wind farm operators and may trigger balancing market penalties.

As wind power penetration increases, the system-wide impact of correlated cut-off events grows proportionally. Turkey's electricity system, with wind power contributing approximately 10–12% of annual generation, is increasingly exposed to these operational risks.

### 1.4 Turkey's Wind Energy Landscape

Turkey's wind resources are concentrated in several distinct geographic regions:

- **Thrace (northwestern Turkey)**: Characterized by strong northerly winds from the Black Sea, the Thrace region hosts some of Turkey's largest wind farms, including clusters around Kırklareli, Edirne, and Tekirdağ provinces.

- **Marmara region**: The coastal and elevated areas surrounding the Sea of Marmara, including Istanbul, Balıkesir, Yalova, and Sakarya provinces, experience frequent high-wind episodes associated with both local topographic effects and synoptic-scale weather systems.

- **Aegean coast**: The western coastline from Çanakkale to İzmir benefits from consistent sea breezes and channeling effects through valleys, with notable wind farm concentrations around the Biga Peninsula and Gulf of İzmir.

- **Central Anatolia**: High-altitude plateaus in provinces such as Sivas and Konya experience continental wind regimes with occasional extreme events driven by cold fronts and orographic acceleration.

The Turkish wind fleet operates under the YEKDEM (Yenilenebilir Enerji Kaynakları Destekleme Mekanizması) renewable energy support mechanism, which provides feed-in tariffs for licensed power plants. As of 2025, approximately 190 licensed wind power plants participate in YEKDEM, with real-time generation data published hourly through the EPİAŞ (Enerji Piyasaları İşletme A.Ş.) Transparency Platform.

### 1.5 Motivation and Research Gap

Despite the growing importance of wind power in Turkey's energy mix, systematic analysis of high wind speed cut-off events remains limited. Previous studies have examined wind resource assessment, capacity factor optimization, and short-term forecasting, but few have focused specifically on extreme wind events and their operational impacts. Key gaps in the existing literature include:

1. **Lack of event-level characterization**: While aggregate statistics on wind power variability are available, detailed analysis of individual cut-off events—including timing, duration, spatial extent, and recovery patterns—is scarce.

2. **Limited meteorological context**: Most operational analyses rely solely on production data without linking observed cut-offs to specific weather systems or synoptic conditions.

3. **Absence of high-resolution modeling**: Reanalysis products such as ERA5, while valuable for climatological studies, have insufficient spatial resolution (0.25° × 0.25°, approximately 25–30 km) to capture the mesoscale wind patterns that drive localized cut-off events over complex terrain.

4. **No systematic vulnerability mapping**: The relative exposure of different wind farms and regions to extreme wind events has not been quantified using observational or modeled data.

### 1.6 Study Objectives

This study addresses the identified research gaps through a combined data-driven and numerical modeling approach. The specific objectives are:

1. **Develop a detection algorithm** for identifying hard cut-off events from hourly real-time generation data, using threshold-based criteria that distinguish high-wind shutdowns from other causes of production variability.

2. **Characterize the frequency, severity, and spatiotemporal patterns** of cut-off events across Turkey's licensed wind fleet over a seven-month study period (October 2024 – April 2025).

3. **Identify the most vulnerable wind farms and regions** based on event frequency, cumulative production losses, and geographic clustering.

4. **Select representative case studies** for high-resolution numerical weather prediction analysis, focusing on an extended storm period in March 2025 that produced multiple correlated cut-off events.

5. **Configure and execute WRF simulations** for the selected cases using nested domains to resolve kilometer-scale wind patterns over the affected regions.

6. **Validate simulated wind fields** against surface meteorological observations and assess the model's ability to reproduce the timing and intensity of extreme wind conditions.

7. **Provide actionable insights** for wind farm operators, grid operators, and policymakers on managing extreme wind risks in Turkey's evolving power system.

---

## 2. Data and Methods

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

Real-time generation data for licensed renewable energy power plants are obtained from the EPİAŞ Transparency Platform (https://seffaflik.epias.com.tr/). The platform provides hourly generation values in megawatts (MW) for each YEKDEM-registered facility, published with a delay of approximately one hour after the end of each settlement period.

Data are retrieved via the EPİAŞ REST API using the following endpoint:
- `/v1/renewables/data/licensed-realtime-generation`

The API requires authentication via a Ticket Granting Ticket (TGT) mechanism. Custom Python scripts are developed to automate data retrieval, handling pagination, rate limiting, and data format conversion.

The retrieved dataset includes:
- **Temporal coverage**: October 1, 2024 to April 30, 2025 (7 months, approximately 5,100 hourly observations per plant)
- **Spatial coverage**: Approximately 190 licensed wind power plants
- **Variables**: Plant identifier, date, hour, and generation (MW)

#### 2.2.2 Wind Farm Characteristics

Supplementary information on wind farm locations and capacities is compiled from:
- EPİAŞ licensed powerplant list API (`/v1/renewables/data/licensed-powerplant-list`)
- Publicly available project documentation and environmental impact assessments
- Geographic information system (GIS) databases of renewable energy installations

Key attributes include:
- Plant name and unique identifier (UEVCB code)
- Installed capacity (MW, both licensed and actual)
- Approximate geographic coordinates (latitude, longitude)
- Province and district location
- Number of turbines (where available)

#### 2.2.3 Meteorological Observations

Surface meteorological observations are obtained from the Turkish State Meteorological Service (MGM) network for model validation purposes. Stations are selected based on proximity to wind farm locations, with priority given to stations providing hourly wind speed and direction data. The matched meteorological stations for the selected case study wind farms are summarized in Table 1.

**Table 1.** Meteorological stations matched to case study wind farms.

| Wind Farm | Province | Nearest Station | Station Code | Distance (km) |
|-----------|----------|-----------------|--------------|---------------|
| KANGAL RES | Sivas | Kangal | KNGL | ~15 |
| GÜLPINAR RES | Çanakkale | Çanakkale | CNKL | ~40 |
| İSTANBUL RES | İstanbul | Çatalca | CTLC | ~10 |
| TATLIPINAR RES | Balıkesir | Balıkesir | BLKS | ~25 |
| EVRENCİK RES | Kırklareli | Kırklareli | KRKL | ~20 |
| ÜÇPINAR RES | Balıkesir | Balıkesir | BLKS | ~20 |
| TAŞPINAR RES | İstanbul | Çatalca | CTLC | ~15 |
| GÖKTEPE RES | Yalova | Yalova | YALV | ~10 |
| ZONGULDAK RES | Sakarya | Adapazarı | ADPZ | ~25 |

#### 2.2.4 ERA5 Reanalysis

ERA5 reanalysis data from the European Centre for Medium-Range Weather Forecasts (ECMWF) are used to provide initial and boundary conditions for WRF simulations. ERA5 offers global coverage at 0.25° × 0.25° horizontal resolution with hourly temporal resolution, making it suitable for downscaling applications.

Variables retrieved include:
- Three-dimensional atmospheric fields: geopotential height, temperature, specific humidity, u- and v-wind components at pressure levels from 1000 hPa to 50 hPa
- Surface fields: 2-m temperature, 10-m u- and v-wind, surface pressure, sea surface temperature, soil temperature and moisture
- Temporal coverage: 48-hour windows centered on each case study event

Data are retrieved from the Copernicus Climate Data Store (CDS) using the CDS API.

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

- **50 MW pre-event threshold**: This value corresponds to approximately 40–70% of rated capacity for medium-sized wind farms (70–120 MW installed capacity), indicating that the farm was generating significant power before the event. Lower thresholds would include events where farms were already operating at reduced output due to low wind speeds.

- **10 MW post-event threshold**: Near-zero output is expected during a true cut-off, as all or most turbines shut down simultaneously. A small tolerance is allowed for partial shutdowns or residual generation from turbines with different cut-out thresholds.

- **80% drop threshold**: This criterion ensures that only abrupt transitions are captured. Gradual production declines, such as those associated with slow wind speed changes or partial curtailment, typically result in smaller hourly drops.

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

#### 2.4.1 Selection Criteria

From the full dataset of detected cut-off events, nine case studies are selected for detailed WRF modeling based on the following criteria:

1. **Temporal clustering**: Events occurring during an extended storm period with multiple correlated cut-offs across different wind farms
2. **Geographic diversity**: Coverage of the major wind energy regions (Thrace, Marmara, Aegean)
3. **Event magnitude**: Priority given to events with larger production losses (>70 MW)
4. **Data availability**: Adequate meteorological observations for model validation

#### 2.4.2 Selected Cases

The selected case studies represent nine cut-off events occurring during a nine-day storm period from March 16–24, 2025. This period was chosen because it captures the evolution of a major synoptic disturbance that affected wind farms across northwestern Turkey in sequence.

**Table 2.** Selected case studies for WRF simulation.

| Case ID | Wind Farm | Province | Lat (°N) | Lon (°E) | Event Date | Event Hour | Loss (MW) |
|---------|-----------|----------|----------|----------|------------|------------|-----------|
| CASE_04 | TATLIPINAR RES | Balıkesir | 39.75 | 28.15 | 2025-03-16 | 10:00 | 104.2 |
| CASE_05 | GÜLPINAR RES | Çanakkale | 39.48 | 26.08 | 2025-03-17 | 10:00 | 97.7 |
| CASE_09 | EVRENCİK RES | Kırklareli | 41.55 | 27.45 | 2025-03-18 | 10:00 | 80.9 |
| CASE_03 | İSTANBUL RES | İstanbul | 41.18 | 28.35 | 2025-03-19 | 10:00 | 108.8 |
| CASE_08 | ÜÇPINAR RES | Balıkesir | 39.68 | 28.10 | 2025-03-20 | 10:00 | 87.0 |
| CASE_11 | TAŞPINAR RES | İstanbul | 41.12 | 28.42 | 2025-03-21 | 10:00 | 77.2 |
| CASE_13 | GÖKTEPE RES | Yalova | 40.55 | 29.25 | 2025-03-22 | 10:00 | 76.0 |
| CASE_14 | ZONGULDAK RES | Sakarya | 40.72 | 30.18 | 2025-03-23 | 10:00 | 73.9 |
| CASE_07 | EVRENCİK RES | Kırklareli | 41.55 | 27.45 | 2025-03-24 | 10:00 | 88.6 |

The nine cases span a geographic corridor from the Aegean coast (Çanakkale, 26°E) through the southern Marmara basin (Balıkesir) to the Bosphorus region (İstanbul) and eastern Marmara (Yalova, Sakarya, up to 30°E), with northern extension into Thrace (Kırklareli). Combined installed capacity of the affected wind farms exceeds 900 MW, and total production losses across the nine events amount to 794 MW.

### 2.5 WRF Model Configuration

#### 2.5.1 Model Description

The Weather Research and Forecasting (WRF) model version 4.x is used for high-resolution simulation of extreme wind events. WRF is a fully compressible, non-hydrostatic mesoscale model widely used for research and operational forecasting applications. The Advanced Research WRF (ARW) dynamical core is employed.

#### 2.5.2 Domain Configuration

A two-domain nested configuration is designed to balance computational efficiency with spatial resolution over the target regions:

**Domain 1 (D01) – Outer Domain**
- Horizontal resolution: 9 km
- Grid dimensions: To be determined based on coverage requirements
- Coverage: Broader region encompassing Turkey and surrounding areas to capture synoptic-scale forcing
- Purpose: Downscaling from ERA5 boundary conditions; representing large-scale atmospheric dynamics

**Domain 2 (D02) – Inner Domain**
- Horizontal resolution: 3 km
- Grid dimensions: To be determined
- Coverage: Northwestern Turkey including Thrace, Marmara, and northern Aegean regions
- Purpose: Resolving mesoscale wind patterns, terrain-induced acceleration, and coastal effects
- One-way nesting from D01

The domains are centered approximately on the Marmara region (40.5°N, 28°E) to ensure coverage of all nine case study wind farms within D02.

#### 2.5.3 Vertical Configuration

- Number of vertical levels: 45
- Model top: 50 hPa
- Vertical coordinate: Terrain-following hybrid sigma-pressure
- Enhanced resolution in the planetary boundary layer (PBL) with approximately 10 levels below 1 km AGL

#### 2.5.4 Physics Parameterizations

The following physics options are selected based on previous WRF studies over complex terrain and coastal regions:

| Component | Scheme | Reference |
|-----------|--------|-----------|
| Microphysics | Thompson | Thompson et al. (2008) |
| Longwave radiation | RRTMG | Iacono et al. (2008) |
| Shortwave radiation | RRTMG | Iacono et al. (2008) |
| Surface layer | Revised MM5 | Jiménez et al. (2012) |
| Land surface | Noah-MP | Niu et al. (2011) |
| Planetary boundary layer | MYNN Level 2.5 | Nakanishi and Niino (2009) |
| Cumulus (D01 only) | Kain-Fritsch | Kain (2004) |

Cumulus parameterization is disabled for D02 (3 km resolution), where convective processes are explicitly resolved.

#### 2.5.5 Initial and Boundary Conditions

- **Initial conditions**: ERA5 reanalysis interpolated to WRF grid
- **Lateral boundary conditions**: ERA5 updated every 6 hours
- **Sea surface temperature**: ERA5 SST, updated daily
- **Land use and terrain**: Default WRF geographic data at appropriate resolution (MODIS land use, GMTED2010 terrain)

#### 2.5.6 Simulation Protocol

For each case study, a 48-hour simulation is performed following this protocol:

1. **Spin-up period**: 12 hours before the analysis period to allow model adjustment
2. **Pre-event period**: 24 hours before the cut-off event to capture the approach of the weather system
3. **Post-event period**: 12 hours after the event to observe recovery conditions

Example for CASE_04 (TATLIPINAR RES, event at 2025-03-16 10:00):
- Simulation start: 2025-03-14 22:00 UTC
- Simulation end: 2025-03-16 22:00 UTC
- Analysis period: 2025-03-15 10:00 to 2025-03-16 22:00 UTC

#### 2.5.7 Output Variables

WRF output is saved at hourly intervals and includes:
- 10-m wind speed and direction (U10, V10)
- 80-m and 100-m wind speed (hub-height relevant levels)
- Maximum wind gust (diagnostic)
- 2-m temperature and relative humidity
- Surface pressure
- Planetary boundary layer height
- Precipitation (accumulated)

### 2.6 Model Validation

#### 2.6.1 Validation Strategy

WRF simulations are validated against available surface observations from the MGM station network. Validation focuses on:
- 10-m wind speed magnitude
- Wind direction
- Timing of peak wind events

#### 2.6.2 Error Metrics

The following statistical metrics are computed for each validation station:

- **Bias**: Mean difference between simulated and observed values
$$\text{Bias} = \frac{1}{N} \sum_{i=1}^{N} (M_i - O_i)$$

- **Root Mean Square Error (RMSE)**:
$$\text{RMSE} = \sqrt{\frac{1}{N} \sum_{i=1}^{N} (M_i - O_i)^2}$$

- **Pearson correlation coefficient (r)**: Measures linear association between model and observations

- **Index of Agreement (IOA)**: Bounded metric for model skill (Willmott, 1981)

where $M_i$ represents modeled values, $O_i$ represents observed values, and $N$ is the number of observations.

#### 2.6.3 Threshold Exceedance Analysis

In addition to continuous validation metrics, the model's ability to simulate the timing and spatial extent of wind speeds exceeding the cut-out threshold (25 m/s) is assessed through:
- Contingency table analysis (hit rate, false alarm rate, critical success index)
- Time series comparison of observed vs. simulated wind speed at matched station locations

### 2.7 Analysis Framework

#### 2.7.1 Climatological Analysis

The full seven-month dataset of detected cut-off events is analyzed to characterize:
- Monthly and seasonal distribution of events
- Diurnal patterns (if present)
- Geographic clustering and regional vulnerability
- Event magnitude distribution (production losses)
- Recovery time statistics

#### 2.7.2 Storm Event Characterization

For the March 16–24, 2025 storm period, WRF output is used to:
- Reconstruct the synoptic evolution of the weather system
- Map the spatial extent and intensity of extreme winds at hourly intervals
- Identify the propagation path and timing of the cut-out wind speed threshold across the study domain
- Correlate simulated hub-height wind speeds with observed production losses at each wind farm

#### 2.7.3 Exposure Assessment

Wind farm exposure to extreme winds is quantified using WRF-derived indicators:
- Maximum simulated wind speed at each farm location
- Duration above 20 m/s and 25 m/s thresholds
- Peak gust speed
- Comparison with turbine design class wind speed limits


