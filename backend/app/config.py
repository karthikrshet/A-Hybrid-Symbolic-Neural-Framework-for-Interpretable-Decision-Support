"""Application settings."""

from __future__ import annotations

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent  # backend/
DATASET_DIR = BASE_DIR / "datasets"
RESULTS_DIR = BASE_DIR / "experiments" / "results"
DB_PATH = Path(os.getenv("NS_DB_PATH", str(BASE_DIR / "data" / "neurosymbolic.db")))

DATASET_SIZE = 5000
RANDOM_SEED = 42

PROJECT_NAME = "NeuroSymbolic AI - Hybrid Symbolic-Neural Decision Support"
VERSION = "2.0.0"

CORS_ORIGIN_REGEX = r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$"
