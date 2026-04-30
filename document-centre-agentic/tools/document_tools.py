from __future__ import annotations

from pathlib import Path


DOCUMENT_EXTENSIONS = {".doc", ".docx", ".pdf", ".ppt", ".pptx", ".xls", ".xlsx", ".txt", ".md"}


def detect_document_operations(instructions: str, files: list[str]) -> list[str]:
    text = instructions.lower()
    operations: list[str] = []
    keywords = {
        "format": "formatting",
        "brand": "brand_formatting",
        "template": "template_application",
        "merge": "merge",
        "combine": "merge",
        "redact": "redaction",
        "convert": "conversion",
        "pdf": "pdf_output",
        "ocr": "ocr",
        "scan": "ocr",
        "compare": "document_compare",
        "proof": "proofreading",
        "repair": "file_repair",
        "corrupt": "file_repair",
        "powerpoint": "presentation",
        "slide": "presentation",
    }
    for keyword, operation in keywords.items():
        if keyword in text and operation not in operations:
            operations.append(operation)

    extensions = {Path(file_name).suffix.lower() for file_name in files}
    if ".pdf" in extensions and "pdf_handling" not in operations:
        operations.append("pdf_handling")
    if extensions.intersection({".png", ".jpg", ".jpeg", ".tiff"}) and "ocr" not in operations:
        operations.append("ocr")
    if not operations:
        operations.append("general_document_production")
    return operations


def estimate_effort_hours(operations: list[str], file_count: int, priority: str) -> float:
    base = 0.75 + (file_count * 0.2)
    weights = {
        "redaction": 1.5,
        "ocr": 1.0,
        "merge": 0.6,
        "document_compare": 0.8,
        "presentation": 1.0,
        "file_repair": 0.7,
        "proofreading": 0.5,
    }
    effort = base + sum(weights.get(operation, 0.3) for operation in operations)
    if priority in {"urgent", "critical"}:
        effort *= 1.15
    return round(min(max(effort, 0.5), 12.0), 2)


def release_checklist(operations: list[str]) -> list[str]:
    checklist = [
        "Confirm instructions, client, matter, and deadline match request.",
        "Run spelling, numbering, cross-reference, and layout checks.",
        "Confirm document properties and file name follow matter convention.",
        "Confirm confidentiality footer/disclaimer is present where required.",
    ]
    if "redaction" in operations:
        checklist.append("Human review required for redaction accuracy before release.")
    if "pdf_output" in operations or "pdf_handling" in operations:
        checklist.append("Validate PDF bookmarks, page order, searchable text, and security settings.")
    if "presentation" in operations:
        checklist.append("Check slide master, logo use, fonts, and speaker notes.")
    return checklist

