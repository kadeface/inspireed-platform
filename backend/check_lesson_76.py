#!/usr/bin/env python
"""检查 lesson 76 中的 HTML 代码单元"""
import asyncio
import json
from sqlalchemy import text
from app.core.database import engine

async def check_lesson_76():
    """检查 lesson 76 中的 HTML 代码单元"""
    async with engine.connect() as conn:
        lesson_id = 76
        
        # 查询 lesson.content
        result = await conn.execute(
            text("SELECT id, title, content FROM lessons WHERE id = :lesson_id"),
            {"lesson_id": lesson_id}
        )
        row = result.fetchone()
        
        if not row:
            print(f"❌ 未找到 Lesson {lesson_id}")
            return
        
        lesson_content = row[2] if row[2] else []
        
        print(f"📋 Lesson {lesson_id}: {row[1]}")
        print(f"总共 {len(lesson_content)} 个单元\n")
        
        # 查找所有 code 类型的单元
        for idx, cell_data in enumerate(lesson_content):
            cell_type = cell_data.get("type") or cell_data.get("cell_type", "")
            cell_title = cell_data.get("title", "")
            
            if cell_type == "code":
                cell_content = cell_data.get("content", {})
                language = cell_content.get("language", "")
                code = cell_content.get("code", "")
                
                print(f"\n{'='*80}")
                print(f"单元 #{idx}: {cell_title}")
                print(f"类型: {cell_type}, 语言: {language}")
                print(f"{'='*80}")
                
                # 如果是 HTML 并且包含 flowchart 相关代码
                if language == "html" and ("flowchart" in code.lower() or "updateflowcharthighlight" in code.lower()):
                    print("\n⚠️  发现包含流程图相关代码的 HTML 单元！\n")
                    print("代码内容：")
                    print("-" * 80)
                    print(code[:2000])  # 打印前 2000 字符
                    if len(code) > 2000:
                        print("\n... (代码太长，已截断) ...")
                    print("-" * 80)
                    
                    # 检查是否有 path.classList 相关代码但缺少空值检查
                    if "path.classList" in code and "if (path" not in code and "path &&" not in code:
                        print("\n❌ 检测到问题：代码中使用了 path.classList 但缺少空值检查！")
                        print("建议：在访问 path.classList 之前添加空值检查")

if __name__ == "__main__":
    asyncio.run(check_lesson_76())

