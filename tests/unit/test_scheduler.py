import asyncio
from golden_agent.core.orchestrator import MultiAgentOrchestrator
from golden_agent.core.state import AgentState, SubTask
from golden_agent.runtime.scheduler import AutonomousScheduler


async def test_autonomous_scheduler_lifecycle() -> None:
    orch = MultiAgentOrchestrator()

    async def noop(task: SubTask, state: AgentState, ctx: str) -> str:
        return "ok"

    for w in ("coder", "researcher", "ops"):
        orch.register_worker(w, noop)

    sched = AutonomousScheduler(orch)
    job = sched.add_job("Periodic health audit", profile="ops", interval_seconds=10)
    assert job.job_id in sched.jobs
    assert sched.remove_job(job.job_id) is True
    assert job.job_id not in sched.jobs
