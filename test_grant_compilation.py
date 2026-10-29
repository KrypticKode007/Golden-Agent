#!/usr/bin/env python3
"""
Kryptic-Agent: Grant Compilation Integrity Tests
Validates threshold boundaries, structure compilation rules, and environmental criteria.
"""

import pytest
import os
from generate_grant_proposal import GrantProposalCompiler

@pytest.fixture
def compiler_instance():
    test_output = "TEST_GRANT_PROPOSAL.md"
    yield GrantProposalCompiler(output_path=test_output)
    # Clean up test artifact outputs following assertion completion
    if os.path.exists(test_output):
        os.remove(test_output)

def test_telemetry_extraction_compliance(compiler_instance):
    """Verify that extracted operational values fall inside expected grant baseline bounds."""
    metrics = compiler_instance.fetch_live_telemetry_metrics()
    assert metrics["node_id"] == "KRYPTIC_EDGE_NODE_01"
    assert metrics["verified_latency_ms"] < compiler_instance.performance_targets["max_allowable_latency_ms"]
    assert metrics["security_epoch_valid"] is True

def test_proposal_structural_generation(compiler_instance):
    """Verify that compiled document content contains critical verification text blocks."""
    proposal_text = compiler_instance.compile_technical_proposal()
    assert "Live Phase I Feasibility Proof" in proposal_text
    assert "KrypticKode007/Golden-Agent" in proposal_text
    assert "HMAC-SHA256" in proposal_text
    assert "0.412 ms" in proposal_text

def test_compilation_failure_on_latency_breach(compiler_instance):
    """Assert that the compilation pipeline aborts safely if latency parameters exceed targets."""
    # Force a breach simulation into the runtime metrics method
    compiler_instance.fetch_live_telemetry_metrics = lambda: {
        "node_id": "BREACHED_TEST_NODE",
        "verified_latency_ms": 2.45,  # Exceeds the 1.0ms performance boundary
        "security_epoch_valid": True,
        "current_state": "LATENCY_OVERLOAD"
    }
    with pytest.raises(ValueError, match="Staging latency limits breach technical grant thresholds"):
        compiler_instance.compile_technical_proposal()
  
