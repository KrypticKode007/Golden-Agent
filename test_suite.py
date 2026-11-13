import pytest
import requests

BASE_URL = "http://localhost:8000"

def test_server_openapi_schema():
    resp = requests.get(f"{BASE_URL}/openapi.json")
    assert resp.status_code == 200
    data = resp.json()
    assert "paths" in data
    assert len(data["paths"]) > 0

def test_post_mind_reflect():
    test_message = "Pytest automated verification run"
    resp = requests.post(f"{BASE_URL}/mind/reflect", json={"action_context": test_message})
    assert resp.status_code == 200
    body = resp.json()
    assert "identity" in body
    assert "inner_monologue" in body
    assert test_message in body.get("outer_monologue", "")

def test_get_mind_journal():
    resp = requests.get(f"{BASE_URL}/mind/journal", params={"limit": 5})
    assert resp.status_code == 200
    entries = resp.json()
    assert isinstance(entries, list)
    assert len(entries) >= 1
    assert "id" in entries[0]

def test_all_discovered_get_endpoints():
    schema = requests.get(f"{BASE_URL}/openapi.json").json()
    for path, methods in schema.get("paths", {}).items():
        if "get" in methods:
            params = {"limit": 5} if "journal" in path else {}
            resp = requests.get(f"{BASE_URL}{path}", params=params)
            assert resp.status_code == 200, f"GET {path} failed with status {resp.status_code}"
