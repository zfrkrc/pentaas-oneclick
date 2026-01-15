import os
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from engine import run_scan, REPORT_DIR

app = FastAPI()


class ScanRequest(BaseModel):
    ip: str
    category: str


@app.post("/scan")
def create_scan(req: ScanRequest):
    try:
        uid = run_scan(req.ip, req.category)
        return {
            "status": "started",
            "scan_id": uid
        }
    except Exception as e:
        print(f"Error during scan: {e}")
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
