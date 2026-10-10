from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from starterapp.config import get_settings
from starterapp.db.models import Base

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

# Migrations run as the admin/owner role, never the restricted application
# role. Falls back to database_url only as a single-role local-dev
# convenience; production deployments should set DATABASE_ADMIN_URL.
settings = get_settings()
admin_url = settings.database_admin_url or settings.database_url
config.set_main_option("sqlalchemy.url", admin_url)


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
