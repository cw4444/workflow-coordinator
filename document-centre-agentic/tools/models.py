from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


class JobStatus(str, Enum):
    NEW = "new"
    TRIAGED = "triaged"
    IN_PROGRESS = "in_progress"
    WAITING_CLIENT = "waiting_client"
    WAITING_HUMAN = "waiting_human"
    QA_REVIEW = "qa_review"
    READY = "ready"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Priority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class JobType(str, Enum):
    DOCUMENT_PRODUCTION = "document_production"
    TECHNICAL_SUPPORT = "technical_support"
    CLIENT_QUERY = "client_query"
    REPORTING = "reporting"
    COMPLIANCE = "compliance"


@dataclass(frozen=True)
class JobRequest:
    title: str
    client: str
    matter: str
    instructions: str
    requested_by: str
    deadline: datetime | None = None
    priority: Priority = Priority.NORMAL
    job_type: JobType = JobType.DOCUMENT_PRODUCTION
    source: str = "dashboard"
    files: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Job:
    id: str
    title: str
    client: str
    matter: str
    instructions: str
    requested_by: str
    deadline: datetime
    priority: Priority
    job_type: JobType
    status: JobStatus = JobStatus.NEW
    risk_level: RiskLevel = RiskLevel.LOW
    source: str = "dashboard"
    files: list[str] = field(default_factory=list)
    assigned_agent: str = "orchestrator"
    estimated_effort_hours: float = 1.0
    qa_status: str = "not_started"
    escalation_reason: str = ""
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class AgentResult:
    agent_name: str
    summary: str
    status: JobStatus | None = None
    risk_level: RiskLevel | None = None
    assigned_agent: str | None = None
    qa_status: str | None = None
    estimated_effort_hours: float | None = None
    escalation_reason: str = ""
    client_message: str = ""
    actions: list[str] = field(default_factory=list)
    data: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class AuditEvent:
    job_id: str
    actor: str
    event_type: str
    message: str
    data: dict[str, Any] = field(default_factory=dict)
    id: str = field(default_factory=lambda: new_id("audit"))
    created_at: datetime = field(default_factory=utc_now)

