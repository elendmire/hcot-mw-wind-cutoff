#!/usr/bin/env python3
"""
ERA5 Reanalysis Data Downloader
=================================
Downloads ERA5 surface and pressure-level variables for Turkey (2022-2025)
via the Copernicus Climate Data Store (CDS) API.

Variables downloaded:
  - 10m and 100m wind speed (u, v components) → for WRF validation & model features
  - Mean sea-level pressure (SLP) → for synoptic pattern classification
  - 2m temperature
  - 500 hPa geopotential height → for synoptic pattern classification

Area: Turkey and surroundings [25-45E, 34-44N]
Resolution: 0.25° × 0.25° (~28 km)

Usage:
    python era5_downloader.py --vars wind_100m --years 2022 2023 2024 2025
    python era5_downloader.py --vars synoptic --years 2022 2023 2024 2025
    python era5_downloader.py --vars all --years 2022 2023 2024 2025

Requires: ~/.cdsapirc with valid CDS API key
"""

import argparse
import logging
from pathlib import Path

import cdsapi

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

ERA5_DIR = Path(__file__).parent / "data" / "era5"
ERA5_DIR.mkdir(parents=True, exist_ok=True)

# Turkey bounding box with buffer [S, N, W, E]
AREA = [44, 25, 34, 45]  # CDS format: N/W/S/E

MONTHS_ALL = [f"{m:02d}" for m in range(1, 13)]
DAYS_ALL = [f"{d:02d}" for d in range(1, 32)]
HOURS_ALL = [f"{h:02d}:00" for h in range(24)]


def download_surface_wind(client: cdsapi.Client, year: int):
    """Download 10m and 100m wind speed (u/v components) for Turkey."""
    out = ERA5_DIR / f"era5_surface_wind_{year}.nc"
    if out.exists():
        logger.info(f"Skipping {out.name} (already exists)")
        return out

    logger.info(f"Downloading surface wind {year}...")
    client.retrieve(
        "reanalysis-era5-single-levels",
        {
            "product_type": "reanalysis",
            "variable": [
                "10m_u_component_of_wind",
                "10m_v_component_of_wind",
                "100m_u_component_of_wind",
                "100m_v_component_of_wind",
                "2m_temperature",
                "mean_sea_level_pressure",
                "total_precipitation",
            ],
            "year": str(year),
            "month": MONTHS_ALL,
            "day": DAYS_ALL,
            "time": HOURS_ALL,
            "area": AREA,
            "format": "netcdf",
        },
        str(out),
    )
    logger.info(f"Saved: {out}")
    return out


def download_pressure_levels(client: cdsapi.Client, year: int):
    """Download 500 hPa geopotential and 850 hPa temperature for synoptic analysis."""
    out = ERA5_DIR / f"era5_pressure_levels_{year}.nc"
    if out.exists():
        logger.info(f"Skipping {out.name} (already exists)")
        return out

    logger.info(f"Downloading pressure levels {year}...")
    client.retrieve(
        "reanalysis-era5-pressure-levels",
        {
            "product_type": "reanalysis",
            "variable": [
                "geopotential",
                "temperature",
                "u_component_of_wind",
                "v_component_of_wind",
            ],
            "pressure_level": ["500", "850"],
            "year": str(year),
            "month": MONTHS_ALL,
            "day": DAYS_ALL,
            "time": ["00:00", "06:00", "12:00", "18:00"],
            "area": AREA,
            "format": "netcdf",
        },
        str(out),
    )
    logger.info(f"Saved: {out}")
    return out


def download_storm_period(client: cdsapi.Client):
    """
    High-resolution download for the 15-18 March 2025 storm period.
    Needed for WRF validation and detailed synoptic analysis.
    """
    out = ERA5_DIR / "era5_storm_march2025.nc"
    if out.exists():
        logger.info(f"Skipping {out.name} (already exists)")
        return out

    logger.info("Downloading high-res storm period (15-18 March 2025)...")
    client.retrieve(
        "reanalysis-era5-single-levels",
        {
            "product_type": "reanalysis",
            "variable": [
                "10m_u_component_of_wind",
                "10m_v_component_of_wind",
                "100m_u_component_of_wind",
                "100m_v_component_of_wind",
                "2m_temperature",
                "mean_sea_level_pressure",
                "total_precipitation",
                "surface_pressure",
                "boundary_layer_height",
            ],
            "year": "2025",
            "month": "03",
            "day": ["14", "15", "16", "17", "18", "19"],
            "time": HOURS_ALL,
            "area": AREA,
            "format": "netcdf",
        },
        str(out),
    )
    logger.info(f"Saved: {out}")
    return out


def main():
    parser = argparse.ArgumentParser(description="ERA5 Downloader for Turkey Wind Study")
    parser.add_argument(
        "--vars",
        choices=["wind", "synoptic", "storm", "all"],
        default="all",
        help="Variables to download",
    )
    parser.add_argument(
        "--years",
        nargs="+",
        type=int,
        default=[2022, 2023, 2024, 2025],
        help="Years to download",
    )
    args = parser.parse_args()

    client = cdsapi.Client()

    if args.vars in ("wind", "all"):
        for yr in args.years:
            try:
                download_surface_wind(client, yr)
            except Exception as e:
                logger.error(f"Surface wind {yr}: {e}")

    if args.vars in ("synoptic", "all"):
        for yr in args.years:
            try:
                download_pressure_levels(client, yr)
            except Exception as e:
                logger.error(f"Pressure levels {yr}: {e}")

    if args.vars in ("storm", "all"):
        try:
            download_storm_period(client)
        except Exception as e:
            logger.error(f"Storm period: {e}")

    logger.info("ERA5 download complete.")


if __name__ == "__main__":
    main()
