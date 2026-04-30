# Document Centre Agentic Operations System

Production-ready starter system for coordinating document production work in a legal or professional services Document Centre.

The system uses a central orchestrator agent supported by specialist agents for document production, scheduling, monitoring, client service, technical support, reporting, and knowledge/compliance. It is designed to augment or automate large parts of a Document Centre Coordinator role: intake, triage, deadline control, bottleneck detection, quality assurance, audit trails, client updates, reporting, and shift handovers.

## Architecture

This implementation uses a lightweight local agent framework instead of requiring hosted LLM credentials. That keeps the system useful on day one in restricted legal environments and makes every decision auditable. The code uses LangGraph-style state transitions: an intake request becomes a persisted job, the orchestrator evaluates state, routes to specialist agents, agents return actions and evidence, and the orchestrator updates status, risk, audit, and notifications.

You can later replace individual deterministic agent methods with LangGraph or LangChain nodes without changing the storage, workflow, UI, or audit contracts.

## Core Capabilities

- Central orchestration for all incoming requests.
- Specialist agent routing by request type, urgency, document format, and client need.
- SQLite persistence for jobs, clients, audit events, comments, handovers, and metrics.
- Deadline and SLA tracking with proactive risk scoring.
- Bottleneck detection with simulated staffing capacity and escalation triggers.
- Document production checks for format, versioning, redaction, brand, and QA.
- Client service drafting for acknowledgements, status updates, complaints, and escalations.
- Shift handover generation covering completed work, pending work, risks, blockers, and staffing.
- Streamlit dashboard for intake, operations view, handover, reports, and job detail.
- CLI entry point for local operation and scripted use.

## Folder Structure

```text
/document-centre-agentic
├── README.md
├── skills.md
├── agents.md
├── main.py
├── config/
├── agents/
├── tools/
├── workflows/
├── ui/
└── tests/
```

## Requirements

- Python 3.11+
- Optional: Streamlit for the dashboard
- Optional: pytest for tests

Install:

```bash
cd document-centre-agentic
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

The core CLI uses only the Python standard library. Streamlit and pytest are listed for the dashboard and tests.

## Run

Initialise the database:

```bash
python main.py init
```

Create a sample workload and process it:

```bash
python main.py demo
python main.py process
```

Generate a shift handover:

```bash
python main.py handover --shift "Late"
```

Start the dashboard:

```bash
streamlit run ui/app.py
```

By default the SQLite database is created at:

```text
document-centre-agentic/data/document_centre.sqlite3
```

Override it with:

```bash
export DCA_DB_PATH=/path/to/document_centre.sqlite3
```

## Operational Model

1. A request enters through the dashboard, CLI, email/Teams/Slack adapter, or API adapter.
2. The orchestrator stores it as a job and applies SLA, priority, and risk rules.
3. Specialist agents run based on job type and current state.
4. Every action writes an audit event.
5. The scheduling and monitoring agents continuously flag deadline and capacity risks.
6. Client service produces communications for acknowledgement, updates, and escalation.
7. Reporting and handover workflows provide leadership visibility.

## Human-In-The-Loop

The system escalates to a human coordinator when:

- deadline risk is high or critical,
- quality checks fail,
- complaint language is detected,
- missing files or instructions block work,
- document redaction or legal judgment is required,
- workload exceeds simulated agent/team capacity.

Escalations are persisted and visible in the dashboard and handover.

## Extending

Add a new tool in `tools/`, then inject it into an agent or the orchestrator. Add a new agent in `agents/` by subclassing `BaseAgent` and returning an `AgentResult`. The orchestrator is intentionally small and explicit so routing and audit behaviour remain reviewable.

## Job Description Coverage

The system is built against the supplied Document Centre Coordinator job ad:

- high-quality document services with accuracy and deadlines,
- workflow coordination across the Document Centre,
- first-line team queries and escalation,
- productivity monitoring and bottleneck detection,
- staffing level checks and management escalation,
- first-line queries and complaint handling,
- professional formatting in line with brand guidelines,
- document-related technical troubleshooting,
- multi-project prioritisation,
- client relationship and customer service support,
- monthly reporting data collation,
- shift handover communication,
- continuous technical knowledge development.

Agent behaviour mirrors the About You section: experienced in legal/professional services document production, technically capable, clear in writing, calm under pressure, detail-oriented, proactive, independent, adaptable, and solutions-focused.
