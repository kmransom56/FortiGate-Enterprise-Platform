# Core Device Intelligence Engine for FortiGate Network Monitor Pro
import asyncio
import logging
import uuid
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import json

from models.device import (
    Device, DeviceCreate, DeviceUpdate, DeviceType, DeviceStatus,
    NetworkInterface, OperatingSystem, DeviceVulnerability
)
from core.network_scanner import NetworkScanner
from core.oui_database import OUIDatabase
from core.advanced_detection import AdvancedDetection
from services.power_automate_service import PowerAutomateService
from config import settings

logger = logging.getLogger(__name__)

class DeviceIntelligenceEngine:
    """
    Core intelligence engine for device discovery, classification, and monitoring
    """
    
    def __init__(self):
        self.devices: Dict[str, Device] = {}
        self.scan_results: Dict[str, Dict] = {}
        self.network_scanner = NetworkScanner()
        self.oui_database = OUIDatabase()
        self.advanced_detection = AdvancedDetection()
        self.power_automate = PowerAutomateService()
        self.is_initialized = False
        self._running_scans: Dict[str, asyncio.Task] = {}
        
    async def initialize(self) -> None:
        """Initialize the intelligence engine and its components"""
        try:
            logger.info("Initializing Device Intelligence Engine...")
            
            # Initialize OUI database
            await self.oui_database.initialize()
            logger.info("OUI database initialized")
            
            # Initialize advanced detection
            await self.advanced_detection.initialize()
            logger.info("Advanced detection initialized")
            
            # Initialize Power Automate service
            if settings.POWER_AUTOMATE_ENABLED:
                await self.power_automate.initialize()
                logger.info("Power Automate service initialized")
            
            self.is_initialized = True
            logger.info("Device Intelligence Engine initialization complete")
            
        except Exception as e:
            logger.error(f"Failed to initialize Device Intelligence Engine: {str(e)}")
            raise
    
    def is_ready(self) -> bool:
        """Check if the engine is ready for operations"""
        return self.is_initialized
    
    async def shutdown(self) -> None:
        """Shutdown the intelligence engine and cleanup resources"""
        logger.info("Shutting down Device Intelligence Engine...")
        
        # Cancel all running scans
        for scan_id, task in self._running_scans.items():
            if not task.done():
                task.cancel()
                logger.info(f"Cancelled running scan: {scan_id}")
        
        # Clear resources
        self._running_scans.clear()
        
        logger.info("Device Intelligence Engine shutdown complete")
    
    # Device Management Methods
    
    async def get_all_devices(
        self, 
        skip: int = 0, 
        limit: int = 100, 
        device_type: Optional[DeviceType] = None,
        status: Optional[DeviceStatus] = None
    ) -> List[Device]:
        """Get all devices with optional filtering"""
        devices = list(self.devices.values())
        
        # Apply filters
        if device_type:
            devices = [d for d in devices if d.device_type == device_type]
        if status:
            devices = [d for d in devices if d.status == status]
        
        # Apply pagination
        return devices[skip:skip + limit]
    
    async def get_device(self, device_id: str) -> Optional[Device]:
        """Get a specific device by ID"""
        return self.devices.get(device_id)
    
    async def create_device(self, device_data: DeviceCreate) -> Device:
        """Create a new device"""
        device_id = str(uuid.uuid4())
        
        # Create primary interface
        primary_interface = NetworkInterface(
            ip_address=device_data.primary_ip,
            mac_address=device_data.primary_mac,
            is_primary=True
        )
        
        # Create device
        device = Device(
            device_id=device_id,
            hostname=device_data.hostname,
            device_name=device_data.device_name,
            device_type=device_data.device_type,
            primary_ip=device_data.primary_ip,
            primary_mac=device_data.primary_mac,
            interfaces=[primary_interface],
            status=DeviceStatus.UNKNOWN
        )
        
        # Classify device using manufacturer lookup
        if device_data.primary_mac:
            manufacturer = await self.oui_database.lookup_manufacturer(device_data.primary_mac)
            if manufacturer:
                device.manufacturer = manufacturer
                device.device_type = await self._classify_device_by_manufacturer(manufacturer)
        
        # Store device
        self.devices[device_id] = device
        
        logger.info(f"Created new device: {device_id} ({device_data.primary_ip})")
        
        # Trigger Power Automate if enabled
        if settings.POWER_AUTOMATE_ENABLED:
            await self.trigger_power_automate(device_id, "device_created")
        
        return device
    
    async def update_device(self, device_id: str, device_data: DeviceUpdate) -> Optional[Device]:
        """Update an existing device"""
        device = self.devices.get(device_id)
        if not device:
            return None
        
        # Update fields
        update_dict = device_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            if hasattr(device, field):
                setattr(device, field, value)
        
        device.last_updated = datetime.utcnow()
        
        logger.info(f"Updated device: {device_id}")
        return device
    
    async def delete_device(self, device_id: str) -> bool:
        """Delete a device"""
        if device_id in self.devices:
            del self.devices[device_id]
            logger.info(f"Deleted device: {device_id}")
            return True
        return False
    
    async def scan_device(self, device_id: str) -> Optional[Device]:
        """Perform a comprehensive scan of a specific device"""
        device = self.devices.get(device_id)
        if not device:
            return None
        
        try:
            # Perform network scan
            scan_result = await self.network_scanner.scan_host(
                device.primary_ip,
                timeout=settings.SCAN_TIMEOUT
            )
            
            # Update device with scan results
            if scan_result:
                device.open_ports = scan_result.get('open_ports', [])
                device.services = scan_result.get('services', [])
                device.status = DeviceStatus.ONLINE if scan_result.get('is_alive') else DeviceStatus.OFFLINE
                
                # OS detection
                os_info = scan_result.get('os_info')
                if os_info:
                    device.operating_system = OperatingSystem(
                        name=os_info.get('name'),
                        version=os_info.get('version'),
                        family=os_info.get('family'),
                        confidence=os_info.get('confidence', 0.0)
                    )
            
            # Vulnerability assessment
            vulnerabilities = await self.advanced_detection.scan_vulnerabilities(device.primary_ip)
            if vulnerabilities:
                device.vulnerabilities.extend(vulnerabilities)
                device.calculate_security_score()
            
            device.last_security_scan = datetime.utcnow()
            device.scan_count += 1
            device.last_updated = datetime.utcnow()
            
            logger.info(f"Scanned device: {device_id} - Found {len(device.open_ports)} open ports, {len(vulnerabilities)} vulnerabilities")
            
            # Trigger Power Automate for security events
            if vulnerabilities and settings.POWER_AUTOMATE_ENABLED:
                await self.trigger_power_automate(device_id, "vulnerabilities_detected")
            
            return device
            
        except Exception as e:
            logger.error(f"Error scanning device {device_id}: {str(e)}")
            device.status = DeviceStatus.UNKNOWN
            return device
    
    # Scanning Methods
    
    async def start_scan(
        self, 
        target: str, 
        scan_type: str = "discovery",
        ports: Optional[List[int]] = None,
        timeout: int = 30,
        aggressive: bool = False
    ) -> str:
        """Start a new network scan"""
        scan_id = str(uuid.uuid4())
        
        scan_data = {
            "scan_id": scan_id,
            "target": target,
            "scan_type": scan_type,
            "ports": ports,
            "timeout": timeout,
            "aggressive": aggressive,
            "status": "queued",
            "started_at": datetime.utcnow().isoformat(),
            "completed_at": None,
            "devices_found": 0,
            "vulnerabilities_found": 0,
            "results": {}
        }
        
        self.scan_results[scan_id] = scan_data
        logger.info(f"Queued scan: {scan_id} for target: {target}")
        
        return scan_id
    
    async def execute_scan_background(self, scan_id: str) -> None:
        """Execute a scan in the background"""
        scan_data = self.scan_results.get(scan_id)
        if not scan_data:
            logger.error(f"Scan {scan_id} not found")
            return
        
        try:
            scan_data["status"] = "running"
            logger.info(f"Starting scan execution: {scan_id}")
            
            if scan_data["scan_type"] == "discovery":
                await self._execute_discovery_scan(scan_id)
            elif scan_data["scan_type"] == "port":
                await self._execute_port_scan(scan_id)
            elif scan_data["scan_type"] == "vulnerability":
                await self._execute_vulnerability_scan(scan_id)
            else:
                raise ValueError(f"Unknown scan type: {scan_data['scan_type']}")
            
            scan_data["status"] = "completed"
            scan_data["completed_at"] = datetime.utcnow().isoformat()
            
            logger.info(f"Scan completed: {scan_id}")
            
        except Exception as e:
            logger.error(f"Scan {scan_id} failed: {str(e)}")
            scan_data["status"] = "failed"
            scan_data["error"] = str(e)
            scan_data["completed_at"] = datetime.utcnow().isoformat()
        
        finally:
            # Remove from running scans
            if scan_id in self._running_scans:
                del self._running_scans[scan_id]
    
    async def _execute_discovery_scan(self, scan_id: str) -> None:
        """Execute a network discovery scan"""
        scan_data = self.scan_results[scan_id]
        target = scan_data["target"]
        
        # Use network scanner to discover devices
        discovered_hosts = await self.network_scanner.discover_network(
            target, 
            timeout=scan_data["timeout"]
        )
        
        devices_found = 0
        for host_info in discovered_hosts:
            # Create or update device
            device_id = await self._create_or_update_device_from_scan(host_info)
            if device_id:
                devices_found += 1
        
        scan_data["devices_found"] = devices_found
        scan_data["results"] = {
            "discovered_hosts": len(discovered_hosts),
            "devices_created": devices_found,
            "scan_range": target
        }
    
    async def _execute_vulnerability_scan(self, scan_id: str) -> None:
        """Execute a vulnerability scan"""
        scan_data = self.scan_results[scan_id]
        target = scan_data["target"]
        
        # First do a basic port scan
        port_results = await self.network_scanner.scan_host(
            target,
            timeout=scan_data["timeout"]
        )
        
        vulnerabilities_found = 0
        if port_results and port_results.get("is_alive"):
            # Scan for vulnerabilities
            vulnerabilities = await self.advanced_detection.scan_vulnerabilities(target)
            vulnerabilities_found = len(vulnerabilities)
            
            # Update or create device with vulnerabilities
            device = await self._find_device_by_ip(target)
            if device:
                device.vulnerabilities.extend(vulnerabilities)
                device.calculate_security_score()
                
                # Trigger Power Automate for critical vulnerabilities
                critical_vulns = [v for v in vulnerabilities if v.severity == "critical"]
                if critical_vulns and settings.POWER_AUTOMATE_ENABLED:
                    await self.trigger_power_automate(device.device_id, "critical_vulnerabilities_detected")
        
        scan_data["vulnerabilities_found"] = vulnerabilities_found
        scan_data["results"] = {
            "target": target,
            "vulnerabilities": vulnerabilities_found,
            "port_scan": port_results
        }
    
    async def get_scan_result(self, scan_id: str) -> Optional[Dict]:
        """Get scan result by ID"""
        return self.scan_results.get(scan_id)
    
    async def get_all_scans(self, status: Optional[str] = None, limit: int = 50) -> List[Dict]:
        """Get all scan results with optional filtering"""
        scans = list(self.scan_results.values())
        
        if status:
            scans = [s for s in scans if s.get("status") == status]
        
        # Sort by start time (newest first)
        scans.sort(key=lambda x: x.get("started_at", ""), reverse=True)
        
        return scans[:limit]
    
    async def cancel_scan(self, scan_id: str) -> bool:
        """Cancel a running scan"""
        if scan_id in self._running_scans:
            task = self._running_scans[scan_id]
            if not task.done():
                task.cancel()
                
                # Update scan status
                if scan_id in self.scan_results:
                    self.scan_results[scan_id]["status"] = "cancelled"
                    self.scan_results[scan_id]["completed_at"] = datetime.utcnow().isoformat()
                
                logger.info(f"Cancelled scan: {scan_id}")
                return True
        
        return False
    
    # Power Automate Integration
    
    async def trigger_power_automate(self, device_id: str, action: str) -> bool:
        """Trigger Power Automate workflow for a device"""
        if not settings.POWER_AUTOMATE_ENABLED:
            logger.warning("Power Automate is not enabled")
            return False
        
        device = self.devices.get(device_id)
        if not device:
            logger.error(f"Device {device_id} not found for Power Automate trigger")
            return False
        
        try:
            # Prepare payload for Power Automate
            payload = {
                "device_id": device_id,
                "action": action,
                "timestamp": datetime.utcnow().isoformat(),
                "device_info": {
                    "hostname": device.hostname,
                    "ip_address": device.primary_ip,
                    "mac_address": device.primary_mac,
                    "device_type": device.device_type.value,
                    "status": device.status.value,
                    "manufacturer": device.manufacturer,
                    "security_score": device.security_score
                }
            }
            
            # Add vulnerability information for security actions
            if action in ["vulnerabilities_detected", "critical_vulnerabilities_detected"]:
                payload["vulnerabilities"] = [
                    {
                        "cve_id": v.cve_id,
                        "severity": v.severity,
                        "score": v.score,
                        "description": v.description
                    }
                    for v in device.vulnerabilities
                ]
            
            # Send to Power Automate
            success = await self.power_automate.trigger_workflow(action, payload)
            
            if success:
                device.power_automate_triggered = True
                device.power_automate_actions.append(f"{action}:{datetime.utcnow().isoformat()}")
                logger.info(f"Power Automate triggered for device {device_id}: {action}")
            else:
                logger.error(f"Failed to trigger Power Automate for device {device_id}: {action}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error triggering Power Automate for device {device_id}: {str(e)}")
            return False
    
    # Utility Methods
    
    async def get_device_statistics(self) -> Dict[str, Any]:
        """Get comprehensive device statistics"""
        total_devices = len(self.devices)
        if total_devices == 0:
            return {
                "total_devices": 0,
                "device_types": {},
                "status_distribution": {},
                "security_summary": {},
                "recent_activity": {}
            }
        
        # Device type distribution
        device_types = {}
        status_distribution = {}
        security_scores = []
        vulnerabilities_count = 0
        
        for device in self.devices.values():
            # Device types
            device_type = device.device_type.value
            device_types[device_type] = device_types.get(device_type, 0) + 1
            
            # Status distribution
            status = device.status.value
            status_distribution[status] = status_distribution.get(status, 0) + 1
            
            # Security metrics
            security_scores.append(device.security_score)
            vulnerabilities_count += len(device.vulnerabilities)
        
        # Calculate security summary
        avg_security_score = sum(security_scores) / len(security_scores) if security_scores else 0
        critical_devices = len([d for d in self.devices.values() if d.security_score < 50])
        
        # Recent activity
        recent_scans = len([s for s in self.scan_results.values() 
                          if datetime.fromisoformat(s.get("started_at", "1970-01-01T00:00:00")) 
                          > datetime.utcnow() - timedelta(hours=24)])
        
        return {
            "total_devices": total_devices,
            "device_types": device_types,
            "status_distribution": status_distribution,
            "security_summary": {
                "average_security_score": round(avg_security_score, 2),
                "total_vulnerabilities": vulnerabilities_count,
                "critical_devices": critical_devices,
                "devices_at_risk": len([d for d in self.devices.values() if len(d.vulnerabilities) > 0])
            },
            "recent_activity": {
                "scans_last_24h": recent_scans,
                "power_automate_triggers": len([d for d in self.devices.values() if d.power_automate_triggered])
            }
        }
    
    async def _classify_device_by_manufacturer(self, manufacturer: str) -> DeviceType:
        """Classify device type based on manufacturer"""
        manufacturer_lower = manufacturer.lower()
        
        # Router manufacturers
        if any(name in manufacturer_lower for name in ['cisco', 'juniper', 'fortinet', 'palo alto']):
            return DeviceType.ROUTER
        
        # Printer manufacturers
        if any(name in manufacturer_lower for name in ['hp', 'canon', 'epson', 'brother']):
            return DeviceType.PRINTER
        
        # IoT device indicators
        if any(name in manufacturer_lower for name in ['nest', 'ring', 'philips hue', 'iot']):
            return DeviceType.IOT_DEVICE
        
        # Mobile device manufacturers
        if any(name in manufacturer_lower for name in ['apple', 'samsung', 'google']):
            return DeviceType.MOBILE_DEVICE
        
        return DeviceType.UNKNOWN
    
    async def _create_or_update_device_from_scan(self, host_info: Dict) -> Optional[str]:
        """Create or update a device from scan results"""
        ip_address = host_info.get("ip")
        if not ip_address:
            return None
        
        # Check if device already exists
        existing_device = await self._find_device_by_ip(ip_address)
        
        if existing_device:
            # Update existing device
            existing_device.last_seen = datetime.utcnow()
            existing_device.status = DeviceStatus.ONLINE if host_info.get("is_alive") else DeviceStatus.OFFLINE
            
            # Update ports and services
            if "open_ports" in host_info:
                existing_device.open_ports = host_info["open_ports"]
            if "services" in host_info:
                existing_device.services = host_info["services"]
            
            return existing_device.device_id
        else:
            # Create new device
            device_data = DeviceCreate(
                primary_ip=ip_address,
                primary_mac=host_info.get("mac"),
                hostname=host_info.get("hostname"),
                device_type=DeviceType.UNKNOWN
            )
            
            device = await self.create_device(device_data)
            return device.device_id
    
    async def _find_device_by_ip(self, ip_address: str) -> Optional[Device]:
        """Find a device by its IP address"""
        for device in self.devices.values():
            if device.primary_ip == ip_address:
                return device
            # Also check secondary interfaces
            for interface in device.interfaces:
                if interface.ip_address == ip_address:
                    return device
        return None
