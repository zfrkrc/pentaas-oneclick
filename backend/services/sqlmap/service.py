import sys
import uuid
import subprocess
from typing import Dict, Any

sys.path.append('/app')
from services.base.tool_service import BaseToolService


class SqlmapService(BaseToolService):
    def __init__(self):
        super().__init__(service_name='sqlmap', version='1.0.0')

    async def scan(self, target: str, options: Dict[str, Any]) -> Dict[str, Any]:
        output_dir = f"/tmp/sqlmap_{uuid.uuid4().hex[:8]}"
        cmd = [
            'python', '/opt/sqlmap/sqlmap.py',
            '-u', target,
            '--batch',
            '--crawl=2',
            '--random-agent',
            '--answers=crack=N',
            f'--output-dir={output_dir}',
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
        raw_output = (result.stdout or '') + ('\n' + result.stderr if result.stderr else '')

        findings = []
        low = raw_output.lower()
        if 'is vulnerable' in low or 'identified the following injection point' in low or 'parameter' in low and 'injectable' in low:
            findings.append({
                'severity': 'high',
                'title': 'Potential SQL Injection Detected',
                'description': 'SQLmap output indicates injectable parameter(s).',
                'details': {'target': target}
            })

        return {
            'findings': findings,
            'raw_output': raw_output,
            'metadata': {'command': ' '.join(cmd), 'exit_code': result.returncode}
        }


if __name__ == '__main__':
    SqlmapService().run()
