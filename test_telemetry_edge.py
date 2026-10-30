import time
import os
import sys
import psutil
import pytest
from robotic_database_core import UnifiedTelemetryDatabase
from kryptic_edge_launch import HardwareAccelerationBridge

@pytest.mark.performance
def test_prolonged_leak_isolation():
    """Executes a high-density 10,000 cycle telemetry run to track memory profiles."""
    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss
    
    db = UnifiedTelemetryDatabase(db_path="perf_stress_matrix.db")
    bridge = HardwareAccelerationBridge()
    
    print(f"\n[START] Starting loop stress execution. Initial RSS footprint: {initial_memory / 1024 / 1024:.2f} MB")
    
    # Fire a continuous 10k stream cycle ring
    for cycle in range(10000):
        latency = bridge.trigger_cycle(operational_mode=2)
        if cycle % 2500 == 0:
            db.log_metric("STRESS_TEST", latency, f"Checkpoint vector block index #{cycle} written.")
            
    final_memory = process.memory_info().rss
    memory_delta = final_memory - initial_memory
    
    print(f"[END] Stress execution completed. Memory variance delta: {memory_delta / 1024 / 1024:.2f} MB")
    
    # Assert structural stability: variance over 10k loops must remain below 15MB ceiling
    assert memory_delta < (15 * 1024 * 1024), "Potential memory leak detected within core cross-language bindings."
    
    if os.path.exists("perf_stress_matrix.db"):
        os.remove("perf_stress_matrix.db")
    
