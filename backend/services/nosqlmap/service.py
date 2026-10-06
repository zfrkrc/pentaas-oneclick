import sys
import subprocess
from typing import Dict, Any

sys.path.append('/app')
from services.base.tool_service import BaseToolService


class NoSQLMapService(BaseToolService):
    def __init__(self):
        super().__init__(service_name='nosqlmap', version='1.0.0')

    async def scan(self, target: str, options: Dict[str, Any]) -> Dict[str, Any]:
        cmd = ['python', '/opt/nosqlmap/nosqlmap.py', '--target', target, '--attack', '1']
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        raw_output = (result.stdout or '') + ('\n' + result.stderr if result.stderr else '')

        findings = []
        low = raw_output.lower()
        if 'vulnerable' in low or 'injection' in low and 'found' in low:
            findings.append({
                'severity': 'high',
                'title': 'Potential NoSQL Injection Detected',
                'description': 'NoSQLMap output indicates possible NoSQL injection behavior.',
                'details': {'target': target}
            })

        return {
            'findings': findings,
            'raw_output': raw_output,
            'metadata': {'command': ' '.join(cmd), 'exit_code': result.returncode}
        }


if __name__ == '__main__':
    NoSQLMapService().run()
