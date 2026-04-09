# Short Summaries

This document contains condensed versions of each major section for quick reference, conference abstracts, or poster presentations.

---

## Abstract (Short Version)

This study analyzes high wind speed cut-off events in Turkish wind power plants using real-time generation data from the EPİAŞ Transparency Platform and Weather Research and Forecasting (WRF) model simulations. Over a seven-month period (October 2024 – April 2025), 78 hard cut-off events affecting 30 wind farms are identified, with a cumulative production loss of 4,931 MW. The Thrace and Marmara regions emerge as the most vulnerable areas, with March 2025 accounting for one-third of all events. Nine representative case studies from an extended storm period (March 16–24, 2025) are selected for high-resolution WRF simulations across two nested domains, covering wind farms from the Aegean to eastern Marmara. The combined data-driven detection and numerical modeling approach enables systematic characterization of extreme wind exposure and supports grid reliability planning in regions with expanding wind power capacity.

---

## Introduction (Short Version)

Wind energy has become a cornerstone of Turkey's electricity system, with installed capacity reaching approximately 12 GW by 2025 and contributing 10–12% of annual generation. However, the integration of large-scale wind power introduces operational challenges, particularly during extreme wind events that exceed turbine design limits and trigger automatic safety shutdowns known as "cut-off" events. When wind speeds surpass the cut-out threshold (typically 23–25 m/s), turbines abruptly transition from full power output to zero generation, creating sudden supply-demand imbalances that challenge grid operators. Large storm systems can cause simultaneous cut-offs across multiple wind farms spanning hundreds of kilometers, amplifying system-wide impacts. Despite the growing importance of wind power in Turkey's energy mix, systematic analysis of these high wind speed cut-off events remains limited, with key gaps including lack of event-level characterization, limited meteorological context, absence of high-resolution modeling, and no systematic vulnerability mapping across wind farm portfolios.

---

## Data and Methods (Short Version)

**Data Collection and Cut-off Detection:** Real-time generation data for approximately 190 licensed wind power plants in Turkey are retrieved from the EPİAŞ Transparency Platform via REST API for the period October 2024 – April 2025. A threshold-based detection algorithm identifies hard cut-off events by flagging hourly transitions where production drops exceed 80 percent from high-generation states (>50 MW) to near-zero output (<10 MW), indicating automatic turbine shutdowns triggered by extreme wind speeds. This approach enables systematic detection of cut-off events using production data as a proxy for nacelle-level wind measurements. Supporting data include wind farm characteristics from EPİAŞ, surface observations from the Turkish State Meteorological Service (MGM) for model validation, and ERA5 reanalysis from ECMWF for WRF boundary conditions.

**WRF Modeling:** Nine case studies representing cut-off events during an extended storm period (March 16–24, 2025) are selected for high-resolution numerical weather prediction using the WRF model. A two-domain nested configuration is employed with 9 km (D01) and 3 km (D02) horizontal resolution to resolve mesoscale wind patterns over northwestern Turkey. The selected cases span a geographic corridor from the Aegean coast (Çanakkale) through the Marmara region (Balıkesir, İstanbul, Yalova, Sakarya) to Thrace (Kırklareli), with affected wind farms representing a combined installed capacity exceeding 900 MW. For each case, 48-hour simulations are performed with ERA5 initial and boundary conditions, and output wind fields at hub-height levels are validated against surface observations and used to characterize the spatial extent, intensity, and temporal evolution of extreme wind conditions associated with each cut-off event.

---
