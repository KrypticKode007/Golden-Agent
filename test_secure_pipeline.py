#!/usr/bin/env python3
"""
Kryptic-Agent: Secure Pipeline Verification Matrix
Tests frontend delivery, auth boundary isolation, and cryptographic signature tracking.
"""

import pytest
import time
from fastapi.testclient import TestClient
from gui_dashboard import app

client = TestClient(app)

def test_frontend_dashboard_delivery():
    """Verify that the embedded frontend dashboard delivers structural layout layers securely."""
    response = client.get("/")
    assert response.status_code == 200
    assert "KRYPTIC-AGENT // EDGE MONITOR" in response.text
    assert "HMAC-SHA256" in response.text

def test_security_boundary_token_isolation():
    """Verify that access is forbidden when a request lacks valid credentials."""
    malicious_payload = {
        "node_id": "BREACH_NODE_99",
        "timestamp": time.time(),
        "system_state": "COMPROMISED",
        "matrix_compute_latency_ms": 99.9,
        "security_epoch_valid": False
    }
    # Attempt submission with an invalid token header
    response = client.post(
        "/api/v1/secure-stream", 
        json=malicious_payload, 
        headers={"X-Secure-Token": "INVALID_MALICIOUS_KEY"}
    )
    assert response.status_code == 403
    assert "Access Denied" in response.json()["detail"]

def test_secure_pipeline_log_consolidation():
    """Verify that validated edge data frames generate compliant HMAC logging signatures."""
    valid_payload = {
        "node_id": "KRYPTIC_EDGE_NODE_01",
        "timestamp": time.time(),
        "system_state": "HOMEOSTATIC_HEALTHY",
        "matrix_compute_latency_ms": 0.412,
        "security_epoch_valid": True
    }
    # Submit payload using the authorized orchestration boundary keys
    response = client.post(
        "/api/v1/secure-stream", 
        json=valid_payload, 
        headers={"X-Secure-Token": "kryptic_token_session_prod_alpha_007"}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "SUCCESS"
    assert "packet_signature" in response.json()
    assert len(response.json()["packet_signature"]) == 64  # Confirms valid SHA256 string allocation
  
