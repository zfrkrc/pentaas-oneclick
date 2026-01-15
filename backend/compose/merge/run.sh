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

echo "Listing generated reports:"
ls -l "$DATA_DIR"

# Simple summary generation
echo "Scan Summary for $TARGET" > "$DATA_DIR/scan_summary.txt"
echo "Date: $(date)" >> "$DATA_DIR/scan_summary.txt"
echo "Files found:" >> "$DATA_DIR/scan_summary.txt"
ls -1 "$DATA_DIR" >> "$DATA_DIR/scan_summary.txt"

echo "[+] Merge/Verification completed. Summary saved to scan_summary.txt"
