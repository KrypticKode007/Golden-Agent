import asyncio
from datetime import datetime, timezone
from uuid import uuid4
from pydantic import BaseModel, Field
from golden_agent.core.orchestrator import MultiAgentOrchestrator
from golden_agent.core.state import AgentState


class ScheduledJob(BaseModel):
    job_id: str = Field(default_factory=lambda: uuid4().hex[:8])
    goal: str
    profile: str = "universal"
    interval_seconds: int = Field(default=3600, ge=10)
    runs_completed: int = 0
    last_run_at: datetime | None = None
    last_status: str = "scheduled"


class AutonomousScheduler:
    """Runs recurring autonomous agent goals on background asyncio intervals."""

    def __init__(self, orchestrator: MultiAgentOrchestrator) -> None:
        self.orchestrator = orchestrator
        self.jobs: dict[str, ScheduledJob] = {}
        self._tasks: dict[str, asyncio.Task[None]] = {}

    def add_job(self, goal: str, profile: str = "universal", interval_seconds: int = 3600) -> ScheduledJob:
        job = ScheduledJob(goal=goal, profile=profile, interval_seconds=interval_seconds)
        self.jobs[job.job_id] = job
        self._tasks[job.job_id] = asyncio.create_task(self._loop(job))
        return job

    def remove_job(self, job_id: str) -> bool:
        task = self._tasks.pop(job_id, None)
        if task:
            task.cancel()
        return self.jobs.pop(job_id, None) is not None

    async def _loop(self, job: ScheduledJob) -> None:
        while job.job_id in self.jobs:
            await asyncio.sleep(job.interval_seconds)
            if job.job_id not in self.jobs:
                break
            state = await self.orchestrator.run(AgentState(goal=job.goal, profile=job.profile))
            job.runs_completed += 1
            job.last_run_at = datetime.now(timezone.utc)
            job.last_status = str(state.status)
