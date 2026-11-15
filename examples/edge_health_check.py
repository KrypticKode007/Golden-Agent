"""Run an autonomic SQLite integrity check and edge runtime diagnostic."""
import asyncio
from golden_agent.core.orchestrator import MultiAgentOrchestrator
from golden_agent.core.state import AgentState


async def main() -> None:
    orch = MultiAgentOrchestrator()
    state = await orch.run(
        AgentState(
            goal="Verify local memory vault health and summarize system readiness.",
            profile="ops",
        )
    )
    print(f"Status: {state.status} | Output: {state.final_output}")


if __name__ == "__main__":
    asyncio.run(main())
