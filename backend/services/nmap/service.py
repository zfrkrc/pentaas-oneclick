import sys
import os
sys.path.append('/app')

from services.base.tool_service import BaseToolService
from services.base.models import Finding
import subprocess
import xml.etree.ElementTree as ET
from typing import Dict, Any, List


class NmapService(BaseToolService):
    """Nmap scanning service"""
    
    def __init__(self):
        super().__init__(service_name="nmap", version="1.0.0")
    
    async def scan(self, target: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Nmap scan"""
        
        # Determine scan type from options
        scan_type = options.get("scan_type", "basic")
        
        if scan_type == "white":
            nmap_args = ["-sV", "-p-", "--open"]
        elif scan_type == "gray":
            nmap_args = ["-sV", "-sC", "-p-"]
        elif scan_type == "black":
            nmap_args = ["-A", "-p-"]
        else:
            nmap_args = ["-sV", "-p", "80,443,8080,8443"]
        
        # Run Nmap
        output_file = f"/tmp/nmap_{target.replace('.', '_')}.xml"
        cmd = ["nmap"] + nmap_args + ["-oX", output_file, target]
        
        try:
            # Increased timeout to 30 minutes for full port scans
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
            raw_output = result.stdout
        except subprocess.TimeoutExpired:
            raw_output = f"Scan timed out after 1800 seconds. Command: {' '.join(cmd)}"
        except Exception as e:
            raw_output = f"Error running nmap: {str(e)}"
        
        # Parse XML output
        findings = []
        
        if os.path.exists(output_file):
            findings = self._parse_nmap_xml(output_file)
        
        return {
            "findings": [f.dict() for f in findings],
            "raw_output": raw_output,
            "metadata": {
                "scan_type": scan_type,
                "command": " ".join(cmd)
            }
        }
    
    def _parse_nmap_xml(self, xml_file: str) -> List[Finding]:
        """Parse Nmap XML output"""
        findings = []
        
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            
            for host in root.findall(".//host"):
                address = host.find(".//address[@addrtype='ipv4']")
                if address is None:
                    continue
                
                ip = address.get("addr")
                
                for port in host.findall(".//port"):
                    port_id = port.get("portid")
                    protocol = port.get("protocol")
                    state = port.find("state")
                    service = port.find("service")
                    
                    if state is not None and state.get("state") == "open":
                        service_name = service.get("name", "unknown") if service is not None else "unknown"
                        version = service.get("version", "") if service is not None else ""
                        
                        findings.append(Finding(
                            severity="info",
                            title=f"Open Port: {port_id}/{protocol}",
                            description=f"Service: {service_name} {version}",
                            details={
                                "ip": ip,
                                "port": port_id,
                                "protocol": protocol,
                                "service": service_name,
                                "version": version
                            }
                        ))
        except Exception as e:
            print(f"Error parsing Nmap XML: {e}")
        
        return findings


if __name__ == "__main__":
    service = NmapService()
    service.run()
