from golden_agent.core.state import RiskLevel
from golden_agent.runtime.guardrails import GuardrailEngine
from golden_agent.runtime.mcp_hub import MCPToolHub
from golden_agent.runtime.sandbox import SandboxRunner


def test_guardrails_hitl() -> None:
    g = GuardrailEngine()
    assert g.evaluate("run_sandbox_code", {"command": "rm -rf /"}).allowed is False
    hitl = g.evaluate("deploy_production", {"env": "prod"})
    assert hitl.requires_approval is True and hitl.risk_level == RiskLevel.DESTRUCTIVE and hitl.approval_request is not None
    g.approve(hitl.approval_request.id)
    assert g.evaluate("deploy_production", {"env": "prod"}, approval_id=hitl.approval_request.id).allowed is True


async def test_sandbox_runner() -> None:
    sbx = SandboxRunner(prefer_docker=False)
    ok = await sbx.run_python("print(21 * 2)")
    assert ok.exit_code == 0 and ok.stdout.strip() == "42"
    to = await sbx.run_python("import time; time.sleep(5)", timeout=1)
    assert to.timed_out is True and to.exit_code == 124


async def test_mcp_hub() -> None:
    hub = MCPToolHub()
    sbx = SandboxRunner(prefer_docker=False)
    hub.register_tool("run_sandbox_code", "Run Python", lambda a: _run(sbx, str(a["code"])))
    res = await hub.invoke("run_sandbox_code", {"code": "print('golden')"})
    assert res.success is True and res.output == "golden"


async def _run(sbx: SandboxRunner, code: str) -> str:
    return (await sbx.run_python(code)).stdout.strip()
