from __future__ import annotations

from collections import Counter, defaultdict

from tools.models import Job, JobStatus, RiskLevel


def kpi_summary(jobs: list[Job]) -> dict:
    total = len(jobs)
    by_status = Counter(job.status.value for job in jobs)
    by_type = Counter(job.job_type.value for job in jobs)
    by_risk = Counter(job.risk_level.value for job in jobs)
    open_jobs = [job for job in jobs if job.status not in {JobStatus.COMPLETED, JobStatus.CANCELLED}]
    effort_by_agent: dict[str, float] = defaultdict(float)
    for job in open_jobs:
        effort_by_agent[job.assigned_agent] += job.estimated_effort_hours
    return {
        "total_jobs": total,
        "open_jobs": len(open_jobs),
        "completed_jobs": by_status.get(JobStatus.COMPLETED.value, 0),
        "critical_or_high_risk": by_risk.get(RiskLevel.CRITICAL.value, 0) + by_risk.get(RiskLevel.HIGH.value, 0),
        "by_status": dict(by_status),
        "by_type": dict(by_type),
        "by_risk": dict(by_risk),
        "effort_by_agent": dict(effort_by_agent),
    }


def monthly_report_text(jobs: list[Job]) -> str:
    summary = kpi_summary(jobs)
    lines = [
        "# Monthly Document Centre Report",
        "",
        f"Total jobs handled: {summary['total_jobs']}",
        f"Open jobs: {summary['open_jobs']}",
        f"Completed jobs: {summary['completed_jobs']}",
        f"High or critical risk jobs: {summary['critical_or_high_risk']}",
        "",
        "## Status Mix",
    ]
    for status, count in sorted(summary["by_status"].items()):
        lines.append(f"- {status}: {count}")
    lines.extend(["", "## Job Type Mix"])
    for job_type, count in sorted(summary["by_type"].items()):
        lines.append(f"- {job_type}: {count}")
    lines.extend(["", "## Management Commentary"])
    if summary["critical_or_high_risk"]:
        lines.append("Immediate attention is required for high or critical risk work.")
    else:
        lines.append("No high or critical risk work is currently recorded.")
    return "\n".join(lines)

