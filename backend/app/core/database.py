"""
数据库连接管理
"""

import logging
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import text

from app.core.config import settings

logger = logging.getLogger(__name__)

engine = create_async_engine(
    str(settings.DATABASE_URI),
    echo=False,
    future=True,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    pool_recycle=3600,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
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

    在生产环境中应使用 Alembic 迁移管理表结构 (alembic upgrade head)。
    create_all 仅在开发/测试环境中使用，用于快速创建缺失的表。
    """
    if settings.ENVIRONMENT == "production":
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("Database connection verified (production mode — skipping create_all)")
    else:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables ensured via create_all (dev/test mode)")


async def close_db() -> None:
    """关闭数据库连接"""
    await engine.dispose()
