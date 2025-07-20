# Device API endpoints for FortiGate Network Monitor Pro
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from datetime import datetime
import logging

from models.device import (
    Device, DeviceCreate, DeviceUpdate, DeviceResponse, 
    DeviceType, DeviceStatus
)
from core.device_intelligence import DeviceIntelligenceEngine
from main import get_intelligence_engine

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/", response_model=DeviceResponse)
async def get_all_devices(
    skip: int = Query(0, ge=0, description="Number of devices to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of devices to return"),
    device_type: Optional[DeviceType] = Query(None, description="Filter by device type"),
    status: Optional[DeviceStatus] = Query(None, description="Filter by device status"),
    intelligence_engine: DeviceIntelligenceEngine = Depends(get_intelligence_engine)
):
    """Get all devices with optional filtering and pagination"""
    try:
        devices = await intelligence_engine.get_all_devices(
            skip=skip, 
            limit=limit,
            device_type=device_type,
            status=status
        )
        
        return DeviceResponse(
            success=True,
            message=f"Retrieved {len(devices)} devices",
            devices=devices,
            count=len(devices)
        )
    except Exception as e:
        logger.error(f"Error retrieving devices: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving devices: {str(e)}")

@router.get("/{device_id}", response_model=DeviceResponse)
async def get_device(
    device_id: str,
    intelligence_engine: DeviceIntelligenceEngine = Depends(get_intelligence_engine)
):
    """Get a specific device by ID"""
    try:
        device = await intelligence_engine.get_device(device_id)
        
        if not device:
            raise HTTPException(status_code=404, detail=f"Device {device_id} not found")
        
        return DeviceResponse(
            success=True,
            message="Device retrieved successfully",
            device=device
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving device {device_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving device: {str(e)}")
@router.post("/", response_model=DeviceResponse)
async def create_device(
    device_data: DeviceCreate,
    intelligence_engine: DeviceIntelligenceEngine = Depends(get_intelligence_engine)
):
    """Create a new device"""
    try:
        device = await intelligence_engine.create_device(device_data)
        
        return DeviceResponse(
            success=True,
            message="Device created successfully",
            device=device
        )
    except Exception as e:
        logger.error(f"Error creating device: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating device: {str(e)}")

@router.put("/{device_id}", response_model=DeviceResponse)
async def update_device(
    device_id: str,
    device_data: DeviceUpdate,
    intelligence_engine: DeviceIntelligenceEngine = Depends(get_intelligence_engine)
):
    """Update an existing device"""
    try:
        device = await intelligence_engine.update_device(device_id, device_data)
        
        if not device:
            raise HTTPException(status_code=404, detail=f"Device {device_id} not found")
        
        return DeviceResponse(
            success=True,
            message="Device updated successfully",
            device=device
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating device {device_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating device: {str(e)}")

@router.delete("/{device_id}", response_model=DeviceResponse)
async def delete_device(
    device_id: str,
    intelligence_engine: DeviceIntelligenceEngine = Depends(get_intelligence_engine)
):
    """Delete a device"""
    try:
        success = await intelligence_engine.delete_device(device_id)
        
        if not success:
            raise HTTPException(status_code=404, detail=f"Device {device_id} not found")
        
        return DeviceResponse(
            success=True,
            message="Device deleted successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting device {device_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error deleting device: {str(e)}")

@router.post("/{device_id}/scan", response_model=DeviceResponse)
async def scan_device(
    device_id: str,
    intelligence_engine: DeviceIntelligenceEngine = Depends(get_intelligence_engine)
):
    """Trigger a security scan for a specific device"""
    try:
        device = await intelligence_engine.scan_device(device_id)
        
        if not device:
            raise HTTPException(status_code=404, detail=f"Device {device_id} not found")
        
        return DeviceResponse(
            success=True,
            message="Device scan completed successfully",
            device=device
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error scanning device {device_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error scanning device: {str(e)}")

@router.post("/{device_id}/power-automate", response_model=DeviceResponse)
async def trigger_power_automate(
    device_id: str,
    action: str = Query(..., description="Power Automate action to trigger"),
    intelligence_engine: DeviceIntelligenceEngine = Depends(get_intelligence_engine)
):
    """Trigger Power Automate workflow for a device"""
    try:
        success = await intelligence_engine.trigger_power_automate(device_id, action)
        
        if not success:
            raise HTTPException(status_code=404, detail=f"Device {device_id} not found or Power Automate failed")
        
        return DeviceResponse(
            success=True,
            message=f"Power Automate action '{action}' triggered successfully for device {device_id}"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error triggering Power Automate for device {device_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error triggering Power Automate: {str(e)}")

@router.get("/statistics/summary")
async def get_device_statistics(
    intelligence_engine: DeviceIntelligenceEngine = Depends(get_intelligence_engine)
):
    """Get device statistics summary"""
    try:
        stats = await intelligence_engine.get_device_statistics()
        
        return {
            "success": True,
            "message": "Statistics retrieved successfully",
            "statistics": stats
        }
    except Exception as e:
        logger.error(f"Error retrieving device statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving statistics: {str(e)}")
