"""
班级匹配工具函数
统一处理用户班级关联的查询逻辑
"""

from typing import Set, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.models.user import User
from app.models.classroom_assistant import ClassroomMembership


async def get_user_classroom_ids(
    db: AsyncSession,
    user: User,
    include_inactive: bool = False
) -> Set[int]:
    """
    获取用户所属的所有班级ID（统一接口）
    
    优先从 ClassroomMembership 获取，如果没有则从 User.classroom_id 获取（向后兼容）
    
    Args:
        db: 数据库会话
        user: 用户对象
        include_inactive: 是否包含非活跃的成员关系
    
    Returns:
        班级ID集合
    """
    classroom_ids = set()
    
    # 优先从 ClassroomMembership 获取（支持多班级）
    query = select(ClassroomMembership).where(
        ClassroomMembership.user_id == user.id
    )
    if not include_inactive:
        query = query.where(ClassroomMembership.is_active == True)
    
    result = await db.execute(query)
    memberships = result.scalars().all()
    
    if memberships:
        # 如果有 ClassroomMembership 记录，使用它们
        for membership in memberships:
            classroom_ids.add(membership.classroom_id)
    elif user.classroom_id:
        # 如果没有 ClassroomMembership，使用 User.classroom_id（向后兼容）
        # 这种情况应该通过数据迁移逐步消除
        classroom_ids.add(user.classroom_id)
    
    return classroom_ids


async def check_user_in_classroom(
    db: AsyncSession,
    user: User,
    classroom_id: int,
    include_inactive: bool = False
) -> bool:
    """
    检查用户是否属于指定班级
    
    Args:
        db: 数据库会话
        user: 用户对象
        classroom_id: 班级ID
        include_inactive: 是否包含非活跃的成员关系
    
    Returns:
        是否属于该班级
    """
    classroom_ids = await get_user_classroom_ids(db, user, include_inactive)
    return classroom_id in classroom_ids


async def get_user_primary_classroom_id(
    db: AsyncSession,
    user: User
) -> Optional[int]:
    """
    获取用户的主班级ID
    
    优先从 ClassroomMembership 中查找 is_primary_class=True 的记录
    如果没有，则返回 User.classroom_id
    
    Args:
        db: 数据库会话
        user: 用户对象
    
    Returns:
        主班级ID，如果没有则返回 None
    """
    # 从 ClassroomMembership 查找主班级
    result = await db.execute(
        select(ClassroomMembership).where(
            and_(
                ClassroomMembership.user_id == user.id,
                ClassroomMembership.is_primary_class == True,
                ClassroomMembership.is_active == True
            )
        )
    )
    primary_membership = result.scalar_one_or_none()
    
    if primary_membership:
        return primary_membership.classroom_id
    
    # 如果没有主班级记录，返回 User.classroom_id（向后兼容）
    return user.classroom_id
