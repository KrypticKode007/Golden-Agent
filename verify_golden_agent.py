#!/usr/bin/env python3
"""
verify_golden_agent.py
Standalone Self-Healing & All-Engines Verification Script for Golden-Agent.
"""

import subprocess
import sys


def main() -> int:
    print("[RUNNER] Executing 1. Self-Healing & All 7 Engines Verification (--verify)...")
    result = subprocess.run([sys.executable, "golden_agent-v8.py", "--verify"])
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
