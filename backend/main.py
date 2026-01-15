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
    # 1. Nuclei (Black/Gray usually)
    nuclei_path = os.path.join(data_dir, "nuclei.json")
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
                    for item in data.get("vulnerabilities", []):
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
                for alert in data.get("site", [{}])[0].get("alerts", []):
                    results["findings"].append({
                        "id": f"zap-{len(results['findings'])}",
                        "title": alert.get("name", "ZAP Finding"),
                        "severity": alert.get("riskdesc", "Medium").split(" ")[0],
                        "description": alert.get("desc", "")
                    })
        except: pass

    # 4. WPScan (Gray usually)
    wpscan_path = os.path.join(data_dir, "wpscan.json")
    if os.path.exists(wpscan_path):
        try:
            with open(wpscan_path, 'r') as f:
                data = json.load(f)
                # Parse vulnerabilities
                ivs = data.get("interesting_findings", [])
                for item in ivs:
                  results["findings"].append({
                        "id": f"wps-i-{len(results['findings'])}",
                        "title": "WPScan Interest",
                        "severity": "Low",
                        "description": item.get("to_s", "Interesting finding")
                    })
                # Parse version vulnerabilities if any
                vulnerabilities = data.get("version", {}).get("vulnerabilities", [])
                for v in vulnerabilities:
                    results["findings"].append({
                        "id": f"wps-v-{len(results['findings'])}",
                        "title": v.get("title", "WordPress Vulnerability"),
                        "severity": "High",
                        "description": f"Fixed in: {v.get('fixed_in', 'N/A')}"
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
                    state = port.find("state").get("state")
                    if state == "open":
                        service = port.find("service")
                        svc_name = service.get("name") if service is not None else "unknown"
                        results["findings"].append({
                            "id": f"nmap-{len(results['findings'])}",
                            "title": f"Open Port: {portid} ({svc_name})",
                            "severity": "Low",
                            "description": f"The port {portid} running {svc_name} was found open."
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
                    if entry.get("status") in [200, 204, 301, 302]:
                        results["findings"].append({
                            "id": f"dir-{len(results['findings'])}",
                            "title": f"Directory Found: {entry.get('path', 'unknown')}",
                            "severity": "Medium" if entry.get("status") == 200 else "Low",
                            "description": f"Accessible path found: {entry.get('url')} (Status: {entry.get('status')})"
                        })
        except: pass

    # Placeholder for counts if findings empty
    if not results["findings"]:
        # Add basic dummy if nothing found to avoid empty dashboard during dev
        results["findings"].append({
            "id": "info-1",
            "title": "Scan Completed",
            "severity": "Low",
            "description": "The scan finished but no specific vulnerabilities were automatically parsed yet."
        })

    return results
