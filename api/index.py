import os
import sys

# Ensure the nested project directory is on PYTHONPATH so `app` package can be imported
CURRENT_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
PY_APP_DIR = os.path.join(PROJECT_ROOT, "pdf2text-api-py")
if PY_APP_DIR not in sys.path:
    sys.path.insert(0, PY_APP_DIR)

# Import FastAPI app
from app.main import app  # noqa: F401 - Vercel detects the ASGI app via `app` symbol
