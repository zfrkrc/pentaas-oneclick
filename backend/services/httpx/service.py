import json
import subprocess
import sys
from typing import Any, Dict, List

sys.path.append('/app')
from services.base.tool_service import BaseToolService


class HttpxService(BaseToolService):
    def __init__(self):
        super().__init__(service_name='httpx', version='1.0.0')

    @staticmethod
    def _classify_severity(status_code: Any, failed: bool) -> str:
        if failed:
            return 'low'
        if not isinstance(status_code, int):
            return 'low'
        if status_code >= 500:
            return 'medium'
        if status_code in (401, 403):
            return 'low'
        return 'info'

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
            failed = bool(row.get('failed'))
            severity = self._classify_severity(status_code, failed)
            transport = row.get('webserver') or row.get('scheme') or 'unknown'
            description_parts = [
                f"Status={status_code}" if status_code is not None else "Status=unknown",
                f"Title={web_title}" if web_title else "Title=unknown",
                f"Transport={transport}",
            ]
            if failed and row.get('error'):
                description_parts.append(f"Error={row.get('error')}")
            findings.append({
                'severity': severity,
                'title': f'httpx probe: {url}',
                'description': ' '.join(description_parts),
                'details': {
                    'url': url,
                    'status_code': status_code,
                    'title': web_title,
                    'technologies': technologies,
                    'host': row.get('host'),
                    'ip': row.get('a'),
                    'port': row.get('port'),
                    'scheme': row.get('scheme'),
                    'webserver': row.get('webserver'),
                    'content_type': row.get('content_type'),
                    'content_length': row.get('content_length'),
                    'failed': failed,
                    'error': row.get('error'),
                }
            })

        return {
            'findings': findings,
            'raw_output': raw_output,
            'metadata': {'command': ' '.join(cmd), 'exit_code': result.returncode}
        }


if __name__ == '__main__':
    HttpxService().run()
