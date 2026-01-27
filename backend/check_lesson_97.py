#!/usr/bin/env python3
"""
检查lesson 97在数据库中存储的URL格式
"""
import asyncio
import sys
import os
import re
import json

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.lesson import Lesson


async def check_lesson_97():
    """检查lesson 97的URL存储格式"""
    print("=" * 80)
    print(" 检查 Lesson 97 的URL存储格式")
    print("=" * 80)
    
    async with AsyncSessionLocal() as db:
        # 查找lesson 97
        result = await db.execute(
            select(Lesson)
            .where(Lesson.id == 97)
        )
        lesson = result.scalar_one_or_none()
        
        if not lesson:
            print("❌ 未找到 lesson 97")
            return
        
        print(f"\n教案 ID={lesson.id}")
        print(f"标题: {lesson.title}")
        print(f"创建时间: {lesson.created_at}")
        print(f"更新时间: {lesson.updated_at}")
        
        if not lesson.content or not isinstance(lesson.content, list):
            print("\n❌ lesson.content 为空或不是列表")
            return
        
        print(f"\n内容单元数量: {len(lesson.content)}")
        print("\n" + "=" * 80)
        
        # 检查每个单元
        for idx, cell in enumerate(lesson.content):
            if not isinstance(cell, dict):
                continue
            
            cell_type = cell.get('type', 'unknown')
            print(f"\n单元 {idx} (type={cell_type})")
            
            if cell_type == 'text':
                content = cell.get('content', {})
                html = content.get('html', '')
                
                if html:
                    # 提取所有img标签的src
                    img_srcs = re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', html, re.IGNORECASE)
                    
                    if img_srcs:
                        print(f"  包含 {len(img_srcs)} 个图片:")
                        for i, src in enumerate(img_srcs, 1):
                            print(f"    图片 {i}: {src}")
                            
                            # 分析URL格式
                            if src.startswith('http://') or src.startswith('https://'):
                                print(f"      ❌ 完整URL（包含IP/域名）")
                                try:
                                    from urllib.parse import urlparse
                                    parsed = urlparse(src)
                                    print(f"        主机: {parsed.netloc}")
                                    print(f"        路径: {parsed.path}")
                                    filename = parsed.path.split('/')[-1]
                                    print(f"        应该存储的文件名: {filename}")
                                except:
                                    pass
                            elif src.startswith('/uploads/'):
                                print(f"      ⚠️  相对路径格式")
                                filename = src.split('/')[-1]
                                print(f"        应该存储的文件名: {filename}")
                            elif '/' not in src and not src.startswith('blob:') and not src.startswith('data:'):
                                print(f"      ✅ 文件名格式（正确！）")
                            else:
                                print(f"      ❓ 未知格式")
                    
                    # 检查文件附件
                    file_urls = re.findall(r'data-(pdf|file)-url=["\']([^"\']+)["\']', html, re.IGNORECASE)
                    if file_urls:
                        print(f"  包含 {len(file_urls)} 个文件附件:")
                        for file_type, url in file_urls:
                            print(f"    {file_type} 文件: {url}")
                            if url.startswith('http://') or url.startswith('https://'):
                                print(f"      ❌ 完整URL格式")
                            elif '/' not in url:
                                print(f"      ✅ 文件名格式（正确！）")
                            else:
                                print(f"      ⚠️  其他格式")
                    
                    # 检查PDF查看URL
                    pdf_view_urls = re.findall(r'data-pdf-view-url=["\']([^"\']+)["\']', html, re.IGNORECASE)
                    if pdf_view_urls:
                        print(f"  包含 {len(pdf_view_urls)} 个PDF查看URL:")
                        for url in pdf_view_urls:
                            print(f"    PDF查看: {url}")
                            if url.startswith('http://') or url.startswith('https://'):
                                print(f"      ❌ 完整URL格式")
                            elif '/' not in url:
                                print(f"      ✅ 文件名格式（正确！）")
                            else:
                                print(f"      ⚠️  其他格式")
                
            elif cell_type == 'video':
                content = cell.get('content', {})
                video_url = content.get('videoUrl') or content.get('video_url')
                thumbnail = content.get('thumbnail') or content.get('thumbnail_url')
                
                if video_url:
                    print(f"  视频URL: {video_url}")
                    if video_url.startswith('http://') or video_url.startswith('https://'):
                        print(f"    ❌ 完整URL格式")
                    elif '/' not in video_url:
                        print(f"    ✅ 文件名格式（正确！）")
                    else:
                        print(f"    ⚠️  其他格式")
                
                if thumbnail:
                    print(f"  缩略图URL: {thumbnail}")
                    if thumbnail.startswith('http://') or thumbnail.startswith('https://'):
                        print(f"    ❌ 完整URL格式")
                    elif '/' not in thumbnail:
                        print(f"    ✅ 文件名格式（正确！）")
                    else:
                        print(f"    ⚠️  其他格式")
        
        print("\n" + "=" * 80)
        print("检查完成")


if __name__ == "__main__":
    asyncio.run(check_lesson_97())

