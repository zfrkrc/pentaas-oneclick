# Generic service template - copy and modify for each tool
import sys
import os
sys.path.append('/app')

from services.base.tool_service import BaseToolService
from services.base.models import Finding
import subprocess
from typing import Dict, Any


class GenericToolService(BaseToolService):
    """Generic tool service - override scan() method"""
    
    def __init__(self, service_name: str, tool_command: str):
        self.tool_command = tool_command
        super().__init__(service_name=service_name, version="1.0.0")
    
    async def scan(self, target: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Execute tool scan"""
        cmd = [self.tool_command, target]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            return {
                "findings": [],  # Parse output to create findings
                "raw_output": result.stdout,
                "metadata": {"command": " ".join(cmd), "exit_code": result.returncode}
            }
        except Exception as e:
            return {
                "findings": [],
                "raw_output": str(e),
                "metadata": {"error": str(e)}
            }
