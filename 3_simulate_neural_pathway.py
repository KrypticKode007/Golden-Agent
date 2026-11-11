#!/usr/bin/env python3
"""
3_simulate_neural_pathway.py
Standalone Human Brain Neural Pathway Simulation Script for Golden-Agent.
"""

import subprocess
import sys


def main() -> int:
    stimulus = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Learn a new skill with clarity"
    print(f"[RUNNER] Executing 3. Neural Pathway Simulation (--brain) for stimulus: {stimulus!r}...")
    result = subprocess.run([sys.executable, "golden_agent-v8.py", "--brain", stimulus])
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
