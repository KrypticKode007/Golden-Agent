import re
from typing import Any
from pydantic import BaseModel
from golden_agent.core.state import ApprovalRequest, RiskLevel


class PolicyDecision(BaseModel):
    allowed: bool
    requires_approval: bool
    risk_level: RiskLevel
    reason: str
    approval_request: ApprovalRequest | None = None


class GuardrailEngine:
    """Classifies tool calls by risk level and enforces Human-in-the-Loop (HITL) gates."""

    BLOCKED_PATTERNS: tuple[str, ...] = (
        r"rm\s+-rf\s+/",
        r"mkfs\.",
        r"dd\s+if=.*of=/dev/",
        r":\(\)\s*\{\s*:\|\:&\s*\};:",
        r"curl\s+.*\|\s*(bash|sh)",
        r"wget\s+.*\|\s*(bash|sh)",
    )

    DESTRUCTIVE_TOOLS: set[str] = {
        "delete_file",
        "drop_table",
        "git_push_force",
        "deploy_production",
        "send_email",
        "execute_shell_unrestricted",
    }

    WRITE_TOOLS: set[str] = {
        "write_file",
        "edit_file",
        "git_commit",
        "git_push",
        "create_issue",
        "post_slack_message",
        "run_sandbox_code",
    }

    def __init__(self, require_approval_for_writes: bool = False) -> None:
        self.require_approval_for_writes = require_approval_for_writes
        self._approved_ids: set[str] = set()

    def approve(self, approval_id: str) -> None:
        self._approved_ids.add(approval_id)

    def classify_risk(self, tool_name: str, arguments: dict[str, Any]) -> RiskLevel:
        serialized = f"{tool_name} {arguments}".lower()

        if tool_name in self.DESTRUCTIVE_TOOLS or any(
            kw in serialized for kw in ("drop ", "delete ", "rm -rf", "force", "production")
        ):
            return RiskLevel.DESTRUCTIVE

        if tool_name in self.WRITE_TOOLS or any(
            kw in tool_name.lower() for kw in ("write", "update", "create", "insert", "run", "exec")
        ):
            return RiskLevel.WRITE

        return RiskLevel.READ

    def evaluate(
        self,
        tool_name: str,
        arguments: dict[str, Any],
        approval_id: str | None = None,
    ) -> PolicyDecision:
        raw_cmd = str(arguments.get("command", "")) + " " + str(arguments.get("code", ""))
        for pattern in self.BLOCKED_PATTERNS:
            if re.search(pattern, raw_cmd):
                return PolicyDecision(
                    allowed=False,
                    requires_approval=False,
                    risk_level=RiskLevel.DESTRUCTIVE,
                    reason=f"Blocked by hard security rule matching pattern: {pattern}",
                )

        risk = self.classify_risk(tool_name, arguments)

        if approval_id and approval_id in self._approved_ids:
            return PolicyDecision(
                allowed=True,
                requires_approval=False,
                risk_level=risk,
                reason="Explicitly approved by human operator.",
            )

        needs_hitl = risk == RiskLevel.DESTRUCTIVE or (
            risk == RiskLevel.WRITE and self.require_approval_for_writes
        )

        if needs_hitl:
            reason = f"Tool '{tool_name}' classified as {risk.value.upper()} and requires human approval."
            req = ApprovalRequest(
                tool_name=tool_name,
                arguments=arguments,
                risk_level=risk,
                reason=reason,
            )
            return PolicyDecision(
                allowed=False,
                requires_approval=True,
                risk_level=risk,
                reason=reason,
                approval_request=req,
            )

        return PolicyDecision(
            allowed=True,
            requires_approval=False,
            risk_level=risk,
            reason=f"Permitted under {risk.value.upper()} policy.",
  )
      
