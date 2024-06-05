"""QA Settings."""

import os
from pathlib import Path


THIS_FILE = Path(__file__).resolve()
PROJECT_ROOT = THIS_FILE.parent.parent.parent.parent

os.environ.setdefault(
    "DATABASE_URL", "postgres://user:password@localhost/db?sslmode=disabled"
)
os.environ.setdefault("DATA_DIR", str(PROJECT_ROOT / ".data"))
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
os.environ.setdefault("SECRET_KEY", "test" * 10)
os.environ.setdefault("ADMIN_NAME", "admin")
os.environ.setdefault("ADMIN_EMAIL", "admin@local.lan")
os.environ.setdefault("EMAIL_HOST", "mailpit")
os.environ.setdefault("EMAIL_PORT", "1025")
os.environ.setdefault("EMAIL_FROM_ADDRESS", "noreply@domain.tld")


from .test import *  # noqa: F403, E402
