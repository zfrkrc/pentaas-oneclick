"""
Scan Engine - HTTP Microservice orchestration
Calls tool microservices via HTTP API, stores results in Redis.
"""
import os
import uuid
import json
import asyncio
import time
import smtplib
import ssl
import httpx
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import logging
from redis import Redis

logger = logging.getLogger(__name__)

# Redis Connection
REDIS_URL = os.getenv("REDIS_URL")
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
if REDIS_URL:
    redis_client = Redis.from_url(REDIS_URL, decode_responses=True)
else:
    redis_client = Redis(host=REDIS_HOST, port=6379, db=0, decode_responses=True)

# ── Microservice port mapping ───────────────────────────────────────────────
SERVICE_PORTS = {
    "nmap":      8001,
    "nuclei":    8002,
    "testssl":   8003,
    "dirsearch": 8004,
    "nikto":     8005,
    "whatweb":   8006,
    "arjun":     8007,
    "dalfox":    8008,
    "wafw00f":   8009,
    "dnsrecon":  8010,
    "wpscan":    8011,
    "zap":       8012,
    "sslyze":    8013,
}

# Services per scan category
PROFILE_SERVICES = {
    "white": ["nmap", "testssl", "dirsearch", "nikto", "whatweb",
              "arjun", "dalfox", "wafw00f", "dnsrecon", "nuclei"],
    "gray":  ["nmap", "wpscan", "zap", "sslyze"],
    "black": ["nmap", "nikto", "nuclei"],
}

# Slow services get longer poll timeout
SLOW_SERVICES = {"nikto", "testssl", "nuclei", "dalfox", "zap", "wpscan"}
SERVICE_TIMEOUT = 600   # max seconds to wait per service
POLL_INTERVAL   = 3     # seconds between status polls


def log_scan(uid: str, message: str):
    """Log scan progress to Redis + stdout"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}"
    try:
        redis_client.rpush(f"scan:{uid}:logs", log_entry)
        redis_client.expire(f"scan:{uid}:logs", 3600)
    except Exception as e:
        print(f"Redis Log Error: {e}")
    print(f"[{uid}] {message}")


def _svc_url(service: str) -> str:
    """Build base URL for a tool microservice (docker compose network)"""
    # Docker Compose services are reachable by their service name
    svc_name = f"{service}-service"
    return f"http://{svc_name}:8000"


import socket
import re

def is_ip(target: str) -> bool:
    """Check if target is an IPv4 or IPv6 address"""
    try:
        socket.inet_aton(target)
        return True
    except socket.error:
        return ":" in target # Basic IPv6 check

def resolve_target(target: str) -> dict:
    """Analyze target and resolve DNS if needed"""
    info = {
        "original": target,
        "ip": None,
        "fqdn": None,
        "url": None,
        "type": "unknown"
    }
    
    # Detect protocol if present
    protocol_match = re.match(r'^(https?://)', target)
    protocol = protocol_match.group(1) if protocol_match else "http://"
    
    # Remove http/https and paths for analysis
    clean_target = re.sub(r'^https?://', '', target).split('/')[0]
    
    if is_ip(clean_target):
        info["ip"] = clean_target
        info["type"] = "ip"
        # Try reverse DNS
        try:
            info["fqdn"] = socket.gethostbyaddr(clean_target)[0]
        except:
            info["fqdn"] = clean_target
    else:
        info["fqdn"] = clean_target
        info["type"] = "fqdn"
        # Resolve to IP
        try:
            info["ip"] = socket.gethostbyname(clean_target)
        except:
            pass
            
    # Prepare URL with preserved or default protocol
    info["url"] = f"{protocol}{info['fqdn']}"
    return info

async def call_service(service: str, target_info: dict, uid: str, category: str) -> tuple:
    """Call a tool microservice with the appropriate target format"""
    url = _svc_url(service)
    timeout = SERVICE_TIMEOUT if service in SLOW_SERVICES else 300
    start_time = time.time()

    # Determine what to send to this specific service
    # Network layer tools prefer IP
    if service in ["nmap"]:
        svc_target = target_info["ip"] or target_info["fqdn"]
    # DNS and SSL tools prefer FQDN/Host
    elif service in ["dnsrecon", "testssl", "sslyze"]:
        svc_target = target_info["fqdn"]
    # Web tools prefer URL
    elif service in ["nuclei", "dirsearch", "nikto", "whatweb", "arjun", "dalfox", "wafw00f", "wpscan", "zap"]:
        svc_target = target_info["url"]
    else:
        svc_target = target_info["original"]

    log_scan(uid, f"🚀 Starting {service} on {svc_target}...")

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            # 1. Trigger scan
            options = {"category": category}
            resp = await client.post(f"{url}/scan", json={
                "target": svc_target,
                "options": options,
            })
            if resp.status_code != 200:
                log_scan(uid, f"❌ {service} - trigger failed: HTTP {resp.status_code}")
                return (service, False, f"HTTP {resp.status_code}")

            data = resp.json()
            svc_scan_id = data.get("scan_id")
            log_scan(uid, f"📡 {service} scan started (id: {svc_scan_id})")

            # 2. Poll status
            elapsed = 0
            while elapsed < timeout:
                await asyncio.sleep(POLL_INTERVAL)
                elapsed = time.time() - start_time

                try:
                    status_resp = await client.get(f"{url}/status/{svc_scan_id}")
                    if status_resp.status_code != 200:
                        continue
                    status_data = status_resp.json()
                    status = status_data.get("status", "")

                    if status == "completed":
                        duration = time.time() - start_time
                        log_scan(uid, f"✅ {service} completed in {duration:.1f}s")
                        # Fetch results
                        await _fetch_and_store_results(client, url, svc_scan_id, service, uid)
                        return (service, True, None)
                    elif status == "failed":
                        msg = status_data.get("message", "unknown error")
                        duration = time.time() - start_time
                        log_scan(uid, f"❌ {service} failed after {duration:.1f}s: {msg}")
                        return (service, False, msg)
                except Exception:
                    pass  # transient network error, retry

            # Timeout
            duration = time.time() - start_time
            log_scan(uid, f"⏱️ {service} timed out after {duration:.1f}s")
            try:
                await _fetch_and_store_results(client, url, svc_scan_id, service, uid)
            except Exception:
                pass
            return (service, True, "Timeout (partial results)")

    except Exception as e:
        duration = time.time() - start_time
        log_scan(uid, f"💥 {service} crashed after {duration:.1f}s: {e}")
        return (service, False, str(e))


async def _fetch_and_store_results(client, url, svc_scan_id, service, uid):
    """Fetch results from microservice and store in Redis"""
    try:
        res = await client.get(f"{url}/results/{svc_scan_id}")
        if res.status_code == 200:
            content = res.text
            redis_client.set(f"scan:{uid}:result:{service}", content)
            redis_client.expire(f"scan:{uid}:result:{service}", 3600)
            log_scan(uid, f"💾 {service} results saved ({len(content)} bytes)")
    except Exception as e:
        log_scan(uid, f"⚠️ Failed to save {service} results: {e}")


async def run_all_services(services: list, target_info: dict, uid: str, category: str):
    """Run all tool services in parallel via HTTP"""
    # Separate nuclei (run last)
    nuclei_svcs = [s for s in services if "nuclei" in s]
    other_svcs  = [s for s in services if "nuclei" not in s]

    results = []

    # 1. Run non-nuclei in parallel
    if other_svcs:
        log_scan(uid, f"📋 Running {len(other_svcs)} services in parallel...")
        tasks = [call_service(svc, target_info, uid, category) for svc in other_svcs]
        results.extend(await asyncio.gather(*tasks, return_exceptions=True))

    # 2. Run nuclei last
    if nuclei_svcs:
        log_scan(uid, f"📋 Running Nuclei ({len(nuclei_svcs)}) — last step...")
        tasks = [call_service(svc, target_info, uid, category) for svc in nuclei_svcs]
        results.extend(await asyncio.gather(*tasks, return_exceptions=True))

    successful = sum(1 for r in results if isinstance(r, tuple) and r[1])
    failed = len(results) - successful
    log_scan(uid, f"📊 Summary: {successful} succeeded, {failed} failed")

    redis_client.set(f"scan:{uid}:status", "completed")
    redis_client.expire(f"scan:{uid}:status", 3600)
    return results


import base64
import subprocess
import signal

class VpnManager:
    """Manages OpenVPN connection for a specific scan"""
    def __init__(self, uid: str, config_base64: str, log_fn):
        self.uid = uid
        self.log = log_fn
        try:
            self.config_content = base64.b64decode(config_base64).decode('utf-8')
        except:
            self.config_content = None
        self.config_path = f"/tmp/vpn_{uid}.ovpn"
        self.process = None

    async def start(self) -> bool:
        if not self.config_content:
            self.log(self.uid, "❌ Geçersiz VPN konfigürasyonu (Base64 hatası)")
            return False

        self.log(self.uid, "🔐 VPN Bağlantısı kuruluyor...")
        with open(self.config_path, 'w') as f:
            f.write(self.config_content)
        
        # Start openvpn
        # Note: --dev tun0 might conflict if multiple workers run, 
        # but for now we assume prioritized/serialized vpn scans
        cmd = ["openvpn", "--config", self.config_path]
        self.process = subprocess.Popen(
            cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            preexec_fn=os.setsid
        )
        
        # Wait for connection (max 30s)
        for _ in range(30):
            await asyncio.sleep(1)
            # Check for tun0 interface
            res = subprocess.run(["ip", "addr", "show", "dev", "tun0"], capture_output=True)
            if res.returncode == 0:
                self.log(self.uid, "✅ VPN Tüneli (tun0) aktif.")
                return True
            
            if self.process.poll() is not None:
                err = self.process.stderr.read().decode()
                self.log(self.uid, f"❌ VPN Başlatılamadı: {err}")
                return False
                
        self.log(self.uid, "⏱️ VPN bağlantısı zaman aşımına uğradı.")
        return False

    def stop(self):
        if self.process:
            self.log(self.uid, "🔌 VPN Tüneli kapatılıyor...")
            os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
            self.process.wait()
        if os.path.exists(self.config_path):
            os.remove(self.config_path)


def run_scan(target: str, category: str, uid: str = None) -> str:
    """Main scan execution — called by RQ worker"""
    if not uid:
        uid = uuid.uuid4().hex

    # 1. Get metadata (especially vpn_config)
    meta = redis_client.hgetall(f"scan:{uid}:meta")
    vpn_config = meta.get("vpn_config")
    
    # 2. Resolve and analyze target
    target_info = resolve_target(target)
    
    # Update meta status
    redis_client.hset(f"scan:{uid}:meta", "status", "running")

    services = PROFILE_SERVICES.get(category, [])
    log_scan(uid, f"🎯 Starting {category.upper()} scan for {target}")
    log_scan(uid, f"📄 Target Strategy: IP={target_info['ip']}, FQDN={target_info['fqdn']}")

    vpn = None
    if vpn_config:
        vpn = VpnManager(uid, vpn_config, log_scan)
        # We need an event loop since call_service is async
        loop = asyncio.get_event_loop()
        if not loop.run_until_complete(vpn.start()):
            log_scan(uid, "❌ VPN bağlantısı başarısız olduğu için tarama iptal edildi.")
            redis_client.hset(f"scan:{uid}:meta", "status", "failed")
            vpn.stop()
            return uid

    # Run all services via HTTP
    try:
        asyncio.run(run_all_services(services, target_info, uid, category))
    except Exception as e:
        log_scan(uid, f"💥 Scan execution failed: {e}")
        if vpn: vpn.stop()
        raise RuntimeError(f"Scan failed: {e}")

    if vpn:
        vpn.stop()

    # Mark completed
    log_scan(uid, f"✅ Scan completed for {target}")
    redis_client.hset(f"scan:{uid}:meta", "status", "completed")
    redis_client.hset(f"scan:{uid}:meta", "completed_at", datetime.now().isoformat())

    # Email notification
    try:
        meta = redis_client.hgetall(f"scan:{uid}:meta")
        user_email = meta.get("user_email") or os.getenv("MAIL_TO", "")
        user_name  = meta.get("user_name", "Kullanıcı")
        if user_email:
            send_scan_email(
                to_email=user_email,
                to_name=user_name,
                target=target,
                category=category,
                uid=uid,
                services=services,
                started_at=meta.get("started_at", ""),
            )
    except Exception as mail_err:
        log_scan(uid, f"⚠️ E-posta gönderilemedi: {mail_err}")

    return uid


def send_scan_email(to_email: str, to_name: str, target: str, category: str,
                    uid: str, services: list, started_at: str):
    """Send HTML email when scan completes"""
    smtp_host = os.getenv("SMTP_HOST", "")
    smtp_port = int(os.getenv("SMTP_PORT", "465"))
    smtp_user = os.getenv("SMTP_USER", "")
    smtp_pass = os.getenv("SMTP_PASS", "")
    smtp_from = os.getenv("SMTP_FROM", smtp_user)

    if not smtp_host or not smtp_user:
        log_scan(uid, "⚠️ SMTP yapılandırması eksik, e-posta gönderilmedi.")
        return

    report_url = f"https://pentestone.zaferkaraca.net/report/{uid}"
    mode_labels = {"white": "White Box", "gray": "Gray Box", "black": "Black Box"}
    mode_label = mode_labels.get(category, category.upper())
    tool_count = len(services)
    completed_at = datetime.now().strftime("%d.%m.%Y %H:%M")

    html = f"""\
<!DOCTYPE html>
<html lang="tr">
<head><meta charset="UTF-8"></head>
<body style="margin:0;padding:0;background:#0f1923;font-family:'Segoe UI',Tahoma,Geneva,Verdana,sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#0f1923;padding:40px 0;">
  <tr><td align="center">
    <table width="600" cellpadding="0" cellspacing="0" style="background:linear-gradient(135deg,#16213e 0%,#1a1a2e 100%);border-radius:16px;border:1px solid rgba(117,230,218,0.15);overflow:hidden;">
      <tr><td style="background:linear-gradient(90deg,#00d4aa 0%,#75E6DA 100%);padding:28px 40px;text-align:center;">
        <h1 style="margin:0;color:#0f1923;font-size:22px;font-weight:800;letter-spacing:0.5px;">🛡️ Tarama Tamamlandı</h1>
      </td></tr>
      <tr><td style="padding:32px 40px;">
        <p style="color:#b0bec5;font-size:15px;margin:0 0 20px;line-height:1.6;">
          Merhaba <strong style="color:#75E6DA;">{to_name}</strong>,<br>
          Güvenlik taramanız başarıyla tamamlandı. Sonuçlarınız aşağıda özetlenmiştir.
        </p>
        <table width="100%" cellpadding="0" cellspacing="0" style="margin:0 0 28px;">
          <tr><td style="padding:12px 16px;background:rgba(255,255,255,0.04);border-radius:8px 8px 0 0;border-bottom:1px solid rgba(255,255,255,0.06);">
            <span style="color:#78909c;font-size:12px;text-transform:uppercase;letter-spacing:1px;">Hedef</span><br>
            <span style="color:#fff;font-size:16px;font-weight:700;">{target}</span>
          </td></tr>
          <tr><td style="padding:12px 16px;background:rgba(255,255,255,0.04);border-bottom:1px solid rgba(255,255,255,0.06);">
            <span style="color:#78909c;font-size:12px;text-transform:uppercase;letter-spacing:1px;">Tarama Modu</span><br>
            <span style="color:#75E6DA;font-size:15px;font-weight:600;">{mode_label}</span>
          </td></tr>
          <tr><td style="padding:12px 16px;background:rgba(255,255,255,0.04);border-bottom:1px solid rgba(255,255,255,0.06);">
            <span style="color:#78909c;font-size:12px;text-transform:uppercase;letter-spacing:1px;">Kullanılan Araçlar</span><br>
            <span style="color:#fff;font-size:15px;font-weight:600;">{tool_count} araç</span>
          </td></tr>
          <tr><td style="padding:12px 16px;background:rgba(255,255,255,0.04);border-radius:0 0 8px 8px;">
            <span style="color:#78909c;font-size:12px;text-transform:uppercase;letter-spacing:1px;">Tamamlanma</span><br>
            <span style="color:#fff;font-size:15px;font-weight:600;">{completed_at}</span>
          </td></tr>
        </table>
        <table width="100%" cellpadding="0" cellspacing="0">
          <tr><td align="center">
            <a href="{report_url}" style="display:inline-block;padding:14px 40px;background:linear-gradient(90deg,#00d4aa,#75E6DA);color:#0f1923;font-size:15px;font-weight:800;text-decoration:none;border-radius:10px;letter-spacing:0.5px;">
              📄 Raporu Görüntüle
            </a>
          </td></tr>
        </table>
        <p style="color:#546e7a;font-size:12px;margin:24px 0 0;text-align:center;line-height:1.5;">
          Bu e-posta <strong>Pentaas One-Click Scanner</strong> tarafından otomatik gönderilmiştir.<br>
          Tarama ID: <code style="background:rgba(255,255,255,0.06);padding:2px 6px;border-radius:4px;color:#78909c;">{uid}</code>
        </p>
      </td></tr>
      <tr><td style="padding:16px 40px;background:rgba(0,0,0,0.2);text-align:center;border-top:1px solid rgba(255,255,255,0.05);">
        <span style="color:#455a64;font-size:11px;">© {datetime.now().year} Zafer Karaca · pentestone.zaferkaraca.net</span>
      </td></tr>
    </table>
  </td></tr>
</table>
</body>
</html>
"""

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"🛡️ Tarama Tamamlandı — {target} ({mode_label})"
    msg["From"]    = f"Pentaas Scanner <{smtp_from}>"
    msg["To"]      = to_email
    msg.attach(MIMEText(html, "html", "utf-8"))

    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE

    with smtplib.SMTP_SSL(smtp_host, smtp_port, context=context) as server:
        server.login(smtp_user, smtp_pass)
        server.sendmail(smtp_from, to_email, msg.as_string())

    log_scan(uid, f"📧 Tarama raporu e-postası gönderildi → {to_email}")
