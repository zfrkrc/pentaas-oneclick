"""
Scan Engine - Parallel execution using docker compose run
Stores logs and results in Redis instead of filesystem.
"""
import subprocess
import uuid
import os
import json
import asyncio
import time
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import logging
from redis import Redis

logger = logging.getLogger(__name__)

# Redis Connection – REDIS_URL varsa onu kullan
REDIS_URL = os.getenv("REDIS_URL")
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
if REDIS_URL:
    redis_client = Redis.from_url(REDIS_URL, decode_responses=True)
else:
    redis_client = Redis(host=REDIS_HOST, port=6379, db=0, decode_responses=True)

BASE_DIR = "/app"
COMPOSE_FILE = f"{BASE_DIR}/compose/docker-compose.string.yml"
# We still need a temp dir for docker volumes, but we won't rely on it for persistent storage
REPORT_DIR = f"{BASE_DIR}/reports"

# Define services for each profile
PROFILE_SERVICES = {
    "white": ["nmap_white", "testssl", "dirsearch", "nikto_white", "whatweb", "arjun", "dalfox", "wafw00f", "dnsrecon", "nuclei_white",
              "sqlmap", "commix", "gittools", "wapiti", "nosqlmap", "gobuster", "arachni"],
    "gray": ["nmap_gray", "wpscan", "zap", "sslyze"],
    "black": ["nmap_black", "nikto_black", "nuclei"]
}

# Output file mapping (Service Name -> Output Filename)
# Only needed for reading the file to save to Redis
OUTPUT_MAPPING = {
    "nmap_white": "nmap_white.xml",
    "nmap_gray": "nmap_gray.xml",
    "nmap_black": "nmap_black.xml",
    "nuclei": "nuclei.json",
    "nuclei_white": "nuclei_white.json",
    "nikto_black": "nikto_black.json",
    "nikto_white": "nikto_white.json",
    "wpscan": "wpscan.json",
    "zap": "zap.json",
    "sslyze": "sslyze.json",
    "testssl": "testssl.json",
    "dirsearch": "dirsearch.json",
    "whatweb": "whatweb.json",
    "arjun": "arjun.json",
    "dalfox": "dalfox.json",
    "wafw00f": "wafw00f.json",
    "dnsrecon": "dnsrecon.json",
    "sqlmap": "sqlmap_output/log",
    "commix": "commix.txt",
    "gittools": "gittools.log",
    "wapiti": "wapiti.json",
    "nosqlmap": "nosqlmap.txt",
    "gobuster": "gobuster.json",
    "w3af": "w3af.json",
    "arachni": "arachni.afr"
}

def log_scan(uid: str, message: str):
    """Log scan progress to Redis"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}"
    
    try:
        # Push to Redis list
        redis_client.rpush(f"scan:{uid}:logs", log_entry)
        # Set expire for logs (1 hour)
        redis_client.expire(f"scan:{uid}:logs", 3600)
    except Exception as e:
        print(f"Redis Log Error: {e}")
    
    print(f"[{uid}] {message}")

def save_result_to_redis(uid: str, service_name: str, host_data_dir_internal: str):
    """Read output file and save to Redis"""
    filename = OUTPUT_MAPPING.get(service_name)
    if not filename:
        return

    filepath = os.path.join(host_data_dir_internal, filename)
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            if content:
                # Save to Redis: scan:{uid}:result:{service_name}
                redis_client.set(f"scan:{uid}:result:{service_name}", content)
                redis_client.expire(f"scan:{uid}:result:{service_name}", 3600) # 1 hour TTL
                log_scan(uid, f"💾 {service_name} results saved to Redis ({len(content)} bytes)")
        except Exception as e:
            log_scan(uid, f"⚠️ Failed to save {service_name} results to Redis: {e}")

async def run_service_async(service_name: str, env_vars: dict, uid: str) -> tuple:
    """Run a single service asynchronously using docker compose with timeout and live logging"""
    # Timeout settings: Longer for slow services
    SLOW_SERVICES = ["nikto_white", "nikto_black", "testssl", "nuclei", "nuclei_white", "dalfox", 
                     "sqlmap", "arachni", "wapiti"]
    SERVICE_TIMEOUT = 300 if service_name in SLOW_SERVICES else 180
    
    log_scan(uid, f"🚀 Starting {service_name} (Timeout: {SERVICE_TIMEOUT}s)...")
    start_time = time.time()
    
    try:
        # Run service, piping stdout/stderr
        process = await asyncio.create_subprocess_exec(
            "docker", "compose", "-f", COMPOSE_FILE,
            "run", "--rm", service_name,
            env=env_vars,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        # Helper to read stream and log
        async def read_stream(stream, label):
            while True:
                line = await stream.readline()
                if not line:
                    break
                decoded_line = line.decode().strip()
                if decoded_line:
                    if "error" in decoded_line.lower() or "fail" in decoded_line.lower() or "warning" in decoded_line.lower():
                         log_scan(uid, f"📝 [{service_name}] {decoded_line}")
        
        try:
            # Run stream readers concurrently with wait_for
            await asyncio.wait_for(
                asyncio.gather(
                    read_stream(process.stdout, "stdout"),
                    read_stream(process.stderr, "stderr"),
                    process.wait()
                ),
                timeout=SERVICE_TIMEOUT
            )
            
            duration = time.time() - start_time
            if process.returncode == 0:
                log_scan(uid, f"✅ {service_name} completed in {duration:.1f}s")
                # Save result to Redis
                save_result_to_redis(uid, service_name, f"{REPORT_DIR}/{uid}/data")
                return (service_name, True, None)
            elif service_name == "testssl" and process.returncode == 7:
                # TestSSL exit code 7 = warning (e.g., TLS 1.3 not supported)
                log_scan(uid, f"⚠️ {service_name} completed with warnings in {duration:.1f}s")
                save_result_to_redis(uid, service_name, f"{REPORT_DIR}/{uid}/data")
                return (service_name, True, "Completed with warnings")
            else:
                log_scan(uid, f"❌ {service_name} failed with code {process.returncode}")
                return (service_name, False, f"Exit code {process.returncode}")
                
        except asyncio.TimeoutError:
            try:
                process.kill()
                await process.wait()
            except:
                pass
            duration = time.time() - start_time
            log_scan(uid, f"⏱️ {service_name} timed out after {duration:.1f}s - Forcefully stopped")
            # Try to save whatever result exists
            save_result_to_redis(uid, service_name, f"{REPORT_DIR}/{uid}/data")
            return (service_name, True, "Timeout (Partial results saved)")
            
    except Exception as e:
        duration = time.time() - start_time
        log_scan(uid, f"💥 {service_name} crashed after {duration:.1f}s: {str(e)}")
        return (service_name, False, str(e))


async def run_all_services_parallel(services: list, env_vars: dict, uid: str):
    """Run services: Others first (parallel), then Nuclei (last)"""
    
    # Separate Nuclei from other services
    nuclei_services = [s for s in services if 'nuclei' in s]
    other_services = [s for s in services if 'nuclei' not in s]
    
    results = []
    
    # 1. Run all non-nuclei services in parallel first
    if other_services:
        log_scan(uid, f"📋 Running {len(other_services)} services in parallel (Priority Group)...")
        tasks = [run_service_async(svc, env_vars, uid) for svc in other_services]
        results.extend(await asyncio.gather(*tasks, return_exceptions=True))
    
    # 2. Run Nuclei services last
    if nuclei_services:
        log_scan(uid, f"📋 Running Nuclei services ({len(nuclei_services)}) - Last Step...")
        tasks = [run_service_async(svc, env_vars, uid) for svc in nuclei_services]
        results.extend(await asyncio.gather(*tasks, return_exceptions=True))
    
    successful = sum(1 for r in results if isinstance(r, tuple) and r[1])
    failed = len(results) - successful
    
    log_scan(uid, f"📊 Summary: {successful} succeeded, {failed} failed")
    
    # Set completion status in Redis
    redis_client.set(f"scan:{uid}:status", "completed")
    redis_client.expire(f"scan:{uid}:status", 3600)
    
    return results


def run_scan(target: str, category: str, uid: str = None) -> str:
    """Main scan execution function"""
    if not uid:
        uid = uuid.uuid4().hex
    
    # Internal path (container view) - Still needed for docker mounts
    data_dir_internal = f"{REPORT_DIR}/{uid}/data"
    os.makedirs(data_dir_internal, exist_ok=True)
    
    # Host path (for DinD)
    host_reports_path = os.environ.get("HOST_REPORTS_PATH", f"{os.getcwd()}/reports")
    host_data_dir = f"{host_reports_path}/{uid}/data"

    # Save metadata to REDIS
    redis_client.hmset(f"scan:{uid}:meta", {
        "target": target,
        "category": category,
        "uid": uid,
        "status": "running",
        "started_at": datetime.now().isoformat()
    })
    redis_client.expire(f"scan:{uid}:meta", 3600)

    # Sanitize and parse target
    target_raw = target.strip()
    target_domain = target_raw.replace("https://", "").replace("http://", "").split('/')[0].split(':')[0]
    target_url = target_raw if (target_raw.startswith("http://") or target_raw.startswith("https://")) else f"http://{target_raw}"

    env_vars = os.environ.copy()
    env_vars["TARGET"] = target_raw
    env_vars["TARGET_URL"] = target_url
    env_vars["TARGET_DOMAIN"] = target_domain
    env_vars["HOST_DATA_DIR"] = host_data_dir

    # Get services for this profile
    services = PROFILE_SERVICES.get(category, [])
    
    log_scan(uid, f"🎯 Starting {category.upper()} scan for {target}")
    log_scan(uid, f"📦 Services: {', '.join(services)}")
    
    # Notify UI about all expected services
    for svc in services:
        log_scan(uid, f"⏳ Pending {svc}")
    
    # Run all services in parallel
    try:
        asyncio.run(run_all_services_parallel(services, env_vars, uid))
    except Exception as e:
        log_scan(uid, f"💥 Scan execution failed: {str(e)}")
        raise RuntimeError(f"Scan failed: {str(e)}")

    # Mark scan as completed in Redis
    log_scan(uid, f"✅ Scan completed for {target}")
    redis_client.hset(f"scan:{uid}:meta", "status", "completed")
    redis_client.hset(f"scan:{uid}:meta", "completed_at", datetime.now().isoformat())

    # E-posta bildirimi gönder
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
    """Tarama tamamlandığında kullanıcıya HTML e-posta gönderir"""
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
      
      <!-- Header -->
      <tr><td style="background:linear-gradient(90deg,#00d4aa 0%,#75E6DA 100%);padding:28px 40px;text-align:center;">
        <h1 style="margin:0;color:#0f1923;font-size:22px;font-weight:800;letter-spacing:0.5px;">🛡️ Tarama Tamamlandı</h1>
      </td></tr>

      <!-- Body -->
      <tr><td style="padding:32px 40px;">
        <p style="color:#b0bec5;font-size:15px;margin:0 0 20px;line-height:1.6;">
          Merhaba <strong style="color:#75E6DA;">{to_name}</strong>,<br>
          Güvenlik taramanız başarıyla tamamlandı. Sonuçlarınız aşağıda özetlenmiştir.
        </p>

        <!-- Info Table -->
        <table width="100%" cellpadding="0" cellspacing="0" style="margin:0 0 28px;">
          <tr>
            <td style="padding:12px 16px;background:rgba(255,255,255,0.04);border-radius:8px 8px 0 0;border-bottom:1px solid rgba(255,255,255,0.06);">
              <span style="color:#78909c;font-size:12px;text-transform:uppercase;letter-spacing:1px;">Hedef</span><br>
              <span style="color:#fff;font-size:16px;font-weight:700;">{target}</span>
            </td>
          </tr>
          <tr>
            <td style="padding:12px 16px;background:rgba(255,255,255,0.04);border-bottom:1px solid rgba(255,255,255,0.06);">
              <span style="color:#78909c;font-size:12px;text-transform:uppercase;letter-spacing:1px;">Tarama Modu</span><br>
              <span style="color:#75E6DA;font-size:15px;font-weight:600;">{mode_label}</span>
            </td>
          </tr>
          <tr>
            <td style="padding:12px 16px;background:rgba(255,255,255,0.04);border-bottom:1px solid rgba(255,255,255,0.06);">
              <span style="color:#78909c;font-size:12px;text-transform:uppercase;letter-spacing:1px;">Kullanılan Araçlar</span><br>
              <span style="color:#fff;font-size:15px;font-weight:600;">{tool_count} araç</span>
            </td>
          </tr>
          <tr>
            <td style="padding:12px 16px;background:rgba(255,255,255,0.04);border-radius:0 0 8px 8px;">
              <span style="color:#78909c;font-size:12px;text-transform:uppercase;letter-spacing:1px;">Tamamlanma</span><br>
              <span style="color:#fff;font-size:15px;font-weight:600;">{completed_at}</span>
            </td>
          </tr>
        </table>

        <!-- CTA Button -->
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

      <!-- Footer -->
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

