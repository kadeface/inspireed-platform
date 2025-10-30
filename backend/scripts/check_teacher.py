"""
检查和创建教师账号
"""
import asyncio
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.user import User, UserRole
from app.core.security import get_password_hash


async def check_and_create_teacher():
    """检查教师账号，如果不存在则创建"""
    async with AsyncSessionLocal() as db:
        # 通过邮箱检查是否已有教师账号
        result = await db.execute(select(User).where(User.email == 'teacher@inspireed.com'))
        teacher = result.scalar_one_or_none()
        
        if teacher:
            print('✅ 教师账号已存在:')
            print(f'  - ID: {teacher.id}')
            print(f'  - 用户名: {teacher.username}')
            print(f'  - 邮箱: {teacher.email}')
            print(f'  - 角色: {teacher.role}')
            print(f'  - 激活状态: {teacher.is_active}')
            print(f'  - 创建时间: {teacher.created_at}')
            print()
            print('🔑 登录信息:')
            print(f'  - 邮箱: teacher@inspireed.com')
            print(f'  - 密码: teacher123 (请确认密码是否正确)')
        else:
            print('❌ 未找到教师账号，正在创建...')
            
            # 创建教师账号
            teacher = User(
                username='teacher',
                email='teacher@inspireed.com',
                full_name='测试教师',
                hashed_password=get_password_hash('teacher123'),
                role=UserRole.TEACHER,
                is_active=True
            )
            
            db.add(teacher)
            await db.commit()
            await db.refresh(teacher)
            
            print('✅ 教师账号创建成功!')
            print(f'  - 用户名: teacher')
            print(f'  - 密码: teacher123')
            print(f'  - 邮箱: teacher@inspireed.com')
            print(f'  - ID: {teacher.id}')
            print(f'  - 角色: {teacher.role}')


if __name__ == '__main__':
    asyncio.run(check_and_create_teacher())

