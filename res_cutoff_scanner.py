#!/usr/bin/env python3
"""
RES Cut-off Tarayıcı
--------------------
Tüm RES santrallerini tarar ve hard cut-off olaylarını tespit eder.

EPİAŞ Endpoint:
- Santral listesi: /v1/renewables/data/licensed-powerplant-list
- Santral verisi: /v1/renewables/data/licensed-realtime-generation

Kullanım:
    export EPIAS_USERNAME='mail'
    export EPIAS_PASSWORD='sifre'
    python res_cutoff_scanner.py --start 2025-03-01 --end 2025-03-31
"""

import os
import json
import time
import requests
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, List
import argparse
import logging

logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)

TGT_CACHE = Path(__file__).parent / ".tgt_cache.json"


class EPIASClient:
    """EPİAŞ API Client"""
    
    BASE = "https://seffaflik.epias.com.tr/electricity-service"
    AUTH = "https://giris.epias.com.tr/cas/v1/tickets"
    
    def __init__(self):
        self.username = os.environ.get("EPIAS_USERNAME")
        self.password = os.environ.get("EPIAS_PASSWORD")
        self._tgt = None
        self._tgt_time = None
        self._load_cache()
    
    def _load_cache(self):
        if TGT_CACHE.exists():
            try:
                cache = json.load(open(TGT_CACHE))
                t = datetime.fromisoformat(cache['timestamp'])
                if datetime.now() - t < timedelta(hours=1.9):
                    self._tgt = cache['tgt']
                    self._tgt_time = t
            except:
                pass
    
    def _save_cache(self):
        json.dump({'tgt': self._tgt, 'timestamp': self._tgt_time.isoformat()}, 
                  open(TGT_CACHE, 'w'))
    
    def get_tgt(self) -> str:
        if self._tgt and self._tgt_time and datetime.now() - self._tgt_time < timedelta(hours=1.9):
            return self._tgt
        
        if not self.username or not self.password:
            raise ValueError("EPIAS_USERNAME ve EPIAS_PASSWORD ayarla!")
        
        r = requests.post(self.AUTH, 
            headers={"Content-Type": "application/x-www-form-urlencoded", "Accept": "text/plain"},
            data={"username": self.username, "password": self.password})
        
        if r.status_code == 201:
            self._tgt = r.text.strip()
            self._tgt_time = datetime.now()
            self._save_cache()
            return self._tgt
        raise Exception(f"TGT alınamadı: {r.status_code}")
    
    def _headers(self):
        return {"TGT": self.get_tgt(), "Content-Type": "application/json"}
    
    def get_licensed_powerplant_list(self) -> pd.DataFrame:
        """YEKDEM lisanslı santral listesi"""
        url = f"{self.BASE}/v1/renewables/data/licensed-powerplant-list"
        
        # API period parametresi datetime formatında istiyor
        today = datetime.now()
        payload = {
            "period": today.strftime("%Y-%m-%dT00:00:00+03:00")
        }
        
        r = requests.post(url, headers=self._headers(), json=payload)
        
        if r.status_code == 200:
            data = r.json()
            # API direkt liste veya items içinde döner
            if isinstance(data, list):
                items = data
            else:
                items = data.get('items', data.get('body', []))
            df = pd.DataFrame(items)
            logger.info(f"Santral listesi: {len(df)} kayıt")
            return df
        else:
            logger.error(f"Santral listesi hatası: {r.status_code}")
            logger.error(r.text[:500])
            return pd.DataFrame()
    
    def get_plant_realtime_generation(
        self,
        powerplant_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> pd.DataFrame:
        """
        Belirli bir santralin gerçek zamanlı üretim verisi.
        
        Endpoint: /v1/renewables/data/licensed-realtime-generation
        """
        url = f"{self.BASE}/v1/renewables/data/licensed-realtime-generation"
        
        payload = {
            "startDate": start_date.strftime("%Y-%m-%dT00:00:00+03:00"),
            "endDate": end_date.strftime("%Y-%m-%dT23:59:59+03:00"),
            "powerPlantId": powerplant_id
        }
        
        r = requests.post(url, headers=self._headers(), json=payload)
        
        if r.status_code == 200:
            data = r.json()
            if isinstance(data, list):
                items = data
            else:
                items = data.get('items', data.get('body', []))
            return pd.DataFrame(items)
        else:
            logger.debug(f"Veri alınamadı (plant {powerplant_id}): {r.status_code}")
            return pd.DataFrame()


class RESCutoffScanner:
    """RES santrallerini tarar ve cut-off tespit eder"""
    
    def __init__(self):
        self.client = EPIASClient()
        self.all_cutoffs = []
    
    def get_res_plants(self) -> pd.DataFrame:
        """Sadece RES santrallerini getir"""
        plants = self.client.get_licensed_powerplant_list()
        
        if len(plants) == 0:
            return plants
        
        # Sütun isimlerini kontrol et
        logger.info(f"Santral sütunları: {plants.columns.tolist()}")
        
        # Olası fuel type sütunları
        fuel_cols = ['fuelType', 'fuel_type', 'resourceType', 'resource_type', 
                     'yakitTipi', 'kaynakTipi', 'fuelTypeName']
        
        for col in fuel_cols:
            if col in plants.columns:
                # RES filtrele
                res = plants[plants[col].str.contains('RÜZGAR|RES|WIND|Rüzgar', case=False, na=False)]
                if len(res) > 0:
                    logger.info(f"RES santrali sayısı: {len(res)}")
                    return res
        
        # Filtre yapılamadıysa isimden dene
        name_cols = ['name', 'powerPlantName', 'santralAdi', 'organizationName']
        for col in name_cols:
            if col in plants.columns:
                res = plants[plants[col].str.contains('RES|RÜZGAR|WPP|WIND', case=False, na=False)]
                if len(res) > 0:
                    logger.info(f"RES santrali (isimden): {len(res)}")
                    return res
        
        logger.warning("RES filtresi yapılamadı, tüm santraller döndürülüyor")
        return plants
    
    def detect_hard_cutoff(
        self,
        df: pd.DataFrame,
        plant_name: str,
        high_ratio: float = 0.7,  # Max üretimin %70'i
        low_ratio: float = 0.1   # Max üretimin %10'u
    ) -> List[dict]:
        """
        Bir santral için hard cut-off tespit et.
        
        Kriter: Max üretimin %70'inden → %10'una (veya 0'a) ani düşüş
        """
        if len(df) < 2:
            return []
        
        # Üretim sütununu bul
        prod_cols = ['generation', 'toplam', 'total', 'quantity', 'value', 'uretim']
        prod_col = None
        for col in prod_cols:
            matching = [c for c in df.columns if col.lower() in c.lower()]
            if matching:
                prod_col = matching[0]
                break
        
        if not prod_col:
            # İlk sayısal sütunu dene
            for col in df.columns:
                if df[col].dtype in ['float64', 'int64']:
                    prod_col = col
                    break
        
        if not prod_col:
            return []
        
        # Tarih sütununu bul
        date_cols = ['date', 'tarih', 'datetime', 'hour', 'saat']
        for col in date_cols:
            matching = [c for c in df.columns if col.lower() in c.lower()]
            if matching:
                df['datetime'] = pd.to_datetime(df[matching[0]], errors='coerce')
                break
        
        df = df.sort_values('datetime').reset_index(drop=True)
        
        # Sayısala çevir
        df['production'] = pd.to_numeric(df[prod_col], errors='coerce')
        
        # Max üretim (kapasite tahmini)
        max_prod = df['production'].max()
        
        if max_prod <= 1:  # Çok düşük üretimli santraller
            return []
        
        # Eşikler
        high_th = max_prod * high_ratio
        low_th = max_prod * low_ratio
        
        # Önceki üretim
        df['prev'] = df['production'].shift(1)
        
        # Hard cut-off: yüksek → düşük
        cutoff_mask = (df['prev'] >= high_th) & (df['production'] <= low_th)
        cutoffs = df[cutoff_mask]
        
        results = []
        for _, row in cutoffs.iterrows():
            results.append({
                'plant_name': plant_name,
                'datetime': row['datetime'],
                'prev_production': row['prev'],
                'production': row['production'],
                'drop_mw': row['prev'] - row['production'],
                'drop_pct': (row['prev'] - row['production']) / row['prev'] * 100,
                'max_capacity': max_prod,
                'is_zero': row['production'] <= 1
            })
        
        return results
    
    def scan_all_res(
        self,
        start_date: datetime,
        end_date: datetime,
        max_plants: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Tüm RES santrallerini tara ve cut-off tespit et.
        """
        print("=" * 70, flush=True)
        print("🌬️  RES HARD CUT-OFF TARAMASI", flush=True)
        print("=" * 70, flush=True)
        print(f"Dönem: {start_date.date()} - {end_date.date()}", flush=True)
        
        # RES listesini al
        print("\n📋 RES listesi alınıyor...")
        res_plants = self.get_res_plants()
        
        if len(res_plants) == 0:
            print("❌ RES santrali bulunamadı!")
            return pd.DataFrame()
        
        # ID ve isim sütunlarını bul
        id_col = None
        name_col = None
        
        for col in ['id', 'powerPlantId', 'santralId', 'organizationId']:
            if col in res_plants.columns:
                id_col = col
                break
        
        for col in ['name', 'powerPlantName', 'santralAdi', 'organizationName']:
            if col in res_plants.columns:
                name_col = col
                break
        
        if not id_col:
            print("❌ Santral ID sütunu bulunamadı!")
            print(f"Mevcut sütunlar: {res_plants.columns.tolist()}")
            return pd.DataFrame()
        
        print(f"✅ {len(res_plants)} RES santrali bulundu")
        
        if max_plants:
            res_plants = res_plants.head(max_plants)
            print(f"   (İlk {max_plants} santral taranacak)")
        
        # Her RES için veri çek ve analiz et
        print("\n🔍 Santraller taranıyor...")
        print("-" * 70)
        
        all_cutoffs = []
        scanned = 0
        cutoff_count = 0
        
        for idx, plant in res_plants.iterrows():
            plant_id = plant[id_col]
            plant_name = plant[name_col] if name_col else f"Santral_{plant_id}"
            
            # Veri çek
            df = self.client.get_plant_realtime_generation(plant_id, start_date, end_date)
            scanned += 1
            
            if len(df) == 0:
                continue
            
            # Cut-off tespit et
            cutoffs = self.detect_hard_cutoff(df, plant_name)
            
            if cutoffs:
                cutoff_count += len(cutoffs)
                all_cutoffs.extend(cutoffs)
                print(f"🔴 {plant_name}: {len(cutoffs)} cut-off tespit edildi!")
                for c in cutoffs:
                    dt = c['datetime'].strftime('%Y-%m-%d %H:%M') if pd.notna(c['datetime']) else 'N/A'
                    print(f"   └─ {dt}: {c['prev_production']:.0f} → {c['production']:.0f} MW")
            
            # Progress
            if scanned % 10 == 0:
                print(f"   ... {scanned}/{len(res_plants)} santral tarandı")
            
            # Rate limiting
            time.sleep(0.5)
        
        print("-" * 70)
        print(f"\n📊 SONUÇ: {scanned} santral tarandı, {cutoff_count} cut-off tespit edildi")
        
        if all_cutoffs:
            result_df = pd.DataFrame(all_cutoffs)
            
            # CSV kaydet
            output_file = DATA_DIR / f"res_cutoffs_{start_date.strftime('%Y%m')}.csv"
            result_df.to_csv(output_file, index=False, encoding='utf-8-sig')
            print(f"✅ Kaydedildi: {output_file}")
            
            # Özet rapor
            print("\n" + "=" * 70)
            print("EN BÜYÜK CUT-OFF OLAYLARI")
            print("=" * 70)
            
            top = result_df.nlargest(10, 'drop_mw')
            for _, row in top.iterrows():
                dt = row['datetime'].strftime('%Y-%m-%d %H:%M') if pd.notna(row['datetime']) else 'N/A'
                zero = "→0" if row['is_zero'] else ""
                print(f"🔴 {row['plant_name']}")
                print(f"   {dt}: {row['prev_production']:.0f} → {row['production']:.0f} MW {zero}")
                print()
            
            return result_df
        
        return pd.DataFrame()


def main():
    parser = argparse.ArgumentParser(description="RES Cut-off Tarayıcı")
    parser.add_argument("--start", "-s", required=True, help="Başlangıç (YYYY-MM-DD)")
    parser.add_argument("--end", "-e", required=True, help="Bitiş (YYYY-MM-DD)")
    parser.add_argument("--max", "-m", type=int, help="Max santral sayısı (test için)")
    
    args = parser.parse_args()
    
    start = datetime.strptime(args.start, "%Y-%m-%d")
    end = datetime.strptime(args.end, "%Y-%m-%d")
    
    scanner = RESCutoffScanner()
    scanner.scan_all_res(start, end, max_plants=args.max)


if __name__ == "__main__":
    main()

