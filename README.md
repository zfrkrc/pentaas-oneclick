# Pentaas OneClick - Güvenlik Tarama ve Analiz Platformu

Pentaas OneClick, web uygulama ve ağ güvenliği testlerini otomatize eden, Docker tabanlı, modüler bir ZA (Zafiyet Analizi) ve Pentest (Sızma Testi) orkestrasyon platformudur.

## 1. Yazılım Gereksinim Spesifikasyonu (SRS)

### 1.1 Amaç ve Kapsam
Bu sistem, güvenlik profesyonellerinin ve sistem yöneticilerinin tek bir arayüz üzerinden farklı derinliklerde (White, Gray, Black Box) otomatik taramalar yapmasını sağlar. Araç çıktılarını normalize eder ve merkezi bir raporlama sunar.

### 1.2 Fonksiyonel Gereksinimler
- **F1: Çoklu Tarama Profilleri:** Sistem, White Box (Bilgi Toplama), Gray Box (Kimlik Doğrulama Odaklı) ve Black Box (Kapsamlı Saldırı) profillerini desteklemelidir.
- **F2: Gerçek Zamanlı Orkestrasyon:** Backend, Docker konteynerlarını dinamik olarak ayağa kaldırabilmeli ve süreçleri izleyebilmelidir.
- **F3: Normalizasyon ve Ayrıştırma:** Farklı araçların ürettiği (JSON, XML) çıktılar tek bir merkezi bulgu şemasına dönüştürülmelidir.
- **F4: Veri Sürekliliği:** Tarama raporları ve ham veriler, benzersiz UUID'ler altında disk üzerinde kalıcı olarak saklanmalıdır.
- **F5: Dinamik Log Yönetimi:** Tarama sırasında oluşan yoğun log trafiği minimize edilerek (Sessiz mod) sistem kaynakları optimize edilmelidir.

### 1.3 Sistem Gereksinimleri
- **İşletim Sistemi:** Linux (Ubuntu 20.04+ önerilir) veya Docker Desktop destekli Windows/macOS.
- **Teknoloji Yığını:** Docker, Docker Compose (v2.x), Python 3.11, React 18, Nginx.
- **Bağımlılıklar:** Host makinede `docker.sock` erişimi gereklidir.

---

## 2. Yazılım Tasarım Açıklaması (SDD)

### 2.1 Sistem Mimarisi
Sistem üç ana katmandan oluşur:

1.  **Sunum Katmanı (Frontend):** Vite + React tabanlı modern bir web arayüzü. Tarama başlatma, durum izleme ve sonuçları görselleştirme işlevlerini üstlenir.
2.  **Kontrol Katmanı (Backend):** FastAPI üzerine kurulu asenkron motor. Docker CLI ile `docker.sock` üzerinden haberleşerek tarama araçlarını konteyner olarak başlatır.
3.  **İşçi Katmanı (Tooling):** Her biri izole bir Docker konteyneri içinde çalışan sektör standardı güvenlik araçları (Nmap, Nuclei, Nikto, Dalfox vb.).

### 2.2 Veri Akış Modeli
1.  Kullanıcı IP/Domain girişi yapar ve profil seçer.
2.  API, talebi alır ve benzersiz bir `scan_id` üretir.
3.  Background Task başlatılır: `docker compose` komutu ilgili profile göre konteynerları ayağa kaldırır.
4.  Tüm araçlar çıktılarını `/reports/<scan_id>/data/` dizinine yazar.
5.  `merge` servisi tarama özetini oluşturur.
6.  Backend, oluşan JSON dosyalarını okuyarak normalize edilmiş sonuçları UI'a döner.

---

## 3. Tarama Profilleri ve Araç Seti

| Kategori | Strateji | Entegre Araçlar |
| :--- | :--- | :--- |
| **White Box** | Bilgi toplama ve hızlı yüzey taraması | Nmap, Nuclei, TestSSL, Dirsearch, Nikto, WhatWeb, Arjun, Dalfox |
| **Gray Box** | Uygulama mantığı ve yapılandırma analizi | Nmap, WPScan, ZAP Baseline, SSLyze |
| **Black Box** | Derinlemesine zafiyet tespiti ve exploit analizi | Nmap (Full), Nuclei (Full), Nikto |

### Araç Detayları
- **Dalfox:** Gelişmiş XSS tarama motoru.
- **Nuclei:** Şablon tabanlı zafiyet tarayıcı.
- **Arjun:** Gizli HTTP parametrelerini keşfeder.
- **ZAP Baseline:** Web uygulama temel güvenlik kontrollerini yapar.

---

## 4. Kurulum ve Dağıtım

Sistemi tek bir komutla ayağa kaldırabilirsiniz:

```bash
# Projeyi klonlayın
git clone <repository-url>
cd pentaas-oneclick

# Docker konteynerlarını build edin ve başlatın
docker compose up --build -d
```

### Önemli Yapılandırma
Sistemin çalışması için `/var/run/docker.sock` dosyasının backend konteynerine mount edilmiş olması gerekir (Varsayılan `docker-compose.yml` içinde bu ayar mevcuttur).

---

## 5. Kullanım (Usage)

1.  Arayüzü açın: `http://localhost` (veya sunucu IP adresiniz).
2.  **Target** kısmına hedef IP veya alan adını girin (Örn: `example.com`).
3.  **Profile** kısmından (White, Gray, Black) birini seçin.
4.  **Start Scan** butonuna basın.
5.  Tarama tamamlandığında **Reports** sekmesinden zafiyet detaylarını inceleyin ve ham veri dosyalarına erişin.

---

## 6. Proje Yapısı

```text
pentaas-oneclick/
├── backend/
│   ├── main.py          # API Endpoints & Parser Logic
│   ├── engine.py        # Docker Orchestration Engine
│   └── compose/         # Araç Dockerfile'ları ve Compose YAML'ları
├── frontend/
│   ├── src/             # UI Components (App, Report)
│   └── public/          # Statik varlıklar
└── nginx/
    └── nginx.conf       # Reverse Proxy ve Rapor Sunumu
```

---
*Bu doküman, sistemin teknik mimarisini ve gereksinimlerini tanımlayan canlı bir belgedir.*
