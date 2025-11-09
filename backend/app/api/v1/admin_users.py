"""
管理员用户管理 API
提供用户账号的增删改查、状态管理、密码重置等功能
"""

from typing import Any, List, Optional, cast
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr, field_validator
from datetime import datetime

from app.core.database import get_db
from app.core.validators import normalize_user_role
from app.models import User, UserRole, Region, School, Grade, Classroom
from app.api.deps import get_current_admin
from app.core.security import get_password_hash
from app.core.config import settings
import secrets
import string
from sqlalchemy.orm import selectinload


router = APIRouter()


# ==================== Request/Response Models ====================


class UserCreate(BaseModel):
    """创建用户请求"""

    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    role: UserRole
    is_active: bool = True
    region_id: Optional[int] = None
    school_id: Optional[int] = None
    grade_id: Optional[int] = None
    classroom_id: Optional[int] = None

    @field_validator("role", mode="before")
    @classmethod
    def normalize_role(cls, value: object) -> UserRole:
        normalized = normalize_user_role(value)
        if normalized is None:
            raise ValueError("用户角色不能为空")
        return normalized


class UserUpdate(BaseModel):
    """更新用户请求"""

    username: Optional[str] = None
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    region_id: Optional[int] = None
    school_id: Optional[int] = None
    grade_id: Optional[int] = None
    classroom_id: Optional[int] = None

    @field_validator("role", mode="before")
    @classmethod
    def normalize_role(cls, value: object) -> Optional[UserRole]:
        normalized = normalize_user_role(value, allow_none=True)
        return normalized


class UserResponse(BaseModel):
    """用户响应"""

    id: int
    username: str
    email: str
    full_name: Optional[str] = None
    role: UserRole
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    region_id: Optional[int] = None
    school_id: Optional[int] = None
    grade_id: Optional[int] = None
    classroom_id: Optional[int] = None
    region_name: Optional[str] = None
    school_name: Optional[str] = None
    grade_name: Optional[str] = None
    classroom_name: Optional[str] = None

    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    """用户列表响应"""

    users: List[UserResponse]
    total: int
    page: int
    size: int
    total_pages: int


class PasswordResetRequest(BaseModel):
    """密码重置请求"""

    user_id: int


class BatchImportRequest(BaseModel):
    """批量导入请求"""

    users: List[UserCreate]


def _user_with_relations_query():
    return select(User).options(
        selectinload(User.region),
        selectinload(User.school),
        selectinload(User.grade),
        selectinload(User.classroom),
    )


async def _fetch_user_with_relations(db: AsyncSession, user_id: int) -> Optional[User]:
    result = await db.execute(_user_with_relations_query().where(User.id == user_id))
    return result.scalar_one_or_none()


def _serialize_user(user: User) -> UserResponse:
    return UserResponse.model_validate(user)


async def _validate_scope_ids(
    db: AsyncSession,
    *,
    region_id: Optional[int] = None,
    school_id: Optional[int] = None,
    grade_id: Optional[int] = None,
    classroom_id: Optional[int] = None,
) -> dict:
    """验证并整理区域/学校/年级/班级信息"""

    resolved: dict[str, Optional[int]] = {
        "region_id": region_id,
        "school_id": school_id,
        "grade_id": grade_id,
        "classroom_id": classroom_id,
    }

    school_obj: Optional[School] = None

    if classroom_id is not None:
        classroom = await db.scalar(select(Classroom).where(Classroom.id == classroom_id))
        if not classroom:
            raise HTTPException(status_code=404, detail="班级不存在")

        resolved["classroom_id"] = cast(int, classroom.id)
        resolved["grade_id"] = cast(Optional[int], classroom.grade_id)
        resolved["school_id"] = cast(Optional[int], classroom.school_id)
        school_obj = await db.scalar(select(School).where(School.id == classroom.school_id))

    if resolved["grade_id"] is not None:
        grade = await db.scalar(select(Grade).where(Grade.id == resolved["grade_id"]))
        if not grade:
            raise HTTPException(status_code=404, detail="年级不存在")

    if resolved["school_id"] is not None:
        school_obj = school_obj or await db.scalar(
            select(School).where(School.id == resolved["school_id"])
        )
        if not school_obj:
            raise HTTPException(status_code=404, detail="学校不存在")
        resolved["school_id"] = cast(Optional[int], school_obj.id)

        if resolved["region_id"] is None:
            resolved["region_id"] = cast(Optional[int], school_obj.region_id)
        elif resolved["region_id"] != cast(Optional[int], school_obj.region_id):
            raise HTTPException(status_code=400, detail="学校与区域不匹配")

    if resolved["region_id"] is not None:
        region = await db.scalar(select(Region).where(Region.id == resolved["region_id"]))
        if not region:
            raise HTTPException(status_code=404, detail="区域不存在")

    return resolved


# ==================== Endpoints ====================


@router.get("/", response_model=UserListResponse)
async def get_users(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=1000, description="每页数量"),
    role: Optional[UserRole] = Query(None, description="角色筛选"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Any:
    """获取用户列表"""

    # 构建查询
    query = _user_with_relations_query()

    # 角色筛选
    if role:
        query = query.where(User.role == role)

    # 搜索筛选
    if search:
        search_filter = or_(User.username.ilike(f"%{search}%"), User.email.ilike(f"%{search}%"))
        query = query.where(search_filter)

    # 获取总数
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # 分页查询
    offset = (page - 1) * size
    query = query.offset(offset).limit(size).order_by(User.created_at.desc())

    result = await db.execute(query)
    users = result.scalars().all()

    total_pages = (total + size - 1) // size

    return UserListResponse(
        users=[_serialize_user(user) for user in users],
        total=total,
        page=page,
        size=size,
        total_pages=total_pages,
    )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Any:
    """获取用户详情"""

    user = await _fetch_user_with_relations(db, user_id)

    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    return _serialize_user(user)


@router.post("/", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Any:
    """创建用户"""

    # 检查用户名是否已存在
    existing_user = await db.execute(select(User).where(User.username == user_data.username))
    if existing_user.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="用户名已存在")

    # 检查邮箱是否已存在
    existing_email = await db.execute(select(User).where(User.email == user_data.email))
    if existing_email.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="邮箱已存在")

    # 创建用户
    hashed_password = get_password_hash(user_data.password)
    scope_ids = await _validate_scope_ids(
        db,
        region_id=user_data.region_id,
        school_id=user_data.school_id,
        grade_id=user_data.grade_id,
        classroom_id=user_data.classroom_id,
    )
    user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
        role=user_data.role,
        is_active=user_data.is_active,
        **scope_ids,
    )

    db.add(user)
    await db.commit()

    refreshed_user = await _fetch_user_with_relations(db, cast(int, user.id))
    if refreshed_user is None:
        raise HTTPException(status_code=404, detail="用户不存在")

    return _serialize_user(refreshed_user)


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Any:
    """更新用户"""

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 检查用户名是否已被其他用户使用
    if user_data.username and user_data.username != user.username:
        existing_user = await db.execute(
            select(User).where(User.username == user_data.username, User.id != user_id)
        )
        if existing_user.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="用户名已存在")

    # 检查邮箱是否已被其他用户使用
    if user_data.email and user_data.email != user.email:
        existing_email = await db.execute(
            select(User).where(User.email == user_data.email, User.id != user_id)
        )
        if existing_email.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="邮箱已存在")

    # 更新用户信息
    update_data = user_data.model_dump(exclude_unset=True)
    scope_fields = {"region_id", "school_id", "grade_id", "classroom_id"}

    if any(field in update_data for field in scope_fields):
        scope_kwargs = {
            field: update_data.get(field, getattr(user, field)) for field in scope_fields
        }
        resolved_scope = await _validate_scope_ids(db, **scope_kwargs)
        for field, value in resolved_scope.items():
            setattr(user, field, value)
        for field in scope_fields:
            update_data.pop(field, None)

    for field, value in update_data.items():
        setattr(user, field, value)

    await db.commit()

    refreshed_user = await _fetch_user_with_relations(db, cast(int, user.id))
    if refreshed_user is None:
        raise HTTPException(status_code=404, detail="用户不存在")

    return _serialize_user(refreshed_user)


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Any:
    """删除用户"""

    # 不能删除自己
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="不能删除自己的账号")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    await db.delete(user)
    await db.commit()

    return {"message": "用户删除成功"}


@router.patch("/{user_id}/toggle-status")
async def toggle_user_status(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Any:
    """切换用户状态（激活/禁用）"""

    # 不能禁用自己
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="不能禁用自己的账号")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    current_status = bool(getattr(user, "is_active"))
    setattr(user, "is_active", not current_status)
    await db.commit()

    updated_status = bool(getattr(user, "is_active"))
    return {"message": f"用户已{'启用' if updated_status else '禁用'}", "is_active": updated_status}


@router.post("/{user_id}/reset-password")
async def reset_user_password(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Any:
    """重置用户密码"""

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 生成新密码（8位随机密码，包含字母和数字）
    alphabet = string.ascii_letters + string.digits
    new_password = "".join(secrets.choice(alphabet) for _ in range(8))
    setattr(user, "hashed_password", get_password_hash(new_password))

    await db.commit()

    # TODO: 发送邮件通知用户新密码
    # 这里应该发送邮件，暂时返回密码用于测试

    return {
        "message": "密码重置成功",
        "new_password": new_password,  # 生产环境中不应该返回密码
        "note": "请通过邮件或安全渠道告知用户新密码",
    }


@router.post("/batch-import")
async def batch_import_users(
    import_data: BatchImportRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Any:
    """批量导入用户"""

    created_user_ids: list[int] = []
    errors = []

    for i, user_data in enumerate(import_data.users):
        try:
            # 检查用户名是否已存在
            existing_user = await db.execute(
                select(User).where(User.username == user_data.username)
            )
            if existing_user.scalar_one_or_none():
                errors.append(f"第{i+1}行：用户名 {user_data.username} 已存在")
                continue

            # 检查邮箱是否已存在
            existing_email = await db.execute(select(User).where(User.email == user_data.email))
            if existing_email.scalar_one_or_none():
                errors.append(f"第{i+1}行：邮箱 {user_data.email} 已存在")
                continue

            # 创建用户
            hashed_password = get_password_hash(user_data.password)
            scope_ids = await _validate_scope_ids(
                db,
                region_id=user_data.region_id,
                school_id=user_data.school_id,
                grade_id=user_data.grade_id,
                classroom_id=user_data.classroom_id,
            )
            user = User(
                username=user_data.username,
                email=user_data.email,
                hashed_password=hashed_password,
                full_name=user_data.full_name,
                role=user_data.role,
                is_active=user_data.is_active,
                **scope_ids,
            )

            db.add(user)
            await db.flush()  # 获取ID但不提交
            created_user_ids.append(cast(int, user.id))

        except HTTPException as exc:
            errors.append(f"第{i+1}行：{exc.detail}")
        except Exception as e:
            errors.append(f"第{i+1}行：{str(e)}")

    await db.commit()

    created_users: list[UserResponse] = []
    if created_user_ids:
        result = await db.execute(
            _user_with_relations_query().where(User.id.in_(created_user_ids))
        )
        created_user_objs = result.scalars().all()
        # 按创建顺序排序
        created_users_map: dict[int, User] = {
            cast(int, user.id): user for user in created_user_objs if user.id is not None
        }
        for user_id in created_user_ids:
            user_obj = created_users_map.get(user_id)
            if user_obj:
                created_users.append(_serialize_user(user_obj))

    return {
        "message": f"批量导入完成，成功创建 {len(created_users)} 个用户",
        "created_users": created_users,
        "errors": errors,
        "success_count": len(created_users),
        "error_count": len(errors),
    }


@router.get("/export/template")
async def download_import_template(
    current_user: User = Depends(get_current_admin),
) -> Any:
    """下载批量导入模板"""

    # 返回CSV模板内容（中文字段，包含备注说明）
    template_content = (
        "学号/用户名,姓名,邮箱,密码,角色,是否激活,区域ID(可选),学校ID(可选),年级ID(可选),班级ID(可选),备注\n"
    )
    template_content += (
        "202301001,张慧,student01@example.com,student123,学生,是,1,101,3,1001,学生账户请填写学号作为登录名\n"
    )
    template_content += (
        "teacher01,李老师,teacher01@example.com,teacher123,教师,是,,,,,教师/管理员可留空组织信息\n"
    )

    return {
        "template": template_content,
        "filename": "user_import_template.csv",
        "note": (
            "请按照模板格式填写用户信息，角色支持：管理员、教研员、教师、学生（或对应英文缩写）；"
            "学生账号的“学号/用户名”需使用学号；“是否激活”可填写 是/否 或 true/false；"
            "组织信息字段可留空，若填写请使用系统中的数值ID。"
        ),
    }
