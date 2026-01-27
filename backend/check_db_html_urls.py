#!/usr/bin/env python3
"""
检查数据库中HTML内容里图片URL的存储格式
"""
import asyncio
import sys
import os
import re

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.lesson import Lesson


async def check_html_urls():
    """检查数据库中HTML内容里的URL格式"""
    print("=" * 80)
    print(" 检查数据库中HTML内容里的URL格式")
    print("=" * 80)
    
    async with AsyncSessionLocal() as db:
        # 查找包含text类型的教案
        result = await db.execute(
            select(Lesson)
            .order_by(Lesson.updated_at.desc())
            .limit(10)
        )
        lessons = result.scalars().all()
        
        for lesson in lessons:
            if not lesson.content or not isinstance(lesson.content, list):
                continue
            
            has_text_cell = False
            for cell in lesson.content:
                if isinstance(cell, dict) and cell.get('type') == 'text':
                    has_text_cell = True
                    break
            
            if not has_text_cell:
                continue
            
            print(f"\n教案 ID={lesson.id}, 标题={lesson.title}")
            
            # 检查text cell中的HTML
            for idx, cell in enumerate(lesson.content):
                if isinstance(cell, dict) and cell.get('type') == 'text':
                    content = cell.get('content', {})
                    html = content.get('html', '')
                    
                    if html and '<img' in html:
                        # 提取所有img标签的src
                        img_srcs = re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', html, re.IGNORECASE)
                        
                        if img_srcs:
                            print(f"  单元 {idx} (text) 包含 {len(img_srcs)} 个图片:")
                            for i, src in enumerate(img_srcs, 1):
                                print(f"    图片 {i}: {src}")
                                
                                # 分析URL格式
                                if src.startswith('http://') or src.startswith('https://'):
                                    print(f"      ❌ 问题: 数据库中存储了完整URL（包含IP/域名）")
                                    # 提取IP/域名
                                    try:
                                        from urllib.parse import urlparse
                                        parsed = urlparse(src)
                                        print(f"        包含主机: {parsed.netloc}")
                                        print(f"        应该只存储文件名: {src.split('/')[-1]}")
                                    except:
                                        pass
                                elif src.startswith('/uploads/'):
                                    print(f"      ⚠️  存储格式: 相对路径")
                                    print(f"        应该只存储文件名: {src.split('/')[-1]}")
                                elif '/' not in src and not src.startswith('blob:') and not src.startswith('data:'):
                                    print(f"      ✅ 存储格式: 文件名（正确！）")
                                else:
                                    print(f"      ❓ 存储格式: 未知格式")


if __name__ == "__main__":
    asyncio.run(check_html_urls())

