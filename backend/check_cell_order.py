#!/usr/bin/env python
"""检查数据库中 Cell 的 order 和 ID 对应关系"""
import asyncio
from sqlalchemy import select, text
from app.core.database import AsyncSessionLocal
from app.models import Cell, Lesson

async def check_cell_orders():
    """检查 Cell 的 order 值"""
    async with AsyncSessionLocal() as db:
        # 检查 lesson_id=36 的所有 Cell
        lesson_id = 36
        result = await db.execute(
            select(Cell).where(Cell.lesson_id == lesson_id).order_by(Cell.order)
        )
        cells = result.scalars().all()
        
        print(f"📋 Lesson {lesson_id} 的 Cell 列表（按 order 排序）:")
        print(f"{'ID':<6} {'Order':<6} {'Type':<12} {'Title':<30}")
        print("-" * 60)
        for cell in cells:
            print(f"{cell.id:<6} {cell.order:<6} {str(cell.cell_type):<12} {str(cell.title)[:30]:<30}")
        
        # 检查是否有重复的 order
        order_counts = {}
        for cell in cells:
            order = cell.order
            if order not in order_counts:
                order_counts[order] = []
            order_counts[order].append(cell.id)
        
        print(f"\n📊 Order 值统计:")
        duplicates = False
        for order, cell_ids in sorted(order_counts.items()):
            if len(cell_ids) > 1:
                print(f"  ⚠️  Order {order}: {len(cell_ids)} 个 Cell (ID: {cell_ids})")
                duplicates = True
            else:
                print(f"  ✅ Order {order}: 1 个 Cell (ID: {cell_ids[0]})")
        
        if duplicates:
            print("\n❌ 发现重复的 order 值！这可能导致导航错误。")
        else:
            print("\n✅ 没有重复的 order 值。")
        
        # 检查 lesson.content 中的顺序
        lesson = await db.get(Lesson, lesson_id)
        if lesson and lesson.content:
            print(f"\n📋 Lesson.content 中的 Cell 顺序:")
            lesson_content = lesson.content
            for idx, cell_data in enumerate(lesson_content):
                cell_id = cell_data.get("id")
                cell_order = cell_data.get("order", idx)
                cell_type = cell_data.get("type") or cell_data.get("cell_type")
                cell_title = cell_data.get("title", "")
                print(f"  [{idx}] ID: {cell_id}, Order: {cell_order}, Type: {cell_type}, Title: {cell_title[:30]}")
                
                # 检查数据库中是否有对应的 Cell
                if cell_order is not None:
                    db_result = await db.execute(
                        select(Cell).where(
                            Cell.lesson_id == lesson_id,
                            Cell.order == cell_order
                        )
                    )
                    db_cell = db_result.scalar_one_or_none()
                    if db_cell:
                        print(f"      → 数据库中找到: Cell ID={db_cell.id}, Order={db_cell.order}")
                    else:
                        print(f"      → ⚠️  数据库中未找到 order={cell_order} 的 Cell")

if __name__ == "__main__":
    asyncio.run(check_cell_orders())

