from __future__ import annotations

from agents.base import BaseAgent
from tools.models import AgentResult, Job, JobStatus


class ReportingAgent(BaseAgent):
    name = "Reporting Agent"

    def run(self, job: Job) -> AgentResult:
        return AgentResult(
            agent_name=self.name,
            summary="Reporting request triaged for KPI collation.",
            status=JobStatus.IN_PROGRESS,
            assigned_agent=self.name,
            actions=[
                "Confirm reporting period and audience.",
                "Collate volume, SLA, risk, escalation, and throughput metrics.",
                "Prepare leadership-ready narrative with exceptions and trends.",
            ],
        )

