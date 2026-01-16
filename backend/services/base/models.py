from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from enum import Enum


class ScanStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class ScanRequest(BaseModel):
    target: str
    options: Optional[Dict[str, Any]] = {}


class ScanResponse(BaseModel):
    scan_id: str
    status: ScanStatus


class ScanStatusResponse(BaseModel):
    scan_id: str
    status: ScanStatus
    progress: Optional[int] = None
    message: Optional[str] = None


class Finding(BaseModel):
    severity: str
    title: str
    description: str
    details: Optional[Dict[str, Any]] = None


class ScanResultsResponse(BaseModel):
    scan_id: str
    status: ScanStatus
    findings: List[Finding] = []
    raw_output: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class HealthResponse(BaseModel):
    service: str
    status: str
    version: str = "1.0.0"
