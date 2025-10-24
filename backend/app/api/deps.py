"""
API 依赖函数
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.models import User, UserRole

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """获取当前用户"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    result = await db.execute(select(User).where(User.id == int(user_id)))
    user = result.scalar_one_or_none()
    
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(status_code=400, detail="用户未激活")
    
    return user


def get_current_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """验证当前用户是否为管理员"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=403,
            detail="需要管理员权限"
        )
    return current_user


def get_current_teacher(
    current_user: User = Depends(get_current_user)
) -> User:
    """验证当前用户是否为教师"""
    if current_user.role not in [UserRole.TEACHER, UserRole.ADMIN]:
        raise HTTPException(
            status_code=403,
            detail="需要教师权限"
        )
    return current_user


def get_current_researcher(
    current_user: User = Depends(get_current_user)
) -> User:
    """验证当前用户是否为教研员"""
    if current_user.role != UserRole.RESEARCHER:
        raise HTTPException(
            status_code=403,
            detail="需要教研员权限"
        )
    return current_user


def get_current_student(
    current_user: User = Depends(get_current_user)
) -> User:
    """验证当前用户是否为学生"""
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(
            status_code=403,
            detail="需要学生权限"
        )
    return current_user


# 别名，方便使用
get_current_active_user = get_current_user
require_admin = get_current_admin
require_teacher = get_current_teacher
require_researcher = get_current_researcher
require_student = get_current_student

