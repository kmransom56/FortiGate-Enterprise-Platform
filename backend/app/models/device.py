# Device data models for FortiGate Network Monitor Pro
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class DeviceType(str, Enum):
    """Device type enumeration"""
    ROUTER = "router"
    SWITCH = "switch" 
    FIREWALL = "firewall"
    ACCESS_POINT = "access_point"
    SERVER = "server"
    WORKSTATION = "workstation"
    PRINTER = "printer"
    IOT_DEVICE = "iot_device"
    MOBILE_DEVICE = "mobile_device"
    UNKNOWN = "unknown"

class DeviceStatus(str, Enum):
    """Device status enumeration"""
    ONLINE = "online"
    OFFLINE = "offline"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"

class OperatingSystem(BaseModel):
    """Operating system information"""
    name: Optional[str] = None
    version: Optional[str] = None
    family: Optional[str] = None  # e.g., "Windows", "Linux", "iOS"
    confidence: float = 0.0  # Confidence score 0-1
    
class NetworkInterface(BaseModel):
    """Network interface information"""
    ip_address: str
    mac_address: Optional[str] = None
    interface_name: Optional[str] = None
    is_primary: bool = False
    
class DeviceVulnerability(BaseModel):
    """Device vulnerability information"""
    cve_id: str
    severity: str  # "critical", "high", "medium", "low"
    score: float  # CVSS score
    description: str
    affected_software: Optional[str] = None
    patch_available: bool = False
    discovered_at: datetime = Field(default_factory=datetime.utcnow)
class Device(BaseModel):
    """Main device model with comprehensive information"""
    
    # Basic identification
    device_id: str = Field(..., description="Unique device identifier")
    hostname: Optional[str] = None
    device_name: Optional[str] = None
    device_type: DeviceType = DeviceType.UNKNOWN
    status: DeviceStatus = DeviceStatus.UNKNOWN
    
    # Network information  
    interfaces: List[NetworkInterface] = Field(default_factory=list)
    primary_ip: Optional[str] = None
    primary_mac: Optional[str] = None
    
    # Hardware information
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    hardware_version: Optional[str] = None
    
    # Software information
    operating_system: Optional[OperatingSystem] = None
    firmware_version: Optional[str] = None
    software_version: Optional[str] = None
    
    # Security information
    vulnerabilities: List[DeviceVulnerability] = Field(default_factory=list)
    security_score: float = 0.0  # Overall security score 0-100
    last_security_scan: Optional[datetime] = None
    
    # Network behavior
    open_ports: List[int] = Field(default_factory=list)
    services: List[str] = Field(default_factory=list)
    protocols: List[str] = Field(default_factory=list)
    
    # Discovery and monitoring
    first_seen: datetime = Field(default_factory=datetime.utcnow)
    last_seen: datetime = Field(default_factory=datetime.utcnow)
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    scan_count: int = 0
    
    # Additional metadata
    tags: List[str] = Field(default_factory=list)
    notes: Optional[str] = None
    custom_fields: Dict[str, Any] = Field(default_factory=dict)
    
    # Power Automate integration fields
    power_automate_triggered: bool = False
    power_automate_actions: List[str] = Field(default_factory=list)
    
    model_config = ConfigDict(from_attributes=True)
    
    def get_primary_interface(self) -> Optional[NetworkInterface]:
        """Get the primary network interface"""
        for interface in self.interfaces:
            if interface.is_primary:
                return interface
        return self.interfaces[0] if self.interfaces else None
    
    def add_vulnerability(self, vulnerability: DeviceVulnerability) -> None:
        """Add a vulnerability to the device"""
        self.vulnerabilities.append(vulnerability)
        self.calculate_security_score()
    
    def calculate_security_score(self) -> float:
        """Calculate overall security score based on vulnerabilities"""
        if not self.vulnerabilities:
            self.security_score = 100.0
            return self.security_score
        
        # Calculate weighted score based on vulnerability severity
        total_impact = 0.0
        weights = {"critical": 10, "high": 7, "medium": 4, "low": 1}
        
        for vuln in self.vulnerabilities:
            weight = weights.get(vuln.severity.lower(), 1)
            total_impact += weight
        
        # Convert to score (higher is better)
        self.security_score = max(0, 100 - min(total_impact * 2, 100))
        return self.security_score

class DeviceCreate(BaseModel):
    """Model for creating new devices"""
    hostname: Optional[str] = None
    device_name: Optional[str] = None
    primary_ip: str
    primary_mac: Optional[str] = None
    device_type: DeviceType = DeviceType.UNKNOWN

class DeviceUpdate(BaseModel):
    """Model for updating devices"""
    hostname: Optional[str] = None
    device_name: Optional[str] = None
    device_type: Optional[DeviceType] = None
    status: Optional[DeviceStatus] = None
    tags: Optional[List[str]] = None
    notes: Optional[str] = None
    custom_fields: Optional[Dict[str, Any]] = None

class DeviceResponse(BaseModel):
    """Response model for device API calls"""
    success: bool
    message: str
    device: Optional[Device] = None
    devices: Optional[List[Device]] = None
    count: Optional[int] = None
