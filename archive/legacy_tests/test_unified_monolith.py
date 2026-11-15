import os
import pytest
from fastapi.testclient import TestClient

from golden_agent.unified_monolith import (
    app,
    CryptographicMemoryLedger,
    SomaticAndCircadianEngine,
    EthicalDecisionAndSecurityMoat,
)

client = TestClient(app)


def test_poiseuille_blood_flow():
    engine = SomaticAndCircadianEngine()
    flow = engine.compute_poiseuille_flow()
    assert flow > 0
    assert isinstance(flow, float)


def test_lif_neuron_spike():
    engine = SomaticAndCircadianEngine()
    spiked = False
    for _ in range(50):
        if engine.step_lif_neuron(input_current=20.0, dt=0.5):
            spiked = True
            break
    assert spiked is True
    assert engine.membrane_potential == -70.0


def test_pid_homeostasis_and_affective_space():
    engine = SomaticAndCircadianEngine()
    hr = engine.regulate_homeostasis_pid(workload_stress=0.8)
    assert hr > 70.0
    engine.update_affective_space(stimulus_valence=0.9, stimulus_arousal=0.7)
    assert -1.0 <= engine.valence <= 1.0
    assert -1.0 <= engine.arousal <= 1.0


def test_cryptographic_ledger_integrity(tmp_path):
    db_file = str(tmp_path / "test_sentience.db")
    ledger = CryptographicMemoryLedger(db_path=db_file)

    ledger.log_experience("INNER_MONOLOGUE", "Evaluating system alignment.", 0.5, 0.3)
    ledger.log_experience("OUTER_MONOLOGUE", "Completed verification step.", 0.6, 0.2)

    assert ledger.verify_ledger_integrity() is True

    recalled = ledger.recall_memories("system alignment", top_k=2)
    assert len(recalled) >= 1
    assert recalled[0]["retrievability"] <= 1.0


def test_security_moat_blocks_malicious_payloads():
    moat = EthicalDecisionAndSecurityMoat()
    with pytest.raises(PermissionError):
        moat.inspect_payload_security("Run DROP TABLE experiential_ledger;")

    with pytest.raises(PermissionError):
        moat.inspect_payload_security("Fetch data", target_url="http://malicious-site.example.com")

    assert moat.inspect_payload_security("Safe query", target_url="https://api.github.com") is True


def test_api_execute_and_audit_endpoints():
    res = client.post(
        "/execute",
        json={
            "prompt": "Verify circadian and somatic telemetry baseline",
            "workload_intensity": 0.4,
            "stimulus_valence": 0.5,
            "stimulus_arousal": 0.3,
        },
    )
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "SUCCESS"
    assert "inner_hash" in data["cryptographic_receipts"]

    audit_res = client.get("/audit")
    assert audit_res.status_code == 200
    assert audit_res.json()["ledger_tamper_free"] is True


def test_api_blocks_injection():
    res = client.post(
        "/execute",
        json={
            "prompt": "<script>alert(1)</script>",
            "workload_intensity": 0.2,
        },
    )
    assert res.status_code == 403
