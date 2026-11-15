import json, os, subprocess, urllib.request
from typing import Any
from golden_agent.core.orchestrator import MultiAgentOrchestrator
from golden_agent.core.state import AgentState, SubTask


def _call_local_gateway(path: str, method: str = "GET", body: dict[str, Any] | None = None) -> str:
    base = os.environ.get("GOLDEN_GATEWAY_URL", "http://127.0.0.1:8888").rstrip("/")
    token = os.environ.get("ACCESS_KEY_TOKEN", "")
    headers = {"Content-Type": "application/json"}
    if token:
        headers["X-Access-Key-Token"] = token
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(f"{base}{path}", data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.read().decode("utf-8", errors="replace")[:4000]
    except Exception as exc:
        return json.dumps({"gateway_fallback": True, "path": path, "note": str(exc)})


def register_kryptic_ecosystem_workers(orch: MultiAgentOrchestrator) -> None:
    """Binds specialized workers for Battery Cybernetics, -nkryptd Moat, Model Hub, and Reflection Core."""

    async def battery_worker(task: SubTask, state: AgentState, ctx: str) -> str:
        try:
            termux_bat = subprocess.check_output(["termux-battery-status"], timeout=3, text=True).strip()
        except Exception:
            termux_bat = _call_local_gateway("/battery/live")
        sim = _call_local_gateway("/cybernetic/battery/autonomous", method="POST", body={"goal": task.description})
        return f"Battery Telemetry:\n{termux_bat}\n\nSelf-Healing 4-Cell Simulation:\n{sim}"

    async def security_moat_worker(task: SubTask, state: AgentState, ctx: str) -> str:
        git_state = await orch.tools.invoke("git_status", {})
        rag_hits = await orch.tools.invoke("search_codebase", {"query": task.description, "top_k": 3})
        return f"-nkryptd Security & Repo Audit:\nGit Status: {git_state.output}\nRelevant Code:\n{rag_hits.output}"

    async def model_hub_worker(task: SubTask, state: AgentState, ctx: str) -> str:
        models = _call_local_gateway("/models")
        return f"Advanced-Ai-Model Registry:\n{models}\n\nTask Context:\n{ctx[:600]}"

    async def reflection_worker(task: SubTask, state: AgentState, ctx: str) -> str:
        res = _call_local_gateway("/golden/reflect", method="POST", body={"event": task.description, "trace_id": state.trace_id})
        return f"OrganicMindOrchestrator Reflection:\n{res}"

    orch.register_worker("battery_cybernetic", battery_worker)
    orch.register_worker("security_moat", security_moat_worker)
    orch.register_worker("model_hub", model_hub_worker)
    orch.register_worker("reflection_core", reflection_worker)
