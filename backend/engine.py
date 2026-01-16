import subprocess
import uuid
import os

BASE_DIR = "/app"
COMPOSE_FILE = f"{BASE_DIR}/compose/docker-compose.string.yml"
REPORT_DIR = f"{BASE_DIR}/reports"


def run_scan(target: str, category: str, uid: str = None) -> str:
    if not uid:
        uid = uuid.uuid4().hex
    
    # Internal path (container view)
    data_dir_internal = f"{REPORT_DIR}/{uid}/data"
    os.makedirs(data_dir_internal, exist_ok=True)
    
    # Host path (for DinD)
    host_reports_path = os.environ.get("HOST_REPORTS_PATH", f"{os.getcwd()}/reports")
    host_data_dir = f"{host_reports_path}/{uid}/data"

    # Save metadata for UI tracking
    with open(f"{data_dir_internal}/meta.json", "w") as f:
        json.dump({"target": target, "category": category, "uid": uid}, f)

    # Sanitize and parse target
    target_raw = target.strip()
    target_domain = target_raw.replace("https://", "").replace("http://", "").split('/')[0].split(':')[0]
    target_url = target_raw if (target_raw.startswith("http://") or target_raw.startswith("https://")) else f"http://{target_raw}"

    env_vars = os.environ.copy()
    env_vars["TARGET"] = target_raw
    env_vars["TARGET_URL"] = target_url
    env_vars["TARGET_DOMAIN"] = target_domain
    env_vars["HOST_DATA_DIR"] = host_data_dir

    # 1. Run Scanners
    print(f"Starting {category} scan for {target}...")
    try:
        result = subprocess.run(
            ["docker", "compose", "-f", COMPOSE_FILE, "--profile", category, "up"],
            env=env_vars,
            check=True,
            capture_output=True,
            text=True
        )
        print(f"DEBUG: Scan Success.\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Scan failed (code {e.returncode}):\nSTDOUT: {e.stdout}\nSTDERR: {e.stderr}")

    # 2. Run Merge
    print("Merging results...")
    try:
        subprocess.run(
            ["docker", "compose", "-f", COMPOSE_FILE, "run", "--rm", "merge"],
            env=env_vars,
            check=True,
            capture_output=True,
            text=True
        )
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Merge failed (code {e.returncode}):\nSTDOUT: {e.stdout}\nSTDERR: {e.stderr}")

    return uid
