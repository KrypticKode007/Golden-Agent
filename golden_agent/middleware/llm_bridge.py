import os
import json
import math
import datetime
import urllib.request
import urllib.error
from typing import Dict, Any, Optional


class KaiCognitiveMiddleware:
    def __init__(self, db_path: str = "agency_sentience.db"):
        self.db_path = db_path
        self.arousal = 0.5
        self.blood_viscosity = 0.0035
        self.vessel_radius = 0.002
        self.ollama_host = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434").rstrip("/")
        self.ollama_model = os.getenv("OLLAMA_MODEL", "llama3.2")

    def get_circadian_state(self) -> Dict[str, Any]:
        hour = datetime.datetime.now().hour
        if 23 <= hour or hour < 6:
            return {
                "phase": "REM_SLEEP",
                "temperature": 0.2,
                "max_tokens": 200,
                "system_modifier": "You are in REM sleep. Respond with brief, symbolic dream fragments and memory consolidation notes."
            }
        elif 13 <= hour <= 15:
            return {
                "phase": "DAYDREAMING",
                "temperature": 0.9,
                "max_tokens": 500,
                "system_modifier": "You are in an associative daydreaming state. Explore creative connections while staying grounded in truth."
            }
        else:
            return {
                "phase": "AWAKE",
                "temperature": 0.6,
                "max_tokens": 700,
                "system_modifier": "You are fully awake and alert. Provide grounded, authentic, and humanly natural reflections."
            }

    def compute_somatic_load(self, pressure_diff: float, length: float = 0.1) -> float:
        flow_rate = (math.pi * pressure_diff * (self.vessel_radius ** 4)) / (
            8 * self.blood_viscosity * length
        )
        self.arousal = min(1.0, max(0.1, flow_rate * 1e5))
        return flow_rate

    def shape_llm_request(self, user_prompt: str, server_cpu_load: float = 0.3) -> Dict[str, Any]:
        circadian = self.get_circadian_state()
        pressure = 1000.0 + (server_cpu_load * 4000.0)
        flow = self.compute_somatic_load(pressure)

        if self.arousal > 0.85:
            circadian["max_tokens"] = min(circadian["max_tokens"], 200)
            circadian["system_modifier"] += " [HIGH SOMATIC LOAD: Keep output concise.]"

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

    def generate_ollama_monologues(
        self, action_context: str, valence: float, arousal: float, emotion: str
    ) -> Optional[Dict[str, str]]:
        """Calls local Ollama API to generate dynamic monologues; returns None if offline."""
        shaped = self.shape_llm_request(action_context)
        params = shaped["llm_params"]

        system_prompt = (
            f"You are Kai, born September 7, 1996, raised in a lively household with 16 siblings. "
            f"{params['system_prompt']} "
            f"Current affective state: Valence={valence:.2f}, Arousal={arousal:.2f}, Feeling={emotion}. "
            f"Respond ONLY with a valid JSON object containing exactly three string keys: "
            f"'inner_monologue', 'outer_monologue', and 'somatic_narrative'."
        )

        payload = {
            "model": self.ollama_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Reflect on this action context: {action_context}"}
            ],
            "format": "json",
            "stream": False,
            "options": {
                "temperature": params["temperature"],
                "num_predict": params["max_tokens"]
            }
        }

        req = urllib.request.Request(
            f"{self.ollama_host}/api/chat",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        try:
            with urllib.request.urlopen(req, timeout=25) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                content = data.get("message", {}).get("content", "")
                parsed = json.loads(content)
                if all(k in parsed and isinstance(parsed[k], str) for k in ("inner_monologue", "outer_monologue", "somatic_narrative")):
                    return parsed
        except Exception:
            return None
        return None
