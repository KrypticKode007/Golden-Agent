from golden_agent.core.orchestrator import MultiAgentOrchestrator
from golden_agent.core.state import AgentState, SubTask, TaskStatus
from golden_agent.workers.ecosystem_workers import register_kryptic_ecosystem_workers


async def test_kryptic_ecosystem_workers_registered() -> None:
    orch = MultiAgentOrchestrator()
    register_kryptic_ecosystem_workers(orch)

    state = AgentState(
        goal="Run battery and security moat check",
        plan=[
            SubTask(id="w1", title="Battery Check", description="Check cells", assigned_worker="battery_cybernetic"),
            SubTask(id="w2", title="Security Moat", description="Audit repo", assigned_worker="security_moat"),
        ],
    )
    out = await orch.run(state)
    assert out.status == TaskStatus.COMPLETED
    assert "Battery Telemetry:" in (out.final_output or "")
    assert "-nkryptd Security & Repo Audit:" in (out.final_output or "")
