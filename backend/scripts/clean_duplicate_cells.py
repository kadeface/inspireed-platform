"""
清理数据库中的重复 Cell 记录

这个脚本会查找并删除重复的 Cell 记录（相同的 lesson_id、order、cell_type）
只保留最新的一条记录
"""

import asyncio
from sqlalchemy import select, and_, func, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import AsyncSessionLocal
from app.models.cell import Cell
from typing import List, Tuple


async def clean_duplicate_cells():
    """清理重复的 Cell 记录"""
    async with AsyncSessionLocal() as db:
        try:
            # 查找重复的 Cell（相同的 lesson_id、order、cell_type）
            # 使用 GROUP BY 和 HAVING 找出重复的组合
            duplicate_query = (
                select(
                    Cell.lesson_id,
                    Cell.order,
                    Cell.cell_type,
                    func.count(Cell.id).label('count')
                )
                .group_by(Cell.lesson_id, Cell.order, Cell.cell_type)
                .having(func.count(Cell.id) > 1)
            )
            
            result = await db.execute(duplicate_query)
            duplicates = result.all()
            
            if not duplicates:
                print("✅ 没有发现重复的 Cell 记录")
                return
            
            print(f"🔍 发现 {len(duplicates)} 组重复的 Cell 记录")
            
            total_deleted = 0
            
            # 对每组重复记录，保留最新的，删除其他的
            for lesson_id, order, cell_type, count in duplicates:
                print(f"\n📦 处理重复组: lesson_id={lesson_id}, order={order}, cell_type={cell_type}, count={count}")
                
                # 查找该组的所有记录，按 ID 降序排序
                cells_query = (
                    select(Cell)
                    .where(
                        and_(
                            Cell.lesson_id == lesson_id,
                            Cell.order == order,
                            Cell.cell_type == cell_type,
                        )
                    )
                    .order_by(Cell.id.desc())
                )
                
                cells_result = await db.execute(cells_query)
                cells = cells_result.scalars().all()
                
                # 保留第一条（最新的），删除其他的
                keep_cell = cells[0]
                delete_cells = cells[1:]
                
                print(f"  ✅ 保留 Cell ID: {keep_cell.id} (最新)")
                
                for cell in delete_cells:
                    print(f"  ❌ 删除 Cell ID: {cell.id}")
                    await db.delete(cell)
                    total_deleted += 1
            
            # 提交更改
            await db.commit()
            
            print(f"\n✅ 清理完成！共删除 {total_deleted} 条重复记录")
            
        except Exception as e:
            print(f"❌ 清理失败: {e}")
            import traceback
            traceback.print_exc()
            await db.rollback()


async def verify_no_duplicates():
    """验证没有重复记录"""
    async with AsyncSessionLocal() as db:
        duplicate_query = (
            select(
                Cell.lesson_id,
                Cell.order,
                Cell.cell_type,
                func.count(Cell.id).label('count')
            )
            .group_by(Cell.lesson_id, Cell.order, Cell.cell_type)
            .having(func.count(Cell.id) > 1)
        )
        
        result = await db.execute(duplicate_query)
        duplicates = result.all()
        
        if duplicates:
            print(f"⚠️ 仍然存在 {len(duplicates)} 组重复记录")
            return False
        else:
            print("✅ 验证通过：没有重复记录")
            return True


async def main():
    print("🧹 开始清理重复的 Cell 记录...")
    await clean_duplicate_cells()
    
    print("\n🔍 验证清理结果...")
    await verify_no_duplicates()


if __name__ == "__main__":
    asyncio.run(main())

