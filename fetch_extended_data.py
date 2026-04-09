#!/usr/bin/env python3
"""
Extended EPİAŞ Data Fetcher
============================
Fetches per-plant wind generation and PTF market prices for 2022-2025.

Usage:
    export EPIAS_USERNAME='your@email.com'
    export EPIAS_PASSWORD='yourpassword'

    # Fetch generation for a specific period
    python fetch_extended_data.py --mode generation --start 2022-01-01 --end 2025-04-30

    # Fetch PTF prices
    python fetch_extended_data.py --mode ptf --start 2022-01-01 --end 2025-04-30

    # Fetch both
    python fetch_extended_data.py --mode all --start 2022-01-01 --end 2025-04-30

Notes:
    - Fetches data month-by-month to avoid EPİAŞ API limits
    - Saves each month as a separate CSV, then merges into a master file
    - Rate limits: 0.5s between plant requests, 2s between months
"""

import argparse
import json
import logging
import os
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import pandas as pd
import requests

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

BASE_URL = "https://seffaflik.epias.com.tr/electricity-service"
AUTH_URL = "https://giris.epias.com.tr/cas/v1/tickets"
TGT_CACHE = Path(__file__).parent / ".tgt_cache.json"
DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)


class EPIASExtendedClient:
    """Full-featured EPİAŞ client for bulk data retrieval."""

    def __init__(self):
        self.username = os.environ.get("EPIAS_USERNAME")
        self.password = os.environ.get("EPIAS_PASSWORD")
        self._tgt: Optional[str] = None
        self._tgt_time: Optional[datetime] = None
        self._load_cache()

    def _load_cache(self):
        if TGT_CACHE.exists():
            try:
                cache = json.loads(TGT_CACHE.read_text())
                ts = datetime.fromisoformat(cache["timestamp"])
                if datetime.now() - ts < timedelta(hours=1.9):
                    self._tgt = cache["tgt"]
                    self._tgt_time = ts
                    logger.info("TGT loaded from cache.")
            except Exception:
                pass

    def _save_cache(self):
        if self._tgt and self._tgt_time:
            TGT_CACHE.write_text(
                json.dumps({"tgt": self._tgt, "timestamp": self._tgt_time.isoformat()})
            )

    def get_tgt(self) -> str:
        if self._tgt and self._tgt_time:
            if datetime.now() - self._tgt_time < timedelta(hours=1.9):
                return self._tgt
        if not self.username or not self.password:
            raise ValueError(
                "Set EPIAS_USERNAME and EPIAS_PASSWORD environment variables."
            )
        r = requests.post(
            AUTH_URL,
            headers={"Content-Type": "application/x-www-form-urlencoded", "Accept": "text/plain"},
            data={"username": self.username, "password": self.password},
            timeout=30,
        )
        if r.status_code == 201:
            self._tgt = r.text.strip()
            self._tgt_time = datetime.now()
            self._save_cache()
            logger.info("New TGT obtained.")
            return self._tgt
        raise Exception(f"TGT failed: {r.status_code} - {r.text[:200]}")

    def _headers(self):
        return {"TGT": self.get_tgt(), "Content-Type": "application/json"}

    def get_plant_list(self) -> pd.DataFrame:
        """Fetch licensed YEKDEM wind plant list."""
        url = f"{BASE_URL}/v1/renewables/data/licensed-powerplant-list"
        payload = {"period": datetime.now().strftime("%Y-%m-%dT00:00:00+03:00")}
        r = requests.post(url, headers=self._headers(), json=payload, timeout=30)
        if r.status_code == 200:
            data = r.json()
            items = data if isinstance(data, list) else data.get("items", data.get("body", []))
            df = pd.DataFrame(items)
            logger.info(f"Plant list: {len(df)} entries")
            return df
        raise Exception(f"Plant list failed: {r.status_code}")

    def get_plant_generation(
        self, plant_id: int, start: datetime, end: datetime
    ) -> pd.DataFrame:
        """Fetch hourly generation for a single plant."""
        url = f"{BASE_URL}/v1/renewables/data/licensed-realtime-generation"
        payload = {
            "startDate": start.strftime("%Y-%m-%dT00:00:00+03:00"),
            "endDate": end.strftime("%Y-%m-%dT23:59:59+03:00"),
            "powerPlantId": plant_id,
        }
        r = requests.post(url, headers=self._headers(), json=payload, timeout=30)
        if r.status_code == 200:
            data = r.json()
            items = data if isinstance(data, list) else data.get("items", data.get("body", []))
            return pd.DataFrame(items)
        logger.debug(f"Plant {plant_id}: {r.status_code}")
        return pd.DataFrame()

    def get_ptf_prices(self, start: datetime, end: datetime) -> pd.DataFrame:
        """
        Fetch PTF (Piyasa Takas Fiyatı) hourly market prices.
        Endpoint: /v1/markets/dam/data/mcp
        """
        url = f"{BASE_URL}/v1/markets/dam/data/mcp"
        payload = {
            "startDate": start.strftime("%Y-%m-%dT00:00:00+03:00"),
            "endDate": end.strftime("%Y-%m-%dT23:59:59+03:00"),
        }
        r = requests.post(url, headers=self._headers(), json=payload, timeout=30)
        if r.status_code == 200:
            data = r.json()
            items = data if isinstance(data, list) else data.get("items", data.get("body", []))
            return pd.DataFrame(items)
        raise Exception(f"PTF failed: {r.status_code} - {r.text[:200]}")


def iter_months(start: datetime, end: datetime):
    """Yield (month_start, month_end) pairs."""
    current = start.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    while current <= end:
        next_month = (current.replace(day=28) + timedelta(days=4)).replace(day=1)
        month_end = min(next_month - timedelta(seconds=1), end)
        yield current, month_end
        current = next_month


def fetch_generation(client: EPIASExtendedClient, start: datetime, end: datetime):
    """
    Fetch per-plant wind generation for [start, end] month-by-month.
    Saves to data/generation_YYYYMM.csv and merges to data/generation_2022_2025.csv
    """
    # Get wind plant list
    logger.info("Fetching wind plant list...")
    plants = client.get_plant_list()

    # Filter wind plants
    res_plants = pd.DataFrame()
    for col in ["fuelType", "fuelTypeName", "resourceType"]:
        if col in plants.columns:
            mask = plants[col].astype(str).str.contains("RÜZGAR|RES|WIND", case=False, na=False)
            if mask.sum() > 0:
                res_plants = plants[mask].copy()
                break
    if len(res_plants) == 0:
        for col in ["name", "powerPlantName", "organizationName"]:
            if col in plants.columns:
                mask = plants[col].astype(str).str.contains("RES|WIND|RÜZGAR", case=False, na=False)
                if mask.sum() > 0:
                    res_plants = plants[mask].copy()
                    break
    if len(res_plants) == 0:
        res_plants = plants.copy()

    id_col = next((c for c in ["id", "powerPlantId", "organizationId"] if c in res_plants.columns), None)
    name_col = next((c for c in ["name", "powerPlantName", "organizationName"] if c in res_plants.columns), None)

    logger.info(f"Wind plants to fetch: {len(res_plants)}")

    # Save plant list
    res_plants.to_csv(DATA_DIR / "res_plant_list.csv", index=False, encoding="utf-8-sig")

    all_monthly = []
    for month_start, month_end in iter_months(start, end):
        month_str = month_start.strftime("%Y%m")
        out_file = DATA_DIR / f"generation_{month_str}.csv"

        if out_file.exists():
            logger.info(f"Skipping {month_str} (already exists)")
            all_monthly.append(pd.read_csv(out_file, encoding="utf-8-sig"))
            continue

        logger.info(f"Fetching generation: {month_str}")
        month_rows = []

        for _, plant in res_plants.iterrows():
            pid = plant.get(id_col) if id_col else None
            pname = plant.get(name_col, f"Plant_{pid}") if name_col else f"Plant_{pid}"

            if pid is None:
                continue

            try:
                df = client.get_plant_generation(int(pid), month_start, month_end)
                if len(df) > 0:
                    df["plant_id"] = pid
                    df["plant_name"] = pname
                    month_rows.append(df)
            except Exception as e:
                logger.warning(f"Plant {pname}: {e}")

            time.sleep(0.5)

        if month_rows:
            month_df = pd.concat(month_rows, ignore_index=True)
            month_df.to_csv(out_file, index=False, encoding="utf-8-sig")
            logger.info(f"Saved {month_str}: {len(month_df)} rows")
            all_monthly.append(month_df)
        else:
            logger.warning(f"No data for {month_str}")

        time.sleep(2)

    if all_monthly:
        merged = pd.concat(all_monthly, ignore_index=True)
        out = DATA_DIR / f"generation_{start.strftime('%Y%m')}_{end.strftime('%Y%m')}.csv"
        merged.to_csv(out, index=False, encoding="utf-8-sig")
        logger.info(f"Merged generation saved: {out} ({len(merged)} rows)")
        return merged
    return pd.DataFrame()


def fetch_ptf(client: EPIASExtendedClient, start: datetime, end: datetime):
    """
    Fetch PTF (market clearing price) for [start, end] month-by-month.
    Saves to data/ptf_prices_YYYY_YYYY.csv
    """
    all_monthly = []
    for month_start, month_end in iter_months(start, end):
        month_str = month_start.strftime("%Y%m")
        out_file = DATA_DIR / f"ptf_{month_str}.csv"

        if out_file.exists():
            logger.info(f"PTF {month_str} already exists, skipping.")
            all_monthly.append(pd.read_csv(out_file, encoding="utf-8-sig"))
            continue

        logger.info(f"Fetching PTF: {month_str}")
        try:
            df = client.get_ptf_prices(month_start, month_end)
            if len(df) > 0:
                df.to_csv(out_file, index=False, encoding="utf-8-sig")
                logger.info(f"PTF {month_str}: {len(df)} rows")
                all_monthly.append(df)
        except Exception as e:
            logger.error(f"PTF {month_str}: {e}")
        time.sleep(1)

    if all_monthly:
        merged = pd.concat(all_monthly, ignore_index=True)
        out = DATA_DIR / f"ptf_prices_{start.strftime('%Y%m')}_{end.strftime('%Y%m')}.csv"
        merged.to_csv(out, index=False, encoding="utf-8-sig")
        logger.info(f"PTF merged: {out}")
        return merged
    return pd.DataFrame()


def main():
    parser = argparse.ArgumentParser(description="EPİAŞ Extended Data Fetcher")
    parser.add_argument("--mode", choices=["generation", "ptf", "all"], default="all")
    parser.add_argument("--start", default="2022-01-01", help="YYYY-MM-DD")
    parser.add_argument("--end", default="2025-04-30", help="YYYY-MM-DD")
    args = parser.parse_args()

    start = datetime.strptime(args.start, "%Y-%m-%d")
    end = datetime.strptime(args.end, "%Y-%m-%d")

    logger.info(f"Fetching {args.mode}: {start.date()} → {end.date()}")

    try:
        client = EPIASExtendedClient()
    except ValueError as e:
        logger.error(str(e))
        return

    if args.mode in ("generation", "all"):
        fetch_generation(client, start, end)

    if args.mode in ("ptf", "all"):
        fetch_ptf(client, start, end)


if __name__ == "__main__":
    main()
