#!/usr/bin/env python3
"""
Export RES generation for Canakkale region (Canakkale, Balikesir, Tekirdag).

Outputs:
1) Hourly detailed CSV for the last N months
2) Monthly summary CSV (plant-level)
"""

import argparse
import json
import logging
import os
import time
import unicodedata
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

import pandas as pd
import requests


BASE_URL = "https://seffaflik.epias.com.tr/electricity-service"
AUTH_URL = "https://giris.epias.com.tr/cas/v1/tickets"
TGT_CACHE_FILE = Path(__file__).parent / ".tgt_cache.json"

DEFAULT_PROVINCES = ["Canakkale", "Balikesir", "Tekirdag"]
SOURCE_ENDPOINT = "/v1/renewables/data/licensed-realtime-generation"


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@dataclass
class MonthWindow:
    year_month: str
    start: datetime
    end: datetime
    expected_hours: int


class EpiasAuth:
    """CAS TGT auth helper with short-lived cache."""

    def __init__(self, username: Optional[str] = None, password: Optional[str] = None):
        self.username = username or os.environ.get("EPIAS_USERNAME")
        self.password = password or os.environ.get("EPIAS_PASSWORD")
        self._tgt: Optional[str] = None
        self._tgt_time: Optional[datetime] = None
        self._load_cache()

    def _load_cache(self) -> None:
        if not TGT_CACHE_FILE.exists():
            return
        try:
            cache = json.loads(TGT_CACHE_FILE.read_text(encoding="utf-8"))
            ts = datetime.fromisoformat(cache["timestamp"])
            if datetime.now() - ts < timedelta(hours=1.9):
                self._tgt = cache["tgt"]
                self._tgt_time = ts
        except Exception:
            pass

    def _save_cache(self) -> None:
        if self._tgt and self._tgt_time:
            payload = {"tgt": self._tgt, "timestamp": self._tgt_time.isoformat()}
            TGT_CACHE_FILE.write_text(json.dumps(payload), encoding="utf-8")

    def get_tgt(self) -> str:
        if self._tgt and self._tgt_time:
            if datetime.now() - self._tgt_time < timedelta(hours=1.9):
                return self._tgt

        if not self.username or not self.password:
            raise ValueError("Set EPIAS_USERNAME and EPIAS_PASSWORD environment variables.")

        resp = requests.post(
            AUTH_URL,
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "text/plain",
            },
            data={"username": self.username, "password": self.password},
            timeout=30,
        )
        if resp.status_code != 201:
            raise RuntimeError(f"Could not get TGT: {resp.status_code} - {resp.text[:200]}")

        self._tgt = resp.text.strip()
        self._tgt_time = datetime.now()
        self._save_cache()
        return self._tgt


class CanakkaleRegionExporter:
    def __init__(
        self,
        provinces: List[str],
        months: int,
        output_dir: Path,
        map_file: Path,
        sleep_sec: float = 0.5,
    ):
        self.auth = EpiasAuth()
        self.session = requests.Session()
        self.provinces = {self._normalize_text(x) for x in provinces}
        self.months = months
        self.output_dir = output_dir
        self.map_file = map_file
        self.sleep_sec = sleep_sec

    @staticmethod
    def _normalize_text(value: object) -> str:
        text = str(value or "").strip().lower()
        text = unicodedata.normalize("NFKD", text)
        text = "".join(c for c in text if not unicodedata.combining(c))
        return text

    @staticmethod
    def _find_column(df: pd.DataFrame, candidates: Iterable[str], contains: Iterable[str] = ()) -> Optional[str]:
        if df.empty:
            return None

        normalized = {c.lower().replace(" ", ""): c for c in df.columns}
        for cand in candidates:
            key = cand.lower().replace(" ", "")
            if key in normalized:
                return normalized[key]

        for col in df.columns:
            key = col.lower().replace(" ", "")
            if any(x.lower().replace(" ", "") in key for x in contains):
                return col
        return None

    def _headers(self) -> Dict[str, str]:
        return {"TGT": self.auth.get_tgt(), "Content-Type": "application/json"}

    @staticmethod
    def _to_iso_start(dt: datetime) -> str:
        return dt.strftime("%Y-%m-%dT00:00:00+03:00")

    @staticmethod
    def _to_iso_end(dt: datetime) -> str:
        return dt.strftime("%Y-%m-%dT23:59:59+03:00")

    def _post_json(self, endpoint: str, payload: Dict) -> Dict:
        url = f"{BASE_URL}{endpoint}"
        resp = self.session.post(url, headers=self._headers(), json=payload, timeout=60)
        if resp.status_code != 200:
            raise RuntimeError(f"{endpoint} failed: {resp.status_code} - {resp.text[:250]}")
        data = resp.json()
        if isinstance(data, list):
            return {"items": data}
        return data

    def get_licensed_powerplant_list(self) -> pd.DataFrame:
        payload = {"period": datetime.now().strftime("%Y-%m-%dT00:00:00+03:00")}
        data = self._post_json("/v1/renewables/data/licensed-powerplant-list", payload)
        items = data.get("items", data.get("body", []))
        return pd.DataFrame(items)

    def get_powerplant_list(self) -> pd.DataFrame:
        data = self._post_json("/v1/generation/data/powerplant-list", {})
        items = data.get("items", data.get("body", []))
        return pd.DataFrame(items)

    def get_plant_realtime_generation(self, plant_id: int, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        payload = {
            "startDate": self._to_iso_start(start_date),
            "endDate": self._to_iso_end(end_date),
            "powerPlantId": int(plant_id),
        }
        data = self._post_json(SOURCE_ENDPOINT, payload)
        items = data.get("items", data.get("body", []))
        return pd.DataFrame(items)

    def _load_manual_region_map(self) -> pd.DataFrame:
        if not self.map_file.exists():
            return pd.DataFrame(columns=["plant_id", "plant_name", "province"])
        df = pd.read_csv(self.map_file, dtype=str).fillna("")
        if "province" not in df.columns:
            raise ValueError(f"Mapping file is missing required column: province ({self.map_file})")
        if "plant_id" not in df.columns:
            df["plant_id"] = ""
        if "plant_name" not in df.columns:
            df["plant_name"] = ""
        return df[["plant_id", "plant_name", "province"]]

    def build_region_plants(self) -> pd.DataFrame:
        licensed = self.get_licensed_powerplant_list()
        if licensed.empty:
            raise RuntimeError("licensed-powerplant-list returned no plants.")

        licensed_id_col = self._find_column(licensed, ["powerPlantId", "id"], contains=["powerplantid"])
        licensed_name_col = self._find_column(
            licensed,
            ["name", "powerPlantName", "organizationName", "shortName"],
            contains=["name", "organization"],
        )
        licensed_eic_col = self._find_column(licensed, ["eic"], contains=["eic"])

        if not licensed_id_col or not licensed_name_col:
            raise RuntimeError(f"Could not detect plant id/name columns in licensed list: {licensed.columns.tolist()}")

        licensed_df = pd.DataFrame(
            {
                "plant_id": pd.to_numeric(licensed[licensed_id_col], errors="coerce"),
                "plant_name": licensed[licensed_name_col].astype(str),
                "eic": licensed[licensed_eic_col].astype(str) if licensed_eic_col else "",
            }
        ).dropna(subset=["plant_id"])

        licensed_df["plant_id"] = licensed_df["plant_id"].astype(int)
        licensed_df["name_norm"] = licensed_df["plant_name"].map(self._normalize_text)
        licensed_df["eic_norm"] = licensed_df["eic"].map(self._normalize_text)

        try:
            powerplants = self.get_powerplant_list()
        except Exception as exc:
            logger.warning("powerplant-list endpoint unavailable (%s). Falling back to manual map.", exc)
            powerplants = pd.DataFrame()

        if powerplants.empty:
            logger.warning("powerplant-list returned empty data; manual region map will be used.")
            merged = licensed_df.copy()
            merged["province"] = ""
        else:
            pp_name_col = self._find_column(
                powerplants,
                ["name", "powerPlantName", "organizationName", "shortName", "santralAdi"],
                contains=["name", "organization", "santral"],
            )
            pp_eic_col = self._find_column(powerplants, ["eic"], contains=["eic"])
            pp_province_col = self._find_column(
                powerplants,
                ["province", "city", "il", "ilAdi", "provinceName", "cityName"],
                contains=["province", "city", " il", "iladi"],
            )
            if not pp_name_col:
                raise RuntimeError(f"Could not detect name column in powerplant-list: {powerplants.columns.tolist()}")

            pp_df = pd.DataFrame(
                {
                    "pp_name": powerplants[pp_name_col].astype(str),
                    "pp_eic": powerplants[pp_eic_col].astype(str) if pp_eic_col else "",
                    "province": powerplants[pp_province_col].astype(str) if pp_province_col else "",
                }
            )
            pp_df["name_norm"] = pp_df["pp_name"].map(self._normalize_text)
            pp_df["eic_norm"] = pp_df["pp_eic"].map(self._normalize_text)

            # Prefer exact EIC join, then fallback name join.
            merged = licensed_df.merge(
                pp_df[["eic_norm", "province"]].drop_duplicates("eic_norm"),
                how="left",
                on="eic_norm",
            )
            missing_province = merged["province"].isna() | (merged["province"].astype(str).str.strip() == "")
            if missing_province.any():
                fallback = licensed_df[missing_province].merge(
                    pp_df[["name_norm", "province"]].drop_duplicates("name_norm"),
                    how="left",
                    on="name_norm",
                )
                merged.loc[missing_province, "province"] = fallback["province"].values

        manual_map = self._load_manual_region_map()
        if not manual_map.empty:
            manual_map["plant_id"] = pd.to_numeric(manual_map["plant_id"], errors="coerce")
            manual_map["name_norm"] = manual_map["plant_name"].map(self._normalize_text)
            manual_map["province_norm"] = manual_map["province"].map(self._normalize_text)

            # Fill missing province by plant_id.
            missing = merged["province"].fillna("").str.strip() == ""
            if missing.any():
                by_id = manual_map.dropna(subset=["plant_id"]).copy()
                by_id["plant_id"] = by_id["plant_id"].astype(int)
                merged = merged.merge(
                    by_id[["plant_id", "province"]].rename(columns={"province": "province_manual_id"}),
                    on="plant_id",
                    how="left",
                )
                merged.loc[missing, "province"] = merged.loc[missing, "province_manual_id"]
                merged = merged.drop(columns=["province_manual_id"], errors="ignore")

            # Fill remaining missing province by normalized name.
            missing = merged["province"].fillna("").str.strip() == ""
            if missing.any():
                by_name = manual_map[manual_map["name_norm"] != ""][["name_norm", "province"]].drop_duplicates("name_norm")
                merged = merged.merge(
                    by_name.rename(columns={"province": "province_manual_name"}),
                    on="name_norm",
                    how="left",
                )
                merged.loc[missing, "province"] = merged.loc[missing, "province_manual_name"]
                merged = merged.drop(columns=["province_manual_name"], errors="ignore")

        merged["province_norm"] = merged["province"].map(self._normalize_text)
        region_plants = merged[merged["province_norm"].isin(self.provinces)].copy()
        region_plants = region_plants[["plant_id", "plant_name", "eic", "province"]].drop_duplicates("plant_id")
        region_plants = region_plants.sort_values(["province", "plant_name"]).reset_index(drop=True)

        if region_plants.empty:
            raise RuntimeError(
                "No plants found for target provinces. "
                "Check powerplant-list province fields or fill plant_region_map.csv."
            )
        return region_plants

    @staticmethod
    def _month_windows(months: int) -> List[MonthWindow]:
        if months < 1:
            raise ValueError("months must be >= 1")

        now = datetime.now()
        current_start = datetime(now.year, now.month, 1)
        start_month = current_start
        for _ in range(months - 1):
            if start_month.month == 1:
                start_month = datetime(start_month.year - 1, 12, 1)
            else:
                start_month = datetime(start_month.year, start_month.month - 1, 1)

        windows: List[MonthWindow] = []
        cursor = start_month
        while cursor <= current_start:
            if cursor.month == 12:
                next_month = datetime(cursor.year + 1, 1, 1)
            else:
                next_month = datetime(cursor.year, cursor.month + 1, 1)
            month_end = next_month - timedelta(days=1)
            if cursor.year == now.year and cursor.month == now.month:
                # Avoid partial-day or future-hour validation issues on EPİAS side.
                month_end = now - timedelta(days=1)

            start_hour = datetime(cursor.year, cursor.month, cursor.day, 0, 0, 0)
            end_hour = datetime(month_end.year, month_end.month, month_end.day, 23, 0, 0)
            expected_hours = int((end_hour - start_hour).total_seconds() / 3600) + 1
            windows.append(
                MonthWindow(
                    year_month=f"{cursor.year:04d}-{cursor.month:02d}",
                    start=cursor,
                    end=month_end,
                    expected_hours=expected_hours,
                )
            )
            cursor = next_month
        return windows

    @staticmethod
    def _extract_datetime(df: pd.DataFrame) -> pd.Series:
        date_col = CanakkaleRegionExporter._find_column(
            df,
            ["date", "datetime", "tarih", "tarihSaat", "time"],
            contains=["date", "datetime", "tarih", "time"],
        )
        if not date_col:
            raise RuntimeError(f"No datetime-like column found in generation data: {df.columns.tolist()}")
        return pd.to_datetime(df[date_col], errors="coerce")

    @staticmethod
    def _extract_generation(df: pd.DataFrame) -> pd.Series:
        gen_col = CanakkaleRegionExporter._find_column(
            df,
            ["generation", "total", "toplam", "value", "quantity", "production", "uretim"],
            contains=["generation", "total", "toplam", "value", "quantity", "production", "uretim"],
        )
        if gen_col:
            return pd.to_numeric(df[gen_col], errors="coerce")

        # Fallback: first numeric-looking column (excluding id-like columns).
        for col in df.columns:
            if "id" in str(col).lower():
                continue
            numeric = pd.to_numeric(df[col], errors="coerce")
            if numeric.notna().sum() > 0:
                return numeric
        raise RuntimeError(f"No generation-like column found in generation data: {df.columns.tolist()}")

    def fetch_hourly(self, plants: pd.DataFrame, month_windows: List[MonthWindow]) -> pd.DataFrame:
        rows: List[pd.DataFrame] = []
        total_calls = len(plants) * len(month_windows)
        call_no = 0

        for _, plant in plants.iterrows():
            plant_id = int(plant["plant_id"])
            plant_name = str(plant["plant_name"])
            province = str(plant["province"])
            eic = str(plant["eic"])

            logger.info("Fetching %s (%s) ...", plant_name, province)
            for window in month_windows:
                call_no += 1
                logger.info(
                    "[%s/%s] %s | %s",
                    call_no,
                    total_calls,
                    plant_name,
                    window.year_month,
                )
                try:
                    df = self.get_plant_realtime_generation(plant_id, window.start, window.end)
                except Exception as exc:
                    logger.warning(
                        "Generation fetch failed for plant=%s month=%s (%s). Skipping month.",
                        plant_id,
                        window.year_month,
                        exc,
                    )
                    time.sleep(self.sleep_sec)
                    continue
                if df.empty:
                    time.sleep(self.sleep_sec)
                    continue

                dt = self._extract_datetime(df)
                gen = self._extract_generation(df)
                out = pd.DataFrame(
                    {
                        "province": province,
                        "plant_id": plant_id,
                        "plant_name": plant_name,
                        "eic": eic,
                        "datetime": dt,
                        "generation_mwh": gen,
                    }
                )
                out = out.dropna(subset=["datetime"]).copy()
                out["hour"] = out["datetime"].dt.strftime("%H:%M")
                out["year_month"] = out["datetime"].dt.strftime("%Y-%m")
                rows.append(out)
                time.sleep(self.sleep_sec)

        if not rows:
            return pd.DataFrame(
                columns=[
                    "province",
                    "plant_id",
                    "plant_name",
                    "eic",
                    "datetime",
                    "hour",
                    "generation_mwh",
                    "year_month",
                ]
            )
        return pd.concat(rows, ignore_index=True)

    @staticmethod
    def validate_hourly(df: pd.DataFrame) -> Dict[str, int]:
        duplicated = int(df.duplicated(subset=["plant_id", "datetime"]).sum())
        if duplicated > 0:
            logger.warning("Found %s duplicate plant_id+datetime rows; keeping first.", duplicated)
            df.drop_duplicates(subset=["plant_id", "datetime"], keep="first", inplace=True)

        missing_generation = int(df["generation_mwh"].isna().sum())
        logger.info("Hourly rows: %s | Missing generation: %s", len(df), missing_generation)

        if not df.empty:
            logger.info("Datetime range: %s -> %s", df["datetime"].min(), df["datetime"].max())

        return {"duplicates_removed": duplicated, "missing_generation_rows": missing_generation}

    @staticmethod
    def build_monthly_summary(hourly_df: pd.DataFrame, windows: List[MonthWindow]) -> pd.DataFrame:
        expected_map = {w.year_month: w.expected_hours for w in windows}
        grouped = (
            hourly_df.groupby(["province", "plant_id", "plant_name", "year_month"], as_index=False)
            .agg(
                total_generation_mwh=("generation_mwh", "sum"),
                mean_hourly_mwh=("generation_mwh", "mean"),
                min_hourly_mwh=("generation_mwh", "min"),
                max_hourly_mwh=("generation_mwh", "max"),
                observed_hour_count=("generation_mwh", lambda s: int(s.notna().sum())),
            )
            .sort_values(["province", "plant_name", "year_month"])
        )
        grouped["expected_hour_count"] = grouped["year_month"].map(expected_map).fillna(0).astype(int)
        grouped["missing_hour_count"] = grouped["expected_hour_count"] - grouped["observed_hour_count"]
        return grouped

    @staticmethod
    def validate_consistency(hourly_df: pd.DataFrame, monthly_df: pd.DataFrame) -> float:
        hourly_totals = (
            hourly_df.groupby(["province", "plant_id", "plant_name", "year_month"], as_index=False)["generation_mwh"]
            .sum()
            .rename(columns={"generation_mwh": "hourly_total"})
        )
        compare = hourly_totals.merge(
            monthly_df[["province", "plant_id", "plant_name", "year_month", "total_generation_mwh"]],
            on=["province", "plant_id", "plant_name", "year_month"],
            how="left",
        )
        compare["delta"] = (compare["hourly_total"] - compare["total_generation_mwh"]).abs()
        max_delta = float(compare["delta"].max()) if not compare.empty else 0.0
        logger.info("Hourly vs monthly consistency max delta: %.8f", max_delta)
        return max_delta

    def run(self) -> Tuple[Path, Path]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        windows = self._month_windows(self.months)
        plants = self.build_region_plants()

        logger.info("Plants in target provinces: %s", len(plants))
        for province, cnt in plants.groupby("province")["plant_id"].count().sort_index().items():
            logger.info(" - %s: %s plant(s)", province, cnt)

        hourly_df = self.fetch_hourly(plants, windows)
        if hourly_df.empty:
            raise RuntimeError("No hourly generation rows were returned from API.")

        pulled_at = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        hourly_df["source_endpoint"] = SOURCE_ENDPOINT
        hourly_df["pulled_at"] = pulled_at
        stats = self.validate_hourly(hourly_df)

        hourly_df = hourly_df.sort_values(["province", "plant_name", "datetime"]).reset_index(drop=True)
        hourly_csv = self.output_dir / "canakkale_region_res_hourly_last6m.csv"
        hourly_df[
            [
                "province",
                "plant_id",
                "plant_name",
                "eic",
                "datetime",
                "hour",
                "generation_mwh",
                "source_endpoint",
                "pulled_at",
            ]
        ].to_csv(hourly_csv, index=False, encoding="utf-8-sig")

        monthly_df = self.build_monthly_summary(hourly_df, windows)
        max_delta = self.validate_consistency(hourly_df, monthly_df)
        monthly_csv = self.output_dir / "canakkale_region_res_monthly_summary_last6m.csv"
        monthly_df[
            [
                "province",
                "plant_id",
                "plant_name",
                "year_month",
                "total_generation_mwh",
                "mean_hourly_mwh",
                "min_hourly_mwh",
                "max_hourly_mwh",
                "missing_hour_count",
            ]
        ].to_csv(monthly_csv, index=False, encoding="utf-8-sig")

        logger.info("Saved hourly CSV: %s", hourly_csv)
        logger.info("Saved monthly CSV: %s", monthly_csv)
        logger.info("Validation stats: %s", stats)
        logger.info("Consistency max delta: %.8f", max_delta)
        return hourly_csv, monthly_csv


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Export last N months RES generation for Canakkale region provinces."
    )
    parser.add_argument(
        "--provinces",
        default=",".join(DEFAULT_PROVINCES),
        help="Comma-separated province list (default: Canakkale,Balikesir,Tekirdag).",
    )
    parser.add_argument(
        "--months",
        type=int,
        default=6,
        help="How many calendar months to include (default: 6).",
    )
    parser.add_argument(
        "--output-dir",
        default=str(Path(__file__).parent / "output"),
        help="Output directory for CSV files.",
    )
    parser.add_argument(
        "--map-file",
        default=str(Path(__file__).parent / "plant_region_map.csv"),
        help="Manual plant->province fallback CSV path.",
    )
    parser.add_argument(
        "--sleep-sec",
        type=float,
        default=0.5,
        help="Delay between API calls to avoid throttling (default: 0.5).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    provinces = [p.strip() for p in args.provinces.split(",") if p.strip()]
    exporter = CanakkaleRegionExporter(
        provinces=provinces,
        months=args.months,
        output_dir=Path(args.output_dir),
        map_file=Path(args.map_file),
        sleep_sec=args.sleep_sec,
    )
    exporter.run()


if __name__ == "__main__":
    main()
