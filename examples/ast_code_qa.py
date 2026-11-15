"""Index a local Python directory into SQLite AST memory and query it."""
import asyncio
from golden_agent.core.orchestrator import MultiAgentOrchestrator
from golden_agent.core.state import AgentState


async def main() -> None:
    orch = MultiAgentOrchestrator()
    chunks = orch.rag.index_directory("src")
    print(f"Indexed {chunks} AST chunks.")
    state = await orch.run(
        AgentState(
            goal="Explain how ModelRouter resolves local vs cloud tiers in 3 bullet points.",
            profile="coder",
        )
    )
    print(state.final_output)


if __name__ == "__main__":
    asyncio.run(main())
