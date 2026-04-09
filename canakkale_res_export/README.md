# Canakkale Region RES Export

This mini-project exports wind power plant (RES) generation for:

- Canakkale
- Balikesir
- Tekirdag

using EPİAS APIs and writes two CSV outputs for the last 6 calendar months.

## Requirements

- Python 3.9+
- `pandas`
- `requests`
- EPİAS credentials in environment variables:

```bash
export EPIAS_USERNAME="your_user"
export EPIAS_PASSWORD="your_password"
```

## Run

```bash
python canakkale_res_export/export_canakkale_region_res.py
```

Optional flags:

```bash
python canakkale_res_export/export_canakkale_region_res.py \
  --months 6 \
  --provinces "Canakkale,Balikesir,Tekirdag" \
  --output-dir canakkale_res_export/output \
  --map-file canakkale_res_export/plant_region_map.csv \
  --sleep-sec 0.5
```

## Outputs

Generated under `canakkale_res_export/output/`:

- `canakkale_region_res_hourly_last6m.csv`
  - Columns: `province,plant_id,plant_name,eic,datetime,hour,generation_mwh,source_endpoint,pulled_at`
- `canakkale_region_res_monthly_summary_last6m.csv`
  - Columns: `province,plant_id,plant_name,year_month,total_generation_mwh,mean_hourly_mwh,min_hourly_mwh,max_hourly_mwh,missing_hour_count`

## Province Matching Logic

1. Pull licensed plant list from `/v1/renewables/data/licensed-powerplant-list`.
2. Pull full powerplant list from `/v1/generation/data/powerplant-list`.
3. Match plants primarily by `eic`, then by normalized plant name.
4. Use `plant_region_map.csv` as fallback when province is missing.

## Fallback Mapping File

`plant_region_map.csv` columns:

- `plant_id`
- `plant_name`
- `province`

You can fill either `plant_id` or `plant_name` (or both) for matching.
