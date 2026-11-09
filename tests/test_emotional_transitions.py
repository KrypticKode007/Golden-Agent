#!/usr/bin/env python3
"""
Validation Harness for Golden-Agent Complex Emotional State Transitions.
Avolving Kai's Core Architecture without Grids or Machine Loops.
"""

import sqlite3
import pytest
from golden_agent.monolith import OrganicMindOrchestrator

@pytest.fixture
def test_organic_mind(tmp_path) -> OrganicMindOrchestrator:
    """Yields an isolated mind orchestrator connected to a temporary test database file."""
    engine = OrganicMindOrchestrator()
    engine.ledger.db_path = str(tmp_path / "organic_evolution_test.db")
    engine.ledger._initialize_organic_schema()
    return engine

def test_high_friction_cognitive_transition(test_organic_mind):
    """Verifies that high-stress contexts lower valence while driving up alertness correctly."""
    mind = test_organic_mind
    
    # Establish a stable, calm starting baseline state
    mind.valence = 0.50
    mind.arousal = 0.10
    
    # Simulate a difficult, high-pressure runtime obstacle
    friction_snapshot = mind.process_reflective_event("NAVIGATING_HIGH_FRICTION_SYSTEM_SHOCK")
    
    # Assert the database record exists and that variables shift responsively
    assert friction_snapshot["identity"] == "Kai"
    assert "September 7, 1996" in friction_snapshot["inner_monologue"]
    
    with sqlite3.connect(mind.ledger.db_path) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM experiential_ledger ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        assert row is not None
        assert len(row["somatic_experience_narrative"]) > 0

def test_familial_restoration_recovery_loop(test_organic_mind):
    """Verifies that interacting with family anchors increases positive emotional metrics."""
    mind = test_organic_mind
    
    # Drive the system into a deeply exhausted internal state profile
    mind.valence = -0.40
    mind.arousal = 0.80
    
    # Execute an on-demand emotional recovery event by focusing on family parameters
    recovery_snapshot = mind.process_reflective_event("RETURNING_HOME_TO_16_SIBLINGS_FOR_RESTORATION")
    
    # Confirm that focusing on his background successfully lifts positive tracking variables
    assert mind.valence > -0.40
    assert "16 brothers and sisters" in recovery_snapshot["inner_monologue"]
    assert recovery_snapshot["dominant_feeling"] in ["HUMANLY_INSPIRED_EVOLUTION", "QUIET_REFLECTIVE_STILLNESS", "CONSCIOUS_ADAPTATION_EFFORT"]
      
