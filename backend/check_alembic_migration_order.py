#!/usr/bin/env python3
"""
检查 Alembic 迁移文件的顺序和依赖关系
用于诊断迁移顺序错误的问题
"""

import os
import re
import ast
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional, Any
from collections import defaultdict

# 迁移文件目录
MIGRATIONS_DIR = Path(__file__).parent / "alembic" / "versions"


def extract_revision_info(file_path: Path) -> Optional[Dict[str, Any]]:
    """从迁移文件中提取 revision 和 down_revision 信息（使用正则表达式）"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 使用正则表达式提取 revision（支持 revision = "xxx" 和 revision: str = "xxx"）
        revision_match = re.search(r'^revision\s*:?\s*\w*\s*[:=]\s*["\']([^"\']+)["\']', content, re.MULTILINE)
        if not revision_match:
            return None
        
        revision = revision_match.group(1)
        
        # 使用正则表达式提取 down_revision
        down_revision = None
        
        # 匹配 down_revision = None 或 down_revision: Union[str, None] = None
        if re.search(r'^down_revision\s*:?\s*[^=]*\s*[:=]\s*None', content, re.MULTILINE):
            down_revision = None
        else:
            # 匹配 down_revision = "xxx" 或 down_revision: Union[str, None] = "xxx"
            down_rev_match = re.search(r'^down_revision\s*:?\s*[^=]*\s*[:=]\s*["\']([^"\']+)["\']', content, re.MULTILINE)
            if down_rev_match:
                down_revision = down_rev_match.group(1)
            else:
                # 匹配元组形式 down_revision = ('xxx', 'yyy')
                tuple_match = re.search(r'^down_revision\s*:?\s*[^=]*\s*[:=]\s*\(([^)]+)\)', content, re.MULTILINE)
                if tuple_match:
                    tuple_content = tuple_match.group(1)
                    # 提取元组中的所有字符串
                    items = re.findall(r'["\']([^"\']+)["\']', tuple_content)
                    if items:
                        down_revision = tuple(items)
        
        return {
            'file': file_path.name,
            'revision': revision,
            'down_revision': down_revision
        }
    except Exception as e:
        print(f"⚠️  解析文件 {file_path.name} 时出错: {e}")
        return None


def check_migration_order():
    """检查迁移顺序"""
    print("=" * 80)
    print("Alembic 迁移文件顺序检查")
    print("=" * 80)
    print()
    
    # 收集所有迁移文件信息
    migrations: Dict[str, Dict] = {}
    files = sorted(MIGRATIONS_DIR.glob("*.py"))
    
    print(f"📁 找到 {len(files)} 个迁移文件\n")
    
    failed_files = []
    for file_path in files:
        info = extract_revision_info(file_path)
        if info:
            migrations[info['revision']] = info
        else:
            failed_files.append(file_path.name)
    
    print(f"✅ 成功解析 {len(migrations)} 个迁移文件")
    if failed_files:
        print(f"⚠️  无法解析 {len(failed_files)} 个文件: {', '.join(failed_files)}")
    print()
    
    # 显示所有 revision 列表
    print("=" * 80)
    print("📋 所有迁移文件的 revision 列表")
    print("=" * 80)
    for rev, info in sorted(migrations.items(), key=lambda x: x[1]['file']):
        down_rev = info['down_revision']
        down_rev_str = str(down_rev) if down_rev is not None else "None (根节点)"
        print(f"  {rev:40s} <- {down_rev_str:40s} ({info['file']})")
    print()
    
    # 构建依赖图
    revision_to_file = {info['revision']: info['file'] for info in migrations.values()}
    down_revision_map: Dict[str, List[str]] = defaultdict(list)  # down_revision -> [revisions]
    all_revisions = set(migrations.keys())
    all_down_revisions = set()
    
    for revision, info in migrations.items():
        down_rev = info['down_revision']
        if down_rev is None:
            continue
        
        # 处理分支合并的情况
        if isinstance(down_rev, tuple):
            for dr in down_rev:
                if dr:
                    all_down_revisions.add(dr)
                    down_revision_map[dr].append(revision)
        else:
            all_down_revisions.add(down_rev)
            down_revision_map[down_rev].append(revision)
    
    # 检查问题
    issues = []
    
    # 1. 检查断链：down_revision 指向不存在的 revision
    print("=" * 80)
    print("🔍 检查断链（down_revision 指向不存在的 revision）...")
    print("=" * 80)
    broken_links = []
    for revision, info in migrations.items():
        down_rev = info['down_revision']
        if down_rev is None:
            continue
        
        if isinstance(down_rev, tuple):
            for dr in down_rev:
                if dr and dr not in all_revisions:
                    broken_links.append((revision, dr, info['file']))
        else:
            if down_rev not in all_revisions:
                broken_links.append((revision, down_rev, info['file']))
    
    if broken_links:
        print(f"❌ 发现 {len(broken_links)} 个断链：\n")
        for rev, down_rev, file in broken_links:
            print(f"   文件: {file}")
            print(f"   revision: {rev}")
            print(f"   down_revision: {down_rev} (不存在)")
            # 尝试找到相似的 revision
            similar = [r for r in all_revisions if down_rev.lower() in r.lower() or r.lower() in down_rev.lower()]
            if similar:
                print(f"   💡 可能的匹配: {', '.join(similar)}")
            print()
        issues.extend(broken_links)
    else:
        print("✅ 没有发现断链\n")
    
    # 2. 检查多个根节点（多个迁移没有 down_revision）
    print("=" * 80)
    print("🔍 检查根节点（没有 down_revision 的迁移）...")
    print("=" * 80)
    roots = [rev for rev, info in migrations.items() if info['down_revision'] is None]
    if len(roots) > 1:
        print(f"❌ 发现 {len(roots)} 个根节点（应该有且仅有一个）：\n")
        for rev in roots:
            print(f"   - {rev} ({revision_to_file[rev]})")
        print()
        issues.append(("multiple_roots", roots))
    elif len(roots) == 0:
        print("❌ 没有根节点（所有迁移都有 down_revision，可能存在循环）\n")
        issues.append(("no_roots", []))
    else:
        print(f"✅ 找到 1 个根节点: {roots[0]} ({revision_to_file[roots[0]]})\n")
    
    # 3. 检查循环依赖
    print("=" * 80)
    print("🔍 检查循环依赖...")
    print("=" * 80)
    def has_cycle(start_rev: str, visited: Set[str], path: Set[str]) -> Optional[List[str]]:
        if start_rev in path:
            return list(path) + [start_rev]
        if start_rev in visited:
            return None
        
        visited.add(start_rev)
        path.add(start_rev)
        
        info = migrations.get(start_rev)
        if info and info['down_revision']:
            down_rev = info['down_revision']
            if isinstance(down_rev, tuple):
                for dr in down_rev:
                    if dr:
                        cycle = has_cycle(dr, visited, path)
                        if cycle:
                            return cycle
            else:
                cycle = has_cycle(down_rev, visited, path)
                if cycle:
                    return cycle
        
        path.remove(start_rev)
        return None
    
    cycles = []
    visited = set()
    for rev in migrations.keys():
        if rev not in visited:
            cycle = has_cycle(rev, visited, set())
            if cycle:
                cycles.append(cycle)
    
    if cycles:
        print(f"❌ 发现 {len(cycles)} 个循环依赖：\n")
        for cycle in cycles:
            print(f"   {' -> '.join(cycle)}")
        print()
        issues.extend(cycles)
    else:
        print("✅ 没有发现循环依赖\n")
    
    # 4. 检查孤立的迁移（没有其他迁移依赖它，且不是根节点）
    print("=" * 80)
    print("🔍 检查孤立的迁移（没有其他迁移依赖它）...")
    print("=" * 80)
    referenced = set()
    for info in migrations.values():
        down_rev = info['down_revision']
        if down_rev:
            if isinstance(down_rev, tuple):
                referenced.update(dr for dr in down_rev if dr)
            else:
                referenced.add(down_rev)
    
    isolated = all_revisions - referenced - set(roots)
    if isolated:
        print(f"⚠️  发现 {len(isolated)} 个孤立的迁移（没有其他迁移依赖它们）：\n")
        for rev in isolated:
            print(f"   - {rev} ({revision_to_file[rev]})")
        print()
    
    # 5. 显示依赖链
    print("=" * 80)
    print("📊 迁移依赖链（从根节点开始）")
    print("=" * 80)
    print()
    
    def print_chain(revision: str, level: int = 0, visited: Optional[Set[str]] = None):
        if visited is None:
            visited = set()
        
        if revision in visited:
            print("   " * level + f"⚠️  {revision} (循环引用)")
            return
        
        visited.add(revision)
        indent = "   " * level
        file_name = revision_to_file.get(revision, "未知")
        print(f"{indent}├─ {revision} ({file_name})")
        
        # 找到依赖此 revision 的所有迁移
        dependents = [rev for rev, info in migrations.items() 
                     if info['down_revision'] == revision or 
                     (isinstance(info['down_revision'], tuple) and revision in info['down_revision'])]
        
        for i, dep in enumerate(sorted(dependents)):
            is_last = i == len(dependents) - 1
            prefix = "└─" if is_last else "├─"
            print_chain(dep, level + 1, visited.copy())
    
    if roots:
        print_chain(roots[0])
    else:
        print("⚠️  无法显示依赖链（没有根节点）")
        # 尝试从所有迁移开始显示
        print("\n尝试显示所有迁移的依赖关系：")
        for rev in sorted(all_revisions):
            info = migrations[rev]
            down_rev = info['down_revision']
            if down_rev and (not isinstance(down_rev, tuple) or all(dr in all_revisions for dr in down_rev if dr)):
                continue
            print(f"\n从 {rev} 开始：")
            print_chain(rev)
    
    print()
    print("=" * 80)
    
    # 总结和修复建议
    if issues:
        print(f"\n❌ 发现 {len(issues)} 个问题需要修复")
        print("\n" + "=" * 80)
        print("🔧 修复建议")
        print("=" * 80)
        print("\n1. 修复断链：")
        for rev, down_rev, file in broken_links:
            print(f"   文件: {file}")
            print(f"   当前 down_revision: {down_rev}")
            similar = [r for r in all_revisions if down_rev.lower() in r.lower() or r.lower() in down_rev.lower()]
            if similar:
                print(f"   建议改为: {similar[0]}")
            print()
        print("\n2. 确保只有一个根节点（down_revision = None）")
        print("3. 修复循环依赖（如果存在）")
    else:
        print("\n✅ 迁移顺序检查通过！")
    
    return issues


if __name__ == "__main__":
    check_migration_order()
