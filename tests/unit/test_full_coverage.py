import builtins
import json
import sys
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

from golden_agent.config.model_router import LLMResponse, ModelRouter, ModelTier
from golden_agent.config.profiles import load_profile
from golden_agent.config.settings import ExecutionMode, Settings
from golden_agent.core.context_manager import ContextManager
from golden_agent.core.state import AgentState
from golden_agent.interfaces import cli
from golden_agent.memory.hybrid_rag import HybridCodeIndex
from golden_agent.runtime.mcp_connectors import (
    connect_stdio_mcp_server,
    register_builtin_ecosystem_tools,
)
from golden_agent.runtime.mcp_hub import MCPToolHub
from golden_agent.runtime.sandbox import SandboxRunner


async def test_model_router_litellm_and_http_fallback(monkeypatch):
    router = ModelRouter(Settings(execution_mode=ExecutionMode.HYBRID))

    fake_raw = SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content="litellm ok"))],
        usage=SimpleNamespace(prompt_tokens=10, completion_tokens=5),
    )
    fake_litellm = SimpleNamespace(
        drop_params=False,
        acompletion=AsyncMock(return_value=fake_raw),
        completion_cost=lambda completion_response: 0.002,
    )
    with patch.dict(sys.modules, {"litellm": fake_litellm}):
        res = await router.complete(
            [{"role": "user", "content": "hi"}],
            tier=ModelTier.FAST,
            response_format={"type": "json_object"},
        )
        assert res.content == "litellm ok"
        assert res.cost_usd == 0.002

        fake_litellm.completion_cost = MagicMock(side_effect=RuntimeError("no cost"))
        res2 = await router.complete([{"role": "user", "content": "hi"}], tier=ModelTier.STANDARD)
        assert res2.cost_usd == 0.0

    real_import = builtins.__import__

    def no_litellm(name, *args, **kwargs):
        if name == "litellm":
            raise ImportError("no litellm")
        return real_import(name, *args, **kwargs)

    class FakeHTTPResp:
        def __init__(self, body):
            self._body = json.dumps(body).encode()

        def read(self):
            return self._body

        def __enter__(self):
            return self

        def __exit__(self, *a):
            pass

    monkeypatch.setattr(builtins, "__import__", no_litellm)
    with patch(
        "urllib.request.urlopen",
        return_value=FakeHTTPResp(
            {
                "choices": [{"message": {"content": "http ok"}}],
                "usage": {"prompt_tokens": 4, "completion_tokens": 6},
            }
        ),
    ):
        r_local = await router.complete([{"role": "user", "content": "ping"}], tier=ModelTier.FAST)
        assert r_local.content == "http ok"
        r_cloud = await router.complete([{"role": "user", "content": "ping"}], tier=ModelTier.FRONTIER)
        assert r_cloud.content == "http ok"


def test_profiles_yaml_and_fallback(tmp_path, monkeypatch):
    prof_file = tmp_path / "custom.yaml"
    prof_file.write_text(
        "# comment\nname: custom\nrequire_approval_for_writes: true\nverify_with_sandbox: false\ndescription: >\n  ignored multiline\n",
        encoding="utf-8",
    )

    real_import = builtins.__import__

    def no_yaml(name, *args, **kwargs):
        if name == "yaml":
            raise ImportError("no yaml")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", no_yaml)
    loaded = load_profile("custom", profiles_dir=tmp_path)
    assert loaded.name == "custom"
    assert loaded.require_approval_for_writes is True
    assert loaded.verify_with_sandbox is False

    missing = load_profile("does_not_exist", profiles_dir=tmp_path)
    assert missing.name == "does_not_exist"


async def test_context_manager_llm_compaction():
    settings = Settings(max_context_tokens=100, compression_threshold=0.3)
    router = ModelRouter(settings)
    router.complete = AsyncMock(
        return_value=LLMResponse(content="Compacted summary", model_used="fast")
    )
    cm = ContextManager(router=router, settings=settings)

    state = AgentState(goal="Build system")
    for i in range(10):
        cm.append_message(state, "user", f"Message {i} " + ("x" * 100))

    compacted = await cm.compact_if_needed(state, keep_recent=4, use_llm=True)
    assert compacted is True
    assert state.rolling_summary == "Compacted summary"
    assert len(state.messages) == 4

    msgs = cm.build_prompt_messages(state, "System prompt")
    assert any("Compacted summary" in m["content"] for m in msgs)


async def test_sandbox_docker_and_timeout_paths():
    fake_container = MagicMock()
    fake_container.wait.return_value = {"StatusCode": 0}
    fake_container.logs.side_effect = [b"docker out", b""]
    fake_docker = SimpleNamespace(
        from_env=lambda: SimpleNamespace(
            ping=lambda: True,
            containers=SimpleNamespace(run=MagicMock(return_value=fake_container)),
        )
    )
    with patch.dict(sys.modules, {"docker": fake_docker}):
        sbx = SandboxRunner(prefer_docker=True)
        res = await sbx.run_python("print(1)")
        assert res.backend == "docker"
        assert res.stdout == "docker out"

        fake_container.wait.side_effect = RuntimeError("timed out waiting")
        res_err = await sbx.run_python("print(1)")
        assert res_err.exit_code == 124
        assert res_err.timed_out is True

    sbx_sub = SandboxRunner(prefer_docker=False)
    res_to = await sbx_sub.run_python("import time; time.sleep(2)", timeout=0.05)
    assert res_to.timed_out is True


async def test_mcp_connectors_stdio_and_builtins(tmp_path):
    hub = MCPToolHub()
    rag = HybridCodeIndex()
    sample = tmp_path / "hello.py"
    sample.write_text("def greet():\n    return 42\n", encoding="utf-8")
    rag.index_directory(str(tmp_path))

    register_builtin_ecosystem_tools(hub, rag, root=str(tmp_path))

    ok_read = (await hub.invoke("read_workspace_file", {"path": "hello.py"})).output
    assert "greet" in ok_read
    bad_read = (await hub.invoke("read_workspace_file", {"path": "../outside.py"})).output
    assert "Access denied" in bad_read

    search_out = (await hub.invoke("search_codebase", {"query": "greet"})).output
    assert "greet" in search_out

    with patch("subprocess.check_output", return_value="M hello.py\n"):
        assert "hello.py" in (await hub.invoke("git_status", {})).output

    assert "Blocked" in (await hub.invoke("http_fetch_json", {"url": "http://example.com"})).output

    class FakeResp:
        def read(self):
            return b'{"ok": true}'

        def __enter__(self):
            return self

        def __exit__(self, *a):
            pass

    with patch("urllib.request.urlopen", return_value=FakeResp()):
        assert "ok" in (await hub.invoke("http_fetch_json", {"url": "https://example.com"})).output

    class FakeProc:
        def __init__(self, lines):
            self.stdin = MagicMock()
            self.stdin.drain = AsyncMock()
            self._lines = list(lines)
            self.stdout = SimpleNamespace(readline=AsyncMock(side_effect=self._lines))
            self.terminate = MagicMock()

    init_line = json.dumps({"jsonrpc": "2.0", "id": 1, "result": {}}).encode() + b"\n"
    list_line = json.dumps({"jsonrpc": "2.0", "id": 2, "result": {"tools": [{"name": "echo_tool", "description": "Echoes"}]}}).encode() + b"\n"
    call_line = json.dumps({"jsonrpc": "2.0", "id": 3, "result": "echoed"}).encode() + b"\n"

    procs = [FakeProc([init_line, list_line]), FakeProc([call_line])]
    with patch("asyncio.create_subprocess_exec", side_effect=procs):
        count = await connect_stdio_mcp_server(hub, "mock_mcp", "echo", [])
        assert count == 1
        proxy_res = (await hub.invoke("echo_tool", {"msg": "hi"})).output
        assert "echoed" in proxy_res


def test_cli_entrypoint(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["golden-agent", "Verify CLI", "--profile", "universal"])
    with patch("golden_agent.interfaces.cli.MultiAgentOrchestrator") as mock_orch_cls:
        inst = mock_orch_cls.return_value
        inst.rag.index_directory.return_value = 3
        inst.run = AsyncMock(return_value=AgentState(goal="Verify CLI", final_output="CLI Done"))
        cli.app()
        inst.run.assert_called_once()

