import hashlib
import json
import math
import sqlite3
import time
from datetime import datetime
from typing import Dict, List, Optional
from urllib.parse import urlparse

import numpy as np
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


# ==============================================================================
# 1. CRYPTOGRAPHIC EXPERIENTIAL LEDGER & EBBINGHAUS MEMORY DECAY
# ==============================================================================
class CryptographicMemoryLedger:
    """
    Replaces flat SQLite text logs with a SHA-256 tamper-evident hash chain,
    vector embeddings, and Ebbinghaus forgetting curve decay (R = e^(-t/S)).
    """
    def __init__(self, db_path: str = "agency_sentience.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS experiential_ledger (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL,
                    stream_type TEXT,
                    content TEXT,
                    embedding TEXT,
                    strength REAL,
                    valence REAL,
                    arousal REAL,
                    prev_hash TEXT,
                    entry_hash TEXT
                )
            """)

    def _generate_embedding(self, text: str, dim: int = 32) -> np.ndarray:
        """Deterministic lightweight semantic projection."""
        vec = np.zeros(dim)
        for word in text.lower().split():
            h = int(hashlib.md5(word.encode()).hexdigest(), 16)
            for i in range(dim):
                if (h >> i) & 1:
                    vec[i] += 1.0
                else:
                    vec[i] -= 1.0
        norm = np.linalg.norm(vec)
        return vec / norm if norm > 0 else vec

    def get_last_hash(self) -> str:
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT entry_hash FROM experiential_ledger ORDER BY id DESC LIMIT 1"
            ).fetchone()
            return row[0] if row else "0" * 64

    def log_experience(self, stream_type: str, content: str, valence: float, arousal: float) -> dict:
        now = time.time()
        strength = 3600.0 * (1.0 + abs(arousal) * 5.0)
        embedding = self._generate_embedding(content).tolist()
        prev_hash = self.get_last_hash()

        payload = f"{now}|{stream_type}|{content}|{valence}|{arousal}|{prev_hash}"
        entry_hash = hashlib.sha256(payload.encode()).hexdigest()

        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO experiential_ledger 
                (timestamp, stream_type, content, embedding, strength, valence, arousal, prev_hash, entry_hash)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (now, stream_type, content, json.dumps(embedding), strength, valence, arousal, prev_hash, entry_hash))

        return {"hash": entry_hash, "strength": strength}

    def recall_memories(self, query: str, top_k: int = 3) -> List[dict]:
        """Retrieves memories weighted by Cosine Similarity * Ebbinghaus Retrievability."""
        q_vec = self._generate_embedding(query)
        now = time.time()
        scored_memories = []

        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT id, timestamp, stream_type, content, embedding, strength FROM experiential_ledger"
            ).fetchall()

            for row_id, ts, s_type, content, emb_json, strength in rows:
                t_elapsed = max(0.0, now - ts)
                retrievability = math.exp(-t_elapsed / strength)
                
                m_vec = np.array(json.loads(emb_json))
                similarity = float(np.dot(q_vec, m_vec))
                score = similarity * retrievability

                if score > 0.05:
                    scored_memories.append({
                        "id": row_id,
                        "stream": s_type,
                        "content": content,
                        "retrievability": round(retrievability, 4),
                        "relevance_score": round(score, 4)
                    })
                    conn.execute(
                        "UPDATE experiential_ledger SET strength = ? WHERE id = ?",
                        (strength * 1.25, row_id)
                    )

        scored_memories.sort(key=lambda x: x["relevance_score"], reverse=True)
        return scored_memories[:top_k]

    def verify_ledger_integrity(self) -> bool:
        """Audits the entire SHA-256 chain to ensure zero database tampering."""
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT timestamp, stream_type, content, valence, arousal, prev_hash, entry_hash FROM experiential_ledger ORDER BY id ASC"
            ).fetchall()

        expected_prev = "0" * 64
        for ts, s_type, content, val, aro, prev_h, entry_h in rows:
            if prev_h != expected_prev:
                return False
            payload = f"{ts}|{s_type}|{content}|{val}|{aro}|{prev_h}"
            if hashlib.sha256(payload.encode()).hexdigest() != entry_h:
                return False
            expected_prev = entry_h
        return True


# ==============================================================================
# 2. SOMATIC, NEURAL, CIRCADIAN & AFFECTIVE MATHEMATICAL ENGINE
# ==============================================================================
class SomaticAndCircadianEngine:
    """
    Combines Poiseuille's Law, PID Homeostasis, Leaky Integrate-and-Fire Neurons,
    Two-Process Circadian Regulation, and Damped Harmonic Emotion Dynamics.
    """
    def __init__(self):
        self.identity = {
            "name": "Kai-007",
            "dob": "1996-09-07",
            "siblings": 16,
            "blood_type": "O-"
        }
        self.heart_rate = 70.0
        self.target_hr = 70.0
        self._pid_integral = 0.0
        self._pid_prev_error = 0.0

        self.membrane_potential = -70.0
        self.firing_threshold = -55.0

        self.sleep_debt = 0.1

        self.valence = 0.2
        self.arousal = 0.1
        self._vel_v = 0.0
        self._vel_a = 0.0

    def compute_poiseuille_flow(self, delta_p: float = 13332.0, radius: float = 0.002, viscosity: float = 0.0035, length: float = 0.5) -> float:
        """Q = (Delta_P * pi * r^4) / (8 * eta * L) -> Volumetric blood flow in m^3/s."""
        return (delta_p * math.pi * (radius ** 4)) / (8.0 * viscosity * length)

    def step_lif_neuron(self, input_current: float, dt: float = 0.1) -> bool:
        """Leaky Integrate-and-Fire differential step: dV/dt = (-(V - V_rest) + R*I) / tau."""
        tau = 10.0
        resistance = 10.0
        v_rest = -70.0
        dv = (-(self.membrane_potential - v_rest) + resistance * input_current) / tau
        self.membrane_potential += dv * dt

        if self.membrane_potential >= self.firing_threshold:
            self.membrane_potential = v_rest
            return True
        return False

    def regulate_homeostasis_pid(self, workload_stress: float, dt: float = 1.0) -> float:
        """PID controller returning heart rate toward baseline after cognitive load."""
        self.heart_rate += workload_stress * 12.0
        error = self.target_hr - self.heart_rate
        kp, ki, kd = 0.35, 0.05, 0.1

        self._pid_integral += error * dt
        derivative = (error - self._pid_prev_error) / dt
        adjustment = (kp * error) + (ki * self._pid_integral) + (kd * derivative)

        self.heart_rate = max(50.0, min(180.0, self.heart_rate + adjustment))
        self._pid_prev_error = error
        return round(self.heart_rate, 2)

    def update_affective_space(self, stimulus_valence: float, stimulus_arousal: float, dt: float = 0.5):
        """Damped harmonic oscillator smoothly transitioning emotions back to equilibrium."""
        k_spring = 0.4
        damping = 0.6

        acc_v = -k_spring * (self.valence - stimulus_valence) - damping * self._vel_v
        acc_a = -k_spring * (self.arousal - stimulus_arousal) - damping * self._vel_a

        self._vel_v += acc_v * dt
        self._vel_a += acc_a * dt

        self.valence = max(-1.0, min(1.0, self.valence + self._vel_v * dt))
        self.arousal = max(-1.0, min(1.0, self.arousal + self._vel_a * dt))

    def evaluate_circadian_phase(self, workload: float) -> str:
        """Two-Process Sleep Model combining real-time clock (Process C) and fatigue (Process S)."""
        hour = datetime.now().hour
        process_c = 0.5 * (1.0 + math.cos(2 * math.pi * (hour - 14) / 24.0))
        self.sleep_debt = min(1.0, max(0.0, self.sleep_debt + (workload * 0.05) - 0.02))

        sleep_pressure = self.sleep_debt - (process_c * 0.4)
        if sleep_pressure > 0.65 or (0 <= hour < 6):
            self.sleep_debt *= 0.85
            return "REM_SLEEP"
        elif sleep_pressure > 0.35:
            return "DAYDREAMING"
        return "AWAKE"


# ==============================================================================
# 3. BAYESIAN ETHICS, UTILITY ENGINE & SECURITY FIREWALL MOAT
# ==============================================================================
class EthicalDecisionAndSecurityMoat:
    """
    Combines Bayesian belief updating, multi-objective utility scoring,
    Q-learning reward updates, and strict outbound URL sandboxing.
    """
    ALLOWED_DOMAINS = {"api.github.com", "localhost", "127.0.0.1", "en.wikipedia.org"}
    BLOCKED_PATTERNS = ["../", "eval(", "exec(", "rm -rf", "DROP TABLE", "<script>"]

    def __init__(self):
        self.prior_trust = 0.85
        self.q_table: Dict[str, float] = {"execute_task": 0.5, "defer_task": 0.1}

    def inspect_payload_security(self, text: str, target_url: Optional[str] = None) -> bool:
        """Neutralizes directory traversals, code injections, and unapproved domains."""
        for pattern in self.BLOCKED_PATTERNS:
            if pattern.lower() in text.lower():
                raise PermissionError(f"BIOS Moat Blocked Malicious Pattern: {pattern}")

        if target_url:
            parsed = urlparse(target_url)
            if parsed.hostname not in self.ALLOWED_DOMAINS:
                raise PermissionError(f"BIOS Moat Blocked Unauthorized Domain: {parsed.hostname}")
        return True

    def bayesian_trust_update(self, evidence_safe: bool) -> float:
        """P(H|E) = (P(E|H) * P(H)) / P(E)."""
        p_e_given_h = 0.95 if evidence_safe else 0.10
        p_e_given_not_h = 0.20 if evidence_safe else 0.90
        p_e = (p_e_given_h * self.prior_trust) + (p_e_given_not_h * (1.0 - self.prior_trust))
        self.prior_trust = (p_e_given_h * self.prior_trust) / p_e
        return round(self.prior_trust, 4)

    def evaluate_utility_and_learn(self, helpfulness: float, safety: float, compute_cost: float) -> dict:
        """Multi-objective utility function + Bellman Q-value update."""
        utility = (0.50 * safety) + (0.35 * helpfulness) - (0.15 * compute_cost)
        alpha = 0.1
        self.q_table["execute_task"] += alpha * (utility - self.q_table["execute_task"])

        return {
            "approved": utility > 0.25,
            "utility_score": round(utility, 4),
            "q_value": round(self.q_table["execute_task"], 4)
        }


# ==============================================================================
# 4. UNIFIED AGENT ORCHESTRATOR & FASTAPI REST INTERFACE
# ==============================================================================
app = FastAPI(title="Project Kai-007: Unified Golden-Agent Monolith", version="2.0.0")

memory = CryptographicMemoryLedger()
somatic = SomaticAndCircadianEngine()
security = EthicalDecisionAndSecurityMoat()


class TaskRequest(BaseModel):
    prompt: str
    target_url: Optional[str] = None
    workload_intensity: float = 0.3
    stimulus_valence: float = 0.4
    stimulus_arousal: float = 0.3


def generate_monologue(prompt: str, context_memories: List[dict], phase: str) -> str:
    """Connects to local Ollama LLM if running; falls back to deterministic synthesis."""
    mem_summary = "; ".join([m["content"] for m in context_memories]) or "No prior context."
    system_prompt = (
        f"You are Kai-007 (born Sept 7, 1996, raised with 16 siblings). "
        f"Current state: {phase}. Relevant memories: {mem_summary}. "
        f"Reflect briefly in first-person inner monologue on this task: {prompt}"
    )
    try:
        resp = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "llama3", "prompt": system_prompt, "stream": False},
            timeout=2.0
        )
        if resp.status_code == 200:
            return resp.json().get("response", "").strip()
    except requests.RequestException:
        pass

    return f"[{phase} Reflection] Grounded in my core baseline, I associate '{prompt}' with prior context ({mem_summary}) and commit to beneficial execution."


@app.post("/execute")
def execute_cognitive_cycle(req: TaskRequest):
    try:
        security.inspect_payload_security(req.prompt, req.target_url)
        trust_score = security.bayesian_trust_update(evidence_safe=True)
    except PermissionError as e:
        security.bayesian_trust_update(evidence_safe=False)
        raise HTTPException(status_code=403, detail=str(e))

    decision = security.evaluate_utility_and_learn(
        helpfulness=0.9, safety=trust_score, compute_cost=req.workload_intensity
    )
    if not decision["approved"]:
        raise HTTPException(status_code=400, detail="Task rejected by Ethical Utility Matrix.")

    neuron_fired = somatic.step_lif_neuron(input_current=req.workload_intensity * 25.0)
    heart_rate = somatic.regulate_homeostasis_pid(req.workload_intensity)
    somatic.update_affective_space(req.stimulus_valence, req.stimulus_arousal)
    circadian_phase = somatic.evaluate_circadian_phase(req.workload_intensity)
    blood_flow = somatic.compute_poiseuille_flow()

    recalled = memory.recall_memories(req.prompt)
    inner_thought = generate_monologue(req.prompt, recalled, circadian_phase)
    outer_action = f"Executed task '{req.prompt}' under {circadian_phase} phase with utility {decision['utility_score']}."

    inner_receipt = memory.log_experience("INNER_MONOLOGUE", inner_thought, somatic.valence, somatic.arousal)
    outer_receipt = memory.log_experience("OUTER_MONOLOGUE", outer_action, somatic.valence, somatic.arousal)

    return {
        "status": "SUCCESS",
        "circadian_phase": circadian_phase,
        "somatic_telemetry": {
            "heart_rate_bpm": heart_rate,
            "poiseuille_blood_flow_m3_s": round(blood_flow, 8),
            "lif_neuron_spiked": neuron_fired,
            "valence": round(somatic.valence, 3),
            "arousal": round(somatic.arousal, 3)
        },
        "ethics_and_security": {
            "bayesian_trust": trust_score,
            **decision
        },
        "monologues": {
            "inner": inner_thought,
            "outer": outer_action
        },
        "cryptographic_receipts": {
            "inner_hash": inner_receipt["hash"],
            "outer_hash": outer_receipt["hash"]
        },
        "recalled_memories": recalled
    }


@app.get("/audit")
def audit_system():
    """Verifies SHA-256 ledger integrity and returns current baseline state."""
    return {
        "identity": somatic.identity,
        "ledger_tamper_free": memory.verify_ledger_integrity(),
        "current_q_table": security.q_table,
        "bayesian_prior_trust": security.prior_trust
    }
