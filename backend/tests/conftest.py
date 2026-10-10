"""Test configuration.

Tests run against a REAL Postgres and Redis (docker-compose's `postgres` and
`redis` services; defaults match docker-compose.yml and .env.example, using
the host ports compose publishes). No grant or auth test is honest against a
mock.
"""

import os
from pathlib import Path

os.environ.setdefault(
    "DATABASE_ADMIN_URL", "postgresql+psycopg://starterapp:starterapp@localhost:5433/starterapp"
)
os.environ.setdefault("APP_DB_ROLE", "starterapp_app")
os.environ.setdefault("APP_DB_PASSWORD", "starterapp_app_dev_only")
os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+psycopg://starterapp_app:starterapp_app_dev_only@localhost:5433/starterapp",
)
os.environ.setdefault("REDIS_URL", "redis://localhost:6380/0")

import pytest  # noqa: E402
import redis  # noqa: E402
from alembic import command  # noqa: E402
from alembic.config import Config  # noqa: E402
from sqlalchemy import create_engine, text  # noqa: E402
from sqlalchemy.orm import Session  # noqa: E402

BACKEND_ROOT = Path(__file__).resolve().parent.parent

# Every table a test may write to; truncated after each test. Add new tables.
ALL_TABLES = ("app_user",)


@pytest.fixture(scope="session", autouse=True)
def _migrated_schema() -> None:
    cfg = Config(str(BACKEND_ROOT / "alembic.ini"))
    command.upgrade(cfg, "head")


@pytest.fixture(scope="session")
def admin_engine():  # type: ignore[no-untyped-def]
    return create_engine(os.environ["DATABASE_ADMIN_URL"])


@pytest.fixture(autouse=True)
def _clean_tables(admin_engine, _migrated_schema):  # type: ignore[no-untyped-def]
    # Cleanup uses the admin role: the application role may be denied
    # TRUNCATE/DELETE on some tables by design.
    yield
    with admin_engine.begin() as conn:
        conn.execute(text(f"TRUNCATE {', '.join(ALL_TABLES)} RESTART IDENTITY CASCADE"))
    # Rate-limit counters are keyed by reused literal usernames across tests,
    # so flush Redis between tests rather than relying on key TTLs.
    redis.Redis.from_url(os.environ["REDIS_URL"]).flushdb()


@pytest.fixture()
def db() -> Session:  # type: ignore[misc]
    from starterapp.db.session import SessionLocal

    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
