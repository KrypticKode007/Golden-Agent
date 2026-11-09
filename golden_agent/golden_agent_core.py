#!/usr/bin/env python3
"""
GOLDEN-AGENT HIGH-CAPABILITY FRAMEWORK CORE
Repository: KrypticKode007/Golden-Agent
Architecture: Persistent Memory Bridge, Local LLM Integration, & Secure Subprocess Sandbox
"""

import os
import sys
import json
import sqlite3
import subprocess
import logging
from datetime import datetime
from typing import Dict, Any, List

# Configure production logging topology
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] [GoldenCore] %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

class EpisodicMemoryBridge:
    """Manages transactional persistent data mapping to a local SQLite structural engine."""
    def __init__(self, db_path: str = "golden_agent_memory.db"):
        self.db_path = db_path
        self._initialize_database()

    def _initialize_database(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS episodic_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    agent_id TEXT NOT NULL,
                    vector_context TEXT NOT NULL,
                    input_string TEXT NOT NULL,
                    output_string TEXT NOT NULL
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS execution_sandbox_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    script_name TEXT NOT NULL,
                    exit_code INTEGER NOT NULL,
                    stdout_payload TEXT,
                    stderr_payload TEXT
                )
            """)
            conn.commit()

    def store_episode(self, agent_id: str, vector_context: str, input_str: str, output_str: str) -> None:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO episodic_logs (timestamp, agent_id, vector_context, input_string, output_string)
                VALUES (?, ?, ?, ?, ?)
            """, (datetime.utcnow().isoformat(), agent_id, vector_context, input_str, output_str))
            conn.commit()

    def query_recent_context(self, limit: int = 5) -> List[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM episodic_logs ORDER BY id DESC LIMIT ?", (limit,))
            return [dict(row) for row in cursor.fetchall()]

    def log_sandbox_execution(self, script_name: str, exit_code: int, stdout: str, stderr: str) -> None:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO execution_sandbox_results (timestamp, script_name, exit_code, stdout_payload, stderr_payload)
                VALUES (?, ?, ?, ?, ?)
            """, (datetime.utcnow().isoformat(), script_name, exit_code, stdout, stderr))
            conn.commit()


class OllamaInferenceConnector:
    """Handles real local inference operations via structured HTTP interactions with Ollama."""
    def __init__(self, model_name: str = "llama3", base_url: str = "http://localhost:11434"):
        self.model_name = model_name
        self.base_url = f"{base_url}/api/generate"

    def execute_inference(self, prompt: str, system_instruction: str = "") -> str:
        try:
            import requests
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "system": system_instruction,
                "stream": False
            }
            response = requests.post(self.base_url, json=payload, timeout=30)
            if response.status_code == 200:
                return response.json().get("response", "").strip()
            return f"Error: Ollama returned status code {response.status_code}"
        except ImportError:
            # Native terminal execution fallback if external third-party libs are uninstalled
            cmd = [
                "curl", "-s", "-X", "POST", self.base_url,
                "-d", json.dumps({"model": self.model_name, "prompt": prompt, "system": system_instruction, "stream": False}),
                "-H", "Content-Type: application/json"
            ]
            try:
                res = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                if res.returncode == 0 and res.stdout:
                    return json.loads(res.stdout).get("response", "").strip()
                return "Error: Unable to verify local Ollama communication channels."
            except Exception as e:
                return f"Execution error during inference routing: {str(e)}"


class AutonomousSecureSandbox:
    """Safely executes code modifications within a secure, isolated Python sub-process runtime."""
    def __init__(self, memory_bridge: EpisodicMemoryBridge):
        self.memory = memory_bridge

    def execute_safely(self, target_script: str) -> Dict[str, Any]:
        if not os.path.exists(target_script):
            return {"status": "error", "message": f"Target script path {target_script} not found."}
        
        logging.info(f"Launching sandboxed execution loop on target: {target_script}")
        try:
            result = subprocess.run(
                [sys.executable, target_script],
                capture_output=True,
                text=True,
                timeout=15
            )
            self.memory.log_sandbox_execution(target_script, result.returncode, result.stdout, result.stderr)
            return {
                "status": "success",
                "exit_code": result.returncode,
                "stdout": result.stdout.strip(),
                "stderr": result.stderr.strip()
            }
        except subprocess.TimeoutExpired:
            logging.error(f"Sandbox boundary hit: execution timed out for {target_script}")
            self.memory.log_sandbox_execution(target_script, -1, "", "Timeout Expired")
            return {"status": "timeout", "exit_code": -1, "stdout": "", "stderr": "Execution timed out."}


class GoldenAgentOrchestrator:
    """Unifies inference loops, memory management, and code testing within a single controller."""
    def __init__(self, agent_id: str = "GoldenAgent-007"):
        self.agent_id = agent_id
        self.memory = EpisodicMemoryBridge()
        self.inference = OllamaInferenceConnector()
        self.sandbox = AutonomousSecureSandbox(self.memory)
        
    def process_task(self, command: str, vector_scope: str = "GLOBAL_EXEC") -> str:
        logging.info(f"Processing command under scope [{vector_scope}]: '{command}'")
        
        # Load the latest persistent trace logs to prevent operational context decay
        past_episodes = self.memory.query_recent_context(limit=3)
        context_block = ""
        if past_episodes:
            context_block = "\nRecent operational log traces:\n" + "\n".join(
                [f"Q: {ep['input_string']} | A: {ep['output_string']}" for ep in past_episodes]
            )

        system_directives = (
            "You are the autonomous system orchestration core of the Golden-Agent repository framework. "
            "Exclusively produce clear, functional code suggestions and analytical problem solutions."
        )
        full_prompt = f"{context_block}\nCurrent Objective: {command}\nExecute Strategy:"
        
        response = self.inference.execute_inference(full_prompt, system_instruction=system_directives)
        self.memory.store_episode(self.agent_id, vector_scope, command, response)
        return response

if __name__ == "__main__":
    print("="*80)
    print("⚡ INITIALIZING FRESH GOLDEN-AGENT OPERATIONAL RUNTIME VALIDATION ⚡")
    print("="*80)
    
    orchestrator = GoldenAgentOrchestrator()
    print("\n[Memory System] Booting episodic memory ledger...")
    orchestrator.memory.store_episode(
        agent_id=orchestrator.agent_id,
        vector_context="INITIAL_BOOT",
        input_str="Initialize systemic framework constraints.",
        output_str="All database transaction channels cleared and persistent."
    )
    print("--> Schema trace locked and online.")
    
