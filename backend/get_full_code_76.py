#!/usr/bin/env python
"""获取 lesson 76 中的完整 HTML 代码"""
import asyncio
import json
from sqlalchemy import text
from app.core.database import engine

async def get_full_code():
    """获取完整代码"""
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
        
        # 找到单元 21 和 22
        for idx in [21, 22]:
            if idx < len(lesson_content):
                cell = lesson_content[idx]
                if cell.get("type") == "code":
                    code = cell.get("content", {}).get("code", "")
                    
                    # 查找 updateFlowchartHighlight 函数
                    if "updateFlowchartHighlight" in code:
                        print(f"\n{'='*80}")
                        print(f"单元 #{idx} - 完整代码")
                        print(f"{'='*80}\n")
                        
                        # 只输出相关函数部分
                        lines = code.split('\n')
                        in_function = False
                        function_lines = []
                        brace_count = 0
                        
                        for i, line in enumerate(lines):
                            if 'updateFlowchartHighlight' in line or 'updateHeight' in line:
                                in_function = True
                                function_lines.append(f"{i+1:4d}: {line}")
                                # 计算花括号
                                brace_count += line.count('{') - line.count('}')
                            elif in_function:
                                function_lines.append(f"{i+1:4d}: {line}")
                                brace_count += line.count('{') - line.count('}')
                                if brace_count <= 0 and ('}' in line):
                                    in_function = False
                                    print('\n'.join(function_lines))
                                    print()
                                    function_lines = []
                                    brace_count = 0

if __name__ == "__main__":
    asyncio.run(get_full_code())

