from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from tools.models import AuditEvent, Job, JobRequest, JobStatus, JobType, Priority, RiskLevel, new_id, utc_now


def _dt(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat()


def _parse_dt(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


class Storage:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self) -> None:
        with self.connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS jobs (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    client TEXT NOT NULL,
                    matter TEXT NOT NULL,
                    instructions TEXT NOT NULL,
                    requested_by TEXT NOT NULL,
                    deadline TEXT NOT NULL,
                    priority TEXT NOT NULL,
                    job_type TEXT NOT NULL,
                    status TEXT NOT NULL,
                    risk_level TEXT NOT NULL,
                    source TEXT NOT NULL,
                    files_json TEXT NOT NULL,
                    assigned_agent TEXT NOT NULL,
                    estimated_effort_hours REAL NOT NULL,
                    qa_status TEXT NOT NULL,
                    escalation_reason TEXT NOT NULL,
                    metadata_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS audit_events (
                    id TEXT PRIMARY KEY,
                    job_id TEXT NOT NULL,
                    actor TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    message TEXT NOT NULL,
                    data_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS comments (
                    id TEXT PRIMARY KEY,
                    job_id TEXT NOT NULL,
                    author TEXT NOT NULL,
                    message TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS handovers (
                    id TEXT PRIMARY KEY,
                    shift_name TEXT NOT NULL,
                    summary TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                """
            )

    def create_job(self, request: JobRequest, default_sla_hours: int = 24) -> Job:
        deadline = request.deadline or (utc_now() + timedelta(hours=default_sla_hours))
        job = Job(
            id=new_id("job"),
            title=request.title,
            client=request.client,
            matter=request.matter,
            instructions=request.instructions,
            requested_by=request.requested_by,
            deadline=deadline,
            priority=request.priority,
            job_type=request.job_type,
            source=request.source,
            files=list(request.files),
            metadata=dict(request.metadata),
        )
        self.upsert_job(job)
        self.add_audit(AuditEvent(job.id, "orchestrator", "job_created", f"Created job '{job.title}'."))
        return job

    def upsert_job(self, job: Job) -> None:
        job.updated_at = utc_now()
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO jobs VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    title=excluded.title,
                    client=excluded.client,
                    matter=excluded.matter,
                    instructions=excluded.instructions,
                    requested_by=excluded.requested_by,
                    deadline=excluded.deadline,
                    priority=excluded.priority,
                    job_type=excluded.job_type,
                    status=excluded.status,
                    risk_level=excluded.risk_level,
                    source=excluded.source,
                    files_json=excluded.files_json,
                    assigned_agent=excluded.assigned_agent,
                    estimated_effort_hours=excluded.estimated_effort_hours,
                    qa_status=excluded.qa_status,
                    escalation_reason=excluded.escalation_reason,
                    metadata_json=excluded.metadata_json,
                    updated_at=excluded.updated_at
                """,
                (
                    job.id,
                    job.title,
                    job.client,
                    job.matter,
                    job.instructions,
                    job.requested_by,
                    _dt(job.deadline),
                    job.priority.value,
                    job.job_type.value,
                    job.status.value,
                    job.risk_level.value,
                    job.source,
                    json.dumps(job.files),
                    job.assigned_agent,
                    job.estimated_effort_hours,
                    job.qa_status,
                    job.escalation_reason,
                    json.dumps(job.metadata),
                    _dt(job.created_at),
                    _dt(job.updated_at),
                ),
            )

    def get_job(self, job_id: str) -> Job | None:
        with self.connect() as conn:
            row = conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
        return self._row_to_job(row) if row else None

    def list_jobs(self, include_completed: bool = True) -> list[Job]:
        query = "SELECT * FROM jobs"
        params: tuple[Any, ...] = ()
        if not include_completed:
            query += " WHERE status NOT IN (?, ?)"
            params = (JobStatus.COMPLETED.value, JobStatus.CANCELLED.value)
        query += " ORDER BY deadline ASC, created_at ASC"
        with self.connect() as conn:
            rows = conn.execute(query, params).fetchall()
        return [self._row_to_job(row) for row in rows]

    def add_audit(self, event: AuditEvent) -> None:
        with self.connect() as conn:
            conn.execute(
                "INSERT INTO audit_events VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    event.id,
                    event.job_id,
                    event.actor,
                    event.event_type,
                    event.message,
                    json.dumps(event.data),
                    _dt(event.created_at),
                ),
            )

    def list_audit(self, job_id: str | None = None, limit: int = 100) -> list[sqlite3.Row]:
        query = "SELECT * FROM audit_events"
        params: tuple[Any, ...] = ()
        if job_id:
            query += " WHERE job_id = ?"
            params = (job_id,)
        query += " ORDER BY created_at DESC LIMIT ?"
        params = (*params, limit)
        with self.connect() as conn:
            return conn.execute(query, params).fetchall()

    def add_comment(self, job_id: str, author: str, message: str) -> None:
        with self.connect() as conn:
            conn.execute(
                "INSERT INTO comments VALUES (?, ?, ?, ?, ?)",
                (new_id("comment"), job_id, author, message, _dt(utc_now())),
            )
        self.add_audit(AuditEvent(job_id, author, "comment", message))

    def save_handover(self, shift_name: str, summary: str) -> str:
        handover_id = new_id("handover")
        with self.connect() as conn:
            conn.execute(
                "INSERT INTO handovers VALUES (?, ?, ?, ?)",
                (handover_id, shift_name, summary, _dt(utc_now())),
            )
        return handover_id

    def list_handovers(self, limit: int = 10) -> list[sqlite3.Row]:
        with self.connect() as conn:
            return conn.execute(
                "SELECT * FROM handovers ORDER BY created_at DESC LIMIT ?", (limit,)
            ).fetchall()

    def _row_to_job(self, row: sqlite3.Row) -> Job:
        return Job(
            id=row["id"],
            title=row["title"],
            client=row["client"],
            matter=row["matter"],
            instructions=row["instructions"],
            requested_by=row["requested_by"],
            deadline=_parse_dt(row["deadline"]),
            priority=Priority(row["priority"]),
            job_type=JobType(row["job_type"]),
            status=JobStatus(row["status"]),
            risk_level=RiskLevel(row["risk_level"]),
            source=row["source"],
            files=json.loads(row["files_json"]),
            assigned_agent=row["assigned_agent"],
            estimated_effort_hours=float(row["estimated_effort_hours"]),
            qa_status=row["qa_status"],
            escalation_reason=row["escalation_reason"],
            metadata=json.loads(row["metadata_json"]),
            created_at=_parse_dt(row["created_at"]),
            updated_at=_parse_dt(row["updated_at"]),
        )

