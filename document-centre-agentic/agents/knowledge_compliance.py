from __future__ import annotations

from agents.base import BaseAgent
from tools.brand import check_brand_compliance
from tools.models import AgentResult, Job, JobStatus


class KnowledgeComplianceAgent(BaseAgent):
    name = "Knowledge and Compliance Agent"

    def run(self, job: Job) -> AgentResult:
        qa_status, findings = check_brand_compliance(job, self.config.get("brand", {}))
        return AgentResult(
            agent_name=self.name,
            summary="Knowledge and compliance check completed.",
            status=JobStatus.WAITING_HUMAN if qa_status != "passed" else JobStatus.IN_PROGRESS,
            qa_status=qa_status,
            escalation_reason="Compliance findings require review." if qa_status != "passed" else "",
            actions=findings,
        )

