import logging
import time
import uuid
from collections.abc import Awaitable, Callable

from fastapi import Depends, FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, Response
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from starlette.exceptions import HTTPException as StarletteHTTPException

from starterapp.api.auth_routes import router as auth_router
from starterapp.api.deps import get_db
from starterapp.logging_config import configure_logging

configure_logging()
logger = logging.getLogger("starterapp.request")

app = FastAPI(title="starterapp", version="0.1.0")

app.include_router(auth_router)
# Register domain routers here.


@app.middleware("http")
async def log_requests(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    request_id = request.headers.get("x-request-id", str(uuid.uuid4()))
    started = time.perf_counter()
    response = await call_next(request)
    duration_ms = round((time.perf_counter() - started) * 1000, 2)
    response.headers["x-request-id"] = request_id
    logger.info(
        "request completed",
        extra={
            "extra_fields": {
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": duration_ms,
            }
        },
    )
    return response


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    # Error contract: {"error": {"code", "message", "field"}}, not FastAPI's
    # default {"detail": ...}. A detail that is not already in that shape
    # (e.g. raised by a library) is wrapped.
    detail = exc.detail
    if isinstance(detail, dict) and "code" in detail:
        error = detail
    else:
        error = {"code": "http_error", "message": str(detail), "field": None}
    # Keep exc.headers (e.g. Retry-After on a 429) on the response.
    return JSONResponse(status_code=exc.status_code, content={"error": error}, headers=exc.headers)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    # `field`/`message` describe the first problem; `fields` lists every
    # problem per field name so a form can show them all at once.
    fields: dict[str, list[str]] = {}
    for item in exc.errors():
        # loc is ("body" | "query" | ..., <name>, ...): drop the source prefix.
        name = ".".join(str(part) for part in item["loc"][1:]) or "request"
        fields.setdefault(name, []).append(str(item["msg"]))
    first_field = next(iter(fields), None)
    message = fields[first_field][0] if first_field else "Invalid request"
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "validation_error",
                "message": message,
                "field": first_field,
                "fields": fields,
            }
        },
    )


@app.get("/health")
def health() -> dict[str, str]:
    # Liveness only: the process is up and can answer.
    return {"status": "ok"}


@app.get("/ready")
def ready(db: Session = Depends(get_db)) -> JSONResponse:
    # Readiness: checks the dependency the app cannot work without (Postgres).
    try:
        db.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        logger.error(
            "readiness check failed: database unreachable",
            extra={"extra_fields": {"error": str(exc)}},
        )
        return JSONResponse(status_code=503, content={"status": "not_ready"})
    return JSONResponse(status_code=200, content={"status": "ready"})
