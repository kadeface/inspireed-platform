#!/usr/bin/env python
"""检查 lesson.content 中的 Cell 顺序"""
import asyncio
import json
from sqlalchemy import text
from app.core.database import engine

async def check_lesson_content():
    """检查 lesson.content 中的 Cell 顺序"""
    async with engine.connect() as conn:
        lesson_id = 36
        
        # 查询 lesson.content
        result = await conn.execute(
            text("SELECT content FROM lessons WHERE id = :lesson_id"),
            {"lesson_id": lesson_id}
        )
        row = result.fetchone()
        
        if not row or not row[0]:
            print("❌ Lesson.content 为空")
            return
        
        lesson_content = row[0]
        
        print(f"📋 Lesson {lesson_id} 的 content 中的 Cell 顺序:")
        print(f"{'Index':<8} {'ID (UUID)':<40} {'Order':<8} {'Type':<15} {'Title':<30}")
        print("-" * 110)
        
        for idx, cell_data in enumerate(lesson_content):
            cell_id = cell_data.get("id", "")
            cell_order = cell_data.get("order", idx)
            cell_type = cell_data.get("type") or cell_data.get("cell_type", "")
            cell_title = cell_data.get("title", "")
            
            print(f"{idx:<8} {str(cell_id)[:40]:<40} {cell_order:<8} {str(cell_type):<15} {str(cell_title)[:30]:<30}")
            
            # 检查数据库中是否有对应的 Cell
            if cell_order is not None:
                db_result = await conn.execute(
                    text("""
                        SELECT id, "order", cell_type, title 
                        FROM cells 
                        WHERE lesson_id = :lesson_id AND "order" = :order
                    """),
                    {"lesson_id": lesson_id, "order": cell_order}
                )
                db_cells = db_result.fetchall()
                
                if db_cells:
                    for db_cell in db_cells:
                        match = "✅" if str(db_cell[2]) == str(cell_type) else "⚠️"
                        print(f"        {match} 数据库: ID={db_cell[0]}, Order={db_cell[1]}, Type={db_cell[2]}, Title={db_cell[3]}")
                else:
                    print(f"        ❌ 数据库中未找到 order={cell_order} 的 Cell")

if __name__ == "__main__":
    asyncio.run(check_lesson_content())

