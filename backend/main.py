from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from engine import run_scan

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
