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
from datetime import datetime
import logging
from redis import Redis

logger = logging.getLogger(__name__)

# Redis Connection
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
redis_client = Redis(host=REDIS_HOST, port=6379, db=0, decode_responses=True)

BASE_DIR = "/app"
COMPOSE_FILE = f"{BASE_DIR}/compose/docker-compose.string.yml"
# We still need a temp dir for docker volumes, but we won't rely on it for persistent storage
REPORT_DIR = f"{BASE_DIR}/reports"

# Define services for each profile
PROFILE_SERVICES = {
    "white": ["nmap_white", "testssl", "dirsearch", "nikto_white", "whatweb", "arjun", "dalfox", "wafw00f", "dnsrecon", "nuclei_white"],
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
    "dnsrecon": "dnsrecon.json"
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
    SLOW_SERVICES = ["nikto_white", "nikto_black", "testssl", "nuclei", "nuclei_white", "dalfox"]
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

    return uid



