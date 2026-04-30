# Workflow Coordinator

Agentic Document Centre Operations System for legal and professional services workflow coordination.

The full application lives in:

```text
document-centre-agentic/
```

Start here:

- [Architecture and run guide](document-centre-agentic/README.md)
- [Agent definitions](document-centre-agentic/agents.md)
- [Tool and skill definitions](document-centre-agentic/skills.md)

## Quick Start

```bash
cd document-centre-agentic
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py demo
python main.py process
streamlit run ui/app.py
```

