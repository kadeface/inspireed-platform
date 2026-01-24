"""
年级考试科目配置 API 路由
"""

from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models import User, UserRole, Grade, Subject, GradeSubjectConfig
from app.schemas.exam_subjects import (
    GradeSubjectConfigResponse,
    GradeSubjectConfigCreate,
    GradeSubjectConfigUpdate,
    GradeSubjectsWithScores,
    BulkCreateGradeSubjectConfig,
)
from app.api.v1.auth import get_current_active_user

router = APIRouter()


def require_district_admin(current_user: User = Depends(get_current_active_user)) -> User:
    """要求区县管理员权限"""
    if current_user.role != UserRole.DISTRICT_ADMIN:
        raise HTTPException(status_code=403, detail="需要区县管理员权限")
    return current_user


# ==================== GradeSubjectConfig Endpoints ====================


@router.get("/grade-subject-configs", response_model=List[GradeSubjectConfigResponse])
async def list_grade_subject_configs(
    grade_id: Optional[int] = Query(None, description="按年级ID筛选"),
    subject_id: Optional[int] = Query(None, description="按学科ID筛选"),
    is_active: Optional[bool] = Query(None, description="按启用状态筛选"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """获取年级考试科目配置列表"""
    query = select(GradeSubjectConfig).order_by(
        GradeSubjectConfig.grade_id,
        GradeSubjectConfig.display_order,
        GradeSubjectConfig.id
    )

    if grade_id is not None:
        query = query.where(GradeSubjectConfig.grade_id == grade_id)
    if subject_id is not None:
        query = query.where(GradeSubjectConfig.subject_id == subject_id)
    if is_active is not None:
        query = query.where(GradeSubjectConfig.is_active == is_active)

    # 加载关联的年级和学科信息
    query = query.options(
        selectinload(GradeSubjectConfig.grade),
        selectinload(GradeSubjectConfig.subject)
    )

    result = await db.execute(query)
    configs = result.scalars().all()

    # 手动构建响应数据
    response_data = []
    for config in configs:
        config_dict = {
            "id": config.id,
            "grade_id": config.grade_id,
            "subject_id": config.subject_id,
            "full_score": config.full_score,
            "pass_line": config.pass_line,
            "excellent_line": config.excellent_line,
            "good_line": config.good_line,
            "is_active": config.is_active,
            "display_order": config.display_order,
            "description": config.description,
            "created_at": config.created_at,
            "updated_at": config.updated_at,
            "created_by": config.created_by,
        }

        # 添加关联信息
        if hasattr(config, 'grade') and config.grade:
            config_dict["grade_name"] = config.grade.name
        if hasattr(config, 'subject') and config.subject:
            config_dict["subject_name"] = config.subject.name
            config_dict["subject_code"] = config.subject.code

        response_data.append(config_dict)

    return response_data


@router.get("/grade-subject-configs/by-grade/{grade_id}", response_model=GradeSubjectsWithScores)
async def get_grade_subjects(
    grade_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """获取某个年级的所有考试科目配置"""
    # 获取年级信息
    grade_result = await db.execute(select(Grade).where(Grade.id == grade_id))
    grade = grade_result.scalar_one_or_none()
    if not grade:
        raise HTTPException(status_code=404, detail="年级不存在")

    # 获取该年级的所有科目配置
    query = (
        select(GradeSubjectConfig)
        .where(GradeSubjectConfig.grade_id == grade_id)
        .where(GradeSubjectConfig.is_active == True)
        .order_by(GradeSubjectConfig.display_order, GradeSubjectConfig.id)
    )
    query = query.options(
        selectinload(GradeSubjectConfig.grade),
        selectinload(GradeSubjectConfig.subject)
    )

    result = await db.execute(query)
    configs = result.scalars().all()

    # 构建响应数据
    subjects_list = []
    for config in configs:
        config_dict = {
            "id": config.id,
            "grade_id": config.grade_id,
            "subject_id": config.subject_id,
            "full_score": config.full_score,
            "pass_line": config.pass_line,
            "excellent_line": config.excellent_line,
            "good_line": config.good_line,
            "is_active": config.is_active,
            "display_order": config.display_order,
            "description": config.description,
            "created_at": config.created_at,
            "updated_at": config.updated_at,
            "created_by": config.created_by,
        }

        if hasattr(config, 'subject') and config.subject:
            config_dict["subject_name"] = config.subject.name
            config_dict["subject_code"] = config.subject.code
        if hasattr(config, 'grade') and config.grade:
            config_dict["grade_name"] = config.grade.name

        subjects_list.append(config_dict)

    return {
        "grade_id": grade.id,
        "grade_name": grade.name,
        "grade_level": grade.level,
        "subjects": subjects_list
    }


@router.post("/grade-subject-configs", response_model=GradeSubjectConfigResponse, status_code=201)
async def create_grade_subject_config(
    config_in: GradeSubjectConfigCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_district_admin),
) -> Any:
    """创建年级考试科目配置 (仅区县管理员)"""
    # 验证年级存在
    grade_result = await db.execute(select(Grade).where(Grade.id == config_in.grade_id))
    grade = grade_result.scalar_one_or_none()
    if not grade:
        raise HTTPException(status_code=404, detail="年级不存在")

    # 验证学科存在
    subject_result = await db.execute(select(Subject).where(Subject.id == config_in.subject_id))
    subject = subject_result.scalar_one_or_none()
    if not subject:
        raise HTTPException(status_code=404, detail="学科不存在")

    # 检查是否已存在相同年级+学科的配置
    existing_result = await db.execute(
        select(GradeSubjectConfig).where(
            GradeSubjectConfig.grade_id == config_in.grade_id,
            GradeSubjectConfig.subject_id == config_in.subject_id
        )
    )
    if existing_result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="该年级已配置此科目")

    # 创建配置
    config = GradeSubjectConfig(
        **config_in.model_dump(),
        created_by=current_user.id
    )
    db.add(config)
    await db.commit()
    await db.refresh(config)

    # 重新加载关联数据
    await db.refresh(config, ["grade", "subject"])

    # 构建响应
    response_dict = {
        "id": config.id,
        "grade_id": config.grade_id,
        "subject_id": config.subject_id,
        "full_score": config.full_score,
        "pass_line": config.pass_line,
        "excellent_line": config.excellent_line,
        "good_line": config.good_line,
        "is_active": config.is_active,
        "display_order": config.display_order,
        "description": config.description,
        "created_at": config.created_at,
        "updated_at": config.updated_at,
        "created_by": config.created_by,
        "grade_name": grade.name,
        "subject_name": subject.name,
        "subject_code": subject.code,
    }

    return response_dict


@router.post("/grade-subject-configs/bulk", response_model=List[GradeSubjectConfigResponse], status_code=201)
async def bulk_create_grade_subject_configs(
    bulk_in: BulkCreateGradeSubjectConfig,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_district_admin),
) -> Any:
    """批量创建年级考试科目配置 (仅区县管理员)"""
    created_configs = []

    for config_in in bulk_in.configs:
        # 验证年级存在
        grade_result = await db.execute(select(Grade).where(Grade.id == config_in.grade_id))
        grade = grade_result.scalar_one_or_none()
        if not grade:
            raise HTTPException(status_code=404, detail=f"年级ID {config_in.grade_id} 不存在")

        # 验证学科存在
        subject_result = await db.execute(select(Subject).where(Subject.id == config_in.subject_id))
        subject = subject_result.scalar_one_or_none()
        if not subject:
            raise HTTPException(status_code=404, detail=f"学科ID {config_in.subject_id} 不存在")

        # 检查是否已存在
        existing_result = await db.execute(
            select(GradeSubjectConfig).where(
                GradeSubjectConfig.grade_id == config_in.grade_id,
                GradeSubjectConfig.subject_id == config_in.subject_id
            )
        )
        if existing_result.scalar_one_or_none():
            continue  # 跳过已存在的配置

        # 创建配置
        config = GradeSubjectConfig(
            **config_in.model_dump(),
            created_by=current_user.id
        )
        db.add(config)
        created_configs.append((config, grade, subject))

    await db.commit()

    # 构建响应
    response_data = []
    for config, grade, subject in created_configs:
        await db.refresh(config)
        response_dict = {
            "id": config.id,
            "grade_id": config.grade_id,
            "subject_id": config.subject_id,
            "full_score": config.full_score,
            "pass_line": config.pass_line,
            "excellent_line": config.excellent_line,
            "good_line": config.good_line,
            "is_active": config.is_active,
            "display_order": config.display_order,
            "description": config.description,
            "created_at": config.created_at,
            "updated_at": config.updated_at,
            "created_by": config.created_by,
            "grade_name": grade.name,
            "subject_name": subject.name,
            "subject_code": subject.code,
        }
        response_data.append(response_dict)

    return response_data


@router.put("/grade-subject-configs/{config_id}", response_model=GradeSubjectConfigResponse)
async def update_grade_subject_config(
    config_id: int,
    config_in: GradeSubjectConfigUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_district_admin),
) -> Any:
    """更新年级考试科目配置 (仅区县管理员)"""
    result = await db.execute(
        select(GradeSubjectConfig)
        .options(selectinload(GradeSubjectConfig.grade), selectinload(GradeSubjectConfig.subject))
        .where(GradeSubjectConfig.id == config_id)
    )
    config = result.scalar_one_or_none()

    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")

    # 更新配置
    update_data = config_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(config, field, value)

    await db.commit()
    await db.refresh(config, ["grade", "subject"])

    # 构建响应
    response_dict = {
        "id": config.id,
        "grade_id": config.grade_id,
        "subject_id": config.subject_id,
        "full_score": config.full_score,
        "pass_line": config.pass_line,
        "excellent_line": config.excellent_line,
        "good_line": config.good_line,
        "is_active": config.is_active,
        "display_order": config.display_order,
        "description": config.description,
        "created_at": config.created_at,
        "updated_at": config.updated_at,
        "created_by": config.created_by,
    }

    if hasattr(config, 'grade') and config.grade:
        response_dict["grade_name"] = config.grade.name
    if hasattr(config, 'subject') and config.subject:
        response_dict["subject_name"] = config.subject.name
        response_dict["subject_code"] = config.subject.code

    return response_dict


@router.delete("/grade-subject-configs/{config_id}", status_code=204)
async def delete_grade_subject_config(
    config_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_district_admin),
) -> None:
    """删除年级考试科目配置 (仅区县管理员)"""
    result = await db.execute(select(GradeSubjectConfig).where(GradeSubjectConfig.id == config_id))
    config = result.scalar_one_or_none()

    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")

    await db.delete(config)
    await db.commit()


@router.patch("/grade-subject-configs/{config_id}/toggle", response_model=GradeSubjectConfigResponse)
async def toggle_grade_subject_config(
    config_id: int,
    is_active: bool,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_district_admin),
) -> Any:
    """启用/禁用年级考试科目配置 (仅区县管理员)"""
    result = await db.execute(
        select(GradeSubjectConfig)
        .options(selectinload(GradeSubjectConfig.grade), selectinload(GradeSubjectConfig.subject))
        .where(GradeSubjectConfig.id == config_id)
    )
    config = result.scalar_one_or_none()

    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")

    config.is_active = is_active
    await db.commit()
    await db.refresh(config, ["grade", "subject"])

    # 构建响应
    response_dict = {
        "id": config.id,
        "grade_id": config.grade_id,
        "subject_id": config.subject_id,
        "full_score": config.full_score,
        "pass_line": config.pass_line,
        "excellent_line": config.excellent_line,
        "good_line": config.good_line,
        "is_active": config.is_active,
        "display_order": config.display_order,
        "description": config.description,
        "created_at": config.created_at,
        "updated_at": config.updated_at,
        "created_by": config.created_by,
    }

    if hasattr(config, 'grade') and config.grade:
        response_dict["grade_name"] = config.grade.name
    if hasattr(config, 'subject') and config.subject:
        response_dict["subject_name"] = config.subject.name
        response_dict["subject_code"] = config.subject.code

    return response_dict
