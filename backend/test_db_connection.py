import asyncio
from app.core.database import AsyncSessionLocal
from app.models import User
from app.core.security import verify_password
from sqlalchemy import select

async def test_login():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.email == 'teacher@inspireed.com'))
        user = result.scalar_one_or_none()
        if user:
            print(f"User found: {user.email}")
            print(f"Username: {user.username}")
            print(f"Role: {user.role}")
            print(f"Is active: {user.is_active}")
            # 测试密码验证
            for password in ['teacher123', 'password123']:
                is_valid = verify_password(password, user.hashed_password)
                print(f"Password '{password}' is valid: {is_valid}")
        else:
            print("User not found")

if __name__ == '__main__':
    asyncio.run(test_login())

