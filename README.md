# 👑 Golden-Agent

![Tests](https://shields.io)
![Platform](https://shields.io)
![License](https://shields.io)

**Lightweight Autonomous Multi-Agent DAG Orchestrator, Hybrid AST RAG Engine & Self-Healing Runtime.**

Built from the ground up for **Linux, Docker, and Android/Termux** edge devices. Unlike heavy cloud frameworks that require hundreds of megabytes of RAM just to import, Golden-Agent delivers deterministic Python AST code memory, tiered local/cloud LLM routing, and Human-in-the-Loop (HITL) guardrails in a near-zero footprint.

## ⚡ Verified Edge Benchmarks (Android / Termux ARM64)
Tested natively on Python 3.14 (ARM64, 2.6 GB RAM device):
* **Cold Import Latency:** `2.10 ms`
* **Peak RAM Footprint:** `11.38 MB` RSS (framework overhead)
* **Codebase AST Indexing:** `325+ chunks` indexed in `< 1.6s`
* **Automated Test Suite:** `22/22 passed` in `6.78s`

## 🏗 Core Architecture
* **Parallel DAG Task Orchestration:** Decomposes high-level goals into dependency-aware sub-tasks with built-in specialist profiles (`universal`, `coder`, `researcher`, `ops`).
* **Hybrid AST & SQLite Memory:** Parses Python Abstract Syntax Trees directly into SQLite (`PRAGMA integrity_check` protected) for exact symbol retrieval without external vector databases.
* **Tiered Local/Cloud Routing:** Routes routine steps to local Ollama models (`qwen2.5:0.5b`, `llama3.2:1b`) and escalates complex reasoning to cloud APIs with zero-dependency HTTP fallback.
* **HITL Guardrails & Sandboxing:** Enforces workspace path isolation, command allowlists, and interactive approval gates before destructive actions.

## 🚀 Quick Start

### 1. Install
```bash
git clone https://github.com
cd Golden-Agent
pip install -e .
```

### 2. Auto-Configure Environment
Run the interactive setup wizard (auto-detects Termux/low-RAM hardware):
```bash
golden-agent init
```

### 3. Run via CLI, Examples, or FastAPI Gateway
```bash
# Run an autonomous task
golden-agent "Audit repository architecture and summarize key modules" --profile coder

# Run ready-made examples
python examples/ast_code_qa.py

# Or launch the REST/SSE API gateway
uvicorn golden_agent.interfaces.api:app --host 0.0.0.0 --port 8000
```

### 📱 Low-RAM / Termux Tuning (< 3 GB RAM Devices)
`golden-agent init` configures low-RAM defaults automatically on Termux. If running Ollama alongside Golden-Agent on < 3 GB RAM devices, set:
```bash
export OLLAMA_NUM_CTX=1024
export OLLAMA_MAX_LOADED_MODELS=1
export GOLDEN_MAX_PARALLEL_WORKERS=1
```

## 🤝 Contributing & License
Contributions are welcome—see [CONTRIBUTING.md](CONTRIBUTING.md). Open-source under the **GNU General Public License v3.0 (GPL-3.0)**.
