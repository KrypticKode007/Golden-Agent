#!/bin/bash
# ==============================================================================
# UNIFIED PIPELINE AUTOMATION LAUNCHER
# ==============================================================================
set -e

echo "=== [1/4] INITIALIZING COMPILATION STEP ==="
if [ -f "kryptic_hardware_accelerator.cpp" ]; then
    g++ -O3 -shared -fPIC kryptic_hardware_accelerator.cpp -o libkryptic_core.so
    echo "[SUCCESS] Shared object library 'libkryptic_core.so' compiled cleanly."
else
    echo "[WARN] 'kryptic_hardware_accelerator.cpp' not found. Standing up mock-simulation fallback mode."
fi

echo -e "\n=== [2/4] VERIFYING DEPENDENCY MAPS ==="
python3 -m pip install -r requirements.txt --quiet
echo "[SUCCESS] Dependencies synchronized."

echo -e "\n=== [3/4] RUNNING VERIFICATION TESTING MATRIX ==="
if [ -f "test_telemetry_edge.py" ]; then
    python3 -m pytest test_telemetry_edge.py -v
    echo "[SUCCESS] All operational verification test cases passed."
else
    echo "[ERROR] 'test_telemetry_edge.py' missing from active tree."
    exit 1
fi

echo -e "\n=== [4/4] STANDING UP UNIFIED DASHBOARD INTERFACE ==="
sleep 1
python3 gui_dashboard.py
