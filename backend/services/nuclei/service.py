import sys
import os
sys.path.append('/app')

from services.base.tool_service import BaseToolService
from services.base.models import Finding
import subprocess
import json
from typing import Dict, Any, List


class NucleiService(BaseToolService):
    def __init__(self):
        super().__init__(service_name="nuclei", version="1.0.0")
    
    async def scan(self, target: str, options: Dict[str, Any]) -> Dict[str, Any]:
        # Use a simple temp file name
        output_file = "/tmp/nuclei_output.json"
        cmd = ["nuclei", "-u", target, "-j", "-o", output_file, "-silent"]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        
        findings = []
        output_lines = []
        if os.path.exists(output_file):
            with open(output_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    output_lines.append(line)
                    try:
                        data = json.loads(line)
                        findings.append(Finding(
                            severity=data.get("info", {}).get("severity", "info"),
                            title=data.get("info", {}).get("name", "Unknown"),
                            description=data.get("matched-at", ""),
                            details=data
                        ))
                    except Exception as e:
                        print(f"Error parsing nuclei line: {e}")
        
        # Return findings with output_data for file writing
        return {
            "findings": [f.dict() for f in findings],
            "raw_output": result.stdout + "\n" + result.stderr,
            "metadata": {"command": " ".join(cmd)},
            "output_data": "\n".join(output_lines)  # Raw JSON lines for file
        }


if __name__ == "__main__":
    NucleiService().run()
