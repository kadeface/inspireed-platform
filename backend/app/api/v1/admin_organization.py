"""
管理员组织架构管理 API
提供区域、学校等组织单位的管理功能
"""

import logging
from typing import Any, List, Optional, Dict
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, Query, File, UploadFile
from sqlalchemy import select, func, or_, join
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from pydantic import BaseModel, Field
from datetime import datetime

from app.core.database import get_db
from app.models import User, Region, School, Grade, Classroom, UserRole
from app.api.deps import get_current_admin, get_current_admin_or_staff

logger = logging.getLogger(__name__)


router = APIRouter()


# ==================== Request/Response Models ====================


class RegionCreate(BaseModel):
    """创建区域请求"""

    name: str
    code: str
    level: int
    parent_id: Optional[int] = None
    description: Optional[str] = None
    is_active: bool = True


class RegionUpdate(BaseModel):
    """更新区域请求"""

    name: Optional[str] = None
    code: Optional[str] = None
    level: Optional[int] = None
    parent_id: Optional[int] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class RegionResponse(BaseModel):
    """区域响应"""

    id: int
    name: str
    code: str
    level: int
    parent_id: Optional[int] = None
    is_active: bool
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SchoolCreate(BaseModel):
    """创建学校请求"""

    name: str
    code: str
    region_id: int
    school_type: str
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    principal: Optional[str] = None
    description: Optional[str] = None
    is_active: bool = True


class SchoolUpdate(BaseModel):
    """更新学校请求"""

    name: Optional[str] = None
    code: Optional[str] = None
    region_id: Optional[int] = None
    school_type: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    principal: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class SchoolResponse(BaseModel):
    """学校响应"""

    id: int
    name: str
    code: str
    region_id: int
    school_type: str
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    principal: Optional[str] = None
    is_active: bool
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    region: Optional[RegionResponse] = None

    class Config:
        from_attributes = True


class RegionListResponse(BaseModel):
    """区域列表响应"""

    regions: List[RegionResponse]
    total: int
    page: int
    size: int
    total_pages: int


class SchoolListResponse(BaseModel):
    """学校列表响应"""

    schools: List[SchoolResponse]
    total: int
    page: int
    size: int
    total_pages: int


class SchoolTypeResponse(BaseModel):
    """学校类型（学段）响应"""

    name: str
    school_count: int


class SchoolTypeListResponse(BaseModel):
    """学校类型列表响应"""

    school_types: List[SchoolTypeResponse]


class SchoolRelationCheck(BaseModel):
    """学校关联数据检查结果"""
    school_id: int
    school_name: str
    has_relations: bool
    relations: Optional[Dict[str, int]] = None  # {classrooms: 0, teachers: 0, students: 0}


class BatchDeleteSchoolsRequest(BaseModel):
    """批量删除学校请求"""
    school_ids: List[int]
    cascade_delete: bool = False


class BatchDeleteSchoolsError(BaseModel):
    """批量删除学校错误详情"""
    school_id: int
    school_name: str
    error: str


class BatchDeleteSchoolsResponse(BaseModel):
    """批量删除学校响应"""
    total_requested: int
    deleted_count: int
    failed_count: int
    errors: List[BatchDeleteSchoolsError]


class ClassroomCreate(BaseModel):
    """创建班级请求"""

    name: str
    school_id: int
    grade_id: int
    code: Optional[str] = None
    enrollment_year: Optional[int] = None
    head_teacher_id: Optional[int] = None
    description: Optional[str] = None
    is_active: bool = True


class ClassroomUpdate(BaseModel):
    """更新班级请求"""

    name: Optional[str] = None
    school_id: Optional[int] = None
    grade_id: Optional[int] = None
    code: Optional[str] = None
    enrollment_year: Optional[int] = None
    head_teacher_id: Optional[int] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class ClassroomResponse(BaseModel):
    """班级响应"""

    id: int
    name: str
    school_id: int
    grade_id: int
    code: Optional[str] = None
    enrollment_year: Optional[int] = None
    head_teacher_id: Optional[int] = None
    is_active: bool
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ClassroomListResponse(BaseModel):
    """班级列表响应"""

    classrooms: List[ClassroomResponse]
    total: int
    page: int
    size: int
    total_pages: int


class ClassroomImportError(BaseModel):
    """班级导入错误"""

    row: int
    field: Optional[str] = None
    message: str


class ClassroomImportResponse(BaseModel):
    """班级导入响应"""

    total: int
    success: int
    failed: int
    created: int
    updated: int
    skipped: int
    errors: List[ClassroomImportError]


# ==================== School Import Models ====================


class SchoolImportItem(BaseModel):
    """学校导入项"""

    region_name: str = Field(..., description="区域名称")
    school_name: str = Field(..., description="学校名称")
    school_code: Optional[str] = Field(None, description="学校代码（可选，用于精确匹配）")
    school_type: Optional[str] = Field(None, description="学校类型：小学/初中/高中/大学等")
    address: Optional[str] = Field(None, description="学校地址")
    phone: Optional[str] = Field(None, description="联系电话")
    email: Optional[str] = Field(None, description="邮箱")
    principal: Optional[str] = Field(None, description="校长姓名")


class SchoolImportRequest(BaseModel):
    """学校批量导入请求"""

    schools: List[SchoolImportItem]
    auto_create_region: bool = Field(True, description="是否自动创建不存在的区域")


class SchoolImportError(BaseModel):
    """学校导入错误"""

    row: int = Field(..., description="行号")
    field: Optional[str] = Field(None, description="字段名")
    message: str = Field(..., description="错误信息")


class SchoolImportResponse(BaseModel):
    """学校批量导入响应"""

    total: int = Field(..., description="总记录数")
    success: int = Field(..., description="成功数")
    failed: int = Field(..., description="失败数")
    created_regions: int = Field(0, description="创建的区域数")
    created_schools: int = Field(0, description="创建的学校数")
    updated_schools: int = Field(0, description="更新的学校数")
    skipped_schools: int = Field(0, description="跳过的学校数（已存在）")
    errors: List[SchoolImportError] = Field(default_factory=list, description="错误列表")


# ==================== Region Endpoints ====================


@router.get("/regions", response_model=RegionListResponse)
async def get_regions(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=1000, description="每页数量"),
    level: Optional[int] = Query(None, description="区域级别筛选"),
    parent_id: Optional[int] = Query(None, description="父级区域筛选"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_or_staff),
) -> Any:
    """获取区域列表（根据用户角色过滤数据）"""

    # 构建查询
    query = select(Region)

    # 根据用户角色添加数据过滤
    if current_user.role == UserRole.DISTRICT_ADMIN:
        # 区县管理员：只能看到自己所属的区县
        if current_user.region_id:
            query = query.where(Region.id == current_user.region_id)
            # 忽略其他筛选条件
            level = None  # type: ignore
            parent_id = None  # type: ignore
        else:
            # 区县管理员没有设置区县，返回空列表
            return RegionListResponse(regions=[], total=0, page=page, size=size, total_pages=0)
    # SCHOOL_ADMIN 和 ADMIN 不过滤区县（虽然SCHOOL_ADMIN一般不需要查看区县列表）

    # 级别筛选
    if level is not None:
        query = query.where(Region.level == level)

    # 父级区域筛选
    if parent_id is not None:
        query = query.where(Region.parent_id == parent_id)

    # 搜索筛选
    if search:
        search_filter = or_(
            Region.name.ilike(f"%{search}%"), Region.code.ilike(f"%{search}%")
        )
        query = query.where(search_filter)

    # 获取总数
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # 分页查询
    offset = (page - 1) * size
    query = query.offset(offset).limit(size).order_by(Region.level, Region.name)

    result = await db.execute(query)
    regions = result.scalars().all()

    total_pages = (total + size - 1) // size

    return RegionListResponse(
        regions=[RegionResponse.model_validate(region) for region in regions],
        total=total,
        page=page,
        size=size,
        total_pages=total_pages,
    )


@router.get("/regions/{region_id}", response_model=RegionResponse)
async def get_region(
    region_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Any:
    """获取区域详情"""

    result = await db.execute(select(Region).where(Region.id == region_id))
    region = result.scalar_one_or_none()

    if not region:
        raise HTTPException(status_code=404, detail="区域不存在")

    return RegionResponse.model_validate(region)


@router.post("/regions", response_model=RegionResponse)
async def create_region(
    region_data: RegionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Any:
    """创建区域"""

    # 检查编码是否已存在
    existing_region = await db.execute(
        select(Region).where(Region.code == region_data.code)
    )
    if existing_region.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="区域编码已存在")

    # 检查父级区域是否存在
    if region_data.parent_id:
        parent_region = await db.execute(
            select(Region).where(Region.id == region_data.parent_id)
        )
        if not parent_region.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="父级区域不存在")

    # 创建区域
    region = Region(**region_data.model_dump())

    db.add(region)
    await db.commit()
    await db.refresh(region)

    return RegionResponse.model_validate(region)


@router.put("/regions/{region_id}", response_model=RegionResponse)
async def update_region(
    region_id: int,
    region_data: RegionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Any:
    """更新区域"""

    result = await db.execute(select(Region).where(Region.id == region_id))
    region = result.scalar_one_or_none()

    if not region:
        raise HTTPException(status_code=404, detail="区域不存在")

    # 检查编码是否已被其他区域使用
    if region_data.code and region_data.code != region.code:
        existing_region = await db.execute(
            select(Region).where(
                Region.code == region_data.code, Region.id != region_id
            )
        )
        if existing_region.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="区域编码已存在")

    # 检查父级区域是否存在
    if region_data.parent_id and region_data.parent_id != region.parent_id:
        parent_region = await db.execute(
            select(Region).where(Region.id == region_data.parent_id)
        )
        if not parent_region.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="父级区域不存在")

    # 更新区域信息
    update_data = region_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(region, field, value)

    await db.commit()
    await db.refresh(region)

    return RegionResponse.model_validate(region)


@router.delete("/regions/{region_id}")
async def delete_region(
    region_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Any:
    """删除区域"""

    result = await db.execute(select(Region).where(Region.id == region_id))
    region = result.scalar_one_or_none()

    if not region:
        raise HTTPException(status_code=404, detail="区域不存在")

    # 检查是否有子区域
    children_count_result = await db.execute(
        select(func.count()).select_from(Region).where(Region.parent_id == region_id)
    )
    children_count = children_count_result.scalar() or 0
    if children_count > 0:
        raise HTTPException(status_code=400, detail="该区域下还有子区域，无法删除")

    # 检查是否有学校
    schools_count_result = await db.execute(
        select(func.count()).select_from(School).where(School.region_id == region_id)
    )
    schools_count = schools_count_result.scalar() or 0
    if schools_count > 0:
        raise HTTPException(status_code=400, detail="该区域下还有学校，无法删除")

    await db.delete(region)
    await db.commit()

    return {"message": "区域删除成功"}


# ==================== School Endpoints ====================


@router.get("/schools", response_model=SchoolListResponse)
async def get_schools(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=1000, description="每页数量"),
    region_id: Optional[int] = Query(None, description="区域筛选"),
    school_type: Optional[str] = Query(None, description="学校类型筛选"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_or_staff),
) -> Any:
    """获取学校列表（根据用户角色过滤数据）"""

    # 构建查询，使用selectinload预加载region关系
    query = select(School).options(selectinload(School.region))

    # 根据用户角色添加数据过滤
    if current_user.role == UserRole.DISTRICT_ADMIN:
        # 区县管理员：只能看到自己区县的学校
        if current_user.region_id:
            query = query.where(School.region_id == current_user.region_id)
            # 如果用户同时传递了region_id参数，必须和自己的区县一致
            if region_id and region_id != current_user.region_id:
                raise HTTPException(status_code=403, detail="只能查看自己区县的学校")
        else:
            # 区县管理员没有设置区县，返回空列表
            return SchoolListResponse(schools=[], total=0, page=page, size=size, total_pages=0)
    elif current_user.role == UserRole.SCHOOL_ADMIN:
        # 学校管理员：只能看到自己的学校
        if current_user.school_id:
            query = query.where(School.id == current_user.school_id)
            # 忽略其他筛选条件，因为只能看到一所学校
            region_id = None  # type: ignore
        else:
            # 学校管理员没有设置学校，返回空列表
            return SchoolListResponse(schools=[], total=0, page=page, size=size, total_pages=0)
    # ADMIN 不过滤，可以看到所有学校

    # 区域筛选（仅ADMIN可以使用）
    if region_id:
        query = query.where(School.region_id == region_id)

    # 学校类型筛选
    if school_type:
        query = query.where(School.school_type == school_type)

    search_filter = None
    # 搜索筛选
    if search:
        search_filter = or_(
            School.name.ilike(f"%{search}%"),
            School.code.ilike(f"%{search}%"),
            School.principal.ilike(f"%{search}%"),
        )
        query = query.where(search_filter)

    # 获取总数（应用相同的过滤条件）
    count_query = select(func.count()).select_from(School)

    # 应用角色过滤到count查询
    if current_user.role == UserRole.DISTRICT_ADMIN and current_user.region_id:
        count_query = count_query.where(School.region_id == current_user.region_id)
    elif current_user.role == UserRole.SCHOOL_ADMIN and current_user.school_id:
        count_query = count_query.where(School.id == current_user.school_id)

    if region_id and current_user.role == UserRole.ADMIN:
        count_query = count_query.where(School.region_id == region_id)
    if school_type:
        count_query = count_query.where(School.school_type == school_type)
    if search_filter is not None:
        count_query = count_query.where(search_filter)
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # 分页查询
    offset = (page - 1) * size
    query = query.offset(offset).limit(size).order_by(School.name)

    result = await db.execute(query)
    schools = result.scalars().all()

    total_pages = (total + size - 1) // size

    return SchoolListResponse(
        schools=[SchoolResponse.model_validate(school) for school in schools],
        total=total,
        page=page,
        size=size,
        total_pages=total_pages,
    )


@router.get("/schools/{school_id}", response_model=SchoolResponse)
async def get_school(
    school_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Any:
    """获取学校详情"""

    result = await db.execute(
        select(School)
        .options(selectinload(School.region))
        .where(School.id == school_id)
    )
    school = result.scalar_one_or_none()

    if not school:
        raise HTTPException(status_code=404, detail="学校不存在")

    return SchoolResponse.model_validate(school)


@router.get("/school-types", response_model=SchoolTypeListResponse)
async def get_school_types(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Any:
    """获取所有学校类型（学段）列表

    从数据库中动态获取所有不重复的 school_type 值，
    用于班级管理的学段筛选功能。
    """

    # 查询所有不重复的 school_type 及其学校数量
    result = await db.execute(
        select(School.school_type, func.count(School.id).label("count"))
        .group_by(School.school_type)
        .order_by(School.school_type)
    )

    school_types_data = result.all()

    # 构建响应数据
    school_types = [
        SchoolTypeResponse(name=row.school_type, school_count=row.count)
        for row in school_types_data
    ]

    return SchoolTypeListResponse(school_types=school_types)


@router.post("/schools", response_model=SchoolResponse)
async def create_school(
    school_data: SchoolCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Any:
    """创建学校"""

    # 检查编码是否已存在
    existing_school = await db.execute(
        select(School).where(School.code == school_data.code)
    )
    if existing_school.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="学校编码已存在")

    # 检查区域是否存在
    region = await db.execute(select(Region).where(Region.id == school_data.region_id))
    if not region.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="区域不存在")

    # 创建学校
    school = School(**school_data.model_dump())

    db.add(school)
    await db.commit()
    await db.refresh(school)

    # 重新查询以加载region关系
    result = await db.execute(
        select(School)
        .options(selectinload(School.region))
        .where(School.id == school.id)
    )
    school = result.scalar_one()

    return SchoolResponse.model_validate(school)


@router.put("/schools/{school_id}", response_model=SchoolResponse)
async def update_school(
    school_id: int,
    school_data: SchoolUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Any:
    """更新学校"""

    result = await db.execute(select(School).where(School.id == school_id))
    school = result.scalar_one_or_none()

    if not school:
        raise HTTPException(status_code=404, detail="学校不存在")

    # 检查编码是否已被其他学校使用
    if school_data.code and school_data.code != school.code:
        existing_school = await db.execute(
            select(School).where(
                School.code == school_data.code, School.id != school_id
            )
        )
        if existing_school.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="学校编码已存在")

    # 检查区域是否存在
    if school_data.region_id and school_data.region_id != school.region_id:
        region = await db.execute(
            select(Region).where(Region.id == school_data.region_id)
        )
        if not region.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="区域不存在")

    # 更新学校信息
    update_data = school_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(school, field, value)

    await db.commit()
    await db.refresh(school)

    # 重新查询以加载region关系
    result = await db.execute(
        select(School)
        .options(selectinload(School.region))
        .where(School.id == school.id)
    )
    school = result.scalar_one()

    return SchoolResponse.model_validate(school)


@router.delete("/schools/{school_id}")
async def delete_school(
    school_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Any:
    """删除学校"""

    result = await db.execute(select(School).where(School.id == school_id))
    school = result.scalar_one_or_none()

    if not school:
        raise HTTPException(status_code=404, detail="学校不存在")

    # 检查是否有用户
    users_count_result = await db.execute(
        select(func.count()).select_from(User).where(User.school_id == school_id)
    )
    users_count = users_count_result.scalar() or 0
    if users_count > 0:
        raise HTTPException(status_code=400, detail="该学校下还有用户，无法删除")

    await db.delete(school)
    await db.commit()

    return {"message": "学校删除成功"}


@router.post("/schools/check-relations")
async def check_school_relations(
    request: Dict[str, List[int]],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Any:
    """检查学校的关联数据

    返回每个学校的关联数据统计（班级、教师、学生）
    使用批量查询优化性能，避免N+1查询问题
    """
    school_ids = request.get("school_ids", [])

    if not school_ids:
        raise HTTPException(status_code=400, detail="必须提供学校ID列表")

    # 限制批量操作的数量
    if len(school_ids) > 1000:
        raise HTTPException(status_code=400, detail="单次最多检查1000所学校")

    # 批量获取所有学校信息（1次查询）
    schools_result = await db.execute(
        select(School).where(School.id.in_(school_ids))
    )
    schools = {school.id: school for school in schools_result.scalars()}

    # 批量获取所有学校的班级数量（1次查询）
    classroom_counts_result = await db.execute(
        select(Classroom.school_id, func.count(Classroom.id))
        .group_by(Classroom.school_id)
        .where(Classroom.school_id.in_(school_ids))
    )
    classroom_counts = {row[0]: row[1] for row in classroom_counts_result}

    # 批量获取所有学校的用户数量（1次查询）
    user_counts_result = await db.execute(
        select(User.school_id, func.count(User.id))
        .group_by(User.school_id)
        .where(User.school_id.in_(school_ids))
    )
    user_counts = {row[0]: row[1] for row in user_counts_result}

    # 构建结果（在内存中处理）
    results = []
    for school_id in school_ids:
        school = schools.get(school_id)

        if not school:
            results.append(SchoolRelationCheck(
                school_id=school_id,
                school_name=f"未知学校 (ID: {school_id})",
                has_relations=False,
                relations=None
            ))
            continue

        # 从预取的计数结果中获取数据
        classrooms_count = classroom_counts.get(school_id, 0)
        users_count = user_counts.get(school_id, 0)

        has_relations = classrooms_count > 0 or users_count > 0

        results.append(SchoolRelationCheck(
            school_id=school_id,
            school_name=school.name,
            has_relations=has_relations,
            relations={
                "classrooms": classrooms_count,
                "teachers_students": users_count  # 简化统计，不细分教师和学生
            } if has_relations else None
        ))

    return {"schools": results}


@router.delete("/schools/batch")
async def batch_delete_schools(
    request: BatchDeleteSchoolsRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Any:
    """批量删除学校

    - cascade_delete=False: 只删除没有关联数据的学校
    - cascade_delete=True: 删除所有学校，包括有关联数据的学校（级联删除）
    """
    school_ids = request.school_ids
    cascade_delete = request.cascade_delete

    if not school_ids:
        raise HTTPException(status_code=400, detail="必须提供学校ID列表")

    # 限制批量操作的数量
    if len(school_ids) > 500:
        raise HTTPException(status_code=400, detail="单次最多删除500所学校")

    deleted_count = 0
    failed_count = 0
    errors: List[BatchDeleteSchoolsError] = []

    for school_id in school_ids:
        try:
            # 获取学校信息
            school_result = await db.execute(
                select(School).where(School.id == school_id)
            )
            school = school_result.scalar_one_or_none()

            if not school:
                errors.append(BatchDeleteSchoolsError(
                    school_id=school_id,
                    school_name=f"未知学校 (ID: {school_id})",
                    error="学校不存在"
                ))
                failed_count += 1
                continue

            # 检查班级数量
            classrooms_count_result = await db.execute(
                select(func.count()).select_from(Classroom).where(Classroom.school_id == school_id)
            )
            classrooms_count = classrooms_count_result.scalar() or 0

            # 检查用户数量
            users_count_result = await db.execute(
                select(func.count()).select_from(User).where(User.school_id == school_id)
            )
            users_count = users_count_result.scalar() or 0

            has_relations = classrooms_count > 0 or users_count > 0

            # 根据cascade_delete参数决定是否删除
            if has_relations and not cascade_delete:
                errors.append(BatchDeleteSchoolsError(
                    school_id=school_id,
                    school_name=school.name,
                    error=f"学校有关联数据（{classrooms_count}个班级，{users_count}个用户），无法删除"
                ))
                failed_count += 1
                continue

            # 级联删除关联数据（如果启用）
            if cascade_delete and has_relations:
                # 注意：实际的级联删除应该通过外键约束或显式删除来完成
                # 这里简化处理，假设数据库有正确的级联设置
                pass

            # 删除学校
            await db.delete(school)
            deleted_count += 1

        except Exception as e:
            logger.error(f"删除学校 {school_id} 失败: {str(e)}")
            errors.append(BatchDeleteSchoolsError(
                school_id=school_id,
                school_name=school.name if school else f"未知学校 (ID: {school_id})",
                error=str(e)
            ))
            failed_count += 1

    # 提交事务
    await db.commit()

    return BatchDeleteSchoolsResponse(
        total_requested=len(school_ids),
        deleted_count=deleted_count,
        failed_count=failed_count,
        errors=errors
    )


# ==================== School Import Endpoints ====================


@router.post("/schools/import", response_model=SchoolImportResponse)
async def import_schools(
    file: UploadFile = File(...),
    auto_create_region: bool = Query(True, description="是否自动创建不存在的区域"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Any:
    """批量导入学校（代理到统一导入系统）

    Excel格式要求：
    - 必需列：区域名称、学校名称
    - 可选列：学校代码、学校类型、地址、联系电话、邮箱、校长
    - 支持格式：.xlsx, .xls
    """
    import tempfile
    from pathlib import Path as PathLib
    from app.services.import_orchestrator import ImportOrchestrator

    # 验证文件类型
    if not file.filename:
        logger.error("文件上传失败: 文件名为空")
        raise HTTPException(status_code=400, detail="必须上传文件")

    file_ext = PathLib(file.filename).suffix.lower()
    if file_ext not in [".xlsx", ".xls"]:
        logger.error(f"文件上传失败: 不支持的文件格式 {file_ext}, 文件名: {file.filename}")
        raise HTTPException(
            status_code=400,
            detail=f"只支持Excel文件格式 (.xlsx, .xls)，当前文件格式: {file_ext}"
        )

    # 保存文件到临时目录
    temp_file_path = None
    try:
        # 创建临时文件
        logger.info(f"开始处理文件上传: {file.filename}, 大小: {file.size if hasattr(file, 'size') else 'unknown'}")
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
            content = await file.read()
            if not content:
                logger.error("文件上传失败: 文件内容为空")
                raise HTTPException(status_code=400, detail="上传的文件为空")
            temp_file.write(content)
            temp_file_path = PathLib(temp_file.name)
            logger.info(f"文件已保存到临时路径: {temp_file_path}, 大小: {len(content)} 字节")

        # 构建导入上下文
        context = {
            "auto_create": auto_create_region,
            "auto_create_region": auto_create_region,
            "update_existing": False,
        }

        # 使用统一导入系统
        orchestrator = ImportOrchestrator()
        result = await orchestrator.execute_import(
            db=db,
            strategy_type="school",
            file_path=temp_file_path,
            context=context
        )

        # 转换错误列表为SchoolImportError对象
        error_objects: List[SchoolImportError] = [
            SchoolImportError(**err) for err in result.get("errors", [])
        ]

        return SchoolImportResponse(
            total=result["total"],
            success=result["success"],
            failed=result["failed"],
            created_regions=result.get("created_regions", 0),
            created_schools=result.get("created", 0),
            updated_schools=result.get("updated", 0),
            skipped_schools=result.get("skipped", 0),
            errors=error_objects
        )

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"导入学校失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"导入失败: {str(e)}"
        )
    finally:
        # 清理临时文件
        if temp_file_path and temp_file_path.exists():
            try:
                temp_file_path.unlink()
            except Exception as e:
                logger.warning(f"删除临时文件失败: {str(e)}")


# ==================== Classroom Endpoints ====================


@router.get("/classrooms", response_model=ClassroomListResponse)
async def get_classrooms(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=1000, description="每页数量"),
    school_id: Optional[int] = Query(None, description="学校筛选"),
    grade_id: Optional[int] = Query(None, description="年级筛选"),
    region_id: Optional[int] = Query(None, description="区域筛选"),
    school_type: Optional[str] = Query(None, description="学段筛选（小学/初中/高中）"),
    is_active: Optional[bool] = Query(None, description="激活状态筛选"),
    search: Optional[str] = Query(None, description="搜索关键词（支持班级名称、班级编码、学校名称）"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Any:
    """获取班级列表"""

    # 如果需要搜索学校名称或按区域/学段筛选，需要JOIN School表
    needs_join = search is not None or region_id is not None or school_type is not None
    
    if needs_join:
        # 需要JOIN School表以支持搜索学校名称或区域筛选
        query = select(Classroom).join(School, Classroom.school_id == School.id)
        count_query = select(func.count(Classroom.id)).select_from(
            join(Classroom, School, Classroom.school_id == School.id)
        )
    else:
        query = select(Classroom)
        count_query = select(func.count(Classroom.id))

    if school_id is not None:
        query = query.where(Classroom.school_id == school_id)
        count_query = count_query.where(Classroom.school_id == school_id)
    if grade_id is not None:
        query = query.where(Classroom.grade_id == grade_id)
        count_query = count_query.where(Classroom.grade_id == grade_id)
    if region_id is not None:
        # 通过School表筛选区域
        if not needs_join:
            # 如果还没有JOIN，需要JOIN School表
            query = query.join(School, Classroom.school_id == School.id)
            count_query = select(func.count(Classroom.id)).select_from(
                join(Classroom, School, Classroom.school_id == School.id)
            )
            needs_join = True  # 标记已JOIN
        query = query.where(School.region_id == region_id)
        count_query = count_query.where(School.region_id == region_id)
    if school_type is not None:
        # 通过School表筛选学段
        if not needs_join:
            # 如果还没有JOIN，需要JOIN School表
            query = query.join(School, Classroom.school_id == School.id)
            count_query = select(func.count(Classroom.id)).select_from(
                join(Classroom, School, Classroom.school_id == School.id)
            )
            needs_join = True  # 标记已JOIN
        query = query.where(School.school_type == school_type)
        count_query = count_query.where(School.school_type == school_type)
    if is_active is not None:
        query = query.where(Classroom.is_active == is_active)
        count_query = count_query.where(Classroom.is_active == is_active)
    if search:
        if not needs_join:
            # 如果还没有JOIN，需要JOIN School表
            query = query.join(School, Classroom.school_id == School.id)
            count_query = select(func.count(Classroom.id)).select_from(
                join(Classroom, School, Classroom.school_id == School.id)
            )
        search_filter = or_(
            Classroom.name.ilike(f"%{search}%"),
            Classroom.code.ilike(f"%{search}%"),
            Classroom.description.ilike(f"%{search}%"),
            School.name.ilike(f"%{search}%"),  # 支持搜索学校名称
        )
        query = query.where(search_filter)
        count_query = count_query.where(search_filter)

    total = (await db.execute(count_query)).scalar() or 0

    offset = (page - 1) * size
    query = query.offset(offset).limit(size).order_by(Classroom.name)

    classrooms = (await db.execute(query)).scalars().all()

    total_pages = (total + size - 1) // size

    return ClassroomListResponse(
        classrooms=[
            ClassroomResponse.model_validate(classroom) for classroom in classrooms
        ],
        total=total,
        page=page,
        size=size,
        total_pages=total_pages,
    )


@router.post("/classrooms", response_model=ClassroomResponse)
async def create_classroom(
    classroom_data: ClassroomCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Any:
    """创建班级"""

    school = await db.scalar(
        select(School).where(School.id == classroom_data.school_id)
    )
    if not school:
        raise HTTPException(status_code=404, detail="学校不存在")

    grade = await db.scalar(select(Grade).where(Grade.id == classroom_data.grade_id))
    if not grade:
        raise HTTPException(status_code=404, detail="年级不存在")

    if classroom_data.head_teacher_id is not None:
        head_teacher = await db.scalar(
            select(User).where(User.id == classroom_data.head_teacher_id)
        )
        if not head_teacher:
            raise HTTPException(status_code=404, detail="班主任用户不存在")

    classroom = Classroom(**classroom_data.model_dump())

    db.add(classroom)
    await db.commit()
    await db.refresh(classroom)

    return ClassroomResponse.model_validate(classroom)


@router.put("/classrooms/{classroom_id}", response_model=ClassroomResponse)
async def update_classroom(
    classroom_id: int,
    classroom_data: ClassroomUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Any:
    """更新班级"""

    classroom = await db.scalar(select(Classroom).where(Classroom.id == classroom_id))
    if not classroom:
        raise HTTPException(status_code=404, detail="班级不存在")

    if (
        classroom_data.school_id is not None
        and classroom_data.school_id != classroom.school_id
    ):
        school = await db.scalar(
            select(School).where(School.id == classroom_data.school_id)
        )
        if not school:
            raise HTTPException(status_code=404, detail="学校不存在")

    if (
        classroom_data.grade_id is not None
        and classroom_data.grade_id != classroom.grade_id
    ):
        grade = await db.scalar(
            select(Grade).where(Grade.id == classroom_data.grade_id)
        )
        if not grade:
            raise HTTPException(status_code=404, detail="年级不存在")

    if classroom_data.head_teacher_id is not None:
        head_teacher = await db.scalar(
            select(User).where(User.id == classroom_data.head_teacher_id)
        )
        if not head_teacher:
            raise HTTPException(status_code=404, detail="班主任用户不存在")

    update_data = classroom_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(classroom, field, value)

    await db.commit()
    await db.refresh(classroom)

    return ClassroomResponse.model_validate(classroom)


@router.post("/classrooms/import", response_model=ClassroomImportResponse)
async def import_classrooms(
    file: UploadFile = File(...),
    school_id: Optional[int] = Query(None, description="学校ID（学校管理员导入时必填，或从当前用户获取）"),
    region_id: Optional[int] = Query(None, description="区域ID（县区管理员导入时可选，用于学校匹配）"),
    update_existing: bool = Query(False, description="是否更新已存在的班级"),
    enrollment_year: Optional[int] = Query(None, description="统一设置的入学年份（如果提供，覆盖Excel中的值）"),
    capacity: Optional[int] = Query(None, description="统一设置的班级容量（如果提供，覆盖Excel中的值）"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Any:
    """批量导入班级（代理到统一导入系统）

    Excel格式要求：
    - 县区管理员导入：必需列：学校名称、年级级别、班级编号
    - 学校管理员导入：必需列：年级级别、班级编号（学校自动使用当前用户的学校）
    - 可选列：学校代码、年级名称、班级名称、入学年份、班级容量、班级描述
    - 支持格式：.xlsx, .xls

    注意：班主任信息不在导入模板中，请在班级创建后通过"班级成员管理"功能添加。
    """
    import tempfile
    from pathlib import Path as PathLib
    from app.services.import_orchestrator import ImportOrchestrator
    from app.models import UserRole

    # 验证文件类型
    if not file.filename:
        logger.error("文件上传失败: 文件名为空")
        raise HTTPException(status_code=400, detail="必须上传文件")

    file_ext = PathLib(file.filename).suffix.lower()
    if file_ext not in [".xlsx", ".xls"]:
        logger.error(f"文件上传失败: 不支持的文件格式 {file_ext}, 文件名: {file.filename}")
        raise HTTPException(
            status_code=400,
            detail=f"只支持Excel文件格式 (.xlsx, .xls)，当前文件格式: {file_ext}"
        )

    # 判断是否为学校管理员（通过用户角色和school_id）
    # 如果用户有school_id且角色为TEACHER，则认为是学校管理员
    is_school_admin = False
    actual_school_id = school_id

    if isinstance(current_user.role, UserRole):
        if current_user.role == UserRole.TEACHER and current_user.school_id:
            is_school_admin = True
            actual_school_id = int(current_user.school_id)  # type: ignore
            logger.info(f"学校管理员导入班级: user_id={current_user.id}, school_id={actual_school_id}")
        elif current_user.role == UserRole.ADMIN:
            is_school_admin = False
            # 如果是管理员但指定了school_id，认为是学校级别的导入
            if school_id:
                actual_school_id = school_id
                is_school_admin = True
        else:
            is_school_admin = False

    # 学校管理员必须提供school_id
    if is_school_admin and not actual_school_id:
        raise HTTPException(
            status_code=400,
            detail="学校管理员导入时必须提供school_id或确保用户已关联学校"
        )

    # 保存文件到临时目录
    temp_file_path = None
    try:
        # 创建临时文件
        logger.info(f"开始处理班级导入文件: {file.filename}, 大小: {file.size if hasattr(file, 'size') else 'unknown'}, 学校管理员: {is_school_admin}, school_id: {actual_school_id}")
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
            content = await file.read()
            if not content:
                logger.error("文件上传失败: 文件内容为空")
                raise HTTPException(status_code=400, detail="上传的文件为空")
            temp_file.write(content)
            temp_file_path = PathLib(temp_file.name)
            logger.info(f"文件已保存到临时路径: {temp_file_path}, 大小: {len(content)} 字节")

        # 构建导入上下文
        context = {
            "school_id": actual_school_id,
            "region_id": region_id,
            "is_school_admin": is_school_admin,
            "update_existing": update_existing,
            "auto_create": True,
        }

        # 使用统一导入系统
        orchestrator = ImportOrchestrator()
        result = await orchestrator.execute_import(
            db=db,
            strategy_type="classroom",
            file_path=temp_file_path,
            context=context
        )

        # 转换错误列表为ClassroomImportError对象
        error_objects: List[ClassroomImportError] = [
            ClassroomImportError(**err) for err in result.get("errors", [])
        ]

        return ClassroomImportResponse(
            total=result["total"],
            success=result["success"],
            failed=result["failed"],
            created=result.get("created", 0),
            updated=result.get("updated", 0),
            skipped=result.get("skipped", 0),
            errors=error_objects
        )

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"导入班级失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"导入失败: {str(e)}"
        )
    finally:
        # 清理临时文件
        if temp_file_path and temp_file_path.exists():
            try:
                temp_file_path.unlink()
            except Exception as e:
                logger.warning(f"删除临时文件失败: {str(e)}")


@router.delete("/classrooms/{classroom_id}")
async def delete_classroom(
    classroom_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Any:
    """删除班级"""

    classroom = await db.scalar(select(Classroom).where(Classroom.id == classroom_id))
    if not classroom:
        raise HTTPException(status_code=404, detail="班级不存在")

    student_count_result = await db.execute(
        select(func.count()).select_from(User).where(User.classroom_id == classroom_id)
    )
    student_count = student_count_result.scalar() or 0
    if student_count > 0:
        raise HTTPException(status_code=400, detail="班级下仍有关联学生，无法删除")

    await db.delete(classroom)
    await db.commit()

    return {"message": "班级删除成功"}


# ==================== Tree Structure Endpoints ====================


@router.get("/regions/tree")
async def get_region_tree(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Any:
    """获取区域树形结构"""

    # 获取所有区域
    result = await db.execute(select(Region).order_by(Region.level, Region.name))
    regions = result.scalars().all()

    # 构建树形结构
    region_dict = {
        region.id: {
            "id": region.id,
            "name": region.name,
            "code": region.code,
            "level": region.level,
            "parent_id": region.parent_id,
            "is_active": region.is_active,
            "children": [],
        }
        for region in regions
    }

    tree = []
    for region in regions:
        if region.parent_id is None:
            tree.append(region_dict[region.id])
        else:
            if region.parent_id in region_dict:
                region_dict[region.parent_id]["children"].append(region_dict[region.id])

    return {"tree": tree}


@router.get("/schools/by-region/{region_id}")
async def get_schools_by_region(
    region_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Any:
    """根据区域获取学校列表"""

    result = await db.execute(
        select(School).where(School.region_id == region_id).order_by(School.name)
    )
    schools = result.scalars().all()

    return {"schools": [SchoolResponse.model_validate(school) for school in schools]}
