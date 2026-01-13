import subprocess
from pathlib import Path
import uuid

BASE_DIR = Path("/app/reports")

def run_scan(ip: str, category: str) -> str:
    uid = uuid.uuid4().hex

    data_dir = BASE_DIR / uid / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    compose_file = "/app/compose/docker-compose.string.yml"

    cmd = [
        "docker", "compose",
        "-f", compose_file,
        "run", "--rm",
        "-e", f"TARGET={ip}",
        "-e", f"DATA_DIR={str(data_dir)}",
        "merge"
    ]

    subprocess.run(
        cmd,
        check=True
    )

    print("Running:", " ".join(cmd))
    subprocess.run(cmd, check=True, cwd="/home/zfrkrc/pentest/pentaas-oneclick")
    return uid
