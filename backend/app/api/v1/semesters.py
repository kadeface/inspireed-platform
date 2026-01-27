"""
学期管理API

提供学期的CRUD操作
"""

from typing import Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, and_
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, Query

from app.api.deps import get_db, get_current_active_user
from app.models import User, Semester, UserRole
from app.schemas.evaluation import (
    SemesterCreate,
    SemesterUpdate,
    SemesterResponse,
)

router = APIRouter()


@router.post("/", response_model=SemesterResponse, status_code=status.HTTP_201_CREATED)
async def create_semester(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    semester_in: SemesterCreate,
) -> Any:
    """
    创建新学期

    需要管理员权限
    """
    # 权限检查：只有管理员可以创建学期
    if current_user.role not in [UserRole.ADMIN, UserRole.DISTRICT_ADMIN, UserRole.SCHOOL_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有管理员可以创建学期"
        )

    # 如果设置为当前学期，需要先将其他学期设为非当前
    if semester_in.is_current:
        result = await db.execute(
            select(Semester).where(
                and_(
                    Semester.is_current == True,
                    Semester.region_id == semester_in.region_id if semester_in.region_id else True
                )
            )
        )
        current_semesters = result.scalars().all()
        # 更新所有is_current为False并提交
        for current_semester in current_semesters:
            current_semester.is_current = False
        # 先提交其他学期的is_current修改
        await db.commit()
 
    # 创建学期
    semester = Semester(**semester_in.model_dump())
    db.add(semester)
    await db.commit()
    await db.refresh(semester)
 
    return semester


@router.get("/", response_model=list[SemesterResponse])
async def list_semesters(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(100, ge=1, le=100, description="返回记录数"),
    year: Optional[int] = Query(None, description="学年筛选"),
    is_current: Optional[bool] = Query(None, description="是否当前学期"),
    region_id: Optional[int] = Query(None, description="区县ID筛选"),
) -> Any:
    """
    获取学期列表

    权限说明：
    - 管理员：可查看所有学期
    - 其他用户：可查看所有学期
    """
    # 构建查询条件
    conditions = []

    if year is not None:
        conditions.append(Semester.year == year)

    if is_current is not None:
        conditions.append(Semester.is_current == is_current)

    if region_id is not None:
        conditions.append(Semester.region_id == region_id)

    # 执行查询
    if conditions:
        query = select(Semester).where(
            and_(*conditions)
        ).order_by(desc(Semester.year), desc(Semester.start_date)).offset(skip).limit(limit)
    else:
        query = select(Semester).order_by(
            desc(Semester.year),
            desc(Semester.start_date)
        ).offset(skip).limit(limit)

    result = await db.execute(query)
    semesters = result.scalars().all()

    return semesters


@router.get("/{semester_id}", response_model=SemesterResponse)
async def get_semester(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    semester_id: int,
) -> Any:
    """
    获取单个学期详情
    """
    result = await db.execute(
        select(Semester).where(Semester.id == semester_id)
    )
    semester = result.scalar_one_or_none()

    if not semester:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="学期不存在"
        )

    return semester


@router.put("/{semester_id}", response_model=SemesterResponse)
async def update_semester(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    semester_id: int,
    semester_in: SemesterUpdate,
) -> Any:
    """
    更新学期信息

    需要管理员权限
    """
    # 权限检查：只有管理员可以更新学期
    if current_user.role not in [UserRole.ADMIN, UserRole.DISTRICT_ADMIN, UserRole.SCHOOL_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有管理员可以更新学期"
        )

    result = await db.execute(
        select(Semester).where(Semester.id == semester_id)
    )
    semester = result.scalar_one_or_none()

    if not semester:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="学期不存在"
        )

    # 如果设置为当前学期，需要先将其他学期设为非当前
    update_data = semester_in.model_dump(exclude_unset=True)
    if update_data.get("is_current") == True:
        # 获取该学期的region_id
        current_semester = await db.execute(
            select(Semester).where(Semester.id == semester_id)
        )
        current_semester = current_semester.scalar_one_or_none()
        if current_semester:
            # 重新查询所有当前学期
            current_result = await db.execute(
                select(Semester).where(
                    and_(
                        Semester.is_current == True,
                        Semester.region_id == current_semester.region_id if current_semester.region_id else True
                    )
                )
            )
            current_semesters = current_result.scalars().all()
            # 更新其他学期的is_current为False
            for other_semester in current_semesters:
                if other_semester.id != semester_id:
                    other_semester.is_current = False
            # 提交is_current修改
            await db.commit()
            # 重新刷新semester对象，因为commit后可能失效
            semester = await db.execute(
                select(Semester).where(Semester.id == semester_id)
            )
            semester = semester.scalar_one_or_none()

    # 更新字段
    for field, value in update_data.items():
        setattr(semester, field, value)

    await db.commit()
    await db.refresh(semester)

    return semester


@router.delete("/{semester_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_semester(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    semester_id: int,
) -> None:
    """
    删除学期

    需要管理员权限
    """
    # 权限检查：只有管理员可以删除学期
    if current_user.role not in [UserRole.ADMIN, UserRole.DISTRICT_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有超级管理员和区县管理员可以删除学期"
        )

    result = await db.execute(
        select(Semester).where(Semester.id == semester_id)
    )
    semester = result.scalar_one_or_none()

    if not semester:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="学期不存在"
        )

    # TODO: 检查是否有关联的考试，如果有则不允许删除

    await db.delete(semester)
    await db.commit()

    return None


@router.get("/current/", response_model=SemesterResponse)
async def get_current_semester(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    region_id: Optional[int] = Query(None, description="区县ID"),
) -> Any:
    """
    获取当前学期

    如果有多个当前学期，返回最新的一个
    """
    conditions = [Semester.is_current == True]

    if region_id:
        conditions.append(Semester.region_id == region_id)

    result = await db.execute(
        select(Semester)
        .where(and_(*conditions))
        .order_by(desc(Semester.start_date))
        .limit(1)
    )
    semester = result.scalar_one_or_none()

    if not semester:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="未找到当前学期"
        )

    return semester
