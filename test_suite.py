from unittest.mock import AsyncMock, patch
import httpx
import golden_agent.interfaces.api as api_mod
from golden_agent.config.model_router import LLMResponse

app = api_mod.create_app()

def _client():
    return httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test")

async def test_server_openapi_schema():
    async with _client() as client:
        resp = await client.get("/openapi.json")
        assert resp.status_code == 200
        data = resp.json()
        assert "paths" in data
        assert len(data["paths"]) > 0

async def test_get_agent_tools():
    async with _client() as client:
        resp = await client.get("/agent/tools")
        assert resp.status_code == 200
        tools = resp.json()
        assert isinstance(tools, list)
        assert len(tools) >= 1

async def test_agent_schedule_lifecycle():
    async with _client() as client:
        create_resp = await client.post("/agent/schedule", json={"goal": "CI health check", "profile": "universal", "interval_seconds": 3600})
        assert create_resp.status_code == 200
        job_id = create_resp.json()["job_id"]

        list_resp = await client.get("/agent/schedules")
        assert list_resp.status_code == 200
        assert any(j["job_id"] == job_id for j in list_resp.json())

        del_resp = await client.delete(f"/agent/schedule/{job_id}")
        assert del_resp.status_code == 200
        assert del_resp.json()["deleted"] is True

async def test_post_agent_run():
    mock_reply = LLMResponse(content="status ok", model_used="mock-model", provider="test", latency_ms=1.0)
    with patch.object(api_mod._orch.router, "complete", new=AsyncMock(return_value=mock_reply)):
        async with _client() as client:
            resp = await client.post("/agent/run", json={"goal": "Return status ok", "profile": "universal"})
            assert resp.status_code == 200
            body = resp.json()
            assert "status" in body

async def test_all_discovered_get_endpoints():
    async with _client() as client:
        schema = (await client.get("/openapi.json")).json()
        for path, methods in schema.get("paths", {}).items():
            if "get" in methods:
                resp = await client.get(path)
                assert resp.status_code == 200, f"GET {path} failed with status {resp.status_code}"
