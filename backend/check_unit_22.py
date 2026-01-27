#!/usr/bin/env python
"""检查单元 22"""
import asyncio
from sqlalchemy import text
from app.core.database import engine

async def check_unit_22():
    """检查单元 22"""
    async with engine.connect() as conn:
        lesson_id = 76
        
        result = await conn.execute(
            text("SELECT content FROM lessons WHERE id = :lesson_id"),
            {"lesson_id": lesson_id}
        )
        row = result.fetchone()
        
        if not row or not row[0]:
            print("❌ 未找到教案")
            return
        
        lesson_content = row[0]
        
        if 22 < len(lesson_content):
            cell = lesson_content[22]
            print(f"单元 #22:")
            print(f"  类型: {cell.get('type')}")
            
            if cell.get("type") == "code":
                content = cell.get("content", {})
                print(f"  语言: {content.get('language')}")
                code = content.get("code", "")
                
                # 查找关键函数
                if "updateFlowchartHighlight" in code:
                    print(f"  ✓ 包含 updateFlowchartHighlight 函数")
                elif "updateFlowPath" in code:
                    print(f"  ✓ 包含 updateFlowPath 函数")
                elif "highlight" in code.lower():
                    print(f"  ✓ 包含 highlight 相关代码")
                    
                    # 查找具体的函数名
                    import re
                    functions = re.findall(r'function\s+(\w+)\s*\(', code)
                    print(f"  函数列表: {', '.join(functions[:10])}")
                else:
                    print(f"  ℹ️  不包含流程图高亮相关代码")

if __name__ == "__main__":
    asyncio.run(check_unit_22())

