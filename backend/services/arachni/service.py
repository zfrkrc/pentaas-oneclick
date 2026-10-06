import sys
import uuid
import subprocess
from typing import Dict, Any

sys.path.append('/app')
from services.base.tool_service import BaseToolService


class ArachniService(BaseToolService):
    def __init__(self):
        super().__init__(service_name='arachni', version='1.0.0')

    async def scan(self, target: str, options: Dict[str, Any]) -> Dict[str, Any]:
        report_file = f"/tmp/arachni_{uuid.uuid4().hex[:8]}.afr"
        cmd = [
            '/opt/arachni/bin/arachni',
            target,
            '--output-only-positives',
            f'--report-save-path={report_file}',
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=1200)
        raw_output = (result.stdout or '') + ('\n' + result.stderr if result.stderr else '')

        return {
            'findings': [],
            'raw_output': raw_output,
            'metadata': {'command': ' '.join(cmd), 'exit_code': result.returncode}
        }


if __name__ == '__main__':
    ArachniService().run()
