"""Create the restricted runtime database role

Revision ID: 0002
Revises: 0001

The application connects as this role (DATABASE_URL) with plain CRUD on its
tables and no DDL rights; migrations run as the admin role. When you add a
table, grant it here (or in the migration that creates it). For an
append-only audit table, grant only SELECT and INSERT so Postgres, not
application discipline, prevents UPDATE and DELETE.
"""

import os
import re
from collections.abc import Sequence

from alembic import op

revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

APP_ROLE = os.environ.get("APP_DB_ROLE", "starterapp_app")
APP_PASSWORD = os.environ.get("APP_DB_PASSWORD", "starterapp_app_dev_only")

MUTABLE_TABLES = ("app_user",)

_SAFE_IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def upgrade() -> None:
    if not _SAFE_IDENTIFIER.match(APP_ROLE) or "'" in APP_PASSWORD:
        raise ValueError(
            "APP_DB_ROLE must be a plain identifier and APP_DB_PASSWORD must not contain quotes"
        )
    op.execute(
        f"""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = '{APP_ROLE}') THEN
                CREATE ROLE {APP_ROLE} LOGIN PASSWORD '{APP_PASSWORD}';
            END IF;
        END
        $$;
        """
    )
    op.execute(f"GRANT USAGE ON SCHEMA public TO {APP_ROLE}")
    for table in MUTABLE_TABLES:
        op.execute(f"GRANT SELECT, INSERT, UPDATE, DELETE ON {table} TO {APP_ROLE}")


def downgrade() -> None:
    for table in MUTABLE_TABLES:
        op.execute(f"REVOKE ALL ON {table} FROM {APP_ROLE}")
    op.execute(f"REVOKE USAGE ON SCHEMA public FROM {APP_ROLE}")
