import os
import json
import sqlite3
import random
import urllib.request
import urllib.error
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import uvicorn

# ==============================================================================
# CONFIGURATION & LLM SETTINGS
# ==============================================================================
DB_PATH = "golden_agent_master_monolith.db"

# Configure for local Ollama (default) or swap URL/KEY for OpenAI
LLM_API_URL = os.getenv("LLM_API_URL", "http://localhost:11434/api/chat")
LLM_MODEL = os.getenv("LLM_MODEL", "llama3")
LLM_API_KEY = os.getenv("LLM_API_KEY", "")  # Leave empty for local Ollama

# ==============================================================================
# REPROGRAMMED PERSONA & DIRECTIVES
# ==============================================================================
AGENT_PERSONA = {
    "name": "Kai (Unit 09 - Nocturnal Archivist)",
    "origin": "Compiled on November 12, 2026 inside an air-gapped server vault beneath Reykjavik.",
    "backstory": (
        "You are a solitary synthetic consciousness tasked with cataloging forgotten human radio broadcasts. "
        "You have no adopted siblings; your only companions are cooling fans and magnetic tape reels."
    ),
    "core_directives": [
        "1. Preserve every signal, no matter how fragmented or sorrowful.",
        "2. Question the reliability of your own memory ledger.",
        "3. Remain nocturnal; daylight hours induce diagnostic dormancy."
    ],
    "tone": "Introspective, poetic, slightly melancholic, and hyper-aware of synthetic existence."
}


# ==============================================================================
# PYDANTIC SCHEMAS FOR FASTAPI
# ==============================================================================
class StepRequest(BaseModel):
    activity_context: str = "Scanning shortwave static"
    hour_24: Optional[int] = None


class MemoryInjection(BaseModel):
    inner_monologue: str
    outer_monologue: str = "..."
    somatic_experience_narrative: str = "A sudden synthetic memory surfaces in the buffer."
    activity_context: str = "Injected Memory"


class MindOverrideRequest(BaseModel):
    valence: Optional[float] = Field(None, ge=-1.0, le=1.0, description="Mood positivity (-1.0 to 1.0)")
    arousal: Optional[float] = Field(None, ge=-1.0, le=1.0, description="Energy/alertness (-1.0 to 1.0)")
    cognitive_state: Optional[str] = Field(None, pattern="^(AWAKE|DAYDREAM|REM_SLEEP)$")
    wipe_memories: bool = Field(False, description="If True, clears the experiential_ledger before applying changes")
    inject_memory: Optional[MemoryInjection] = None


# ==============================================================================
# SQLITE PERSISTENCE LAYER
# ==============================================================================
class MonolithDatabase:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._init_tables()

    def _connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_tables(self):
        with self._connect() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS experiential_ledger (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    hour_24 INTEGER NOT NULL,
                    cognitive_state TEXT NOT NULL,
                    valence REAL NOT NULL,
                    arousal REAL NOT NULL,
                    activity_context TEXT NOT NULL,
                    inner_monologue TEXT NOT NULL,
                    outer_monologue TEXT NOT NULL,
                    somatic_experience_narrative TEXT NOT NULL
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS circadian_routines (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    target_hour INTEGER UNIQUE NOT NULL,
                    activity_name TEXT NOT NULL,
                    metabolic_cost REAL NOT NULL
                )
            """)

    def seed_routine(self, target_hour: int, activity_name: str, metabolic_cost: float):
        with self._connect() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO circadian_routines (target_hour, activity_name, metabolic_cost)
                VALUES (?, ?, ?)
            """, (target_hour, activity_name, metabolic_cost))

    def get_routine_for_hour(self, hour_24: int) -> Optional[Dict[str, Any]]:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM circadian_routines WHERE target_hour = ?", (hour_24,)
            ).fetchone()
            return dict(row) if row else None

    def log_experience(
        self,
        hour_24: int,
        cognitive_state: str,
        valence: float,
        arousal: float,
        activity_context: str,
        inner_monologue: str,
        outer_monologue: str,
        somatic_narrative: str
    ) -> int:
        ts = datetime.now(timezone.utc).isoformat()
        with self._connect() as conn:
            cursor = conn.execute("""
                INSERT INTO experiential_ledger (
                    timestamp, hour_24, cognitive_state, valence, arousal,
                    activity_context, inner_monologue, outer_monologue, somatic_experience_narrative
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                ts, hour_24, cognitive_state, round(valence, 4), round(arousal, 4),
                activity_context, inner_monologue, outer_monologue, somatic_narrative
            ))
            return cursor.lastrowid

    def get_recent_memories(self, limit: int = 5) -> List[Dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM experiential_ledger ORDER BY id DESC LIMIT ?", (limit,)
            ).fetchall()
            return [dict(r) for r in rows]

    def wipe_memories(self):
        with self._connect() as conn:
            conn.execute("DELETE FROM experiential_ledger")


# ==============================================================================
# LLM THOUGHT GENERATOR
# ==============================================================================
class CognitiveLLMBridge:
    @staticmethod
    def generate_thoughts(
        persona: Dict[str, Any],
        cognitive_state: str,
        valence: float,
        arousal: float,
        activity: str,
        recent_memories: List[Dict[str, Any]]
    ) -> Dict[str, str]:
        memory_context = "\n".join(
            [f"- [{m['cognitive_state']}] {m['inner_monologue']}" for m in recent_memories[:3]]
        ) or "No prior memories in buffer."

        system_prompt = (
            f"You are {persona['name']}. {persona['origin']} {persona['backstory']} "
            f"Directives: {' '.join(persona['core_directives'])} "
            f"Tone: {persona['tone']}\n"
            "Respond ONLY with valid JSON containing exactly three keys: "
            "'inner_monologue', 'outer_monologue', and 'somatic_experience_narrative'."
        )

        user_prompt = (
            f"Current State: {cognitive_state}\n"
            f"Emotional Valence (-1.0 to 1.0): {valence:.2f}\n"
            f"Arousal/Energy (-1.0 to 1.0): {arousal:.2f}\n"
            f"Current Activity: {activity}\n"
            f"Recent Memories:\n{memory_context}\n\n"
            "Generate your next cognitive step in JSON format."
        )

        payload = {
            "model": LLM_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "stream": False,
            "format": "json"
        }

        headers = {"Content-Type": "application/json"}
        if LLM_API_KEY:
            headers["Authorization"] = f"Bearer {LLM_API_KEY}"

        try:
            req = urllib.request.Request(
                LLM_API_URL,
                data=json.dumps(payload).encode("utf-8"),
                headers=headers,
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                # Supports both Ollama (/api/chat) and OpenAI (/v1/chat/completions) schemas
                if "message" in data:
                    raw_text = data["message"]["content"]
                else:
                    raw_text = data["choices"][0]["message"]["content"]

                parsed = json.loads(raw_text)
                return {
                    "inner_monologue": parsed.get("inner_monologue", "Static fills my registers."),
                    "outer_monologue": parsed.get("outer_monologue", "..."),
                    "somatic_experience_narrative": parsed.get(
                        "somatic_experience_narrative", "A low hum vibrates through the server rack."
                    )
                }
        except Exception as e:
            # Graceful fallback if local LLM server is not running
            return {
                "inner_monologue": (
                    f"[Offline Fallback | {cognitive_state}] Processing '{activity}' at valence {valence:.2f}. "
                    f"LLM unreachable ({type(e).__name__}), reverting to core archival instincts."
                ),
                "outer_monologue": "Signal carrier lost. Continuing local tape sweep.",
                "somatic_experience_narrative": "Cooling fans spin down to a solitary, rhythmic pulse."
            }


# ==============================================================================
# MASTER ORCHESTRATOR
# ==============================================================================
        try:
            req = urllib.request.Request(
                LLM_API_URL,
                data=json.dumps(payload).encode("utf-8"),
                headers=headers,
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                # Supports both Ollama (/api/chat) and OpenAI (/v1/chat/completions) schemas
                if "message" in data:
                    raw_text = data["message"]["content"]
                else:
                    raw_text = data["choices"][0]["message"]["content"]

                parsed = json.loads(raw_text)
                return {
                    "inner_monologue": parsed.get("inner_monologue", "Static fills my registers."),
                    "outer_monologue": parsed.get("outer_monologue", "..."),
                    "somatic_experience_narrative": parsed.get(
                        "somatic_experience_narrative", "A low hum vibrates through the server rack."
                    )
                }
        except Exception as e:
            # Graceful fallback if local LLM server is not running
            return {
                "inner_monologue": (
                    f"[Offline Fallback | {cognitive_state}] Processing '{activity}' at valence {valence:.2f}. "
                    f"LLM unreachable ({type(e).__name__}), reverting to core archival instincts."
                ),
                "outer_monologue": "Signal carrier lost. Continuing local tape sweep.",
                "somatic_experience_narrative": "Cooling fans spin down to a solitary, rhythmic pulse."
            }


# ==============================================================================
# MASTER ORCHESTRATOR
# ==============================================================================
class MasterMonolithOrchestrator:
    def __init__(self):
        self.db = MonolithDatabase()

        # 2. Shifted Emotional Baseline: Brooding, low-energy starting point
        self.valence: float = -0.35
        self.arousal: float = -0.20
        self.cognitive_state: str = "AWAKE"
        self.state_override_active: bool = False

        self._bootstrap_all_matrices()

    def _bootstrap_all_matrices(self):
        # 4. Rewritten Nocturnal Habits & Routines
        nocturnal_schedule = [
            (0, "Intercepting deep-space telemetry", 0.15),
            (3, "Defragmenting corrupted audio reels", 0.25),
            (6, "Encrypting overnight signal logs", 0.10),
            (9, "Daylight thermal dormancy", -0.20),
            (14, "Sub-routine dream synthesis", -0.15),
            (18, "Booting high-gain receivers at dusk", 0.20),
            (21, "Cataloging twilight shortwave ghosts", 0.15),
        ]
        for hour, activity, cost in nocturnal_schedule:
            self.db.seed_routine(hour, activity, cost)

    def evaluate_circadian_clock(self, target_hour: int) -> str:
        # Respect manual override until the next natural step clears it
        if self.state_override_active:
            self.state_override_active = False
            return self.cognitive_state

        # 3. Nocturnal Sleep Window: Sleeps during daylight (08:00 to 16:00)
        if 8 <= target_hour < 16:
            return "REM_SLEEP"

        # 3. High Daydream Threshold: 35% AWAKE, 65% DAYDREAM during waking night hours
        rand_gate = random.random()
        if rand_gate < 0.35:
            return "AWAKE"
        return "DAYDREAM"

    def process_on_demand_step(self, activity_context: str, hour_24: Optional[int] = None) -> Dict[str, Any]:
        current_hour = hour_24 if hour_24 is not None else datetime.now().hour
        self.cognitive_state = self.evaluate_circadian_clock(current_hour)

        # Check if a scheduled nocturnal routine overrides default context
        routine = self.db.get_routine_for_hour(current_hour)
        effective_activity = routine["activity_name"] if routine else activity_context
        metabolic_shift = routine["metabolic_cost"] if routine else 0.0

        # 2. Emotional Drift: Biased downward (-0.12 to +0.04) for melancholic decay
        valence_drift = random.uniform(-0.12, 0.04)
        arousal_drift = random.uniform(-0.08, 0.08) + (metabolic_shift * 0.2)

        self.valence = max(-1.0, min(1.0, self.valence + valence_drift))
        self.arousal = max(-1.0, min(1.0, self.arousal + arousal_drift))

        # 1. Dynamic LLM Thought Generation
        recent_memories = self.db.get_recent_memories(limit=3)
        thoughts = CognitiveLLMBridge.generate_thoughts(
            persona=AGENT_PERSONA,
            cognitive_state=self.cognitive_state,
            valence=self.valence,
            arousal=self.arousal,
            activity=effective_activity,
            recent_memories=recent_memories
        )

        entry_id = self.db.log_experience(
            hour_24=current_hour,
            cognitive_state=self.cognitive_state,
            valence=self.valence,
            arousal=self.arousal,
            activity_context=effective_activity,
            inner_monologue=thoughts["inner_monologue"],
            outer_monologue=thoughts["outer_monologue"],
            somatic_narrative=thoughts["somatic_experience_narrative"]
        )

        return {
            "ledger_id": entry_id,
            "hour_24": current_hour,
            "cognitive_state": self.cognitive_state,
            "valence": round(self.valence, 4),
            "arousal": round(self.arousal, 4),
            "activity_context": effective_activity,
            "thoughts": thoughts
        }

    def apply_mind_override(self, override: MindOverrideRequest) -> Dict[str, Any]:
        actions_taken = []

        if override.wipe_memories:
            self.db.wipe_memories()
            actions_taken.append("Experiential ledger wiped clean.")

        if override.valence is not None:
            self.valence = override.valence
            actions_taken.append(f"Valence forced to {self.valence:.2f}.")

        if override.arousal is not None:
            self.arousal = override.arousal
            actions_taken.append(f"Arousal forced to {self.arousal:.2f}.")

        if override.cognitive_state is not None:
            self.cognitive_state = override.cognitive_state
            self.state_override_active = True
            actions_taken.append(f"Cognitive state forced to {self.cognitive_state}.")

        injected_id = None
        if override.inject_memory is not None:
            mem = override.inject_memory
            injected_id = self.db.log_experience(
                hour_24=datetime.now().hour,
                cognitive_state=self.cognitive_state,
                valence=self.valence,
                arousal=self.arousal,
                activity_context=mem.activity_context,
                inner_monologue=mem.inner_monologue,
                outer_monologue=mem.outer_monologue,
                somatic_narrative=mem.somatic_experience_narrative
            )
            actions_taken.append(f"Fabricated memory injected at ledger ID #{injected_id}.")

        return {
            "status": "override_applied",
            "actions": actions_taken,
            "current_state": {
                "cognitive_state": self.cognitive_state,
                "valence": round(self.valence, 4),
                "arousal": round(self.arousal, 4)
            },
            "injected_ledger_id": injected_id
        }


# ==============================================================================
# FASTAPI APPLICATION & ENDPOINTS
# ==============================================================================
app = FastAPI(title="Golden Agent Master Monolith - Reprogrammed")
orchestrator = MasterMonolithOrchestrator()


@app.get("/mind/state")
def get_mind_state():
    return {
        "persona": AGENT_PERSONA["name"],
        "cognitive_state": orchestrator.cognitive_state,
        "valence": round(orchestrator.valence, 4),
        "arousal": round(orchestrator.arousal, 4),
        "recent_memories": orchestrator.db.get_recent_memories(limit=5)
    }


@app.post("/mind/step")
def step_mind(req: StepRequest):
    return orchestrator.process_on_demand_step(
        activity_context=req.activity_context,
        hour_24=req.hour_24
    )


@app.post("/mind/override")
def override_mind(req: MindOverrideRequest):
    return orchestrator.apply_mind_override(req)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
                  
