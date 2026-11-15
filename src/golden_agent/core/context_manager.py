from golden_agent.config.model_router import ModelRouter, ModelTier
from golden_agent.config.settings import Settings, get_settings
from golden_agent.core.state import AgentState, Message


class ContextManager:
    def __init__(self, router: ModelRouter | None = None, settings: Settings | None = None) -> None:
        self.router = router or ModelRouter()
        self.settings = settings or get_settings()

    def current_usage_ratio(self, state: AgentState) -> float:
        chars = len(state.goal) + len(state.rolling_summary) + sum(len(m.content) for m in state.messages)
        return (chars // 4) / max(1, self.settings.max_context_tokens)

    def prune_tool_output(self, output: str, max_chars: int = 4000) -> str:
        if len(output) <= max_chars:
            return output
        half = max_chars // 2
        return f"{output[:half]}\n... [{len(output) - max_chars} chars omitted] ...\n{output[-half:]}"

    async def compact_if_needed(self, state: AgentState, keep_recent: int = 6, use_llm: bool = True) -> bool:
        if self.current_usage_ratio(state) < self.settings.compression_threshold or len(state.messages) <= keep_recent:
            return False
        older, state.messages = state.messages[:-keep_recent], state.messages[-keep_recent:]
        transcript = "\n".join(f"{m.role.upper()}: {m.content}" for m in older)
        if use_llm:
            resp = await self.router.complete(
                [{"role": "system", "content": "Summarize key facts, file paths, and decisions concisely."},
                 {"role": "user", "content": f"{state.rolling_summary}\n\n{transcript}"}],
                tier=ModelTier.FAST, temperature=0.1,
            )
            state.rolling_summary = resp.content.strip()
            state.total_tokens += resp.prompt_tokens + resp.completion_tokens
            state.total_cost_usd += resp.cost_usd
        else:
            condensed = " | ".join(f"{m.role}: {m.content[:120]}" for m in older)
            state.rolling_summary = f"{state.rolling_summary}\n{condensed}".strip()
        return True

    def build_prompt_messages(self, state: AgentState, system_prompt: str) -> list[dict[str, str]]:
        msgs = [{"role": "system", "content": system_prompt}]
        if state.rolling_summary:
            msgs.append({"role": "system", "content": f"Summary:\n{state.rolling_summary}"})
        msgs.extend({"role": m.role, "content": m.content} for m in state.messages)
        if not state.messages or state.messages[-1].content != state.goal:
            msgs.append({"role": "user", "content": state.goal})
        return msgs

    def append_message(self, state: AgentState, role: str, content: str) -> None:
        state.messages.append(Message(role=role, content=self.prune_tool_output(content)))
