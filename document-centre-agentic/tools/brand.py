from __future__ import annotations

import re
from pathlib import Path

from tools.models import Job


def check_brand_compliance(job: Job, brand_config: dict) -> tuple[str, list[str]]:
    findings: list[str] = []
    instructions = job.instructions.lower()
    metadata = job.metadata or {}

    for field in brand_config.get("required_metadata", []):
        if not metadata.get(field) and field not in {"client", "matter"}:
            findings.append(f"Missing required metadata: {field}.")

    if brand_config.get("required_footer", "").lower() not in instructions:
        findings.append("Confirm confidentiality footer/disclaimer before release.")

    template = metadata.get("template")
    approved_templates = set(brand_config.get("approved_templates", []))
    if template and template not in approved_templates:
        findings.append(f"Template '{template}' is not in the approved template list.")
    if not template:
        findings.append("No template family recorded.")

    for file_name in job.files:
        if not _looks_versioned(file_name):
            findings.append(f"File name should include version marker: {Path(file_name).name}.")

    if findings:
        return "needs_review", findings
    return "passed", ["Brand and release checks passed against configured rules."]


def _looks_versioned(file_name: str) -> bool:
    return bool(re.search(r"[_-]v\d{1,3}\.", file_name, flags=re.IGNORECASE))

