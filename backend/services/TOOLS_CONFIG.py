# Helper script to generate simple tool services
import os

TOOLS = {
    "whatweb": {"base_image": "python:3.11-slim", "install": "apt-get update && apt-get install -y whatweb"},
    "wafw00f": {"base_image": "python:3.11-slim", "install": "pip install wafw00f"},
    "dirsearch": {"base_image": "python:3.11-slim", "install": "pip install dirsearch"},
    "arjun": {"base_image": "python:3.11-slim", "install": "pip install arjun"},
    "dalfox": {"base_image": "hahwul/dalfox:latest", "install": "apk add python3 py3-pip"},
    "nikto": {"base_image": "python:3.11-slim", "install": "apt-get update && apt-get install -y nikto"},
    "testssl": {"base_image": "drwetter/testssl.sh:latest", "install": "apk add python3 py3-pip"},
    "dnsrecon": {"base_image": "python:3.11-slim", "install": "pip install dnspython netaddr lxml"},
    "wpscan": {"base_image": "wpscanteam/wpscan:latest", "install": "apk add python3 py3-pip"},
    "zap": {"base_image": "zaproxy/zap-stable:latest", "install": "apt-get update && apt-get install -y python3 python3-pip"},
    "sslyze": {"base_image": "python:3.11-slim", "install": "pip install sslyze"},
}

# This is just documentation - actual services created manually below
