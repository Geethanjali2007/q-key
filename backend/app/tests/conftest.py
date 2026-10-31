import os
import sys
import tempfile

# Ensure the backend root (containing the "app" package) is importable when
# pytest is run from the backend/ directory.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

# Point the app at an isolated, temporary SQLite database for the test run so
# tests never touch a developer's real qkey.db.
_tmp_db_fd, _tmp_db_path = tempfile.mkstemp(suffix=".db")
os.environ["DATABASE_URL"] = f"sqlite:///{_tmp_db_path}"
os.environ["DEMO_MODE"] = "true"
os.environ["ALLOW_CSPRNG_FALLBACK"] = "true"
