from __future__ import annotations

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st

from agents.orchestrator import OrchestratorAgent
from tools.config import db_path, load_config
from tools.intake import classify_request
from tools.models import JobStatus, Priority
from tools.reporting import kpi_summary, monthly_report_text
from tools.storage import Storage
from workflows.handover import generate_handover


@st.cache_resource
def system() -> tuple[Storage, OrchestratorAgent]:
    config = load_config()
    storage = Storage(db_path())
    storage.init_db()
    return storage, OrchestratorAgent(storage, config)


def main() -> None:
    st.set_page_config(page_title="Document Centre Operations", layout="wide")
    storage, orchestrator = system()
    st.title("Document Centre Operations")

    page = st.sidebar.radio(
        "View",
        ["Intake", "Operations Queue", "Job Detail", "Shift Handover", "Reports"],
    )

    if page == "Intake":
        intake_view(orchestrator)
    elif page == "Operations Queue":
        queue_view(storage, orchestrator)
    elif page == "Job Detail":
        detail_view(storage, orchestrator)
    elif page == "Shift Handover":
        handover_view(storage)
    else:
        reports_view(storage)


def intake_view(orchestrator: OrchestratorAgent) -> None:
    st.subheader("New Request")
    with st.form("intake_form"):
        title = st.text_input("Title")
        client = st.text_input("Client")
        matter = st.text_input("Matter")
        requested_by = st.text_input("Requested by")
        instructions = st.text_area("Instructions", height=160)
        col1, col2 = st.columns(2)
        with col1:
            priority = st.selectbox("Priority", [priority.value for priority in Priority], index=1)
            due_date = st.date_input("Deadline date", value=datetime.now(timezone.utc).date())
        with col2:
            due_time = st.time_input("Deadline time", value=(datetime.now() + timedelta(hours=24)).time().replace(second=0, microsecond=0))
            files = st.text_area("Files, one per line", height=80)
        submitted = st.form_submit_button("Create request")

    if submitted:
        if not all([title, client, matter, requested_by, instructions]):
            st.error("Title, client, matter, requested by, and instructions are required.")
            return
        deadline = datetime.combine(due_date, due_time, tzinfo=timezone.utc)
        request = classify_request(
            title=title,
            client=client,
            matter=matter,
            instructions=instructions,
            requested_by=requested_by,
            deadline=deadline,
            priority=priority,
            source="dashboard",
            files=[line.strip() for line in files.splitlines() if line.strip()],
        )
        job = orchestrator.intake(request)
        st.success(f"Created {job.id}")


def queue_view(storage: Storage, orchestrator: OrchestratorAgent) -> None:
    jobs = storage.list_jobs(include_completed=False)
    summary = kpi_summary(jobs)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Open", summary["open_jobs"])
    c2.metric("High/Critical", summary["critical_or_high_risk"])
    c3.metric("Types", len(summary["by_type"]))
    c4.metric("Agents", len(summary["effort_by_agent"]))

    col1, col2 = st.columns([1, 1])
    if col1.button("Process open queue", type="primary"):
        processed = orchestrator.process_open_jobs()
        st.success(f"Processed {len(processed)} jobs.")
        st.rerun()
    include_completed = col2.checkbox("Include completed", value=False)
    jobs = storage.list_jobs(include_completed=include_completed)

    st.subheader("Queue")
    if not jobs:
        st.info("No jobs found.")
        return

    rows = [
        {
            "id": job.id,
            "title": job.title,
            "client": job.client,
            "matter": job.matter,
            "status": job.status.value,
            "priority": job.priority.value,
            "risk": job.risk_level.value,
            "deadline": job.deadline.strftime("%Y-%m-%d %H:%M UTC"),
            "owner": job.assigned_agent,
            "qa": job.qa_status,
        }
        for job in jobs
    ]
    st.dataframe(rows, use_container_width=True, hide_index=True)


def detail_view(storage: Storage, orchestrator: OrchestratorAgent) -> None:
    jobs = storage.list_jobs(include_completed=True)
    if not jobs:
        st.info("No jobs available.")
        return
    selected = st.selectbox("Job", [f"{job.id} | {job.title}" for job in jobs])
    job_id = selected.split(" | ", 1)[0]
    job = storage.get_job(job_id)
    if not job:
        st.error("Job not found.")
        return

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Status", job.status.value)
    c2.metric("Risk", job.risk_level.value)
    c3.metric("Priority", job.priority.value)
    c4.metric("QA", job.qa_status)

    st.write(f"**Client/Matter:** {job.client} / {job.matter}")
    st.write(f"**Deadline:** {job.deadline.strftime('%Y-%m-%d %H:%M UTC')}")
    st.write(f"**Owner:** {job.assigned_agent}")
    st.write("**Instructions**")
    st.write(job.instructions)

    if job.escalation_reason:
        st.warning(job.escalation_reason)

    col1, col2 = st.columns(2)
    if col1.button("Process this job"):
        orchestrator.process_job(job.id)
        st.rerun()
    if col2.button("Mark completed"):
        orchestrator.complete_job(job.id)
        st.rerun()

    with st.form("comment"):
        message = st.text_area("Add note")
        submitted = st.form_submit_button("Save note")
    if submitted and message.strip():
        storage.add_comment(job.id, "dashboard_user", message.strip())
        st.rerun()

    st.subheader("Audit Trail")
    audit = storage.list_audit(job.id, limit=50)
    for event in audit:
        st.caption(f"{event['created_at']} | {event['actor']} | {event['event_type']}")
        st.write(event["message"])


def handover_view(storage: Storage) -> None:
    st.subheader("Shift Handover")
    shift = st.text_input("Shift name", value="Current")
    if st.button("Generate handover", type="primary"):
        st.session_state["handover"] = generate_handover(storage, shift)
    if "handover" in st.session_state:
        st.markdown(st.session_state["handover"])

    st.subheader("Recent Handovers")
    for handover in storage.list_handovers():
        with st.expander(f"{handover['shift_name']} | {handover['created_at']}"):
            st.markdown(handover["summary"])


def reports_view(storage: Storage) -> None:
    jobs = storage.list_jobs(include_completed=True)
    summary = kpi_summary(jobs)
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Jobs", summary["total_jobs"])
    c2.metric("Open Jobs", summary["open_jobs"])
    c3.metric("High/Critical", summary["critical_or_high_risk"])

    st.subheader("Status")
    st.bar_chart(summary["by_status"])
    st.subheader("Job Types")
    st.bar_chart(summary["by_type"])
    st.subheader("Management Report")
    st.markdown(monthly_report_text(jobs))


if __name__ == "__main__":
    main()

