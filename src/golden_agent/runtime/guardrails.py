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
    BLOCKED_PATTERNS: tuple[str, ...] = (
        r"rm\s+-rf\s+/", r"mkfs\.", r"dd\s+if=.*of=/dev/",
        r":\(\)\s*\{\s*:\|\:&\s*\};:", r"curl\s+.*\|\s*(bash|sh)", r"wget\s+.*\|\s*(bash|sh)",
    )
    DESTRUCTIVE_TOOLS: set[str] = {
        "delete_file", "drop_table", "git_push_force",
        "deploy_production", "send_email", "execute_shell_unrestricted",
    }
    WRITE_TOOLS: set[str] = {
        "write_file", "edit_file", "git_commit", "git_push",
        "create_issue", "post_slack_message", "run_sandbox_code",
    }

    def __init__(self, require_approval_for_writes: bool = False) -> None:
        self.require_approval_for_writes = require_approval_for_writes
        self._approved_ids: set[str] = set()

    def approve(self, approval_id: str) -> None:
        self._approved_ids.add(approval_id)

    def classify_risk(self, tool_name: str, arguments: dict[str, Any]) -> RiskLevel:
        s = f"{tool_name} {arguments}".lower()
        if tool_name in self.DESTRUCTIVE_TOOLS or any(k in s for k in ("drop ", "delete ", "rm -rf", "force", "production")):
            return RiskLevel.DESTRUCTIVE
        if tool_name in self.WRITE_TOOLS or any(k in tool_name.lower() for k in ("write", "update", "create", "insert", "run", "exec")):
            return RiskLevel.WRITE
        return RiskLevel.READ

    def evaluate(self, tool_name: str, arguments: dict[str, Any], approval_id: str | None = None) -> PolicyDecision:
        raw_cmd = f"{arguments.get('command', '')} {arguments.get('code', '')}"
        for pat in self.BLOCKED_PATTERNS:
            if re.search(pat, raw_cmd):
                return PolicyDecision(allowed=False, requires_approval=False, risk_level=RiskLevel.DESTRUCTIVE, reason=f"Blocked pattern: {pat}")
        risk = self.classify_risk(tool_name, arguments)
        if approval_id and approval_id in self._approved_ids:
            return PolicyDecision(allowed=True, requires_approval=False, risk_level=risk, reason="Approved by human operator.")
        if risk == RiskLevel.DESTRUCTIVE or (risk == RiskLevel.WRITE and self.require_approval_for_writes):
            reason = f"Tool '{tool_name}' ({risk.value.upper()}) requires human approval."
            req = ApprovalRequest(tool_name=tool_name, arguments=arguments, risk_level=risk, reason=reason)
            return PolicyDecision(allowed=False, requires_approval=True, risk_level=risk, reason=reason, approval_request=req)
        return PolicyDecision(allowed=True, requires_approval=False, risk_level=risk, reason=f"Permitted ({risk.value.upper()}).")
