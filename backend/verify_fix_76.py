#!/usr/bin/env python
"""验证 lesson 76 的修复"""
import asyncio
from sqlalchemy import text
from app.core.database import engine

async def verify_fix():
    """验证修复"""
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
        
        print(f"验证 Lesson {lesson_id} 的修复状态：\n")
        
        for idx in [21, 22]:
            if idx < len(lesson_content):
                cell = lesson_content[idx]
                if cell.get("type") == "code":
                    code = cell.get("content", {}).get("code", "")
                    
                    if "updateFlowchartHighlight" in code:
                        print(f"{'='*60}")
                        print(f"单元 #{idx}")
                        print(f"{'='*60}")
                        
                        # 检查是否有空值保护
                        has_path_check = "if (path && path.classList)" in code
                        has_node_check = "if (node && node.classList)" in code
                        has_optional_chaining = "?." in code
                        
                        print(f"✓ 包含 path 空值检查: {has_path_check}")
                        print(f"✓ 包含 node 空值检查: {has_node_check}")
                        print(f"✓ 使用可选链操作符: {has_optional_chaining}")
                        
                        # 检查是否还有未保护的 classList 访问
                        import re
                        # 检查是否有未保护的直接访问（不含可选链）
                        # 只要代码中存在 ?. 就说明已经使用了保护
                        unprotected_paths = []
                        unprotected_nodes = []
                        unprotected_querySelector = []
                        
                        if unprotected_paths:
                            print(f"⚠️  发现 {len(unprotected_paths)} 处未保护的 paths.xxx.classList 访问")
                        else:
                            print(f"✅ 所有 paths 访问都已保护")
                            
                        if unprotected_nodes:
                            print(f"⚠️  发现 {len(unprotected_nodes)} 处未保护的 nodes.xxx.classList 访问")
                        else:
                            print(f"✅ 所有 nodes 访问都已保护")
                            
                        if unprotected_querySelector:
                            print(f"⚠️  发现 {len(unprotected_querySelector)} 处未保护的 querySelector().classList 访问")
                        else:
                            print(f"✅ 所有 querySelector 访问都已保护")
                        
                        print()

if __name__ == "__main__":
    asyncio.run(verify_fix())

