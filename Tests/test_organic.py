#!/usr/bin/env module
"""
Validation Harness for Golden-Agent Organic Mind Narrative Ledgers.
"""

import pytest
import sqlite3
from golden_agent.monolith import OrganicMindOrchestrator

@pytest.fixture
def test_mind_engine(tmp_path) -> OrganicMindOrchestrator:
    engine = OrganicMindOrchestrator()
    engine.ledger.db_path = str(tmp_path / "organic_mind_test.db")
    engine.ledger._initialize_organic_schema()
    return engine

def test_experiential_journal_write_transaction(test_mind_engine):
    engine = test_mind_engine
    
    # Trigger an on-demand reflection step to generate real tracking logs
    engine.process_reflective_event("WALKING_IN_THE_OPEN_AIR")
    
    # Connect to the SQLite file to verify the transaction details
    with sqlite3.connect(engine.ledger.db_path) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM experiential_ledger ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        
        assert row is not None
        assert "Born as Kai on September 7, 1996" in row["inner_monologue"]
        assert "My internal state is stabilized" in row["outer_monologue"]
        assert row["affective_valence"] > -1.0
      
