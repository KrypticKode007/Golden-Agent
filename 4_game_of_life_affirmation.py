#!/usr/bin/env python3
"""
4_game_of_life_affirmation.py
Standalone Game of Life Affirmation Engine Script for Golden-Agent.
"""

import subprocess
import sys


def main() -> int:
    topic = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "intuition"
    print(f"[RUNNER] Executing 4. The Game of Life Affirmation Engine (--affirm) for topic: {topic!r}...")
    result = subprocess.run([sys.executable, "golden_agent-v8.py", "--affirm", topic])
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
