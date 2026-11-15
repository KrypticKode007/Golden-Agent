#!/usr/bin/env python3
"""
ask_cognitive_assistant.py
Standalone Real-Time Cognitive AI Assistant Query Script for Golden-Agent.
"""

import subprocess
import sys


def main() -> int:
    prompt = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else (
        "Help me stick to my daily routine, strengthen brain focus, and give an affirmation"
    )
    print(f"[RUNNER] Executing Real-Time Cognitive AI Assistant (--ask) with prompt: {prompt!r}...")
    result = subprocess.run([sys.executable, "golden_agent-v8.py", "--ask", prompt])
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
