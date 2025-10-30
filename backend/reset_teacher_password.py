import asyncio
from app.core.database import AsyncSessionLocal
from app.models import User
from app.core.security import get_password_hash
from sqlalchemy import select

async def reset_password():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.email == 'teacher@inspireed.com'))
        user = result.scalar_one_or_none()
        if user:
            user.hashed_password = get_password_hash('teacher123')
            await db.commit()
            print(f"✅ 密码已重置为: teacher123")
            print(f"   邮箱: {user.email}")
        else:
            print("❌ 未找到教师账号")

if __name__ == '__main__':
    asyncio.run(reset_password())

