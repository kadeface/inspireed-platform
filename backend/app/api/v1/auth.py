"""
认证API路由
"""

from datetime import datetime, timedelta
from typing import Any, List, Optional, Tuple, cast

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from sqlalchemy import or_, select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.security import create_access_token, verify_password, get_password_hash
from app.models import User
from app.models.organization import Region, School
from app.models.user import UserRole
from app.schemas.user import (
    RegisterRegionOption,
    RegisterSchoolOption,
    TeacherRegisterRequest,
    UserResponse,
)
from app.schemas.token import Token
from app.services.school_import_service import SchoolImportService

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

INACTIVE_USER_MESSAGE = "账号审核中或未激活，请联系平台管理员"


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
        user_id = payload.get("sub")
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

    if not cast(bool, user.is_active):
        raise HTTPException(status_code=400, detail=INACTIVE_USER_MESSAGE)

    # 预先填充组织信息，方便序列化
    user.region_name = user.region.name if user.region else None  # type: ignore[attr-defined]
    user.school_name = user.school.name if user.school else None  # type: ignore[attr-defined]
    user.grade_name = user.grade.name if user.grade else None  # type: ignore[attr-defined]

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """获取当前活跃用户"""
    if not cast(bool, current_user.is_active):
        raise HTTPException(status_code=400, detail=INACTIVE_USER_MESSAGE)
    return current_user


async def _resolve_registration_school(
    db: AsyncSession,
    *,
    school_id: Optional[int],
    school_name: Optional[str],
    region_id: Optional[int],
) -> Tuple[int, int]:
    """解析注册时的学校，返回 (school_id, region_id)"""
    if school_id is not None:
        result = await db.execute(
            select(School).where(School.id == school_id, School.is_active == True)  # noqa: E712
        )
        school = result.scalar_one_or_none()
        if not school:
            raise HTTPException(status_code=400, detail="所选学校不存在或已停用")
        return int(school.id), int(school.region_id)  # type: ignore[arg-type]

    assert school_name is not None
    normalized_name = school_name.strip()

    exact_result = await db.execute(
        select(School).where(
            School.name == normalized_name,
            School.is_active == True,  # noqa: E712
        )
    )
    exact_matches = exact_result.scalars().all()
    if len(exact_matches) == 1:
        school = exact_matches[0]
        return int(school.id), int(school.region_id)  # type: ignore[arg-type]
    if len(exact_matches) > 1:
        if region_id is None:
            raise HTTPException(
                status_code=400,
                detail="存在多个同名学校，请选择所属区域",
            )
        region_result = await db.execute(
            select(School).where(
                School.name == normalized_name,
                School.region_id == region_id,
                School.is_active == True,  # noqa: E712
            )
        )
        school = region_result.scalar_one_or_none()
        if school:
            return int(school.id), int(school.region_id)  # type: ignore[arg-type]

    if region_id is None:
        fuzzy_result = await db.execute(
            select(School).where(
                School.name.ilike(f"%{normalized_name}%"),
                School.is_active == True,  # noqa: E712
            )
        )
        fuzzy_matches = fuzzy_result.scalars().all()
        if len(fuzzy_matches) == 1:
            school = fuzzy_matches[0]
            return int(school.id), int(school.region_id)  # type: ignore[arg-type]
        raise HTTPException(status_code=400, detail="请选择所属区域")

    region = await db.scalar(select(Region).where(Region.id == region_id, Region.is_active == True))  # noqa: E712
    if not region:
        raise HTTPException(status_code=400, detail="所选区域不存在或已停用")

    school, _operation = await SchoolImportService.find_or_create_school(
        db,
        {"school_name": normalized_name},
        region_id,
    )
    if school is None:
        raise HTTPException(status_code=400, detail="无法创建学校，请重试")

    return int(school.id), int(school.region_id)  # type: ignore[arg-type]


@router.get("/register/schools", response_model=List[RegisterSchoolOption])
async def list_register_schools(
    search: Optional[str] = Query(None, description="学校名称搜索"),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """获取注册页可选学校列表（公开）"""
    query = (
        select(School)
        .options(selectinload(School.region))
        .where(School.is_active == True)  # noqa: E712
        .order_by(School.name)
        .limit(50)
    )
    if search and search.strip():
        keyword = search.strip()
        query = query.where(
            or_(
                School.name.ilike(f"%{keyword}%"),
                School.code.ilike(f"%{keyword}%"),
            )
        )

    result = await db.execute(query)
    schools = result.scalars().all()
    return [
        RegisterSchoolOption(
            id=int(school.id),  # type: ignore[arg-type]
            name=str(school.name),
            region_name=school.region.name if school.region else None,
        )
        for school in schools
    ]


@router.get("/register/regions", response_model=List[RegisterRegionOption])
async def list_register_regions(
    db: AsyncSession = Depends(get_db),
) -> Any:
    """获取注册页可选区域列表（公开）"""
    result = await db.execute(
        select(Region)
        .where(Region.is_active == True)  # noqa: E712
        .order_by(Region.level, Region.name)
    )
    regions = result.scalars().all()
    return [
        RegisterRegionOption(
            id=int(region.id),  # type: ignore[arg-type]
            name=str(region.name),
            level=int(region.level),  # type: ignore[arg-type]
        )
        for region in regions
    ]


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def register(
    user_in: TeacherRegisterRequest, db: AsyncSession = Depends(get_db)
) -> Any:
    """教师公开注册"""
    result = await db.execute(select(User).where(User.email == user_in.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="该邮箱已被注册")

    result = await db.execute(select(User).where(User.username == user_in.username))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="该用户名已被使用")

    resolved_school_id, resolved_region_id = await _resolve_registration_school(
        db,
        school_id=user_in.school_id,
        school_name=user_in.school_name,
        region_id=user_in.region_id,
    )

    user = User(
        email=user_in.email,
        username=user_in.username,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name,
        role=UserRole.TEACHER,
        school_id=resolved_school_id,
        region_id=resolved_region_id,
        is_active=False,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    return user


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
) -> Any:
    """用户登录"""
    import traceback

    try:
        result = await db.execute(
            select(User).where(
                (User.email == form_data.username) | (User.username == form_data.username)
            )
        )
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误",
                headers={"WWW-Authenticate": "Bearer"},
            )

        try:
            password_valid = verify_password(form_data.password, cast(str, user.hashed_password))
        except Exception as e:
            print(f"❌ 密码验证错误: {type(e).__name__}: {e}")
            print(traceback.format_exc())
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"密码验证失败: {str(e)}",
            )

        if not password_valid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误",
                headers={"WWW-Authenticate": "Bearer"},
            )

        is_active = cast(bool, user.is_active)
        if not is_active:
            raise HTTPException(status_code=400, detail=INACTIVE_USER_MESSAGE)

        try:
            user.last_login = datetime.utcnow()  # type: ignore[assignment]
            await db.commit()
        except Exception as e:
            print(f"⚠️ 更新最后登录时间失败: {e}")

        try:
            access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(
                subject=user.id, expires_delta=access_token_expires
            )
        except Exception as e:
            print(f"❌ 创建访问令牌错误: {type(e).__name__}: {e}")
            print(traceback.format_exc())
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"创建访问令牌失败: {str(e)}",
            )

        return {"access_token": access_token, "token_type": "bearer"}
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ 登录过程发生未预期的错误: {type(e).__name__}: {e}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"登录失败: {str(e)}",
        )


@router.get("/me", response_model=UserResponse)
async def read_users_me(
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """获取当前用户信息"""
    return current_user
