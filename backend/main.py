import os
import json
import uuid
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from engine import run_scan, REPORT_DIR

app = FastAPI()


class ScanRequest(BaseModel):
    ip: str
    category: str


@app.post("/scan")
async def create_scan(req: ScanRequest, background_tasks: BackgroundTasks):
    try:
        # Generate UID here so we can return it immediately
        uid = uuid.uuid4().hex
        
        # Run the heavy subprocess in the background
        background_tasks.add_task(run_scan, req.ip, req.category, uid)
        
        return {
            "status": "started",
            "scan_id": uid
        }
    except Exception as e:
        print(f"Error starting scan task: {e}")
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@app.get("/scan/{scan_id}")
def get_scan_status(scan_id: str):
    path = os.path.join(REPORT_DIR, scan_id, "data", "scan_summary.txt")
    if os.path.exists(path):
        return {"status": "completed", "scan_id": scan_id}
    
    # Check if directory exists at least
    dir_path = os.path.join(REPORT_DIR, scan_id, "data")
    if os.path.exists(dir_path):
        return {"status": "running", "scan_id": scan_id}
    
    return {"status": "not_found", "scan_id": scan_id}


@app.get("/scan/{scan_id}/results")
def get_scan_results(scan_id: str):
    data_dir = os.path.join(REPORT_DIR, scan_id, "data")
    if not os.path.exists(data_dir):
        raise HTTPException(status_code=404, detail="Scan results not found")

    results = {
        "findings": [],
        "raw_files": os.listdir(data_dir)
    }

    # Helper to parse common tool outputs
    # 1. Nuclei (All modes)
    for nuclei_file in ["nuclei.json", "nuclei_white.json"]:
        nuclei_path = os.path.join(data_dir, nuclei_file)
        if os.path.exists(nuclei_path):
            try:
                with open(nuclei_path, 'r') as f:
                    for line in f:
                        if not line.strip(): continue
                        item = json.loads(line)
                        results["findings"].append({
                            "id": f"nuclei-{len(results['findings'])}",
                            "title": item.get("info", {}).get("name", "Nuclei Finding"),
                            "severity": item.get("info", {}).get("severity", "info").capitalize(),
                            "description": item.get("info", {}).get("description", "No description provided.")
                        })
            except: pass

    # 2. Nikto (Common)
    for nikto_file in ["nikto_white.json", "nikto_black.json"]:
        nikto_path = os.path.join(data_dir, nikto_file)
        if os.path.exists(nikto_path):
            try:
                with open(nikto_path, 'r') as f:
                    data = json.load(f)
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
            except: pass

    # 3. ZAP (Gray usually)
    zap_path = os.path.join(data_dir, "zap.json")
    if os.path.exists(zap_path):
        try:
            with open(zap_path, 'r') as f:
                data = json.load(f)
                sites = data.get("site", [])
                if isinstance(sites, dict): sites = [sites] # robustness
                for site in sites:
                    for alert in site.get("alerts", []):
                        # Map riskcode to severity
                        risk = alert.get("riskdesc", "Medium").split(" ")[0].capitalize()
                        results["findings"].append({
                            "id": f"zap-{len(results['findings'])}",
                            "title": alert.get("name", "ZAP Finding"),
                            "severity": risk,
                            "description": alert.get("desc", "No description provided.")
                        })
        except: pass
    
    # Check for ZAP yaml just in case
    zap_yaml = os.path.join(data_dir, "zap.yaml")
    if os.path.exists(zap_yaml):
        results["findings"].append({
            "id": f"zap-y-{len(results['findings'])}",
            "title": "ZAP YAML Report Found",
            "severity": "Info",
            "description": "ZAP produced a YAML report instead of JSON. This might contain configuration or alert summaries."
        })

    # 4. WPScan (Gray usually)
    wpscan_path = os.path.join(data_dir, "wpscan.json")
    if os.path.exists(wpscan_path):
        try:
            with open(wpscan_path, 'r') as f:
                data = json.load(f)
                
                # Check for WPScan abort/errors
                if data.get("scan_aborted"):
                    results["findings"].append({
                        "id": f"wps-a-{len(results['findings'])}",
                        "title": "WPScan: Scan Aborted",
                        "severity": "Info",
                        "description": data.get("scan_aborted")
                    })
                else:
                    # Check for nested targets if it's not the flat format
                    targets = [data]
                    if not data.get("interesting_findings") and not data.get("version"):
                        # Try to find target keys (they are usually URLs)
                        for k, v in data.items():
                            if isinstance(v, dict) and (v.get("interesting_findings") or v.get("version")):
                                targets.append(v)
                    
                    for t in targets:
                        # Parse interesting findings
                        for item in t.get("interesting_findings", []):
                            results["findings"].append({
                                "id": f"wps-i-{len(results['findings'])}",
                                "title": "WPScan Interest",
                                "severity": "Info",
                                "description": item.get("to_s", "Interesting finding")
                            })
                        # Parse version vulnerabilities
                        vulnerabilities = t.get("version", {}).get("vulnerabilities", [])
                        for v in vulnerabilities:
                            results["findings"].append({
                                "id": f"wps-v-{len(results['findings'])}",
                                "title": v.get("title", "WordPress Vulnerability"),
                                "severity": "High",
                                "description": f"Fixed in: {v.get('fixed_in', 'N/A')}"
                            })
                        # Parse plugin vulnerabilities
                        for p_name, p_data in t.get("plugins", {}).items():
                            for v in p_data.get("vulnerabilities", []):
                                results["findings"].append({
                                    "id": f"wps-p-{len(results['findings'])}",
                                    "title": f"Plugin: {p_name}",
                                    "severity": "High",
                                    "description": v.get("title", "Vulnerability")
                                })
        except: pass

    # 5. Nmap (Common - XML Parsing)
    import xml.etree.ElementTree as ET
    for nmap_file in ["nmap_white.xml", "nmap_gray.xml", "nmap_black.xml"]:
        nmap_path = os.path.join(data_dir, nmap_file)
        if os.path.exists(nmap_path):
            try:
                tree = ET.parse(nmap_path)
                root = tree.getroot()
                for port in root.findall(".//port"):
                    portid = port.get("portid")
                    state_node = port.find("state")
                    if state_node is not None and state_node.get("state") == "open":
                        service = port.find("service")
                        svc_name = service.get("name") if service is not None else "unknown"
                        svc_ver = service.get("version") if service is not None else ""
                        svc_prod = service.get("product") if service is not None else ""
                        full_svc = f"{svc_prod} {svc_ver}".strip() or svc_name
                        
                        results["findings"].append({
                            "id": f"nmap-{len(results['findings'])}",
                            "title": f"Open Port: {portid} ({svc_name})",
                            "severity": "Low",
                            "description": f"Service: {full_svc} detected on port {portid}."
                        })
            except: pass

    # 6. Dirsearch (White/Gray)
    dirsearch_path = os.path.join(data_dir, "dirsearch.json")
    if os.path.exists(dirsearch_path):
        try:
            with open(dirsearch_path, 'r') as f:
                data = json.load(f)
                # dirsearch format is sometimes a dict with "results" or list of entries
                entries = data if isinstance(data, list) else data.get("results", [])
                for entry in entries:
                    if entry.get("status") in [200, 204, 301, 302, 307]:
                        results["findings"].append({
                            "id": f"dir-{len(results['findings'])}",
                            "title": f"Directory Found: {entry.get('path', 'unknown')}",
                            "severity": "Medium" if entry.get("status") in [200, 307] else "Low",
                            "description": f"Accessible path found: {entry.get('url')} (Status: {entry.get('status')})"
                        })
        except: pass

    # 7. SSLyze (Gray/White)
    sslyze_path = os.path.join(data_dir, "sslyze.json")
    if os.path.exists(sslyze_path):
        try:
            with open(sslyze_path, 'r') as f:
                data = json.load(f)
                server_results = data.get("server_scan_results", [])
                for target in server_results:
                    if target.get("scan_status") == "ERROR_NO_CONNECTIVITY":
                         results["findings"].append({
                                "id": f"ssl-err-{len(results['findings'])}",
                                "title": "SSLyze: No Connectivity",
                                "severity": "Info",
                                "description": f"Could not connect to {target.get('server_location', {}).get('hostname')}:443 for SSL scan."
                            })
                         continue

                    scan_res = target.get("scan_result", {})
        except: pass

    # 8. TestSSL (Common - JSON list)
    testssl_path = os.path.join(data_dir, "testssl.json")
    if os.path.exists(testssl_path):
        try:
            with open(testssl_path, 'r') as f:
                data = json.load(f)
                for item in data:
                    sev = item.get("severity", "INFO")
                    # Map TestSSL severity to frontend
                    sev_map = {
                        "FATAL": "Critical",
                        "CRITICAL": "Critical",
                        "HIGH": "High",
                        "MEDIUM": "Medium",
                        "LOW": "Low",
                        "WARN": "Medium",
                        "INFO": "Info",
                        "OK": "Info"
                    }
                    mapped_sev = sev_map.get(sev, "Info")
                    
                    if sev in ["FATAL", "CRITICAL", "HIGH", "MEDIUM", "LOW", "WARN"]:
                        results["findings"].append({
                            "id": f"tssl-{len(results['findings'])}",
                            "title": f"TestSSL: {item.get('id', 'Issue')}",
                            "severity": mapped_sev,
                            "description": item.get("finding", "No description")
                        })
        except: pass

    # 9. WhatWeb (Common - JSON list)
    whatweb_path = os.path.join(data_dir, "whatweb.json")
    if os.path.exists(whatweb_path):
        try:
            with open(whatweb_path, 'r') as f:
                data = json.load(f)
                for entry in data:
                    plugins = entry.get("plugins", {})
                    for p_name, p_val in plugins.items():
                        # Extract string or version, joining lists if necessary
                        desc_parts = []
                        for key in ["string", "version"]:
                            val = p_val.get(key)
                            if val:
                                if isinstance(val, list):
                                    desc_parts.extend([str(v) for v in val])
                                else:
                                    desc_parts.append(str(val))
                        
                        desc = ", ".join(desc_parts) if desc_parts else "Detected"
                        
                        results["findings"].append({
                            "id": f"ww-{len(results['findings'])}",
                            "title": f"Tech Detected: {p_name}",
                            "severity": "Info",
                            "description": desc
                        })
        except: pass

    # 10. Arjun (Hidden parameter discovery)
    arjun_path = os.path.join(data_dir, "arjun.json")
    if os.path.exists(arjun_path):
        try:
            with open(arjun_path, 'r') as f:
                data = json.load(f)
                # Arjun JSON: {"url": ["param1", "param2"]}
                for url, params in data.items():
                    if params:
                        results["findings"].append({
                            "id": f"arjun-{len(results['findings'])}",
                            "title": "Hidden Parameters Found",
                            "severity": "Medium",
                            "description": f"Target: {url}\nParameters: {', '.join(params)}"
                        })
        except: pass

    # 11. Dalfox (XSS Scanner)
    dalfox_path = os.path.join(data_dir, "dalfox.json")
    if os.path.exists(dalfox_path):
        try:
            with open(dalfox_path, 'r') as f:
                # Dalfox can produce multiple lines of JSON
                for line in f:
                    if not line.strip(): continue
                    item = json.loads(line)
                    results["findings"].append({
                        "id": f"dalfox-{len(results['findings'])}",
                        "title": f"XSS Found: {item.get('type', 'Vulnerability')}",
                        "severity": "High",
                        "description": f"URL: {item.get('url', 'N/A')}\nParam: {item.get('param', 'N/A')}\nPoc: {item.get('poc', 'N/A')}"
                    })
        except: pass
    
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
        except: pass

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
        except: pass


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
