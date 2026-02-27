import sys
sys.path.append('/app')
from services.base.tool_service import BaseToolService
import subprocess
from typing import Dict, Any

class DirsearchService(BaseToolService):
    def __init__(self):
        super().__init__(service_name='dirsearch', version='1.0.0')
    
    async def scan(self, target: str, options: Dict[str, Any]) -> Dict[str, Any]:
        cmd = ['dirsearch', '-u', target, '--format=json']
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        return {'findings': [], 'raw_output': result.stdout, 'metadata': {'command': ' '.join(cmd)}}

if __name__ == '__main__':
    DirsearchService().run()
