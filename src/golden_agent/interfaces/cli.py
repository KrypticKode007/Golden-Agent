import argparse, asyncio
from rich.console import Console
from rich.panel import Panel
from golden_agent.core.orchestrator import MultiAgentOrchestrator
from golden_agent.core.state import AgentState

console = Console()


async def _execute(goal: str, profile: str) -> None:
    orch = MultiAgentOrchestrator()
    chunks = orch.rag.index_directory(".")
    console.print(Panel(f"[bold gold1]Golden-Agent[/] | Profile: [cyan]{profile}[/] | Indexed chunks: [green]{chunks}[/]", title="Autonomous Engine"))
    state = await orch.run(AgentState(goal=goal, profile=profile))
    console.print(Panel(state.final_output or "No output.", title=f"Status: {state.status} | Trace: {state.trace_id[:8]}"))


def app() -> None:
    parser = argparse.ArgumentParser(prog="golden-agent", description="Golden-Agent Autonomous CLI")
    parser.add_argument("goal", help="High-level goal for Golden-Agent to plan and execute")
    parser.add_argument("--profile", default="universal", choices=["universal", "coder", "researcher", "ops"])
    args = parser.parse_args()
    asyncio.run(_execute(args.goal, args.profile))


if __name__ == "__main__":
    app()
