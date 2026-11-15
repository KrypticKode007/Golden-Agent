Golden-Agent (Project Kai-007) is an autonomous multi-agent platform and cognitive AI architecture created by KrypticKode007 (Brandon Mark Wilson, Dinuba, CA), running on Linux and Termux environments via a FastAPI gateway on port 8888 [].

Ecosystem Architecture

• Gateway & Auth: Orchestrated through unified_golden_gateway.py and access_key_token.py, utilizing HMAC-SHA256 signature verification (X-Access-Key-Token or Authorization: Bearer <token>) [].
• Core & Cognitive Modules: Features OrganicMindOrchestrator (core.py), somatic kinematics (main_somatic_core.py), circadian memory tracking (daily_experience_engine.py), and a 5-track agent engine in src/golden_agent/ supporting DAG task decomposition and tiered hybrid model routing [].
• Security & Cybernetics: Protected by the -nkryptd AST and regex security moat (with emergency buffer wiping) alongside live self-healing battery telemetry (kai_master_cybernetic.py) [].

Quick Start & Reference Summary

Installation, environment configuration, and repository setup instructions can be accessed directly via the project repository. Core API endpoints cover health checks, file management, reflections, battery telemetry, model execution, and agent task orchestration.
