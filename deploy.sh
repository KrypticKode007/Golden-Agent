#!/bin/bash
set -euo pipefail

echo "Launching Golden-Agent Cluster Ecosystem..."
python3 "main_sentience_core (2).py" &
SERVER_PID=$!
cleanup() {
	kill "$SERVER_PID" 2>/dev/null || true
	wait "$SERVER_PID" 2>/dev/null || true
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

sleep 1
python3 vr_pov_monitor.py
