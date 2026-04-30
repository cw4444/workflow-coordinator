# Workflow Coordinator

This is a small local web app for coordinating Document Centre work: new requests, deadlines, risk flags, client updates, reports, and shift handovers.

Built by [Codex from OpenAI](https://chatgpt.com/codex/cloud).

It is not an `.exe` yet. For now, you run it with Python and open it in your browser. You do not need to edit the code to try it.

## What You Get

- A browser dashboard for Document Centre requests.
- A sample workload you can load immediately.
- Deadline and risk checks.
- Agent-style routing for document production, client queries, reporting, technical issues, and compliance.
- Shift handover summaries.
- A local SQLite database saved on your own machine.

## Before You Start

You need:

- Python 3.11 or newer
- Git, unless you use the ZIP download option

If you do not have Python:

- Windows: install Python from <https://www.python.org/downloads/windows/>
- Mac: install Python from <https://www.python.org/downloads/macos/>
- Linux: use your system package manager, for example `sudo apt install python3 python3-venv`

During Python installation on Windows, tick:

```text
Add python.exe to PATH
```

## Option A: Download With Git

Open Terminal, Command Prompt, PowerShell, or WSL and run:

```bash
git clone https://github.com/cw4444/workflow-coordinator.git
cd workflow-coordinator/document-centre-agentic
```

## Option B: Download Without Git

1. Go to <https://github.com/cw4444/workflow-coordinator>
2. Click the green `Code` button.
3. Click `Download ZIP`.
4. Unzip the file somewhere sensible.
5. Open Terminal, Command Prompt, PowerShell, or WSL in the unzipped folder.
6. Go into the app folder:

```bash
cd document-centre-agentic
```

## Install The App

From inside the `document-centre-agentic` folder, run these commands.

### Windows PowerShell

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

If PowerShell blocks activation, run this once:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Then try:

```powershell
.\.venv\Scripts\Activate.ps1
```

### Mac, Linux, Or WSL

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Start The Dashboard

Still inside the `document-centre-agentic` folder, run:

```bash
streamlit run ui/app.py
```

Your browser should open automatically.

If it does not, open this address yourself:

```text
http://localhost:8501
```

## Load Demo Data

If you want some example jobs to appear in the dashboard, stop the dashboard with `Ctrl+C`, then run:

```bash
python main.py demo
python main.py process
streamlit run ui/app.py
```

On Windows, if `python` does not work, use:

```powershell
py main.py demo
py main.py process
streamlit run ui/app.py
```

## Where The App Is

The actual app folder is:

```text
document-centre-agentic/
```

Important files:

- `ui/app.py` starts the dashboard.
- `main.py` runs command-line actions.
- `data/document_centre.sqlite3` is the local database, created when you run the app.
- `document-centre-agentic/README.md` has the more technical architecture notes.

## Common Problems

### `python` is not recognised

Try:

```bash
python3 --version
```

or on Windows:

```powershell
py --version
```

If none of those work, Python is not installed or was not added to PATH.

### `streamlit` is not recognised

Activate the virtual environment first.

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Mac, Linux, or WSL:

```bash
source .venv/bin/activate
```

Then run:

```bash
streamlit run ui/app.py
```

### The browser opens but there is no data

That is normal on the first run. Add a request in the `Intake` screen, or load demo data:

```bash
python main.py demo
python main.py process
```

### I am using WSL and cannot find the files in Windows

The Windows Explorer path usually looks like:

```text
\\wsl.localhost\Ubuntu\home\YOUR_USERNAME\projects\workflow-coordinator
```

For this local build, the path was:

```text
\\wsl.localhost\Ubuntu\home\cw444\projects\workflow-coordinator
```

## Stop The App

Go back to the terminal running Streamlit and press:

```text
Ctrl+C
```

## Is This Safe To Put On GitHub?

The repo ignores common local/private files such as:

- `.env`
- local databases
- virtual environments
- Python caches
- Streamlit local state
- credential and key files

Do not manually upload private client documents, real credentials, or production databases to GitHub.

## More Technical Notes

For architecture, agents, tools, and extension details:

- [Architecture README](document-centre-agentic/README.md)
- [Agent definitions](document-centre-agentic/agents.md)
- [Tool and skill definitions](document-centre-agentic/skills.md)
