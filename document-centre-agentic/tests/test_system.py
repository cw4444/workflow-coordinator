from __future__ import annotations

from datetime import datetime, timedelta, timezone

from agents.orchestrator import OrchestratorAgent
from tools.config import load_config
from tools.intake import classify_request
from tools.models import JobStatus, Priority, RiskLevel
from tools.reporting import kpi_summary
from tools.storage import Storage
from workflows.handover import generate_handover


def make_system(tmp_path):
    storage = Storage(tmp_path / "test.sqlite3")
    storage.init_db()
    config = load_config()
    return storage, OrchestratorAgent(storage, config)


def test_intake_and_process_document_job(tmp_path):
    storage, orchestrator = make_system(tmp_path)
    request = classify_request(
        title="Urgent PDF bundle",
        client="Client A",
        matter="Matter 1",
        instructions="Urgent merge and format PDF bundle with Confidential footer.",
        requested_by="lawyer@example.com",
        deadline=datetime.now(timezone.utc) + timedelta(hours=2),
        priority=Priority.URGENT.value,
        files=["CLIENT_MATTER_bundle_v01.docx"],
    )

    job = orchestrator.intake(request)
    processed = orchestrator.process_job(job.id)

    assert processed.id == job.id
    assert processed.status in {JobStatus.READY, JobStatus.IN_PROGRESS, JobStatus.WAITING_HUMAN}
    assert processed.risk_level in {RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.CRITICAL}
    assert storage.list_audit(job.id)


def test_complaint_routes_to_human_review(tmp_path):
    _, orchestrator = make_system(tmp_path)
    request = classify_request(
        title="Client complaint",
        client="Client B",
        matter="Matter 2",
        instructions="Client is unhappy and wants this escalated.",
        requested_by="partner@example.com",
    )

    job = orchestrator.intake(request)
    processed = orchestrator.process_job(job.id)

    assert processed.status == JobStatus.WAITING_HUMAN
    assert processed.escalation_reason


def test_handover_and_reporting(tmp_path):
    storage, orchestrator = make_system(tmp_path)
    request = classify_request(
        title="Monthly KPI",
        client="Internal",
        matter="Ops",
        instructions="Prepare monthly KPI report.",
        requested_by="ops@example.com",
    )
    job = orchestrator.intake(request)
    orchestrator.process_job(job.id)

    summary = kpi_summary(storage.list_jobs(include_completed=True))
    handover = generate_handover(storage, "Test")

    assert summary["total_jobs"] == 1
    assert "Test Shift Handover" in handover
    assert job.id in handover

