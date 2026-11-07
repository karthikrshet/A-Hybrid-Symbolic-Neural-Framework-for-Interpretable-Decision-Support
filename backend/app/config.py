"""Application settings."""

from __future__ import annotations

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent  # backend/


def _load_env_file(path: Path) -> None:
    """Load KEY=VALUE lines from backend/.env (real environment variables win)."""
    if not path.is_file():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        value = value.strip().strip('"').strip("'")
        if key.strip() and value:
            os.environ.setdefault(key.strip(), value)


_load_env_file(BASE_DIR / ".env")
DATASET_DIR = BASE_DIR / "datasets"
RESULTS_DIR = BASE_DIR / "experiments" / "results"
_db = Path(os.getenv("NS_DB_PATH", str(BASE_DIR / "data" / "neurosymbolic.db")))
DB_PATH = _db if _db.is_absolute() else BASE_DIR / _db

DATASET_SIZE = 5000
RANDOM_SEED = 42

PROJECT_NAME = "NeuroSymbolic AI - Hybrid Symbolic-Neural Decision Support"
VERSION = "2.0.0"

CORS_ORIGIN_REGEX = r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$"
