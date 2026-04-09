"""
EPİAŞ Şeffaflık API Client
--------------------------
TGT alma ve veri export işlemleri için client modülü.

Referanslar:
- https://seffaflik.epias.com.tr/electricity-service/technical/tr/index.html
- https://www.epias.com.tr/tum-duyurular/seffaflik-platformu-web-servisleri-ticket-tgt-alma-servisinde-degisiklik/
"""

import os
import time
import json
import requests
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# TGT cache dosyası
TGT_CACHE_FILE = Path(__file__).parent / ".tgt_cache.json"
TGT_VALIDITY_HOURS = 2  # TGT 2 saat geçerli


class EpiasClient:
    """EPİAŞ Şeffaflık Platform API Client"""
    
    BASE_URL = "https://seffaflik.epias.com.tr/electricity-service"
    AUTH_URL = "https://giris.epias.com.tr/cas/v1/tickets"
    
    def __init__(self, username: Optional[str] = None, password: Optional[str] = None):
        """
        EPİAŞ client'ı başlat.
        
        Args:
            username: EPİAŞ kullanıcı adı (veya EPIAS_USERNAME env var)
            password: EPİAŞ şifre (veya EPIAS_PASSWORD env var)
        """
        self.username = username or os.environ.get("EPIAS_USERNAME")
        self.password = password or os.environ.get("EPIAS_PASSWORD")
        
        if not self.username or not self.password:
            raise ValueError(
                "EPİAŞ credentials gerekli! Ya parametre olarak ver ya da "
                "EPIAS_USERNAME ve EPIAS_PASSWORD environment variable'larını ayarla."
            )
        
        self._tgt: Optional[str] = None
        self._tgt_timestamp: Optional[datetime] = None
        self._load_cached_tgt()
    
    def _load_cached_tgt(self):
        """Cache'den TGT yükle (varsa ve geçerliyse)"""
        if TGT_CACHE_FILE.exists():
            try:
                with open(TGT_CACHE_FILE, 'r') as f:
                    cache = json.load(f)
                
                cached_time = datetime.fromisoformat(cache['timestamp'])
                if datetime.now() - cached_time < timedelta(hours=TGT_VALIDITY_HOURS - 0.1):
                    self._tgt = cache['tgt']
                    self._tgt_timestamp = cached_time
                    logger.info(f"Cache'den TGT yüklendi (geçerlilik: {TGT_VALIDITY_HOURS - (datetime.now() - cached_time).total_seconds()/3600:.1f} saat)")
            except (json.JSONDecodeError, KeyError):
                pass
    
    def _save_tgt_cache(self):
        """TGT'yi cache'e kaydet"""
        with open(TGT_CACHE_FILE, 'w') as f:
            json.dump({
                'tgt': self._tgt,
                'timestamp': self._tgt_timestamp.isoformat()
            }, f)
    
    def get_tgt(self, force_refresh: bool = False) -> str:
        """
        TGT (Ticket Granting Ticket) al.
        
        2025 güncellemesiyle username/password body içinde gönderilmeli!
        
        Args:
            force_refresh: True ise cache'i yoksay, yeni TGT al
            
        Returns:
            TGT string (TGT-xxx formatında)
        """
        # Cache'deki TGT hala geçerliyse onu kullan
        if not force_refresh and self._tgt and self._tgt_timestamp:
            if datetime.now() - self._tgt_timestamp < timedelta(hours=TGT_VALIDITY_HOURS - 0.1):
                return self._tgt
        
        logger.info("Yeni TGT alınıyor...")
        
        response = requests.post(
            self.AUTH_URL,
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "text/plain"
            },
            data={
                "username": self.username,
                "password": self.password
            }
        )
        
        if response.status_code == 201:
            self._tgt = response.text.strip()
            self._tgt_timestamp = datetime.now()
            self._save_tgt_cache()
            logger.info(f"TGT alındı: {self._tgt[:20]}...")
            return self._tgt
        else:
            raise Exception(f"TGT alınamadı! Status: {response.status_code}, Response: {response.text}")
    
    def export_licensed_realtime_generation(
        self,
        start_date: datetime,
        end_date: datetime,
        export_type: str = "CSV",
        output_file: Optional[str] = None
    ) -> Path:
        """
        Lisanslı YEKDEM santralleri gerçek zamanlı üretim verisini export et.
        
        Endpoint: /v1/renewables/export/licensed-realtime-generation
        
        Args:
            start_date: Başlangıç tarihi
            end_date: Bitiş tarihi  
            export_type: "CSV", "XLSX" veya "PDF"
            output_file: Çıktı dosya adı (opsiyonel)
            
        Returns:
            Kaydedilen dosyanın Path'i
        """
        tgt = self.get_tgt()
        
        url = f"{self.BASE_URL}/v1/renewables/export/licensed-realtime-generation"
        
        # ISO-8601 format with timezone (+03:00 Turkey)
        payload = {
            "startDate": start_date.strftime("%Y-%m-%dT%H:%M:%S+03:00"),
            "endDate": end_date.strftime("%Y-%m-%dT%H:%M:%S+03:00"),
            "exportType": export_type
        }
        
        logger.info(f"Export isteniyor: {start_date.date()} - {end_date.date()}")
        
        response = requests.post(
            url,
            headers={
                "Content-Type": "application/json",
                "TGT": tgt
            },
            json=payload
        )
        
        if response.status_code == 200:
            # Dosya adını belirle
            if output_file is None:
                ext = export_type.lower()
                output_file = f"realtime_generation_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.{ext}"
            
            output_path = Path(__file__).parent / "data" / output_file
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"Veri kaydedildi: {output_path}")
            return output_path
        else:
            raise Exception(f"Export başarısız! Status: {response.status_code}, Response: {response.text}")
    
    def fetch_multiple_months(
        self,
        months: int = 3,
        end_date: Optional[datetime] = None,
        export_type: str = "CSV"
    ) -> list[Path]:
        """
        Birden fazla ay için veri çek (aylık parçalara bölerek).
        
        EPİAŞ API'si büyük tarih aralıklarını kabul etmeyebilir,
        bu yüzden aylık parçalara bölüyoruz.
        
        Args:
            months: Kaç ay geriye git
            end_date: Bitiş tarihi (default: bugün)
            export_type: Export formatı
            
        Returns:
            Kaydedilen dosyaların listesi
        """
        if end_date is None:
            end_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        files = []
        current_end = end_date
        
        for i in range(months):
            # Ay başını hesapla
            current_start = (current_end.replace(day=1) - timedelta(days=1)).replace(day=1)
            if i == 0:
                current_start = current_end.replace(day=1)
            
            month_end = current_end
            month_start = current_start
            
            try:
                file_path = self.export_licensed_realtime_generation(
                    start_date=month_start,
                    end_date=month_end,
                    export_type=export_type
                )
                files.append(file_path)
                
                # Rate limiting - EPİAŞ'ı yormamak için
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"Ay {month_start.strftime('%Y-%m')} için hata: {e}")
            
            # Bir önceki aya geç
            current_end = current_start - timedelta(days=1)
        
        return files


if __name__ == "__main__":
    # Test
    client = EpiasClient()
    
    # Son 3 ayın verisini çek
    files = client.fetch_multiple_months(months=3)
    print(f"\nToplam {len(files)} dosya indirildi:")
    for f in files:
        print(f"  - {f}")


