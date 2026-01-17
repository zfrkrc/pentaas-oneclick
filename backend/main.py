from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import HTMLResponse
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

# Version
__version__ = "2.0.0"

# App initialization
app = FastAPI(
    title="PentaaS OneClick Scanners",
    version=__version__,
    description="Automated penetration testing platform with 24+ security tools"
)

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
    return {
        "message": "PentaaS OneClick Scanner API is Ready",
        "version": __version__,
        "tools_count": 24,
        "profiles": ["white", "gray", "black"]
    }


@app.get("/version")
def get_version():
    """Get API version information"""
    return {
        "version": __version__,
        "release_date": "2026-01-17",
        "tools": {
            "white_box": 17,
            "gray_box": 4,
            "black_box": 3,
            "total": 24
        }
    }


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


@app.get("/scans")
def list_scans():
    """List all past scans from Redis"""
    if not redis_conn:
        return {"scans": []}
    
    try:
        # Find all scan meta keys
        keys = redis_conn.keys("scan:*:meta")
        scans = []
        
        for key in keys:
            try:
                # key format: scan:{uid}:meta
                uid = key.split(":")[1]
                meta = redis_conn.hgetall(key)
                scans.append({
                    "scan_id": uid,
                    "target": meta.get("target", "Unknown"),
                    "scan_type": meta.get("category", "Unknown"),
                    "status": meta.get("status", "Unknown"),
                    "timestamp": meta.get("started_at", "")
                })
            except:
                continue
        
        # Sort by timestamp desc
        scans.sort(key=lambda x: x["timestamp"], reverse=True)
        return {"scans": scans}
    except Exception as e:
        logger.error(f"Error listing scans: {e}")
        return {"scans": [], "error": str(e)}


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
            elif "⏳ Pending" in line:
                parts = line.split("Pending ")
                if len(parts) > 1:
                    svc = parts[1].strip()
                    if svc not in services_status:
                        services_status[svc] = {"status": "pending", "completed": False}
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
    nuclei_found = False
    for nuclei_svc in ["nuclei", "nuclei_white"]:
        content = get_content(nuclei_svc)
        if content:
            has_findings = False
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
                    has_findings = True
                    nuclei_found = True
                except Exception as e:
                    logger.error(f"Nuclei parsing error: {e}")
                    results["findings"].append({
                        "id": "err-nuc",
                        "title": "Nuclei Parse Error",
                        "severity": "Info",
                        "description": f"Failed to parse output: {str(e)}"
                    })
            
            # If content exists but no findings were added
            if not has_findings and not any(f["id"].startswith("err-nuc") for f in results["findings"]):
                results["findings"].append({
                    "id": f"nuc-info",
                    "title": "Nuclei Scan Completed",
                    "severity": "Info",
                    "description": "Nuclei scan completed successfully. No vulnerabilities found."
                })
                nuclei_found = True

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
            except Exception as e:
                logger.error(f"Nikto parsing error: {e}")
                results["findings"].append({"id": "err-nikto", "title": "Nikto Parse Error", "severity": "Info", "description": str(e)})

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
        except Exception as e:
            logger.error(f"ZAP parsing error: {e}")
            results["findings"].append({"id": "err-zap", "title": "ZAP Parse Error", "severity": "Info", "description": str(e)})

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
        except Exception as e:
            logger.error(f"WPScan parsing error: {e}")
            results["findings"].append({"id": "err-wps", "title": "WPScan Parse Error", "severity": "Info", "description": str(e)})

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
        except Exception as e:
            logger.error(f"Dirsearch parsing error: {e}")
            results["findings"].append({"id": "err-dirsearch", "title": "Dirsearch Parse Error", "severity": "Info", "description": str(e)})

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
        except Exception as e:
            logger.error(f"TestSSL parsing error: {e}")
            results["findings"].append({"id": "err-testssl", "title": "TestSSL Parse Error", "severity": "Info", "description": str(e)})

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
            has_params = False
            for url, params in data.items():
                if params:
                    results["findings"].append({
                        "id": f"arj-{len(results['findings'])}",
                        "title": "Hidden Parameters",
                        "severity": "Medium",
                        "description": f"Params: {', '.join(params)}"
                    })
                    has_params = True
            
            if not has_params:
                results["findings"].append({
                    "id": "arj-info",
                    "title": "Arjun Scan Completed",
                    "severity": "Info",
                    "description": "Arjun scan completed. No hidden parameters found."
                })
        except Exception as e:
            logger.error(f"Arjun parsing error: {e}")
            results["findings"].append({"id": "err-arjun", "title": "Arjun Parse Error", "severity": "Info", "description": str(e)})

    # 11. Dalfox
    content = get_content("dalfox")
    if content:
        try:
             items = []
             has_findings = False
             
             # Try to parse as JSON array or line-by-line JSON
             if content.strip().startswith("["):
                 try: items = json.loads(content)
                 except: pass
             else:
                 for line in content.splitlines():
                     if line.strip():
                         try: items.append(json.loads(line))
                         except: pass
             
             for item in items:
                # Dalfox JSON structure varies, try multiple key patterns
                # Common keys: data, message, message_str, url, param, poc, payload, type
                
                # Extract URL/Target
                url_val = (item.get('data') or item.get('url') or 
                          item.get('target') or item.get('message_str') or "")
                
                # Extract Parameter
                param_val = item.get('param') or item.get('parameter') or ""
                
                # Extract Payload/POC
                poc_val = item.get('poc') or item.get('payload') or item.get('evidence') or ""
                
                # Extract vulnerability type
                vuln_type = item.get('type') or item.get('cwe') or 'XSS'
                
                # Only add if we have meaningful data (not all N/A)
                if url_val or param_val or poc_val:
                    results["findings"].append({
                        "id": f"dal-{len(results['findings'])}",
                        "title": f"XSS Vulnerability: {vuln_type}",
                        "severity": "High",
                        "description": f"URL: {url_val if url_val else 'Not specified'}\nParameter: {param_val if param_val else 'Not specified'}\nPayload: {poc_val if poc_val else 'Not specified'}"
                    })
                    has_findings = True
             
             # If content exists but no valid findings parsed, add info message
             if not has_findings and content.strip():
                 results["findings"].append({
                     "id": "dal-info",
                     "title": "Dalfox Scan Completed",
                     "severity": "Info",
                     "description": f"Dalfox scan completed. Raw output length: {len(content)} bytes. No XSS vulnerabilities detected."
                 })
        except Exception as e:
            logger.error(f"Dalfox parsing error: {e}")
            results["findings"].append({
                "id": "err-dalfox",
                "title": "Dalfox Parse Error",
                "severity": "Info",
                "description": f"Failed to parse Dalfox output: {str(e)}"
            })

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
            if isinstance(data, list) and len(data) > 0:
                # Group records by type for better readability
                record_types = {}
                for record in data:
                    rec_type = record.get('type', 'Unknown')
                    if rec_type not in record_types:
                        record_types[rec_type] = []
                    record_types[rec_type].append(record)
                
                # Create findings for each record type
                for rec_type, records in record_types.items():
                    record_details = []
                    # Show ALL records (no limit)
                    for rec in records:
                        name = rec.get('name', rec.get('hostname', 'N/A'))
                        address = rec.get('address', rec.get('target', rec.get('exchange', 'N/A')))
                        record_details.append(f"  • {name} → {address}")
                    
                    results["findings"].append({
                        "id": f"dns-{rec_type.lower()}-{len(results['findings'])}",
                        "title": f"DNS Records: {rec_type} ({len(records)} found)",
                        "severity": "Info",
                        "description": "\n".join(record_details) if record_details else f"Found {len(records)} {rec_type} records"
                    })
        except Exception as e:
            logger.error(f"DNSRecon parsing error: {e}")
            results["findings"].append({
                "id": "err-dns",
                "title": "DNSRecon Parse Error",
                "severity": "Info",
                "description": f"Failed to parse DNSRecon output: {str(e)}"
            })

    return results


@app.get("/report/{scan_id}", response_class=HTMLResponse)
async def get_scan_report_html(scan_id: str):
    """Generate and serve a standalone HTML report for a scan"""
    try:
        # Reuse existing logic to get results
        # Assuming get_scan_results is synchronous as defined in main.py
        results_data = get_scan_results(scan_id)
        
        target = results_data.get("target", "Unknown")
        scan_type = results_data.get("scan_type", "Unknown")
        timestamp = results_data.get("timestamp", "Unknown")
        findings = results_data.get("findings", [])
        
        # Calculate Severity Counts
        counts = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0, "Info": 0}
        for f in findings:
            sev = f.get("severity", "Info")
            if sev in counts: counts[sev] += 1
            else: counts["Info"] += 1

        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Scan Report - {target}</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
            <style>
                body {{ background-color: #f4f6f9; }}
                .severity-Critical {{ background-color: #dc3545; color: white; }}
                .severity-High {{ background-color: #fd7e14; color: white; }}
                .severity-Medium {{ background-color: #ffc107; color: black; }}
                .severity-Low {{ background-color: #0dcaf0; color: white; }}
                .severity-Info {{ background-color: #6c757d; color: white; }}
                .card {{ border: none; box-shadow: 0 0.125rem 0.25rem rgba(0,0,0,0.075); margin-bottom: 20px; }}
            </style>
        </head>
        <body>
            <div class="container py-5">
                <div class="header d-flex justify-content-between align-items-center mb-5">
                    <div>
                        <h1 class="display-5 fw-bold text-dark">PentaaS OneClick Report</h1>
                        <p class="text-muted mb-0">Scan ID: {scan_id}</p>
                    </div>
                    <div class="text-end">
                        <h3 class="fw-bold">{target}</h3>
                        <span class="badge bg-dark fs-6">{str(scan_type).upper()}</span>
                        <span class="badge bg-secondary fs-6">{timestamp}</span>
                    </div>
                </div>

                <!-- Summary Cards -->
                <div class="row g-3 mb-5">
                    <div class="col"><div class="card p-3 text-center border-top border-4 border-danger"><h3 class="text-danger fw-bold">{counts['Critical']}</h3><span class="text-muted">Critical</span></div></div>
                    <div class="col"><div class="card p-3 text-center border-top border-4 border-warning"><h3 class="text-warning fw-bold">{counts['High']}</h3><span class="text-muted">High</span></div></div>
                    <div class="col"><div class="card p-3 text-center border-top border-4 border-warning" style="border-color: #ffc107 !important;"><h3 class="text-dark fw-bold">{counts['Medium']}</h3><span class="text-muted">Medium</span></div></div>
                    <div class="col"><div class="card p-3 text-center border-top border-4 border-info"><h3 class="text-info fw-bold">{counts['Low']}</h3><span class="text-muted">Low</span></div></div>
                    <div class="col"><div class="card p-3 text-center border-top border-4 border-secondary"><h3 class="text-secondary fw-bold">{counts['Info']}</h3><span class="text-muted">Info</span></div></div>
                </div>

                <!-- Detailed Findings -->
                <div class="card">
                    <div class="card-header bg-white py-3">
                        <h4 class="mb-0 fw-bold">Detailed Findings</h4>
                    </div>
                    <div class="card-body p-0">
                        <div class="table-responsive">
                            <table class="table table-hover mb-0 align-middle">
                                <thead class="bg-light">
                                    <tr>
                                        <th style="width: 100px;">Severity</th>
                                        <th style="width: 200px;">ID</th>
                                        <th>Finding / Title</th>
                                        <th>Description / Info</th>
                                    </tr>
                                </thead>
                                <tbody>
        """
        
        if not findings:
            html_content += '<tr><td colspan="4" class="text-center p-4">No vulnerabilities found. System appears secure.</td></tr>'
        else:
            for f in findings:
                sev_class = f"severity-{f.get('severity', 'Info')}"
                fid = f.get('id', 'N/A')
                title = f.get('title', 'N/A')
                desc = f.get('description', '')
                if len(desc) > 300: desc = desc[:300] + "..."
                
                # HTML Escape (simple)
                title = str(title).replace("<", "&lt;").replace(">", "&gt;")
                desc = str(desc).replace("<", "&lt;").replace(">", "&gt;").replace("\\n", "<br>")

                html_content += f"""
                <tr>
                    <td><span class="badge {sev_class} w-100 py-2">{f.get('severity', 'Info')}</span></td>
                    <td class="text-secondary small">{fid}</td>
                    <td class="fw-bold">{title}</td>
                    <td class="text-muted small">{desc}</td>
                </tr>
                """

        html_content += """
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
                
                <div class="text-center mt-5 text-muted">
                    <small>Generated by PentaaS OneClick Scanner | Zafer Karaca</small>
                </div>
            </div>
        </body>
        </html>
        """
        
        return HTMLResponse(content=html_content, status_code=200)

    except Exception as e:
        logger.error(f"Error generating report: {e}")
        return HTMLResponse(content=f"<h1>Error generating report</h1><p>{str(e)}</p>", status_code=500)
