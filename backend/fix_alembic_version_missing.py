#!/usr/bin/env python3
"""修复 Alembic 版本记录 - 解决找不到修订版本的问题

当数据库中的 alembic_version 表记录了一个不存在的迁移版本时，使用此脚本修复。
脚本会：
1. 检查当前数据库版本
2. 找到实际存在的 head 版本
3. 将数据库版本更新为正确的版本
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import text
from app.core.database import engine
from alembic import config, script


async def get_current_db_version():
    """获取数据库中当前记录的版本"""
    try:
        async with engine.begin() as conn:
            # 检查 alembic_version 表是否存在
            result = await conn.execute(
                text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'alembic_version')")
            )
            table_exists = result.scalar()
            
            if not table_exists:
                print("⚠️  alembic_version 表不存在，可能是新数据库")
                return None
            
            # 获取当前版本
            result = await conn.execute(text("SELECT version_num FROM alembic_version"))
            current_version = result.scalar_one_or_none()
            return current_version
    except Exception as e:
        print(f"❌ 获取数据库版本失败: {e}")
        return None


def get_head_revision():
    """获取当前 head 版本（最新的迁移）"""
    try:
        cfg = config.Config('alembic.ini')
        script_dir = script.ScriptDirectory.from_config(cfg)
        
        # 获取所有 head 版本（可能有多个分支）
        heads = script_dir.get_revisions('heads')
        head_revisions = [h.revision for h in heads]
        
        if len(head_revisions) == 1:
            return head_revisions[0]
        elif len(head_revisions) > 1:
            print(f"⚠️  发现多个 head 版本: {head_revisions}")
            print(f"   使用第一个: {head_revisions[0]}")
            return head_revisions[0]
        else:
            print("❌ 未找到任何 head 版本")
            return None
    except Exception as e:
        print(f"❌ 获取 head 版本失败: {e}")
        return None


async def fix_version(target_version: str):
    """将数据库版本更新为目标版本"""
    try:
        async with engine.begin() as conn:
            # 检查 alembic_version 表是否存在
            result = await conn.execute(
                text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'alembic_version')")
            )
            table_exists = result.scalar()
            
            if not table_exists:
                print("⚠️  alembic_version 表不存在，创建表...")
                await conn.execute(text("CREATE TABLE alembic_version (version_num VARCHAR(32) NOT NULL, CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num))"))
            
            # 检查表中是否有记录
            result = await conn.execute(text("SELECT COUNT(*) FROM alembic_version"))
            count = result.scalar()
            
            if count == 0:
                print(f"✅ 插入新版本记录: {target_version}")
                await conn.execute(
                    text("INSERT INTO alembic_version (version_num) VALUES (:version)"),
                    {"version": target_version}
                )
            else:
                # 获取当前版本
                result = await conn.execute(text("SELECT version_num FROM alembic_version"))
                current_version = result.scalar_one()
                
                print(f"📊 当前数据库版本: {current_version}")
                print(f"📊 目标版本: {target_version}")
                
                if current_version == target_version:
                    print(f"✅ 版本已经是正确的: {target_version}")
                    return True
                
                # 更新版本
                print(f"🔄 更新版本: {current_version} -> {target_version}")
                await conn.execute(
                    text("UPDATE alembic_version SET version_num = :version"),
                    {"version": target_version}
                )
            
            # 验证更新
            result = await conn.execute(text("SELECT version_num FROM alembic_version"))
            new_version = result.scalar_one()
            
            if new_version == target_version:
                print(f"✅ 版本修复成功！当前版本: {new_version}")
                return True
            else:
                print(f"❌ 版本更新失败，当前版本: {new_version}")
                return False
    except Exception as e:
        print(f"❌ 修复版本失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    print("🔍 检查 Alembic 版本记录...")
    print("=" * 60)
    
    # 获取数据库当前版本
    current_version = await get_current_db_version()
    if current_version is None:
        print("⚠️  无法获取数据库版本，可能是新数据库")
    else:
        print(f"📊 数据库当前版本: {current_version}")
    
    # 获取 head 版本
    print("\n🔍 查找 head 版本...")
    head_version = get_head_revision()
    
    if head_version is None:
        print("❌ 无法找到 head 版本，请检查迁移文件")
        return
    
    print(f"📊 Head 版本: {head_version}")
    
    # 检查版本是否存在
    cfg = config.Config('alembic.ini')
    script_dir = script.ScriptDirectory.from_config(cfg)
    
    if current_version:
        try:
            revision_obj = script_dir.get_revision(current_version)
            print(f"✅ 当前版本 {current_version} 在迁移文件中存在")
            if current_version == head_version:
                print("✅ 版本已经是最新的，无需修复")
                return
        except Exception as e:
            print(f"❌ 当前版本 {current_version} 在迁移文件中不存在: {e}")
            print("   这就是导致错误的原因！")
    
    print("\n" + "=" * 60)
    print("🔄 开始修复版本...")
    print("=" * 60)
    
    # 询问确认
    if current_version:
        print(f"\n⚠️  警告：")
        print(f"   当前数据库版本: {current_version} (不存在)")
        print(f"   将更新为: {head_version} (最新的 head 版本)")
        print(f"\n   这会将数据库版本标记为最新的迁移版本。")
        print(f"   如果数据库实际上还没有执行到这个版本，")
        print(f"   请先运行 'alembic upgrade head' 来执行迁移。")
    
    # 执行修复
    success = await fix_version(head_version)
    
    if success:
        print("\n" + "=" * 60)
        print("✅ 修复完成！")
        print("=" * 60)
        print("\n💡 下一步：")
        print("   运行 'alembic upgrade head' 确保所有迁移都已执行")
    else:
        print("\n" + "=" * 60)
        print("❌ 修复失败")
        print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())

