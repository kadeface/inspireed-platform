#!/usr/bin/env python3
"""
检查数据库中教案内容的URL格式
"""
import asyncio
import sys
import os
import re
import json

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.models.lesson import Lesson


async def check_lesson_urls():
    """检查教案中的URL格式"""
    async with AsyncSessionLocal() as db:
        # 获取前10个教案
        result = await db.execute(select(Lesson).limit(10))
        lessons = result.scalars().all()
        
        print(f"检查前 {len(lessons)} 个教案的URL格式:\n")
        
        for lesson in lessons:
            print(f"=" * 80)
            print(f"教案 ID: {lesson.id}")
            print(f"标题: {lesson.title}")
            print(f"封面图: {lesson.cover_image_url}")
            
            if lesson.content:
                # 查找所有包含图片的cell
                for idx, cell in enumerate(lesson.content):
                    if isinstance(cell, dict):
                        cell_type = cell.get('type', '')
                        if cell_type == 'text':
                            content = cell.get('content', {})
                            if isinstance(content, dict):
                                html = content.get('html', '')
                                if html and '<img' in html:
                                    # 提取img标签的src
                                    img_matches = re.findall(r'<img[^>]+src\s*=\s*["\']([^"\']+)["\']', html, re.IGNORECASE)
                                    if img_matches:
                                        print(f"\n  Cell {idx} (text) 包含 {len(img_matches)} 个图片:")
                                        for img_src in img_matches[:3]:  # 只显示前3个
                                            print(f"    - {img_src}")
                        
                        elif cell_type == 'video':
                            content = cell.get('content', {})
                            if isinstance(content, dict):
                                video_url = content.get('videoUrl') or content.get('video_url')
                                if video_url:
                                    print(f"\n  Cell {idx} (video) 视频URL:")
                                    print(f"    - {video_url}")
            
            print()


if __name__ == "__main__":
    print("检查教案内容中的URL格式")
    print("=" * 80)
    print()
    
    asyncio.run(check_lesson_urls())

