from __future__ import annotations

from agents.client_services import ClientServicesAgent
from agents.document_production import DocumentProductionAgent
from agents.knowledge_compliance import KnowledgeComplianceAgent
from agents.monitoring import ProductivityMonitoringAgent
from agents.reporting_agent import ReportingAgent
from agents.scheduling import WorkflowSchedulingAgent
from agents.technical_support import TechnicalSupportAgent
from tools.models import AgentResult, AuditEvent, Job, JobRequest, JobStatus, JobType, RiskLevel
from tools.storage import Storage


RISK_ORDER = [RiskLevel.LOW, RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.CRITICAL]


class OrchestratorAgent:
    name = "Central Orchestrator Agent"

    def __init__(self, storage: Storage, config: dict):
        self.storage = storage
        self.config = config
        self.scheduling = WorkflowSchedulingAgent(config)
        self.monitoring = ProductivityMonitoringAgent(config)
        self.client_services = ClientServicesAgent(config)
        self.specialists = {
            JobType.DOCUMENT_PRODUCTION: DocumentProductionAgent(config),
            JobType.TECHNICAL_SUPPORT: TechnicalSupportAgent(config),
            JobType.CLIENT_QUERY: ClientServicesAgent(config),
            JobType.REPORTING: ReportingAgent(config),
            JobType.COMPLIANCE: KnowledgeComplianceAgent(config),
        }

    def intake(self, request: JobRequest) -> Job:
        sla_key = "standard"
        if request.priority.value in {"urgent", "critical"}:
            sla_key = request.priority.value
        if request.job_type == JobType.CLIENT_QUERY and "complaint" in request.instructions.lower():
            sla_key = "complaint"
        default_sla = self.config.get("sla_hours", {}).get(sla_key, 24)
        job = self.storage.create_job(request, default_sla_hours=default_sla)
        self.storage.add_audit(
            AuditEvent(job.id, self.name, "intake", f"Intake received via {job.source}; routed for triage.")
        )
        return job

    def process_job(self, job_id: str) -> Job:
        job = self.storage.get_job(job_id)
        if not job:
            raise ValueError(f"Job not found: {job_id}")

        results = [self.scheduling.run(job)]
        job = self._apply_result(job, results[-1])

        specialist = self.specialists.get(job.job_type, self.specialists[JobType.DOCUMENT_PRODUCTION])
        results.append(specialist.run(job))
        job = self._apply_result(job, results[-1])

        results.append(self.monitoring.run(job))
        job = self._apply_result(job, results[-1])

        if job.risk_level in {RiskLevel.HIGH, RiskLevel.CRITICAL} or job.job_type == JobType.CLIENT_QUERY:
            results.append(self.client_services.run(job))
            job = self._apply_result(job, results[-1])

        if job.escalation_reason:
            job.status = JobStatus.WAITING_HUMAN
        elif job.qa_status == "passed" and job.status in {JobStatus.IN_PROGRESS, JobStatus.QA_REVIEW}:
            job.status = JobStatus.READY
        elif job.status == JobStatus.NEW:
            job.status = JobStatus.TRIAGED

        self.storage.upsert_job(job)
        self.storage.add_audit(
            AuditEvent(
                job.id,
                self.name,
                "orchestration_complete",
                f"Processed job with {len(results)} agent passes. Current status: {job.status.value}.",
                {"agents": [result.agent_name for result in results]},
            )
        )
        return job

    def process_open_jobs(self) -> list[Job]:
        processed: list[Job] = []
        for job in self.storage.list_jobs(include_completed=False):
            if job.status not in {JobStatus.WAITING_HUMAN, JobStatus.COMPLETED, JobStatus.CANCELLED}:
                processed.append(self.process_job(job.id))
        return processed

    def complete_job(self, job_id: str, note: str = "Completed and released.") -> Job:
        job = self.storage.get_job(job_id)
        if not job:
            raise ValueError(f"Job not found: {job_id}")
        job.status = JobStatus.COMPLETED
        job.qa_status = "passed" if job.qa_status == "not_started" else job.qa_status
        self.storage.upsert_job(job)
        self.storage.add_audit(AuditEvent(job.id, self.name, "job_completed", note))
        return job

    def _apply_result(self, job: Job, result: AgentResult) -> Job:
        if result.status:
            job.status = result.status
        if result.risk_level:
            job.risk_level = _max_risk(job.risk_level, result.risk_level)
        if result.assigned_agent:
            job.assigned_agent = result.assigned_agent
        if result.qa_status:
            job.qa_status = result.qa_status
        if result.estimated_effort_hours:
            job.estimated_effort_hours = result.estimated_effort_hours
        if result.escalation_reason:
            job.escalation_reason = result.escalation_reason

        self.storage.upsert_job(job)
        self.storage.add_audit(
            AuditEvent(
                job.id,
                result.agent_name,
                "agent_result",
                result.summary,
                {
                    "actions": result.actions,
                    "client_message": result.client_message,
                    "data": result.data,
                    "escalation_reason": result.escalation_reason,
                },
            )
        )
        return job


def _max_risk(current: RiskLevel, candidate: RiskLevel) -> RiskLevel:
    return RISK_ORDER[max(RISK_ORDER.index(current), RISK_ORDER.index(candidate))]

