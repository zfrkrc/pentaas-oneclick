from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
import uuid
import json
import logging
from redis import Redis
from datetime import datetime
import xml.etree.ElementTree as ET

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# App initialization
app = FastAPI(title="PentaaS OneClick Scanners")

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Redis Connection
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
try:
    redis_conn = Redis(host=REDIS_HOST, port=6379, db=0, decode_responses=True)
except Exception as e:
    logger.error(f"Failed to connect to Redis: {e}")
    redis_conn = None

# Directories (kept for legacy references or temp storage if needed)
BASE_DIR = "/app"
REPORT_DIR = f"{BASE_DIR}/reports"

# Pydantic Models matches Frontend Request
class ScanRequest(BaseModel):
    ip: str
    category: str  # white, gray, black

class ScanResponse(BaseModel):
    message: str
    scan_id: str
    status: str


@app.get("/")
def read_root():
    return {"message": "PentaaS OneClick Scanner API is Ready"}


@app.post("/scan", response_model=ScanResponse)
async def create_scan(scan: ScanRequest, background_tasks: BackgroundTasks):
    """
    Start a new scan.
    Enqueues the scan task to RQ worker.
    """
    from worker import queue_scan  # Deferred import to avoid circular dependency
    
    # Map frontend fields to backend variables
    target = scan.ip
    scan_type = scan.category

    scan_id = uuid.uuid4().hex
    
    # Save initial metadata to Redis immediately
    if redis_conn:
        redis_conn.hmset(f"scan:{scan_id}:meta", {
            "target": target,
            "category": scan_type,
            "uid": scan_id,
            "status": "queued",
            "started_at": datetime.now().isoformat()
        })
        redis_conn.expire(f"scan:{scan_id}:meta", 3600)

    try:
        # Enqueue task
        job = queue_scan(target, scan_type, scan_id)
        
        return {
            "message": "Scan started successfully",
            "scan_id": scan_id,
            "status": "queued"
        }
    except Exception as e:
        logger.error(f"Failed to queue scan: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/scan/{scan_id}")
async def get_scan_status(scan_id: str):
    """Get real-time scan status from Redis"""
    if not redis_conn:
         return {"status": "error", "message": "Redis unavailable"}

    try:
        # Check metadata in Redis
        meta = redis_conn.hgetall(f"scan:{scan_id}:meta")
        if not meta:
            return {"status": "not_found", "scan_id": scan_id}
        
        status = meta.get("status", "running")
        
        # Check individual services status from logs logic
        services_status = {}
        logs = redis_conn.lrange(f"scan:{scan_id}:logs", 0, -1)
        
        for line in logs:
            if "🚀 Starting" in line:
                parts = line.split("Starting ")
                if len(parts) > 1:
                    svc = parts[1].split("(")[0].strip().split("...")[0].strip()
                    services_status[svc] = {"status": "running", "completed": False}
            elif "✅" in line and "completed" in line:
                parts = line.split("] ✅ ")
                if len(parts) > 1:
                    svc = parts[1].split(" completed")[0].strip()
                    services_status[svc] = {"status": "completed", "completed": True}
            elif "❌" in line and "failed" in line:
                 parts = line.split("] ❌ ")
                 if len(parts) > 1:
                    svc = parts[1].split(" failed")[0].strip()
                    services_status[svc] = {"status": "failed", "completed": True}

        return {
            "status": status,
            "scan_id": scan_id,
            "services": services_status
        }
    except Exception as e:
        logger.error(f"Error getting scan status: {e}")
        return {"status": "error", "scan_id": scan_id, "error": str(e)}


@app.get("/scan/{scan_id}/logs")
def get_scan_logs(scan_id: str):
    """Get real-time scan logs from Redis"""
    if not redis_conn:
         return {"logs": [], "error": "Redis unavailable"}

    try:
        logs = redis_conn.lrange(f"scan:{scan_id}:logs", 0, -1)
        if not logs:
             return {"scan_id": scan_id, "logs": [], "message": "No logs found"}
             
        return {
            "scan_id": scan_id,
            "logs": logs,
            "total_lines": len(logs)
        }
    except Exception as e:
        logger.error(f"Error getting logs: {e}")
        return {"scan_id": scan_id, "logs": [], "error": str(e)}


@app.get("/scan/{scan_id}/results")
def get_scan_results(scan_id: str):
    """Get scan results from Redis"""
    if not redis_conn:
        raise HTTPException(status_code=500, detail="Redis unavailable")

    # Get metadata for target info
    meta = redis_conn.hgetall(f"scan:{scan_id}:meta")
    target = meta.get("target", "unknown")
    category = meta.get("category", "unknown")
    
    results = {
        "scan_id": scan_id,
        "target": target,
        "scan_type": category,
        "timestamp": meta.get("started_at", datetime.now().isoformat()),
        "findings": []
    }

    # Helper to get content from Redis
    def get_content(service_name):
        return redis_conn.get(f"scan:{scan_id}:result:{service_name}")

    # 1. Nuclei (Critical)
    for nuclei_svc in ["nuclei", "nuclei_white"]:
        content = get_content(nuclei_svc)
        if content:
            for line in content.splitlines():
                if not line.strip(): continue
                try:
                    finding = json.loads(line)
                    results["findings"].append({
                        "id": f"nuc-{len(results['findings'])}",
                        "title": finding.get("info", {}).get("name", "Unknown Vuln"),
                        "severity": finding.get("info", {}).get("severity", "Low").capitalize(),
                        "description": f"Template: {finding.get('template-id')}\nMatcher: {finding.get('matcher-name', 'N/A')}\nExtracted: {finding.get('extracted-results', [])}"
                    })
                except json.JSONDecodeError:
                    pass

    # 2. Nikto
    for nikto_svc in ["nikto_white", "nikto_black"]:
        content = get_content(nikto_svc)
        if content:
            try:
                data = json.loads(content)
                items = []
                if isinstance(data, list):
                    for entry in data:
                        items.extend(entry.get("vulnerabilities", []))
                else:
                    items = data.get("vulnerabilities", [])
                
                for item in items:
                    results["findings"].append({
                        "id": f"nikto-{len(results['findings'])}",
                        "title": "Nikto Finding",
                        "severity": "Medium",
                        "description": item.get("msg", "Unknown finding")
                    })
            except: pass

    # 3. ZAP
    content = get_content("zap")
    if content:
        try:
            data = json.loads(content)
            sites = data.get("site", [])
            if isinstance(sites, dict): sites = [sites]
            for site in sites:
                for alert in site.get("alerts", []):
                    risk = alert.get("riskdesc", "Medium").split(" ")[0].capitalize()
                    results["findings"].append({
                        "id": f"zap-{len(results['findings'])}",
                        "title": alert.get("name", "ZAP Finding"),
                        "severity": risk,
                        "description": alert.get("desc", "No description provided.")
                    })
        except: pass

    # 4. WPScan
    content = get_content("wpscan")
    if content:
        try:
            data = json.loads(content)
            if data.get("scan_aborted"):
                 results["findings"].append({"id": f"wps-a", "title": "WPScan Aborted", "severity": "Info", "description": data.get("scan_aborted")})
            else:
                # Add parsing if needed
                pass 
        except: pass

    # 5. Nmap
    for nmap_svc in ["nmap_white", "nmap_gray", "nmap_black"]:
        content = get_content(nmap_svc)
        if content:
            try:
                root = ET.fromstring(content)
                for port in root.findall(".//port"):
                    portid = port.get("portid")
                    state = port.find("state")
                    if state is not None and state.get("state") == "open":
                        service = port.find("service")
                        svc_name = service.get("name") if service is not None else "unknown"
                        results["findings"].append({
                            "id": f"nmap-{len(results['findings'])}",
                            "title": f"Open Port: {portid} ({svc_name})",
                            "severity": "Low",
                            "description": f"Port {portid} is open."
                        })
            except: pass

    # 6. Dirsearch
    content = get_content("dirsearch")
    if content:
        try:
            data = json.loads(content)
            entries = data if isinstance(data, list) else data.get("results", [])
            for entry in entries:
                if entry.get("status") in [200, 204, 301, 302, 307]:
                    results["findings"].append({
                        "id": f"dir-{len(results['findings'])}",
                        "title": f"Directory: {entry.get('path')}",
                        "severity": "Info",
                        "description": f"URL: {entry.get('url')} ({entry.get('status')})"
                    })
        except: pass

    # 7. SSLyze (Simplified)
    content = get_content("sslyze")
    if content:
         results["findings"].append({"id": "ssl-info", "title": "SSLyze Completed", "severity": "Info", "description": "SSL Scan finished."})


    # 8. TestSSL
    content = get_content("testssl")
    if content:
        try:
            data = json.loads(content)
            if isinstance(data, list):
                for item in data:
                   sev = item.get("severity", "INFO")
                   if sev in ["FATAL", "CRITICAL", "HIGH", "MEDIUM", "LOW"]:
                       results["findings"].append({
                           "id": f"tssl-{len(results['findings'])}",
                           "title": f"TestSSL: {item.get('id')}",
                           "severity": sev.capitalize(),
                           "description": item.get("finding")
                       })
        except: pass

    # 9. WhatWeb
    content = get_content("whatweb")
    if content:
        try:
            data = json.loads(content)
            for entry in data:
                plugins = entry.get("plugins", {})
                results["findings"].append({
                    "id": f"ww-{len(results['findings'])}",
                    "title": "WhatWeb Tech Detected",
                    "severity": "Info",
                    "description": ", ".join(plugins.keys())
                })
        except: pass

    # 10. Arjun
    content = get_content("arjun")
    if content:
        try:
            data = json.loads(content)
            for url, params in data.items():
                if params:
                    results["findings"].append({
                        "id": f"arj-{len(results['findings'])}",
                        "title": "Hidden Parameters",
                        "severity": "Medium",
                        "description": f"Params: {', '.join(params)}"
                    })
        except: pass

    # 11. Dalfox
    content = get_content("dalfox")
    if content:
        try:
             items = []
             if content.strip().startswith("["):
                 try: items = json.loads(content)
                 except: pass
             else:
                 for line in content.splitlines():
                     try: items.append(json.loads(line))
                     except: pass
             
             for item in items:
                # Fallback keys for Dalfox JSON
                url_val = item.get('url') or item.get('target') or item.get('message_str') or "N/A"
                param_val = item.get('param') or item.get('parameter') or "N/A"
                poc_val = item.get('poc') or item.get('payload') or "N/A"

                results["findings"].append({
                    "id": f"dal-{len(results['findings'])}",
                    "title": f"XSS: {item.get('type', 'Vuln')}",
                    "severity": "High",
                    "description": f"Target: {url_val}\nParam: {param_val}\nPayload: {poc_val}"
                })
        except: pass

    # 12. Wafw00f
    content = get_content("wafw00f")
    if content:
        try:
            data = json.loads(content)
            if isinstance(data, list):
                for entry in data:
                    firewall = entry.get("firewall", "None")
                    if firewall and firewall != "None":
                         results["findings"].append({
                             "id": f"waf-{len(results['findings'])}",
                             "title": f"WAF: {firewall}",
                             "severity": "Info",
                             "description": "WAF Detected"
                         })
        except: pass

    # 13. DNSRecon
    content = get_content("dnsrecon")
    if content:
        try:
            data = json.loads(content)
            if isinstance(data, list):
                 results["findings"].append({
                     "id": f"dns-{len(results['findings'])}",
                     "title": f"DNS Records Found",
                     "severity": "Info",
                     "description": f"Found {len(data)} records"
                 })
        except: pass

    return results
