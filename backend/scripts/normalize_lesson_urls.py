#!/usr/bin/env python3
"""
规范化教案内容中的资源URL
将包含localhost或IP地址的完整URL转换为相对路径
"""
import asyncio
import sys
import os
import re
from urllib.parse import urlparse

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.models.lesson import Lesson


def normalize_url(url: str) -> str:
    """将完整URL转换为相对路径"""
    if not url or not isinstance(url, str):
        return url
    
    # 如果已经是相对路径，直接返回
    if url.startswith('/uploads/'):
        return url
    
    # 如果是完整URL（包含localhost或IP地址），提取路径部分
    if url.startswith(('http://', 'https://')):
        try:
            parsed = urlparse(url)
            # 检查是否是资源URL
            if parsed.path.startswith('/uploads/'):
                return parsed.path
        except:
            pass
    
    return url


def normalize_content(content):
    """递归规范化教案内容中的URL"""
    if isinstance(content, dict):
        result = {}
        for key, value in content.items():
            if key in ['cover_image_url', 'preview_url', 'download_url', 'videoUrl', 'video_url', 
                      'html_url', 'htmlUrl', 'url', 'src', 'href', 'file_url', 'fileUrl',
                      'image_url', 'imageUrl', 'thumbnail_url', 'thumbnailUrl']:
                result[key] = normalize_url(value) if isinstance(value, str) else value
            elif key == 'html' and isinstance(value, str):
                # 处理HTML中的图片URL
                html = value
                # 替换img标签中的src
                html = re.sub(
                    r'<img\s+([^>]*?)src\s*=\s*["\']([^"\']+)["\']',
                    lambda m: f'<img {m.group(1)}src="{normalize_url(m.group(2))}"',
                    html,
                    flags=re.IGNORECASE
                )
                result[key] = html
            else:
                result[key] = normalize_content(value)
        return result
    elif isinstance(content, list):
        return [normalize_content(item) for item in content]
    else:
        return content


async def normalize_lesson_urls():
    """规范化所有教案中的资源URL"""
    async with AsyncSessionLocal() as db:
        # 获取所有教案
        result = await db.execute(select(Lesson))
        lessons = result.scalars().all()
        
        updated_count = 0
        total_count = len(lessons)
        
        print(f"找到 {total_count} 个教案，开始处理...")
        
        for lesson in lessons:
            try:
                # 规范化封面图URL
                if lesson.cover_image_url:
                    old_url = lesson.cover_image_url
                    new_url = normalize_url(old_url)
                    if old_url != new_url:
                        lesson.cover_image_url = new_url
                        print(f"  教案 {lesson.id} ({lesson.title}): 封面图URL已规范化")
                        print(f"    {old_url} -> {new_url}")
                
                # 规范化内容中的URL
                if lesson.content:
                    old_content = lesson.content
                    new_content = normalize_content(old_content)
                    
                    # 检查是否有变化
                    if str(old_content) != str(new_content):
                        lesson.content = new_content
                        updated_count += 1
                        print(f"  教案 {lesson.id} ({lesson.title}): 内容URL已规范化")
                
            except Exception as e:
                print(f"  错误: 处理教案 {lesson.id} 时出错: {str(e)}")
                continue
        
        # 提交更改
        if updated_count > 0:
            await db.commit()
            print(f"\n✅ 成功规范化 {updated_count} 个教案的URL")
        else:
            print("\n✅ 所有教案的URL已经是规范格式")
        
        return updated_count


if __name__ == "__main__":
    print("=" * 60)
    print("规范化教案内容中的资源URL")
    print("=" * 60)
    print()
    
    updated = asyncio.run(normalize_lesson_urls())
    
    print()
    print("=" * 60)
    print(f"处理完成，共更新 {updated} 个教案")
    print("=" * 60)

