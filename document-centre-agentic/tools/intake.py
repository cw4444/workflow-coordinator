from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone

from tools.models import JobRequest, JobType, Priority


def classify_request(
    title: str,
    client: str,
    matter: str,
    instructions: str,
    requested_by: str,
    deadline: datetime | None = None,
    priority: str = "normal",
    source: str = "dashboard",
    files: list[str] | None = None,
) -> JobRequest:
    text = f"{title} {instructions}".lower()
    job_type = JobType.DOCUMENT_PRODUCTION
    if any(word in text for word in ["error", "corrupt", "locked", "won't open", "conversion failed"]):
        job_type = JobType.TECHNICAL_SUPPORT
    elif any(word in text for word in ["report", "kpi", "monthly"]):
        job_type = JobType.REPORTING
    elif any(word in text for word in ["policy", "brand", "template compliance", "guideline"]):
        job_type = JobType.COMPLIANCE
    elif _contains_any(text, ["complaint", "unhappy", "chase", "status", "where is", "escalate"]):
        job_type = JobType.CLIENT_QUERY

    parsed_priority = Priority(priority.lower()) if priority.lower() in Priority._value2member_map_ else Priority.NORMAL
    if _contains_any(text, ["urgent", "asap", "immediate", "critical"]):
        parsed_priority = max_priority(parsed_priority, Priority.URGENT)
    if _contains_any(text, ["complaint", "unhappy", "escalate"]):
        parsed_priority = max_priority(parsed_priority, Priority.HIGH)

    if deadline is None:
        hours = 24
        if parsed_priority == Priority.URGENT:
            hours = 4
        if parsed_priority == Priority.CRITICAL:
            hours = 1
        deadline = datetime.now(timezone.utc) + timedelta(hours=hours)

    return JobRequest(
        title=title,
        client=client,
        matter=matter,
        instructions=instructions,
        requested_by=requested_by,
        deadline=deadline,
        priority=parsed_priority,
        job_type=job_type,
        source=source,
        files=files or [],
        metadata={
            "client": client,
            "matter": matter,
            "owner": requested_by,
            "classification": "confidential",
            "template": _detect_template(text),
        },
    )


def max_priority(current: Priority, candidate: Priority) -> Priority:
    order = [Priority.LOW, Priority.NORMAL, Priority.HIGH, Priority.URGENT, Priority.CRITICAL]
    return order[max(order.index(current), order.index(candidate))]


def _contains_any(text: str, terms: list[str]) -> bool:
    return any(re.search(rf"\b{re.escape(term)}\b", text) for term in terms)


def _detect_template(text: str) -> str:
    for template in ["legal_letter", "court_bundle", "board_pack", "transaction_bible", "presentation"]:
        if template in text or template.replace("_", " ") in text:
            return template
    return "legal_letter"
