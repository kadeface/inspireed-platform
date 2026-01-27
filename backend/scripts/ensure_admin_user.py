"""
确保admin用户存在并密码正确
用于部署时初始化管理员账号
"""

import asyncio
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# 忽略 bcrypt 版本警告
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="passlib")

from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.core.security import get_password_hash, verify_password
from app.models import User, UserRole


async def ensure_admin_user():
    """确保admin用户存在并密码正确"""
    async with AsyncSessionLocal() as db:
        print("🔧 检查并确保admin用户存在...\n")

        # Admin账号配置
        admin_email = "admin@inspireed.com"
        admin_username = "admin"
        admin_password = "admin123"
        admin_full_name = "系统管理员"

        # 先通过用户名查找
        result = await db.execute(
            select(User).where(User.username == admin_username)
        )
        user = result.scalar_one_or_none()

        # 如果用户名不存在，通过邮箱查找
        if not user:
            result = await db.execute(
                select(User).where(User.email == admin_email)
            )
            user = result.scalar_one_or_none()

        if user:
            # 用户存在，检查并更新
            print(f"✅ 找到用户: {user.username} (ID: {user.id})")
            print(f"   邮箱: {user.email}")
            print(f"   角色: {user.role}")
            print(f"   激活状态: {user.is_active}")

            # 更新密码（捕获可能的错误）
            try:
                user.hashed_password = get_password_hash(admin_password)
            except Exception as e:
                print(f"   ⚠️  密码哈希错误: {e}")
                print(f"   尝试使用备用方法...")
                # 如果 get_password_hash 失败，直接使用 bcrypt
                import bcrypt
                user.hashed_password = bcrypt.hashpw(
                    admin_password.encode('utf-8'), 
                    bcrypt.gensalt()
                ).decode('utf-8')
            
            # 确保用户是激活的
            user.is_active = True
            
            # 确保角色是admin
            if user.role != UserRole.ADMIN:
                print(f"   ⚠️  警告: 用户角色是 {user.role}，将更新为 ADMIN")
                user.role = UserRole.ADMIN

            await db.commit()
            await db.refresh(user)

            # 验证密码是否正确
            is_valid = verify_password(admin_password, user.hashed_password)
            print(f"   密码验证: {'✅ 正确' if is_valid else '❌ 错误'}")

            print(f"\n✅ Admin用户已更新")
            print(f"   用户名: {admin_username}")
            print(f"   密码: {admin_password}")
        else:
            # 用户不存在，创建新用户
            print("📝 创建新的admin用户...")
            # 尝试获取密码哈希（捕获可能的错误）
            try:
                hashed_pwd = get_password_hash(admin_password)
            except Exception as e:
                print(f"   ⚠️  密码哈希错误: {e}")
                print(f"   尝试使用备用方法...")
                # 如果 get_password_hash 失败，直接使用 bcrypt
                import bcrypt
                hashed_pwd = bcrypt.hashpw(
                    admin_password.encode('utf-8'), 
                    bcrypt.gensalt()
                ).decode('utf-8')
            
            user = User(
                email=admin_email,
                username=admin_username,
                full_name=admin_full_name,
                hashed_password=hashed_pwd,
                role=UserRole.ADMIN,
                is_active=True,
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)

            # 验证密码
            is_valid = verify_password(admin_password, user.hashed_password)
            print(f"   密码验证: {'✅ 正确' if is_valid else '❌ 错误'}")

            print(f"\n✅ Admin用户已创建")
            print(f"   用户名: {admin_username}")
            print(f"   密码: {admin_password}")
            print(f"   用户ID: {user.id}")

        print("\n" + "=" * 50)
        print("📋 登录信息:")
        print("=" * 50)
        print(f"用户名: {admin_username}")
        print(f"密码: {admin_password}")
        print("=" * 50)


if __name__ == "__main__":
    asyncio.run(ensure_admin_user())

