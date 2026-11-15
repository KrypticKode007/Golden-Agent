import asyncio, json, re
from collections.abc import Awaitable, Callable
from golden_agent.config.model_router import ModelRouter, ModelTier
from golden_agent.config.profiles import DomainProfile, load_profile
from golden_agent.config.settings import Settings, get_settings
from golden_agent.core.context_manager import ContextManager
from golden_agent.core.state import AgentState, SubTask, TaskStatus
from golden_agent.memory.episodic_store import EpisodicMemoryStore
from golden_agent.memory.hybrid_rag import HybridCodeIndex
from golden_agent.runtime.guardrails import GuardrailEngine
from golden_agent.runtime.mcp_hub import MCPToolHub
from golden_agent.workers.verifier import VerifierWorker

WorkerFn = Callable[[SubTask, AgentState, str], Awaitable[str]]


class MultiAgentOrchestrator:
    """Supervisor DAG planner + parallel map-reduce executor + self-correcting verifier."""

    def __init__(
        self,
        router: ModelRouter | None = None,
        settings: Settings | None = None,
        tool_hub: MCPToolHub | None = None,
        rag: HybridCodeIndex | None = None,
        memory: EpisodicMemoryStore | None = None,
        verifier: VerifierWorker | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.router = router or ModelRouter(self.settings)
        self.context = ContextManager(self.router, self.settings)
        self.tools = tool_hub or MCPToolHub(GuardrailEngine())
        self.rag = rag or HybridCodeIndex()
        self.memory = memory or EpisodicMemoryStore()
        self.verifier = verifier or VerifierWorker()
        self._workers: dict[str, WorkerFn] = {
            "coder": self._default_worker,
            "researcher": self._default_worker,
            "ops": self._default_worker,
        }

    def register_worker(self, name: str, fn: WorkerFn) -> None:
        self._workers[name] = fn

    async def _default_worker(self, task: SubTask, state: AgentState, context_block: str) -> str:
        tier = ModelTier.FRONTIER if task.assigned_worker == "coder" else ModelTier.STANDARD
        msgs = [
            {"role": "system", "content": f"You are the {task.assigned_worker} specialist. Execute the subtask concisely."},
            {"role": "user", "content": f"Goal: {state.goal}\nSubtask: {task.title} - {task.description}\nContext:\n{context_block}"},
        ]
        resp = await self.router.complete_with_retry(msgs, tier=tier)
        state.total_tokens += resp.prompt_tokens + resp.completion_tokens
        state.total_cost_usd += resp.cost_usd
        return resp.content

    async def plan(self, state: AgentState, profile: DomainProfile) -> list[SubTask]:
        if state.plan:
            return state.plan
        msgs = [
            {"role": "system", "content": 'Break the goal into 1-4 JSON subtasks: [{"id":"t1","title":"...","description":"...","assigned_worker":"coder|researcher|ops","dependencies":[]}]'},
            {"role": "user", "content": state.goal},
        ]
        try:
            resp = await self.router.complete_with_retry(msgs, tier=ModelTier.FRONTIER, temperature=0.1)
            state.total_tokens += resp.prompt_tokens + resp.completion_tokens
            state.total_cost_usd += resp.cost_usd
            raw_json = re.search(r"\[.*\]", resp.content, re.DOTALL)
            items = json.loads(raw_json.group(0)) if raw_json else []
            loader = getattr(SubTask, "model_validate", None) or SubTask.parse_obj
            state.plan = [loader(i) for i in items]
        except Exception:
            state.plan = []
        if not state.plan:
            state.plan = [SubTask(id="t1", title="Execute Goal", description=state.goal, assigned_worker=profile.default_worker)]
        return state.plan

    async def run(self, state: AgentState) -> AgentState:
        profile = load_profile(state.profile)
        self.tools.guardrails.require_approval_for_writes = profile.require_approval_for_writes
        state.status = TaskStatus.IN_PROGRESS

        rag_hits = "\n".join(f"[{h.chunk.file_path}:{h.chunk.symbol_name}] {h.chunk.content[:300]}" for h in self.rag.search(state.goal, top_k=3))
        episodes = "\n".join(f"- ({e.category}) {e.summary}" for e in self.memory.recall(state.goal, limit=3))
        shared_ctx = f"Code/Doc Context:\n{rag_hits}\n\nPrior Memory:\n{episodes}".strip()

        await self.plan(state, profile)
        completed_ids: set[str] = {t.id for t in state.plan if t.status == TaskStatus.COMPLETED}

        while len(completed_ids) < len(state.plan):
            ready = [t for t in state.plan if t.status == TaskStatus.PENDING and all(d in completed_ids for d in t.dependencies)]
            if not ready:
                state.status = TaskStatus.FAILED
                return state

            async def _exec(task: SubTask) -> None:
                task.status = TaskStatus.IN_PROGRESS
                worker = self._workers.get(task.assigned_worker, self._default_worker)
                dep_notes = "\n".join(f"{t.title}: {t.result}" for t in state.plan if t.id in task.dependencies)
                output = await worker(task, state, f"{shared_ctx}\n{dep_notes}".strip())

                code_match = re.search(r"```python\n(.*?)```", output, re.DOTALL)
                if profile.verify_with_sandbox and code_match:
                    report = await self.verifier.verify_python_snippet(code_match.group(1))
                    if not report.passed and task.retries < self.settings.max_verifier_retries:
                        task.retries += 1
                        output = await worker(task, state, f"{shared_ctx}\nFix this verification error:\n{report.feedback}")

                task.result = output
                task.status = TaskStatus.COMPLETED
                state.artifacts[task.id] = output

            await asyncio.gather(*(_exec(t) for t in ready[: self.settings.max_parallel_workers]))
            completed_ids.update(t.id for t in ready[: self.settings.max_parallel_workers])
            await self.context.compact_if_needed(state, use_llm=False)

        state.final_output = "\n\n".join(f"### {t.title}\n{t.result}" for t in state.plan)
        state.status = TaskStatus.COMPLETED
        return state
