"""
Scan Orchestrator - Manages parallel execution of microservices
"""
import asyncio
import aiohttp
import os
import json
import uuid
from typing import Dict, List, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

REPORT_DIR = "/app/reports"

# Service endpoints mapping
SERVICE_ENDPOINTS = {
    "white": {
        "nmap": "http://nmap-service:8000",
        "nuclei": "http://nuclei-service:8000",
        "testssl": "http://testssl-service:8000",
        "dirsearch": "http://dirsearch-service:8000",
        "nikto": "http://nikto-service:8000",
        "whatweb": "http://whatweb-service:8000",
        "arjun": "http://arjun-service:8000",
        "dalfox": "http://dalfox-service:8000",
        "wafw00f": "http://wafw00f-service:8000",
        "dnsrecon": "http://dnsrecon-service:8000"
    },
    "gray": {
        "nmap": "http://nmap-service:8000",
        "wpscan": "http://wpscan-service:8000",
        "zap": "http://zap-service:8000",
        "sslyze": "http://sslyze-service:8000"
    },
    "black": {
        "nmap": "http://nmap-service:8000",
        "nuclei": "http://nuclei-service:8000",
        "nikto": "http://nikto-service:8000"
    }
}


class ScanOrchestrator:
    """Orchestrates parallel scan execution across microservices"""
    
    def __init__(self):
        self.active_scans: Dict[str, Dict[str, Any]] = {}
    
    def log_scan(self, scan_id: str, message: str):
        """Log scan progress"""
        log_file = f"{REPORT_DIR}/{scan_id}/data/scan.log"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        try:
            with open(log_file, "a") as f:
                f.write(f"[{timestamp}] {message}\n")
        except Exception as e:
            logger.error(f"Failed to write log: {e}")
        
        logger.info(f"[{scan_id}] {message}")
    
    async def trigger_service_scan(
        self, 
        service_name: str, 
        service_url: str, 
        target: str, 
        scan_id: str,
        options: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Trigger scan on a single microservice"""
        
        self.log_scan(scan_id, f"🚀 Triggering {service_name}...")
        
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "target": target,
                    "options": options or {}
                }
                
                # Start scan on microservice
                async with session.post(
                    f"{service_url}/scan",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        service_scan_id = data.get("scan_id")
                        self.log_scan(scan_id, f"✅ {service_name} started (service_scan_id: {service_scan_id})")
                        return {
                            "service": service_name,
                            "status": "started",
                            "service_scan_id": service_scan_id,
                            "error": None
                        }
                    else:
                        error_msg = await resp.text()
                        self.log_scan(scan_id, f"❌ {service_name} failed to start: {error_msg[:100]}")
                        return {
                            "service": service_name,
                            "status": "failed",
                            "service_scan_id": None,
                            "error": error_msg
                        }
        
        except asyncio.TimeoutError:
            self.log_scan(scan_id, f"⏱️ {service_name} timeout")
            return {
                "service": service_name,
                "status": "timeout",
                "service_scan_id": None,
                "error": "Connection timeout"
            }
        except Exception as e:
            self.log_scan(scan_id, f"💥 {service_name} error: {str(e)}")
            return {
                "service": service_name,
                "status": "error",
                "service_scan_id": None,
                "error": str(e)
            }
    
    async def check_service_status(
        self,
        service_name: str,
        service_url: str,
        service_scan_id: str,
        scan_id: str
    ) -> Dict[str, Any]:
        """Check status of a running service scan"""
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{service_url}/status/{service_scan_id}",
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return {
                            "service": service_name,
                            "status": data.get("status", "unknown"),
                            "completed": data.get("status") == "completed",
                            "error": None
                        }
                    else:
                        return {
                            "service": service_name,
                            "status": "error",
                            "completed": False,
                            "error": f"HTTP {resp.status}"
                        }
        
        except Exception as e:
            return {
                "service": service_name,
                "status": "error",
                "completed": False,
                "error": str(e)
            }
    
    async def start_scan(
        self,
        target: str,
        category: str,
        scan_id: str = None
    ) -> str:
        """Start parallel scan across all services"""
        
        if not scan_id:
            scan_id = uuid.uuid4().hex
        
        # Create scan directory
        data_dir = f"{REPORT_DIR}/{scan_id}/data"
        os.makedirs(data_dir, exist_ok=True)
        
        # Save metadata
        with open(f"{data_dir}/meta.json", "w") as f:
            json.dump({
                "target": target,
                "category": category,
                "scan_id": scan_id,
                "started_at": datetime.now().isoformat()
            }, f)
        
        self.log_scan(scan_id, f"🎯 Starting {category.upper()} scan for {target}")
        
        # Get services for this category
        services = SERVICE_ENDPOINTS.get(category, {})
        self.log_scan(scan_id, f"📦 Services: {', '.join(services.keys())}")
        
        # Trigger all services in parallel
        tasks = [
            self.trigger_service_scan(name, url, target, scan_id)
            for name, url in services.items()
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Store service scan IDs for status tracking
        service_scans = {}
        for result in results:
            if isinstance(result, dict) and result.get("service_scan_id"):
                service_scans[result["service"]] = {
                    "service_scan_id": result["service_scan_id"],
                    "service_url": services[result["service"]],
                    "status": "running"
                }
        
        # Store in active scans
        self.active_scans[scan_id] = {
            "target": target,
            "category": category,
            "services": service_scans,
            "started_at": datetime.now().isoformat()
        }
        
        self.log_scan(scan_id, f"✅ All services triggered ({len(service_scans)}/{len(services)} started)")
        
        return scan_id
    
    async def get_scan_status(self, scan_id: str) -> Dict[str, Any]:
        """Get current status of all services in a scan"""
        
        if scan_id not in self.active_scans:
            # Check if scan exists in filesystem
            data_dir = f"{REPORT_DIR}/{scan_id}/data"
            if not os.path.exists(data_dir):
                return {"status": "not_found", "scan_id": scan_id}
            
            # Check for completion marker
            if os.path.exists(f"{data_dir}/scan_summary.txt"):
                return {"status": "completed", "scan_id": scan_id, "services": {}}
            
            return {"status": "unknown", "scan_id": scan_id, "services": {}}
        
        scan_info = self.active_scans[scan_id]
        services_status = {}
        
        # Check status of all services in parallel
        tasks = []
        for service_name, service_info in scan_info["services"].items():
            tasks.append(
                self.check_service_status(
                    service_name,
                    service_info["service_url"],
                    service_info["service_scan_id"],
                    scan_id
                )
            )
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Build status response
        all_completed = True
        for result in results:
            if isinstance(result, dict):
                service_name = result["service"]
                services_status[service_name] = {
                    "status": result["status"],
                    "completed": result["completed"]
                }
                if not result["completed"]:
                    all_completed = False
        
        # If all completed, mark scan as done
        if all_completed and len(services_status) > 0:
            data_dir = f"{REPORT_DIR}/{scan_id}/data"
            with open(f"{data_dir}/scan_summary.txt", "w") as f:
                f.write(f"Scan completed\n")
            self.log_scan(scan_id, "✅ All services completed")
            return {
                "status": "completed",
                "scan_id": scan_id,
                "services": services_status
            }
        
        return {
            "status": "running",
            "scan_id": scan_id,
            "services": services_status
        }


# Global orchestrator instance
orchestrator = ScanOrchestrator()


def run_scan(target: str, category: str, uid: str = None) -> str:
    """Wrapper for RQ job compatibility"""
    return asyncio.run(orchestrator.start_scan(target, category, uid))


async def get_scan_status_async(scan_id: str) -> Dict[str, Any]:
    """Get scan status asynchronously"""
    return await orchestrator.get_scan_status(scan_id)
