"""
高中总分评价API

提供高中学生总分成绩的CRUD操作和统计分析
"""

from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, and_

from app.api.deps import get_db, get_current_active_user
from app.models import User, ExamTotalScore, Exam, StudentType
from app.schemas.evaluation import (
    ExamTotalScoreCreate,
    ExamTotalScoreUpdate,
    ExamTotalScoreResponse,
    ExamTotalScoreBatchCreate,
)
from app.services.total_score_calculator import TotalScoreCalculator

router = APIRouter()


@router.post("/", response_model=ExamTotalScoreResponse, status_code=status.HTTP_201_CREATED)
async def create_total_score(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    score_in: ExamTotalScoreCreate,
) -> Any:
    """
    创建高中总分评价记录

    需要教师或管理员权限
    """
    # 权限检查：只有教师和管理员可以创建
    if current_user.role not in ["admin", "district_admin", "school_admin", "teacher"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有教师和管理员可以创建总分评价记录"
        )

    # 验证考试是否存在
    exam_result = await db.execute(
        select(Exam).where(Exam.id == score_in.exam_id)
    )
    exam = exam_result.scalar_one_or_none()
    if not exam:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="考试不存在"
        )

    # 检查学生类型是否有效
    try:
        student_type = StudentType(score_in.student_type)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"无效的学生类型: {score_in.student_type}，必须是 none/arts/science"
        )

    # 使用TotalScoreCalculator创建记录
    total_score = await TotalScoreCalculator.create_total_score(
        session=db,
        exam_id=score_in.exam_id,
        student_id=score_in.student_id,
        total_score=score_in.total_score,
        student_type=student_type,
        score_lines={
            "c9_line": score_in.c9_line,
            "special_control_line": score_in.special_control_line,
            "undergraduate_line": score_in.undergraduate_line,
            "junior_college_line": score_in.junior_college_line,
        } if any([score_in.c9_line, score_in.special_control_line,
                 score_in.undergraduate_line, score_in.junior_college_line]) else None,
        created_by=current_user.id
    )

    # 保存到数据库
    db.add(total_score)
    await db.commit()
    await db.refresh(total_score)

    return total_score


@router.post("/batch", response_model=list[ExamTotalScoreResponse])
async def batch_create_total_scores(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    batch_in: ExamTotalScoreBatchCreate,
) -> Any:
    """
    批量创建高中总分评价记录

    需要教师或管理员权限
    """
    # 权限检查：只有教师和管理员可以创建
    if current_user.role not in ["admin", "district_admin", "school_admin", "teacher"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有教师和管理员可以创建总分评价记录"
        )

    # 验证考试是否存在
    exam_result = await db.execute(
        select(Exam).where(Exam.id == batch_in.exam_id)
    )
    exam = exam_result.scalar_one_or_none()
    if not exam:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="考试不存在"
        )

    # 批量创建记录
    total_scores = await TotalScoreCalculator.batch_create_for_exam(
        session=db,
        exam_id=batch_in.exam_id,
        scores_data=batch_in.scores,
        created_by=current_user.id
    )

    # 批量保存
    db.add_all(total_scores)
    await db.commit()

    # 刷新所有记录
    for score in total_scores:
        await db.refresh(score)

    return total_scores


@router.get("/", response_model=list[ExamTotalScoreResponse])
async def list_total_scores(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(100, ge=1, le=100, description="返回记录数"),
    exam_id: Optional[int] = Query(None, description="考试ID"),
    student_id: Optional[int] = Query(None, description="学生ID"),
    student_type: Optional[str] = Query(None, description="学生类型"),
) -> Any:
    """
    获取高中总分评价列表

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
        conditions.append(ExamTotalScore.student_id == current_user.id)
    elif current_user.role == "teacher":
        # 教师必须指定考试ID
        if not exam_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="教师必须指定考试ID"
            )
        # TODO: 验证教师是否任教该考试涉及的班级

    # 应用筛选条件
    if student_id:
        if current_user.role == "student" and student_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="学生只能查看自己的记录"
            )
        conditions.append(ExamTotalScore.student_id == student_id)

    if exam_id:
        conditions.append(ExamTotalScore.exam_id == exam_id)

    if student_type:
        # 验证学生类型是否有效
        try:
            StudentType(student_type)
            conditions.append(ExamTotalScore.student_type == student_type)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"无效的学生类型: {student_type}"
            )

    # 执行查询
    if conditions:
        query = select(ExamTotalScore).where(
            and_(*conditions)
        ).order_by(desc(ExamTotalScore.total_score)).offset(skip).limit(limit)
    else:
        query = select(ExamTotalScore).order_by(
            desc(ExamTotalScore.total_score)
        ).offset(skip).limit(limit)

    result = await db.execute(query)
    scores = result.scalars().all()

    return scores


@router.get("/{score_id}", response_model=ExamTotalScoreResponse)
async def get_total_score(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    score_id: int,
) -> Any:
    """
    获取单个高中总分评价记录
    """
    result = await db.execute(
        select(ExamTotalScore).where(ExamTotalScore.id == score_id)
    )
    score = result.scalar_one_or_none()

    if not score:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="总分评价记录不存在"
        )

    # 权限检查
    if current_user.role == "student" and score.student_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只能查看自己的记录"
        )

    return score


@router.put("/{score_id}", response_model=ExamTotalScoreResponse)
async def update_total_score(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    score_id: int,
    score_in: ExamTotalScoreUpdate,
) -> Any:
    """
    更新高中总分评价记录

    只有创建者和管理员可以更新
    """
    result = await db.execute(
        select(ExamTotalScore).where(ExamTotalScore.id == score_id)
    )
    score = result.scalar_one_or_none()

    if not score:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="总分评价记录不存在"
        )

    # 权限检查：只有创建者和管理员可以更新
    if current_user.role not in ["admin", "district_admin", "school_admin"]:
        if score.created_by != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有创建者和管理员可以更新总分评价记录"
            )

    # 验证学生类型（如果提供）
    if score_in.student_type:
        try:
            StudentType(score_in.student_type)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"无效的学生类型: {score_in.student_type}"
            )

    # 更新字段
    update_data = score_in.model_dump(exclude_unset=True)

    # 如果更新了分数线，需要重新计算达标情况
    if any(key in update_data for key in ["c9_line", "special_control_line",
                                          "undergraduate_line", "junior_college_line",
                                          "total_score"]):
        # 获取更新后的总分（如果提供）
        new_total_score = update_data.get("total_score", score.total_score)

        # 获取更新后的分数线（如果提供）
        new_c9_line = update_data.get("c9_line", score.c9_line)
        new_special_control_line = update_data.get("special_control_line", score.special_control_line)
        new_undergraduate_line = update_data.get("undergraduate_line", score.undergraduate_line)
        new_junior_college_line = update_data.get("junior_college_line", score.junior_college_line)

        # 重新计算达标情况
        if new_c9_line is not None:
            score.reached_c9 = new_total_score >= new_c9_line
        if new_special_control_line is not None:
            score.reached_special_control = new_total_score >= new_special_control_line
        if new_undergraduate_line is not None:
            score.reached_undergraduate = new_total_score >= new_undergraduate_line
        if new_junior_college_line is not None:
            score.reached_junior_college = new_total_score >= new_junior_college_line

    # 应用其他字段更新
    for field, value in update_data.items():
        if field not in ["c9_line", "special_control_line", "undergraduate_line", "junior_college_line", "total_score"]:
            setattr(score, field, value)

    await db.commit()
    await db.refresh(score)

    return score


@router.delete("/{score_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_total_score(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    score_id: int,
) -> None:
    """
    删除高中总分评价记录

    只有管理员可以删除
    """
    result = await db.execute(
        select(ExamTotalScore).where(ExamTotalScore.id == score_id)
    )
    score = result.scalar_one_or_none()

    if not score:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="总分评价记录不存在"
        )

    # 权限检查：只有管理员可以删除
    if current_user.role not in ["admin", "district_admin", "school_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有管理员可以删除总分评价记录"
        )

    await db.delete(score)
    await db.commit()

    return None


@router.get("/exams/{exam_id}/statistics")
async def get_exam_statistics(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    exam_id: int,
    student_type: Optional[str] = Query(None, description="学生类型筛选"),
) -> Any:
    """
    获取考试的总分统计信息

    返回：
    - 总人数、平均分、最高分、最低分
    - 各分数线达标人数和百分比
    - 分数段分布
    """
    # 权限检查：所有登录用户都可以查看统计
    # 验证学生类型（如果提供）
    student_type_enum = None
    if student_type:
        try:
            student_type_enum = StudentType(student_type)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"无效的学生类型: {student_type}"
            )

    # 获取统计信息
    stats = await TotalScoreCalculator.get_exam_statistics(
        session=db,
        exam_id=exam_id,
        student_type=student_type_enum
    )

    return stats


@router.get("/students/{student_id}/history", response_model=list[ExamTotalScoreResponse])
async def get_student_total_score_history(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    student_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
) -> Any:
    """
    获取学生的高考总分历史记录
    """
    # 权限检查
    if current_user.role == "student" and student_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只能查看自己的记录"
        )

    # 执行查询
    result = await db.execute(
        select(ExamTotalScore)
        .where(ExamTotalScore.student_id == student_id)
        .order_by(desc(ExamTotalScore.created_at))
        .offset(skip)
        .limit(limit)
    )
    scores = result.scalars().all()

    return scores


@router.get("/exams/{exam_id}/ranking")
async def get_exam_ranking(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    exam_id: int,
    student_type: Optional[str] = Query(None, description="学生类型筛选"),
    top_n: int = Query(50, ge=1, le=100, description="返回前N名"),
) -> Any:
    """
    获取考试总分排名

    返回前N名的学生成绩
    """
    # 权限检查：所有登录用户都可以查看排名

    # 构建查询条件
    conditions = [ExamTotalScore.exam_id == exam_id]

    if student_type:
        try:
            StudentType(student_type)
            conditions.append(ExamTotalScore.student_type == student_type)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"无效的学生类型: {student_type}"
            )

    # 执行查询
    result = await db.execute(
        select(ExamTotalScore)
        .where(and_(*conditions))
        .order_by(desc(ExamTotalScore.total_score))
        .limit(top_n)
    )
    scores = result.scalars().all()

    # 添加排名信息
    ranking = []
    for idx, score in enumerate(scores, start=1):
        ranking.append({
            "rank": idx,
            "student_id": score.student_id,
            "total_score": score.total_score,
            "student_type": score.student_type,
            "grade_level": TotalScoreCalculator.get_grade_level(
                score.total_score,
                StudentType(score.student_type)
            ),
            "reached_c9": score.reached_c9,
            "reached_special_control": score.reached_special_control,
            "reached_undergraduate": score.reached_undergraduate,
            "reached_junior_college": score.reached_junior_college,
        })

    return {
        "exam_id": exam_id,
        "student_type": student_type,
        "total_count": len(scores),
        "ranking": ranking
    }
