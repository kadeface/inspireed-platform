#!/usr/bin/env python3
"""修复 Alembic 版本记录 - 将不存在的版本更新为当前 head"""

import asyncio
from sqlalchemy import text
from app.core.database import engine

async def fix_version():
    """将数据库版本更新为当前 head: 20250122_add_student_projects"""
    async with engine.begin() as conn:
        # 检查当前版本
        result = await conn.execute(text("SELECT version_num FROM alembic_version"))
        current_version = result.scalar_one_or_none()
        print(f"当前数据库版本: {current_version}")
        
        # 目标版本（当前实际存在的 head）
        target_version = "20250122_add_student_projects"
        
        if current_version == target_version:
            print(f"版本已经是正确的: {target_version}")
            return
        
        # 更新版本
        print(f"更新版本: {current_version} -> {target_version}")
        await conn.execute(
            text("UPDATE alembic_version SET version_num = :version"),
            {"version": target_version}
        )
        
        # 验证更新
        result = await conn.execute(text("SELECT version_num FROM alembic_version"))
        new_version = result.scalar_one()
        print(f"更新后的版本: {new_version}")
        
        if new_version == target_version:
            print("✅ 版本修复成功！")
        else:
            print("❌ 版本更新失败")

if __name__ == "__main__":
    asyncio.run(fix_version())

