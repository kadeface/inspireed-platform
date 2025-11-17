#!/usr/bin/env python
"""使用原始 SQL 检查 Cell 的 order 和 ID 对应关系"""
import asyncio
from sqlalchemy import text
from app.core.database import engine
from app.core.config import settings

async def check_cell_orders_raw():
    """使用原始 SQL 检查 Cell 的 order 值"""
    async with engine.connect() as conn:
        lesson_id = 36
        
        # 查询所有 Cell
        result = await conn.execute(
            text("""
                SELECT id, "order", cell_type, title 
                FROM cells 
                WHERE lesson_id = :lesson_id 
                ORDER BY "order"
            """),
            {"lesson_id": lesson_id}
        )
        cells = result.fetchall()
        
        print(f"📋 Lesson {lesson_id} 的 Cell 列表（按 order 排序）:")
        print(f"{'ID':<6} {'Order':<6} {'Type':<15} {'Title':<30}")
        print("-" * 70)
        for cell in cells:
            print(f"{cell[0]:<6} {cell[1]:<6} {str(cell[2]):<15} {str(cell[3] or '')[:30]:<30}")
        
        # 检查是否有重复的 order
        order_counts = {}
        for cell in cells:
            order = cell[1]
            if order not in order_counts:
                order_counts[order] = []
            order_counts[order].append(cell[0])
        
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
        
        # 检查 order=0 的 Cell
        result = await conn.execute(
            text("""
                SELECT id, "order", cell_type, title 
                FROM cells 
                WHERE lesson_id = :lesson_id AND "order" = 0
            """),
            {"lesson_id": lesson_id}
        )
        order_0_cells = result.fetchall()
        
        print(f"\n🔍 Order=0 的 Cell:")
        if order_0_cells:
            for cell in order_0_cells:
                print(f"  ID: {cell[0]}, Type: {cell[2]}, Title: {cell[3]}")
        else:
            print("  ⚠️  没有找到 order=0 的 Cell")

if __name__ == "__main__":
    asyncio.run(check_cell_orders_raw())

