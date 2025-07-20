# Network scanning API endpoints
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Query
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
import logging

from core.device_intelligence import DeviceIntelligenceEngine
from main import get_intelligence_engine

router = APIRouter()
logger = logging.getLogger(__name__)

class ScanRequest(BaseModel):
    """Request model for network scanning"""
    target: str = Field(..., description="IP address, range, or hostname to scan")
    scan_type: str = Field(default="discovery", description="Type of scan: discovery, port, vulnerability")
    ports: Optional[List[int]] = Field(default=None, description="Specific ports to scan")
    timeout: int = Field(default=30, ge=1, le=300, description="Scan timeout in seconds")
    aggressive: bool = Field(default=False, description="Use aggressive scanning techniques")

class ScanResult(BaseModel):
    """Scan result model"""
    scan_id: str
    target: str
    scan_type: str
    status: str  # "running", "completed", "failed"
    started_at: str
    completed_at: Optional[str] = None
    devices_found: int = 0
    vulnerabilities_found: int = 0
    results: Dict[str, Any] = Field(default_factory=dict)

class ScanResponse(BaseModel):
    """Response model for scan operations"""
    success: bool
    message: str
    scan_result: Optional[ScanResult] = None
    scan_results: Optional[List[ScanResult]] = None

@router.post("/start", response_model=ScanResponse)
async def start_scan(
    scan_request: ScanRequest,
    background_tasks: BackgroundTasks,
    intelligence_engine: DeviceIntelligenceEngine = Depends(get_intelligence_engine)
):
    """Start a new network scan"""
    try:
        scan_id = await intelligence_engine.start_scan(
            target=scan_request.target,
            scan_type=scan_request.scan_type,
            ports=scan_request.ports,
            timeout=scan_request.timeout,
            aggressive=scan_request.aggressive
        )
        
        # Add background task to execute the scan
        background_tasks.add_task(
            intelligence_engine.execute_scan_background, 
            scan_id
        )
        
        scan_result = ScanResult(
            scan_id=scan_id,
            target=scan_request.target,
            scan_type=scan_request.scan_type,
            status="running",
            started_at=datetime.utcnow().isoformat()
        )
        
        return ScanResponse(
            success=True,
            message=f"Scan started successfully with ID: {scan_id}",
            scan_result=scan_result
        )
    except Exception as e:
        logger.error(f"Error starting scan: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error starting scan: {str(e)}")

@router.get("/{scan_id}", response_model=ScanResponse)
async def get_scan_status(
    scan_id: str,
    intelligence_engine: DeviceIntelligenceEngine = Depends(get_intelligence_engine)
):
    """Get the status and results of a specific scan"""
    try:
        scan_result = await intelligence_engine.get_scan_result(scan_id)
        
        if not scan_result:
            raise HTTPException(status_code=404, detail=f"Scan {scan_id} not found")
        
        return ScanResponse(
            success=True,
            message="Scan status retrieved successfully",
            scan_result=scan_result
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving scan {scan_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving scan: {str(e)}")

@router.get("/", response_model=ScanResponse)
async def get_all_scans(
    status: Optional[str] = Query(None, description="Filter by scan status"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of scans to return"),
    intelligence_engine: DeviceIntelligenceEngine = Depends(get_intelligence_engine)
):
    """Get all scans with optional filtering"""
    try:
        scan_results = await intelligence_engine.get_all_scans(status=status, limit=limit)
        
        return ScanResponse(
            success=True,
            message=f"Retrieved {len(scan_results)} scans",
            scan_results=scan_results
        )
    except Exception as e:
        logger.error(f"Error retrieving scans: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving scans: {str(e)}")

@router.delete("/{scan_id}", response_model=ScanResponse)
async def cancel_scan(
    scan_id: str,
    intelligence_engine: DeviceIntelligenceEngine = Depends(get_intelligence_engine)
):
    """Cancel a running scan"""
    try:
        success = await intelligence_engine.cancel_scan(scan_id)
        
        if not success:
            raise HTTPException(status_code=404, detail=f"Scan {scan_id} not found or cannot be cancelled")
        
        return ScanResponse(
            success=True,
            message=f"Scan {scan_id} cancelled successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling scan {scan_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error cancelling scan: {str(e)}")

@router.post("/network-discovery", response_model=ScanResponse)
async def discover_network(
    network_range: str = Query(..., description="Network range to discover (e.g., 192.168.1.0/24)"),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    intelligence_engine: DeviceIntelligenceEngine = Depends(get_intelligence_engine)
):
    """Discover all devices in a network range"""
    try:
        scan_request = ScanRequest(
            target=network_range,
            scan_type="discovery",
            timeout=60
        )
        
        scan_id = await intelligence_engine.start_scan(
            target=scan_request.target,
            scan_type=scan_request.scan_type,
            timeout=scan_request.timeout
        )
        
        background_tasks.add_task(
            intelligence_engine.execute_scan_background,
            scan_id
        )
        
        scan_result = ScanResult(
            scan_id=scan_id,
            target=network_range,
            scan_type="discovery",
            status="running",
            started_at=datetime.utcnow().isoformat()
        )
        
        return ScanResponse(
            success=True,
            message=f"Network discovery started for {network_range}",
            scan_result=scan_result
        )
    except Exception as e:
        logger.error(f"Error starting network discovery: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error starting network discovery: {str(e)}")

@router.post("/vulnerability-scan", response_model=ScanResponse)
async def vulnerability_scan(
    target: str = Query(..., description="Target IP or hostname for vulnerability scan"),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    intelligence_engine: DeviceIntelligenceEngine = Depends(get_intelligence_engine)
):
    """Perform a vulnerability scan on a specific target"""
    try:
        scan_request = ScanRequest(
            target=target,
            scan_type="vulnerability",
            timeout=180,
            aggressive=True
        )
        
        scan_id = await intelligence_engine.start_scan(
            target=scan_request.target,
            scan_type=scan_request.scan_type,
            timeout=scan_request.timeout,
            aggressive=scan_request.aggressive
        )
        
        background_tasks.add_task(
            intelligence_engine.execute_scan_background,
            scan_id
        )
        
        scan_result = ScanResult(
            scan_id=scan_id,
            target=target,
            scan_type="vulnerability",
            status="running",
            started_at=datetime.utcnow().isoformat()
        )
        
        return ScanResponse(
            success=True,
            message=f"Vulnerability scan started for {target}",
            scan_result=scan_result
        )
    except Exception as e:
        logger.error(f"Error starting vulnerability scan: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error starting vulnerability scan: {str(e)}")
