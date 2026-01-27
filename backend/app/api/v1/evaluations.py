"""
增值评价API

提供首尾对比评价的创建、查询和管理功能
"""

import logging
from typing import Any, Optional, List
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, and_
from fastapi import APIRouter, Depends, HTTPException, status, Query

from app.api.deps import get_db, get_current_active_user
from app.models import User, ValueAddedEvaluation, UserRole
from app.schemas.evaluation import (
    ValueAddedEvaluationCreate,
    ValueAddedEvaluationResponse,
    ValueAddedEvaluationSummary,
)
from app.services.value_added_evaluation_service import (
    ValueAddedEvaluationService,
    RateMetricsCalculator,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/", response_model=ValueAddedEvaluationResponse, status_code=status.HTTP_201_CREATED)
async def create_value_added_evaluation(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    evaluation_in: ValueAddedEvaluationCreate,
) -> Any:
    """
    创建增值评价（首尾对比）

    权限说明：
    - 管理员、区县管理员、学校管理员、教研员可以创建评价

    计算流程：
    1. 选择基线考试和结束考试
    2. 选择评价范围（区县/学校/班级）
    3. 选择科目
    4. 计算各率指标（优秀率、优良率、合格率、低分率）
    5. 计算增值 = 结束值 - 基线值
    6. 保存评价结果和明细
    """
    # 权限检查
    if current_user.role not in [
        UserRole.ADMIN,
        UserRole.DISTRICT_ADMIN,
        UserRole.SCHOOL_ADMIN,
        UserRole.RESEARCHER,
    ]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有管理员和教研员可以创建评价"
        )

    try:
        evaluation = await ValueAddedEvaluationService.calculate_value_added_evaluation(
            db=db,
            name=evaluation_in.name,
            baseline_exam_id=evaluation_in.baseline_exam_id,
            endline_exam_id=evaluation_in.endline_exam_id,
            subject_id=evaluation_in.subject_id,
            scope_type=evaluation_in.scope_type,
            scope_id=evaluation_in.scope_id,
            region_id=evaluation_in.region_id,
            school_id=evaluation_in.school_id,
            classroom_id=evaluation_in.classroom_id,
            created_by=current_user.id,
            metrics=evaluation_in.metrics,
            score_lines=evaluation_in.score_lines,
        )
        return evaluation

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"创建评价失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建评价失败: {str(e)}"
        )


@router.get("/{evaluation_id}", response_model=ValueAddedEvaluationSummary)
async def get_evaluation_summary(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    evaluation_id: int,
) -> Any:
    """
    获取评价汇总信息

    返回评价的详细汇总，包括基线、结束指标和增值情况
    """
    # 权限检查：所有登录用户都可以查看评价
    try:
        summary = await ValueAddedEvaluationService.get_evaluation_summary(
            db, evaluation_id
        )
        return summary

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"获取评价汇总失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取评价汇总失败: {str(e)}"
        )


@router.get("/", response_model=list[ValueAddedEvaluationResponse])
async def list_evaluations(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(50, ge=1, le=100, description="返回记录数"),
    scope_type: Optional[str] = Query(None, description="范围类型筛选"),
    subject_id: Optional[int] = Query(None, description="科目ID筛选"),
    baseline_exam_id: Optional[int] = Query(None, description="基线考试ID筛选"),
    endline_exam_id: Optional[int] = Query(None, description="结束考试ID筛选"),
) -> Any:
    """
    获取评价列表

    权限说明：
    - 管理员、教研员：可查看所有评价
    - 其他用户：只能查看相关范围的评价
    """
    # 构建查询条件
    conditions = []

    # 根据角色限制数据访问
    if current_user.role == UserRole.STUDENT:
        # 学生不能查看评价
        return []
    elif current_user.role == UserRole.TEACHER:
        # 教师只能查看所教班级的评价
        # TODO: 根据教师的任教班级筛选
        pass

    # 应用筛选条件
    if scope_type:
        conditions.append(ValueAddedEvaluation.scope_type == scope_type)

    if subject_id:
        conditions.append(ValueAddedEvaluation.subject_id == subject_id)

    if baseline_exam_id:
        conditions.append(ValueAddedEvaluation.baseline_exam_id == baseline_exam_id)

    if endline_exam_id:
        conditions.append(ValueAddedEvaluation.endline_exam_id == endline_exam_id)

    # 执行查询
    if conditions:
        query = select(ValueAddedEvaluation).where(
            and_(*conditions)
        ).order_by(desc(ValueAddedEvaluation.created_at)).offset(skip).limit(limit)
    else:
        query = select(ValueAddedEvaluation).order_by(
            desc(ValueAddedEvaluation.created_at)
        ).offset(skip).limit(limit)

    result = await db.execute(query)
    evaluations = result.scalars().all()

    return evaluations


@router.post("/batch", status_code=status.HTTP_201_CREATED)
async def batch_create_evaluations(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    name: str = Query(..., description="评价名称（基础）"),
    baseline_exam_id: int = Query(..., description="基线考试ID"),
    endline_exam_id: int = Query(..., description="结束考试ID"),
    subject_id: int = Query(..., description="科目ID"),
    school_id: int = Query(..., description="学校ID"),
    classroom_ids: Optional[List[int]] = Query(None, description="班级ID列表"),
) -> Any:
    """
    批量创建班级评价

    为学校的一个或多个班级同时创建增值评价

    权限说明：
    - 管理员、区县管理员、学校管理员可以批量创建
    """
    # 权限检查
    if current_user.role not in [
        UserRole.ADMIN,
        UserRole.DISTRICT_ADMIN,
        UserRole.SCHOOL_ADMIN,
    ]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有管理员可以批量创建评价"
        )

    try:
        evaluations = await ValueAddedEvaluationService.batch_evaluate_classrooms(
            db=db,
            name=name,
            baseline_exam_id=baseline_exam_id,
            endline_exam_id=endline_exam_id,
            subject_id=subject_id,
            school_id=school_id,
            created_by=current_user.id,
            classroom_ids=classroom_ids,
        )

        return {
            "message": f"成功创建 {len(evaluations)} 个评价",
            "evaluation_ids": [eval.id for eval in evaluations],
        }

    except Exception as e:
        logger.error(f"批量创建评价失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"批量创建评价失败: {str(e)}"
        )


@router.get("/metrics/calculate")
async def calculate_metrics(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    exam_id: int = Query(..., description="考试ID"),
    subject_id: int = Query(..., description="科目ID"),
    scope_type: str = Query(..., description="范围类型"),
    scope_id: Optional[int] = Query(None, description="范围ID"),
) -> Any:
    """
    计算指定考试的率指标

    用于快速查看某个考试、科目、范围的率指标情况
    """
    try:
        metrics = await RateMetricsCalculator.calculate_exam_metrics(
            db=db,
            exam_id=exam_id,
            subject_id=subject_id,
            scope_type=scope_type,
            scope_id=scope_id,
        )
        return metrics

    except Exception as e:
        logger.error(f"计算率指标失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"计算率指标失败: {str(e)}"
        )


@router.delete("/{evaluation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_evaluation(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    evaluation_id: int,
) -> None:
    """
    删除评价

    权限说明：
    - 管理员、区县管理员可以删除任何评价
    - 学校管理员只能删除本校的评价
    - 创建者可以删除自己创建的评价
    """
    # 查询评价
    result = await db.execute(
        select(ValueAddedEvaluation).where(ValueAddedEvaluation.id == evaluation_id)
    )
    evaluation = result.scalar_one_or_none()

    if not evaluation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="评价不存在"
        )

    # 权限检查
    if current_user.role not in [UserRole.ADMIN, UserRole.DISTRICT_ADMIN]:
        if current_user.role == UserRole.SCHOOL_ADMIN:
            if evaluation.school_id != current_user.school_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="只能删除本校的评价"
                )
        elif evaluation.created_by != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只能删除自己创建的评价"
            )

    # 删除评价（级联删除明细）
    await db.delete(evaluation)
    await db.commit()
