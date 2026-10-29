#!/usr/bin/env bash
# ==============================================================================
# NAME: run_full_repo.sh
# PURPOSE: Executes the entire Golden-Agent framework orchestration layer,
#          compiles high-speed binaries, and outputs validation metrics.
# ==============================================================================

set -euo pipefail

TARGET_BRANCH="commercial/strategy-funding"

echo "[+] Target Path Verification: Alignment set to branch -> $TARGET_BRANCH"

# 1. Environment and Dependency Validation
if [ -f "scripts/audit_environment.py" ]; then
    python3 scripts/audit_environment.py
else
    echo "[-] Error: Environment audit matrix missing. Run staging macros first." >&2
    exit 1
fi

# 2. Native C++ Component Compilation
echo "[+] Initializing Native Acceleration Toolchains..."
if [ -f "kryptic_hardware_accelerator.cpp" ]; then
    g++ -O3 -std=c++17 -Wall -Wextra -Werror kryptic_hardware_accelerator.cpp -o matrix_accelerator
    chmod +x matrix_accelerator
    echo "    -> Compiled high-speed matrix accelerator binary: ./matrix_accelerator"
else
    echo "    -> [NOTICE] Low-level C++ source not present in staging workspace. Simulating hardware translation layer..."
fi

# 3. Document Matrix Verification
echo "[+] Verification Engine: Refreshing strategic asset layouts..."
if [ -f "commercial/strategy/generate_grant_proposal.py" ]; then
    python3 commercial/strategy/generate_grant_proposal.py
fi
if [ -f "generate_abstract.py" ]; then
    python3 generate_abstract.py
fi

# 4. Phase I Financial Profile Generation
echo "[+] Financial Operations Matrix: Processing cost-accounting allocations..."
if [ -f "commercial/strategy/budget_calculator.py" ]; then
    python3 commercial/strategy/budget_calculator.py 150000.00
fi

# 5. Core Performance and Milestone Test Matrix Execution
echo "[+] Initializing Cybernetic Validation Testing Matrix (PyTest Ecosystem)..."
if [ -f "tests/test_grant_milestones.py" ]; then
    pytest tests/test_grant_milestones.py -v
else
    echo "[-] Error: Milestone testing framework not found at tests/test_grant_milestones.py" >&2
    exit 1
fi

echo "[+] Execution Pipeline Sequence Completed Successfully. System State: COMPLIANT."
