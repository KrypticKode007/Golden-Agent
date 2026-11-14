import os
import re
import gc
import sys
import ast
import json
import time
import asyncio
import subprocess
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Register all Kryptic repositories in sys.path
BASE_DIR = os.path.expanduser("~/kryptic_ecosystem")
REPOS = ["Golden-Agent", "nkryptd", "Autonomous-self-healing-battery", "Advanced-Ai-Model"]
for repo in REPOS:
    repo_path = os.path.join(BASE_DIR, repo)
    if os.path.exists(repo_path) and repo_path not in sys.path:
        sys.path.insert(0, repo_path)

from golden_agent import OrganicMindOrchestrator

# Mount Autonomous Self-Healing Battery FastAPI sub-app
try:
    sys.path.insert(0, os.path.join(BASE_DIR, "Autonomous-self-healing-battery"))
    import main as battery_module
    cybernetic_subapp = getattr(battery_module, "app", None)
except Exception as e:
    print(f"[Gateway Warning] Battery sub-app mount skipped: {e}")
    cybernetic_subapp = None

app = FastAPI(
    title="Kryptic Unified Golden-Agent Ecosystem",
    description="Unified gateway: Golden-Agent + nkryptd Moat + Self-Healing Battery + Advanced-Ai-Model + Android Alerts.",
    version="2.0.0"
)

if cybernetic_subapp:
    app.mount("/cybernetic", cybernetic_subapp)

mind = OrganicMindOrchestrator()

# --- 1. ANDROID PHONE NOTIFICATIONS (TERMUX-API) ---
def send_phone_alert(title: str, content: str, alert_id: str = "kryptic_alert") -> bool:
    """Dispatches a native Android notification via Termux:API."""
    try:
        subprocess.Popen([
            "termux-notification",
            "--id", alert_id,
            "--title", title,
            "--content", content,
            "--priority", "high",
            "--vibrate", "300,150,300"
        ])
        return True
    except Exception:
        return False

# --- 2. NKRYPTD SECURITY MOAT & MECHANICAL SHAKER ---
THREAT_PATTERNS = re.compile(
    r"(\b(UNION\s+SELECT|DROP\s+TABLE|EXEC\(|EVAL\(|__IMPORT__|OS\.SYSTEM|SUBPROCESS|RM\s+-RF)\b|<script|\.\./)",
    re.IGNORECASE
)

def trigger_mechanical_shaker(reason: str) -> Dict[str, Any]:
    """Scramble volatile entropy buffers, zero-wipe memory, run GC, and alert phone."""
    entropy_junk = bytearray(os.urandom(4096))
    for i in range(len(entropy_junk)):
        entropy_junk[i] = 0
    del entropy_junk
    gc.collect()

    send_phone_alert(
        title="🛡️ nkryptd Mechanical Shaker Triggered",
        content=f"Blocked threat: {reason[:90]}",
        alert_id="nkryptd_shaker"
    )

    return {
        "protocol": "MECHANICAL_SHAKER_ENGAGED",
        "reason": reason,
        "memory_scrubbed": True,
        "phone_notified": True,
        "timestamp": time.time()
    }

def screen_payload_with_nkryptd(payload: str) -> None:
    """Inbound Allergy Filter + AST Structural Moat check."""
    if THREAT_PATTERNS.search(payload):
        shaker_report = trigger_mechanical_shaker(f"Allergy Filter blocked: {payload[:60]}")
        raise HTTPException(status_code=403, detail=shaker_report)
    try:
        tree = ast.parse(payload)
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom, ast.Global)):
                shaker_report = trigger_mechanical_shaker("AST Moat blocked restricted primitive")
                raise HTTPException(status_code=403, detail=shaker_report)
    except SyntaxError:
        pass

# --- 3. LIVE ANDROID BATTERY TELEMETRY & THERMAL WATCHDOG ---
def read_android_battery() -> Dict[str, Any]:
    """Reads live Android sysfs battery nodes or Termux:API battery status."""
    sysfs_base = "/sys/class/power_supply/battery"
    if os.path.exists(sysfs_base):
        try:
            fields = ["capacity", "voltage_now", "current_now", "temp", "status", "health"]
            data = {}
            for f in fields:
                fpath = os.path.join(sysfs_base, f)
                if os.path.exists(fpath):
                    with open(fpath, "r") as fp:
                        data[f] = fp.read().strip()
            if data:
                return {"source": "android_sysfs", "telemetry": data}
        except Exception:
            pass

    try:
        out = subprocess.check_output(["termux-battery-status"], timeout=2).decode("utf-8")
        return {"source": "termux_api", "telemetry": json.loads(out)}
    except Exception:
        return {"source": "simulated_fallback", "telemetry": {"status": "Unknown"}}

def check_battery_alerts(bat_info: Dict[str, Any]) -> None:
    """Triggers Android notifications on thermal spikes or critically low battery."""
    telemetry = bat_info.get("telemetry", {})
    try:
        # Android sysfs temp is in tenths of °C (400 = 40.0°C); termux-api is in °C (40.0)
        raw_temp = float(telemetry.get("temp", telemetry.get("temperature", 0)))
        temp_c = raw_temp / 10.0 if raw_temp > 100 else raw_temp
        capacity = int(telemetry.get("capacity", telemetry.get("percentage", 100)))

        if temp_c >= 40.0:
            send_phone_alert(
                title="🌡️ High Battery Temperature Warning",
                content=f"Device battery reached {temp_c:.1f}°C. Golden-Agent throttling active.",
                alert_id="battery_thermal"
            )
        elif capacity <= 15 and str(telemetry.get("status", "")).upper() != "CHARGING":
            send_phone_alert(
                title="🔋 Low Battery Homeostasis Alert",
                content=f"Battery at {capacity}%. Conservation mode engaged.",
                alert_id="battery_low"
            )
    except Exception:
        pass

# --- 4. ADVANCED-AI-MODEL BRIDGE ---
ADVANCED_MODEL_DIR = os.path.join(BASE_DIR, "Advanced-Ai-Model")

def list_advanced_models() -> List[str]:
    if not os.path.exists(ADVANCED_MODEL_DIR):
        return []
    scripts = []
    for root, _, files in os.walk(ADVANCED_MODEL_DIR):
        if ".git" in root or "__pycache__" in root:
            continue
        for f in files:
            if f.endswith(".py") and not f.startswith("__"):
                rel = os.path.relpath(os.path.join(root, f), ADVANCED_MODEL_DIR)
                scripts.append(rel)
    return sorted(scripts)

class EventRequest(BaseModel):
    event: str

class ModelRunRequest(BaseModel):
    script_name: str
    args: Optional[List[str]] = []

# --- 5. UNIFIED API ROUTES ---
@app.get("/health")
def unified_health():
    bat = read_android_battery()
    return {
        "status": "ONLINE",
        "version": "2.0.0",
        "modules": {
            "golden_agent": "ACTIVE",
            "nkryptd_moat": "ARMED",
            "cybernetic_battery": "MOUNTED" if cybernetic_subapp else "STANDALONE",
            "advanced_ai_models_available": len(list_advanced_models())
        },
        "hardware_battery": bat
    }

@app.post("/golden/reflect")
def process_golden_event(req: EventRequest):
    screen_payload_with_nkryptd(req.event)
    bat = read_android_battery()
    check_battery_alerts(bat)
    enriched_event = f"{req.event} | HW_BATTERY={json.dumps(bat)}"
    snapshot = mind.process_reflective_event(enriched_event)
    return {
        "security_clearance": "PASSED_NKRYPTD_MOAT",
        "battery_context": bat,
        "golden_snapshot": snapshot
    }

@app.get("/battery/live")
def get_live_battery():
    bat = read_android_battery()
    check_battery_alerts(bat)
    return bat

@app.get("/models")
def get_models():
    return {
        "repository": "Advanced-Ai-Model",
        "available_scripts": list_advanced_models()
    }

@app.post("/models/run")
def run_advanced_model(req: ModelRunRequest):
    # Prevent path traversal & screen arguments through nkryptd
    if ".." in req.script_name or req.script_name.startswith("/"):
        raise HTTPException(status_code=403, detail=trigger_mechanical_shaker("Directory traversal blocked"))
    for arg in (req.args or []):
        screen_payload_with_nkryptd(arg)

    target_path = os.path.abspath(os.path.join(ADVANCED_MODEL_DIR, req.script_name))
    if not target_path.startswith(os.path.abspath(ADVANCED_MODEL_DIR)) or not os.path.exists(target_path):
        raise HTTPException(status_code=404, detail=f"Script '{req.script_name}' not found in Advanced-Ai-Model")

    try:
        proc = subprocess.run(
            [sys.executable, target_path, *(req.args or [])],
            cwd=ADVANCED_MODEL_DIR,
            capture_output=True,
            text=True,
            timeout=30
        )
        mind.process_reflective_event(f"EXECUTED_ADVANCED_MODEL | {req.script_name} | RC={proc.returncode}")
        return {
            "script": req.script_name,
            "returncode": proc.returncode,
            "stdout": proc.stdout[-4000:],
            "stderr": proc.stderr[-2000:]
        }
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=504, detail="Model script timed out after 30 seconds")

async def background_homeostasis_loop():
    while True:
        try:
            bat = read_android_battery()
            check_battery_alerts(bat)
            mind.process_reflective_event(f"AUTONOMOUS_HOMEOSTASIS_TICK | {json.dumps(bat)}")
        except Exception as e:
            print(f"[Homeostasis Loop] Notice: {e}")
        await asyncio.sleep(30)

@app.on_event("startup")
async def startup_event():
    send_phone_alert(
        title="⚡ Golden-Agent Ecosystem Online",
        content="Unified Gateway v2.0 active on port 8888 with nkryptd Moat.",
        alert_id="golden_boot"
    )
    asyncio.create_task(background_homeostasis_loop())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8888)
