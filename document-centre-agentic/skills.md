# Tool and Skill Definitions

This file defines the operational tools available to the Document Centre agent system. Each skill is designed to be auditable, replaceable, and safe for legal/professional services work.

## 1. Document Processing Skill

**Purpose:** Create, edit, format, merge, convert, redact, version, and QA documents.

**Supported document classes:**

- Word documents: `.docx`
- PDF documents: `.pdf`
- PowerPoint presentations: `.pptx`
- Plain text and markdown instructions: `.txt`, `.md`
- Image/OCR inputs: `.png`, `.jpg`, `.tiff`

**Responsibilities:**

- Detect requested output type.
- Validate source files exist in the simulated document store.
- Track version numbers and file lineage.
- Identify redaction-sensitive language.
- Check whether a job needs OCR, conversion, merge, compare, or repair.
- Run brand checks against configured rules.
- Emit a QA checklist before release.

**Production integrations to add:**

- `python-docx` for Word editing.
- `pypdf` or `PyMuPDF` for PDF operations.
- `python-pptx` for presentation edits.
- OCR via Tesseract, Azure Document Intelligence, AWS Textract, or Google Document AI.
- DMS/SharePoint/NetDocuments/iManage connectors.

## 2. Calendar and Deadline Management Skill

**Purpose:** Track deadlines, SLAs, prioritisation, reminders, and escalation windows.

**Responsibilities:**

- Calculate time remaining for each job.
- Classify deadline risk as low, medium, high, or critical.
- Apply default SLA by job type and priority.
- Identify overdue work.
- Suggest reallocation when workload exceeds capacity.
- Produce scheduled reminder and escalation events.

**Production integrations to add:**

- Outlook/Exchange calendar.
- Microsoft Graph.
- Google Calendar.
- Firm-specific matter management calendars.

## 3. Email and Teams/Slack Integration Skill

**Purpose:** Receive work requests and send controlled status updates.

**Responsibilities:**

- Convert inbound emails or chat messages into job records.
- Extract client, matter, deadline, document type, attachments, and instructions.
- Prepare acknowledgements and status updates for review or sending.
- Detect complaint or escalation language.
- Preserve communication history.

**Production integrations to add:**

- Microsoft Graph mail and Teams APIs.
- Gmail API where appropriate.
- Slack Events API.
- Shared mailbox monitoring.

## 4. Database and History Skill

**Purpose:** Persist operational truth for jobs, clients, audit events, comments, handovers, and metrics.

**Implementation:** SQLite by default, with a PostgreSQL migration path.

**Responsibilities:**

- Store every intake, routing decision, quality check, communication, and escalation.
- Maintain immutable audit events.
- Enable KPI reporting.
- Support dashboard filtering and shift handovers.

**Production integrations to add:**

- PostgreSQL with role-based access.
- Data warehouse exports.
- Retention and legal hold policies.

## 5. Knowledge Update Skill

**Purpose:** Maintain current guidance on document tools, templates, brand standards, and best practice.

**Responsibilities:**

- Store firm brand guidelines and template rules.
- Flag outdated guidance.
- Provide agent-readable compliance checks.
- Support web search or intranet lookup for approved sources.

**Controls:**

- No external web result should override approved internal policy automatically.
- Updates require human approval before becoming active production guidance.

## 6. File System and DMS Simulation Skill

**Purpose:** Provide a local simulation of SharePoint/DMS behaviour.

**Responsibilities:**

- Store input and output file references.
- Track versions.
- Represent matter/client folder locations.
- Validate naming conventions.

**Production integrations to add:**

- SharePoint.
- iManage.
- NetDocuments.
- OneDrive.
- SFTP intake folders.

## 7. Brand Guideline Enforcement Skill

**Purpose:** Ensure outgoing work follows firm style, templates, naming, metadata, and accessibility rules.

**Responsibilities:**

- Validate file naming.
- Check template family.
- Check required metadata.
- Confirm client/matter references are present.
- Flag missing confidentiality footer or disclaimer.
- Enforce accessibility and PDF release checklist.

## 8. Reporting and Charting Skill

**Purpose:** Generate operational reports and KPI dashboard data.

**Responsibilities:**

- Volume by job type, client, priority, and status.
- SLA performance.
- Overdue and at-risk jobs.
- Throughput by agent/team.
- Escalation count and reasons.
- Monthly leadership report text.

**Production integrations to add:**

- Power BI.
- Tableau.
- Excel export.
- Scheduled email reports.

## 9. Human Escalation Skill

**Purpose:** Keep human coordinators in control of risk-sensitive work.

**Responsibilities:**

- Request human review for quality failures, complaints, legal judgment, unclear instructions, missing files, or critical deadline pressure.
- Log the escalation reason.
- Produce a concise recommended action.
- Keep the client service agent informed for status messaging.

