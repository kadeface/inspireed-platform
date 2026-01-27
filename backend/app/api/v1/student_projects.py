"""
学生项目API路由
"""

from typing import Any, List, Optional, cast
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models import User, UserRole, StudentProject, ProjectStatus, ProjectStage
from app.schemas.student_project import (
    StudentProjectCreate,
    StudentProjectUpdate,
    StudentProjectResponse,
    StudentProjectListResponse,
    StageContentUpdate,
)
from app.api.v1.auth import get_current_active_user

router = APIRouter()


def _calculate_completion(content: list) -> int:
    """计算阶段完成度（基于非空cell数量）"""
    if not content:
        return 0
    # 简单计算：有内容就算有进度，可以根据实际需求调整
    non_empty_cells = [cell for cell in content if cell and isinstance(cell, dict) and cell.get("content")]
    # 假设至少需要3个cell才算完成，可以根据需求调整
    completion = min(100, int((len(non_empty_cells) / max(3, len(content))) * 100))
    return completion


def _update_completion(project: StudentProject) -> dict:
    """更新项目的完成度"""
    completion = {
        "engage": _calculate_completion(cast(list, project.engage_content or [])),
        "explore": _calculate_completion(cast(list, project.explore_content or [])),
        "explain": _calculate_completion(cast(list, project.explain_content or [])),
        "elaborate": _calculate_completion(cast(list, project.elaborate_content or [])),
        "evaluate": _calculate_completion(cast(list, project.evaluate_content or [])),
    }
    project.completion = completion  # type: ignore
    return completion


async def _get_project_or_404(
    db: AsyncSession, project_id: int, current_user: User
) -> StudentProject:
    """获取项目或返回404，同时检查权限"""
    result = await db.execute(
        select(StudentProject)
        .options(selectinload(StudentProject.creator))
        .where(StudentProject.id == project_id)
    )
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    # 权限检查：学生只能访问自己的项目
    user_role = cast(str, current_user.role)
    if user_role == UserRole.STUDENT.value:
        if project.creator_id != current_user.id:  # type: ignore
            raise HTTPException(status_code=403, detail="无权限访问此项目")

    return project


def _project_to_response(project: StudentProject) -> StudentProjectResponse:
    """将项目对象转换为响应"""
    project_data = {
        k: v
        for k, v in project.__dict__.items()
        if not k.startswith("_")
    }
    
    # 确保所有字段都有默认值
    project_data.setdefault("engage_content", project.engage_content or [])
    project_data.setdefault("explore_content", project.explore_content or [])
    project_data.setdefault("explain_content", project.explain_content or [])
    project_data.setdefault("elaborate_content", project.elaborate_content or [])
    project_data.setdefault("evaluate_content", project.evaluate_content or [])
    project_data.setdefault("completion", project.completion or {})
    project_data.setdefault("tags", project.tags or [])
    project_data.setdefault("team_members", project.team_members or [])
    
    project_data["creator_name"] = project.creator.full_name if project.creator else None
    
    return StudentProjectResponse.model_validate(project_data)


@router.get("/", response_model=StudentProjectListResponse)
async def list_projects(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None, description="状态筛选: draft, in_progress, completed, submitted"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """获取学生项目列表"""
    # 权限检查：只允许学生查看自己的项目
    user_role = cast(str, current_user.role)
    if user_role != UserRole.STUDENT.value:
        raise HTTPException(status_code=403, detail="只有学生可以访问项目列表")

    # 构建查询
    query = select(StudentProject).where(StudentProject.creator_id == current_user.id)

    # 状态筛选
    if status:
        try:
            status_enum = ProjectStatus(status.lower())
            query = query.where(StudentProject.status == status_enum)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"无效的状态值: {status}")

    # 获取总数
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # 分页
    query = query.order_by(StudentProject.updated_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)

    # 加载关联关系
    query = query.options(selectinload(StudentProject.creator))

    # 执行查询
    result = await db.execute(query)
    projects = result.scalars().all()

    # 转换为响应
    items = [_project_to_response(project) for project in projects]

    return StudentProjectListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("/", response_model=StudentProjectResponse, status_code=201)
async def create_project(
    project_in: StudentProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """创建新项目"""
    # 权限检查：只允许学生创建项目
    user_role = cast(str, current_user.role)
    if user_role != UserRole.STUDENT.value:
        raise HTTPException(status_code=403, detail="只有学生可以创建项目")

    # 创建项目
    project = StudentProject(
        title=project_in.title,
        description=project_in.description,
        creator_id=current_user.id,
        project_type=project_in.project_type,
        status=ProjectStatus.DRAFT,
        engage_content=[],
        explore_content=[],
        explain_content=[],
        elaborate_content=[],
        evaluate_content=[],
        completion={"engage": 0, "explore": 0, "explain": 0, "elaborate": 0, "evaluate": 0},
        tags=[],
        team_members=[],
    )

    db.add(project)
    await db.commit()
    await db.refresh(project)

    # 加载关联关系
    await db.refresh(project, ["creator"])

    return _project_to_response(project)


@router.get("/{project_id}", response_model=StudentProjectResponse)
async def get_project(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """获取项目详情"""
    project = await _get_project_or_404(db, project_id, current_user)
    return _project_to_response(project)


@router.put("/{project_id}", response_model=StudentProjectResponse)
async def update_project(
    project_id: int,
    project_in: StudentProjectUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """更新项目"""
    project = await _get_project_or_404(db, project_id, current_user)

    # 更新字段
    update_data = project_in.model_dump(exclude_unset=True)

    # 处理状态更新
    if "status" in update_data and update_data["status"]:
        try:
            project.status = ProjectStatus(update_data["status"])  # type: ignore
        except ValueError:
            raise HTTPException(status_code=400, detail=f"无效的状态值: {update_data['status']}")

    # 更新其他字段
    for field, value in update_data.items():
        if field == "status":
            continue  # 已经处理过了
        if field in ["engage_content", "explore_content", "explain_content", "elaborate_content", "evaluate_content"]:
            setattr(project, field, value or [])
        elif hasattr(project, field):
            setattr(project, field, value)

    # 更新完成度
    _update_completion(project)

    await db.commit()
    await db.refresh(project, ["creator"])

    return _project_to_response(project)


@router.delete("/{project_id}", status_code=204)
async def delete_project(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """删除项目"""
    project = await _get_project_or_404(db, project_id, current_user)

    await db.delete(project)
    await db.commit()


@router.put("/{project_id}/stages/{stage}", response_model=StudentProjectResponse)
async def update_stage_content(
    project_id: int,
    stage: str,
    stage_content: StageContentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """更新指定阶段的内容"""
    project = await _get_project_or_404(db, project_id, current_user)

    # 验证阶段名称
    try:
        stage_enum = ProjectStage(stage.lower())
    except ValueError:
        raise HTTPException(status_code=400, detail=f"无效的阶段值: {stage}")

    # 更新对应阶段的内容
    stage_field = f"{stage_enum.value}_content"
    if hasattr(project, stage_field):
        setattr(project, stage_field, stage_content.content or [])
    else:
        raise HTTPException(status_code=400, detail=f"无效的阶段字段: {stage_field}")

    # 更新完成度
    _update_completion(project)

    await db.commit()
    await db.refresh(project, ["creator"])

    return _project_to_response(project)
