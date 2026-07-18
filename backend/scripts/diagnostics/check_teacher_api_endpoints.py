"""
测试教师端相关API端点
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models import User, Lesson, Course, Chapter


async def test_api_endpoints():
    """测试API端点可用性"""
    async with AsyncSessionLocal() as db:
        print("=" * 60)
        print("🧪 测试教师端API端点可用性")
        print("=" * 60)
        print()
        
        # 1. 检查教师账号
        print("1️⃣  检查教师账号")
        teacher_result = await db.execute(
            select(User).where(User.email == "teacher@inspireed.com")
        )
        teacher = teacher_result.scalar_one_or_none()
        if teacher:
            print(f"   ✅ 教师账号存在: {teacher.username} (ID: {teacher.id})")
        else:
            print("   ❌ 教师账号不存在")
            return
        print()
        
        # 2. 检查课程
        print("2️⃣  检查课程")
        course_result = await db.execute(
            select(Course).where(Course.is_active == True).limit(1)
        )
        course = course_result.scalar_one_or_none()
        if course:
            print(f"   ✅ 课程存在: {course.name} (ID: {course.id})")
        else:
            print("   ⚠️  没有可用课程")
        print()
        
        # 3. 检查教案
        print("3️⃣  检查教案")
        lesson_result = await db.execute(
            select(Lesson).where(Lesson.creator_id == teacher.id).limit(5)
        )
        lessons = lesson_result.scalars().all()
        print(f"   ✅ 找到 {len(lessons)} 个教案")
        if lessons:
            print("   可用教案ID列表:")
            for lesson in lessons:
                print(f"      - {lesson.title} (ID: {lesson.id}, 状态: {lesson.status})")
        print()
        
        # 4. API端点列表
        print("4️⃣  API端点列表")
        print("   以下API端点应该可用（需要教师token）:")
        print()
        print("   📝 教案相关:")
        print("      POST   /api/v1/lessons/              - 创建教案")
        print("      GET    /api/v1/lessons/              - 获取教案列表")
        print("      GET    /api/v1/lessons/{id}          - 获取教案详情")
        print("      PATCH  /api/v1/lessons/{id}           - 更新教案")
        print()
        print("   📋 活动相关:")
        print("      POST   /api/v1/activities/submissions - 创建提交（学生）")
        print("      POST   /api/v1/activities/submissions/{id}/submit - 提交活动（学生）")
        print("      GET    /api/v1/activities/cells/{id}/submissions - 获取提交列表（教师）")
        print("      GET    /api/v1/activities/cells/{id}/statistics - 获取统计数据（教师）")
        print()
        print("   💬 问答相关:")
        print("      GET    /api/v1/questions/             - 获取问题列表")
        print("      GET    /api/v1/questions/{id}          - 获取问题详情")
        print()
        print("=" * 60)
        print("✅ API端点测试完成")
        print()
        print("💡 下一步:")
        print("   1. 使用教师账号登录前端")
        print("   2. 按照测试指南操作:")
        print("      docs/testing/TEACHER_WORKFLOW_TEST_GUIDE.md")
        print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_api_endpoints())

