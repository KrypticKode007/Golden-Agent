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
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel

BASE_DIR = os.path.expanduser("~/kryptic_ecosystem")
REPOS = ["Golden-Agent", "nkryptd", "Autonomous-self-healing-battery", "Advanced-Ai-Model"]
for repo in REPOS:
    repo_path = os.path.join(BASE_DIR, repo)
    if os.path.exists(repo_path) and repo_path not in sys.path:
        sys.path.insert(0, repo_path)

from golden_agent import OrganicMindOrchestrator
from access_key_token import verify_access_key_token, ACCESS_KEY_TOKEN

try:
    sys.path.insert(0, os.path.join(BASE_DIR, "Autonomous-self-healing-battery"))
    import main as battery_module
    cybernetic_subapp = getattr(battery_module, "app", None)
except Exception as e:
    print(f"[Gateway Warning] Battery sub-app mount skipped: {e}")
    cybernetic_subapp = None

app = FastAPI(
    title="Kryptic Unified Golden-Agent Ecosystem",
    description="Protected unified gateway across Golden-Agent, nkryptd, Self-Healing Battery, and Advanced-Ai-Model.",
    version="2.1.0"
)

if cybernetic_subapp:
    app.mount("/cybernetic", cybernetic_subapp)

mind = OrganicMindOrchestrator()

def send_phone_alert(title: str, content: str, alert_id: str = "kryptic_alert") -> bool:
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

THREAT_PATTERNS = re.compile(
    r"(\b(UNION\s+SELECT|DROP\s+TABLE|EXEC\(|EVAL\(|__IMPORT__|OS\.SYSTEM|SUBPROCESS|RM\s+-RF)\b|<script|\.\./)",
    re.IGNORECASE
)

def trigger_mechanical_shaker(reason: str) -> Dict[str, Any]:
    entropy_junk = bytearray(os.urandom(4096))
    for i in range(len(entropy_junk)):
        entropy_junk[i] = 0
    del entropy_junk
    gc.collect()
    send_phone_alert("nkryptd Mechanical Shaker", f"Blocked: {reason[:90]}", "nkryptd_shaker")
    return {"protocol": "MECHANICAL_SHAKER_ENGAGED", "reason": reason, "memory_scrubbed": True, "timestamp": time.time()}

def screen_payload_with_nkryptd(payload: str) -> None:
    if THREAT_PATTERNS.search(payload):
        raise HTTPException(status_code=403, detail=trigger_mechanical_shaker(f"Allergy Filter: {payload[:60]}"))
    try:
        tree = ast.parse(payload)
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom, ast.Global)):
                raise HTTPException(status_code=403, detail=trigger_mechanical_shaker("AST Moat blocked restricted primitive"))
    except SyntaxError:
        pass

def read_android_battery() -> Dict[str, Any]:
    sysfs_base = "/sys/class/power_supply/battery"
    if os.path.exists(sysfs_base):
        try:
            fields = ["capacity", "voltage_now", "current_now", "temp", "status", "health"]
            data = {f: open(os.path.join(sysfs_base, f)).read().strip() for f in fields if os.path.exists(os.path.join(sysfs_base, f))}
            if data:
                return {"source": "android_sysfs", "telemetry": data}
        except Exception:
            pass
    try:
        out = subprocess.check_output(["termux-battery-status"], timeout=2).decode("utf-8")
        return {"source": "termux_api", "telemetry": json.loads(out)}
    except Exception:
        return {"source": "simulated_fallback", "telemetry": {"status": "Unknown"}}

class EventRequest(BaseModel):
    event: str

class ModelRunRequest(BaseModel):
    script_name: str
    args: Optional[List[str]] = []

@app.get("/health")
def unified_health():
    token_configured = bool(os.getenv("ACCESS_KEY_TOKEN", ACCESS_KEY_TOKEN))
    return {
        "status": "ONLINE",
        "version": "2.1.0",
        "access_key_token_configured": token_configured,
        "hardware_battery": read_android_battery()
    }

@app.get("/files/tree", dependencies=[Depends(verify_access_key_token)])
def list_all_ecosystem_files():
    tree: Dict[str, List[str]] = {}
    for repo in REPOS:
        repo_path = os.path.join(BASE_DIR, repo)
        file_list = []
        if os.path.exists(repo_path):
            for root, _, files in os.walk(repo_path):
                if ".git" in root or "__pycache__" in root:
                    continue
                for f in files:
                    file_list.append(os.path.relpath(os.path.join(root, f), repo_path))
        tree[repo] = sorted(file_list)
    return {"ecosystem_files": tree}

@app.get("/files/read", dependencies=[Depends(verify_access_key_token)])
def read_ecosystem_file(repo: str, path: str):
    if repo not in REPOS:
        raise HTTPException(status_code=400, detail=f"Invalid repo. Choose from: {REPOS}")
    repo_root = os.path.abspath(os.path.join(BASE_DIR, repo))
    target = os.path.abspath(os.path.join(repo_root, path))
    if not target.startswith(repo_root) or not os.path.isfile(target):
        raise HTTPException(status_code=404, detail="File not found or path outside repository boundary.")
    with open(target, "r", encoding="utf-8", errors="replace") as fp:
        return {"repo": repo, "path": path, "content": fp.read()}

@app.post("/golden/reflect", dependencies=[Depends(verify_access_key_token)])
def process_golden_event(req: EventRequest):
    screen_payload_with_nkryptd(req.event)
    bat = read_android_battery()
    snapshot = mind.process_reflective_event(f"{req.event} | HW_BATTERY={json.dumps(bat)}")
    return {"security_clearance": "PASSED_NKRYPTD_MOAT", "battery_context": bat, "golden_snapshot": snapshot}

@app.get("/battery/live", dependencies=[Depends(verify_access_key_token)])
def get_live_battery():
    return read_android_battery()

@app.get("/models", dependencies=[Depends(verify_access_key_token)])
def get_models():
    adv_dir = os.path.join(BASE_DIR, "Advanced-Ai-Model")
    scripts = []
    if os.path.exists(adv_dir):
        for root, _, files in os.walk(adv_dir):
            if ".git" in root or "__pycache__" in root:
                continue
            for f in files:
                if f.endswith(".py") and not f.startswith("__"):
                    scripts.append(os.path.relpath(os.path.join(root, f), adv_dir))
    return {"repository": "Advanced-Ai-Model", "available_scripts": sorted(scripts)}

@app.post("/models/run", dependencies=[Depends(verify_access_key_token)])
def run_advanced_model(req: ModelRunRequest):
    adv_dir = os.path.abspath(os.path.join(BASE_DIR, "Advanced-Ai-Model"))
    for arg in (req.args or []):
        screen_payload_with_nkryptd(arg)
    target_path = os.path.abspath(os.path.join(adv_dir, req.script_name))
    if not target_path.startswith(adv_dir) or not os.path.exists(target_path):
        raise HTTPException(status_code=404, detail="Script not found")
    proc = subprocess.run([sys.executable, target_path, *(req.args or [])], cwd=adv_dir, capture_output=True, text=True, timeout=30)
    return {"script": req.script_name, "returncode": proc.returncode, "stdout": proc.stdout[-4000:], "stderr": proc.stderr[-2000:]}

async def background_homeostasis_loop():
    while True:
        try:
            bat = read_android_battery()
            mind.process_reflective_event(f"AUTONOMOUS_HOMEOSTASIS_TICK | {json.dumps(bat)}")
        except Exception:
            pass
        await asyncio.sleep(30)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(background_homeostasis_loop())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8888)
