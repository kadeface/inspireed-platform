"""
Section（大环节）API路由
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models import User, Section, SectionType, Lesson, Cell
from app.schemas.section import (
    SectionCreate,
    SectionUpdate,
    SectionResponse,
    SectionWithCells,
    SectionMove,
    CellMoveRequest,
)
from app.api.v1.auth import get_current_active_user

router = APIRouter()

# 默认大环节定义
DEFAULT_SECTIONS = [
    {"name": "教学目标、教学重点难点、学生学情分析", "type": "default", "order": 0},
    {"name": "教学过程", "type": "default", "order": 1},
    {"name": "课堂练习", "type": "default", "order": 2},
    {"name": "课程资源", "type": "default", "order": 3},
    {"name": "反思总结", "type": "default", "order": 4},
]


async def _get_lesson_and_check_permission(
    db: AsyncSession, lesson_id: int, current_user: User, require_edit: bool = True
) -> Lesson:
    """获取教案并检查权限"""
    from app.models import UserRole, LessonStatus
    
    result = await db.execute(
        select(Lesson).where(Lesson.id == lesson_id)
    )
    lesson = result.scalar_one_or_none()
    
    if not lesson:
        raise HTTPException(status_code=404, detail="教案不存在")
    
    # 如果只需要查看权限，学生可以查看已发布的教案
    if not require_edit:
        from app.models import UserRole, LessonStatus
        user_role = UserRole(current_user.role.value if hasattr(current_user.role, 'value') else current_user.role)
        lesson_status = LessonStatus(lesson.status.value if hasattr(lesson.status, 'value') else lesson.status)
        
        if user_role == UserRole.STUDENT:
            if lesson_status == LessonStatus.PUBLISHED:
                return lesson
            else:
                raise HTTPException(status_code=403, detail="无权查看该教案")
        # 管理员和教研员可以查看所有教案
        elif user_role in {UserRole.ADMIN, UserRole.RESEARCHER}:
            return lesson
        # 教师可以查看自己创建的或已发布的教案
        elif lesson.creator_id == current_user.id or lesson_status == LessonStatus.PUBLISHED:
            return lesson
        else:
            raise HTTPException(status_code=403, detail="无权查看该教案")
    
    # 需要编辑权限：只有创建者可以管理大环节
    if lesson.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权操作该教案的大环节")
    
    return lesson


@router.post("/lessons/{lesson_id}/sections", response_model=SectionResponse, status_code=201)
async def create_section(
    lesson_id: int,
    section_in: SectionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> SectionResponse:
    """创建大环节"""
    # 验证 lesson_id 匹配
    if section_in.lesson_id != lesson_id:
        raise HTTPException(status_code=400, detail="lesson_id 不匹配")
    
    # 检查权限
    await _get_lesson_and_check_permission(db, lesson_id, current_user)
    
    # 获取当前最大 order 值
    result = await db.execute(
        select(func.max(Section.order))
        .where(Section.lesson_id == lesson_id)
    )
    max_order = result.scalar_one() or -1
    
    # 创建大环节
    section = Section(
        lesson_id=lesson_id,
        name=section_in.name,
        type=SectionType(section_in.type),
        order=max_order + 1,
        is_collapsed=section_in.is_collapsed,
    )
    
    db.add(section)
    await db.commit()
    await db.refresh(section)
    
    return SectionResponse.model_validate(section)


@router.get("/lessons/{lesson_id}/sections", response_model=List[SectionWithCells])
async def list_sections(
    lesson_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> List[SectionWithCells]:
    """获取教案的所有大环节列表（包含 Cells）"""
    # 检查权限（学生可以查看已发布的教案）
    lesson = await _get_lesson_and_check_permission(db, lesson_id, current_user, require_edit=False)
    
    # 加载大环节及其 Cells
    result = await db.execute(
        select(Section)
        .options(selectinload(Section.cells))
        .where(Section.lesson_id == lesson_id)
        .order_by(Section.order)
    )
    sections = result.scalars().all()
    
    # 转换为响应格式
    sections_with_cells = []
    for section in sections:
        # 将 Cells 转换为字典格式（与前端兼容）
        cells_data = []
        for cell in sorted(section.cells, key=lambda c: c.order):
            cell_dict = {
                "id": cell.id,
                "type": cell.cell_type.value if hasattr(cell.cell_type, "value") else str(cell.cell_type),
                "order": cell.order,
                "title": cell.title,
                "content": cell.content,
                "config": cell.config or {},
                "editable": cell.editable,
                "cognitive_level": cell.cognitive_level.value if cell.cognitive_level and hasattr(cell.cognitive_level, "value") else cell.cognitive_level,
                "prerequisite_cells": cell.prerequisite_cells or [],
                "mastery_criteria": cell.mastery_criteria or {},
            }
            cells_data.append(cell_dict)
        
        section_dict = SectionWithCells.model_validate(section)
        section_dict.cells = cells_data
        sections_with_cells.append(section_dict)
    
    return sections_with_cells


@router.get("/sections/{section_id}", response_model=SectionWithCells)
async def get_section(
    section_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> SectionWithCells:
    """获取大环节详情"""
    result = await db.execute(
        select(Section)
        .options(selectinload(Section.cells))
        .where(Section.id == section_id)
    )
    section = result.scalar_one_or_none()
    
    if not section:
        raise HTTPException(status_code=404, detail="大环节不存在")
    
    # 检查权限
    await _get_lesson_and_check_permission(db, section.lesson_id, current_user)
    
    # 转换 Cells
    cells_data = []
    for cell in sorted(section.cells, key=lambda c: c.order):
        cell_dict = {
            "id": cell.id,
            "type": cell.cell_type.value if hasattr(cell.cell_type, "value") else str(cell.cell_type),
            "order": cell.order,
            "title": cell.title,
            "content": cell.content,
            "config": cell.config or {},
            "editable": cell.editable,
            "cognitive_level": cell.cognitive_level.value if cell.cognitive_level and hasattr(cell.cognitive_level, "value") else cell.cognitive_level,
            "prerequisite_cells": cell.prerequisite_cells or [],
            "mastery_criteria": cell.mastery_criteria or {},
        }
        cells_data.append(cell_dict)
    
    section_dict = SectionWithCells.model_validate(section)
    section_dict.cells = cells_data
    return section_dict


@router.put("/sections/{section_id}", response_model=SectionResponse)
async def update_section(
    section_id: int,
    section_in: SectionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> SectionResponse:
    """更新大环节"""
    result = await db.execute(
        select(Section).where(Section.id == section_id)
    )
    section = result.scalar_one_or_none()
    
    if not section:
        raise HTTPException(status_code=404, detail="大环节不存在")
    
    # 检查权限
    await _get_lesson_and_check_permission(db, section.lesson_id, current_user)
    
    # 检查是否允许修改默认大环节的名称
    if section.type == SectionType.DEFAULT and section_in.name is not None:
        raise HTTPException(status_code=400, detail="默认大环节的名称不能修改")
    
    # 更新字段
    if section_in.name is not None:
        section.name = section_in.name
    if section_in.order is not None:
        section.order = section_in.order
    if section_in.is_collapsed is not None:
        section.is_collapsed = section_in.is_collapsed
    
    await db.commit()
    await db.refresh(section)
    
    return SectionResponse.model_validate(section)


@router.delete("/sections/{section_id}", status_code=204)
async def delete_section(
    section_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> None:
    """删除大环节"""
    result = await db.execute(
        select(Section).where(Section.id == section_id)
    )
    section = result.scalar_one_or_none()
    
    if not section:
        raise HTTPException(status_code=404, detail="大环节不存在")
    
    # 检查权限
    await _get_lesson_and_check_permission(db, section.lesson_id, current_user)
    
    # 检查是否允许删除默认大环节
    if section.type == SectionType.DEFAULT:
        raise HTTPException(status_code=400, detail="默认大环节不能删除")
    
    # 检查是否有 Cell
    if section.cells:
        raise HTTPException(
            status_code=400,
            detail="该大环节下还有 Cell，请先移动或删除这些 Cell 后再删除大环节"
        )
    
    await db.delete(section)
    await db.commit()


@router.post("/sections/{section_id}/move", response_model=SectionResponse)
async def move_section(
    section_id: int,
    move_data: SectionMove,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> SectionResponse:
    """移动大环节（调整顺序）"""
    result = await db.execute(
        select(Section).where(Section.id == section_id)
    )
    section = result.scalar_one_or_none()
    
    if not section:
        raise HTTPException(status_code=404, detail="大环节不存在")
    
    # 检查权限
    await _get_lesson_and_check_permission(db, section.lesson_id, current_user)
    
    # 获取同一教案下的所有大环节
    result = await db.execute(
        select(Section)
        .where(Section.lesson_id == section.lesson_id)
        .order_by(Section.order)
    )
    all_sections = list(result.scalars().all())
    
    # 移除当前大环节
    all_sections.remove(section)
    
    # 插入到新位置
    new_order = move_data.new_order
    if new_order < 0:
        new_order = 0
    if new_order >= len(all_sections):
        new_order = len(all_sections)
    
    all_sections.insert(new_order, section)
    
    # 更新所有大环节的 order
    for idx, sec in enumerate(all_sections):
        sec.order = idx
    
    await db.commit()
    await db.refresh(section)
    
    return SectionResponse.model_validate(section)


@router.post("/cells/{cell_id}/move", status_code=200)
async def move_cell_to_section(
    cell_id: int,
    move_data: CellMoveRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> dict:
    """移动 Cell 到指定大环节"""
    # 获取 Cell
    result = await db.execute(
        select(Cell).where(Cell.id == cell_id)
    )
    cell = result.scalar_one_or_none()
    
    if not cell:
        raise HTTPException(status_code=404, detail="Cell 不存在")
    
    # 检查权限
    await _get_lesson_and_check_permission(db, cell.lesson_id, current_user)
    
    # 获取目标大环节
    result = await db.execute(
        select(Section).where(Section.id == move_data.section_id)
    )
    target_section = result.scalar_one_or_none()
    
    if not target_section:
        raise HTTPException(status_code=404, detail="目标大环节不存在")
    
    # 检查目标大环节是否属于同一教案
    if target_section.lesson_id != cell.lesson_id:
        raise HTTPException(status_code=400, detail="目标大环节不属于同一教案")
    
    # 获取目标大环节下的所有 Cell
    result = await db.execute(
        select(Cell)
        .where(Cell.section_id == move_data.section_id)
        .order_by(Cell.order)
    )
    target_cells = list(result.scalars().all())
    
    # 如果 Cell 已经在目标大环节中，先从列表中移除
    if cell in target_cells:
        target_cells.remove(cell)
    
    # 确定新的 order
    if move_data.new_order is not None:
        new_order = move_data.new_order
        if new_order < 0:
            new_order = 0
        if new_order > len(target_cells):
            new_order = len(target_cells)
    else:
        # 默认插入到末尾
        new_order = len(target_cells)
    
    # 插入到新位置
    target_cells.insert(new_order, cell)
    
    # 更新所有 Cell 的 order 和 section_id
    for idx, c in enumerate(target_cells):
        c.order = idx
        c.section_id = move_data.section_id
    
    await db.commit()
    
    return {"message": "Cell 移动成功", "cell_id": cell_id, "section_id": move_data.section_id}


@router.post("/lessons/{lesson_id}/migrate-sections", status_code=200)
async def migrate_lesson_to_sections(
    lesson_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> dict:
    """将现有教案迁移到默认大环节结构"""
    # 检查权限
    lesson = await _get_lesson_and_check_permission(db, lesson_id, current_user)
    
    # 检查是否已迁移
    result = await db.execute(
        select(Section).where(Section.lesson_id == lesson_id)
    )
    existing_sections = result.scalars().all()
    
    if existing_sections:
        return {"message": "该教案已经迁移过", "sections_count": len(existing_sections)}
    
    # 创建默认大环节
    created_sections = []
    for section_data in DEFAULT_SECTIONS:
        section = Section(
            lesson_id=lesson_id,
            name=section_data["name"],
            type=SectionType(section_data["type"]),
            order=section_data["order"],
            is_collapsed=False,
        )
        db.add(section)
        created_sections.append(section)
    
    await db.flush()  # 获取 section.id
    
    # 获取"教学过程"大环节（用于迁移现有 Cell）
    teaching_process_section = next(
        (s for s in created_sections if s.name == "教学过程"), None
    )
    
    if teaching_process_section:
        # 获取所有未关联大环节的 Cell
        result = await db.execute(
            select(Cell)
            .where(Cell.lesson_id == lesson_id)
            .where(Cell.section_id.is_(None))
            .order_by(Cell.order)
        )
        cells = result.scalars().all()
        
        # 将 Cell 关联到"教学过程"大环节
        for idx, cell in enumerate(cells):
            cell.section_id = teaching_process_section.id
            cell.order = idx
    
    await db.commit()
    
    return {
        "message": "迁移成功",
        "sections_created": len(created_sections),
        "cells_migrated": len(cells) if teaching_process_section else 0,
    }
