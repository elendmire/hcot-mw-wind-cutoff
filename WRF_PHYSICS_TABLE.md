# WRF Model Fizik Parametreleri

Bu tablo, WRF simülasyonlarında kullanılan fizik parametrelerini açıklamaktadır.

---

## Fizik Paketi (Physics Suite)

| Parametre | Değer | Açıklama |
|-----------|-------|----------|
| `physics_suite` | `'CONUS'` | Kıta ABD için optimize edilmiş fizik paketi. Varsayılan olarak Thompson mikrofizik, RRTMG radyasyon, MYJ sınır tabakası şemalarını içerir. |

---

## Mikrofizik (Microphysics)

| Parametre | Değer | Şema Adı | Açıklama |
|-----------|-------|----------|----------|
| `mp_physics` | 8 (CONUS default) | Thompson Scheme | Aerosol-duyarlı mikrofizik şeması. Bulut suyu, bulut buzu, yağmur, kar ve graupel için tahmin yapar. Rüzgar türbini uygulamaları için önerilir. |

---

## Kümülüs Parametrizasyonu (Cumulus)

| Parametre | Değer | Şema Adı | Açıklama |
|-----------|-------|----------|----------|
| `cu_physics` | 0 | Kapalı | Kümülüs konveksiyonu kapalı. 3 km çözünürlükte konveksiyon açıkça çözüldüğü için parametrizasyon gerekmez. |
| `cudt` | 5 | - | Kümülüs çağrı aralığı (dakika). cu_physics=0 olduğu için etkisiz. |

---

## Radyasyon Şemaları (Radiation)

| Parametre | Değer | Şema Adı | Açıklama |
|-----------|-------|----------|----------|
| `ra_lw_physics` | 4 (CONUS default) | RRTMG Longwave | Rapid Radiative Transfer Model for GCMs. Uzun dalga radyasyonu için en gelişmiş şema. Sera gazı konsantrasyonlarını içerir. |
| `ra_sw_physics` | 4 (CONUS default) | RRTMG Shortwave | Kısa dalga (güneş) radyasyonu için RRTMG şeması. Bulut-radyasyon etkileşimlerini doğru hesaplar. |
| `radt` | 15 | - | Radyasyon hesaplama aralığı (dakika). 3 km çözünürlük için 15 dakika uygundur (kural: ~1 dk/km). |

---

## Sınır Tabakası (Planetary Boundary Layer)

| Parametre | Değer | Şema Adı | Açıklama |
|-----------|-------|----------|----------|
| `bl_pbl_physics` | 1 | YSU (Yonsei University) | Asimetrik konvektif profil ve sayaç-gradyan akı ile non-lokal difüzyon şeması. Rüzgar enerjisi uygulamaları için yaygın kullanılır. Gün içi karışım derinliğini iyi temsil eder. |
| `bldt` | 0 | - | Sınır tabakası hesaplama aralığı. 0 = her zaman adımında çağrılır. |

---

## Yüzey Tabakası (Surface Layer)

| Parametre | Değer | Şema Adı | Açıklama |
|-----------|-------|----------|----------|
| `sf_sfclay_physics` | 1 | Revised MM5 Monin-Obukhov | Yüzey-atmosfer değişimi için Jimenez tarafından revize edilmiş MM5 şeması. Yüzey akıları, sürtünme hızı ve pürüzlülük uzunluğu hesaplar. |

---

## Arazi Yüzeyi (Land Surface)

| Parametre | Değer | Şema Adı | Açıklama |
|-----------|-------|----------|----------|
| `sf_surface_physics` | 1 | Thermal Diffusion | 5 katmanlı termal difüzyon şeması. Toprak sıcaklığını ve yüzey enerji dengesini hesaplar. Basit ama hesaplama açısından verimli. |
| `num_land_cat` | 21 | MODIS + Lake | MODIS arazi örtüsü kategorileri (göl dahil). 21 farklı arazi kullanım tipi. |

---

## Bulut ve Diğer Ayarlar

| Parametre | Değer | Açıklama |
|-----------|-------|----------|
| `icloud` | 1 | Bulut etkisi radyasyonda aktif. Xu-Randall bulut fraksiyonu yöntemi kullanılır. |
| `sf_urban_physics` | 0 | Kentsel kanopi modeli kapalı. |
| `fractional_seaice` | 0 | Kesirli deniz buzu kapalı. Deniz buzu bayrak olarak (var/yok) işlenir. |

---

## Domain Yapılandırması

| Parametre | Değer | Açıklama |
|-----------|-------|----------|
| `max_dom` | 1 | Tek domain (nested yok) |
| `dx` | 3000 m | Yatay çözünürlük (3 km) |
| `dy` | 3000 m | Yatay çözünürlük (3 km) |
| `e_vert` | 51 | Dikey seviye sayısı |
| `time_step` | 18 s | Zaman adımı (kural: ~6*dx km için uygun) |

---

## Özet: Şema Kombinasyonu

```
┌─────────────────────────────────────────────────────────────┐
│                    WRF FİZİK YAPISI                         │
├─────────────────────────────────────────────────────────────┤
│  Mikrofizik:        Thompson (mp=8)                         │
│  Uzun Dalga:        RRTMG (ra_lw=4)                         │
│  Kısa Dalga:        RRTMG (ra_sw=4)                         │
│  Sınır Tabakası:    YSU (bl_pbl=1)                          │
│  Yüzey Tabakası:    Revised MM5 M-O (sf_sfclay=1)           │
│  Arazi Yüzeyi:      Thermal Diffusion (sf_surface=1)        │
│  Kümülüs:           Kapalı (cu=0, dx=3km için uygun)        │
├─────────────────────────────────────────────────────────────┤
│  Çözünürlük: 3 km × 3 km × 51 seviye                        │
│  Radyasyon aralığı: 15 dakika                               │
└─────────────────────────────────────────────────────────────┘
```

---

## Poster İçin Kısa Tablo

| Kategori | Şema | Referans |
|----------|------|----------|
| Mikrofizik | Thompson | Thompson et al. (2008) |
| Uzun Dalga Radyasyon | RRTMG | Iacono et al. (2008) |
| Kısa Dalga Radyasyon | RRTMG | Iacono et al. (2008) |
| Sınır Tabakası | YSU | Hong et al. (2006) |
| Yüzey Tabakası | Revised MM5 M-O | Jiménez et al. (2012) |
| Arazi Yüzeyi | Thermal Diffusion | Dudhia (1996) |
| Kümülüs | Kapalı | - |

---

## Notlar

- **CONUS Suite**: Continental US için optimize edilmiş paket. `-1` değeri suite varsayılanını kullanır.
- **3 km Çözünürlük**: Bu ölçekte konveksiyon açıkça çözülebildiği için kümülüs parametrizasyonu kapatılmıştır.
- **YSU PBL**: Rüzgar enerjisi uygulamalarında yaygın tercih edilen şema. Konvektif sınır tabakasını iyi temsil eder.
- **51 Dikey Seviye**: Atmosferin iyi çözünmesi için yeterli. Alt seviyelerde yoğun, üst seviyelerde seyrek dağılım.
