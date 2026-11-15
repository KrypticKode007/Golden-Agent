from golden_agent.interfaces.api import approve_action, create_app, list_tools


async def test_api_tools_and_approval_endpoints() -> None:
    app = create_app()
    routes = {getattr(r, "path", "") for r in app.routes}
    assert "/agent/run" in routes and "/agent/stream" in routes

    tools = await list_tools()
    assert any(t["name"] == "run_sandbox_code" for t in tools)

    res = await approve_action("abc12345")
    assert res == {"status": "approved", "approval_id": "abc12345"}
