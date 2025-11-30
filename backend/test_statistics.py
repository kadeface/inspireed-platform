"""
测试统计功能的脚本
用于验证统计数据是否正确
"""

import asyncio
import sys
from pathlib import Path

backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.services.realtime import get_submission_statistics


async def test_statistics(cell_id: int = 11, session_id: int = 98):
    """测试统计功能"""
    print("=" * 80)
    print(f"📊 测试统计功能 (Cell ID: {cell_id}, Session ID: {session_id})")
    print("=" * 80)
    
    async with AsyncSessionLocal() as db:
        # 调用统计函数
        stats = await get_submission_statistics(
            db=db,
            cell_id=cell_id,
            lesson_id=76,  # 假设lesson_id是76
            session_id=session_id
        )
        
        print("\n✅ 统计结果:")
        print(f"   总学生数: {stats['total_students']}")
        print(f"   已提交: {stats['submitted_count']}")
        print(f"   草稿中: {stats['draft_count']}")
        print(f"   未开始: {stats['not_started_count']}")
        print(f"   平均分: {stats['average_score']}")
        print(f"   平均用时: {stats['average_time_spent']} 秒")
        
        print("\n" + "=" * 80)
        
        # 验证数据
        print("\n🔍 数据验证:")
        total = stats['submitted_count'] + stats['draft_count'] + stats['not_started_count']
        print(f"   提交数 + 草稿数 + 未开始数 = {total}")
        print(f"   总学生数 = {stats['total_students']}")
        
        if total == stats['total_students']:
            print("   ✅ 数据一致！")
        else:
            print("   ⚠️ 数据不一致！请检查逻辑")


if __name__ == "__main__":
    cell_id = int(sys.argv[1]) if len(sys.argv) > 1 else 11
    session_id = int(sys.argv[2]) if len(sys.argv) > 2 else 98
    
    asyncio.run(test_statistics(cell_id, session_id))

