#!/usr/bin/env python
"""检查数据库中的 celltype 枚举值"""
import asyncio
from sqlalchemy import text
from app.core.database import engine
from app.core.config import settings

async def check_enum():
    """检查 celltype 枚举值"""
    print(f"🔍 连接数据库: {settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}")
    
    async with engine.connect() as conn:
        # 检查枚举值
        result = await conn.execute(
            text("SELECT unnest(enum_range(NULL::celltype))::text AS value ORDER BY value")
        )
        values = [row[0] for row in result]
        
        print('\n📋 CellType枚举值:')
        for value in values:
            marker = '✅' if value in ['activity', 'flowchart'] else '  '
            print(f'{marker}  - {value}')
        
        # 检查是否包含 activity 和 flowchart
        has_activity = 'activity' in values
        has_flowchart = 'flowchart' in values
        
        print(f'\n📊 检查结果:')
        print(f'  activity: {"✅ 存在" if has_activity else "❌ 缺失"}')
        print(f'  flowchart: {"✅ 存在" if has_flowchart else "❌ 缺失"}')
        
        if not has_activity or not has_flowchart:
            print('\n⚠️  枚举值缺失，需要执行迁移修复！')
            print('   运行: alembic upgrade head')
        else:
            print('\n✅ 所有枚举值都存在！')
        
        return has_activity and has_flowchart

if __name__ == "__main__":
    asyncio.run(check_enum())
