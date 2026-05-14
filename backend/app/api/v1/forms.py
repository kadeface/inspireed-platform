"""
Forms API - 互动表单接口
"""

from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text

from app.core.database import get_db
from app.core.auth import get_current_active_user
from app.models.user import User, UserRole
from app.models.form_cell import FormCell, FormResponse
from app.schemas.form_cell import (
    FormCellCreate,
    FormCellUpdate,
    FormCellResponse,
    FormResponseCreate,
    FormResponseResponse,
    FormResults,
    FormOptionResponse,
)


router = APIRouter(prefix="/forms", tags=["forms"])


# ==================== Helper Functions ====================


def validate_form_access(form_cell: FormCell, current_user: User) -> None:
    """
    验证用户对表单的访问权限

    Args:
        form_cell: 表单单元格实例
        current_user: 当前用户

    Raises:
        HTTPException: 权限不足时抛出 403 错误
    """
    # 只有创建者（教师）可以修改/删除表单
    if form_cell.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有表单创建者可以执行此操作"
        )


def validate_answers_format(
    answers: List[Dict[str, Any]],
    cell_type: str,
    options: List[Dict[str, Any]]
) -> None:
    """
    验证答案格式是否符合表单类型要求

    Args:
        answers: 用户提交的答案列表
        cell_type: 表单类型
        options: 表单选项列表

    Raises:
        HTTPException: 答案格式不正确时抛出 400 错误
    """
    if not answers:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="答案不能为空"
        )

    option_ids = {opt.get("id") for opt in options if opt.get("id")}

    if cell_type == "single_choice":
        # 单选：只有一个答案，且必须是有效选项
        if len(answers) != 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="单选题只能选择一个选项"
            )
        if answers[0].get("option_id") not in option_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="选项ID无效"
            )

    elif cell_type == "multiple_choice":
        # 多选：至少一个答案，所有选项ID必须有效
        if len(answers) < 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="多选题至少选择一个选项"
            )
        answer_option_ids = {ans.get("option_id") for ans in answers}
        invalid_ids = answer_option_ids - option_ids
        if invalid_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"选项ID无效: {invalid_ids}"
            )

    elif cell_type == "ranking":
        # 排序：所有选项都必须排序，且order不能重复
        if len(answers) != len(option_ids):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"排序题必须对所有{len(option_ids)}个选项进行排序"
            )
        answer_option_ids = {ans.get("option_id") for ans in answers}
        if answer_option_ids != option_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="排序题必须包含所有选项"
            )
        orders = [ans.get("order", 0) for ans in answers]
        if len(orders) != len(set(orders)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="排序值不能重复"
            )


# ==================== CRUD Endpoints ====================


@router.post("/", response_model=FormCellResponse, status_code=status.HTTP_201_CREATED)
async def create_form(
    form_data: FormCellCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> FormCell:
    """
    创建互动表单

    Args:
        form_data: 表单创建数据
        current_user: 当前用户（需教师权限）
        db: 数据库会话

    Returns:
        FormCellResponse: 创建的表单详情

    Raises:
        HTTPException: 权限不足时抛出 403 错误
    """
    # 只有教师可以创建表单
    if current_user.role != UserRole.TEACHER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有教师可以创建表单"
        )

    # 验证至少有2个选项
    if len(form_data.options) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="表单至少需要2个选项"
        )

    # 构造选项数据（不包含ID，由数据库生成）
    options_data = [
        {
            "id": f"opt_{i}",  # 临时ID，前端可能需要
            "text": opt.text,
            "order": opt.order,
            "image_url": opt.image_url
        }
        for i, opt in enumerate(form_data.options)
    ]

    # 创建表单
    form_cell = FormCell(
        cell_type=form_data.cell_type,
        title=form_data.title,
        description=form_data.description,
        options=options_data,
        settings=form_data.settings,
        time_limit=form_data.time_limit,
        created_by=current_user.id
    )

    db.add(form_cell)
    await db.commit()
    await db.refresh(form_cell)

    return form_cell


@router.get("/{form_cell_id}", response_model=FormCellResponse)
async def get_form(
    form_cell_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> FormCell:
    """
    获取表单详情

    Args:
        form_cell_id: 表单ID
        current_user: 当前用户
        db: 数据库会话

    Returns:
        FormCellResponse: 表单详情

    Raises:
        HTTPException: 表单不存在时抛出 404 错误
    """
    result = await db.execute(
        select(FormCell).where(FormCell.id == form_cell_id)
    )
    form_cell = result.scalar_one_or_none()

    if not form_cell:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="表单不存在"
        )

    return form_cell


@router.put("/{form_cell_id}", response_model=FormCellResponse)
async def update_form(
    form_cell_id: int,
    form_data: FormCellUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> FormCell:
    """
    更新表单配置

    Args:
        form_cell_id: 表单ID
        form_data: 更新数据
        current_user: 当前用户
        db: 数据库会话

    Returns:
        FormCellResponse: 更新后的表单详情

    Raises:
        HTTPException: 表单不存在或权限不足时抛出错误
    """
    result = await db.execute(
        select(FormCell).where(FormCell.id == form_cell_id)
    )
    form_cell = result.scalar_one_or_none()

    if not form_cell:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="表单不存在"
        )

    # 验证权限
    validate_form_access(form_cell, current_user)

    # 如果更新选项，验证至少有2个
    if form_data.options is not None and len(form_data.options) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="表单至少需要2个选项"
        )

    # 更新字段
    update_data = form_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field == "options" and value is not None:
            # 重新构造选项数据
            value = [
                {
                    "id": f"opt_{i}",
                    "text": opt.text,
                    "order": opt.order,
                    "image_url": opt.image_url
                }
                for i, opt in enumerate(value)
            ]
        setattr(form_cell, field, value)

    await db.commit()
    await db.refresh(form_cell)

    return form_cell


@router.delete("/{form_cell_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_form(
    form_cell_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> None:
    """
    删除表单

    Args:
        form_cell_id: 表单ID
        current_user: 当前用户
        db: 数据库会话

    Raises:
        HTTPException: 表单不存在或权限不足时抛出错误
    """
    result = await db.execute(
        select(FormCell).where(FormCell.id == form_cell_id)
    )
    form_cell = result.scalar_one_or_none()

    if not form_cell:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="表单不存在"
        )

    # 验证权限
    validate_form_access(form_cell, current_user)

    await db.delete(form_cell)
    await db.commit()


# ==================== Student Endpoints ====================


@router.post("/{form_cell_id}/submit", response_model=FormResponseResponse, status_code=status.HTTP_201_CREATED)
async def submit_form_response(
    form_cell_id: int,
    response_data: FormResponseCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> FormResponse:
    """
    学生提交表单答案

    Args:
        form_cell_id: 表单ID
        response_data: 答案数据
        current_user: 当前用户
        db: 数据库会话

    Returns:
        FormResponseResponse: 提交的答案详情

    Raises:
        HTTPException: 表单不存在或答案格式错误时抛出错误
    """
    # 获取表单
    result = await db.execute(
        select(FormCell).where(FormCell.id == form_cell_id)
    )
    form_cell = result.scalar_one_or_none()

    if not form_cell:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="表单不存在"
        )

    # 验证答案格式
    validate_answers_format(
        response_data.answers,
        form_cell.cell_type,
        form_cell.options
    )

    # 创建答案记录
    form_response = FormResponse(
        form_cell_id=form_cell_id,
        user_id=current_user.id,
        answers=response_data.answers,
        session_id=response_data.session_id
    )

    db.add(form_response)
    await db.commit()
    await db.refresh(form_response)

    return form_response


@router.get("/{form_cell_id}/results", response_model=FormResults)
async def get_form_results(
    form_cell_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> FormResults:
    """
    获取表单结果统计

    Args:
        form_cell_id: 表单ID
        current_user: 当前用户
        db: 数据库会话

    Returns:
        FormResults: 表单统计结果

    Raises:
        HTTPException: 表单不存在时抛出 404 错误
    """
    # 获取表单
    result = await db.execute(
        select(FormCell).where(FormCell.id == form_cell_id)
    )
    form_cell = result.scalar_one_or_none()

    if not form_cell:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="表单不存在"
    )

    # 获取总回答数
    count_result = await db.execute(
        select(func.count(FormResponse.id))
        .where(FormResponse.form_cell_id == form_cell_id)
    )
    total_responses = count_result.scalar() or 0

    # 根据表单类型计算选项统计
    cell_type = form_cell.cell_type
    options = form_cell.options

    if cell_type == "single_choice":
        # 单选：计算每个选项的选择次数
        option_stats = []
        for opt in options:
            opt_id = opt.get("id")
            # 使用 jsonb_array_elements 展开数组，然后过滤
            count_query = """
                SELECT COUNT(*)
                FROM form_responses
                WHERE form_cell_id = :form_cell_id
                AND EXISTS (
                    SELECT 1
                    FROM jsonb_array_elements(answers) AS ans
                    WHERE ans->>'option_id' = :opt_id
                )
            """
            count_result = await db.execute(
                text(count_query),
                {"form_cell_id": form_cell_id, "opt_id": opt_id}
            )
            count = count_result.scalar() or 0
            percentage = (count / total_responses * 100) if total_responses > 0 else 0
            option_stats.append({
                "option_id": opt_id,
                "text": opt.get("text"),
                "count": count,
                "percentage": round(percentage, 2)
            })

    elif cell_type == "multiple_choice":
        # 多选：计算每个选项的选择次数
        option_stats = []
        for opt in options:
            opt_id = opt.get("id")
            count_query = """
                SELECT COUNT(*)
                FROM form_responses
                WHERE form_cell_id = :form_cell_id
                AND EXISTS (
                    SELECT 1
                    FROM jsonb_array_elements(answers) AS ans
                    WHERE ans->>'option_id' = :opt_id
                )
            """
            count_result = await db.execute(
                text(count_query),
                {"form_cell_id": form_cell_id, "opt_id": opt_id}
            )
            count = count_result.scalar() or 0
            percentage = (count / total_responses * 100) if total_responses > 0 else 0
            option_stats.append({
                "option_id": opt_id,
                "text": opt.get("text"),
                "count": count,
                "percentage": round(percentage, 2)
            })

    elif cell_type == "ranking":
        # 排序：计算每个选项的平均排名
        option_stats = []
        for opt in options:
            opt_id = opt.get("id")
            # 计算该选项的平均order值
            avg_query = """
                SELECT AVG(CAST((ans->>'order') AS NUMERIC))
                FROM form_responses,
                     jsonb_array_elements(answers) AS ans
                WHERE form_cell_id = :form_cell_id
                AND ans->>'option_id' = :opt_id
            """
            avg_result = await db.execute(
                text(avg_query),
                {"form_cell_id": form_cell_id, "opt_id": opt_id}
            )
            avg_rank = avg_result.scalar() or 0
            option_stats.append({
                "option_id": opt_id,
                "text": opt.get("text"),
                "average_rank": round(float(avg_rank), 2)
            })

    else:
        # 未知类型，返回空统计
        option_stats = []

    # 计算响应率（这里简化为100%，因为没有记录总参与人数）
    response_rate = 100.0

    return FormResults(
        form_cell_id=form_cell_id,
        total_responses=total_responses,
        option_stats=option_stats,
        response_rate=response_rate
    )
