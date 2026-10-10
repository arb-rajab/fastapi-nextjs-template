"""Helpers for the API error contract: {"error": {"code", "message", "field"}}.

Route handlers raise `HTTPException(detail={"code", "message", "field"})`;
the exception handlers in `starterapp.main` wrap that detail in an `error`
envelope, so clients see one shape for every failure.
"""

from fastapi import HTTPException


def api_error(
    status_code: int,
    code: str,
    message: str,
    field: str | None = None,
    headers: dict[str, str] | None = None,
) -> HTTPException:
    return HTTPException(
        status_code=status_code,
        detail={"code": code, "message": message, "field": field},
        headers=headers,
    )


def not_found(message: str) -> HTTPException:
    return api_error(404, "not_found", message)


def forbidden(message: str) -> HTTPException:
    return api_error(403, "forbidden", message)


def conflict(code: str, message: str, field: str | None = None) -> HTTPException:
    return api_error(409, code, message, field)
