#!/usr/bin/env python3
"""检查 Alembic 迁移链的完整性"""

import os
import re
from pathlib import Path

def extract_migration_info(content):
    """从迁移文件内容中提取 revision 和 down_revision"""
    # 提取 revision
    revision_match = re.search(r'revision[:\s=]+["\']([^"\']+)["\']', content)
    revision = revision_match.group(1) if revision_match else None
    
    # 提取 down_revision
    down_revision = None
    # 尝试多种格式
    patterns = [
        r'down_revision[:\s=]+["\']([^"\']+)["\']',
        r'down_revision[:\s=]+None',
        r'Revises:\s*([^\n]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, content)
        if match:
            if 'None' in match.group(0):
                down_revision = None
            elif match.lastindex:
                down_revision = match.group(1).strip().strip('"').strip("'")
            break
    
    return revision, down_revision

def main():
    versions_dir = Path('alembic/versions')
    migrations = {}
    
    print("🔍 扫描迁移文件...")
    print("=" * 60)
    
    # 读取所有迁移文件
    for file in sorted(versions_dir.glob('*.py')):
        if file.name.startswith('__'):
            continue
        
        content = file.read_text()
        revision, down_revision = extract_migration_info(content)
        
        if revision:
            migrations[revision] = {
                'file': file.name,
                'down_revision': down_revision
            }
            print(f"  {revision:30s} <- {down_revision or 'None':20s} ({file.name})")
    
    print(f"\n✅ 找到 {len(migrations)} 个迁移文件")
    print("=" * 60)
    
    # 检查迁移链
    print("\n📊 迁移链分析：")
    
    # 找到起始点（down_revision 为 None 的）
    heads = [rev for rev, info in migrations.items() if info['down_revision'] is None]
    print(f"\n起始迁移（根节点）: {len(heads)} 个")
    for head in heads:
        print(f"  - {head}")
    
    # 检查断链
    print("\n🔗 检查断链：")
    orphans = []
    for rev, info in migrations.items():
        if info['down_revision'] and info['down_revision'] not in migrations:
            orphans.append((rev, info['down_revision']))
    
    if orphans:
        print("  ❌ 发现断链：")
        for rev, missing in orphans:
            print(f"    {rev} ({migrations[rev]['file']})")
            print(f"      依赖: {missing} (不存在)")
    else:
        print("  ✅ 所有迁移都有有效的依赖")
    
    # 检查是否有多个 head（分支）
    if len(heads) > 1:
        print(f"\n⚠️  警告: 发现 {len(heads)} 个起始迁移，可能存在分支")
        print("   需要合并迁移或使用分支标签")
    
    # 查找最长链
    def find_chain_length(start_rev, visited=None):
        if visited is None:
            visited = set()
        
        if start_rev in visited:
            return 0
        
        visited.add(start_rev)
        
        # 找到下一个迁移
        next_migrations = [rev for rev, info in migrations.items() 
                          if info['down_revision'] == start_rev]
        
        if not next_migrations:
            return 1
        
        max_length = 0
        for next_rev in next_migrations:
            length = find_chain_length(next_rev, visited.copy())
            max_length = max(max_length, length)
        
        return 1 + max_length
    
    if heads:
        max_chain = max(find_chain_length(head) for head in heads)
        print(f"\n📏 最长迁移链: {max_chain} 个迁移")
    
    print("\n" + "=" * 60)
    print("💡 提示：")
    print("  运行 'alembic upgrade head' 会自动按顺序执行所有迁移")
    print("  不需要手动运行每个迁移文件")

if __name__ == '__main__':
    main()

