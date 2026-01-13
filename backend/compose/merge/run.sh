#!/bin/bash
set -e

if [ -z "$TARGET" ]; then
  echo "TARGET is not set"
  exit 1
fi

if [ -z "$DATA_DIR" ]; then
  echo "DATA_DIR is not set"
  exit 1
fi

mkdir -p "$DATA_DIR"

echo "[+] Scan started for $TARGET"
echo "[+] Output dir: $DATA_DIR"

# 🔥 NSE PATH'i EXPLICIT veriyoruz
nmap \
  --datadir /usr/share/nmap \
  -Pn \
  -sV \
  -oA "$DATA_DIR/nmap" \
  "$TARGET"

echo "[+] Scan completed"
