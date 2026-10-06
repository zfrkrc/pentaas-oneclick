import os
import json
import sys
import uuid
import subprocess
from typing import Dict, Any

sys.path.append('/app')
from services.base.tool_service import BaseToolService


class WapitiService(BaseToolService):
    def __init__(self):
        super().__init__(service_name='wapiti', version='1.0.0')

    async def scan(self, target: str, options: Dict[str, Any]) -> Dict[str, Any]:
        output_file = f"/tmp/wapiti_{uuid.uuid4().hex[:8]}.json"
        cmd = ['wapiti', '-u', target, '-f', 'json', '-o', output_file]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
        raw_output = (result.stdout or '') + ('\n' + result.stderr if result.stderr else '')
        findings = []

        if os.path.exists(output_file):
            try:
                with open(output_file, 'r') as f:
                    data = json.load(f)
                vulns = data.get('vulnerabilities', {}) if isinstance(data, dict) else {}
                for vuln_type, items in vulns.items():
                    if not items:
                        continue
                    findings.append({
                        'severity': 'medium',
                        'title': f'Wapiti: {vuln_type}',
                        'description': f'{len(items)} potential issue(s) reported for {vuln_type}.',
                        'details': {'type': vuln_type, 'count': len(items)}
                    })
            except Exception:
                pass

        return {
            'findings': findings,
            'raw_output': raw_output,
            'metadata': {'command': ' '.join(cmd), 'exit_code': result.returncode}
        }


if __name__ == '__main__':
    WapitiService().run()
