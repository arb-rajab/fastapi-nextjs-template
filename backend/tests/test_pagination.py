"""Pagination helper: query validation, the envelope, and the SQL helper."""

from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from starterapp.api.deps import get_db
from starterapp.api.pagination import (
    MAX_PER_PAGE,
    Page,
    PageParams,
    build_page,
    paginate,
    total_pages,
)
from starterapp.db import models
from starterapp.main import app as main_app


class UserOut(BaseModel):
    username: str


def _seed_users(db: Session, count: int) -> None:
    for i in range(count):
        db.add(models.AppUser(username=f"user{i:02d}", password_hash="x"))
    db.commit()


def _list_app() -> FastAPI:
    # A throwaway app, so the test does not depend on any domain router.
    app = FastAPI()
    # Reuse the real error handlers so the 422 shape is the production one.
    app.exception_handlers.update(main_app.exception_handlers)

    @app.get("/users", response_model=Page[UserOut])
    def list_users(params: PageParams = Depends(), db: Session = Depends(get_db)) -> Page[UserOut]:
        stmt = select(models.AppUser).order_by(models.AppUser.username)
        return paginate(db, stmt, params, lambda u: UserOut(username=u.username))

    return app


def test_total_pages_rounds_up() -> None:
    assert total_pages(0, 20) == 0
    assert total_pages(1, 20) == 1
    assert total_pages(20, 20) == 1
    assert total_pages(21, 20) == 2


def test_page_params_offset_and_limit() -> None:
    params = PageParams(page=3, per_page=10)

    assert params.offset == 20
    assert params.limit == 10


def test_build_page_envelope() -> None:
    page = build_page(["a", "b"], PageParams(page=2, per_page=2), total=5)

    assert page.model_dump() == {
        "items": ["a", "b"],
        "page": 2,
        "per_page": 2,
        "total": 5,
        "total_pages": 3,
    }


def test_defaults_to_first_page_of_twenty(db: Session) -> None:
    _seed_users(db, 25)

    body = TestClient(_list_app()).get("/users").json()

    assert body["page"] == 1
    assert body["per_page"] == 20
    assert body["total"] == 25
    assert body["total_pages"] == 2
    assert len(body["items"]) == 20
    assert body["items"][0] == {"username": "user00"}


def test_second_page_returns_the_remainder(db: Session) -> None:
    _seed_users(db, 25)

    body = TestClient(_list_app()).get("/users", params={"page": 2}).json()

    assert [i["username"] for i in body["items"]] == [f"user{n:02d}" for n in range(20, 25)]


def test_page_past_the_end_is_empty_not_an_error(db: Session) -> None:
    _seed_users(db, 3)

    response = TestClient(_list_app()).get("/users", params={"page": 9})

    assert response.status_code == 200
    assert response.json()["items"] == []
    assert response.json()["total"] == 3


def test_empty_table_has_zero_pages(db: Session) -> None:
    body = TestClient(_list_app()).get("/users").json()

    assert body["items"] == []
    assert body["total_pages"] == 0


def test_pages_do_not_overlap(db: Session) -> None:
    _seed_users(db, 7)
    client = TestClient(_list_app())

    seen: list[str] = []
    for page in (1, 2, 3):
        body = client.get("/users", params={"page": page, "per_page": 3}).json()
        seen.extend(i["username"] for i in body["items"])

    assert seen == [f"user{n:02d}" for n in range(7)]


def test_invalid_values_use_the_validation_envelope() -> None:
    client = TestClient(_list_app())

    for params, field in (
        ({"page": 0}, "page"),
        ({"page": "abc"}, "page"),
        ({"per_page": 0}, "per_page"),
        ({"per_page": MAX_PER_PAGE + 1}, "per_page"),
    ):
        response = client.get("/users", params=params)

        assert response.status_code == 422, params
        error = response.json()["error"]
        assert error["code"] == "validation_error"
        assert error["field"] == field
        assert field in error["fields"]
