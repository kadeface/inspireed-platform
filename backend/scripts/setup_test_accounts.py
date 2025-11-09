"""
设置所有测试账号（管理员、教师、学生、研究员）
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


async def setup_test_accounts():
    """创建或检查所有测试账号"""
    async with AsyncSessionLocal() as db:
        print("🔧 开始设置测试账号...\n")

        # 测试账号配置
        test_accounts = [
            {
                "email": "admin@inspireed.com",
                "username": "admin",
                "full_name": "测试管理员",
                "password": "admin123",
                "role": UserRole.ADMIN,
            },
            {
                "email": "teacher@inspireed.com",
                "username": "teacher",
                "full_name": "测试教师",
                "password": "teacher123",
                "role": UserRole.TEACHER,
            },
            {
                "email": "student@inspireed.com",
                "username": "student",
                "full_name": "测试学生",
                "password": "student123",
                "role": UserRole.STUDENT,
            },
            {
                "email": "researcher@inspireed.com",
                "username": "researcher",
                "full_name": "测试研究员",
                "password": "researcher123",
                "role": UserRole.RESEARCHER,
            },
        ]

        for account_config in test_accounts:
            # 通过邮箱检查账号是否存在
            result = await db.execute(
                select(User).where(User.email == account_config["email"])
            )
            user = result.scalar_one_or_none()

            if user:
                # 如果存在，更新密码确保正确
                user.hashed_password = get_password_hash(account_config["password"])
                await db.commit()
                await db.refresh(user)
                print(f"✅ {account_config['role'].value} 账号已存在，密码已更新")
                print(f"   邮箱: {user.email}")
                print(f"   密码: {account_config['password']}")
            else:
                # 如果不存在，创建新账号
                user = User(
                    email=account_config["email"],
                    username=account_config["username"],
                    full_name=account_config["full_name"],
                    hashed_password=get_password_hash(account_config["password"]),
                    role=account_config["role"],
                    is_active=True,
                )
                db.add(user)
                await db.commit()
                await db.refresh(user)
                print(f"✅ 创建 {account_config['role'].value} 账号")
                print(f"   邮箱: {user.email}")
                print(f"   密码: {account_config['password']}")

            print()

        print("=" * 50)
        print("📋 测试账号列表:")
        print("=" * 50)
        for account_config in test_accounts:
            print(
                f"{account_config['role'].value.upper():12} - {account_config['email']:25} / {account_config['password']}"
            )
        print("=" * 50)


if __name__ == "__main__":
    asyncio.run(setup_test_accounts())
