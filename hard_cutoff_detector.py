"""
Hard Cut-off Dedektörü
----------------------
Yüksek üretimden birden 0'a (veya çok düşüğe) düşen durumları tespit eder.

Cut-off Kriterleri:
- Önceki saat: YÜKSEK üretim (örn. >X MW)
- Şu anki saat: ~0 veya ÇOK DÜŞÜK (<Y MW)
- Bu = HARD CUT-OFF (türbin durmuş)

Bu yüzdelik değil, MUTLAK değer bazlı tespit!
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Optional
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class HardCutoffDetector:
    """Yüksek→0 düşen hard cut-off olaylarını tespit eder"""
    
    def __init__(self, data_dir: Optional[Path] = None):
        self.data_dir = data_dir or Path(__file__).parent / "data"
        self.df = None
    
    def load_data(self, file_pattern: str = "realtime_generation*.csv") -> pd.DataFrame:
        """CSV verilerini yükle"""
        files = list(self.data_dir.glob(file_pattern))
        
        if not files:
            raise FileNotFoundError(f"Veri bulunamadı: {file_pattern}")
        
        dfs = []
        for f in sorted(files):
            try:
                # EPİAŞ formatı: ; ile ayrılmış, Türkçe encoding
                df = pd.read_csv(f, sep=';', encoding='utf-8-sig')
                dfs.append(df)
            except Exception as e:
                logger.error(f"Dosya yüklenemedi {f}: {e}")
        
        self.df = pd.concat(dfs, ignore_index=True)
        logger.info(f"Yüklenen: {len(self.df)} satır, {len(files)} dosya")
        return self.df
    
    def preprocess(self, df: Optional[pd.DataFrame] = None) -> pd.DataFrame:
        """Veriyi hazırla"""
        if df is None:
            df = self.df
        
        df = df.copy()
        
        # Sütun isimlerini normalize et
        df.columns = df.columns.str.strip().str.lower()
        
        # Tarih-saat birleştir
        if 'tarih' in df.columns and 'saat' in df.columns:
            df['datetime'] = pd.to_datetime(
                df['tarih'] + ' ' + df['saat'], 
                format='%d.%m.%Y %H:%M',
                errors='coerce'
            )
        
        # Rüzgar sütununu bul ve düzelt
        wind_col = [c for c in df.columns if 'rüzgar' in c.lower()]
        if wind_col:
            self.wind_col = wind_col[0]
            # Türkçe sayı formatı: 1.234,56 → 1234.56
            df[self.wind_col] = (
                df[self.wind_col]
                .astype(str)
                .str.replace('.', '', regex=False)  # Binlik ayracı kaldır
                .str.replace(',', '.', regex=False)  # Ondalık virgülü noktaya çevir
                .astype(float)
            )
        
        df = df.sort_values('datetime').reset_index(drop=True)
        self.df = df
        return df
    
    def detect_hard_cutoffs(
        self,
        df: Optional[pd.DataFrame] = None,
        high_threshold_mw: float = 500,   # "Yüksek" üretim eşiği
        low_threshold_mw: float = 100,    # "Düşük" üretim eşiği (cut-off sonrası)
        zero_threshold_mw: float = 50     # "Sıfır" kabul edilecek eşik
    ) -> pd.DataFrame:
        """
        HARD cut-off tespit et.
        
        Kriter: Önceki saat >= high_threshold VE şu an <= low_threshold
        
        Args:
            high_threshold_mw: Önceki saatte en az bu kadar üretim olmalı
            low_threshold_mw: Şu an en fazla bu kadar üretim olmalı
            zero_threshold_mw: Bu değerin altı "sıfır" kabul edilir
        """
        if df is None:
            df = self.df
        
        if not hasattr(self, 'wind_col'):
            raise ValueError("Önce preprocess() çağır!")
        
        df = df.copy()
        prod_col = self.wind_col
        
        # Önceki ve sonraki saati hesapla
        df['prev_production'] = df[prod_col].shift(1)
        df['next_production'] = df[prod_col].shift(-1)
        df['production'] = df[prod_col]
        
        # HARD CUT-OFF KRİTERİ:
        # Önceki saat YÜKSEK (>=high) VE şu an DÜŞÜK (<=low)
        hard_cutoff_mask = (
            (df['prev_production'] >= high_threshold_mw) &
            (df['production'] <= low_threshold_mw)
        )
        
        cutoffs = df[hard_cutoff_mask].copy()
        
        if len(cutoffs) > 0:
            cutoffs['drop_mw'] = cutoffs['prev_production'] - cutoffs['production']
            cutoffs['is_zero'] = cutoffs['production'] <= zero_threshold_mw
            cutoffs['recovery_1h'] = df.loc[cutoffs.index, 'next_production'].values
            
            # 2-6 saat sonrası recovery
            for h in range(2, 7):
                cutoffs[f'recovery_{h}h'] = df[prod_col].shift(-h).loc[cutoffs.index].values
        
        logger.info(f"🔴 HARD cut-off tespit edildi: {len(cutoffs)}")
        if len(cutoffs) > 0:
            zero_count = cutoffs['is_zero'].sum()
            logger.info(f"   Bunların {zero_count}'i tamamen 0'a düşmüş")
        
        return cutoffs
    
    def generate_report(self, cutoffs: pd.DataFrame) -> str:
        """Hard cut-off raporu"""
        report = []
        report.append("=" * 65)
        report.append("🔴 HARD CUT-OFF RAPORU (Yüksek → 0 Düşüşler)")
        report.append("=" * 65)
        report.append(f"Analiz Tarihi: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        
        if len(cutoffs) == 0:
            report.append("\n✅ Hard cut-off tespit edilmedi!")
            report.append("   (Yüksek üretimden ani sıfıra düşüş yok)")
        else:
            report.append(f"\n{'─' * 50}")
            report.append(f"Toplam Hard Cut-off: {len(cutoffs)}")
            report.append(f"Tamamen 0'a düşen: {cutoffs['is_zero'].sum()}")
            report.append(f"\nOrtalama düşüş: {cutoffs['drop_mw'].mean():.1f} MW")
            report.append(f"Maksimum düşüş: {cutoffs['drop_mw'].max():.1f} MW")
            
            report.append(f"\n{'─' * 50}")
            report.append("EN BÜYÜK DÜŞÜŞLER:")
            report.append(f"{'─' * 50}")
            
            top = cutoffs.nlargest(10, 'drop_mw')
            for _, row in top.iterrows():
                dt = row['datetime'].strftime('%Y-%m-%d %H:%M') if pd.notna(row['datetime']) else 'N/A'
                prev = row['prev_production']
                curr = row['production']
                drop = row['drop_mw']
                zero = "🔴" if row['is_zero'] else "🟡"
                report.append(f"  {zero} {dt}: {prev:.0f} → {curr:.0f} MW (düşüş: {drop:.0f} MW)")
        
        report.append(f"\n{'=' * 65}")
        return "\n".join(report)
    
    def export_cutoffs(self, cutoffs: pd.DataFrame, filename: str = "hard_cutoffs.csv"):
        """Cut-off'ları CSV'ye kaydet"""
        output_path = self.data_dir / filename
        cutoffs.to_csv(output_path, index=False, encoding='utf-8-sig')
        logger.info(f"Kaydedildi: {output_path}")
        return output_path


def analyze_plant_cutoffs(plant_file: str = "plant_generation*.csv"):
    """
    Santral bazlı hard cut-off analizi.
    
    Her santral için ayrı ayrı yüksek→0 düşüşlerini tespit eder.
    """
    data_dir = Path(__file__).parent / "data"
    files = list(data_dir.glob(plant_file))
    
    if not files:
        print(f"❌ Santral verisi bulunamadı: {plant_file}")
        print("   Önce çek: python fetch_res_plants.py --start 2025-03-01 --end 2025-03-31")
        return None
    
    print("=" * 70)
    print("🌬️  SANTRAL BAZLI HARD CUT-OFF ANALİZİ")
    print("=" * 70)
    
    # Tüm dosyaları birleştir
    dfs = []
    for f in files:
        try:
            df = pd.read_csv(f, encoding='utf-8-sig')
            dfs.append(df)
            print(f"Yüklendi: {f.name} ({len(df)} satır)")
        except Exception as e:
            print(f"Hata {f.name}: {e}")
    
    if not dfs:
        return None
    
    df = pd.concat(dfs, ignore_index=True)
    df.columns = df.columns.str.strip().str.lower()
    
    print(f"\nToplam: {len(df)} satır")
    print(f"Sütunlar: {df.columns.tolist()}")
    
    # Santral ismi sütununu bul
    name_cols = ['powerplantname', 'santraladi', 'uevcbname', 'name', 'organizationname']
    name_col = None
    for col in name_cols:
        if col in df.columns:
            name_col = col
            break
    
    if not name_col:
        print("❌ Santral ismi sütunu bulunamadı!")
        return None
    
    # Üretim sütununu bul
    prod_cols = ['generation', 'uretim', 'toplam', 'quantity', 'value']
    prod_col = None
    for col in prod_cols:
        matching = [c for c in df.columns if col in c.lower()]
        if matching:
            prod_col = matching[0]
            break
    
    if not prod_col:
        print("❌ Üretim sütunu bulunamadı!")
        return None
    
    # Tarih sütununu bul ve parse et
    date_cols = ['date', 'tarih', 'datetime', 'hour']
    for col in date_cols:
        matching = [c for c in df.columns if col in c.lower()]
        if matching:
            df['datetime'] = pd.to_datetime(df[matching[0]], errors='coerce')
            break
    
    print(f"\nSantral sütunu: {name_col}")
    print(f"Üretim sütunu: {prod_col}")
    
    # Sayısala çevir
    df[prod_col] = pd.to_numeric(
        df[prod_col].astype(str).str.replace(',', '.').str.replace(' ', ''),
        errors='coerce'
    )
    
    # Sadece RES'leri filtrele (varsa)
    if 'fueltype' in df.columns or 'yakittipi' in df.columns:
        fuel_col = 'fueltype' if 'fueltype' in df.columns else 'yakittipi'
        df = df[df[fuel_col].str.contains('RÜZGAR|RES|WIND', case=False, na=False)]
        print(f"RES filtrelendi: {len(df)} satır")
    
    # Unique santraller
    plants = df[name_col].unique()
    print(f"\nToplam santral: {len(plants)}")
    
    # Her santral için analiz
    all_cutoffs = []
    
    print("\n" + "-" * 70)
    print("SANTRAL BAZLI ANALİZ")
    print("-" * 70)
    
    for plant_name in plants:
        plant_df = df[df[name_col] == plant_name].sort_values('datetime').copy()
        
        if len(plant_df) < 2:
            continue
        
        # Bu santralin max üretimi
        max_prod = plant_df[prod_col].max()
        
        if max_prod <= 0:
            continue
        
        # Önceki üretim
        plant_df['prev'] = plant_df[prod_col].shift(1)
        
        # Hard cut-off: Max üretimin %70'inden → %10'una düşüş
        high_th = max_prod * 0.7
        low_th = max_prod * 0.1
        
        cutoff_mask = (plant_df['prev'] >= high_th) & (plant_df[prod_col] <= low_th)
        cutoffs = plant_df[cutoff_mask].copy()
        
        if len(cutoffs) > 0:
            cutoffs['plant_name'] = plant_name
            cutoffs['max_capacity'] = max_prod
            cutoffs['drop_mw'] = cutoffs['prev'] - cutoffs[prod_col]
            cutoffs['production'] = cutoffs[prod_col]
            all_cutoffs.append(cutoffs)
            
            print(f"🔴 {plant_name}: {len(cutoffs)} hard cut-off (max: {max_prod:.0f} MW)")
    
    if all_cutoffs:
        result = pd.concat(all_cutoffs, ignore_index=True)
        
        print("\n" + "=" * 70)
        print(f"TOPLAM: {len(result)} hard cut-off olayı tespit edildi")
        print("=" * 70)
        
        # En büyük düşüşler
        print("\nEN BÜYÜK DÜŞÜŞLER:")
        top = result.nlargest(10, 'drop_mw')
        for _, row in top.iterrows():
            dt = row['datetime'].strftime('%Y-%m-%d %H:%M') if pd.notna(row['datetime']) else 'N/A'
            print(f"  🔴 {row['plant_name']}: {dt} - {row['prev']:.0f} → {row['production']:.0f} MW")
        
        # CSV kaydet
        output_path = data_dir / "plant_hard_cutoffs.csv"
        result.to_csv(output_path, index=False, encoding='utf-8-sig')
        print(f"\n✅ Kaydedildi: {output_path}")
        
        return result
    else:
        print("\n✅ Hard cut-off tespit edilmedi!")
        return pd.DataFrame()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--plant":
        # Santral bazlı analiz
        analyze_plant_cutoffs()
    else:
        # Aggregate analiz
        detector = HardCutoffDetector()
        
        try:
            df = detector.load_data()
            df = detector.preprocess()
            
            print("\n" + "=" * 60)
            print("AGGREGATE VERİ ANALİZİ (Tüm Türkiye RES toplamı)")
            print("=" * 60)
            
            cutoffs = detector.detect_hard_cutoffs(
                high_threshold_mw=800,
                low_threshold_mw=200
            )
            
            print(detector.generate_report(cutoffs))
            
            if len(cutoffs) > 0:
                detector.export_cutoffs(cutoffs)
            
            print("\n💡 Santral bazlı analiz için: python hard_cutoff_detector.py --plant")
                
        except FileNotFoundError as e:
            print(f"❌ {e}")

