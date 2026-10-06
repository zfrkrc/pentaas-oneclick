# Yeni Microservice Mimarisi - Kullanım Kılavuzu

## 🎯 Mimari Özeti

```
Frontend (Session Token: scan_id)
    ↓
Backend Orchestrator
    ↓ (Paralel HTTP İstekleri)
    ├─→ White Box: 18 servis
    ├─→ Gray Box: 4 servis
    └─→ Black Box: 3 servis
         (Toplam 25 benzersiz araç servisi)
```

## ✨ Özellikler

### 1. **Tam Asenkron Çalışma**
- ✅ Backend, seçilen profile göre tüm servislere **aynı anda** HTTP POST isteği atar
- ✅ Her servis bağımsız çalışır
- ✅ Bir servisin bitmesini beklemeden diğerleri devam eder

### 2. **Real-Time Status Tracking**
- ✅ Frontend her 2 saniyede bir status sorar
- ✅ Backend tüm servislere **paralel** status isteği atar
- ✅ Her servisin durumu (running/completed) ayrı ayrı gösterilir

### 3. **Session-Based Scan Management**
- ✅ Her scan için unique `scan_id` (session token)
- ✅ Frontend bu token ile status ve results sorar
- ✅ Backend token ile hangi servislerin çalıştığını takip eder

## 📡 API Akışı

### 1. **Scan Başlatma**

**Request:**
```http
POST /api/scan
Content-Type: application/json

{
  "ip": "example.com",
  "category": "white"
}
```

**Response:**
```json
{
  "status": "started",
  "scan_id": "abc123def456",
  "job_id": "rq-job-id"
}
```

**Backend İşlemi:**
```python
# 1. Scan ID oluştur
scan_id = "abc123def456"

# 2. TÜM servislere PARALEL istek at
await asyncio.gather(
    trigger_service("nmap", target, scan_id),
    trigger_service("nuclei", target, scan_id),
    trigger_service("nikto", target, scan_id),
    # ... diğer servisler
)

# 3. Her servis kendi scan_id'sini döner
# Backend bunları saklar
```

### 2. **Status Sorgulama** (Her 2 saniyede)

**Request:**
```http
GET /api/scan/abc123def456
```

**Response:**
```json
{
  "status": "running",
  "scan_id": "abc123def456",
  "services": {
    "nmap": {
      "status": "completed",
      "completed": true
    },
    "nuclei": {
      "status": "running",
      "completed": false
    },
    "nikto": {
      "status": "running",
      "completed": false
    },
    "dirsearch": {
      "status": "completed",
      "completed": true
    }
  }
}
```

**Backend İşlemi:**
```python
# TÜM servislere PARALEL status isteği
results = await asyncio.gather(
    check_status("nmap-service:8000", nmap_scan_id),
    check_status("nuclei-service:8000", nuclei_scan_id),
    check_status("nikto-service:8000", nikto_scan_id),
    # ... diğer servisler
)

# Tüm sonuçları birleştir ve döndür
```

### 3. **Results Alma**

**Request:**
```http
GET /api/scan/abc123def456/results
```

**Response:**
```json
{
  "findings": [
    {
      "id": "nmap-1",
      "title": "Open Port: 80 (http)",
      "severity": "Low",
      "description": "..."
    },
    {
      "id": "nuclei-1",
      "title": "SSL Certificate Issue",
      "severity": "Medium",
      "description": "..."
    }
  ],
  "progress": {
    "completed": ["nmap", "dirsearch", "whatweb"],
    "pending": ["nuclei", "nikto"]
  }
}
```

## 🔍 Log Takibi

### 1. **API ile:**
```bash
curl http://your-server/api/scan/abc123def456/logs
```

### 2. **Sunucuda:**
```bash
tail -f ./reports/abc123def456/data/scan.log
```

### 3. **Log Formatı:**
```
[2026-01-17 00:10:23] 🎯 Starting WHITE scan for example.com
[2026-01-17 00:10:23] 📦 Services: nmap, nuclei, nikto, dirsearch, ...
[2026-01-17 00:10:24] 🚀 Triggering nmap...
[2026-01-17 00:10:24] 🚀 Triggering nuclei...
[2026-01-17 00:10:24] 🚀 Triggering nikto...
[2026-01-17 00:10:25] ✅ nmap started (service_scan_id: xyz789)
[2026-01-17 00:10:25] ✅ nuclei started (service_scan_id: abc456)
[2026-01-17 00:10:30] ✅ All services triggered (18/18 started - white profile)
```

## 🚀 Deployment

### 1. **Backend Rebuild:**
```bash
cd /path/to/pentaas-oneclick
docker compose build backend worker
docker compose up -d backend worker
```

### 2. **Frontend Rebuild:**
```bash
docker compose build frontend
docker compose up -d frontend
```

### 3. **Servisler Zaten Çalışıyor:**
Microservice'ler (`nmap-service`, `nuclei-service`, vb.) zaten `docker-compose.yml` ile ayakta.

## ✅ Avantajlar

1. **Gerçek Paralel Çalışma**: Tüm servisler aynı anda başlar
2. **Bağımsız Servisler**: Bir servis fail olsa diğerleri etkilenmez
3. **Real-Time Progress**: Frontend her servisin durumunu ayrı ayrı gösterir
4. **Scalable**: Yeni servis eklemek çok kolay
5. **Session-Based**: Her scan izole, birbirini etkilemez

## 🎯 Test

```bash
# 1. Scan başlat
curl -X POST http://localhost/api/scan \
  -H "Content-Type: application/json" \
  -d '{"ip": "example.com", "category": "white"}'

# Response: {"scan_id": "abc123", ...}

# 2. Status kontrol et (2 saniyede bir)
curl http://localhost/api/scan/abc123

# 3. Logs kontrol et
curl http://localhost/api/scan/abc123/logs

# 4. Results al
curl http://localhost/api/scan/abc123/results
```

## 🔧 Troubleshooting

### Servisler başlamıyor:
```bash
# Servislerin health check'ini kontrol et
curl http://nmap-service:8000/health
curl http://nuclei-service:8000/health
```

### Backend logları:
```bash
docker logs -f pentaas-oneclick-backend-1
docker logs -f pentaas-oneclick-worker-1
```

### Servis logları:
```bash
docker logs -f pentaas-oneclick-nmap-service-1
docker logs -f pentaas-oneclick-nuclei-service-1
```
