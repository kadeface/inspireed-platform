"""Alembic环境配置"""

from logging.config import fileConfig
import asyncio
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import AsyncConnection, async_engine_from_config

from alembic import context

from app.core.config import settings
from app.core.database import Base
from app.models import *  # noqa: Import all models

# this is the Alembic Config object
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 设置数据库URL
config.set_main_option("sqlalchemy.url", str(settings.DATABASE_URI))

# add your model's MetaData object here
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run migrations in 'online' mode with async engine."""
    # 确保使用 settings.DATABASE_URI，而不是 alembic.ini 中的配置
    # 这样可以正确使用 Docker 环境变量（如 POSTGRES_SERVER=postgres）
    database_url = str(settings.DATABASE_URI)
    print(f"🔗 Using database URL: {database_url.split('@')[1] if '@' in database_url else '***'}")
    
    # 创建配置字典，确保使用正确的数据库 URL
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = database_url
    
    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        # connection 是 AsyncConnection 类型，具有 run_sync 方法
        connection_typed: AsyncConnection = connection
        await connection_typed.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
