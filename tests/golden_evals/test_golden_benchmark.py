from pathlib import Path
from golden_agent.core.orchestrator import MultiAgentOrchestrator
from golden_agent.core.state import AgentState, SubTask, TaskStatus
from golden_agent.telemetry.tracer import AgentTracer


async def test_golden_end_to_end_benchmark(tmp_path: Path) -> None:
    tracer = AgentTracer(log_path=tmp_path / "traces.jsonl")
    orch = MultiAgentOrchestrator()

    async def coder_sim(task: SubTask, state: AgentState, ctx: str) -> str:
        with tracer.span(state.trace_id, "coder_step", worker="coder", task=task.id):
            return "```python\ndef add(a: int, b: int) -> int:\n    return a + b\nassert add(3, 4) == 7\nprint('PASS')\n```"

    async def researcher_sim(task: SubTask, state: AgentState, ctx: str) -> str:
        with tracer.span(state.trace_id, "research_step", worker="researcher", task=task.id):
            return "Synthesized 3 architectural findings with verified citations."

    orch.register_worker("coder", coder_sim)
    orch.register_worker("researcher", researcher_sim)

    state = AgentState(
        goal="Research best pattern and implement verified add() helper",
        profile="universal",
        plan=[
            SubTask(id="r1", title="Research pattern", description="Analyze options", assigned_worker="researcher"),
            SubTask(id="c1", title="Implement helper", description="Write tested code", assigned_worker="coder", dependencies=["r1"]),
        ],
    )

    result = await orch.run(state)
    assert result.status == TaskStatus.COMPLETED
    assert "PASS" in (result.final_output or "")
    assert len(tracer.spans) == 2
    assert (tmp_path / "traces.jsonl").is_file()
