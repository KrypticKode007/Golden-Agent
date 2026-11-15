import asyncio, json
from fastapi import APIRouter, FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from golden_agent.core.orchestrator import MultiAgentOrchestrator
from golden_agent.core.state import AgentState, TaskStatus
from golden_agent.runtime.mcp_connectors import register_builtin_ecosystem_tools
from golden_agent.workers.ecosystem_workers import register_kryptic_ecosystem_workers
from golden_agent.runtime.sandbox import SandboxRunner
from golden_agent.runtime.scheduler import AutonomousScheduler

router = APIRouter(prefix="/agent", tags=["golden-agent"])
_orch = MultiAgentOrchestrator()
_orch.rag.index_directory(".")


async def _builtin_sandbox(args: dict[str, object]) -> str:
    res = await SandboxRunner(prefer_docker=False).run_python(str(args.get("code", "")))
    return res.stdout.strip() or res.stderr.strip()


_orch.tools.register_tool("run_sandbox_code", "Execute Python code in isolated sandbox", _builtin_sandbox)
register_builtin_ecosystem_tools(_orch.tools, _orch.rag)
register_kryptic_ecosystem_workers(_orch)
_scheduler = AutonomousScheduler(_orch)


class RunRequest(BaseModel):
    goal: str
    profile: str = "universal"


@router.get("/tools")
async def list_tools() -> list[dict[str, str]]:
    return [{"name": t.name, "description": t.description, "server": t.server} for t in _orch.tools.list_tools()]


@router.post("/index")
async def reindex_workspace(path: str = ".") -> dict[str, int]:
    return {"indexed_chunks": _orch.rag.index_directory(path)}


@router.post("/approve/{approval_id}")
async def approve_action(approval_id: str) -> dict[str, str]:
    _orch.tools.guardrails.approve(approval_id)
    return {"status": "approved", "approval_id": approval_id}


@router.post("/run")
async def run_agent(req: RunRequest) -> dict[str, object]:
    state = await _orch.run(AgentState(goal=req.goal, profile=req.profile))
    dump = state.model_dump(mode="json") if hasattr(state, "model_dump") else json.loads(state.json())
    return dump


@router.post("/stream")
async def stream_agent(req: RunRequest) -> StreamingResponse:
    async def _events():
        state = AgentState(goal=req.goal, profile=req.profile)
        yield f"data: {json.dumps({'event': 'started', 'trace_id': state.trace_id, 'profile': req.profile})}\n\n"
        await asyncio.sleep(0)
        final = await _orch.run(state)
        yield f"data: {json.dumps({'event': 'completed', 'status': final.status, 'output': final.final_output})}\n\n"

    return StreamingResponse(_events(), media_type="text/event-stream")




class ScheduleRequest(BaseModel):
    goal: str
    profile: str = "universal"
    interval_seconds: int = 3600


@router.get("/schedules")
async def list_schedules() -> list[dict[str, object]]:
    return [
        j.model_dump(mode="json") if hasattr(j, "model_dump") else {"job_id": j.job_id, "goal": j.goal, "profile": j.profile, "interval_seconds": j.interval_seconds, "runs_completed": j.runs_completed, "last_status": j.last_status}
        for j in _scheduler.jobs.values()
    ]


@router.post("/schedule")
async def create_schedule(req: ScheduleRequest) -> dict[str, object]:
    job = _scheduler.add_job(goal=req.goal, profile=req.profile, interval_seconds=req.interval_seconds)
    return {"job_id": job.job_id, "goal": job.goal, "profile": job.profile, "interval_seconds": job.interval_seconds}


@router.delete("/schedule/{job_id}")
async def delete_schedule(job_id: str) -> dict[str, object]:
    removed = _scheduler.remove_job(job_id)
    if not removed:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return {"deleted": True, "job_id": job_id}


def create_app() -> FastAPI:
    app = FastAPI(title="Golden-Agent Autonomous Platform", version="0.1.0")
    app.include_router(router)
    existing = {getattr(r, "path", "") for r in app.routes}
    if "/agent/run" not in existing:
        app.add_api_route("/agent/tools", list_tools, methods=["GET"])
        app.add_api_route("/agent/index", reindex_workspace, methods=["POST"])
        app.add_api_route("/agent/approve/{approval_id}", approve_action, methods=["POST"])
        app.add_api_route("/agent/run", run_agent, methods=["POST"])
        app.add_api_route("/agent/stream", stream_agent, methods=["POST"])
        app.add_api_route("/agent/schedules", list_schedules, methods=["GET"])
        app.add_api_route("/agent/schedule", create_schedule, methods=["POST"])
        app.add_api_route("/agent/schedule/{job_id}", delete_schedule, methods=["DELETE"])
    return app


def mount_onto(existing_app: FastAPI, dependencies: list[object] | None = None) -> FastAPI:
    """Mount Golden-Agent autonomous endpoints onto unified_golden_gateway.py."""
    existing_app.include_router(router, dependencies=dependencies or [])
    return existing_app
