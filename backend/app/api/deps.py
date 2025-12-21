"""
API 依赖函数
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.core.database import get_db
from app.models import User, UserRole, ClassroomMembership, RoleInClass, Classroom

from typing import Optional, cast, List

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")
oauth2_scheme_optional = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login", auto_error=False
)


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
) -> User:
    """获取当前用户"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id: Optional[str] = payload.get("sub")
        if not isinstance(user_id, str):
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    result = await db.execute(
        select(User)
        .options(
            selectinload(User.region),
            selectinload(User.school),
            selectinload(User.grade),
        )
        .where(User.id == int(user_id))
    )
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception

    if not isinstance(user.is_active, bool) or not cast(bool, user.is_active):
        raise HTTPException(status_code=400, detail="用户未激活")

    user.region_name = user.region.name if user.region else None  # type: ignore[attr-defined]
    user.school_name = user.school.name if user.school else None  # type: ignore[attr-defined]
    user.grade_name = user.grade.name if user.grade else None  # type: ignore[attr-defined]

    return user


async def get_current_user_optional(
    token: Optional[str] = Depends(oauth2_scheme_optional),
    db: AsyncSession = Depends(get_db),
) -> Optional[User]:
    """获取当前用户（可选，不强制认证）"""
    if token is None:
        return None

    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id: Optional[str] = payload.get("sub")
        if not isinstance(user_id, str):
            return None
    except JWTError:
        return None

    result = await db.execute(
        select(User)
        .options(
            selectinload(User.region),
            selectinload(User.school),
            selectinload(User.grade),
        )
        .where(User.id == int(user_id))
    )
    user = result.scalar_one_or_none()

    if (
        user is None
        or not isinstance(user.is_active, bool)
        or not cast(bool, user.is_active)
    ):
        return None

    user.region_name = user.region.name if user.region else None  # type: ignore[attr-defined]
    user.school_name = user.school.name if user.school else None  # type: ignore[attr-defined]
    user.grade_name = user.grade.name if user.grade else None  # type: ignore[attr-defined]

    return user


def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    """验证当前用户是否为管理员"""
    if (
        not isinstance(current_user.role, UserRole)
        or cast(UserRole, current_user.role) != UserRole.ADMIN
    ):
        raise HTTPException(status_code=403, detail="需要管理员权限")
    return current_user


def get_current_teacher(current_user: User = Depends(get_current_user)) -> User:
    """验证当前用户是否为教师"""
    if not isinstance(current_user.role, UserRole) or cast(
        UserRole, current_user.role
    ) not in [UserRole.TEACHER, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="需要教师权限")
    return current_user


def get_current_researcher(current_user: User = Depends(get_current_user)) -> User:
    """验证当前用户是否为教研员"""
    if (
        not isinstance(current_user.role, UserRole)
        or cast(UserRole, current_user.role) != UserRole.RESEARCHER
    ):
        raise HTTPException(status_code=403, detail="需要教研员权限")
    return current_user


def get_current_student(current_user: User = Depends(get_current_user)) -> User:
    """验证当前用户是否为学生"""
    if (
        not isinstance(current_user.role, UserRole)
        or cast(UserRole, current_user.role) != UserRole.STUDENT
    ):
        raise HTTPException(status_code=403, detail="需要学生权限")
    return current_user


async def get_current_user_from_token(
    token: str,
    db: AsyncSession,
) -> Optional[User]:
    """从 JWT Token 获取当前用户（用于 WebSocket 认证）"""
    
    try:
        # 解码 Token
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        
        user_id: Optional[str] = payload.get("sub")
        if user_id is None:
            return None
        
        # 查询用户
        result = await db.execute(
            select(User)
            .options(
                selectinload(User.region),
                selectinload(User.school),
                selectinload(User.grade),
            )
            .where(User.id == int(user_id))
        )
        user = result.scalar_one_or_none()
        
        if user is None:
            return None
        
        if not isinstance(user.is_active, bool) or not cast(bool, user.is_active):
            return None
        
        user.region_name = user.region.name if user.region else None  # type: ignore[attr-defined]
        user.school_name = user.school.name if user.school else None  # type: ignore[attr-defined]
        user.grade_name = user.grade.name if user.grade else None  # type: ignore[attr-defined]
        
        return user
    
    except JWTError:
        return None


# 别名，方便使用
get_current_active_user = get_current_user
require_admin = get_current_admin
require_teacher = get_current_teacher
require_researcher = get_current_researcher
require_student = get_current_student


async def get_classroom_membership(
    db: AsyncSession,
    user_id: int,
    classroom_id: int,
) -> Optional[ClassroomMembership]:
    """获取用户在指定班级的成员关系"""
    result = await db.execute(
        select(ClassroomMembership).where(
            ClassroomMembership.user_id == user_id,
            ClassroomMembership.classroom_id == classroom_id,
            ClassroomMembership.is_active == True,
        )
    )
    return result.scalar_one_or_none()


async def check_classroom_permission(
    db: AsyncSession,
    current_user: User,
    classroom_id: int,
    allowed_roles: List[RoleInClass],
) -> ClassroomMembership:
    """
    检查用户在班级中的权限
    
    Args:
        db: 数据库会话
        current_user: 当前用户
        classroom_id: 班级ID
        allowed_roles: 允许的角色列表
    
    Returns:
        ClassroomMembership: 成员关系对象
    
    Raises:
        HTTPException: 如果无权限或班级不存在
    """
    # 检查班级是否存在
    classroom = await db.get(Classroom, classroom_id)
    if not classroom:
        raise HTTPException(status_code=404, detail="班级不存在")
    
    # Admin 全通 - 管理员可以访问所有班级
    # 注意：这里管理员如果没有成员关系会继续执行下面的检查，导致403
    # 如果需要管理员全通，建议在具体的API端点中单独处理管理员权限
    # （例如 get_classroom_members 端点已经做了特殊处理）
    if isinstance(current_user.role, UserRole) and cast(UserRole, current_user.role) == UserRole.ADMIN:
        # 尝试获取成员关系，如果有则返回
        membership = await get_classroom_membership(db, cast(int, current_user.id), classroom_id)
        if membership:
            return membership
        # 对于管理员，如果没有成员关系，由具体API端点决定是否允许访问
        # 这里继续执行下面的检查，可能会抛出403，但这样可以保证安全性
    
    # 检查成员关系
    membership = await get_classroom_membership(db, cast(int, current_user.id), classroom_id)
    if not membership:
        raise HTTPException(
            status_code=403, detail="您不是该班级的成员"
        )
    
    # 检查角色权限
    if membership.role_in_class not in allowed_roles:
        role_names = ", ".join([role.value for role in allowed_roles])
        raise HTTPException(
            status_code=403,
            detail=f"需要以下角色之一：{role_names}，您当前角色：{membership.role_in_class.value}",
        )
    
    return membership


async def require_classroom_management_permission(
    classroom_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ClassroomMembership:
    """
    要求班级管理权限（点名/纪律/正面行为录入）
    允许角色：head_teacher_primary, head_teacher_deputy, subject_teacher, cadre
    """
    return await check_classroom_permission(
        db,
        current_user,
        classroom_id,
        [
            RoleInClass.HEAD_TEACHER_PRIMARY,
            RoleInClass.HEAD_TEACHER_DEPUTY,
            RoleInClass.SUBJECT_TEACHER,
            RoleInClass.CADRE,
        ],
    )


async def require_classroom_duty_setting_permission(
    classroom_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ClassroomMembership:
    """
    要求值日设置权限
    允许角色：head_teacher_primary, head_teacher_deputy, cadre
    """
    return await check_classroom_permission(
        db,
        current_user,
        classroom_id,
        [
            RoleInClass.HEAD_TEACHER_PRIMARY,
            RoleInClass.HEAD_TEACHER_DEPUTY,
            RoleInClass.CADRE,
        ],
    )


async def require_classroom_member(
    classroom_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ClassroomMembership:
    """
    要求是班级成员（任意角色）
    """
    return await check_classroom_permission(
        db,
        current_user,
        classroom_id,
        [
            RoleInClass.HEAD_TEACHER_PRIMARY,
            RoleInClass.HEAD_TEACHER_DEPUTY,
            RoleInClass.SUBJECT_TEACHER,
            RoleInClass.CADRE,
            RoleInClass.STUDENT,
        ],
    )
