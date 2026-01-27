#!/usr/bin/env python
"""修复 lesson 76 单元 22 的空值检查问题"""
import asyncio
import json
from sqlalchemy import text
from app.core.database import engine

async def fix_unit_22():
    """修复单元 22"""
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
            if cell.get("type") == "code":
                code = cell.get("content", {}).get("code", "")
                
                if "highlightFlowPath" in code:
                    print(f"\n修复单元 #22...")
                    
                    # 查找并显示 highlightFlowPath 函数
                    lines = code.split('\n')
                    in_function = False
                    function_lines = []
                    brace_count = 0
                    
                    for i, line in enumerate(lines):
                        if 'highlightFlowPath' in line and 'function' in line:
                            in_function = True
                            function_lines.append(f"{i+1:4d}: {line}")
                            brace_count += line.count('{') - line.count('}')
                        elif in_function:
                            function_lines.append(f"{i+1:4d}: {line}")
                            brace_count += line.count('{') - line.count('}')
                            if brace_count <= 0 and '}' in line:
                                break
                    
                    if function_lines:
                        print("\n原始函数:")
                        print('\n'.join(function_lines[:30]))  # 显示前 30 行
                        print()
                    
                    # 应用类似的修复
                    import re
                    new_code = code
                    
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
                    
                    if original_paths_forEach in code:
                        new_code = new_code.replace(original_paths_forEach, fixed_paths_forEach)
                        print("  ✓ 修复了 paths.forEach")
                    
                    if original_nodes_forEach in new_code:
                        new_code = new_code.replace(original_nodes_forEach, fixed_nodes_forEach)
                        print("  ✓ 修复了 nodes.forEach")
                    
                    # 修复 document.querySelector().classList 调用
                    pattern = r"document\.querySelector\(([^)]+)\)\.classList"
                    
                    def replace_querySelector(match):
                        selector = match.group(1)
                        return f"(document.querySelector({selector})?.classList || {{add: () => {{}}, remove: () => {{}}}})"
                    
                    matches = re.findall(pattern, new_code)
                    if matches:
                        new_code = re.sub(pattern, replace_querySelector, new_code)
                        print(f"  ✓ 修复了 {len(matches)} 处 querySelector().classList 调用")
                    
                    # 修复 document.getElementById().classList 调用
                    pattern2 = r"document\.getElementById\(([^)]+)\)\.classList"
                    
                    def replace_getElementById(match):
                        id_arg = match.group(1)
                        return f"(document.getElementById({id_arg})?.classList || {{add: () => {{}}, remove: () => {{}}}})"
                    
                    matches2 = re.findall(pattern2, new_code)
                    if matches2:
                        new_code = re.sub(pattern2, replace_getElementById, new_code)
                        print(f"  ✓ 修复了 {len(matches2)} 处 getElementById().classList 调用")
                    
                    # 修复 paths.xxx.classList 和 nodes.xxx.classList 调用
                    path_node_pattern = r"(paths|nodes)\.(\w+)\.classList\."
                    
                    def replace_path_node(match):
                        obj = match.group(1)
                        key = match.group(2)
                        return f"({obj}.{key}?.classList || {{add: () => {{}}, remove: () => {{}}}})."
                    
                    path_node_matches = re.findall(path_node_pattern, new_code)
                    if path_node_matches:
                        new_code = re.sub(path_node_pattern, replace_path_node, new_code)
                        print(f"  ✓ 修复了 {len(path_node_matches)} 处 paths/nodes 属性访问")
                    
                    if new_code != code:
                        # 更新单元内容
                        cell["content"]["code"] = new_code
                        lesson_content[22] = cell
                        
                        # 保存到数据库
                        content_json = json.dumps(lesson_content)
                        await conn.execute(
                            text("UPDATE lessons SET content = CAST(:content AS jsonb) WHERE id = :lesson_id"),
                            {"content": content_json, "lesson_id": lesson_id}
                        )
                        await conn.commit()
                        print(f"  ✅ 单元 #22 修复完成并已保存到数据库")
                    else:
                        print(f"  ℹ️  单元 #22 未发现需要修复的模式")

if __name__ == "__main__":
    asyncio.run(fix_unit_22())

