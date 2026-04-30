from __future__ import annotations

from datetime import datetime, timezone

from tools.models import Job, Priority, RiskLevel


def hours_remaining(deadline: datetime) -> float:
    return (deadline.astimezone(timezone.utc) - datetime.now(timezone.utc)).total_seconds() / 3600


def deadline_risk(job: Job, thresholds: dict[str, float]) -> RiskLevel:
    remaining = hours_remaining(job.deadline)
    if remaining <= thresholds.get("critical_hours_remaining", 1):
        return RiskLevel.CRITICAL
    if remaining <= thresholds.get("high_hours_remaining", 4):
        return RiskLevel.HIGH
    if remaining <= thresholds.get("medium_hours_remaining", 12):
        return RiskLevel.MEDIUM
    if job.priority in {Priority.URGENT, Priority.CRITICAL}:
        return RiskLevel.MEDIUM
    return RiskLevel.LOW


def priority_score(job: Job) -> tuple[int, float]:
    priority_weight = {
        Priority.CRITICAL: 0,
        Priority.URGENT: 1,
        Priority.HIGH: 2,
        Priority.NORMAL: 3,
        Priority.LOW: 4,
    }[job.priority]
    return priority_weight, hours_remaining(job.deadline)

