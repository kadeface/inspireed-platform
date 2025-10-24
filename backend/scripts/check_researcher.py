"""
检查和创建教研员账号
"""
import asyncio
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.user import User, UserRole
from app.core.security import get_password_hash


async def check_and_create_researcher():
    """检查教研员账号，如果不存在则创建"""
    async with AsyncSessionLocal() as db:
        # 检查是否已有教研员
        result = await db.execute(select(User).where(User.role == UserRole.RESEARCHER))
        researchers = result.scalars().all()
        
        if researchers:
            print('✅ 已有教研员账号:')
            for r in researchers:
                print(f'  - ID: {r.id}')
                print(f'  - 用户名: {r.username}')
                print(f'  - 邮箱: {r.email}')
                print(f'  - 激活状态: {r.is_active}')
                print(f'  - 创建时间: {r.created_at}')
                print()
        else:
            print('❌ 未找到教研员账号，正在创建...')
            
            # 创建教研员账号
            researcher = User(
                username='researcher',
                email='researcher@inspireed.com',
                hashed_password=get_password_hash('password123'),
                role=UserRole.RESEARCHER,
                is_active=True
            )
            
            db.add(researcher)
            await db.commit()
            await db.refresh(researcher)
            
            print('✅ 教研员账号创建成功!')
            print(f'  - 用户名: researcher')
            print(f'  - 密码: password123')
            print(f'  - 邮箱: researcher@inspireed.com')
            print(f'  - ID: {researcher.id}')


if __name__ == '__main__':
    asyncio.run(check_and_create_researcher())

