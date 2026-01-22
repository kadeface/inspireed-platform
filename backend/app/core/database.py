"""
数据库连接管理
"""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base, Session, sessionmaker
from sqlalchemy import create_engine

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

# 创建会话工厂（异步）
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# 创建同步引擎和会话工厂（用于迁移脚本等）
# 将异步数据库URI转换为同步URI（postgresql+asyncpg:// -> postgresql://）
sync_db_uri = str(settings.DATABASE_URI).replace("+asyncpg", "", 1)
sync_engine = create_engine(
    sync_db_uri,
    echo=False,
    future=True,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

SessionLocal = sessionmaker(
    sync_engine,
    class_=Session,
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
    
    注意：如果使用 Alembic 迁移，应该运行 `alembic upgrade head` 而不是依赖此函数
    此函数主要用于开发环境或没有迁移的情况
    """
    import asyncio
    from sqlalchemy import inspect, text
    
    max_retries = 5
    retry_delay = 5
    
    for attempt in range(max_retries):
        try:
            # 检查是否已有 Alembic 版本表（说明使用了迁移）
            async with engine.begin() as conn:
                # 使用 run_sync 执行同步的检查操作
                def check_alembic_table(sync_conn):
                    from sqlalchemy import inspect
                    inspector = inspect(sync_conn)
                    return inspector.has_table("alembic_version")
                
                has_alembic_version = await conn.run_sync(check_alembic_table)
                
                if has_alembic_version:
                    print("ℹ️ 检测到 Alembic 迁移系统，跳过自动创建表")
                    print("   请运行 'alembic upgrade head' 来应用数据库迁移")
                    return
                
                # 如果没有迁移系统，则自动创建表
                await conn.run_sync(Base.metadata.create_all)
            print(f"✅ Database initialized successfully")
            return
        except Exception as e:
            error_msg = str(e)
            # 如果是表已存在的错误，可以忽略
            if "already exists" in error_msg.lower() or "duplicate" in error_msg.lower():
                print(f"ℹ️ 表已存在，跳过创建: {error_msg[:100]}")
                return
            if attempt < max_retries - 1:
                print(f"⚠️ Database initialization failed (attempt {attempt + 1}/{max_retries}): {e}")
                print(f"⏳ Retrying in {retry_delay} seconds...")
                await asyncio.sleep(retry_delay)
            else:
                print(f"❌ Database initialization failed after {max_retries} attempts: {e}")
                print(f"💡 提示：如果使用 Alembic 迁移，请运行 'alembic upgrade head'")
                raise


async def close_db() -> None:
    """
    关闭数据库连接
    """
    await engine.dispose()
