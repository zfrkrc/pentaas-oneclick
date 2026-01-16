import sys
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
        output_file = f"/tmp/nuclei_{target.replace('.', '_')}.json"
        cmd = ["nuclei", "-u", target, "-json", "-o", output_file]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        
        findings = []
        if os.path.exists(output_file):
            with open(output_file, 'r') as f:
                for line in f:
                    try:
                        data = json.loads(line.strip())
                        findings.append(Finding(
                            severity=data.get("info", {}).get("severity", "info"),
                            title=data.get("info", {}).get("name", "Unknown"),
                            description=data.get("matched-at", ""),
                            details=data
                        ))
                    except:
                        pass
        
        return {
            "findings": [f.dict() for f in findings],
            "raw_output": result.stdout,
            "metadata": {"command": " ".join(cmd)}
        }


if __name__ == "__main__":
    NucleiService().run()
