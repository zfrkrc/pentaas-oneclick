import re
import sys
import subprocess
from typing import Dict, Any

sys.path.append('/app')
from services.base.tool_service import BaseToolService


class GobusterService(BaseToolService):
    def __init__(self):
        super().__init__(service_name='gobuster', version='1.0.0')

    async def scan(self, target: str, options: Dict[str, Any]) -> Dict[str, Any]:
        cmd = [
            'gobuster', 'dir',
            '-u', target,
            '-w', '/usr/share/wordlists/common.txt',
            '--no-error',
            '-q',
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        raw_output = (result.stdout or '') + ('\n' + result.stderr if result.stderr else '')

        findings = []
        for line in raw_output.splitlines():
            status_match = re.search(r'Status:\s*(\d{3})', line)
            if not status_match:
                continue
            status = int(status_match.group(1))
            if status in (200, 204, 301, 302, 307, 401, 403):
                path = line.split(' (Status:')[0].strip()
                findings.append({
                    'severity': 'info',
                    'title': f'Gobuster Path: {path}',
                    'description': f'HTTP status {status}',
                    'details': {'path': path, 'status': status}
                })

        return {
            'findings': findings,
            'raw_output': raw_output,
            'metadata': {'command': ' '.join(cmd), 'exit_code': result.returncode}
        }


if __name__ == '__main__':
    GobusterService().run()
