# Project Kai-007: Golden-Agent Monolith

A unified cognitive, somatic, and cryptographic agent framework built on FastAPI, computational neuroscience models, and tamper-evident SQLite storage.

## Overview

**Golden-Agent** integrates physiological simulation, memory decay mathematics, and security sandboxing into a single event-driven REST service (`golden_agent/unified_monolith.py`).

### Core Architecture

1. **Cryptographic Experiential Ledger**
   - Stores inner and outer monologue entries in a SHA-256 hash chain (`prev_hash` -> `entry_hash`) inside `agency_sentience.db`.
   - Retrieves contextual memories using cosine similarity weighted by the **Ebbinghaus Forgetting Curve** ($R = e^{-t/S}$) with spacing-effect reinforcement.
2. **Somatic & Circadian Simulation Engine**
   - **Fluid Kinematics:** Computes volumetric blood flow on demand via **Poiseuille's Law** ($Q = \frac{\Delta P \pi r^4}{8 \eta L}$).
   - **Homeostasis:** Regulates virtual heart rate back to baseline after cognitive load using a **PID Controller**.
   - **Neural Spiking:** Models membrane potential integration and action potential firing using **Leaky Integrate-and-Fire (LIF)** differential equations.
   - **Circadian & Affective Dynamics:** Combines a **Two-Process Sleep Model** (circadian wave + sleep debt) with **Damped Harmonic Motion** for smooth emotional valence and arousal transitions.
3. **Bayesian Ethics & Security Moat**
   - Validates incoming payloads and outbound URLs against strict domain whitelists and injection filters.
   - Updates trust priors dynamically via **Bayesian Inference** and scores tasks using a multi-objective utility function with Bellman Q-learning updates.

## Repository Layout

```text
Golden-Agent/
├── .github/
│   └── workflows/
│       └── ci.yml                 # Automated pytest & Docker CI workflow
├── golden_agent/
│   └── unified_monolith.py        # Core FastAPI application & mathematical engines
├── tests/
│   └── test_unified_monolith.py   # Pytest verification suite
├── Dockerfile                     # Multi-stage non-root container build
├── requirements.txt               # Python dependency lockfile
└── README.md                      # Project documentation
```

## Quick Start

### 1. Local Installation

```bash
git clone https://github.com/KrypticKode007/Golden-Agent.git
cd Golden-Agent
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

*(Optional)* If you have [Ollama](https://ollama.com) running locally with `llama3`, the monologue generator will automatically connect to `http://localhost:11434` for live reflections; otherwise, it uses built-in deterministic synthesis.

### 2. Run the Server

```bash
uvicorn golden_agent.unified_monolith:app --host 0.0.0.0 --port 8000 --reload
```

### 3. API Endpoints

- **`POST /execute`** — Runs a full cognitive, somatic, and ethical cycle:
  ```bash
  curl -X POST http://localhost:8000/execute \
    -H "Content-Type: application/json" \
    -d '{"prompt": "Analyze system status", "workload_intensity": 0.4}'
  ```
- **`GET /audit`** — Verifies SHA-256 ledger integrity and returns current Q-table and trust priors:
  ```bash
  curl http://localhost:8000/audit
  ```

### 4. Docker Deployment

```bash
docker build -t golden-agent .
docker run -p 8000:8000 golden-agent
```

### 5. Running Tests

```bash
pytest -v
```

## License

This project is licensed under the GPL-3.0 License.
