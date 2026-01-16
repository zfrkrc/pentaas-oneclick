from fastapi import FastAPI, HTTPException
from abc import ABC, abstractmethod
import uuid
import os
import json
import asyncio
from typing import Dict, Any
from .models import (
    ScanRequest, ScanResponse, ScanStatusResponse, 
    ScanResultsResponse, HealthResponse, ScanStatus
)


class BaseToolService(ABC):
    """Base class for all tool services"""
    
    def __init__(self, service_name: str, version: str = "1.0.0"):
        self.service_name = service_name
        self.version = version
        self.app = FastAPI(title=f"{service_name} Service")
        self.scans: Dict[str, Dict[str, Any]] = {}
        self.results_dir = os.getenv("RESULTS_DIR", "/data/results")
        os.makedirs(self.results_dir, exist_ok=True)
        
        # Register routes
        self._register_routes()
    
    def _register_routes(self):
        """Register FastAPI routes"""
        
        @self.app.get("/health", response_model=HealthResponse)
        async def health():
            return HealthResponse(
                service=self.service_name,
                status="healthy",
                version=self.version
            )
        
        @self.app.get("/ready")
        async def ready():
            """Readiness check"""
            return {"ready": True, "service": self.service_name}
        
        @self.app.post("/scan", response_model=ScanResponse)
        async def create_scan(request: ScanRequest):
            scan_id = str(uuid.uuid4())
            
            # Store scan info
            self.scans[scan_id] = {
                "target": request.target,
                "options": request.options,
                "status": ScanStatus.QUEUED
            }
            
            # Start scan asynchronously in background
            asyncio.create_task(self._execute_scan(scan_id, request.target, request.options))
            
            return ScanResponse(scan_id=scan_id, status=ScanStatus.QUEUED)
        
        @self.app.get("/status/{scan_id}", response_model=ScanStatusResponse)
        async def get_status(scan_id: str):
            if scan_id not in self.scans:
                raise HTTPException(status_code=404, detail="Scan not found")
            
            scan_info = self.scans[scan_id]
            return ScanStatusResponse(
                scan_id=scan_id,
                status=scan_info["status"],
                progress=scan_info.get("progress"),
                message=scan_info.get("message")
            )
        
        @self.app.get("/results/{scan_id}", response_model=ScanResultsResponse)
        async def get_results(scan_id: str):
            if scan_id not in self.scans:
                raise HTTPException(status_code=404, detail="Scan not found")
            
            scan_info = self.scans[scan_id]
            
            # Load results from file
            results_file = os.path.join(self.results_dir, f"{scan_id}.json")
            if not os.path.exists(results_file):
                return ScanResultsResponse(
                    scan_id=scan_id,
                    status=scan_info["status"],
                    findings=[]
                )
            
            with open(results_file, 'r') as f:
                results = json.load(f)
            
            return ScanResultsResponse(
                scan_id=scan_id,
                status=scan_info["status"],
                findings=results.get("findings", []),
                raw_output=results.get("raw_output"),
                metadata=results.get("metadata")
            )
    
    async def _execute_scan(self, scan_id: str, target: str, options: Dict[str, Any]):
        """Execute the scan (to be implemented by subclasses)"""
        try:
            self.scans[scan_id]["status"] = ScanStatus.RUNNING
            
            # Call the tool-specific scan method
            results = await self.scan(target, options)
            
            # Save results
            results_file = os.path.join(self.results_dir, f"{scan_id}.json")
            with open(results_file, 'w') as f:
                json.dump(results, f, indent=2)
            
            self.scans[scan_id]["status"] = ScanStatus.COMPLETED
            print(f"[{self.service_name}] Scan {scan_id} completed successfully")
        except Exception as e:
            error_msg = f"Scan failed: {type(e).__name__}: {str(e)}"
            self.scans[scan_id]["status"] = ScanStatus.FAILED
            self.scans[scan_id]["message"] = error_msg
            print(f"[{self.service_name}] Scan {scan_id} failed: {error_msg}")
            
            # Save partial results if any
            try:
                results_file = os.path.join(self.results_dir, f"{scan_id}.json")
                with open(results_file, 'w') as f:
                    json.dump({"error": error_msg, "findings": []}, f, indent=2)
            except:
                pass
    
    @abstractmethod
    async def scan(self, target: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """
        Tool-specific scan implementation
        Must return a dict with:
        - findings: List[Finding]
        - raw_output: str
        - metadata: Dict[str, Any]
        """
        pass
    
    def run(self, host: str = "0.0.0.0", port: int = 8000):
        """Run the FastAPI service"""
        import uvicorn
        uvicorn.run(self.app, host=host, port=port)
