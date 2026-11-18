# ruff: noqa: INP001
"""Write the FastAPI app's OpenAPI schema to frontend/openapi.json.

Used by `npm run gen:api` so the frontend types are generated from the
backend's real schema. No server or database is started.
"""

import json
import os
import sys
from pathlib import Path

# `Settings` is read at import time and requires PostgreSQL credentials;
# throwaway values are enough because nothing connects.
os.environ.setdefault("POSTGRES_USER", "test")
os.environ.setdefault("POSTGRES_PASSWORD", "test")
os.environ.setdefault("POSTGRES_DB", "test")

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from backend.app.main import app  # noqa: E402

OUTPUT = ROOT / "frontend" / "openapi.json"

OUTPUT.write_text(
    json.dumps(app.openapi(), indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
    newline="\n",
)
