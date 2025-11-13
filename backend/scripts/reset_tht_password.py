"""
重置教研员 tht 账号密码
"""

import asyncio
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.user import User, UserRole
from app.core.security import get_password_hash


async def reset_tht_password():
    """重置教研员 tht 账号密码"""
    async with AsyncSessionLocal() as db:
        # 查找教研员账号（通过用户名或邮箱）
        result = await db.execute(
            select(User).where(
                (User.username == "tht") | (User.email == "tht@inspireed.com")
            )
        )
        user = result.scalar_one_or_none()

        if user:
            # 检查账号信息
            print(f"✅ 找到账号:")
            print(f"  - ID: {user.id}")
            print(f"  - 用户名: {user.username}")
            print(f"  - 邮箱: {user.email}")
            print(f"  - 姓名: {user.full_name}")
            print(f"  - 角色: {user.role}")
            print(f"  - 激活状态: {user.is_active}")
            print(f"  - 创建时间: {user.created_at}")
            print()

            # 确保账号是激活状态
            if not user.is_active:
                user.is_active = True
                print("⚠️  账号未激活，已自动激活")

            # 重置密码为 tht123456（简单易记）
            new_password = "tht123456"
            user.hashed_password = get_password_hash(new_password)
            await db.commit()
            await db.refresh(user)

            print("=" * 50)
            print("✅ 密码已重置成功!")
            print("=" * 50)
            print(f"📧 邮箱: {user.email}")
            print(f"👤 用户名: {user.username}")
            print(f"🔒 新密码: {new_password}")
            print(f"🎭 角色: {user.role}")
            print(f"✅ 激活状态: {user.is_active}")
            print("=" * 50)
            print("\n🌐 登录地址: http://localhost:5173/login")
            print("📱 教研员端首页: http://localhost:5173/researcher")
        else:
            print("❌ 未找到用户名 tht 或邮箱 tht@inspireed.com 的账号")
            print("   请检查账号信息是否正确")


if __name__ == "__main__":
    asyncio.run(reset_tht_password())

