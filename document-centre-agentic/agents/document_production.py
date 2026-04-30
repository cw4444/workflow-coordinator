from __future__ import annotations

from agents.base import BaseAgent
from tools.brand import check_brand_compliance
from tools.document_tools import detect_document_operations, estimate_effort_hours, release_checklist
from tools.models import AgentResult, Job, JobStatus, RiskLevel


class DocumentProductionAgent(BaseAgent):
    name = "Document Production Agent"

    def run(self, job: Job) -> AgentResult:
        operations = detect_document_operations(job.instructions, job.files)
        effort = estimate_effort_hours(operations, len(job.files), job.priority.value)
        qa_status, brand_findings = check_brand_compliance(job, self.config.get("brand", {}))
        checklist = release_checklist(operations)
        escalation = ""
        risk = None

        if "redaction" in operations:
            escalation = "Human review required for redaction-sensitive work."
            risk = RiskLevel.HIGH
        elif qa_status != "passed":
            escalation = "Brand or release checks need review before client delivery."

        actions = [
            f"Detected operations: {', '.join(operations)}.",
            f"Estimated production effort: {effort} hours.",
            *brand_findings,
            *checklist,
        ]
        return AgentResult(
            agent_name=self.name,
            summary="Document production assessment completed.",
            status=JobStatus.QA_REVIEW if qa_status != "passed" else JobStatus.IN_PROGRESS,
            risk_level=risk,
            assigned_agent=self.name,
            qa_status=qa_status,
            estimated_effort_hours=effort,
            escalation_reason=escalation,
            actions=actions,
            data={"operations": operations, "checklist": checklist, "brand_findings": brand_findings},
        )

