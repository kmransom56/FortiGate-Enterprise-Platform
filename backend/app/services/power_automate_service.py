# Power Automate Integration Service
import aiohttp
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import json

from config import settings

logger = logging.getLogger(__name__)

class PowerAutomateService:
    """
    Service for integrating with Microsoft Power Automate workflows
    Enables automated responses to network security events
    """
    
    def __init__(self):
        self.webhook_url = settings.POWER_AUTOMATE_WEBHOOK_URL
        self.session: Optional[aiohttp.ClientSession] = None
        self.workflow_mappings = {
            "device_created": "new_device_detected",
            "vulnerabilities_detected": "security_vulnerability_found", 
            "critical_vulnerabilities_detected": "critical_security_alert",
            "device_offline": "device_connectivity_lost",
            "suspicious_activity": "security_incident_detected",
            "compliance_violation": "compliance_alert"
        }
    
    async def initialize(self) -> None:
        """Initialize the Power Automate service"""
        try:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30),
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": "FortiGate-Network-Monitor-Pro/1.0"
                }
            )
            
            logger.info("Power Automate service initialized")
            
            # Test connection if webhook URL is configured
            if self.webhook_url:
                await self._test_connection()
                
        except Exception as e:
            logger.error(f"Failed to initialize Power Automate service: {str(e)}")
            raise
    
    async def _test_connection(self) -> None:
        """Test connection to Power Automate webhook"""
        try:
            test_payload = {
                "test": True,
                "timestamp": datetime.utcnow().isoformat(),
                "message": "Connection test from FortiGate Network Monitor Pro"
            }
            
            async with self.session.post(self.webhook_url, json=test_payload) as response:
                if response.status == 200:
                    logger.info("Power Automate connection test successful")
                else:
                    logger.warning(f"Power Automate connection test returned status: {response.status}")
                    
        except Exception as e:
            logger.warning(f"Power Automate connection test failed: {str(e)}")
    
    async def trigger_workflow(self, action: str, payload: Dict[str, Any]) -> bool:
        """
        Trigger a Power Automate workflow with the given action and payload
        
        Args:
            action: The action type (e.g., 'vulnerabilities_detected')
            payload: The data payload to send to Power Automate
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.webhook_url or not self.session:
            logger.warning("Power Automate webhook URL not configured or service not initialized")
            return False
        
        try:
            # Map internal action to Power Automate workflow name
            workflow_name = self.workflow_mappings.get(action, action)
            
            # Prepare the Power Automate payload
            power_automate_payload = {
                "workflow": workflow_name,
                "action": action,
                "timestamp": datetime.utcnow().isoformat(),
                "source": "FortiGate Network Monitor Pro",
                "data": payload,
                "metadata": {
                    "version": "1.0",
                    "priority": self._get_action_priority(action),
                    "requires_immediate_attention": self._is_critical_action(action)
                }
            }
            
            # Send to Power Automate
            async with self.session.post(
                self.webhook_url, 
                json=power_automate_payload
            ) as response:
                
                if response.status == 200:
                    response_data = await response.json()
                    logger.info(f"Power Automate workflow '{workflow_name}' triggered successfully")
                    return True
                else:
                    error_text = await response.text()
                    logger.error(f"Power Automate webhook failed: {response.status} - {error_text}")
                    return False
                    
        except aiohttp.ClientError as e:
            logger.error(f"Network error triggering Power Automate: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error triggering Power Automate: {str(e)}")
            return False
    
    async def send_security_alert(
        self, 
        device_info: Dict[str, Any], 
        vulnerabilities: list,
        severity: str = "high"
    ) -> bool:
        """
        Send a security alert to Power Automate with detailed vulnerability information
        
        Args:
            device_info: Information about the affected device
            vulnerabilities: List of vulnerabilities found
            severity: Alert severity level
            
        Returns:
            bool: True if successful
        """
        payload = {
            "alert_type": "security_vulnerability",
            "severity": severity,
            "device": device_info,
            "vulnerabilities": vulnerabilities,
            "recommended_actions": self._get_recommended_actions(vulnerabilities),
            "compliance_impact": self._assess_compliance_impact(vulnerabilities)
        }
        
        action = "critical_vulnerabilities_detected" if severity == "critical" else "vulnerabilities_detected"
        return await self.trigger_workflow(action, payload)
    
    async def send_device_discovery_alert(self, device_info: Dict[str, Any]) -> bool:
        """
        Send a device discovery alert to Power Automate
        
        Args:
            device_info: Information about the newly discovered device
            
        Returns:
            bool: True if successful
        """
        payload = {
            "alert_type": "device_discovery",
            "device": device_info,
            "discovery_timestamp": datetime.utcnow().isoformat(),
            "requires_classification": True,
            "security_assessment_needed": True
        }
        
        return await self.trigger_workflow("device_created", payload)
    
    async def send_compliance_alert(
        self, 
        device_info: Dict[str, Any], 
        compliance_violations: list
    ) -> bool:
        """
        Send a compliance violation alert to Power Automate
        
        Args:
            device_info: Information about the non-compliant device
            compliance_violations: List of compliance violations
            
        Returns:
            bool: True if successful
        """
        payload = {
            "alert_type": "compliance_violation",
            "device": device_info,
            "violations": compliance_violations,
            "remediation_steps": self._get_compliance_remediation(compliance_violations),
            "deadline": self._calculate_remediation_deadline(compliance_violations)
        }
        
        return await self.trigger_workflow("compliance_violation", payload)
    
    def _get_action_priority(self, action: str) -> str:
        """Get priority level for an action"""
        priority_mapping = {
            "critical_vulnerabilities_detected": "critical",
            "vulnerabilities_detected": "high", 
            "compliance_violation": "high",
            "suspicious_activity": "medium",
            "device_offline": "medium",
            "device_created": "low"
        }
        return priority_mapping.get(action, "medium")
    
    def _is_critical_action(self, action: str) -> bool:
        """Check if an action requires immediate attention"""
        critical_actions = [
            "critical_vulnerabilities_detected",
            "compliance_violation",
            "suspicious_activity"
        ]
        return action in critical_actions
    
    def _get_recommended_actions(self, vulnerabilities: list) -> list:
        """Get recommended actions based on vulnerabilities"""
        actions = []
        
        for vuln in vulnerabilities:
            if vuln.get("severity") == "critical":
                actions.append("Immediate patching required")
                actions.append("Isolate device if possible")
            elif vuln.get("severity") == "high":
                actions.append("Schedule patching within 24 hours")
                actions.append("Monitor device activity")
            
        # Remove duplicates
        return list(set(actions))
    
    def _assess_compliance_impact(self, vulnerabilities: list) -> str:
        """Assess compliance impact of vulnerabilities"""
        critical_count = len([v for v in vulnerabilities if v.get("severity") == "critical"])
        high_count = len([v for v in vulnerabilities if v.get("severity") == "high"])
        
        if critical_count > 0:
            return "high_compliance_risk"
        elif high_count > 2:
            return "medium_compliance_risk"
        else:
            return "low_compliance_risk"
    
    def _get_compliance_remediation(self, violations: list) -> list:
        """Get remediation steps for compliance violations"""
        remediation_steps = [
            "Review and update security policies",
            "Implement missing security controls", 
            "Schedule compliance audit",
            "Update documentation"
        ]
        return remediation_steps
    
    def _calculate_remediation_deadline(self, violations: list) -> str:
        """Calculate deadline for remediation based on violation severity"""
        # Simple logic - in real implementation this would be more sophisticated
        critical_violations = [v for v in violations if v.get("severity") == "critical"]
        
        if critical_violations:
            # 24 hours for critical violations
            deadline = datetime.utcnow().replace(hour=23, minute=59, second=59)
        else:
            # 7 days for other violations
            deadline = datetime.utcnow().replace(hour=23, minute=59, second=59)
            deadline = deadline.replace(day=deadline.day + 7)
        
        return deadline.isoformat()
    
    async def shutdown(self) -> None:
        """Shutdown the Power Automate service"""
        if self.session:
            await self.session.close()
            self.session = None
        
        logger.info("Power Automate service shutdown complete")
