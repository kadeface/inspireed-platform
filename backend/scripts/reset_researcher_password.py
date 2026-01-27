"""
重置教研员密码
"""

import asyncio
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.user import User, UserRole
from app.core.security import get_password_hash


async def reset_password():
    """重置教研员密码"""
    async with AsyncSessionLocal() as db:
        # 查找教研员
        result = await db.execute(select(User).where(User.username == "researcher"))
        researcher = result.scalar_one_or_none()

        if researcher:
            # 重置密码
            researcher.hashed_password = get_password_hash("password123")
            await db.commit()
            print("✅ 教研员密码已重置为: password123")
        else:
            print("❌ 未找到教研员账号")


if __name__ == "__main__":
    asyncio.run(reset_password())
