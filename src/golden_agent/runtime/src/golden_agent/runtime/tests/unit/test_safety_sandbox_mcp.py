from golden_agent.core.state import RiskLevel
from golden_agent.runtime.guardrails import GuardrailEngine
from golden_agent.runtime.mcp_hub import MCPToolHub
from golden_agent.runtime.sandbox import SandboxRunner


def test_guardrails_block_and_hitl() -> None:
    engine = GuardrailEngine()

    # 1. Hard block on catastrophic shell pattern
    blocked = engine.evaluate("run_sandbox_code", {"command": "rm -rf /"})
    assert blocked.allowed is False
    assert blocked.requires_approval is False

    # 2. Destructive action triggers HITL approval pause
    hitl = engine.evaluate("deploy_production", {"env": "prod"})
    assert hitl.allowed is False
    assert hitl.requires_approval is True
    assert hitl.risk_level == RiskLevel.DESTRUCTIVE
    assert hitl.approval_request is not None

    # 3. Once approved by ID, execution is permitted
    engine.approve(hitl.approval_request.id)
    resumed = engine.evaluate(
        "deploy_production",
        {"env": "prod"},
        approval_id=hitl.approval_request.id,
    )
    assert resumed.allowed is True


async def test_sandbox_execution_and_timeout() -> None:
    runner = SandboxRunner(prefer_docker=False)

    ok = await runner.run_python("print(21 * 2)")
    assert ok.exit_code == 0
    assert ok.stdout.strip() == "42"

    timed_out = await runner.run_python("import time; time.sleep(5)", timeout=1)
    assert timed_out.timed_out is True
    assert timed_out.exit_code == 124


async def test_mcp_hub_tool_invocation() -> None:
    hub = MCPToolHub()
    runner = SandboxRunner(prefer_docker=False)

    async def exec_code(args: dict[str, object]) -> str:
        res = await runner.run_python(str(args.get("code", "")))
        return res.stdout.strip() or res.stderr.strip()

    hub.register_tool(
        name="run_sandbox_code",
        description="Execute Python code safely",
        handler=exec_code,
    )

    result = await hub.invoke("run_sandbox_code", {"code": "print('golden')"})
    assert result.success is True
    assert result.output == "golden"
  
