"""Grant-assertion tests against the application's real runtime role
(DATABASE_URL): Postgres grants, not application discipline, bound what the
app can do."""

import pytest
from sqlalchemy import text
from sqlalchemy.exc import ProgrammingError

from starterapp.db.session import engine as app_role_engine


def test_app_role_can_read_and_write_app_user() -> None:
    with app_role_engine.begin() as conn:
        conn.execute(
            text(
                "INSERT INTO app_user (id, username, password_hash) "
                "VALUES (gen_random_uuid(), 'grant-check', 'x')"
            )
        )
        count = conn.execute(
            text("SELECT count(*) FROM app_user WHERE username = 'grant-check'")
        ).scalar_one()
        assert count == 1


def test_app_role_cannot_run_ddl() -> None:
    with app_role_engine.connect() as conn:
        with pytest.raises(ProgrammingError, match="permission denied"):
            conn.execute(text("CREATE TABLE should_not_exist (id int)"))
        conn.rollback()
