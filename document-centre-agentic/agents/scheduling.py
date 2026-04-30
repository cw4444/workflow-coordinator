from __future__ import annotations

from agents.base import BaseAgent
from tools.deadline import deadline_risk, hours_remaining
from tools.models import AgentResult, Job, JobStatus, RiskLevel


class WorkflowSchedulingAgent(BaseAgent):
    name = "Workflow and Scheduling Agent"

    def run(self, job: Job) -> AgentResult:
        risk = deadline_risk(job, self.config.get("risk_thresholds", {}))
        remaining = hours_remaining(job.deadline)
        actions = [f"Deadline is in {remaining:.2f} hours.", f"Deadline risk assessed as {risk.value}."]
        status = JobStatus.TRIAGED if job.status == JobStatus.NEW else job.status
        escalation = ""
        if risk in {RiskLevel.HIGH, RiskLevel.CRITICAL}:
            escalation = "Deadline risk requires coordinator attention and possible reallocation."
            actions.append(escalation)
        return AgentResult(
            agent_name=self.name,
            summary="Workflow priority and deadline risk assessed.",
            status=status,
            risk_level=risk,
            escalation_reason=escalation,
            actions=actions,
            data={"hours_remaining": remaining},
        )

