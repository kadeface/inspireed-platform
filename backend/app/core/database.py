"""
数据库连接管理
"""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

from app.core.config import settings

# 创建异步引擎
engine = create_async_engine(
    str(settings.DATABASE_URI),
    echo=False,
    future=True,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

# 创建会话工厂
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# 声明基类
Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    获取数据库会话的依赖注入函数
    """
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
    初始化数据库（创建所有表）
    增加重试机制，防止数据库连接失败导致应用无法启动
    """
    import asyncio
    max_retries = 5
    retry_delay = 5
    
    for attempt in range(max_retries):
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            print(f"✅ Database initialized successfully")
            return
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"⚠️ Database initialization failed (attempt {attempt + 1}/{max_retries}): {e}")
                print(f"⏳ Retrying in {retry_delay} seconds...")
                await asyncio.sleep(retry_delay)
            else:
                print(f"❌ Database initialization failed after {max_retries} attempts: {e}")
                raise


async def close_db() -> None:
    """
    关闭数据库连接
    """
    await engine.dispose()
