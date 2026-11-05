import os
import sys
from pathlib import Path

# Make `app` importable when pytest is run from the backend directory.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# Deterministic test configuration; no external service is contacted by the
# test suite and no real credentials are required.
os.environ.setdefault("ENVIRONMENT", "testing")
os.environ.setdefault("JWT_SECRET_KEY", "test-only-secret-" + "x" * 32)
os.environ.setdefault("ENABLE_DEBUG_ENDPOINTS", "false")
