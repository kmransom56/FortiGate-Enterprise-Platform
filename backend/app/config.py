# Configuration settings for FortiGate Network Monitor Pro
from pydantic_settings import BaseSettings
from typing import List, Optional
import os

class Settings(BaseSettings):
    """Application configuration settings"""
    
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "FortiGate Network Monitor Pro"
    VERSION: str = "1.0.0"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000", 
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000"
    ]
    
    # Database
    DATABASE_URL: str = "postgresql://admin:password@localhost:5432/fortigate_monitor"
    
    # Network Scanning
    SCAN_TIMEOUT: int = 30
    MAX_CONCURRENT_SCANS: int = 100
    DEFAULT_SCAN_RANGE: str = "192.168.1.0/24"
    
    # Power Automate Integration
    POWER_AUTOMATE_WEBHOOK_URL: Optional[str] = None
    POWER_AUTOMATE_ENABLED: bool = False
    
    # External Services
    VULNERABILITY_DATABASE_URL: str = "https://nvd.nist.gov/feeds/json/cve/1.1/"
    OUI_DATABASE_URL: str = "https://standards-oui.ieee.org/oui/oui.txt"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create global settings instance
settings = Settings()
