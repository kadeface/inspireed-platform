"""
管理员用户管理 API
提供用户账号的增删改查、状态管理、密码重置等功能
"""

from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr
from datetime import datetime

from app.core.database import get_db
from app.models import User, UserRole
from app.api.deps import get_current_admin
from app.core.security import get_password_hash
from app.core.config import settings
import secrets
import string


router = APIRouter()


# ==================== Request/Response Models ====================


class UserCreate(BaseModel):
    """创建用户请求"""

    username: str
    email: EmailStr
    password: str
    role: UserRole
    is_active: bool = True


class UserUpdate(BaseModel):
    """更新用户请求"""

    username: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


class UserResponse(BaseModel):
    """用户响应"""

    id: int
    username: str
    email: str
    role: UserRole
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None

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


# ==================== Endpoints ====================


@router.get("/", response_model=UserListResponse)
async def get_users(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=100, description="每页数量"),
    role: Optional[UserRole] = Query(None, description="角色筛选"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Any:
    """获取用户列表"""

    # 构建查询
    query = select(User)

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
        users=[UserResponse.model_validate(user) for user in users],
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

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    return UserResponse.model_validate(user)


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
    user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
        role=user_data.role,
        is_active=user_data.is_active,
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    return UserResponse.model_validate(user)


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
    for field, value in update_data.items():
        setattr(user, field, value)

    await db.commit()
    await db.refresh(user)

    return UserResponse.model_validate(user)


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

    user.is_active = not user.is_active
    await db.commit()

    return {"message": f"用户已{'启用' if user.is_active else '禁用'}", "is_active": user.is_active}


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
    user.hashed_password = get_password_hash(new_password)

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

    created_users = []
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
            user = User(
                username=user_data.username,
                email=user_data.email,
                hashed_password=hashed_password,
                role=user_data.role,
                is_active=user_data.is_active,
            )

            db.add(user)
            await db.flush()  # 获取ID但不提交
            created_users.append(UserResponse.model_validate(user))

        except Exception as e:
            errors.append(f"第{i+1}行：{str(e)}")

    await db.commit()

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

    # 返回CSV模板内容
    template_content = "username,email,password,role,is_active\n"
    template_content += "user1,user1@example.com,password123,teacher,true\n"
    template_content += "user2,user2@example.com,password123,student,true\n"

    return {
        "template": template_content,
        "filename": "user_import_template.csv",
        "note": "请按照模板格式填写用户信息，role可选值：admin, researcher, teacher, student",
    }
