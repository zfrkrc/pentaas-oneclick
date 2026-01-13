from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, IPvAnyAddress
import uuid, pathlib, json, subprocess
from engine import run_scan
from ai_sum import summarise

app = FastAPI(title="Pentest-OneClick")
SCAN_ROOT = pathlib.Path("/app/reports")

class ScanReq(BaseModel):
    ip: IPvAnyAddress
    category: str  # white gray black

@app.post("/scan")
def create_scan(req: ScanReq, bg: BackgroundTasks):
    uid = run_scan(str(req.ip), req.category)
    return {"uid": uid, "status": "queued"}

@app.get("/report/{uid}")
def get_report(uid: str):
    f = SCAN_ROOT / uid / "result.json"
    if not f.exists():
        raise HTTPException(404, "Henüz bitmedi veya hatalı UID")
    raw = json.loads(f.read_text())
    ai = summarise(raw)
    return {"ai_summary": ai, "raw": raw}

@app.get("/download/{uid}")
def download(uid: str):
    zip_path = SCAN_ROOT / uid / "bundle.zip"
    if not zip_path.exists():
        subprocess.run(["zip", "-j", zip_path, *(SCAN_ROOT / uid).glob("*")], check=True)
    return FileResponse(zip_path, filename=f"{uid}.zip")
