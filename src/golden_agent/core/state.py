from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from uuid import uuid4
from pydantic import BaseModel, Field


class TaskStatus(StrEnum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    AWAITING_APPROVAL = "awaiting_approval"
    COMPLETED = "completed"
    FAILED = "failed"


class RiskLevel(StrEnum):
    READ = "read"
    WRITE = "write"
    DESTRUCTIVE = "destructive"


class SubTask(BaseModel):
    id: str = Field(default_factory=lambda: uuid4().hex[:8])
    title: str
    description: str
    assigned_worker: str
    dependencies: list[str] = Field(default_factory=list)
    status: TaskStatus = TaskStatus.PENDING
    result: str | None = None
    retries: int = 0


class ApprovalRequest(BaseModel):
    id: str = Field(default_factory=lambda: uuid4().hex[:8])
    tool_name: str
    arguments: dict[str, Any]
    risk_level: RiskLevel
    reason: str
    approved: bool | None = None


class Message(BaseModel):
    role: str
    content: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = Field(default_factory=dict)


class AgentState(BaseModel):
    trace_id: str = Field(default_factory=lambda: uuid4().hex)
    session_id: str = Field(default_factory=lambda: uuid4().hex[:12])
    profile: str = "universal"
    goal: str
    messages: list[Message] = Field(default_factory=list)
    rolling_summary: str = ""
    plan: list[SubTask] = Field(default_factory=list)
    artifacts: dict[str, str] = Field(default_factory=dict)
    pending_approvals: list[ApprovalRequest] = Field(default_factory=list)
    total_tokens: int = 0
    total_cost_usd: float = 0.0
    status: TaskStatus = TaskStatus.PENDING
    final_output: str | None = None
    
