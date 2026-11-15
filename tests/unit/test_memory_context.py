from pathlib import Path
from golden_agent.config.settings import Settings
from golden_agent.core.context_manager import ContextManager
from golden_agent.core.state import AgentState, Message
from golden_agent.memory.episodic_store import EpisodicMemoryStore
from golden_agent.memory.hybrid_rag import HybridCodeIndex


async def test_context_compression() -> None:
    cm = ContextManager(settings=Settings(max_context_tokens=200, compression_threshold=0.5))
    state = AgentState(goal="Refactor")
    for i in range(10):
        state.messages.append(Message(role="user", content=f"Turn {i}: " + ("x" * 120)))
    assert await cm.compact_if_needed(state, keep_recent=3, use_llm=False) is True
    assert len(state.messages) == 3 and "Turn 0" in state.rolling_summary


def test_hybrid_rag_search() -> None:
    idx = HybridCodeIndex()
    idx.index_directory("src/golden_agent")
    hits = idx.search("ModelRouter resolve_model frontier local", top_k=3)
    assert any(h.chunk.symbol_name == "resolve_model" for h in hits)


def test_episodic_memory(tmp_path: Path) -> None:
    db = tmp_path / "ep.json"
    EpisodicMemoryStore(db).remember("fix", "Use importlib mode in pytest", tags=["pytest"])
    matches = EpisodicMemoryStore(db).recall("pytest importlib")
    assert len(matches) == 1 and "importlib" in matches[0].summary
