"""
数据迁移脚本：将资源URL从路径格式转换为文件名格式

迁移内容：
1. resources表：file_url, thumbnail_url
2. library_assets表：storage_key, public_url, thumbnail_url
3. library_asset_versions表：storage_key, public_url
4. lessons表：content字段中的HTML图片URL

使用方法：
    python scripts/migrate_resource_urls_to_filenames.py [--dry-run] [--yes]
    
参数：
    --dry-run: 只显示将要更改的内容，不实际修改数据库
    --yes: 跳过确认提示，直接执行
"""

import asyncio
import sys
import re
import argparse
from pathlib import Path
from typing import Dict, List, Tuple

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select, update, text
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import AsyncSessionLocal
from app.models.curriculum import Resource
from app.models.library_asset import LibraryAsset, LibraryAssetVersion
from app.models.lesson import Lesson
from app.utils.resource_url import url_to_filename


def extract_filename_from_path(path: str) -> str:
    """
    从路径中提取文件名
    支持格式：
    - /uploads/resources/xxx.png
    - /uploads/thumbnails/xxx.png
    - uploads/resources/xxx.png
    - http://example.com/uploads/resources/xxx.png
    - xxx.png（已经是文件名，直接返回）
    """
    if not path:
        return path
    
    # 如果已经是文件名（不包含路径分隔符），直接返回
    if '/' not in path:
        return path
    
    # 提取文件名（最后一个/之后的部分）
    filename = path.split('/')[-1]
    
    # 处理 /uploads/resources/ 路径
    if '/uploads/resources/' in path:
        filename = path.split('/uploads/resources/')[-1]
    elif path.startswith('/uploads/resources/'):
        filename = path.replace('/uploads/resources/', '', 1)
    elif path.startswith('uploads/resources/'):
        filename = path.replace('uploads/resources/', '', 1)
    # 处理 /uploads/thumbnails/ 路径
    elif '/uploads/thumbnails/' in path:
        filename = path.split('/uploads/thumbnails/')[-1]
    elif path.startswith('/uploads/thumbnails/'):
        filename = path.replace('/uploads/thumbnails/', '', 1)
    elif path.startswith('uploads/thumbnails/'):
        filename = path.replace('uploads/thumbnails/', '', 1)
    
    return filename


async def migrate_resources_table(db: AsyncSession, dry_run: bool = False) -> Tuple[int, int]:
    """
    迁移resources表的file_url和thumbnail_url
    返回：(更新的记录数, 跳过的记录数)
    """
    print("\n1. 迁移 resources 表...")
    
    # 查询所有需要迁移的记录
    result = await db.execute(select(Resource))
    resources = result.scalars().all()
    
    updated_count = 0
    skipped_count = 0
    
    for resource in resources:
        updated = False
        
        # 迁移 file_url
        if resource.file_url:
            old_file_url = resource.file_url
            new_file_url = extract_filename_from_path(old_file_url)
            if new_file_url != old_file_url:
                resource.file_url = new_file_url
                updated = True
                print(f"  Resource ID={resource.id}: file_url '{old_file_url}' -> '{new_file_url}'")
        
        # 迁移 thumbnail_url
        if resource.thumbnail_url:
            old_thumbnail_url = resource.thumbnail_url
            new_thumbnail_url = extract_filename_from_path(old_thumbnail_url)
            if new_thumbnail_url != old_thumbnail_url:
                resource.thumbnail_url = new_thumbnail_url
                updated = True
                print(f"  Resource ID={resource.id}: thumbnail_url '{old_thumbnail_url}' -> '{new_thumbnail_url}'")
        
        if updated:
            updated_count += 1
        else:
            skipped_count += 1
    
    if updated_count > 0:
        await db.commit()
    
    print(f"  ✓ 更新 {updated_count} 条记录，跳过 {skipped_count} 条记录")
    return updated_count, skipped_count


async def migrate_library_assets_table(db: AsyncSession, dry_run: bool = False) -> Tuple[int, int]:
    """
    迁移library_assets表的storage_key、public_url和thumbnail_url
    返回：(更新的记录数, 跳过的记录数)
    """
    print("\n2. 迁移 library_assets 表...")
    
    result = await db.execute(select(LibraryAsset))
    assets = result.scalars().all()
    
    updated_count = 0
    skipped_count = 0
    
    for asset in assets:
        updated = False
        
        # 迁移 storage_key
        if asset.storage_key:
            old_storage_key = asset.storage_key
            new_storage_key = extract_filename_from_path(old_storage_key)
            if new_storage_key != old_storage_key:
                asset.storage_key = new_storage_key
                updated = True
                print(f"  LibraryAsset ID={asset.id}: storage_key '{old_storage_key}' -> '{new_storage_key}'")
        
        # 迁移 public_url
        if asset.public_url:
            old_public_url = asset.public_url
            new_public_url = extract_filename_from_path(old_public_url)
            if new_public_url != old_public_url:
                asset.public_url = new_public_url
                updated = True
                print(f"  LibraryAsset ID={asset.id}: public_url '{old_public_url}' -> '{new_public_url}'")
        
        # 迁移 thumbnail_url
        if asset.thumbnail_url:
            old_thumbnail_url = asset.thumbnail_url
            new_thumbnail_url = extract_filename_from_path(old_thumbnail_url)
            if new_thumbnail_url != old_thumbnail_url:
                asset.thumbnail_url = new_thumbnail_url
                updated = True
                print(f"  LibraryAsset ID={asset.id}: thumbnail_url '{old_thumbnail_url}' -> '{new_thumbnail_url}'")
        
        if updated:
            updated_count += 1
        else:
            skipped_count += 1
    
    if updated_count > 0 and not dry_run:
        await db.commit()
    
    print(f"  ✓ 更新 {updated_count} 条记录，跳过 {skipped_count} 条记录" + (" (dry-run)" if dry_run else ""))
    return updated_count, skipped_count


async def migrate_library_asset_versions_table(db: AsyncSession, dry_run: bool = False) -> Tuple[int, int]:
    """
    迁移library_asset_versions表的storage_key和public_url
    返回：(更新的记录数, 跳过的记录数)
    """
    print("\n3. 迁移 library_asset_versions 表...")
    
    result = await db.execute(select(LibraryAssetVersion))
    versions = result.scalars().all()
    
    updated_count = 0
    skipped_count = 0
    
    for version in versions:
        updated = False
        
        # 迁移 storage_key
        if version.storage_key:
            old_storage_key = version.storage_key
            new_storage_key = extract_filename_from_path(old_storage_key)
            if new_storage_key != old_storage_key:
                version.storage_key = new_storage_key
                updated = True
                print(f"  LibraryAssetVersion ID={version.id} (asset_id={version.asset_id}, version={version.version}): storage_key '{old_storage_key}' -> '{new_storage_key}'")
        
        # 迁移 public_url
        if version.public_url:
            old_public_url = version.public_url
            new_public_url = extract_filename_from_path(old_public_url)
            if new_public_url != old_public_url:
                version.public_url = new_public_url
                updated = True
                print(f"  LibraryAssetVersion ID={version.id} (asset_id={version.asset_id}, version={version.version}): public_url '{old_public_url}' -> '{new_public_url}'")
        
        if updated:
            updated_count += 1
        else:
            skipped_count += 1
    
    if updated_count > 0 and not dry_run:
        await db.commit()
    
    print(f"  ✓ 更新 {updated_count} 条记录，跳过 {skipped_count} 条记录" + (" (dry-run)" if dry_run else ""))
    return updated_count, skipped_count


def convert_html_urls_to_filenames(html: str) -> Tuple[str, bool]:
    """
    将HTML中的图片URL转换为文件名
    返回：(转换后的HTML, 是否有变化)
    """
    if not html or '<img' not in html:
        return html, False
    
    changed = False
    new_html = html
    
    # 替换img标签中的src属性
    def replace_img_src(match):
        nonlocal changed
        src_value = match.group(2)
        # 跳过blob:、data:、http://、https://开头的URL
        if src_value.startswith(('blob:', 'data:', 'http://', 'https://')):
            return match.group(0)
        
        # 提取文件名
        new_src = extract_filename_from_path(src_value)
        if new_src != src_value:
            changed = True
            return f'{match.group(1)}{new_src}{match.group(3)}'
        return match.group(0)
    
    new_html = re.sub(
        r'(<img[^>]*\s+src\s*=\s*["\'])([^"\']+)(["\'][^>]*>)',
        replace_img_src,
        new_html,
        flags=re.IGNORECASE
    )
    
    # 替换data-pdf-url、data-file-url等属性
    for attr in ["data-pdf-url", "data-file-url", "data-file-download-url", "data-pdf-view-url"]:
        def replace_attr(match):
            nonlocal changed
            url_value = match.group(2)
            if url_value.startswith(('blob:', 'data:', 'http://', 'https://')):
                return match.group(0)
            new_url = extract_filename_from_path(url_value)
            if new_url != url_value:
                changed = True
                return f'{match.group(1)}{new_url}{match.group(3)}'
            return match.group(0)
        
        pattern = f'({attr}\\s*=\\s*["\'])([^"\']+)(["\'])'
        new_html = re.sub(pattern, replace_attr, new_html, flags=re.IGNORECASE)
    
    return new_html, changed


async def migrate_lessons_content(db: AsyncSession, dry_run: bool = False) -> Tuple[int, int]:
    """
    迁移lessons表的content字段中的HTML图片URL
    返回：(更新的记录数, 跳过的记录数)
    """
    print("\n4. 迁移 lessons 表的 content 字段...")
    
    result = await db.execute(select(Lesson))
    lessons = result.scalars().all()
    
    updated_count = 0
    skipped_count = 0
    
    for lesson in lessons:
        if not lesson.content:
            skipped_count += 1
            continue
        
        # 处理content（可能是list或JSON字符串）
        import json
        content = lesson.content
        
        # 如果content是字符串，尝试解析为JSON
        if isinstance(content, str):
            try:
                content = json.loads(content)
            except json.JSONDecodeError:
                skipped_count += 1
                continue
        
        if not isinstance(content, list):
            skipped_count += 1
            continue
        
        content_changed = False
        new_content = []
        
        for cell in content:
            if not isinstance(cell, dict):
                new_content.append(cell)
                continue
            
            cell_type = cell.get('type', '')
            cell_content = cell.get('content', {})
            
            # 处理text类型的cell
            if cell_type == 'text' and isinstance(cell_content, dict):
                html = cell_content.get('html', '')
                if html:
                    new_html, changed = convert_html_urls_to_filenames(html)
                    if changed:
                        cell_content = cell_content.copy()
                        cell_content['html'] = new_html
                        cell = cell.copy()
                        cell['content'] = cell_content
                        content_changed = True
                        print(f"  Lesson ID={lesson.id}: 更新了 text cell 的 HTML")
            
            new_content.append(cell)
        
        if content_changed:
            lesson.content = new_content
            updated_count += 1
        else:
            skipped_count += 1
    
    if updated_count > 0 and not dry_run:
        await db.commit()
    
    print(f"  ✓ 更新 {updated_count} 条记录，跳过 {skipped_count} 条记录" + (" (dry-run)" if dry_run else ""))
    return updated_count, skipped_count


async def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='资源URL迁移脚本：将路径格式转换为文件名格式')
    parser.add_argument('--dry-run', action='store_true', help='只显示将要更改的内容，不实际修改数据库')
    parser.add_argument('--yes', action='store_true', help='跳过确认提示，直接执行')
    args = parser.parse_args()
    
    print("=" * 80)
    print("资源URL迁移脚本：将路径格式转换为文件名格式")
    print("=" * 80)
    if args.dry_run:
        print("\n⚠️  DRY-RUN模式：不会实际修改数据库")
    
    # 确认操作（除非使用了--yes参数）
    if not args.yes:
        print("\n⚠️  警告：此操作将修改数据库中的数据！")
        print("建议在运行前备份数据库。")
        response = input("\n是否继续？(yes/no): ")
        if response.lower() not in ['yes', 'y']:
            print("操作已取消。")
            return
    
    async with AsyncSessionLocal() as db:
        total_updated = 0
        total_skipped = 0
        
        try:
            # 1. 迁移resources表
            updated, skipped = await migrate_resources_table(db, args.dry_run)
            total_updated += updated
            total_skipped += skipped
            
            # 2. 迁移library_assets表
            updated, skipped = await migrate_library_assets_table(db, args.dry_run)
            total_updated += updated
            total_skipped += skipped
            
            # 3. 迁移library_asset_versions表
            updated, skipped = await migrate_library_asset_versions_table(db, args.dry_run)
            total_updated += updated
            total_skipped += skipped
            
            # 4. 迁移lessons表的content字段
            updated, skipped = await migrate_lessons_content(db, args.dry_run)
            total_updated += updated
            total_skipped += skipped
            
            print("\n" + "=" * 80)
            if args.dry_run:
                print("预览完成！（未实际修改数据库）")
            else:
                print("迁移完成！")
            print("=" * 80)
            print(f"总计：更新 {total_updated} 条记录，跳过 {total_skipped} 条记录")
            
        except Exception as e:
            await db.rollback()
            print(f"\n❌ 错误：{e}")
            import traceback
            traceback.print_exc()
            raise


if __name__ == "__main__":
    asyncio.run(main())

