#!/usr/bin/env bash
# ==============================================================================
# NAME: sync_testing_suite.sh
# PURPOSE: Automated staging macro for milestone test suites and workflows.
# ==============================================================================

set -euo pipefail

TARGET_BRANCH="commercial/strategy-funding"
TEST_FILE="tests/test_grant_milestones.py"
WORKFLOW_FILE=".github/workflows/grant_ci.yml"

print_status() {
    echo -e "\033[1;34m[+]\033[0m $1"
}

# 1. Base Environment Checks
if [ ! -d "tests" ] || [ ! -f "requirements.txt" ]; then
    echo "[-] Error: Macro must be executed from the root of the Golden-Agent repository." >&2
    exit 1
fi

# Ensure correct branch state is checked out
current_branch=$(git branch --show-current 2>/dev/null || echo "detached")
if [ "$current_branch" != "$TARGET_BRANCH" ]; then
    print_status "Aligning workspace context to target branch: $TARGET_BRANCH"
    git checkout -b "$TARGET_BRANCH" 2>/dev/null || git checkout "$TARGET_BRANCH"
fi

# 2. Compile Python Milestone Validation Suite
print_status "Staging validation test suite -> $TEST_FILE"
cat << 'EOF' > "$TEST_FILE"
#!/usr/bin/env python3
import os
import time
import pytest
from unittest.mock import patch, mock_open

from os_telemetry_provider import LinuxHardwareTelemetryProvider
from kryptic_agent_core import AutonomousAgentCore

class TestPhaseIMilestoneValidation:
    """
    Automated pytest validation suite tracking compliance for 
    Phase I technical milestones and performance bounds.
    """

    def test_orchestration_loop_latency_threshold(self):
        """Validates Milestone 1: Assures loop latency remains < 1.0ms."""
        agent = AutonomousAgentCore()
        start_time = time.perf_counter()
        execution_status = agent.execute_single_loop_pass()
        end_time = time.perf_counter()
        latency_ms = (end_time - start_time) * 1000
        assert execution_status is True
        assert latency_ms < 1.0

    @patch("builtins.open", new_callable=mock_open, read_data="25000\n")
    @patch("os.path.exists", return_value=True)
    def test_sys_class_hardware_telemetry_parsing(self, mock_exists, mock_file):
        """Validates Milestone 1: Verifies /sys/class registers parse cleanly."""
        provider = LinuxHardwareTelemetryProvider()
        metrics = provider.read_thermal_registers()
        assert "thermal_zone0" in metrics
        assert metrics["thermal_zone0"] == 25000

    def test_resilient_persistence_on_mock_operational_shock(self):
        """Validates Milestone 2: Enforces memory state survival post-fault."""
        agent = AutonomousAgentCore()
        agent.set_memory_register("grant_secure_anchor", "FAR_COMPLIANT_VAL")
        with pytest.raises(ValueError):
            agent.process_secured_command_broadcast(malformed_payload=True)
        assert agent.get_memory_register("grant_secure_anchor") == "FAR_COMPLIANT_VAL"
EOF

# 3. Compile GitHub Actions CI/CD Workflow configuration
print_status "Staging automated CI/CD engine -> $WORKFLOW_FILE"
mkdir -p .github/workflows
cat << 'EOF' > "$WORKFLOW_FILE"
name: Grant Milestone Verification Engine
on:
  push:
    branches: [ "main", "commercial/strategy-funding" ]
  pull_request:
    branches: [ "main", "commercial/strategy-funding" ]
jobs:
  validate-milestones:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-python@v5
      with:
        python-version: '3.10'
        cache: 'pip'
    - name: Install System Dependencies
      run: |
        sudo apt-get update
        sudo apt-get install -y g++ cmake sqlite3 libsqlite3-dev
    - name: Install Python Infrastructure
      run: |
        python -m pip install --upgrade pip
        pip install pytest fastapi uvicorn requests cryptography
    - name: Compile Accelerator Binary
      run: |
        g++ -O3 -std=c++17 -Wall -Wextra -Werror kryptic_hardware_accelerator.cpp -o matrix_accelerator
        chmod +x matrix_accelerator
    - name: Run Milestone Tests
      run: pytest tests/test_grant_milestones.py -v
EOF

chmod +x "$TEST_FILE"
print_status "Staging complete. Execution environment successfully updated under branch $TARGET_BRANCH."
