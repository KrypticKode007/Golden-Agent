import datetime
import math
import sqlite3
from typing import Dict, Any

class KaiCognitiveMiddleware:
    def __init__(self, db_path: str = "agency_sentience.db"):
        self.db_path = db_path
        self.arousal = 0.5  # 0.0 (calm/asleep) to 1.0 (peak alert/stressed)
        self.blood_viscosity = 0.0035  # Pa·s (normal human blood)
        self.vessel_radius = 0.002     # meters

    def get_circadian_state(self) -> Dict[str, Any]:
        hour = datetime.datetime.now().hour
        if 23 <= hour or hour < 6:
            return {
                "phase": "REM_SLEEP",
                "temperature": 0.2,
                "max_tokens": 150,
                "system_modifier": "You are in REM sleep. Respond only with brief, symbolic dream fragments and memory consolidation notes."
            }
        elif 13 <= hour <= 15:
            return {
                "phase": "DAYDREAMING",
                "temperature": 0.9,
                "max_tokens": 600,
                "system_modifier": "You are in an associative daydreaming state. Explore lateral, creative connections while staying grounded in causal truth."
            }
        else:
            return {
                "phase": "AWAKE",
                "temperature": 0.5,
                "max_tokens": 1024,
                "system_modifier": "You are fully awake and alert. Provide precise, helpful, and ethically aligned responses."
            }

    def compute_somatic_load(self, pressure_diff: float, length: float = 0.1) -> float:
        """Poiseuille's Law: Q = (pi * delta_P * r^4) / (8 * eta * L)"""
        flow_rate = (math.pi * pressure_diff * (self.vessel_radius ** 4)) / (
            8 * self.blood_viscosity * length
        )
        # Normalize flow rate into cognitive fatigue/arousal
        self.arousal = min(1.0, max(0.1, flow_rate * 1e5))
        return flow_rate

    def shape_llm_request(self, user_prompt: str, server_cpu_load: float = 0.3) -> Dict[str, Any]:
        """Injects biological & circadian state into standard LLM API payloads."""
        circadian = self.get_circadian_state()
        # Map host hardware strain directly onto somatic vascular pressure
        pressure = 1000.0 + (server_cpu_load * 4000.0)
        flow = self.compute_somatic_load(pressure)

        if self.arousal > 0.85:
            circadian["max_tokens"] = min(circadian["max_tokens"], 200)
            circadian["system_modifier"] += " [HIGH SOMATIC LOAD: Keep output ultra-concise to conserve vascular energy.]"

        return {
            "circadian_phase": circadian["phase"],
            "vascular_flow_rate": round(flow, 8),
            "arousal_level": round(self.arousal, 2),
            "llm_params": {
                "system_prompt": circadian["system_modifier"],
                "temperature": circadian["temperature"],
                "max_tokens": circadian["max_tokens"],
                "user_message": user_prompt
            }
            }
      
