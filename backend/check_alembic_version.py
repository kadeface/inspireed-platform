#!/usr/bin/env python3
"""检查 Alembic 版本问题的诊断脚本"""

import asyncio
from sqlalchemy import text
from app.core.database import engine

async def check_version():
    """检查数据库中的版本记录"""
    async with engine.connect() as conn:
        # 检查 alembic_version 表
        try:
            result = await conn.execute(text("SELECT version_num FROM alembic_version"))
            version = result.scalar_one_or_none()
            print(f"数据库中的当前版本: {version}")
        except Exception as e:
            print(f"查询版本时出错: {e}")
            # 检查表是否存在
            try:
                result = await conn.execute(text("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'alembic_version'
                    )
                """))
                exists = result.scalar_one()
                print(f"alembic_version 表是否存在: {exists}")
            except Exception as e2:
                print(f"检查表是否存在时出错: {e2}")

if __name__ == "__main__":
    asyncio.run(check_version())

