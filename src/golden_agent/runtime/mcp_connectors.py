import asyncio, json, os, subprocess, urllib.request
from pathlib import Path
from typing import Any
from golden_agent.memory.hybrid_rag import HybridCodeIndex
from golden_agent.runtime.mcp_hub import MCPToolHub


async def connect_stdio_mcp_server(hub: MCPToolHub, name: str, command: str, args: list[str]) -> int:
    """Discovers tools from an external MCP stdio server via JSON-RPC 2.0 and registers them on MCPToolHub."""
    proc = await asyncio.create_subprocess_exec(
        command, *args, stdin=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    assert proc.stdin and proc.stdout
    init_req = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "golden-agent", "version": "0.1.0"}}}) + "\n"
    proc.stdin.write(init_req.encode())
    await proc.stdin.drain()
    await asyncio.wait_for(proc.stdout.readline(), timeout=10)

    list_req = json.dumps({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}) + "\n"
    proc.stdin.write(list_req.encode())
    await proc.stdin.drain()
    raw = await asyncio.wait_for(proc.stdout.readline(), timeout=10)
    proc.terminate()

    tools = json.loads(raw.decode()).get("result", {}).get("tools", [])
    for t in tools:
        t_name = t["name"]

        async def _proxy(tool_args: dict[str, Any], _tn: str = t_name) -> str:
            p = await asyncio.create_subprocess_exec(
                command, *args, stdin=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE
            )
            assert p.stdin and p.stdout
            call_msg = json.dumps({"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": _tn, "arguments": tool_args}}) + "\n"
            p.stdin.write(call_msg.encode())
            await p.stdin.drain()
            res_line = await asyncio.wait_for(p.stdout.readline(), timeout=30)
            p.terminate()
            return res_line.decode("utf-8", errors="replace").strip()

        hub.register_tool(t_name, t.get("description", ""), _proxy, input_schema=t.get("inputSchema"), server=name)
    return len(tools)


def register_builtin_ecosystem_tools(hub: MCPToolHub, rag: HybridCodeIndex, root: str = ".") -> None:
    """Registers native workspace, AST search, Git, and HTTP tools onto MCPToolHub."""
    base = Path(root).resolve()

    async def read_workspace_file(args: dict[str, Any]) -> str:
        target = (base / str(args.get("path", ""))).resolve()
        if not str(target).startswith(str(base)) or not target.is_file():
            return "Access denied or file not found."
        return target.read_text(encoding="utf-8", errors="replace")[:8000]

    async def search_codebase(args: dict[str, Any]) -> str:
        hits = rag.search(str(args.get("query", "")), top_k=int(args.get("top_k", 5)))
        return "\n".join(f"{h.chunk.file_path}:{h.chunk.symbol_name} (score={h.score})" for h in hits) or "No matches."

    async def git_status(_: dict[str, Any]) -> str:
        out = subprocess.check_output(["git", "status", "-s"], cwd=str(base), text=True)
        return out.strip() or "Clean working tree."

    async def http_fetch_json(args: dict[str, Any]) -> str:
        url = str(args.get("url", ""))
        if not url.startswith(("https://", "http://localhost", "http://127.0.0.1")):
            return "Blocked non-HTTPS external URL."
        req = urllib.request.Request(url, headers={"User-Agent": "Golden-Agent/0.1"})
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.read().decode("utf-8", errors="replace")[:6000]

    hub.register_tool("read_workspace_file", "Read a file inside the workspace safely", read_workspace_file, {"type": "object", "properties": {"path": {"type": "string"}}})
    hub.register_tool("search_codebase", "Search indexed Python AST & docs via hybrid RAG", search_codebase, {"type": "object", "properties": {"query": {"type": "string"}}})
    hub.register_tool("git_status", "Inspect current Git working tree status", git_status)
    hub.register_tool("http_fetch_json", "Fetch JSON/text from an HTTPS or local endpoint", http_fetch_json, {"type": "object", "properties": {"url": {"type": "string"}}})
