from collections.abc import Awaitable, Callable
from typing import Any
from pydantic import BaseModel, Field
from golden_agent.core.state import ApprovalRequest
from golden_agent.runtime.guardrails import GuardrailEngine


ToolHandler = Callable[[dict[str, Any]], Awaitable[str]]


class ToolSpec(BaseModel):
    name: str
    description: str
    input_schema: dict[str, Any] = Field(default_factory=dict)
    server: str = "builtin"


class ToolCallResult(BaseModel):
    tool_name: str
    success: bool
    output: str
    blocked: bool = False
    approval_request: ApprovalRequest | None = None


class MCPToolHub:
    """Unified registry for local built-in tools and external Model Context Protocol (MCP) servers."""

    def __init__(self, guardrails: GuardrailEngine | None = None) -> None:
        self.guardrails = guardrails or GuardrailEngine()
        self._specs: dict[str, ToolSpec] = {}
        self._handlers: dict[str, ToolHandler] = {}

    def register_tool(
        self,
        name: str,
        description: str,
        handler: ToolHandler,
        input_schema: dict[str, Any] | None = None,
        server: str = "builtin",
    ) -> None:
        self._specs[name] = ToolSpec(
            name=name,
            description=description,
            input_schema=input_schema or {"type": "object", "properties": {}},
            server=server,
        )
        self._handlers[name] = handler

    def list_tools(self) -> list[ToolSpec]:
        return list(self._specs.values())

    def to_openai_schemas(self) -> list[dict[str, Any]]:
        return [
            {
                "type": "function",
                "function": {
                    "name": spec.name,
                    "description": spec.description,
                    "parameters": spec.input_schema,
                },
            }
            for spec in self._specs.values()
        ]

    async def invoke(
        self,
        tool_name: str,
        arguments: dict[str, Any],
        approval_id: str | None = None,
    ) -> ToolCallResult:
        if tool_name not in self._handlers:
            return ToolCallResult(
                tool_name=tool_name,
                success=False,
                output=f"Unknown tool: '{tool_name}'. Available: {sorted(self._specs.keys())}",
            )

        decision = self.guardrails.evaluate(tool_name, arguments, approval_id=approval_id)
        if not decision.allowed:
            return ToolCallResult(
                tool_name=tool_name,
                success=False,
                output=decision.reason,
                blocked=True,
                approval_request=decision.approval_request,
            )

        try:
            output = await self._handlers[tool_name](arguments)
            return ToolCallResult(tool_name=tool_name, success=True, output=output)
        except Exception as exc:
            return ToolCallResult(
                tool_name=tool_name,
                success=False,
                output=f"Tool '{tool_name}' raised error: {exc}",
            )
          
