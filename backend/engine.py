"""
Scan Engine - Parallel execution using docker compose run
"""
import subprocess
import uuid
import os
import json
import asyncio
import time
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

BASE_DIR = "/app"
COMPOSE_FILE = f"{BASE_DIR}/compose/docker-compose.string.yml"
REPORT_DIR = f"{BASE_DIR}/reports"

# Define services for each profile
PROFILE_SERVICES = {
    "white": ["nmap_white", "testssl", "dirsearch", "nikto_white", "whatweb", "arjun", "dalfox", "wafw00f", "dnsrecon", "nuclei_white"],
    "gray": ["nmap_gray", "wpscan", "zap", "sslyze"],
    "black": ["nmap_black", "nikto_black", "nuclei"]
}


def log_scan(uid: str, message: str):
    """Log scan progress to a file"""
    log_file = f"{REPORT_DIR}/{uid}/data/scan.log"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with open(log_file, "a") as f:
            f.write(f"[{timestamp}] {message}\n")
    except Exception as e:
        logger.error(f"Failed to write log: {e}")
    
    print(f"[{uid}] {message}")


async def run_service_async(service_name: str, env_vars: dict, uid: str) -> tuple:
    """Run a single service asynchronously using docker compose with timeout and live logging"""
    # Timeout settings: 3 minutes (180s)
    SERVICE_TIMEOUT = 180 
    
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
                return (service_name, True, None)
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
            return (service_name, False, "Operation timed out")
            
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
    return results


def run_scan(target: str, category: str, uid: str = None) -> str:
    """Main scan execution function"""
    if not uid:
        uid = uuid.uuid4().hex
    
    # Internal path (container view)
    data_dir_internal = f"{REPORT_DIR}/{uid}/data"
    os.makedirs(data_dir_internal, exist_ok=True)
    
    # Host path (for DinD)
    host_reports_path = os.environ.get("HOST_REPORTS_PATH", f"{os.getcwd()}/reports")
    host_data_dir = f"{host_reports_path}/{uid}/data"

    # Save metadata for UI tracking
    with open(f"{data_dir_internal}/meta.json", "w") as f:
        json.dump({"target": target, "category": category, "uid": uid}, f)

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
    
    # Run all services in parallel
    try:
        asyncio.run(run_all_services_parallel(services, env_vars, uid))
    except Exception as e:
        log_scan(uid, f"💥 Scan execution failed: {str(e)}")
        raise RuntimeError(f"Scan failed: {str(e)}")

    # Mark scan as completed
    log_scan(uid, f"✅ Scan completed for {target}")
    with open(f"{data_dir_internal}/scan_summary.txt", "w") as f:
        f.write(f"Scan completed for {target}\n")
        f.write(f"Category: {category}\n")
        f.write(f"UID: {uid}\n")

    return uid


# Track active scans for status checking
active_scans = {}


def get_scan_status(scan_id: str) -> dict:
    """Get scan status by checking filesystem"""
    data_dir = f"{REPORT_DIR}/{scan_id}/data"
    
    if not os.path.exists(data_dir):
        return {"status": "not_found", "scan_id": scan_id}
    
    # Check for completion marker
    if os.path.exists(f"{data_dir}/scan_summary.txt"):
        return {"status": "completed", "scan_id": scan_id}
    
    # Check log file for progress
    log_file = f"{data_dir}/scan.log"
    services_status = {}
    
    if os.path.exists(log_file):
        try:
            with open(log_file, 'r') as f:
                logs = f.readlines()
            
            # Parse logs to extract service status
            for line in logs:
                if "🚀 Starting" in line:
                    # Extract service name
                    parts = line.split("Starting ")
                    if len(parts) > 1:
                        service_name = parts[1].split("...")[0].strip()
                        services_status[service_name] = {"status": "running", "completed": False}
                
                elif "✅" in line and "completed in" in line:
                    # Extract service name
                    parts = line.split("] ✅ ")
                    if len(parts) > 1:
                        service_name = parts[1].split(" completed")[0].strip()
                        services_status[service_name] = {"status": "completed", "completed": True}
                
                elif "❌" in line and "failed" in line:
                    parts = line.split("] ❌ ")
                    if len(parts) > 1:
                        service_name = parts[1].split(" failed")[0].strip()
                        services_status[service_name] = {"status": "failed", "completed": True}
        
        except Exception as e:
            logger.error(f"Error parsing log file: {e}")
    
    # Check if any files exist (indicates progress)
    try:
        files = os.listdir(data_dir)
        report_files = [f for f in files if f not in ["meta.json", "scan.log", "scan_summary.txt"] and not f.startswith(".")]
        
        if len(report_files) > 0:
            return {
                "status": "running",
                "scan_id": scan_id,
                "services": services_status,
                "files_generated": len(report_files)
            }
    except Exception:
        pass
    
    return {
        "status": "running",
        "scan_id": scan_id,
        "services": services_status
    }


# For async compatibility
async def get_scan_status_async(scan_id: str) -> dict:
    """Async wrapper for get_scan_status"""
    return get_scan_status(scan_id)
