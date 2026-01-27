#!/usr/bin/env python
"""修复 lesson 76 中的空值检查问题"""
import asyncio
import json
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import JSONB
from app.core.database import engine

async def fix_lesson_76():
    """修复 lesson 76"""
    async with engine.connect() as conn:
        lesson_id = 76
        
        # 获取教案
        result = await conn.execute(
            text("SELECT content FROM lessons WHERE id = :lesson_id"),
            {"lesson_id": lesson_id}
        )
        row = result.fetchone()
        
        if not row or not row[0]:
            print("❌ 未找到教案")
            return
        
        lesson_content = row[0]
        modified = False
        
        # 修复单元 21 和 22
        for idx in [21, 22]:
            if idx < len(lesson_content):
                cell = lesson_content[idx]
                if cell.get("type") == "code":
                    code = cell.get("content", {}).get("code", "")
                    
                    if "updateFlowchartHighlight" in code:
                        print(f"\n修复单元 #{idx}...")
                        
                        # 修复 Object.values().forEach 调用
                        original_paths_forEach = """Object.values(paths).forEach(path => {
                    path.classList.remove('active');
                });"""
                        
                        fixed_paths_forEach = """Object.values(paths).forEach(path => {
                    if (path && path.classList) {
                        path.classList.remove('active');
                    }
                });"""
                        
                        original_nodes_forEach = """Object.values(nodes).forEach(node => {
                    node.classList.remove('active');
                });"""
                        
                        fixed_nodes_forEach = """Object.values(nodes).forEach(node => {
                    if (node && node.classList) {
                        node.classList.remove('active');
                    }
                });"""
                        
                        original_nodeTexts_forEach = """nodeTexts.forEach(text => {
                    text.classList.remove('active');
                });"""
                        
                        fixed_nodeTexts_forEach = """nodeTexts.forEach(text => {
                    if (text && text.classList) {
                        text.classList.remove('active');
                    }
                });"""
                        
                        # 应用修复
                        new_code = code
                        if original_paths_forEach in code:
                            new_code = new_code.replace(original_paths_forEach, fixed_paths_forEach)
                            print("  ✓ 修复了 paths.forEach")
                        
                        if original_nodes_forEach in new_code:
                            new_code = new_code.replace(original_nodes_forEach, fixed_nodes_forEach)
                            print("  ✓ 修复了 nodes.forEach")
                        
                        if original_nodeTexts_forEach in new_code:
                            new_code = new_code.replace(original_nodeTexts_forEach, fixed_nodeTexts_forEach)
                            print("  ✓ 修复了 nodeTexts.forEach")
                        
                        # 修复所有 document.querySelector().classList 调用
                        # 使用更安全的模式
                        import re
                        
                        # 查找所有 document.querySelector(...).classList 模式
                        pattern = r"document\.querySelector\(([^)]+)\)\.classList"
                        
                        def replace_querySelector(match):
                            selector = match.group(1)
                            return f"(document.querySelector({selector})?.classList || {{add: () => {{}}, remove: () => {{}}}})"
                        
                        # 计算替换次数
                        matches = re.findall(pattern, new_code)
                        if matches:
                            new_code = re.sub(pattern, replace_querySelector, new_code)
                            print(f"  ✓ 修复了 {len(matches)} 处 querySelector().classList 调用")
                        
                        # 修复 paths.xxx.classList 和 nodes.xxx.classList 调用
                        # 这些可能在条件语句中
                        path_node_pattern = r"(paths|nodes)\.(\w+)\.classList\."
                        
                        def replace_path_node(match):
                            obj = match.group(1)  # paths or nodes
                            key = match.group(2)  # path1, node1, etc.
                            return f"({obj}.{key}?.classList || {{add: () => {{}}, remove: () => {{}}}})."
                        
                        path_node_matches = re.findall(path_node_pattern, new_code)
                        if path_node_matches:
                            new_code = re.sub(path_node_pattern, replace_path_node, new_code)
                            print(f"  ✓ 修复了 {len(path_node_matches)} 处 paths/nodes 属性访问")
                        
                        if new_code != code:
                            # 更新单元内容
                            cell["content"]["code"] = new_code
                            lesson_content[idx] = cell
                            modified = True
                            print(f"  ✅ 单元 #{idx} 修复完成")
                        else:
                            print(f"  ⚠️  单元 #{idx} 未发现需要修复的模式")
        
        if modified:
            # 保存到数据库
            # 将列表转换为 JSON 字符串，然后让 PostgreSQL 将其转换为 JSONB
            content_json = json.dumps(lesson_content)
            await conn.execute(
                text("UPDATE lessons SET content = CAST(:content AS jsonb) WHERE id = :lesson_id"),
                {"content": content_json, "lesson_id": lesson_id}
            )
            await conn.commit()
            print(f"\n✅ Lesson {lesson_id} 修复完成并已保存到数据库")
        else:
            print(f"\n⚠️  没有进行任何修改")

if __name__ == "__main__":
    asyncio.run(fix_lesson_76())

