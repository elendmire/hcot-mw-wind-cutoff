# WRF 2-Domain Simulation Workflow
## Hard Cutoff Event: 15–18 March 2025

---

## Domain Configuration

| Parameter | d01 (outer) | d02 (inner) |
|---|---|---|
| Resolution | 9 km | 3 km |
| Grid (e_we × e_sn) | 201 × 181 | 202 × 199 |
| Extent | ~1800 × 1620 km | ~603 × 594 km |
| Coverage | Turkey + Balkans + E. Med | NW Turkey (Marmara, Çanakkale, Aegean) |
| Nesting ratio | — | 1:3 (one-way + feedback=1) |
| Time step | 54 s | 18 s |
| Cu scheme | Kain-Fritsch | OFF (convective-permitting) |

**Center (Lambert Conformal):** 35.0°E, 39.5°N  
**True latitudes:** 37°N, 42°N

### Why 2 domains?
The 2-domain setup provides:
1. **Better boundary conditions** for d02 via a properly spun-up outer domain
2. **Synoptic-scale forcing** captured at 9 km (Bora-type flow, Mediterranean cyclones)
3. **Reduced boundary artifacts** vs. driving 3 km directly from ERA5 (0.25°~28 km)
4. **Standard practice** for Q1 papers on regional wind energy (Priya et al., 2021; Santoni et al., 2020)

---

## Physics Configuration

| Scheme | d01 | d02 | Rationale |
|---|---|---|---|
| Microphysics | Thompson (8) | Thompson (8) | Better aerosol/cloud for storm cases |
| LW Radiation | RRTMG (4) | RRTMG (4) | More accurate than RRTM for OLR |
| SW Radiation | RRTMG (4) | RRTMG (4) | Spectral bands improve accuracy |
| Surface layer | MM5 similarity (1) | MM5 similarity (1) | Tested in Turkey Aegean studies |
| Land surface | Noah LSM (2) | Noah LSM (2) | Full soil moisture, sea surface |
| PBL | YSU (1) | YSU (1) | Non-local, stable conditions |
| Cumulus | Kain-Fritsch (1) | OFF (0) | Not needed at 3 km |

---

## Step-by-Step Workflow

### 0. Prerequisites
```bash
# WRF v4.x compiled with ERA5 support
module load wrf/4.4
export WPS_DIR=/path/to/WPS
export WRF_DIR=/path/to/WRF
export GEOG_DIR=/path/to/WPS_GEOG
```

### 1. ERA5 Boundary Data
Download ERA5 GRIB2 files for 2025-03-14 00Z – 2025-03-18 00Z:
```bash
# Use era5_downloader.py (already exists in this repo)
cd /path/to/repo
python era5_downloader.py --storm-only   # downloads March 15-18 high-res event
```

Required ERA5 variables for WPS:
- Pressure levels (1000–1 hPa): U, V, T, Q, Z
- Surface: MSLP, 2m T, 2m Td, 10m U, 10m V, SST, soil T/moisture

### 2. WPS — Geogrid
```bash
cd $WPS_DIR
cp /path/to/repo/wrf/namelist.wps.2dom namelist.input
# IMPORTANT: Update geog_data_path in namelist.wps.2dom
./geogrid.exe >& log.geogrid
# Check: geo_em.d01.nc and geo_em.d02.nc created
# Verify i_parent_start/j_parent_start match planned coverage
```

**After geogrid, update `namelist.input.2dom`:**
```python
# Run this helper to extract actual parent start indices from geogrid output
import netCDF4 as nc
d01 = nc.Dataset('geo_em.d01.nc')
d02 = nc.Dataset('geo_em.d02.nc')
print("d02 i_parent_start:", d02.i_parent_start)
print("d02 j_parent_start:", d02.j_parent_start)
```

### 3. WPS — Ungrib (ERA5 → WPS format)
```bash
ln -sf $WPS_DIR/ungrib/Variable_Tables/Vtable.ERA-interim.pl Vtable
./link_grib.csh /path/to/era5/grib/*.grib2
./ungrib.exe >& log.ungrib
```

### 4. WPS — Metgrid
```bash
./metgrid.exe >& log.metgrid
# Check: met_em.d01.2025-03-14_00:00:00.nc, met_em.d02.*.nc created
```

### 5. WRF — Real (initialization)
```bash
cd $WRF_DIR/run
cp /path/to/repo/wrf/namelist.input.2dom namelist.input
ln -sf $WPS_DIR/met_em.d0*.nc .
./real.exe >& log.real
# Check: wrfinput_d01, wrfinput_d02, wrfbdy_d01 created
```

### 6. WRF — Main Simulation
```bash
# Single node (adjust for your HPC scheduler)
mpirun -np 32 ./wrf.exe >& log.wrf &
tail -f rsl.out.0000   # monitor progress

# On HPC with SLURM:
sbatch wrf_submit.sh
```

### 7. Post-processing
```bash
# Extract 10m/100m wind from wrfout files
python wrf_postprocess.py   # see analysis/wrf_validation.py
```

---

## Validation Strategy

Compare d02 output against:
1. **MGM surface stations**: Çanakkale, Edremit, İzmir-Çiğli (10m wind speed, direction)
2. **EPİAŞ generation data**: Correlate modeled 100m wind with observed plant output
3. **ERA5 100m wind**: Bias/RMSE analysis at turbine hub heights

Key metrics: RMSE, Bias, Correlation (r), Index of Agreement (d)

---

## Expected Outputs

| File | Description |
|---|---|
| `figures/fig_wrf_domain_map.png` | Domain extent map (d01 + d02) |
| `figures/fig_wrf_wind_march2025.png` | Simulated 100m wind field during cutoff event |
| `figures/fig_wrf_validation_scatter.png` | Obs vs WRF at MGM stations |
| `data/wrf_d02_march2025_wind.csv` | Extracted hub-height wind at RES plant locations |

---

## Estimated Compute Requirements

| Resource | Estimate |
|---|---|
| Cores | 32–64 (MPI) |
| Wall time | ~4–8 hours for 4-day simulation |
| Memory | ~64 GB |
| Storage | ~20 GB wrfout files |

---

## Citation

This 2-domain configuration follows best practices for wind energy studies:
- Priya et al. (2021, Nat. Hazards): 9–3 km nesting reduces boundary errors
- Santoni et al. (2020, Wind Energy): One-way mesoscale–microscale for wind farms
- Siedersleben et al. (2020, Geosci. Model Dev.): WRF TKE at ≤5 km for offshore wind
