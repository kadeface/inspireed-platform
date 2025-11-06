"""
发布测试课程供学生学习
"""

import asyncio
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models import Lesson, LessonStatus, User, UserRole


async def publish_test_lessons():
    """发布测试课程"""

    async with AsyncSessionLocal() as db:
        print("📚 开始发布测试课程...")

        # 获取所有草稿状态的教案
        result = await db.execute(select(Lesson).where(Lesson.status == LessonStatus.DRAFT))
        draft_lessons = result.scalars().all()

        if not draft_lessons:
            print("⚠️  没有找到草稿状态的教案")

            # 检查是否有已发布的课程
            result = await db.execute(select(Lesson).where(Lesson.status == LessonStatus.PUBLISHED))
            published_lessons = result.scalars().all()

            if published_lessons:
                print(f"\n✅ 已有 {len(published_lessons)} 个已发布的课程:")
                for lesson in published_lessons:
                    print(f"   - {lesson.title}")
            else:
                print("\n❌ 没有任何课程！请先运行 python scripts/create_test_data.py 创建测试数据")
            return

        print(f"\n找到 {len(draft_lessons)} 个草稿教案，开始发布...")

        published_count = 0
        for lesson in draft_lessons:
            lesson.status = LessonStatus.PUBLISHED
            published_count += 1
            print(f"   ✓ 发布: {lesson.title}")

        await db.commit()

        print(f"\n✅ 成功发布 {published_count} 个课程！")

        # 显示所有已发布的课程
        result = await db.execute(select(Lesson).where(Lesson.status == LessonStatus.PUBLISHED))
        all_published = result.scalars().all()

        print(f"\n📊 当前已发布课程总数: {len(all_published)}")
        print("\n课程列表:")
        print("=" * 60)
        for i, lesson in enumerate(all_published, 1):
            print(f"{i}. {lesson.title}")
            if lesson.description:
                print(f"   描述: {lesson.description[:50]}...")
            print(f"   单元数: {lesson.cell_count}")
            print()

        print("=" * 60)
        print("\n✨ 现在学生可以登录学习这些课程了！")
        print("🌐 学生登录: http://localhost:5173/login")
        print("📧 邮箱: student@inspireed.com")
        print("🔒 密码: student123")


if __name__ == "__main__":
    asyncio.run(publish_test_lessons())
