import os
import time
import pytest
import concurrent.futures
from robotic_database_core import UnifiedTelemetryDatabase
from kryptic_edge_launch import HardwareAccelerationBridge

DB_FILE = "test_agency_sentience.db"

@pytest.fixture(autouse=True)
def cleanup_test_db():
    """Ensures a clean database environment before and after every validation pass."""
    if os.path.exists(DB_FILE):
        try:
            os.remove(DB_FILE)
        except OSError:
            pass
    yield
    if os.path.exists(DB_FILE):
        try:
            os.remove(DB_FILE)
        except OSError:
            pass

def test_database_initialization():
    """Asserts that the schema initializes correctly and tables are ready."""
    db = UnifiedTelemetryDatabase(db_path=DB_FILE)
    assert os.path.exists(DB_FILE), "Database file was not created."
    logs = db.get_latest_logs(limit=1)
    assert isinstance(logs, list), "Log retrieval failed to return a valid list structure."

def test_high_concurrency_stress_ingestion():
    """Simulates high-speed telemetry streams from simultaneous multi-threaded sensor matrices."""
    db = UnifiedTelemetryDatabase(db_path=DB_FILE)
    thread_count = 10
    logs_per_thread = 20

    def worker_stream(worker_id: int):
        for i in range(logs_per_thread):
            success = db.log_metric(
                module=f"SENSOR_MATRIX_{worker_id}",
                latency=14.2 + (worker_id * 0.5),
                message=f"Telemetry check-in packet index #{i} verified stable."
            )
            assert success is True, "Database write failure under concurrent operational load."

    with concurrent.futures.ThreadPoolExecutor(max_workers=thread_count) as executor:
        futures = [executor.submit(worker_stream, t) for t in range(thread_count)]
        concurrent.futures.wait(futures)

    latest_logs = db.get_latest_logs(limit=300)
    assert len(latest_logs) == (thread_count * logs_per_thread), "Telemetry packet loss detected in persistence layer."

def test_hardware_bridge_fallback_mechanisms():
    """Validates that the execution controller drops safely back to mock-simulation defaults if binaries are uncompiled."""
    bridge = HardwareAccelerationBridge(library_path="./non_existent_mock_library.so")
    assert bridge.compiled_library is None, "Bridge failed to register a missing shared object file cleanly."
    
    latency = bridge.trigger_cycle(operational_mode=1)
    assert latency == 14.2, "Hardware acceleration engine failed to deliver standard baseline fallback metrics."
                
