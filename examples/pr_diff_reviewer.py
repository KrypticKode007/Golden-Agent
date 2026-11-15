"""Review staged git changes for bugs, security issues, and edge cases."""
import asyncio
import subprocess
from golden_agent.core.orchestrator import MultiAgentOrchestrator
from golden_agent.core.state import AgentState


async def main() -> None:
    diff = subprocess.check_output(["git", "diff", "HEAD~1"], text=True)[:6000]
    orch = MultiAgentOrchestrator()
    state = await orch.run(
        AgentState(
            goal=f"Review this git diff for regressions or security risks:\n\n{diff}",
            profile="coder",
        )
    )
    print(state.final_output)


if __name__ == "__main__":
    asyncio.run(main())
