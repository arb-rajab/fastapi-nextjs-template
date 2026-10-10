#!/bin/sh
# Production entrypoint: migrate as the admin role, then serve with gunicorn
# managing uvicorn workers. WEB_CONCURRENCY is a starting point, not a
# load-tested number.
#
# gunicorn's access log is left off on purpose: per-request logging is
# already emitted as JSON by the `log_requests` middleware in
# starterapp.main, and enabling both would duplicate every request.
set -eu

alembic upgrade head

exec gunicorn starterapp.main:app \
    --worker-class uvicorn.workers.UvicornWorker \
    --workers "${WEB_CONCURRENCY:-4}" \
    --bind 0.0.0.0:8000 \
    --timeout "${GUNICORN_TIMEOUT:-60}" \
    --graceful-timeout 30 \
    --error-logfile - \
    --log-level "${LOG_LEVEL:-info}"
