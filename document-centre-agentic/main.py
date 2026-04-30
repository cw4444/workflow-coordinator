from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone

from agents.orchestrator import OrchestratorAgent
from tools.config import db_path, load_config
from tools.intake import classify_request
from tools.models import JobType, Priority
from tools.reporting import monthly_report_text
from tools.storage import Storage
from workflows.handover import generate_handover


def build_system() -> tuple[Storage, OrchestratorAgent]:
    config = load_config()
    storage = Storage(db_path())
    storage.init_db()
    return storage, OrchestratorAgent(storage, config)


def cmd_init(_: argparse.Namespace) -> None:
    storage, _ = build_system()
    print(f"Database initialised at {storage.path}")


def cmd_demo(_: argparse.Namespace) -> None:
    _, orchestrator = build_system()
    samples = [
        classify_request(
            title="Urgent bundle formatting for hearing",
            client="Aster Legal",
            matter="Project Atlas",
            instructions="Urgent formatting, merge PDFs, apply legal_letter template, add Confidential footer.",
            requested_by="associate@example.com",
            deadline=datetime.now(timezone.utc) + timedelta(hours=3),
            priority=Priority.URGENT.value,
            files=["ASTER_ATLAS_bundle_v01.docx", "exhibits_v01.pdf"],
        ),
        classify_request(
            title="Client chasing late status update",
            client="Northbank Capital",
            matter="Refinancing",
            instructions="Client is unhappy and asking where the final PDF is. Please provide status urgently.",
            requested_by="partner@example.com",
            deadline=datetime.now(timezone.utc) + timedelta(hours=2),
            priority=Priority.HIGH.value,
            files=["NORTHBANK_REFI_pack_v02.pdf"],
        ),
        classify_request(
            title="Monthly KPI report",
            client="Internal",
            matter="Document Centre Operations",
            instructions="Prepare monthly report covering volumes, SLA, throughput, complaints and bottlenecks.",
            requested_by="ops.manager@example.com",
            priority=Priority.NORMAL.value,
            files=[],
        ),
    ]
    for request in samples:
        job = orchestrator.intake(request)
        print(f"Created {job.id}: {job.title}")


def cmd_intake(args: argparse.Namespace) -> None:
    _, orchestrator = build_system()
    deadline = datetime.fromisoformat(args.deadline) if args.deadline else None
    if deadline and deadline.tzinfo is None:
        deadline = deadline.replace(tzinfo=timezone.utc)
    request = classify_request(
        title=args.title,
        client=args.client,
        matter=args.matter,
        instructions=args.instructions,
        requested_by=args.requested_by,
        deadline=deadline,
        priority=args.priority,
        source="cli",
        files=args.files or [],
    )
    job = orchestrator.intake(request)
    print(f"Created {job.id}: {job.title}")


def cmd_process(_: argparse.Namespace) -> None:
    _, orchestrator = build_system()
    processed = orchestrator.process_open_jobs()
    if not processed:
        print("No open jobs required processing.")
        return
    for job in processed:
        print(f"{job.id}: {job.status.value} | {job.risk_level.value} | {job.assigned_agent}")


def cmd_complete(args: argparse.Namespace) -> None:
    _, orchestrator = build_system()
    job = orchestrator.complete_job(args.job_id, args.note)
    print(f"Completed {job.id}: {job.title}")


def cmd_handover(args: argparse.Namespace) -> None:
    storage, _ = build_system()
    print(generate_handover(storage, args.shift))


def cmd_report(_: argparse.Namespace) -> None:
    storage, _ = build_system()
    print(monthly_report_text(storage.list_jobs(include_completed=True)))


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description="Document Centre Agentic Operations System")
    sub = root.add_subparsers(required=True)

    sub.add_parser("init").set_defaults(func=cmd_init)
    sub.add_parser("demo").set_defaults(func=cmd_demo)
    sub.add_parser("process").set_defaults(func=cmd_process)
    sub.add_parser("report").set_defaults(func=cmd_report)

    intake = sub.add_parser("intake")
    intake.add_argument("--title", required=True)
    intake.add_argument("--client", required=True)
    intake.add_argument("--matter", required=True)
    intake.add_argument("--instructions", required=True)
    intake.add_argument("--requested-by", required=True)
    intake.add_argument("--deadline", help="ISO datetime, e.g. 2026-04-30T17:00:00+00:00")
    intake.add_argument("--priority", default="normal", choices=[priority.value for priority in Priority])
    intake.add_argument("--files", nargs="*")
    intake.set_defaults(func=cmd_intake)

    complete = sub.add_parser("complete")
    complete.add_argument("job_id")
    complete.add_argument("--note", default="Completed and released.")
    complete.set_defaults(func=cmd_complete)

    handover = sub.add_parser("handover")
    handover.add_argument("--shift", default="Current")
    handover.set_defaults(func=cmd_handover)
    return root


if __name__ == "__main__":
    args = parser().parse_args()
    args.func(args)

