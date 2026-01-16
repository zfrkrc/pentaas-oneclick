import os
import json
import uuid
import xml.etree.ElementTree as ET
import logging
from typing import List, Dict, Any
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from engine import run_scan, REPORT_DIR
import redis
from rq import Queue

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# RQ Setup
redis_url = os.getenv('REDIS_URL', 'redis://redis:6379')
redis_conn = redis.from_url(redis_url)
q = Queue(connection=redis_conn)

app = FastAPI()

PROFILE_TOOLS = {
    "white": {
        "Nmap": "nmap_white.xml",
        "TestSSL": "testssl.json",
        "Dirsearch": "dirsearch.json",
        "Nikto": "nikto_white.json",
        "WhatWeb": "whatweb.json",
        "Nuclei": "nuclei_white.json",
        "Arjun": "arjun.json",
        "Dalfox": "dalfox.json",
        "Wafw00f": "wafw00f.json",
        "DNSRecon": "dnsrecon.json"
    },
    "gray": {
        "Nmap": "nmap_gray.xml",
        "WPScan": "wpscan.json",
        "ZAP Baseline": "zap.json",
        "SSLyze": "sslyze.json"
    },
    "black": {
        "Nmap": "nmap_black.xml",
        "Nuclei": "nuclei.json",
        "Nikto": "nikto_black.json"
    }
}



class ScanRequest(BaseModel):
    ip: str
    category: str


@app.post("/scan")
async def create_scan(req: ScanRequest):
    try:
        # Generate UID here so we can return it immediately
        uid = uuid.uuid4().hex
        
        # Enqueue the scan job to RQ with 30 minute timeout
        job = q.enqueue(run_scan, req.ip, req.category, uid, job_timeout=1800)
        logger.info(f"Enqueued scan job {job.id} for target {req.ip}, UID: {uid}")
        
        return {
            "status": "started",
            "scan_id": uid,
            "job_id": job.id
        }
    except Exception as e:
        logger.error(f"Error starting scan job: {e}")
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@app.get("/scan/{scan_id}")
async def get_scan_status(scan_id: str):
    """Get real-time status of all services in the scan"""
    from engine import get_scan_status_async
    
    try:
        status = await get_scan_status_async(scan_id)
        return status
    except Exception as e:
        logger.error(f"Error getting scan status: {e}")
        return {"status": "error", "scan_id": scan_id, "error": str(e)}


@app.get("/scan/{scan_id}/logs")
def get_scan_logs(scan_id: str):
    """Get real-time scan logs"""
    log_file = os.path.join(REPORT_DIR, scan_id, "data", "scan.log")
    
    if not os.path.exists(log_file):
        return {"scan_id": scan_id, "logs": [], "message": "Log file not found"}
    
    try:
        with open(log_file, 'r') as f:
            logs = f.readlines()
        
        return {
            "scan_id": scan_id,
            "logs": [line.strip() for line in logs],
            "total_lines": len(logs)
        }
    except Exception as e:
        return {"scan_id": scan_id, "logs": [], "error": str(e)}


@app.get("/scan/{scan_id}/results")
def get_scan_results(scan_id: str):
    data_dir = os.path.join(REPORT_DIR, scan_id, "data")
    if not os.path.exists(data_dir):
        raise HTTPException(status_code=404, detail="Scan results not found")

    results = {
        "findings": [],
        "raw_files": os.listdir(data_dir),
        "progress": {"completed": [], "pending": []}
    }

    # Load metadata to know which category we are in
    meta_path = os.path.join(data_dir, "meta.json")
    category = "white"
    if os.path.exists(meta_path):
        try:
            with open(meta_path, 'r') as f:
                meta = json.load(f)
                category = meta.get("category", "white")
        except Exception as e:
            logger.error(f"Error reading meta.json: {e}")

    # Track progress
    expected_tools = PROFILE_TOOLS.get(category, {})
    for tool_name, filename in expected_tools.items():
        if os.path.exists(os.path.join(data_dir, filename)):
            results["progress"]["completed"].append(tool_name)
        else:
            results["progress"]["pending"].append(tool_name)


    # Helper to parse common tool outputs
    # 1. Nuclei (All modes)
    for nuclei_file in ["nuclei.json", "nuclei_white.json"]:
        nuclei_path = os.path.join(data_dir, nuclei_file)
        if os.path.exists(nuclei_path):
            try:
                with open(nuclei_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if not line: continue
                        try:
                            item = json.loads(line)
                            results["findings"].append({
                                "id": f"nuclei-{len(results['findings'])}",
                                "title": item.get("info", {}).get("name", "Nuclei Finding"),
                                "severity": item.get("info", {}).get("severity", "info").capitalize(),
                                "description": item.get("info", {}).get("description", "No description provided.")
                            })
                        except json.JSONDecodeError:
                            logger.error(f"Failed to parse nuclei line: {line[:100]}")
            except Exception as e:
                logger.error(f"Error reading nuclei file: {e}")

    # 2. Nikto (Common)
    for nikto_file in ["nikto_white.json", "nikto_black.json"]:
        nikto_path = os.path.join(data_dir, nikto_file)
        if os.path.exists(nikto_path):
            try:
                # Check if file is empty
                if os.path.getsize(nikto_path) == 0:
                    continue

                with open(nikto_path, 'r') as f:
                    try:
                        data = json.load(f)
                    except json.JSONDecodeError:
                        continue 

                    # Nikto can be a list or a dict
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
            except Exception as e:
                logger.error(f"Error reading nikto file: {e}")

    # ... (ZAP, WPScan, Nmap, etc. skipped in diff) ...

    # 8. TestSSL (Common - JSON list)
    testssl_path = os.path.join(data_dir, "testssl.json")
    if os.path.exists(testssl_path):
        try:
            if os.path.getsize(testssl_path) == 0:
                pass
            else:
                with open(testssl_path, 'r') as f:
                    try:
                        data = json.load(f)
                        if isinstance(data, list):
                            for item in data:
                                sev = item.get("severity", "INFO")
                                sev_map = {
                                    "FATAL": "Critical", "CRITICAL": "Critical", "HIGH": "High",
                                    "MEDIUM": "Medium", "LOW": "Low", "WARN": "Medium",
                                    "INFO": "Info", "OK": "Info"
                                }
                                mapped_sev = sev_map.get(sev, "Info")
                                
                                if sev in ["FATAL", "CRITICAL", "HIGH", "MEDIUM", "LOW", "WARN"]:
                                    results["findings"].append({
                                        "id": f"tssl-{len(results['findings'])}",
                                        "title": f"TestSSL: {item.get('id', 'Issue')}",
                                        "severity": mapped_sev,
                                        "description": item.get("finding", "No description")
                                    })
                    except json.JSONDecodeError:
                        pass # File likely being written
        except Exception as e:
            logger.error(f"Error reading testssl file: {e}")

    # 11. Dalfox (XSS Scanner)
    dalfox_path = os.path.join(data_dir, "dalfox.json")
    if os.path.exists(dalfox_path) and os.path.getsize(dalfox_path) > 0:
        try:
            with open(dalfox_path, 'r') as f:
                content = f.read().strip()
                if not content:
                    pass
                elif content.startswith("["):
                    # JSON Array format
                    try:
                        items = json.loads(content)
                        for item in items:
                            results["findings"].append({
                                "id": f"dalfox-{len(results['findings'])}",
                                "title": f"XSS Found: {item.get('type', 'Vulnerability')}",
                                "severity": "High",
                                "description": f"URL: {item.get('url', 'N/A')}\nParam: {item.get('param', 'N/A')}\nPoc: {item.get('poc', 'N/A')}"
                            })
                    except json.JSONDecodeError:
                        pass
                else:
                    # JSON Lines format
                    for line in content.splitlines():
                        if not line.strip(): continue
                        try:
                            item = json.loads(line)
                            results["findings"].append({
                                "id": f"dalfox-{len(results['findings'])}",
                                "title": f"XSS Found: {item.get('type', 'Vulnerability')}",
                                "severity": "High",
                                "description": f"URL: {item.get('url', 'N/A')}\nParam: {item.get('param', 'N/A')}\nPoc: {item.get('poc', 'N/A')}"
                            })
                        except json.JSONDecodeError:
                            pass
        except Exception as e:
            logger.error(f"Error reading dalfox file: {e}")
    
    # 10. Waf00f
    waf_path = os.path.join(data_dir, "wafw00f.json")
    if os.path.exists(waf_path):
        try:
            with open(waf_path, 'r') as f:
                data = json.load(f)
                for item in data:
                    if item.get("firewall") != "None":
                        results["findings"].append({
                            "id": f"waf-{len(results['findings'])}",
                            "title": f"WAF Detected: {item.get('firewall')}",
                            "severity": "Info",
                            "description": f"Target is protected by {item.get('firewall')} ({item.get('manufacturer', 'N/A')})"
                        })
        except Exception as e:
            logger.error(f"Error reading wafw00f file: {e}")

    # 11. DNSRecon
    dns_path = os.path.join(data_dir, "dnsrecon.json")
    if os.path.exists(dns_path):
        try:
            with open(dns_path, 'r') as f:
                data = json.load(f)
                for item in data:
                    results["findings"].append({
                        "id": f"dns-{len(results['findings'])}",
                        "title": f"DNS Record: {item.get('type')}",
                        "severity": "Info",
                        "description": f"Name: {item.get('name')}\nValue: {item.get('address') or item.get('exchange') or item.get('strings') or 'N/A'}"
                    })
        except Exception as e:
            logger.error(f"Error reading dnsrecon file: {e}")


    # Placeholder for counts if findings empty
    if not results["findings"]:
        # Check if we at least have files but no findings
        if results["raw_files"]:
            results["findings"].append({
                "id": "info-1",
                "title": "Scan Finished",
                "severity": "Info",
                "description": f"Scan completed. Found files: {', '.join(results['raw_files'])}. No critical vulnerabilities were automatically flagged."
            })
        else:
            results["findings"].append({
                "id": "info-1",
                "title": "Scan Incomplete",
                "severity": "Info",
                "description": "The scan finished or was interrupted without producing output files."
            })

    # Final pass to ensure severity is capitalized correctly for frontend
    for f in results["findings"]:
        f["severity"] = f["severity"].capitalize()
        # Map "Informational" or anything else to "Info" for consistency if needed
        if f["severity"] == "Informational":
            f["severity"] = "Info"

    return results
