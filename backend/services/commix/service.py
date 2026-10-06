import sys
import subprocess
from typing import Dict, Any

sys.path.append('/app')
from services.base.tool_service import BaseToolService


class CommixService(BaseToolService):
    def __init__(self):
        super().__init__(service_name='commix', version='1.0.0')

    async def scan(self, target: str, options: Dict[str, Any]) -> Dict[str, Any]:
        cmd = [
            'python', '/opt/commix/commix.py',
            '--url', target,
            '--batch',
            '--output-dir=/tmp/commix_output',
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
        raw_output = (result.stdout or '') + ('\n' + result.stderr if result.stderr else '')

        findings = []
        low = raw_output.lower()
        if 'vulnerable' in low or 'injection' in low and 'found' in low:
            findings.append({
                'severity': 'high',
                'title': 'Potential Command Injection Detected',
                'description': 'Commix output indicates possible command injection.',
                'details': {'target': target}
            })

        return {
            'findings': findings,
            'raw_output': raw_output,
            'metadata': {'command': ' '.join(cmd), 'exit_code': result.returncode}
        }


if __name__ == '__main__':
    CommixService().run()
