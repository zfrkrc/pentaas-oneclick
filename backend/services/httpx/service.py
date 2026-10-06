import json
import subprocess
import sys
from typing import Any, Dict, List

sys.path.append('/app')
from services.base.tool_service import BaseToolService


class HttpxService(BaseToolService):
    def __init__(self):
        super().__init__(service_name='httpx', version='1.0.0')

    async def scan(self, target: str, options: Dict[str, Any]) -> Dict[str, Any]:
        cmd = [
            'httpx',
            '-u', target,
            '-silent',
            '-json',
            '-status-code',
            '-title',
            '-tech-detect',
            '-follow-host-redirects',
            '-timeout', '10',
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        stdout = result.stdout or ''
        stderr = result.stderr or ''
        raw_output = stdout + ('\n' + stderr if stderr else '')

        findings: List[Dict[str, Any]] = []
        for line in stdout.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue

            url = row.get('url') or target
            status_code = row.get('status_code')
            web_title = row.get('title') or ''
            technologies = row.get('tech') or []
            findings.append({
                'severity': 'info',
                'title': f'httpx probe: {url}',
                'description': f'Status={status_code} Title={web_title}',
                'details': {
                    'url': url,
                    'status_code': status_code,
                    'title': web_title,
                    'technologies': technologies,
                    'host': row.get('host'),
                    'ip': row.get('a'),
                }
            })

        return {
            'findings': findings,
            'raw_output': raw_output,
            'metadata': {'command': ' '.join(cmd), 'exit_code': result.returncode}
        }


if __name__ == '__main__':
    HttpxService().run()
