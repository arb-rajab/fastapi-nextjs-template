FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml ./
COPY src ./src
COPY alembic ./alembic
COPY alembic.ini ./

RUN pip install --no-cache-dir .

EXPOSE 8000

# Migrations run as the admin role (DATABASE_ADMIN_URL); the app then serves
# as the restricted role (DATABASE_URL).
CMD ["sh", "-c", "alembic upgrade head && uvicorn starterapp.main:app --host 0.0.0.0 --port 8000"]
