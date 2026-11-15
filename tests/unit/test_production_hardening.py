import pytest
from golden_agent.config.model_router import ModelRouter
from golden_agent.memory.hybrid_rag import HybridCodeIndex


def test_polyglot_symbol_extraction() -> None:
    idx = HybridCodeIndex()
    ts_code = """
    export interface AgentConfig {
        maxRetries: number;
    }
    export async function runPipeline(input: string): Promise<void> {
        console.log(input);
    }
    """
    go_code = """
    package main
    type Orchestrator struct { Workers int }
    func (o *Orchestrator) ExecuteTask(id string) error {
        return nil
    }
    """
    rust_code = """
    pub struct MemoryVault { pub path: String }
    pub fn verify_integrity(vault: &MemoryVault) -> bool {
        true
    }
    """
    ts_chunks = idx.chunk_polyglot_source("app.ts", ts_code)
    go_chunks = idx.chunk_polyglot_source("main.go", go_code)
    rs_chunks = idx.chunk_polyglot_source("lib.rs", rust_code)

    assert [c.symbol_name for c in ts_chunks] == ["AgentConfig", "runPipeline"]
    assert [c.symbol_name for c in go_chunks] == ["Orchestrator", "ExecuteTask"]
    assert [c.symbol_name for c in rs_chunks] == ["MemoryVault", "verify_integrity"]


def test_model_router_json_repair() -> None:
    noisy = 'Sure! Here is your DAG plan:\n```json\n{"steps": ["analyze", "patch"], "confidence": 0.95}\n```\nHope that helps!'
    parsed = ModelRouter.extract_json(noisy)
    assert parsed["steps"] == ["analyze", "patch"]
    assert parsed["confidence"] == 0.95

    with pytest.raises(ValueError):
        ModelRouter.extract_json("No structured data at all")


@pytest.mark.asyncio
async def test_model_router_exponential_retry(monkeypatch: pytest.MonkeyPatch) -> None:
    import urllib.error
    from golden_agent.config.model_router import LLMResponse

    router = ModelRouter()
    attempts = {"count": 0}

    async def flaky_complete(*args, **kwargs) -> LLMResponse:
        attempts["count"] += 1
        if attempts["count"] < 3:
            raise urllib.error.URLError("Temporary socket reset")
        return LLMResponse(content="Recovered cleanly", model_used="ollama/qwen2.5:0.5b")

    monkeypatch.setattr(router, "complete", flaky_complete)
    res = await router.complete_with_retry([{"role": "user", "content": "ping"}], max_retries=3, base_delay=0.01)
    assert res.content == "Recovered cleanly"
    assert attempts["count"] == 3


@pytest.mark.asyncio
async def test_concurrent_rag_and_memory_stress(tmp_path) -> None:
    import asyncio
    from golden_agent.memory.episodic_store import EpisodicMemoryStore

    store = EpisodicMemoryStore(tmp_path / "episodes.json")
    idx = HybridCodeIndex()
    idx.index_directory("src/golden_agent")

    async def worker(i: int) -> int:
        store.remember("stress", f"Completed edge node diagnostic #{i}", tags=["arm64", f"worker-{i}"])
        hits = idx.search("ModelRouter resolve_model", top_k=3)
        return len(hits)

    results = await asyncio.gather(*(worker(i) for i in range(15)))
    assert all(r > 0 for r in results)
    assert len(store.recall("diagnostic", limit=20)) == 15
