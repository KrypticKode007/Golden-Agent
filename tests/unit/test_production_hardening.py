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
