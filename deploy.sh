#!/bin/bash
echo "Launching Golden-Agent Cluster Ecosystem..."
python3 main_sentience_core.py &
SERVER_PID=$!
sleep 1
python3 vr_pov_monitor.py
kill $SERVER_PID
