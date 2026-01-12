# dontest
Black-White-Gray   Pentest Test/Analiz/Aksiyom
| Kategori  | Araç Seti (CLI)                                                  | Çıktı Formatı     |
| --------- | ---------------------------------------------------------------- | ----------------- |
| **White** | `nmap -sT -F`, `testssl.sh`, `dirsearch`, `nikto`                | JSON + CSV        |
| **Gray**  | `nmap -sV -sC`, `wpscan`, `zap-baseline.py`, `sslyze`            | JSON + XML        |
| **Black** | `nmap -A`, `metasploit` (auxiliary), `nuclei`, `jaeles`, `nikto` | JSON + XML + LOOT |
                 ┌-----------------┐
                 │  nginx (80/443) │  ← React / Bootstrap UI
                 └--------+--------┘
                          │
                 ┌--------▼--------┐
                 │  FastAPI        │  /scan  /report/<id>  /download/<id>
                 │  (docker.sock)  │  AI özetini de burada üretir
                 └--------+--------┘
                          │
          +---------------▼---------------+
          │   docker-compose.<kat>.yml    │
          │   - zap-baseline              │
          │   - nmap-json                 │
          │   - testssl.sh-json           │
          │   - dirsearch-json            │
          │   - nuclei-json               │
          +---------------+---------------+
                          │
                 ┌--------▼--------┐
                 │  shared vol.    │  ./data/<uuid>/  (raw)
                 │  ./reports/     │  ./reports/<uuid>/ (html+json)
                 └-----------------┘
