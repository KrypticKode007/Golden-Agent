#!/usr/bin/env python3
"""
GOLDEN-AGENT WEB SERVICE ROUTER & TIMELINE CONTROLLER
Repository: KrypticKode007/Golden-Agent
Architecture: Asynchronous REST API, Time-Rewind Integration & Normal Schedule Lock
"""

import sys
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from golden_agent.time_dilation import ChronoReversalController

app = FastAPI(title="Golden-Agent Quantum Telemetry Core", version="2.1.0")
controller = ChronoReversalController()

class ReversalResponse(BaseModel):
    status: str
    baseline_time: str
    target_origin_time: str
    clamped_valence: float
    clamped_arousal: float
    total_logs_written: int

@app.get("/")
async def get_system_metrics():
    return {
        "status": "ONLINE",
        "schedule_mode": "STANDARD_REALTIME_CLOCK",
        "current_state_vectors": {
            "affective_valence": round(controller.valence, 4),
            "affective_arousal": round(controller.arousal, 4)
        }
    }

@app.post("/timeline/rewind", response_model=ReversalResponse)
async def trigger_timeline_rewind():
    try:
        controller.execute_rewind_protocol()
        stream = controller.ledger.query_reversal_stream()
        return {
            "status": "REWIND_SUCCESS_REALTIME_CLOCK_LOCKED",
            "baseline_time": stream[0]["timestamp"],
            "target_origin_time": stream[-1]["timestamp"],
            "clamped_valence": round(controller.valence, 4),
            "clamped_arousal": round(controller.arousal, 4),
            "total_logs_written": len(stream)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))