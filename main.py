#!/usr/bin/env python3
"""
EPİAŞ Rüzgar Cut-off Analiz Aracı
=================================

Bu script:
1. EPİAŞ Şeffaflık'tan gerçek zamanlı üretim verisi çeker
2. Open-Meteo'dan rüzgar hızı verisi çeker
3. GERÇEK cut-off olaylarını tespit eder (rüzgar ≥23 m/s + üretim düşüşü)
4. Analiz raporu ve görselleştirme oluşturur

Kullanım:
---------
# Sadece veri çek (3 aylık)
python main.py --fetch --months 3

# GERÇEK cut-off analizi (rüzgar hızı ile) - ÖNERİLEN!
python main.py --real-cutoff

# Eski analiz (sadece üretim düşüşüne bakarak)
python main.py --analyze

# Her ikisini de yap
python main.py --fetch --real-cutoff --months 5

# Özel tarih aralığı
python main.py --fetch --start 2025-09-01 --end 2025-12-01

Gereksinimler:
--------------
EPIAS_USERNAME ve EPIAS_PASSWORD environment variable'larını ayarla:

export EPIAS_USERNAME="kullanici@mail.com"
export EPIAS_PASSWORD='sifre123'  # Tek tırnak kullan (! için)
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

# Proje modüllerini import et
from epias_client import EpiasClient
from wind_cutoff_analyzer import (
    WindCutoffAnalyzer, 
    visualize_cutoffs, 
    visualize_real_cutoffs,
    SOFT_CUTOFF_SPEED,
    HARD_CUTOFF_SPEED
)


def parse_args():
    """Komut satırı argümanlarını parse et"""
    parser = argparse.ArgumentParser(
        description="EPİAŞ Rüzgar Cut-off Analiz Aracı",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        '--fetch', '-f',
        action='store_true',
        help="EPİAŞ'tan veri çek"
    )
    
    parser.add_argument(
        '--analyze', '-a',
        action='store_true',
        help="Mevcut veriyi analiz et"
    )
    
    parser.add_argument(
        '--months', '-m',
        type=int,
        default=3,
        help="Kaç aylık veri çekilsin (default: 3)"
    )
    
    parser.add_argument(
        '--start', '-s',
        type=str,
        help="Başlangıç tarihi (YYYY-MM-DD format)"
    )
    
    parser.add_argument(
        '--end', '-e',
        type=str,
        help="Bitiş tarihi (YYYY-MM-DD format)"
    )
    
    parser.add_argument(
        '--threshold', '-t',
        type=float,
        default=50.0,
        help="Cut-off tespit eşiği (yüzde düşüş, default: 50)"
    )
    
    parser.add_argument(
        '--output', '-o',
        type=str,
        default="cutoff_report.txt",
        help="Rapor çıktı dosyası"
    )
    
    parser.add_argument(
        '--no-plot',
        action='store_true',
        help="Grafik oluşturma"
    )
    
    parser.add_argument(
        '--real-cutoff', '-r',
        action='store_true',
        help="GERÇEK cut-off analizi yap (rüzgar hızı verisi ile - ÖNERİLEN!)"
    )
    
    parser.add_argument(
        '--wind-threshold', '-w',
        type=float,
        default=23.0,
        help="Rüzgar hızı cut-off eşiği (m/s, default: 23)"
    )
    
    return parser.parse_args()


def fetch_data(args) -> list[Path]:
    """EPİAŞ'tan veri çek"""
    print("\n" + "=" * 50)
    print("📡 EPİAŞ'TAN VERİ ÇEKİLİYOR")
    print("=" * 50)
    
    try:
        client = EpiasClient()
    except ValueError as e:
        print(f"\n❌ Hata: {e}")
        print("\nÇözüm: Environment variable'ları ayarla:")
        print("  export EPIAS_USERNAME='kullanici@mail.com'")
        print("  export EPIAS_PASSWORD='sifre123'")
        sys.exit(1)
    
    if args.start and args.end:
        # Özel tarih aralığı
        start = datetime.strptime(args.start, "%Y-%m-%d")
        end = datetime.strptime(args.end, "%Y-%m-%d")
        
        print(f"📅 Tarih aralığı: {start.date()} - {end.date()}")
        
        files = [client.export_licensed_realtime_generation(
            start_date=start,
            end_date=end,
            export_type="CSV"
        )]
    else:
        # Aylık veri çekimi
        print(f"📅 Son {args.months} ayın verisi çekiliyor...")
        files = client.fetch_multiple_months(months=args.months, export_type="CSV")
    
    print(f"\n✅ {len(files)} dosya indirildi:")
    for f in files:
        print(f"   📁 {f.name}")
    
    return files


def analyze_data(args) -> tuple:
    """Veriyi analiz et"""
    print("\n" + "=" * 50)
    print("🔍 CUT-OFF ANALİZİ YAPILIYOR")
    print("=" * 50)
    
    analyzer = WindCutoffAnalyzer()
    
    try:
        df = analyzer.load_multiple_files("*.csv")
    except FileNotFoundError:
        print("\n❌ Veri dosyası bulunamadı!")
        print("   Önce --fetch ile veri çekin.")
        sys.exit(1)
    
    print(f"\n📊 Yüklenen veri: {len(df)} satır")
    
    # Veriyi hazırla
    df = analyzer.preprocess_data()
    
    if analyzer.wind_col is None:
        print("\n⚠️  Rüzgar sütunu bulunamadı. Mevcut sütunlar:")
        for col in df.columns[:10]:
            print(f"   - {col}")
        print("   ...")
        
        # Manuel sütun seçimi
        wind_col = input("\nRüzgar sütunu adını girin: ").strip()
        if wind_col in df.columns:
            analyzer.wind_col = wind_col
        else:
            print("❌ Geçersiz sütun adı!")
            sys.exit(1)
    
    # Cut-off tespiti
    analyzer.DROP_THRESHOLD_PERCENT = args.threshold
    cutoffs = analyzer.detect_cutoffs()
    
    # Analiz
    analysis = analyzer.analyze_cutoff_patterns(cutoffs)
    
    # Rapor
    report = analyzer.generate_report(cutoffs, analysis, args.output)
    print("\n" + report)
    
    # CSV export
    if len(cutoffs) > 0:
        analyzer.export_cutoffs_to_csv(cutoffs)
    
    return df, cutoffs, analyzer


def analyze_real_cutoffs(args) -> tuple:
    """
    GERÇEK cut-off analizi yap (rüzgar hızı verisi ile).
    
    Bu doğru yöntem! Rüzgar ≥23 m/s olduğunda üretim düşüşü = cut-off
    """
    print("\n" + "=" * 60)
    print("🌬️  GERÇEK CUT-OFF ANALİZİ (Rüzgar Hızı ile)")
    print("=" * 60)
    print(f"   Cut-off eşiği: ≥{args.wind_threshold} m/s")
    print(f"   Hard cut-off: ≥{HARD_CUTOFF_SPEED} m/s")
    
    analyzer = WindCutoffAnalyzer()
    
    # Üretim verisini yükle
    try:
        df = analyzer.load_multiple_files("realtime_generation*.csv")
    except FileNotFoundError:
        print("\n❌ Üretim verisi bulunamadı!")
        print("   Önce --fetch ile veri çekin.")
        sys.exit(1)
    
    print(f"\n📊 Üretim verisi: {len(df)} satır")
    
    # Ön işleme
    df = analyzer.preprocess_data()
    
    if analyzer.wind_col is None:
        print("❌ Rüzgar üretim sütunu bulunamadı!")
        sys.exit(1)
    
    print(f"   Rüzgar üretim sütunu: {analyzer.wind_col}")
    
    # GERÇEK cut-off tespiti (rüzgar hızı ile)
    print("\n🌍 Open-Meteo'dan rüzgar hızı verisi çekiliyor...")
    print("   (Türkiye'nin ana rüzgar bölgeleri için)")
    
    try:
        cutoffs = analyzer.detect_real_cutoffs(
            wind_threshold=args.wind_threshold,
            production_drop_pct=20  # %20 düşüş yeterli (yüksek rüzgarda)
        )
    except Exception as e:
        print(f"\n❌ Rüzgar verisi çekilemedi: {e}")
        print("   İnternet bağlantınızı kontrol edin.")
        sys.exit(1)
    
    # Rapor
    report = analyzer.generate_real_cutoff_report(cutoffs, "real_cutoff_report.txt")
    print("\n" + report)
    
    # CSV export
    if len(cutoffs) > 0:
        analyzer.export_cutoffs_to_csv(cutoffs, "real_cutoffs.csv")
    
    return analyzer.df, cutoffs, analyzer


def main():
    """Ana fonksiyon"""
    args = parse_args()
    
    # En az bir işlem seçilmeli
    if not args.fetch and not args.analyze and not args.real_cutoff:
        print("⚠️  En az bir işlem seçin:")
        print("   --fetch        : EPİAŞ'tan veri çek")
        print("   --real-cutoff  : GERÇEK cut-off analizi (önerilen!)")
        print("   --analyze      : Basit üretim düşüşü analizi")
        print("\n   Yardım için: python main.py --help")
        sys.exit(1)
    
    # Veri çek
    if args.fetch:
        fetch_data(args)
    
    # GERÇEK cut-off analizi (rüzgar hızı ile)
    if args.real_cutoff:
        df, cutoffs, analyzer = analyze_real_cutoffs(args)
        
        # Görselleştirme
        if not args.no_plot:
            print("\n📈 Grafik oluşturuluyor...")
            try:
                visualize_real_cutoffs(df, cutoffs, analyzer.wind_col)
            except Exception as e:
                print(f"   ⚠️  Grafik oluşturulamadı: {e}")
    
    # Eski analiz (sadece üretim düşüşü)
    elif args.analyze:
        print("\n⚠️  NOT: Bu analiz sadece üretim düşüşüne bakıyor.")
        print("   Gerçek cut-off tespiti için --real-cutoff kullanın!\n")
        
        df, cutoffs, analyzer = analyze_data(args)
        
        # Görselleştirme
        if not args.no_plot and len(cutoffs) > 0:
            print("\n📈 Grafik oluşturuluyor...")
            try:
                visualize_cutoffs(df, cutoffs, analyzer.wind_col)
            except Exception as e:
                print(f"   ⚠️  Grafik oluşturulamadı: {e}")
    
    print("\n✨ İşlem tamamlandı!")


if __name__ == "__main__":
    main()


