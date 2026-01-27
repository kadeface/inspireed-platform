"""
为智慧农业课程添加章节数据
"""

import asyncio
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models import Subject, Grade, Course, Chapter


async def add_chapters():
    """为智慧农业课程添加章节"""

    async with AsyncSessionLocal() as db:
        print("🚀 开始为智慧农业课程添加章节...")

        # 1. 获取信息技术学科和七年级
        result = await db.execute(select(Subject).where(Subject.code == "computer"))
        computer_subject = result.scalar_one_or_none()

        result = await db.execute(select(Grade).where(Grade.level == 7))
        grade_7 = result.scalar_one_or_none()

        if not computer_subject or not grade_7:
            print("❌ 学科或年级不存在")
            return

        # 2. 获取智慧农业课程
        result = await db.execute(
            select(Course).where(
                Course.subject_id == computer_subject.id, Course.grade_id == grade_7.id
            )
        )
        course = result.scalar_one_or_none()

        if not course:
            print("❌ 智慧农业课程不存在")
            return

        print(f"✓ 找到课程: {course.name}")

        # 3. 创建章节数据
        chapters_data = [
            {
                "name": "第一章：智慧农业概述",
                "code": "chapter-1",
                "description": "了解智慧农业的基本概念和发展现状",
                "display_order": 1,
            },
            {
                "name": "第二章：传感器技术",
                "code": "chapter-2",
                "description": "学习各种传感器在农业中的应用",
                "display_order": 2,
            },
            {
                "name": "第三章：物联网技术",
                "code": "chapter-3",
                "description": "掌握物联网在智慧农业中的实现",
                "display_order": 3,
            },
            {
                "name": "第四章：数据分析",
                "code": "chapter-4",
                "description": "学习农业数据的收集和分析方法",
                "display_order": 4,
            },
            {
                "name": "第五章：智能控制",
                "code": "chapter-5",
                "description": "了解自动化控制系统在农业中的应用",
                "display_order": 5,
            },
        ]

        # 4. 创建章节
        created_chapters = []
        for chapter_data in chapters_data:
            # 检查章节是否已存在
            result = await db.execute(
                select(Chapter).where(
                    Chapter.course_id == course.id, Chapter.code == chapter_data["code"]
                )
            )
            existing_chapter = result.scalar_one_or_none()

            if not existing_chapter:
                chapter = Chapter(
                    course_id=course.id,
                    name=chapter_data["name"],
                    code=chapter_data["code"],
                    description=chapter_data["description"],
                    display_order=chapter_data["display_order"],
                    is_active=True,
                )
                db.add(chapter)
                await db.commit()
                await db.refresh(chapter)
                created_chapters.append(chapter)
                print(f"✓ 创建章节: {chapter.name}")
            else:
                print(f"✓ 章节已存在: {existing_chapter.name}")
                created_chapters.append(existing_chapter)

        # 5. 为第一章创建子章节
        chapter1 = created_chapters[0]
        sub_chapters_data = [
            {
                "name": "1.1 智慧农业的定义",
                "code": "section-1-1",
                "description": "学习智慧农业的基本定义和特征",
                "display_order": 1,
            },
            {
                "name": "1.2 智慧农业的发展历程",
                "code": "section-1-2",
                "description": "了解智慧农业的发展历史和现状",
                "display_order": 2,
            },
            {
                "name": "1.3 智慧农业的应用领域",
                "code": "section-1-3",
                "description": "掌握智慧农业在各个领域的应用",
                "display_order": 3,
            },
        ]

        for sub_data in sub_chapters_data:
            result = await db.execute(
                select(Chapter).where(
                    Chapter.course_id == course.id, Chapter.code == sub_data["code"]
                )
            )
            existing_sub = result.scalar_one_or_none()

            if not existing_sub:
                sub_chapter = Chapter(
                    course_id=course.id,
                    parent_id=chapter1.id,
                    name=sub_data["name"],
                    code=sub_data["code"],
                    description=sub_data["description"],
                    display_order=sub_data["display_order"],
                    is_active=True,
                )
                db.add(sub_chapter)
                await db.commit()
                await db.refresh(sub_chapter)
                print(f"✓ 创建子章节: {sub_chapter.name}")
            else:
                print(f"✓ 子章节已存在: {existing_sub.name}")

        print(f"\n✅ 章节创建完成！")
        print(f"📊 为课程 '{course.name}' 创建了 {len(created_chapters)} 个章节")


if __name__ == "__main__":
    asyncio.run(add_chapters())
