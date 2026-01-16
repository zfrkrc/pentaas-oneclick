# Quick service generator for remaining tools
# Run this to create minimal services for all remaining tools

TOOLS_CONFIG = {
    "testssl": "testssl.sh",
    "dirsearch": "dirsearch",
    "nikto": "nikto",
    "arjun": "arjun",
    "dalfox": "dalfox",
    "dnsrecon": "dnsrecon",
    "wpscan": "wpscan",
    "zap": "zap-baseline.py",
    "sslyze": "sslyze"
}

# Template for simple services
SERVICE_TEMPLATE = """import sys
sys.path.append('/app')
from services.base.tool_service import BaseToolService
import subprocess
from typing import Dict, Any

class {class_name}Service(BaseToolService):
    def __init__(self):
        super().__init__(service_name="{service_name}", version="1.0.0")
    
    async def scan(self, target: str, options: Dict[str, Any]) -> Dict[str, Any]:
        cmd = ["{tool_cmd}", target]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        return {{
            "findings": [],
            "raw_output": result.stdout,
            "metadata": {{"command": " ".join(cmd)}}
        }}

if __name__ == "__main__":
    {class_name}Service().run()
"""

print("Use this template to create remaining services")
