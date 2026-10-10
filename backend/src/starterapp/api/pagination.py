"""Offset pagination: query parsing, the list envelope, and a SQLAlchemy helper.

Every paginated endpoint returns the same envelope::

    {"items": [...], "page": 2, "per_page": 20, "total": 95, "total_pages": 5}

and reads ``?page=`` (1-based) and ``?per_page=`` (default 20, at most 100)
through the `PageParams` dependency. Bad values are rejected with the standard
422 ``validation_error`` envelope, never silently clamped.

    @router.get("/things", response_model=Page[ThingOut])
    def list_things(params: PageParams = Depends(), db: Session = Depends(get_db)):
        stmt = select(Thing).order_by(Thing.created_at.desc(), Thing.id)
        return paginate(db, stmt, params, ThingOut.model_validate)

Always order by something unique (end with the primary key): without a total
order, rows can repeat or vanish between pages.
"""

from collections.abc import Callable
from typing import Annotated, Any

from fastapi import Query
from pydantic import BaseModel
from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

DEFAULT_PER_PAGE = 20
MAX_PER_PAGE = 100


class PageParams:
    """FastAPI dependency: `params: PageParams = Depends()`."""

    def __init__(
        self,
        page: Annotated[int, Query(ge=1, le=1_000_000)] = 1,
        per_page: Annotated[int, Query(ge=1, le=MAX_PER_PAGE)] = DEFAULT_PER_PAGE,
    ) -> None:
        self.page = page
        self.per_page = per_page

    @property
    def limit(self) -> int:
        return self.per_page

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.per_page


class Page[T](BaseModel):
    items: list[T]
    page: int
    per_page: int
    total: int
    total_pages: int


def total_pages(total: int, per_page: int) -> int:
    return (total + per_page - 1) // per_page if total > 0 else 0


def build_page[T](items: list[T], params: PageParams, total: int) -> Page[T]:
    return Page[T](
        items=items,
        page=params.page,
        per_page=params.per_page,
        total=total,
        total_pages=total_pages(total, params.per_page),
    )


def paginate[T](
    db: Session,
    stmt: Select[Any],
    params: PageParams,
    convert: Callable[[Any], T],
) -> Page[T]:
    """Runs `stmt` (an ORM entity select, already ordered) one page at a time.

    `convert` maps each ORM row to the item type, for example
    ``ThingOut.model_validate`` with ``from_attributes=True``.
    """
    count_stmt = select(func.count()).select_from(stmt.order_by(None).subquery())
    total = db.execute(count_stmt).scalar_one()
    rows = db.execute(stmt.limit(params.limit).offset(params.offset)).scalars().all()
    return build_page([convert(row) for row in rows], params, total)
