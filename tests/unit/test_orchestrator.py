import asyncio
from golden_agent.core.orchestrator import MultiAgentOrchestrator
from golden_agent.core.state import AgentState, SubTask, TaskStatus
from golden_agent.workers.verifier import VerifierWorker


async def test_parallel_dag_execution() -> None:
    orch = MultiAgentOrchestrator()
    executed_order: list[str] = []

    async def fast_worker(task: SubTask, state: AgentState, ctx: str) -> str:
        await asyncio.sleep(0.02)
        executed_order.append(task.id)
        return f"done:{task.id}"

    for w in ("coder", "researcher", "ops"):
        orch.register_worker(w, fast_worker)

    state = AgentState(
        goal="Parallel DAG test",
        profile="universal",
        plan=[
            SubTask(id="a", title="Branch A", description="Independent 1", assigned_worker="researcher"),
            SubTask(id="b", title="Branch B", description="Independent 2", assigned_worker="coder"),
            SubTask(id="c", title="Merge C", description="Depends on A & B", assigned_worker="ops", dependencies=["a", "b"]),
        ],
    )
    out = await orch.run(state)
    assert out.status == TaskStatus.COMPLETED
    assert executed_order[-1] == "c"
    assert set(executed_order[:2]) == {"a", "b"}


async def test_verifier_catches_syntax_and_runtime_errors() -> None:
    v = VerifierWorker()
    bad = await v.verify_python_snippet("def broken(:\n  pass")
    assert bad.passed is False and "SyntaxError" in bad.feedback

    good = await v.verify_python_snippet("assert 2 + 2 == 4\nprint('ok')")
    assert good.passed is True and good.feedback == "ok"
