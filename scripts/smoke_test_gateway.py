import asyncio, os, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from golden_agent.core.state import AgentState, SubTask, TaskStatus
from golden_agent.interfaces.api import RunRequest, _orch, list_tools, run_agent


async def main() -> None:
    tools = await list_tools()
    print(f"[1/3] Registered MCP/Sandbox tools ({len(tools)}):", [t["name"] for t in tools])

    # Verify codebase search tool live
    search_res = await _orch.tools.invoke("search_codebase", {"query": "GuardrailEngine classify_risk"})
    assert search_res.success, search_res.output
    print(f"[2/3] Live AST Hybrid RAG hit -> {search_res.output.splitlines()}")

    # Verify full end-to-end orchestrator execution via /agent/run handler
    async def mock_worker(task: SubTask, state: AgentState, ctx: str) -> str:
        return f"Verified execution for '{task.title}' (context chars={len(ctx)})"

    for w in ("coder", "researcher", "ops"):
        _orch.register_worker(w, mock_worker)

    _orch.plan = lambda state, profile: asyncio.sleep(0, result=setattr(state, "plan", [
        SubTask(id="s1", title="Audit workspace", description="Check files", assigned_worker="researcher"),
        SubTask(id="s2", title="Verify sandbox", description="Run check", assigned_worker="coder", dependencies=["s1"]),
    ]) or state.plan)  # type: ignore[method-assign]

    res = await run_agent(RunRequest(goal="Smoke test unified gateway", profile="universal"))
    assert res["status"] == TaskStatus.COMPLETED, res
    print(f"[3/3] End-to-end /agent/run status={res['status']} | trace_id={res['trace_id'][:8]}")
    print("ALL GATEWAY SMOKE CHECKS PASSED!")


if __name__ == "__main__":
    asyncio.run(main())
