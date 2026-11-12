#!/bin/bash
set -e

echo "🧹 Organizing Golden-Agent Repository..."

# Create modular directory structure
mkdir -p legacy
mkdir -p golden_agent/modules
mkdir -p golden_agent/middleware
mkdir -p sdk/unreal_godot

# Move duplicate/versioned files to legacy
mv -f "README (2).md" "README (3).md" "golden_agent-v2.py" "golden_agent-v8.py" "main_sentience_core (2).py" "golden-agent-ci (1).yml" legacy/ 2>/dev/null || true

# Create module __init__ files
touch golden_agent/__init__.py
touch golden_agent/modules/__init__.py
touch golden_agent/middleware/__init__.py

echo "✅ Repository structured cleanly. Legacy files archived in /legacy."
