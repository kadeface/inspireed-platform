"""
日常表现成绩API

提供日常表现成绩的CRUD操作和计算功能
"""

from datetime import datetime
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, and_

from app.api.deps import get_db, get_current_active_user
from app.models import User, DailyPerformanceScore, Classroom
from app.schemas.evaluation import (
    DailyPerformanceScoreCreate,
    DailyPerformanceScoreUpdate,
    DailyPerformanceScoreResponse,
    DailyPerformanceScoreCalculate,
    DailyPerformanceScoreBatchCalculate,
)
from app.services.daily_performance_calculator import DailyPerformanceCalculator

router = APIRouter()


@router.post("/calculate", response_model=DailyPerformanceScoreResponse, status_code=status.HTTP_201_CREATED)
async def calculate_daily_performance(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    calculation_params: DailyPerformanceScoreCalculate,
) -> Any:
    """
    为单个学生计算日常表现成绩

    需要教师或管理员权限
    """
    # 权限检查：只有教师和管理员可以计算
    if current_user.role not in ["admin", "district_admin", "school_admin", "teacher"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有教师和管理员可以计算日常表现成绩"
        )

    # 验证班级是否存在
    classroom_result = await db.execute(
        select(Classroom).where(Classroom.id == calculation_params.classroom_id)
    )
    classroom = classroom_result.scalar_one_or_none()
    if not classroom:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="班级不存在"
        )

    # 检查是否已存在相同周期的成绩记录
    existing_result = await db.execute(
        select(DailyPerformanceScore).where(
            and_(
                DailyPerformanceScore.student_id == calculation_params.student_id,
                DailyPerformanceScore.classroom_id == calculation_params.classroom_id,
                DailyPerformanceScore.period_name == calculation_params.period_name
            )
        )
    )
    existing = existing_result.scalar_one_or_none()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"该学生在{calculation_params.period_name}的成绩记录已存在"
        )

    # 计算成绩
    score = await DailyPerformanceCalculator.calculate_for_student(
        session=db,
        student_id=calculation_params.student_id,
        classroom_id=calculation_params.classroom_id,
        start_date=calculation_params.start_date,
        end_date=calculation_params.end_date,
        period_name=calculation_params.period_name,
        semester_id=calculation_params.semester_id,
        weights=calculation_params.weights,
        created_by=current_user.id
    )

    # 保存到数据库
    db.add(score)
    await db.commit()
    await db.refresh(score)

    return score


@router.post("/batch-calculate", response_model=list[DailyPerformanceScoreResponse])
async def batch_calculate_daily_performance(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    params: DailyPerformanceScoreBatchCalculate,
) -> Any:
    """
    批量为班级计算日常表现成绩

    需要教师或管理员权限
    """
    # 权限检查：只有教师和管理员可以计算
    if current_user.role not in ["admin", "district_admin", "school_admin", "teacher"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有教师和管理员可以计算日常表现成绩"
        )

    # 验证班级是否存在
    classroom_result = await db.execute(
        select(Classroom).where(Classroom.id == params.classroom_id)
    )
    classroom = classroom_result.scalar_one_or_none()
    if not classroom:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="班级不存在"
        )

    # 批量计算成绩
    scores = await DailyPerformanceCalculator.batch_calculate_for_classroom(
        session=db,
        classroom_id=params.classroom_id,
        start_date=params.start_date,
        end_date=params.end_date,
        period_name=params.period_name,
        semester_id=params.semester_id,
        weights=params.weights,
        created_by=current_user.id
    )

    # 批量保存
    db.add_all(scores)
    await db.commit()

    # 刷新所有记录
    for score in scores:
        await db.refresh(score)

    return scores


@router.get("/", response_model=list[DailyPerformanceScoreResponse])
async def list_daily_performance_scores(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(100, ge=1, le=100, description="返回记录数"),
    student_id: Optional[int] = Query(None, description="学生ID"),
    classroom_id: Optional[int] = Query(None, description="班级ID"),
    semester_id: Optional[int] = Query(None, description="学期ID"),
) -> Any:
    """
    获取日常表现成绩列表

    权限说明：
    - 管理员：可查看所有记录
    - 教师：只能查看本班记录
    - 学生：只能查看本人记录
    """
    # 构建查询条件
    conditions = []

    # 根据角色限制数据访问
    if current_user.role == "student":
        # 学生只能查看自己的记录
        conditions.append(DailyPerformanceScore.student_id == current_user.id)
    elif current_user.role == "teacher":
        # 教师只能查看所教班级的记录
        if not classroom_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="教师必须指定班级ID"
            )
        # TODO: 验证教师是否任教该班级
        conditions.append(DailyPerformanceScore.classroom_id == classroom_id)
    # 管理员可查看所有记录

    # 应用筛选条件
    if student_id:
        if current_user.role == "student" and student_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="学生只能查看自己的记录"
            )
        conditions.append(DailyPerformanceScore.student_id == student_id)

    if classroom_id:
        conditions.append(DailyPerformanceScore.classroom_id == classroom_id)

    if semester_id:
        conditions.append(DailyPerformanceScore.semester_id == semester_id)

    # 执行查询
    if conditions:
        query = select(DailyPerformanceScore).where(
            and_(*conditions)
        ).order_by(desc(DailyPerformanceScore.created_at)).offset(skip).limit(limit)
    else:
        query = select(DailyPerformanceScore).order_by(
            desc(DailyPerformanceScore.created_at)
        ).offset(skip).limit(limit)

    result = await db.execute(query)
    scores = result.scalars().all()

    return scores


@router.get("/{score_id}", response_model=DailyPerformanceScoreResponse)
async def get_daily_performance_score(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    score_id: int,
) -> Any:
    """
    获取单个日常表现成绩记录
    """
    result = await db.execute(
        select(DailyPerformanceScore).where(DailyPerformanceScore.id == score_id)
    )
    score = result.scalar_one_or_none()

    if not score:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="成绩记录不存在"
        )

    # 权限检查
    if current_user.role == "student" and score.student_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只能查看自己的记录"
        )

    return score


@router.put("/{score_id}", response_model=DailyPerformanceScoreResponse)
async def update_daily_performance_score(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    score_id: int,
    score_in: DailyPerformanceScoreUpdate,
) -> Any:
    """
    更新日常表现成绩记录

    只有创建者和管理员可以更新
    """
    result = await db.execute(
        select(DailyPerformanceScore).where(DailyPerformanceScore.id == score_id)
    )
    score = result.scalar_one_or_none()

    if not score:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="成绩记录不存在"
        )

    # 权限检查：只有创建者和管理员可以更新
    if current_user.role not in ["admin", "district_admin", "school_admin"]:
        if score.created_by != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有创建者和管理员可以更新成绩记录"
            )

    # 更新字段
    update_data = score_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(score, field, value)

    await db.commit()
    await db.refresh(score)

    return score


@router.delete("/{score_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_daily_performance_score(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    score_id: int,
) -> None:
    """
    删除日常表现成绩记录

    只有创建者和管理员可以删除
    """
    result = await db.execute(
        select(DailyPerformanceScore).where(DailyPerformanceScore.id == score_id)
    )
    score = result.scalar_one_or_none()

    if not score:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="成绩记录不存在"
        )

    # 权限检查：只有管理员可以删除
    if current_user.role not in ["admin", "district_admin", "school_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有管理员可以删除成绩记录"
        )

    await db.delete(score)
    await db.commit()

    return None


@router.get("/students/{student_id}/history", response_model=list[DailyPerformanceScoreResponse])
async def get_student_performance_history(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    student_id: int,
    semester_id: Optional[int] = Query(None, description="学期ID"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
) -> Any:
    """
    获取学生的日常表现成绩历史记录
    """
    # 权限检查
    if current_user.role == "student" and student_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只能查看自己的记录"
        )

    # 构建查询条件
    conditions = [DailyPerformanceScore.student_id == student_id]

    if semester_id:
        conditions.append(DailyPerformanceScore.semester_id == semester_id)

    # 执行查询
    result = await db.execute(
        select(DailyPerformanceScore)
        .where(and_(*conditions))
        .order_by(desc(DailyPerformanceScore.created_at))
        .offset(skip)
        .limit(limit)
    )
    scores = result.scalars().all()

    return scores


@router.get("/classrooms/{classroom_id}/statistics")
async def get_classroom_performance_statistics(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    classroom_id: int,
    period_name: Optional[str] = Query(None, description="统计周期名称"),
) -> Any:
    """
    获取班级日常表现统计信息

    返回：
    - 总人数、平均分
    - 各等级人数和百分比
    - 各维度平均分
    """
    # 权限检查：只有教师和管理员可以查看班级统计
    if current_user.role not in ["admin", "district_admin", "school_admin", "teacher"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有教师和管理员可以查看班级统计"
        )

    # 构建查询条件
    conditions = [DailyPerformanceScore.classroom_id == classroom_id]

    if period_name:
        conditions.append(DailyPerformanceScore.period_name == period_name)

    # 执行查询
    result = await db.execute(
        select(DailyPerformanceScore).where(and_(*conditions))
    )
    scores = result.scalars().all()

    if not scores:
        return {
            "classroom_id": classroom_id,
            "total_count": 0,
            "average_score": 0,
            "grade_distribution": {},
            "dimension_averages": {}
        }

    # 统计各项数据
    total_count = len(scores)
    average_score = sum(s.final_score for s in scores) / total_count

    # 等级分布
    grade_distribution = {
        "优秀": sum(1 for s in scores if s.grade_level == "优秀"),
        "良好": sum(1 for s in scores if s.grade_level == "良好"),
        "合格": sum(1 for s in scores if s.grade_level == "合格"),
        "不合格": sum(1 for s in scores if s.grade_level == "不合格"),
    }

    # 各维度平均分
    dimension_averages = {}
    if scores and scores[0].detail_scores:
        detail_keys = ["attendance_score", "behavior_score", "discipline_score", "duty_score"]
        for key in detail_keys:
            values = [s.detail_scores.get(key, 0) for s in scores if s.detail_scores]
            if values:
                dimension_averages[key] = round(sum(values) / len(values), 2)

    return {
        "classroom_id": classroom_id,
        "period_name": period_name,
        "total_count": total_count,
        "average_score": round(average_score, 2),
        "grade_distribution": {
            "优秀": f"{grade_distribution['优秀']}人 ({grade_distribution['优秀']/total_count*100:.1f}%)",
            "良好": f"{grade_distribution['良好']}人 ({grade_distribution['良好']/total_count*100:.1f}%)",
            "合格": f"{grade_distribution['合格']}人 ({grade_distribution['合格']/total_count*100:.1f}%)",
            "不合格": f"{grade_distribution['不合格']}人 ({grade_distribution['不合格']/total_count*100:.1f}%)",
        },
        "dimension_averages": dimension_averages,
    }
