from __future__ import annotations

from agents.base import BaseAgent
from tools.models import AgentResult, Job, JobStatus, RiskLevel


class TechnicalSupportAgent(BaseAgent):
    name = "Technical Support Agent"

    def run(self, job: Job) -> AgentResult:
        text = job.instructions.lower()
        actions = []
        risk = None
        escalation = ""
        if "corrupt" in text or "won't open" in text:
            actions.append("Attempt file repair using backup copy, previous version, or application open-and-repair.")
            escalation = "Potential corrupt file; preserve original and request replacement if repair fails."
            risk = RiskLevel.HIGH
        if "font" in text:
            actions.append("Check approved font availability and template font mapping.")
        if "conversion" in text or "pdf" in text:
            actions.append("Retry conversion with print-to-PDF fallback and validate bookmarks/security.")
        if not actions:
            actions.append("Review file, application version, permissions, and template dependencies.")
        return AgentResult(
            agent_name=self.name,
            summary="Technical troubleshooting plan prepared.",
            status=JobStatus.WAITING_HUMAN if escalation else JobStatus.IN_PROGRESS,
            risk_level=risk,
            escalation_reason=escalation,
            actions=actions,
        )

