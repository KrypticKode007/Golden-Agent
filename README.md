# ⚡ Golden-Agent (Project Kai-007) — Unified Kryptic Ecosystem

**Golden-Agent (Project Kai-007)** is a post-algorithmic, on-demand cognitive AI architecture developed by **KrypticKode007 (Brandon Mark Wilson, Dinuba, CA)**. With **`unified_golden_gateway.py`** and **`access_key_token.py`**, this repository serves as the **token-protected central command core** unifying `Golden-Agent`, `-nkryptd`, `Autonomous-self-healing-battery`, and `Advanced-Ai-Model` under a single FastAPI gateway (`Port 8888`) for Linux and Termux.

## 🧬 Architecture
* **🔐 Blank-Default Access Key (`access_key_token.py`):** `ACCESS_KEY_TOKEN` defaults to blank (`""`) and uses constant-time `hmac.compare_digest` verification via `X-Access-Key-Token` or `Authorization: Bearer <token>`.
* **🧠 Golden-Agent (`OrganicMindOrchestrator`):** Processes on-demand experiential narratives, inner/outer monologues, anatomical kinematics, and 24-hour circadian memory sorting.
* **🛡️ `-nkryptd` Security Moat:** Screens payloads via regex Allergy Filter + Python AST Moat and triggers the Mechanical Shaker (`os.urandom` buffer wipe + `gc.collect()`) on threats.
* **🔋 Self-Healing Battery & Cybernetics (`/cybernetic`):** Reads live Android battery telemetry (`/sys/class/power_supply/battery` or `termux-battery-status`) and mounts the 4-cell self-healing battery controller.
* **🤖 `Advanced-Ai-Model` & File Hub (`/models` & `/files`):** Exposes authenticated file inspection (`/files/tree`, `/files/read`) and script execution across all 4 repositories.

## 🚀 Quick Start
```bash
export ACCESS_KEY_TOKEN="\$(python -c 'import secrets; print(secrets.token_urlsafe(32))')"
export PYTHONPATH="\$HOME/kryptic_ecosystem/Golden-Agent:\(HOME/kryptic_ecosystem/nkryptd:\)HOME/kryptic_ecosystem/Autonomous-self-healing-battery:\(HOME/kryptic_ecosystem/Advanced-Ai-Model:\)PYTHONPATH"
python ~/kryptic_ecosystem/Golden-Agent/unified_golden_gateway.py
```

## 📡 Unified API Endpoints
* `GET /health` — Public system & token configuration status
* `GET /files/tree` — List all files across all 4 integrated repos (`X-Access-Key-Token`)
* `GET /files/read?repo=...&path=...` — Read any file across the 4 repos (`X-Access-Key-Token`)
* `POST /golden/reflect` — Send a `nkryptd`-screened reflective event to Golden-Agent (`X-Access-Key-Token`)
* `GET /battery/live` — Live Android battery telemetry (`X-Access-Key-Token`)
* `GET /models` & `POST /models/run` — List and run `Advanced-Ai-Model` scripts (`X-Access-Key-Token`)
* `POST /cybernetic/battery/autonomous` — Run 4-cell self-healing battery simulation

## 🤖 Autonomous Multi-Agent Engine (`src/golden_agent`)

Golden-Agent includes a modular, 5-track autonomous agent platform mounted directly onto the gateway (`Port 8888`) and runnable from the CLI:

- **Multi-Agent DAG Orchestrator (`core/orchestrator.py`):** Decomposes complex goals into parallel subtasks across specialized `coder`, `researcher`, and `ops` workers with swappable YAML profiles (`profiles/`).
- **Tiered Hybrid Model Router (`config/model_router.py`):** Routes tasks across Tier 1 (Fast/Local Ollama), Tier 2 (Standard), and Tier 3 (Frontier Reasoning) models with zero-dependency HTTP and LiteLLM support.
- **Guardrails, HITL & Sandbox (`runtime/`):** Classifies tool calls (`READ`, `WRITE`, `DESTRUCTIVE`), pauses destructive actions for human approval, and runs code in isolated Docker or Termux subprocess sandboxes.
- **Context Compressor & Hybrid AST RAG (`core/context_manager.py`, `memory/`):** Compresses long sessions automatically, indexes Python AST + docs with BM25/coverage search, and persists cross-session episodic memory.
- **Flight-Recorder Telemetry & Evals (`telemetry/tracer.py`, `tests/golden_evals/`):** Logs JSONL span timings/costs and runs automated regression benchmarks in CI.

### Autonomous Endpoints & CLI

- `POST /agent/run` — Execute a goal (`{"goal": "...", "profile": "universal|coder|researcher|ops"}`)
- `POST /agent/stream` — Stream live Server-Sent Events (SSE) execution updates
- `POST /agent/approve/{approval_id}` — Approve a paused Human-in-the-Loop (HITL) action
- `GET /agent/tools` & `POST /agent/index` — Inspect registered MCP/sandbox tools and re-index workspace AST chunks
- **Termux / Terminal CLI:**
  ```bash
  PYTHONPATH=src python -m golden_agent.interfaces.cli "Audit repository and summarize key modules" --profile researcher
  ```
