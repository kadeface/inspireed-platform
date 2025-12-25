"""
管理员用户管理 API
提供用户账号的增删改查、状态管理、密码重置等功能
"""

from typing import Any, List, Optional, cast
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr, Field, field_validator
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


class UnifiedImportItem(BaseModel):
    """统一导入项 - 支持创建用户和添加到班级"""
    
    # 用户标识字段（用于匹配已存在的用户）
    student_id_number: Optional[str] = Field(None, max_length=50, description="学籍号（唯一标识，推荐使用）")
    username: Optional[str] = Field(None, max_length=100, description="用户名/学号")
    email: Optional[str] = Field(None, max_length=255, description="邮箱")
    full_name: Optional[str] = Field(None, max_length=100, description="姓名")
    
    # 用户创建/更新字段
    password: Optional[str] = Field(None, min_length=6, max_length=50, description="密码（创建新用户时必需）")
    role: Optional[UserRole] = Field(None, description="用户角色")
    is_active: Optional[bool] = Field(True, description="是否激活")
    
    # 组织信息
    region_id: Optional[int] = Field(None, description="区域ID")
    school_id: Optional[int] = Field(None, description="学校ID")
    grade_id: Optional[int] = Field(None, description="年级ID")
    classroom_id: Optional[int] = Field(None, description="班级ID（如果提供，会自动将用户添加到班级）")
    
    # 班级成员信息（当提供classroom_id时使用）
    seat_no: Optional[int] = Field(None, description="座号")
    role_in_class: Optional[str] = Field(None, description="班级内角色：学生/正班主任/副班主任/任课教师/班干部")
    cadre_title: Optional[str] = Field(None, max_length=50, description="职务名称")
    is_primary_class: Optional[bool] = Field(False, description="是否为主班级")
    student_no: Optional[str] = Field(None, max_length=50, description="班级内的学号")
    
    @field_validator("role", mode="before")
    @classmethod
    def normalize_role(cls, value: object) -> Optional[UserRole]:
        if value is None:
            return None
        normalized = normalize_user_role(value, allow_none=True)
        return normalized


class UnifiedImportRequest(BaseModel):
    """统一导入请求 - 支持创建用户和添加到班级"""
    
    items: List[UnifiedImportItem]


class UnifiedImportResponse(BaseModel):
    """统一导入响应"""
    
    message: str
    created_users: List[UserResponse]
    added_members: List[dict]  # 添加到班级的成员信息
    errors: List[str]
    success_count: int
    error_count: int
    created_user_count: int
    added_member_count: int


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
    """Serialize user with related organization names."""
    return UserResponse(
        id=cast(int, user.id),
        username=cast(str, user.username),
        email=cast(str, user.email),
        full_name=cast(Optional[str], user.full_name),
        role=cast(UserRole, user.role),
        is_active=cast(bool, user.is_active),
        created_at=cast(datetime, user.created_at),
        last_login=cast(Optional[datetime], getattr(user, "last_login", None)),
        region_id=cast(Optional[int], user.region_id),
        school_id=cast(Optional[int], user.school_id),
        grade_id=cast(Optional[int], user.grade_id),
        classroom_id=cast(Optional[int], user.classroom_id),
        region_name=user.region.name if user.region else None,
        school_name=user.school.name if user.school else None,
        grade_name=user.grade.name if user.grade else None,
        classroom_name=user.classroom.name if user.classroom else None,
    )


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
        classroom = await db.scalar(
            select(Classroom).where(Classroom.id == classroom_id)
        )
        if not classroom:
            raise HTTPException(status_code=404, detail="班级不存在")

        resolved["classroom_id"] = cast(int, classroom.id)
        resolved["grade_id"] = cast(Optional[int], classroom.grade_id)
        resolved["school_id"] = cast(Optional[int], classroom.school_id)
        school_obj = await db.scalar(
            select(School).where(School.id == classroom.school_id)
        )

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
        region = await db.scalar(
            select(Region).where(Region.id == resolved["region_id"])
        )
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
        search_filter = or_(
            User.username.ilike(f"%{search}%"), User.email.ilike(f"%{search}%")
        )
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
    existing_user = await db.execute(
        select(User).where(User.username == user_data.username)
    )
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
    # 确保 is_active 有默认值，如果为 None 则设为 True
    is_active = user_data.is_active if user_data.is_active is not None else True
    user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
        role=user_data.role,
        is_active=is_active,
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
            field: update_data.get(field, getattr(user, field))
            for field in scope_fields
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
    return {
        "message": f"用户已{'启用' if updated_status else '禁用'}",
        "is_active": updated_status,
    }


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
            existing_email = await db.execute(
                select(User).where(User.email == user_data.email)
            )
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
            # 确保 is_active 有默认值，如果为 None 则设为 True
            is_active = user_data.is_active if user_data.is_active is not None else True
            user = User(
                username=user_data.username,
                email=user_data.email,
                hashed_password=hashed_password,
                full_name=user_data.full_name,
                role=user_data.role,
                is_active=is_active,
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
            cast(int, user.id): user
            for user in created_user_objs
            if user.id is not None
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
    template_content += "202301001,张慧,student01@example.com,student123,学生,是,1,101,3,1001,学生账户请填写学号作为登录名\n"
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


@router.get("/export/unified-template")
async def download_unified_import_template(
    current_user: User = Depends(get_current_admin),
) -> Any:
    """下载统一导入模板（支持创建用户和添加到班级）"""
    
    # 统一模板包含所有字段，添加详细的说明注释
    template_content = "# 统一数据导入模板\n"
    template_content += "# 说明：本模板支持一次导入完成用户创建和班级成员添加\n"
    template_content += "# \n"
    template_content += "# 【重要】组织架构ID获取方式：\n"
    template_content += "# \n"
    template_content += "# 1. 区域ID、学校ID、班级ID：\n"
    template_content += "#    访问路径：管理员后台 -> 组织架构管理\n"
    template_content += "#    在这些页面中，每个组织单位的ID会显示在列表中（通常在表格的第一列）\n"
    template_content += "#    班级ID说明：\n"
    template_content += "#      - 班级ID是数据库中的数字ID，需要在组织架构管理页面的班级列表中查看\n"
    template_content += "#      - 班级编码（code）格式为\"入学年份+班级编号\"，例如：202501（表示2025年入学的01班）\n"
    template_content += "#      - 导入时填写的是班级ID（数字），不是班级编码\n"
    template_content += "#      - 班级编码仅用于显示和识别，不能用作导入时的ID\n"
    template_content += "# \n"
    template_content += "# 2. 年级ID（重要说明）：\n"
    template_content += "#    方法一：访问 管理员后台 -> 课程管理 页面，在课程树结构中查看年级信息\n"
    template_content += "#    方法二：在组织架构管理 -> 创建/编辑班级时，年级下拉框中显示\"年级名称 (ID: 年级ID)\"格式\n"
    template_content += "#    方法三：系统标准年级ID对应关系（按顺序递增）：\n"
    template_content += "#            一年级→ID:1, 二年级→ID:2, 三年级→ID:3, 四年级→ID:4, 五年级→ID:5, 六年级→ID:6\n"
    template_content += "#            七年级→ID:7, 八年级→ID:8, 九年级→ID:9, 高一→ID:10, 高二→ID:11, 高三→ID:12, 未分类→ID:13\n"
    template_content += "#    提示：年级ID从1开始按顺序递增，与年级级别（level）基本一致\n"
    template_content += "# \n"
    template_content += "# 3. 如果组织架构尚未建立，请先到'组织架构管理'页面创建相应的区域、学校、班级\n"
    template_content += "#    注意：年级信息通常在课程系统中管理，而非组织架构管理中\n"
    template_content += "# \n"
    template_content += "# 4. 组织架构ID为数字，例如：区域ID=1, 学校ID=101, 年级ID=3, 班级ID=5（数据库数字ID）\n"
    template_content += "#    注意：班级ID是数据库中的数字ID（如：5），不是班级编码（如：202501）\n"
    template_content += "# 5. 这些字段为可选字段，如果用户不属于特定组织，可以留空\n"
    template_content += "# \n"
    template_content += "# 字段说明：\n"
    template_content += "# - 学籍号（推荐）：唯一标识，用于匹配已存在的用户，如果用户已存在则更新，不存在则创建\n"
    template_content += "# - 如果用户不存在，需要提供：学号/用户名、邮箱、密码\n"
    template_content += "# - 如果用户已存在，系统会根据学籍号/用户名/邮箱匹配并更新信息（密码可选）\n"
    template_content += "# - 如果提供了班级ID，系统会自动将用户添加到班级\n"
    template_content += "# - 角色可选值：管理员、教研员、教师、学生（或admin、researcher、teacher、student）\n"
    template_content += "# - 班级角色可选值：学生、正班主任、副班主任、任课教师、班干部\n"
    template_content += "# - 主班级：true/false，表示是否为主班级\n"
    template_content += "# - 是否激活：是/否 或 true/false\n"
    template_content += "# \n"
    template_content += "学籍号,学号/用户名,姓名,邮箱,密码,角色,是否激活,区域ID,学校ID,年级ID,班级ID,座号,班级角色,职务名称,主班级,班级学号\n"
    template_content += "2024001001,2024001,张三,zhangsan@example.com,123456,学生,是,1,101,3,5,1,学生,,true,2024001\n"
    template_content += ",teacher01,李老师,teacher01@example.com,123456,教师,是,1,101,,,,,任课教师,,,\n"
    
    return {
        "template": template_content,
        "filename": "unified_import_template.csv",
        "note": (
            "统一导入模板说明：\n\n"
            "【组织架构ID获取方式】\n"
            "区域ID、学校ID、年级ID、班级ID等组织架构ID可以通过以下方式获取：\n\n"
            "1. 区域ID、学校ID、班级ID：\n"
            "   访问路径：管理员后台 -> 组织架构管理页面\n"
            "   在组织架构管理页面中，每个组织单位的ID会显示在列表中（通常在表格的第一列）\n"
            "   班级ID说明：\n"
            "     - 班级ID是数据库中的数字ID，需要在组织架构管理页面的班级列表中查看\n"
            "     - 班级编码（code）格式为\"入学年份+班级编号\"，例如：202501（表示2025年入学的01班）\n"
            "     - 导入时填写的是班级ID（数字），不是班级编码\n"
            "     - 班级编码仅用于显示和识别，不能用作导入时的ID\n\n"
            "2. 年级ID（重要说明）：\n"
            "   方法一：访问 管理员后台 -> 课程管理 页面，在课程树结构中查看年级信息\n"
            "   方法二：在组织架构管理 -> 创建/编辑班级时，年级下拉框中显示\"年级名称 (ID: 年级ID)\"格式\n"
            "   方法三：系统标准年级ID对应关系（按顺序递增）：\n"
            "           一年级→ID:1, 二年级→ID:2, 三年级→ID:3, 四年级→ID:4, 五年级→ID:5, 六年级→ID:6\n"
            "           七年级→ID:7, 八年级→ID:8, 九年级→ID:9, 高一→ID:10, 高二→ID:11, 高三→ID:12, 未分类→ID:13\n"
            "   提示：年级ID从1开始按顺序递增，与年级级别（level）基本一致\n"
            "   注意：年级信息通常在课程系统中管理，而非组织架构管理中\n\n"
            "3. 如果组织架构尚未建立，请先到组织架构管理页面创建相应的区域、学校、班级\n"
            "4. 这些字段为可选字段，如果用户不属于特定组织，可以留空\n\n"
            "【字段说明】\n"
            "1. 学籍号（推荐）：唯一标识，用于匹配已存在的用户\n"
            "2. 如果用户不存在，系统会根据学号/用户名、邮箱、姓名创建新用户（需要提供密码）\n"
            "3. 如果用户已存在，系统会更新用户信息（密码可选）\n"
            "4. 如果提供了班级ID，系统会自动将用户添加到班级\n"
            "5. 角色可选值：管理员、教研员、教师、学生\n"
            "6. 班级角色可选值：学生、正班主任、副班主任、任课教师、班干部\n"
            "7. 主班级：true/false，表示是否为主班级\n"
            "8. 班级学号：班级内的学号，可能与学籍号不同"
        ),
    }


@router.post("/unified-import")
async def unified_import(
    import_data: UnifiedImportRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Any:
    """统一导入 - 支持创建用户和添加到班级"""
    
    from app.api.v1.classroom_assistant import find_user_by_identifiers
    from app.models.classroom_assistant import ClassroomMembership, RoleInClass
    
    created_users: List[UserResponse] = []
    added_members: List[dict] = []
    errors: List[str] = []
    
    for i, item in enumerate(import_data.items):
        try:
            # 1. 查找或创建用户
            user: Optional[User] = None
            
            # 尝试根据标识字段查找用户
            if item.student_id_number or item.username or item.email or item.full_name:
                user = await find_user_by_identifiers(
                    db,
                    student_id_number=item.student_id_number,
                    username=item.username,
                    email=item.email,
                    full_name=item.full_name,
                )
            
            if user:
                # 用户已存在，更新信息
                if item.full_name and item.full_name != user.full_name:
                    setattr(user, 'full_name', item.full_name)
                if item.email and item.email != user.email:
                    # 检查新邮箱是否已被使用
                    existing = await db.execute(
                        select(User).where(User.email == item.email, User.id != user.id)
                    )
                    if existing.scalar_one_or_none():
                        errors.append(f"第{i+1}行：邮箱 {item.email} 已被其他用户使用")
                        continue
                    setattr(user, 'email', item.email)
                if item.username and item.username != user.username:
                    # 检查新用户名是否已被使用
                    existing = await db.execute(
                        select(User).where(User.username == item.username, User.id != user.id)
                    )
                    if existing.scalar_one_or_none():
                        errors.append(f"第{i+1}行：用户名 {item.username} 已被其他用户使用")
                        continue
                    setattr(user, 'username', item.username)
                if item.student_id_number and item.student_id_number != user.student_id_number:
                    # 检查学籍号是否已被使用
                    if item.student_id_number:
                        existing = await db.execute(
                            select(User).where(
                                User.student_id_number == item.student_id_number,
                                User.id != user.id
                            )
                        )
                        if existing.scalar_one_or_none():
                            errors.append(f"第{i+1}行：学籍号 {item.student_id_number} 已被其他用户使用")
                            continue
                    setattr(user, 'student_id_number', item.student_id_number)
                if item.password:
                    setattr(user, 'hashed_password', get_password_hash(item.password))
                if item.role is not None:
                    setattr(user, 'role', item.role)
                if item.is_active is not None:
                    setattr(user, 'is_active', item.is_active)
                
                # 更新组织信息
                if item.region_id is not None or item.school_id is not None or \
                   item.grade_id is not None or item.classroom_id is not None:
                    scope_ids = await _validate_scope_ids(
                        db,
                        region_id=item.region_id,
                        school_id=item.school_id,
                        grade_id=item.grade_id,
                        classroom_id=item.classroom_id,
                    )
                    for key, value in scope_ids.items():
                        setattr(user, key, value)
                
                await db.flush()
            else:
                # 用户不存在，创建新用户
                if not item.username:
                    errors.append(f"第{i+1}行：创建新用户需要提供用户名/学号")
                    continue
                if not item.email:
                    errors.append(f"第{i+1}行：创建新用户需要提供邮箱")
                    continue
                if not item.password:
                    errors.append(f"第{i+1}行：创建新用户需要提供密码")
                    continue
                
                # 检查用户名和邮箱是否已存在
                existing_username = await db.execute(
                    select(User).where(User.username == item.username)
                )
                if existing_username.scalar_one_or_none():
                    errors.append(f"第{i+1}行：用户名 {item.username} 已存在")
                    continue
                
                existing_email = await db.execute(
                    select(User).where(User.email == item.email)
                )
                if existing_email.scalar_one_or_none():
                    errors.append(f"第{i+1}行：邮箱 {item.email} 已存在")
                    continue
                
                # 检查学籍号是否已存在
                if item.student_id_number:
                    existing_sid = await db.execute(
                        select(User).where(User.student_id_number == item.student_id_number)
                    )
                    if existing_sid.scalar_one_or_none():
                        errors.append(f"第{i+1}行：学籍号 {item.student_id_number} 已存在")
                        continue
                
                # 创建用户
                hashed_password = get_password_hash(item.password)
                scope_ids = await _validate_scope_ids(
                    db,
                    region_id=item.region_id,
                    school_id=item.school_id,
                    grade_id=item.grade_id,
                    classroom_id=item.classroom_id,
                )
                
                user = User(
                    username=item.username,
                    email=item.email,
                    hashed_password=hashed_password,
                    full_name=item.full_name,
                    student_id_number=item.student_id_number,
                    role=item.role if item.role is not None else UserRole.STUDENT,
                    is_active=item.is_active if item.is_active is not None else True,
                    **scope_ids,
                )
                
                db.add(user)
                await db.flush()
            
            # 2. 如果提供了班级ID，将用户添加到班级
            if item.classroom_id:
                classroom = await db.get(Classroom, item.classroom_id)
                if not classroom:
                    errors.append(f"第{i+1}行：班级 {item.classroom_id} 不存在")
                    continue
                
                # 检查是否已是成员
                existing_membership = await db.execute(
                    select(ClassroomMembership).where(
                        ClassroomMembership.classroom_id == item.classroom_id,
                        ClassroomMembership.user_id == user.id,
                    )
                )
                membership = existing_membership.scalar_one_or_none()
                
                # 解析班级角色
                role_in_class = RoleInClass.STUDENT
                if item.role_in_class:
                    role_map = {
                        "学生": RoleInClass.STUDENT,
                        "正班主任": RoleInClass.HEAD_TEACHER_PRIMARY,
                        "副班主任": RoleInClass.HEAD_TEACHER_DEPUTY,
                        "任课教师": RoleInClass.SUBJECT_TEACHER,
                        "班干部": RoleInClass.CADRE,
                    }
                    role_in_class = role_map.get(item.role_in_class, RoleInClass.STUDENT)
                
                if membership:
                    # 更新现有成员关系
                    if not bool(membership.is_active):
                        setattr(membership, 'is_active', True)
                    setattr(membership, 'role_in_class', role_in_class)
                    if item.seat_no is not None:
                        setattr(membership, 'seat_no', item.seat_no)
                    if item.cadre_title is not None:
                        setattr(membership, 'cadre_title', item.cadre_title)
                    if item.is_primary_class is not None:
                        setattr(membership, 'is_primary_class', item.is_primary_class)
                    if item.student_no is not None:
                        setattr(membership, 'student_no', item.student_no)
                    await db.flush()
                else:
                    # 创建新成员关系
                    membership = ClassroomMembership(
                        classroom_id=item.classroom_id,
                        user_id=user.id,
                        role_in_class=role_in_class,
                        seat_no=item.seat_no,
                        cadre_title=item.cadre_title,
                        is_primary_class=item.is_primary_class if item.is_primary_class is not None else False,
                        student_no=item.student_no,
                        is_active=True,
                    )
                    db.add(membership)
                    await db.flush()
                
                added_members.append({
                    "user_id": user.id,
                    "username": user.username,
                    "full_name": user.full_name,
                    "classroom_id": item.classroom_id,
                    "classroom_name": classroom.name if classroom else None,
                })
            
            # 记录创建的用户
            if user.id not in [u.id for u in created_users]:
                result = await db.execute(
                    _user_with_relations_query().where(User.id == user.id)
                )
                user_obj = result.scalar_one_or_none()
                if user_obj:
                    created_users.append(_serialize_user(user_obj))
            
        except HTTPException as exc:
            errors.append(f"第{i+1}行：{exc.detail}")
        except Exception as e:
            errors.append(f"第{i+1}行：{str(e)}")
    
    await db.commit()
    
    return UnifiedImportResponse(
        message=f"统一导入完成，成功创建/更新 {len(created_users)} 个用户，添加到班级 {len(added_members)} 个成员",
        created_users=created_users,
        added_members=added_members,
        errors=errors,
        success_count=len(created_users) + len(added_members),
        error_count=len(errors),
        created_user_count=len(created_users),
        added_member_count=len(added_members),
    )
