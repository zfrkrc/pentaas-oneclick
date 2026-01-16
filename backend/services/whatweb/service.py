import sys
sys.path.append('/app')
from services.base.tool_service import BaseToolService
from services.base.models import Finding
import subprocess
from typing import Dict, Any

class WhatWebService(BaseToolService):
    def __init__(self):
        super().__init__(service_name="whatweb", version="1.0.0")
    
    async def scan(self, target: str, options: Dict[str, Any]) -> Dict[str, Any]:
        cmd = ["whatweb", "--color=never", target]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        return {
            "findings": [],
            "raw_output": result.stdout,
            "metadata": {"command": " ".join(cmd)}
        }

if __name__ == "__main__":
    WhatWebService().run()
