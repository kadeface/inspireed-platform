"""
管理员组织架构管理 API
提供区域、学校等组织单位的管理功能
"""

from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from pydantic import BaseModel
from datetime import datetime

from app.core.database import get_db
from app.models import User, Region, School
from app.api.deps import get_current_admin


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


# ==================== Region Endpoints ====================


@router.get("/regions", response_model=RegionListResponse)
async def get_regions(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=100, description="每页数量"),
    level: Optional[int] = Query(None, description="区域级别筛选"),
    parent_id: Optional[int] = Query(None, description="父级区域筛选"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Any:
    """获取区域列表"""

    # 构建查询
    query = select(Region)

    # 级别筛选
    if level is not None:
        query = query.where(Region.level == level)

    # 父级区域筛选
    if parent_id is not None:
        query = query.where(Region.parent_id == parent_id)

    # 搜索筛选
    if search:
        search_filter = or_(Region.name.ilike(f"%{search}%"), Region.code.ilike(f"%{search}%"))
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
    existing_region = await db.execute(select(Region).where(Region.code == region_data.code))
    if existing_region.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="区域编码已存在")

    # 检查父级区域是否存在
    if region_data.parent_id:
        parent_region = await db.execute(select(Region).where(Region.id == region_data.parent_id))
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
            select(Region).where(Region.code == region_data.code, Region.id != region_id)
        )
        if existing_region.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="区域编码已存在")

    # 检查父级区域是否存在
    if region_data.parent_id and region_data.parent_id != region.parent_id:
        parent_region = await db.execute(select(Region).where(Region.id == region_data.parent_id))
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
    children_count = await db.execute(
        select(func.count()).select_from(Region).where(Region.parent_id == region_id)
    )
    if children_count.scalar() > 0:
        raise HTTPException(status_code=400, detail="该区域下还有子区域，无法删除")

    # 检查是否有学校
    schools_count = await db.execute(
        select(func.count()).select_from(School).where(School.region_id == region_id)
    )
    if schools_count.scalar() > 0:
        raise HTTPException(status_code=400, detail="该区域下还有学校，无法删除")

    await db.delete(region)
    await db.commit()

    return {"message": "区域删除成功"}


# ==================== School Endpoints ====================


@router.get("/schools", response_model=SchoolListResponse)
async def get_schools(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=100, description="每页数量"),
    region_id: Optional[int] = Query(None, description="区域筛选"),
    school_type: Optional[str] = Query(None, description="学校类型筛选"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Any:
    """获取学校列表"""

    # 构建查询，使用selectinload预加载region关系
    query = select(School).options(selectinload(School.region))

    # 区域筛选
    if region_id:
        query = query.where(School.region_id == region_id)

    # 学校类型筛选
    if school_type:
        query = query.where(School.school_type == school_type)

    # 搜索筛选
    if search:
        search_filter = or_(
            School.name.ilike(f"%{search}%"),
            School.code.ilike(f"%{search}%"),
            School.principal.ilike(f"%{search}%"),
        )
        query = query.where(search_filter)

    # 获取总数
    count_query = select(func.count()).select_from(School)
    if region_id:
        count_query = count_query.where(School.region_id == region_id)
    if school_type:
        count_query = count_query.where(School.school_type == school_type)
    if search:
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
        select(School).options(selectinload(School.region)).where(School.id == school_id)
    )
    school = result.scalar_one_or_none()

    if not school:
        raise HTTPException(status_code=404, detail="学校不存在")

    return SchoolResponse.model_validate(school)


@router.post("/schools", response_model=SchoolResponse)
async def create_school(
    school_data: SchoolCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Any:
    """创建学校"""

    # 检查编码是否已存在
    existing_school = await db.execute(select(School).where(School.code == school_data.code))
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
        select(School).options(selectinload(School.region)).where(School.id == school.id)
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
            select(School).where(School.code == school_data.code, School.id != school_id)
        )
        if existing_school.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="学校编码已存在")

    # 检查区域是否存在
    if school_data.region_id and school_data.region_id != school.region_id:
        region = await db.execute(select(Region).where(Region.id == school_data.region_id))
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
        select(School).options(selectinload(School.region)).where(School.id == school.id)
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
    users_count = await db.execute(
        select(func.count()).select_from(User).where(User.school_id == school_id)
    )
    if users_count.scalar() > 0:
        raise HTTPException(status_code=400, detail="该学校下还有用户，无法删除")

    await db.delete(school)
    await db.commit()

    return {"message": "学校删除成功"}


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
