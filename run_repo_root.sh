#!/usr/bin/env bash
# ==============================================================================
# Kryptic-Agent: Unified Core Launch, Verification & Production Packaging
# ==============================================================================

set -euo pipefail

INFO="[\033[0;34mINFO\033[0m]"
SUCCESS="[\033[0;32mSUCCESS\033[0m]"
ERROR="[\033[0;31mERROR\033[0m]"

echo -e "${INFO} Commencing global repository orchestration and structural packaging..."

# 1. Align Environmental Framework Boundaries
export PYTHONPATH="${PYTHONPATH:-}:${PWD}"

# 2. Strict C++ Native Optimization Compilation
echo -e "${INFO} Building high-speed native acceleration math engine..."
if g++ -O3 -std=c++17 -Wall -Wextra -Werror kryptic_hardware_accelerator.cpp -o matrix_accelerator; then
    chmod +x matrix_accelerator
    echo -e "  ${SUCCESS} Native accelerator compiled flawlessly."
else
    echo -e "  ${ERROR} Compilation breach detected. Terminating pipeline." && exit 1
fi

# 3. Initialize Corporate Compliance Scaffolding
echo -e "${INFO} Synchronizing corporate manifests and grant proposal proofs..."
python generate_llc12_manifest.py
python generate_grant_proposal.py

# 4. Programmatic Validation Engine Matrix
echo -e "${INFO} Spawning testing hooks via pytest..."
if pytest tests -v; then
    echo -e "  ${SUCCESS} All unit and data schema tests passed flawlessly."
else
    echo -e "  ${ERROR} Testing framework execution failure." && exit 1
fi

# 5. Production Release Packing Pipeline
echo -e "${INFO} Compressing verified passing branch structures into release asset..."
zip -r kryptic-agent-passing-branches.zip . \
    -x "*.git*" -x "*persistent_data/*" -x "*logs/*" -x "*__pycache__*"

echo -e "\n=============================================================================="
echo -e "${SUCCESS} DEPLOYMENT STATUS: SECURE, IMMUTABLE, AND PREPPED FOR VENTURE DELIVERY"
echo -e "=============================================================================="
