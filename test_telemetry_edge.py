#!/usr/bin/env python3
"""
Kryptic-Agent: Telemetry Validation Test Suite
Uses FastAPI TestClient to programmatically assert API safety and layer validation.
"""

import pytest
from fastapi.testclient import TestClient

# Import the ASGI application context directly from your framework repository workspace
from gui_dashboard import app

client = TestClient(app)

def test_gateway_root_connection():
    """Verify that the base API engine route responds with correct operational signatures."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ONLINE"
    assert "Kryptic" in response.json()["engine"]

def test_telemetry_frame_schema_validation():
    """Verify that the telemetry framework accurately maps metrics output values."""
    response = client.get("/api/v1/telemetry")
    assert response.status_code == 200
    
    data = response.json()
    # Structural type checks to guarantee clean automation interfaces
    assert data["node_id"] == "KRYPTIC_EDGE_NODE_01"
    assert isinstance(data["matrix_compute_latency_ms"], float)
    assert data["matrix_compute_latency_ms"] < 1.0  # Must reflect sub-millisecond C++ engine thresholds
    assert data["security_epoch_valid"] is True
    assert data["system_state"] == "HOMEOSTATIC_HEALTHY"

def test_subsystem_diagnostic_readouts():
    """Verify that internal boundary micro-checks report optimal stability states."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    
    subsystems = response.json()["subsystems"]
    assert subsystems["cpp_acceleration_bindings"] == "CONNECTED"
    assert subsystems["cryptographic_key_rotation"] == "STABLE"
    assert subsystems["robotic_database_ledger"] == "SYNCHRONIZED"
