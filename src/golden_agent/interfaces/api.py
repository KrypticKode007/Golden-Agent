import asyncio, json
from fastapi import APIRouter, FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from golden_agent.core.orchestrator import MultiAgentOrchestrator
from golden_agent.core.state import AgentState, TaskStatus
from golden_agent.runtime.sandbox import SandboxRunner

router = APIRouter(prefix="/agent", tags=["golden-agent"])
_orch = MultiAgentOrchestrator()
_orch.rag.index_directory(".")


async def _builtin_sandbox(args: dict[str, object]) -> str:
    res = await SandboxRunner(prefer_docker=False).run_python(str(args.get("code", "")))
    return res.stdout.strip() or res.stderr.strip()


_orch.tools.register_tool("run_sandbox_code", "Execute Python code in isolated sandbox", _builtin_sandbox)


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


def create_app() -> FastAPI:
    app = FastAPI(title="Golden-Agent Autonomous Platform", version="0.1.0")
    app.include_router(router)
    return app


def mount_onto(existing_app: FastAPI, dependencies: list[object] | None = None) -> FastAPI:
    """Mount Golden-Agent autonomous endpoints onto unified_golden_gateway.py."""
    existing_app.include_router(router, dependencies=dependencies or [])
    return existing_app
