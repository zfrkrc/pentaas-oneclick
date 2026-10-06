import os
import sys
import uuid
import subprocess
from typing import Dict, Any

sys.path.append('/app')
from services.base.tool_service import BaseToolService


class GitToolsService(BaseToolService):
    def __init__(self):
        super().__init__(service_name='gittools', version='1.0.0')

    async def scan(self, target: str, options: Dict[str, Any]) -> Dict[str, Any]:
        git_url = f"{target.rstrip('/')}/.git"
        output_dir = f"/tmp/gitdump_{uuid.uuid4().hex[:8]}"
        cmd = ['git-dumper', git_url, output_dir]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        raw_output = (result.stdout or '') + ('\n' + result.stderr if result.stderr else '')

        findings = []
        file_count = 0
        if os.path.isdir(output_dir):
            for _, _, files in os.walk(output_dir):
                file_count += len(files)

        if result.returncode == 0 and file_count > 0:
            findings.append({
                'severity': 'medium',
                'title': 'Exposed .git Repository Suspected',
                'description': f'git-dumper extracted {file_count} files from target repository metadata.',
                'details': {'git_url': git_url}
            })

        return {
            'findings': findings,
            'raw_output': raw_output,
            'metadata': {'command': ' '.join(cmd), 'exit_code': result.returncode, 'file_count': file_count}
        }


if __name__ == '__main__':
    GitToolsService().run()
