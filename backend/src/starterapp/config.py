"""Application configuration, sourced from environment variables (and `.env`)."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # `database_url` is the application's runtime role. `database_admin_url`
    # is the migration/owner role Alembic runs as; when unset, migrations
    # fall back to `database_url` (a local-dev convenience only).
    database_url: str = "postgresql+psycopg://starterapp:starterapp@localhost:5433/starterapp"
    database_admin_url: str | None = None

    redis_url: str = "redis://localhost:6380/0"

    # Session tokens are HS256 JWTs this process both issues and verifies.
    # The default is a labelled dev-only placeholder: every real deployment
    # MUST override JWT_SECRET_KEY with a long random value, because a token
    # signed with the default is forgeable by anyone who can read this file.
    jwt_secret_key: str = "starterapp-dev-only-jwt-secret-DO-NOT-USE-IN-PRODUCTION"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60 * 24

    # Login attempts per username per 5-minute window before a 429.
    login_rate_limit_per_5_minutes: int = 10
    # Registration attempts across the whole instance per 5-minute window.
    # Global rather than per-username: the identity being limited does not
    # exist yet, so a per-username key would be trivially evaded.
    register_rate_limit_per_5_minutes: int = 20

    log_level: str = "INFO"


@lru_cache
def get_settings() -> Settings:
    return Settings()
