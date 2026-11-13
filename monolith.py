import os
import json
import math
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

LLM_API_URL = os.getenv("LLM_API_URL", "http://localhost:11434/api/chat")
LLM_MODEL = os.getenv("LLM_MODEL", "llama3")
LLM_API_KEY = os.getenv("LLM_API_KEY", "")

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
                    somatic_experience_narrative TEXT NOT NULL,
                    motor_plan_json TEXT NOT NULL
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
        somatic_narrative: str,
        motor_plan: Dict[str, Any]
    ) -> int:
        ts = datetime.now(timezone.utc).isoformat()
        with self._connect() as conn:
            cursor = conn.execute("""
                INSERT INTO experiential_ledger (
                    timestamp, hour_24, cognitive_state, valence, arousal,
                    activity_context, inner_monologue, outer_monologue,
                    somatic_experience_narrative, motor_plan_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                ts, hour_24, cognitive_state, round(valence, 4), round(arousal, 4),
                activity_context, inner_monologue, outer_monologue,
                somatic_narrative, json.dumps(motor_plan)
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
# FLUENT SOMATIC & KINEMATIC BODY ENGINE
# ==============================================================================
class FluentBodyKinematics:
    """
    Translates the mind's intent, emotional valence, arousal, and consciousness
    state into smooth, natural joint trajectories and organic motion curves.
    """

    def __init__(self):
        # Current joint angles in degrees (smoothly interpolated on each thought)
        self.joints: Dict[str, float] = {
            "head_pitch": -5.0,
            "head_yaw": 0.0,
            "head_roll": 0.0,
            "spine_arch": -4.0,
            "shoulder_left_pitch": 10.0,
            "shoulder_right_pitch": 10.0,
            "elbow_left_flex": 25.0,
            "elbow_right_flex": 25.0,
            "wrist_left_supination": 0.0,
            "wrist_right_supination": 0.0,
            "breath_cycle_hz": 0.22
        }
        self.current_posture: str = "seated_archivist_slouch"
        self.active_gesture: str = "idle_breathing"
        self.gaze_target: str = "oscilloscope_screen"
        self.fluidity_curve: str = "cubic_ease_in_out"
        self.movement_speed: float = 0.45

    @staticmethod
    def _smooth_lerp(current: float, target: float, smoothing_factor: float) -> float:
        """Applies organic damping so joints glide rather than snap."""
        return round(current + (target - current) * smoothing_factor, 2)

    def synthesize_movement(
        self,
        cognitive_state: str,
        valence: float,
        arousal: float,
        llm_motor_intent: Dict[str, Any]
    ) -> Dict[str, Any]:
        # 1. Calculate organic movement physics from emotion
        # Higher arousal = faster velocity; lower valence = heavier, slower damping
        raw_speed = 0.5 + (arousal * 0.35) + (valence * 0.15)
        self.movement_speed = round(max(0.10, min(1.0, raw_speed)), 3)

        # Smoothing factor controls how fluidly the body transitions toward the new pose
        smoothing = max(0.15, min(0.75, self.movement_speed * 0.65))

        # 2. Determine baseline posture offsets from valence (slump vs upright)
        emotional_spine_bias = valence * 12.0   # -12 deg slump to +12 deg upright
        emotional_head_pitch = valence * 10.0   # Downcast when sad, lifted when positive

        # 3. Apply consciousness state overrides (REM_SLEEP, DAYDREAM, AWAKE)
        if cognitive_state == "REM_SLEEP":
            self.current_posture = "dormant_reclined_rest"
            self.active_gesture = "autonomic_rem_micro_twitch"
            self.gaze_target = "eyelids_closed"
            self.fluidity_curve = "sine_wave_autonomic"
            target_joints = {
                "head_pitch": -18.0,
                "head_yaw": round(random.uniform(-6.0, 6.0), 1),
                "head_roll": 8.0,
                "spine_arch": -14.0,
                "shoulder_left_pitch": 2.0,
                "shoulder_right_pitch": 2.0,
                "elbow_left_flex": 15.0,
                "elbow_right_flex": 15.0,
                "wrist_left_supination": round(random.uniform(-3.0, 3.0), 1),
                "wrist_right_supination": round(random.uniform(-3.0, 3.0), 1),
                "breath_cycle_hz": 0.16
            }
        elif cognitive_state == "DAYDREAM":
            self.current_posture = "unfocused_drifting_sway"
            for self.active_gesture = llm_motor_intent.get("gesture", "slow_hand_drift")
           
        def step_mind(req: StepRequest):
return orchestrator.process_on_demand_step(
activity_context=req.activity_context,
hour_24=req.hour_24
)
@app.post("/mind/override")
def override_mind(req: MindOverrideRequest):
return orchestrator.apply_mind_override(req)
if name == "main":
uvicorn.run(app, host="0.0.0.0", port=8000) 
