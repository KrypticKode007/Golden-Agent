import httpx
from golden_agent.interfaces.api import create_app

app = create_app()

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

async def test_get_agent_schedules():
    async with _client() as client:
        resp = await client.get("/agent/schedules")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

async def test_all_discovered_get_endpoints():
    async with _client() as client:
        schema = (await client.get("/openapi.json")).json()
        for path, methods in schema.get("paths", {}).items():
            if "get" in methods:
                resp = await client.get(path)
                assert resp.status_code == 200, f"GET {path} failed with status {resp.status_code}"
