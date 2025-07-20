"""
FortiGate Network Monitor Pro - Enhanced Device Intelligence
OUI Lookup and Device Classification Module
"""

import json
import requests
from typing import Dict, List, Optional, Tuple
import re

class DeviceIntelligence:
    def __init__(self):
        self.oui_database = {}
        self.device_icons = {}
        self.load_oui_database()
        self.load_device_icons()
    
    def load_oui_database(self):
        """Load OUI database for manufacturer lookup"""
        # This would typically load from a local OUI database file
        # For demo, including common network device OUIs
        self.oui_database = {
            # Fortinet
            "00:09:0F": {"manufacturer": "Fortinet", "type": "network_security"},
            "90:6C:AC": {"manufacturer": "Fortinet", "type": "network_security"},
            "00:90:7F": {"manufacturer": "Fortinet", "type": "network_security"},
            
            # Cisco
            "00:1B:0D": {"manufacturer": "Cisco", "type": "network_equipment"},
            "00:1E:13": {"manufacturer": "Cisco", "type": "network_equipment"}, 
            "00:23:EA": {"manufacturer": "Cisco", "type": "network_equipment"},
            "B8:BE:BF": {"manufacturer": "Cisco", "type": "network_equipment"},
            
            # HP/HPE
            "00:1B:78": {"manufacturer": "HP", "type": "network_equipment"},
            "94:57:A5": {"manufacturer": "HPE", "type": "network_equipment"},
            "80:C1:6E": {"manufacturer": "HPE", "type": "server"},
            
            # Dell
            "00:14:22": {"manufacturer": "Dell", "type": "server"},
            "90:B1:1C": {"manufacturer": "Dell", "type": "server"},
            "B0:83:FE": {"manufacturer": "Dell", "type": "server"},
            
            # Apple
            "00:1B:63": {"manufacturer": "Apple", "type": "endpoint"},
            "A8:96:75": {"manufacturer": "Apple", "type": "endpoint"},
            "F4:F1:5A": {"manufacturer": "Apple", "type": "endpoint"},
            
            # Microsoft
            "00:12:5A": {"manufacturer": "Microsoft", "type": "endpoint"},
            "7C:ED:8D": {"manufacturer": "Microsoft", "type": "endpoint"},
            
            # Ubiquiti
            "00:15:6D": {"manufacturer": "Ubiquiti", "type": "network_equipment"},
            "24:A4:3C": {"manufacturer": "Ubiquiti", "type": "network_equipment"},
            "F0:9F:C2": {"manufacturer": "Ubiquiti", "type": "network_equipment"},
            
            # Netgear
            "00:09:5B": {"manufacturer": "Netgear", "type": "network_equipment"},
            "20:4E:7F": {"manufacturer": "Netgear", "type": "network_equipment"},
            
            # Common Printer OUIs
            "00:11:85": {"manufacturer": "Canon", "type": "printer"},
            "00:1E:8F": {"manufacturer": "Canon", "type": "printer"},
            "00:0D:9A": {"manufacturer": "Brother", "type": "printer"},
            "00:80:92": {"manufacturer": "Brother", "type": "printer"},
            "00:80:77": {"manufacturer": "Brother", "type": "printer"},
            "18:A6:05": {"manufacturer": "Epson", "type": "printer"},
            "00:00:48": {"manufacturer": "Epson", "type": "printer"},
            "00:80:91": {"manufacturer": "Epson", "type": "printer"},
            "00:01:E3": {"manufacturer": "HP", "type": "printer"},
            "D4:C9:EF": {"manufacturer": "HP", "type": "printer"},
            
            # IoT Devices
            "B4:E6:2D": {"manufacturer": "Raspberry Pi", "type": "iot"},
            "DC:A6:32": {"manufacturer": "Raspberry Pi", "type": "iot"},
            "E4:5F:01": {"manufacturer": "Raspberry Pi", "type": "iot"},
            
            # Mobile Devices
            "40:B0:FA": {"manufacturer": "Samsung", "type": "mobile"},
            "E8:99:C4": {"manufacturer": "Samsung", "type": "mobile"},
            "20:02:AF": {"manufacturer": "Samsung", "type": "mobile"},
        }
    
    def load_device_icons(self):
        """Load device icon mappings"""
        self.device_icons = {
            # Network Security
            "fortigate": "fas fa-shield-alt",
            "fortiswitch": "fas fa-network-wired", 
            "fortinet": "fas fa-shield-alt",
            "firewall": "fas fa-fire-flame-curved",
            
            # Network Equipment
            "cisco_router": "fas fa-route",
            "cisco_switch": "fas fa-network-wired",
            "ubiquiti_ap": "fas fa-wifi",
            "ubiquiti_switch": "fas fa-network-wired",
            "netgear_router": "fas fa-route",
            "hp_switch": "fas fa-network-wired",
            
            # Servers
            "dell_server": "fas fa-server",
            "hp_server": "fas fa-server", 
            "hpe_server": "fas fa-server",
            "generic_server": "fas fa-server",
            
            # Endpoints
            "apple_mac": "fab fa-apple",
            "apple_iphone": "fas fa-mobile-alt",
            "apple_ipad": "fas fa-tablet-alt",
            "microsoft_surface": "fab fa-microsoft",
            "windows_pc": "fab fa-windows",
            "generic_laptop": "fas fa-laptop",
            "generic_desktop": "fas fa-desktop",
            
            # Printers
            "canon_printer": "fas fa-print",
            "brother_printer": "fas fa-print",
            "epson_printer": "fas fa-print", 
            "hp_printer": "fas fa-print",
            "generic_printer": "fas fa-print",
            
            # IoT
            "raspberry_pi": "fab fa-raspberry-pi",
            "iot_sensor": "fas fa-microchip",
            "smart_camera": "fas fa-video",
            "generic_iot": "fas fa-microchip",
            
            # Mobile
            "samsung_phone": "fas fa-mobile-alt",
            "android_tablet": "fas fa-tablet-alt",
            "generic_mobile": "fas fa-mobile-alt",
            
            # Unknown/Default
            "unknown": "fas fa-question-circle",
            "generic": "fas fa-desktop"
        }
    
    def lookup_oui(self, mac_address: str) -> Dict[str, str]:
        """
        Lookup device manufacturer and type based on MAC address OUI
        
        Args:
            mac_address: MAC address in format XX:XX:XX:XX:XX:XX
            
        Returns:
            Dict with manufacturer, type, and icon information
        """
        if not mac_address:
            return self._get_unknown_device()
            
        # Extract OUI (first 3 octets)
        mac_clean = mac_address.upper().replace("-", ":").replace(".", ":")
        oui = ":".join(mac_clean.split(":")[:3])
        
        if oui in self.oui_database:
            device_info = self.oui_database[oui].copy()
            device_info["icon"] = self._get_device_icon(
                device_info["manufacturer"], 
                device_info["type"]
            )
            device_info["confidence"] = "high"
            return device_info
        
        # Try online OUI lookup as fallback
        online_info = self._online_oui_lookup(oui)
        if online_info:
            return online_info
            
        return self._get_unknown_device()
    
    def _online_oui_lookup(self, oui: str) -> Optional[Dict[str, str]]:
        """Fallback to online OUI lookup"""
        try:
            # Using IEEE OUI lookup (replace with your preferred service)
            response = requests.get(
                f"https://api.macvendors.com/{oui}",
                timeout=2
            )
            if response.status_code == 200:
                manufacturer = response.text.strip()
                device_type = self._infer_device_type(manufacturer)
                return {
                    "manufacturer": manufacturer,
                    "type": device_type,
                    "icon": self._get_device_icon(manufacturer, device_type),
                    "confidence": "medium"
                }
        except:
            pass
        
        return None
    
    def _infer_device_type(self, manufacturer: str) -> str:
        """Infer device type from manufacturer name"""
        manufacturer_lower = manufacturer.lower()
        
        # Network security
        if any(term in manufacturer_lower for term in ["fortinet", "palo alto", "checkpoint"]):
            return "network_security"
            
        # Network equipment
        if any(term in manufacturer_lower for term in ["cisco", "juniper", "ubiquiti", "netgear", "linksys"]):
            return "network_equipment"
            
        # Servers
        if any(term in manufacturer_lower for term in ["dell", "hp", "hpe", "supermicro"]):
            return "server"
            
        # Printers
        if any(term in manufacturer_lower for term in ["canon", "brother", "epson", "xerox"]):
            return "printer"
            
        # Mobile/tablets
        if any(term in manufacturer_lower for term in ["samsung", "xiaomi", "huawei"]):
            return "mobile"
            
        # IoT
        if any(term in manufacturer_lower for term in ["raspberry", "arduino", "espressif"]):
            return "iot"
            
        # Default to endpoint
        return "endpoint"
    
    def _get_device_icon(self, manufacturer: str, device_type: str) -> str:
        """Get appropriate icon for device"""
        manufacturer_lower = manufacturer.lower()
        
        # Specific manufacturer + type combinations
        if "fortinet" in manufacturer_lower:
            return self.device_icons.get("fortinet", "fas fa-shield-alt")
        elif "cisco" in manufacturer_lower and device_type == "network_equipment":
            return self.device_icons.get("cisco_switch", "fas fa-network-wired")
        elif "apple" in manufacturer_lower:
            return self.device_icons.get("apple_mac", "fab fa-apple")
        elif "microsoft" in manufacturer_lower:
            return self.device_icons.get("microsoft_surface", "fab fa-microsoft")
        elif "raspberry" in manufacturer_lower:
            return self.device_icons.get("raspberry_pi", "fab fa-raspberry-pi")
        
        # Fallback to device type
        type_icons = {
            "network_security": "fas fa-shield-alt",
            "network_equipment": "fas fa-network-wired",
            "server": "fas fa-server",
            "endpoint": "fas fa-laptop",
            "printer": "fas fa-print",
            "mobile": "fas fa-mobile-alt",
            "iot": "fas fa-microchip"
        }
        
        return type_icons.get(device_type, "fas fa-question-circle")
    
    def _get_unknown_device(self) -> Dict[str, str]:
        """Return default info for unknown devices"""
        return {
            "manufacturer": "Unknown",
            "type": "unknown",
            "icon": "fas fa-question-circle",
            "confidence": "none"
        }
    
    def classify_device(self, mac_address: str, ip_address: str = None, 
                       hostname: str = None, ports: List[int] = None) -> Dict[str, str]:
        """
        Enhanced device classification using multiple data points
        
        Args:
            mac_address: Device MAC address
            ip_address: Device IP address
            hostname: Device hostname (if available)
            ports: Open ports (if port scan performed)
            
        Returns:
            Comprehensive device classification
        """
        # Start with OUI lookup
        device_info = self.lookup_oui(mac_address)
        
        # Enhance with hostname analysis
        if hostname:
            hostname_info = self._analyze_hostname(hostname)
            if hostname_info:
                device_info.update(hostname_info)
        
        # Enhance with port analysis
        if ports:
            port_info = self._analyze_ports(ports)
            if port_info:
                device_info.update(port_info)
        
        # Add display properties
        device_info["display_name"] = self._generate_display_name(device_info, hostname)
        device_info["css_class"] = self._get_css_class(device_info["type"])
        device_info["risk_level"] = self._assess_risk_level(device_info, ports)
        
        return device_info
    
    def _analyze_hostname(self, hostname: str) -> Optional[Dict[str, str]]:
        """Analyze hostname for device type clues"""
        hostname_lower = hostname.lower()
        
        # Network equipment patterns
        if any(pattern in hostname_lower for pattern in ["switch", "router", "ap-", "wap"]):
            return {"type": "network_equipment", "hostname_hint": "network_device"}
            
        # Server patterns
        if any(pattern in hostname_lower for pattern in ["server", "srv", "db", "web", "mail"]):
            return {"type": "server", "hostname_hint": "server"}
            
        # Printer patterns
        if any(pattern in hostname_lower for pattern in ["print", "hp-", "canon", "brother"]):
            return {"type": "printer", "hostname_hint": "printer"}
            
        return None
    
    def _analyze_ports(self, ports: List[int]) -> Optional[Dict[str, str]]:
        """Analyze open ports for device type clues"""
        # Web servers
        if 80 in ports or 443 in ports:
            return {"port_hint": "web_service"}
            
        # SSH servers
        if 22 in ports:
            return {"port_hint": "ssh_server"}
            
        # Printers
        if 631 in ports or 9100 in ports:
            return {"type": "printer", "port_hint": "printer"}
            
        # Network management
        if 161 in ports:  # SNMP
            return {"port_hint": "managed_device"}
            
        return None
    
    def _generate_display_name(self, device_info: Dict, hostname: str = None) -> str:
        """Generate user-friendly display name"""
        manufacturer = device_info.get("manufacturer", "Unknown")
        device_type = device_info.get("type", "Device")
        
        if hostname:
            return f"{hostname} ({manufacturer})"
        
        if manufacturer != "Unknown":
            return f"{manufacturer} {device_type.replace('_', ' ').title()}"
        
        return f"Unknown {device_type.replace('_', ' ').title()}"
    
    def _get_css_class(self, device_type: str) -> str:
        """Get CSS class for device styling"""
        css_classes = {
            "network_security": "device-icon fortigate",
            "network_equipment": "device-icon fortiswitch", 
            "server": "device-icon server",
            "endpoint": "device-icon endpoint",
            "printer": "device-icon printer",
            "mobile": "device-icon mobile",
            "iot": "device-icon iot",
            "unknown": "device-icon unknown"
        }
        return css_classes.get(device_type, "device-icon unknown")
    
    def _assess_risk_level(self, device_info: Dict, ports: List[int] = None) -> str:
        """Assess security risk level of device"""
        device_type = device_info.get("type", "unknown")
        manufacturer = device_info.get("manufacturer", "Unknown")
        
        # High risk: Unknown devices with open services
        if manufacturer == "Unknown" and ports and len(ports) > 5:
            return "high"
            
        # Medium risk: IoT devices, unknown devices
        if device_type in ["iot", "unknown"] or manufacturer == "Unknown":
            return "medium"
            
        # Low risk: Known network equipment, managed devices
        if device_type in ["network_security", "network_equipment"]:
            return "low"
            
        return "low"

# Usage example for integration
def enhance_device_discovery():
    """Example of how to integrate with existing FortiGate API calls"""
    intelligence = DeviceIntelligence()
    
    # Mock device data from FortiGate API
    devices = [
        {"mac": "90:6C:AC:12:34:56", "ip": "192.168.1.1", "hostname": "FortiGate-100F"},
        {"mac": "00:1B:0D:11:22:33", "ip": "192.168.1.2", "hostname": "Cisco-Switch-01"},
        {"mac": "B4:E6:2D:AA:BB:CC", "ip": "192.168.1.100", "hostname": "rpi-sensor-01"},
        {"mac": "00:11:85:DD:EE:FF", "ip": "192.168.1.50", "hostname": "Canon-Printer"}
    ]
    
    enhanced_devices = []
    for device in devices:
        enhanced = intelligence.classify_device(
            mac_address=device["mac"],
            ip_address=device["ip"], 
            hostname=device["hostname"]
        )
        enhanced.update(device)  # Merge with original data
        enhanced_devices.append(enhanced)
    
    return enhanced_devices

if __name__ == "__main__":
    # Demo the enhanced device classification
    devices = enhance_device_discovery()
    for device in devices:
        print(f"Device: {device['display_name']}")
        print(f"  Type: {device['type']} (Icon: {device['icon']})")
        print(f"  Risk: {device['risk_level']}")
        print(f"  CSS: {device['css_class']}")
        print()
