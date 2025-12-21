"""
项目Cell API路由
"""

from typing import Any, List, Optional, cast
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models import User, UserRole, StudentProject, ProjectCell, ProjectStage, CellType
from app.schemas.project_cell import (
    ProjectCellCreate,
    ProjectCellUpdate,
    ProjectCellResponse,
    ProjectCellListResponse,
)
from app.api.v1.auth import get_current_active_user

router = APIRouter()


async def _get_project_or_404(
    db: AsyncSession, project_id: int, current_user: User
) -> StudentProject:
    """获取项目或返回404，同时检查权限"""
    result = await db.execute(
        select(StudentProject).where(StudentProject.id == project_id)
    )
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    # 权限检查：学生只能访问自己的项目
    user_role = cast(str, current_user.role)
    if user_role == UserRole.STUDENT.value:
        if project.creator_id != current_user.id:
            raise HTTPException(status_code=403, detail="无权限访问此项目")

    return project


async def _get_cell_or_404(
    db: AsyncSession, cell_id: int, current_user: User
) -> ProjectCell:
    """获取Cell或返回404，同时检查权限"""
    result = await db.execute(
        select(ProjectCell)
        .options(selectinload(ProjectCell.project))
        .where(ProjectCell.id == cell_id)
    )
    cell = result.scalar_one_or_none()

    if not cell:
        raise HTTPException(status_code=404, detail="Cell不存在")

    # 权限检查：通过项目检查权限
    await _get_project_or_404(db, cell.project_id, current_user)

    return cell


def _cell_to_response(cell: ProjectCell) -> ProjectCellResponse:
    """将Cell对象转换为响应"""
    cell_data = {
        k: v
        for k, v in cell.__dict__.items()
        if not k.startswith("_")
    }
    return ProjectCellResponse.model_validate(cell_data)


@router.get("/projects/{project_id}/cells", response_model=ProjectCellListResponse)
async def list_project_cells(
    project_id: int,
    stage: Optional[str] = Query(None, description="按阶段筛选"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """获取项目的所有Cells"""
    # 验证项目权限
    await _get_project_or_404(db, project_id, current_user)

    # 构建查询
    query = select(ProjectCell).where(ProjectCell.project_id == project_id)

    # 阶段筛选
    if stage:
        try:
            stage_enum = ProjectStage(stage.lower())
            query = query.where(ProjectCell.stage == stage_enum)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"无效的阶段值: {stage}")

    # 排序
    query = query.order_by(ProjectCell.stage, ProjectCell.order)

    # 执行查询
    result = await db.execute(query)
    cells = result.scalars().all()

    # 转换为响应
    items = [_cell_to_response(cell) for cell in cells]

    return ProjectCellListResponse(
        items=items,
        total=len(items),
    )


@router.post("/projects/{project_id}/cells", response_model=ProjectCellResponse, status_code=201)
async def create_project_cell(
    project_id: int,
    cell_in: ProjectCellCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """创建项目Cell"""
    # 验证项目权限
    project = await _get_project_or_404(db, project_id, current_user)

    # 验证project_id匹配
    if cell_in.project_id != project_id:
        raise HTTPException(status_code=400, detail="项目ID不匹配")

    # 验证阶段
    try:
        stage_enum = ProjectStage(cell_in.stage.lower())
    except ValueError:
        raise HTTPException(status_code=400, detail=f"无效的阶段值: {cell_in.stage}")

    # 验证Cell类型
    try:
        cell_type_enum = CellType(cell_in.cell_type.upper())
    except ValueError:
        raise HTTPException(status_code=400, detail=f"无效的Cell类型: {cell_in.cell_type}")

    # 创建Cell
    cell = ProjectCell(
        project_id=project_id,
        stage=stage_enum,
        cell_type=cell_type_enum,
        title=cell_in.title,
        content=cell_in.content,
        config=cell_in.config or {},
        order=cell_in.order,
    )

    db.add(cell)
    await db.commit()
    await db.refresh(cell)

    return _cell_to_response(cell)


@router.put("/cells/{cell_id}", response_model=ProjectCellResponse)
async def update_project_cell(
    cell_id: int,
    cell_in: ProjectCellUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """更新项目Cell"""
    cell = await _get_cell_or_404(db, cell_id, current_user)

    # 更新字段
    update_data = cell_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if hasattr(cell, field):
            setattr(cell, field, value)

    await db.commit()
    await db.refresh(cell)

    return _cell_to_response(cell)


@router.delete("/cells/{cell_id}", status_code=204)
async def delete_project_cell(
    cell_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """删除项目Cell"""
    cell = await _get_cell_or_404(db, cell_id, current_user)

    await db.delete(cell)
    await db.commit()

