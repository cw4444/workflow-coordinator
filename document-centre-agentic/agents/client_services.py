from __future__ import annotations

import re

from agents.base import BaseAgent
from tools.deadline import hours_remaining
from tools.models import AgentResult, Job, JobStatus, RiskLevel


COMPLAINT_TERMS = {"complaint", "unhappy", "disappointed", "poor service", "late", "chase", "escalate"}


class ClientServicesAgent(BaseAgent):
    name = "Client Services and Queries Agent"

    def run(self, job: Job) -> AgentResult:
        text = f"{job.title} {job.instructions}".lower()
        is_complaint = any(re.search(rf"\b{re.escape(term)}\b", text) for term in COMPLAINT_TERMS)
        remaining = hours_remaining(job.deadline)
        message = (
            f"Thank you for your request. We have logged it as {job.id} for {job.client} / {job.matter}. "
            f"The current target deadline is {job.deadline.strftime('%Y-%m-%d %H:%M UTC')}."
        )
        if remaining < 0:
            message += " This is currently overdue and has been escalated for immediate review."
        elif remaining <= 4:
            message += " We are treating this as time-sensitive and monitoring it closely."
        else:
            message += " We will provide an update if anything affects timing or scope."

        escalation = "Complaint or relationship-risk language detected; human coordinator should review response." if is_complaint else ""
        return AgentResult(
            agent_name=self.name,
            summary="Client communication prepared.",
            status=JobStatus.WAITING_HUMAN if is_complaint else job.status,
            risk_level=RiskLevel.HIGH if is_complaint else None,
            escalation_reason=escalation,
            client_message=message,
            actions=["Prepared client acknowledgement/status message."] + ([escalation] if escalation else []),
            data={"complaint_detected": is_complaint},
        )
