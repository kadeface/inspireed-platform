"""
数据库连接管理
"""

import asyncio
import logging
from typing import AsyncGenerator

from sqlalchemy import create_engine, inspect
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base, Session, sessionmaker

from app.core.config import settings

logger = logging.getLogger(__name__)

engine = create_async_engine(
    str(settings.DATABASE_URI),
    echo=False,
    future=True,
    pool_pre_ping=True,
    pool_size=50,
    max_overflow=100,
    pool_recycle=3600,
    pool_timeout=30,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

sync_db_uri = str(settings.DATABASE_URI).replace("+asyncpg", "", 1)
sync_engine = create_engine(
    sync_db_uri,
    echo=False,
    future=True,
    pool_pre_ping=True,
    pool_size=50,
    max_overflow=100,
    pool_recycle=3600,
    pool_timeout=30,
)

SessionLocal = sessionmaker(
    sync_engine,
    class_=Session,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """获取数据库会话的依赖注入函数"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """
    初始化数据库。

    带重试机制，防止数据库连接失败导致应用无法启动。
    如果检测到 Alembic 迁移系统，跳过 create_all。
    """
    max_retries = 5
    retry_delay = 5

    for attempt in range(max_retries):
        try:
            async with engine.begin() as conn:
                def _check_alembic(sync_conn):
                    return inspect(sync_conn).has_table("alembic_version")

                has_alembic = await conn.run_sync(_check_alembic)

                if has_alembic:
                    logger.info("Alembic migration system detected — skipping create_all")
                    return

                await conn.run_sync(Base.metadata.create_all)

            logger.info("Database initialized successfully")
            return
        except Exception as e:
            error_msg = str(e)
            if "already exists" in error_msg.lower() or "duplicate" in error_msg.lower():
                logger.info("Tables already exist, skipping creation")
                return
            if attempt < max_retries - 1:
                logger.warning(
                    "Database init failed (attempt %d/%d): %s — retrying in %ds",
                    attempt + 1, max_retries, e, retry_delay,
                )
                await asyncio.sleep(retry_delay)
            else:
                logger.error("Database init failed after %d attempts", max_retries)
                raise


async def close_db() -> None:
    """关闭数据库连接"""
    await engine.dispose()
