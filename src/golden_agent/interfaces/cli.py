import argparse
import asyncio
import os
from pathlib import Path
import urllib.error
from rich.console import Console
from rich.panel import Panel
from golden_agent.core.orchestrator import MultiAgentOrchestrator
from golden_agent.core.state import AgentState

console = Console()


def _load_dotenv(path: str = ".env") -> None:
    env_file = Path(path)
    if not env_file.is_file():
        return
    for raw_line in env_file.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        os.environ.setdefault(key.strip(), val.strip().strip('"').strip("'"))


def _init_wizard() -> None:
    is_termux = "com.termux" in os.environ.get("PREFIX", "") or Path("/data/data/com.termux").exists()
    console.print(Panel("[bold gold1]Golden-Agent Setup Wizard[/]", title="Init"))
    mode = "local" if is_termux else input("Execution mode [local/hybrid/cloud] (default: local): ").strip() or "local"
    if mode == "local":
        default_model = "ollama/qwen2.5:0.5b" if is_termux else "ollama/qwen2.5:7b"
        model = input(f"Local Ollama model (default: {default_model}): ").strip() or default_model
        workers = "1" if is_termux else "3"
        env_text = (
            f"GOLDEN_EXECUTION_MODE=local\n"
            f"GOLDEN_OLLAMA_BASE_URL=http://127.0.0.1:11434\n"
            f"GOLDEN_TIER1_LOCAL_MODEL={model}\n"
            f"GOLDEN_TIER2_LOCAL_MODEL={model}\n"
            f"GOLDEN_TIER3_LOCAL_MODEL={model}\n"
            f"GOLDEN_MAX_PARALLEL_WORKERS={workers}\n"
        )
    else:
        api_key = input("Enter OPENAI_API_KEY (leave blank to set later): ").strip()
        env_text = (
            f"GOLDEN_EXECUTION_MODE={mode}\n"
            f"OPENAI_BASE_URL=https://openai.com\n"
            f"OPENAI_API_KEY={api_key}\n"
        )
    Path(".env").write_text(env_text, encoding="utf-8")
    console.print(f"[green]✓ Saved .env[/] ({'Termux low-RAM profile' if is_termux else mode + ' profile'})")


async def _execute(goal: str, profile: str) -> None:
    orch = MultiAgentOrchestrator()
    chunks = orch.rag.index_directory(".")
    console.print(
        Panel(
            f"[bold gold1]Golden-Agent[/] | Profile: [cyan]{profile}[/] | Indexed chunks: [green]{chunks}[/]",
            title="Autonomous Engine",
        )
    )
    try:
        state = await orch.run(AgentState(goal=goal, profile=profile))
        console.print(
            Panel(
                state.final_output or "No output.",
                title=f"Status: {state.status} | Trace: {state.trace_id[:8]}",
            )
        )
    except (RuntimeError, urllib.error.URLError, ConnectionError) as exc:
        console.print(
            Panel(
                f"[bold red]Provider Error:[/] {exc}\n\n"
                "[dim]Tip: Run 'golden-agent init' to configure .env or start Ollama locally (ollama serve).[/]",
                title="Execution Halted",
                border_style="red",
            )
        )


def app() -> None:
    _load_dotenv()
    parser = argparse.ArgumentParser(prog="golden-agent", description="Golden-Agent Autonomous CLI")
    parser.add_argument("goal", help="Goal to execute, or 'init' to run the setup wizard")
    parser.add_argument("--profile", default="universal", choices=["universal", "coder", "researcher", "ops"])
    args = parser.parse_args()
    if args.goal.strip().lower() == "init":
        _init_wizard()
        return
    asyncio.run(_execute(args.goal, args.profile))


if __name__ == "__main__":
    app()
