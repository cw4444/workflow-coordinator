from __future__ import annotations

from agents.base import BaseAgent
from tools.models import AgentResult, Job, JobStatus


class ProductivityMonitoringAgent(BaseAgent):
    name = "Productivity and Monitoring Agent"

    def run(self, job: Job) -> AgentResult:
        threshold = self.config.get("staffing", {}).get("human_escalation_threshold", 0.85)
        capacity = self.config.get("staffing", {}).get("agent_capacity_hours_per_shift", 7)
        utilisation = min(job.estimated_effort_hours / capacity, 2.0)
        actions = [f"Job uses approximately {utilisation:.0%} of one agent shift capacity."]
        escalation = ""
        if utilisation >= threshold:
            escalation = "Estimated effort is high for one shift; consider splitting work or adding human support."
            actions.append(escalation)
        return AgentResult(
            agent_name=self.name,
            summary="Productivity and capacity check completed.",
            status=job.status if job.status != JobStatus.NEW else JobStatus.TRIAGED,
            escalation_reason=escalation,
            actions=actions,
            data={"utilisation": utilisation, "single_agent_capacity_hours": capacity},
        )

