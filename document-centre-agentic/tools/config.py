from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG_PATH = PROJECT_ROOT / "config" / "defaults.json"
DEFAULT_DB_PATH = PROJECT_ROOT / "data" / "document_centre.sqlite3"


def load_config(path: str | Path | None = None) -> dict[str, Any]:
    config_path = Path(path) if path else DEFAULT_CONFIG_PATH
    with config_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def db_path() -> Path:
    return Path(os.environ.get("DCA_DB_PATH", DEFAULT_DB_PATH))

