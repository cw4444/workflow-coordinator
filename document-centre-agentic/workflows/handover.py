from __future__ import annotations

from datetime import datetime, timezone

from tools.deadline import hours_remaining
from tools.models import Job, JobStatus, RiskLevel
from tools.reporting import kpi_summary
from tools.storage import Storage


def generate_handover(storage: Storage, shift_name: str = "Current") -> str:
    jobs = storage.list_jobs(include_completed=True)
    open_jobs = [job for job in jobs if job.status not in {JobStatus.COMPLETED, JobStatus.CANCELLED}]
    completed = [job for job in jobs if job.status == JobStatus.COMPLETED]
    risks = [job for job in open_jobs if job.risk_level in {RiskLevel.HIGH, RiskLevel.CRITICAL}]
    blockers = [job for job in open_jobs if job.status == JobStatus.WAITING_HUMAN or job.escalation_reason]
    summary = kpi_summary(jobs)

    lines = [
        f"# {shift_name} Shift Handover",
        f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        "",
        "## Snapshot",
        f"- Open jobs: {summary['open_jobs']}",
        f"- Completed jobs: {summary['completed_jobs']}",
        f"- High/critical risk jobs: {summary['critical_or_high_risk']}",
        "",
        "## Completed Work",
    ]
    if completed:
        for job in completed[-10:]:
            lines.append(f"- {job.id}: {job.title} ({job.client} / {job.matter})")
    else:
        lines.append("- None recorded.")

    lines.extend(["", "## Pending Work"])
    if open_jobs:
        for job in sorted(open_jobs, key=lambda item: item.deadline)[:15]:
            lines.append(
                f"- {job.id}: {job.title} | {job.status.value} | {job.risk_level.value} | "
                f"due in {hours_remaining(job.deadline):.1f}h | owner {job.assigned_agent}"
            )
    else:
        lines.append("- No open jobs.")

    lines.extend(["", "## Risks and Blockers"])
    if risks or blockers:
        seen = set()
        for job in risks + blockers:
            if job.id in seen:
                continue
            seen.add(job.id)
            reason = job.escalation_reason or "Deadline or quality risk."
            lines.append(f"- {job.id}: {reason}")
    else:
        lines.append("- No active high-risk blockers recorded.")

    lines.extend(["", "## Staffing and Capacity"])
    effort = sum(job.estimated_effort_hours for job in open_jobs)
    lines.append(f"- Estimated open effort: {effort:.1f} hours.")
    if effort > 20:
        lines.append("- Recommend management review for additional resource or reallocation.")
    else:
        lines.append("- Current simulated capacity appears manageable.")

    handover = "\n".join(lines)
    storage.save_handover(shift_name, handover)
    return handover

