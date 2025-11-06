"""
创建学生测试账号
"""

import asyncio
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.core.security import get_password_hash
from app.models import User, UserRole


async def create_student_account():
    """创建学生测试账号"""

    async with AsyncSessionLocal() as db:
        print("🎓 开始创建学生测试账号...")

        # 检查学生账号是否已存在
        result = await db.execute(select(User).where(User.email == "student@inspireed.com"))
        student = result.scalar_one_or_none()

        if student:
            print(f"✓ 学生账号已存在: {student.email}")
            print(f"  用户名: {student.username}")
            print(f"  角色: {student.role}")
        else:
            # 创建学生账号
            student = User(
                email="student@inspireed.com",
                username="student",
                full_name="测试学生",
                hashed_password=get_password_hash("student123"),
                role=UserRole.STUDENT,
                is_active=True,
            )
            db.add(student)
            await db.commit()
            await db.refresh(student)
            print(f"✅ 成功创建学生账号: {student.email}")

        print("\n" + "=" * 50)
        print("🔑 学生登录信息:")
        print("=" * 50)
        print(f"📧 邮箱: student@inspireed.com")
        print(f"🔒 密码: student123")
        print(f"👤 用户名: {student.username}")
        print(f"🎭 角色: student")
        print("=" * 50)
        print("\n🌐 登录地址: http://localhost:5173/login")
        print("📱 学生端首页: http://localhost:5173/student")
        print("\n✨ 提示: 登录后可以浏览已发布的课程并开始学习！")


if __name__ == "__main__":
    asyncio.run(create_student_account())
