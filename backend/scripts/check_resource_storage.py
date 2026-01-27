"""
检查资源存储方式
验证数据库存储格式、文件系统存储位置、API返回格式
"""

import asyncio
import os
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.curriculum import Resource
from app.models.library_asset import LibraryAsset
from app.models.lesson import Lesson
from app.core.config import settings


async def check_resource_storage():
    """检查资源存储方式"""
    print("=" * 80)
    print("资源存储方式检查")
    print("=" * 80)
    
    async with AsyncSessionLocal() as db:
        # 1. 检查配置
        print("\n1. 配置信息:")
        print(f"   UPLOAD_DIR: {settings.UPLOAD_DIR}")
        print(f"   RESOURCE_BASE_PATH: {settings.RESOURCE_BASE_PATH}")
        print(f"   RESOURCE_BASE_URL: {settings.RESOURCE_BASE_URL or '(未设置，将从请求中获取)'}")
        
        # 2. 检查文件系统存储
        print("\n2. 文件系统存储:")
        resources_dir = os.path.join(settings.UPLOAD_DIR, "resources")
        if os.path.exists(resources_dir):
            files = [f for f in os.listdir(resources_dir) if os.path.isfile(os.path.join(resources_dir, f))]
            print(f"   存储目录: {os.path.abspath(resources_dir)}")
            print(f"   文件数量: {len(files)}")
            if files:
                print(f"   示例文件: {files[0]}")
                # 检查文件格式（应该是UUID格式）
                if len(files[0].split('.')) == 2:
                    name, ext = files[0].rsplit('.', 1)
                    print(f"   文件名格式: UUID.{ext} ✓")
                else:
                    print(f"   文件名格式: {files[0]} (可能不是UUID格式)")
        else:
            print(f"   存储目录不存在: {resources_dir}")
        
        # 3. 检查Resource表的存储格式
        print("\n3. Resource表存储格式:")
        result = await db.execute(select(Resource).limit(5))
        resources = result.scalars().all()
        if resources:
            print(f"   找到 {len(resources)} 条记录（显示前5条）:")
            for r in resources:
                file_url = r.file_url
                thumbnail_url = r.thumbnail_url
                print(f"\n   Resource ID={r.id}, Title={r.title}")
                print(f"     file_url: {file_url}")
                if file_url:
                    # 检查存储格式
                    if file_url.startswith(('http://', 'https://')):
                        print(f"      格式: 完整URL ✗ (应该只存储文件名)")
                    elif '/' in file_url and not file_url.startswith('/'):
                        print(f"      格式: 相对路径 ✗ (应该只存储文件名)")
                    elif file_url.startswith('/'):
                        print(f"      格式: 绝对路径 ✗ (应该只存储文件名)")
                    else:
                        print(f"      格式: 文件名 ✓")
                if thumbnail_url:
                    print(f"     thumbnail_url: {thumbnail_url}")
                    if not thumbnail_url.startswith(('http://', 'https://', '/')):
                        print(f"      格式: 文件名 ✓")
                    else:
                        print(f"      格式: URL/路径 ✗ (应该只存储文件名)")
        else:
            print("   未找到Resource记录")
        
        # 4. 检查LibraryAsset表的存储格式
        print("\n4. LibraryAsset表存储格式:")
        result = await db.execute(select(LibraryAsset).limit(5))
        assets = result.scalars().all()
        if assets:
            print(f"   找到 {len(assets)} 条记录（显示前5条）:")
            for a in assets:
                storage_key = a.storage_key
                public_url = a.public_url
                thumbnail_url = a.thumbnail_url
                print(f"\n   LibraryAsset ID={a.id}, Title={a.title}")
                print(f"     storage_key: {storage_key}")
                if storage_key:
                    if storage_key.startswith(('http://', 'https://')):
                        print(f"      格式: 完整URL ✗ (应该只存储文件名)")
                    elif '/' in storage_key and not storage_key.startswith('/'):
                        print(f"      格式: 相对路径 ✗ (应该只存储文件名)")
                    elif storage_key.startswith('/'):
                        print(f"      格式: 绝对路径 ✗ (应该只存储文件名)")
                    else:
                        print(f"      格式: 文件名 ✓")
                if public_url:
                    print(f"     public_url: {public_url}")
                    if public_url.startswith(('http://', 'https://')):
                        print(f"      格式: 完整URL ✗ (应该只存储文件名)")
                    elif public_url.startswith('/'):
                        print(f"      格式: 绝对路径 ✗ (应该只存储文件名)")
                    else:
                        print(f"      格式: 文件名 ✓")
                if thumbnail_url:
                    print(f"     thumbnail_url: {thumbnail_url}")
        else:
            print("   未找到LibraryAsset记录")
        
        # 5. 检查Lesson表的content中的URL格式
        print("\n5. Lesson表content中的URL格式:")
        result = await db.execute(select(Lesson).limit(3))
        lessons = result.scalars().all()
        if lessons:
            print(f"   找到 {len(lessons)} 条记录（显示前3条）:")
            for lesson in lessons:
                print(f"\n   Lesson ID={lesson.id}, Title={lesson.title}")
                if lesson.content:
                    import json
                    content = lesson.content if isinstance(lesson.content, list) else json.loads(lesson.content) if isinstance(lesson.content, str) else []
                    for idx, cell in enumerate(content[:2]):  # 只检查前2个cell
                        if isinstance(cell, dict):
                            cell_type = cell.get('type', '')
                            content_data = cell.get('content', {})
                            if cell_type == 'video' and isinstance(content_data, dict):
                                video_url = content_data.get('videoUrl') or content_data.get('video_url')
                                if video_url:
                                    print(f"     Cell {idx} (video): {video_url[:80]}...")
                                    if video_url.startswith(('http://', 'https://')):
                                        print(f"       格式: 完整URL ✗ (应该只存储文件名)")
                                    elif '/' in video_url and not video_url.startswith('/'):
                                        print(f"       格式: 相对路径 ✗ (应该只存储文件名)")
                                    else:
                                        print(f"       格式: 文件名 ✓")
                            elif cell_type == 'text' and isinstance(content_data, dict):
                                html = content_data.get('html', '')
                                if html and '<img' in html:
                                    import re
                                    img_matches = re.findall(r'<img[^>]+src\s*=\s*["\']([^"\']+)["\']', html, re.IGNORECASE)
                                    if img_matches:
                                        print(f"     Cell {idx} (text): 包含 {len(img_matches)} 个图片")
                                        for img_src in img_matches[:1]:  # 只显示第一个
                                            print(f"       图片URL: {img_src[:80]}...")
                                            if img_src.startswith(('http://', 'https://')):
                                                print(f"         格式: 完整URL ✗ (应该只存储文件名)")
                                            elif img_src.startswith(('blob:', 'data:')):
                                                print(f"         格式: Blob/Data URL (临时，正常)")
                                            elif '/' in img_src and not img_src.startswith('/'):
                                                print(f"         格式: 相对路径 ✗ (应该只存储文件名)")
                                            else:
                                                print(f"         格式: 文件名 ✓")
        else:
            print("   未找到Lesson记录")
        
        # 6. 总结
        print("\n" + "=" * 80)
        print("总结:")
        print("=" * 80)
        print("✓ 表示符合预期（只存储文件名）")
        print("✗ 表示不符合预期（存储了完整URL或路径）")
        print("\n预期存储格式:")
        print("  - 数据库: 只存储文件名（UUID.扩展名）")
        print("  - 文件系统: storage/resources/{UUID}.{ext}")
        print("  - API返回: 完整URL（动态服务器地址 + RESOURCE_BASE_PATH + 文件名）")


if __name__ == "__main__":
    asyncio.run(check_resource_storage())

