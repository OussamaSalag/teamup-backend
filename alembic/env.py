from __future__ import annotations

import asyncio
import logging
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# ---------------------------------------------------------------------------
# Alembic Config object
# ---------------------------------------------------------------------------
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

logger = logging.getLogger("alembic.env")

# ---------------------------------------------------------------------------
# Project imports — settings & metadata
# ---------------------------------------------------------------------------
from app.core.config import settings  # noqa: E402
from app.db.session import Base  # noqa: E402

# Import ALL models so SQLAlchemy metadata is fully populated for autogenerate
from app.models.user import User, UserRole, Skill, ProfileSkill, UserPreference  # noqa: E402, F401
from app.models.project import Project, ProjectMember, ProjectSkill, ProjectJoinRequest  # noqa: E402, F401
from app.models.task import Task  # noqa: E402, F401
from app.models.message import Conversation, ConversationParticipant, Message  # noqa: E402, F401
from app.models.notification import Notification  # noqa: E402, F401
from app.models.mentor import MentorFeedback  # noqa: E402, F401

# Point alembic at our metadata and database URL
target_metadata = Base.metadata
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)


# ---------------------------------------------------------------------------
# Offline migrations
# ---------------------------------------------------------------------------
def run_migrations_offline() -> None:
    """Run migrations without a live DB connection (generates SQL script)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


# ---------------------------------------------------------------------------
# Online migrations (async)
# ---------------------------------------------------------------------------
def do_run_migrations(connection) -> None:  # type: ignore[type-arg]
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Create an async engine and run migrations through a sync connection."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
