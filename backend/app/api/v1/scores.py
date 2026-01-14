"""
成绩查询API

提供成绩的查询、统计和分析功能
"""

from typing import Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, and_, func, case
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, Query

from app.api.deps import get_db, get_current_active_user
from app.models import User, Exam, Score, UserRole, Subject
from app.schemas.evaluation import ScoreResponse

router = APIRouter()


@router.get("/", response_model=list[ScoreResponse])
async def list_scores(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(100, ge=1, le=100, description="返回记录数"),
    exam_id: Optional[int] = Query(None, description="考试ID筛选"),
    subject_id: Optional[int] = Query(None, description="科目ID筛选"),
    student_id: Optional[int] = Query(None, description="学生ID筛选"),
    min_score: Optional[float] = Query(None, description="最低分数筛选"),
    max_score: Optional[float] = Query(None, description="最高分数筛选"),
    grade_level: Optional[str] = Query(None, description="等级筛选"),
) -> Any:
    """
    获取成绩列表

    权限说明：
    - 管理员：可查看所有成绩
    - 教研员：可查看所属区县/学校的成绩
    - 教师：只能查看所教班级/年级的成绩
    - 学生：只能查看自己的成绩
    """
    # 构建查询条件
    conditions = []

    # 根据角色限制数据访问
    if current_user.role == UserRole.STUDENT:
        # 学生只能查看自己的成绩
        conditions.append(Score.student_id == current_user.id)
    elif current_user.role == UserRole.TEACHER:
        # 教师只能查看所教班级/年级的成绩
        # TODO: 根据教师的任教班级/年级筛选
        pass
    # 教研员和管理员可以查看更多数据

    # 应用筛选条件
    if student_id:
        if current_user.role == UserRole.STUDENT and student_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="学生只能查看自己的成绩"
            )
        conditions.append(Score.student_id == student_id)

    if exam_id:
        conditions.append(Score.exam_id == exam_id)

    if subject_id:
        conditions.append(Score.subject_id == subject_id)

    if min_score is not None:
        conditions.append(Score.raw_score >= min_score)

    if max_score is not None:
        conditions.append(Score.raw_score <= max_score)

    if grade_level:
        conditions.append(Score.grade_level == grade_level)

    # 执行查询
    if conditions:
        query = select(Score).where(
            and_(*conditions)
        ).order_by(desc(Score.raw_score)).offset(skip).limit(limit)
    else:
        query = select(Score).order_by(
            desc(Score.raw_score)
        ).offset(skip).limit(limit)

    result = await db.execute(query)
    scores = result.scalars().all()

    return scores


@router.get("/{score_id}", response_model=ScoreResponse)
async def get_score(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    score_id: int,
) -> Any:
    """
    获取单个成绩详情
    """
    result = await db.execute(
        select(Score).where(Score.id == score_id)
    )
    score = result.scalar_one_or_none()

    if not score:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="成绩不存在"
        )

    # 权限检查
    if current_user.role == UserRole.STUDENT and score.student_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只能查看自己的成绩"
        )

    return score


@router.get("/exams/{exam_id}/statistics")
async def get_exam_score_statistics(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    exam_id: int,
    subject_id: Optional[int] = Query(None, description="科目ID（可选，不填则统计总分）"),
) -> Any:
    """
    获取考试成绩统计

    返回：
    - 总人数、缺考人数、作弊人数
    - 平均分、最高分、最低分
    - 优秀率、优良率、及格率、低分率
    - 分数段分布
    """
    # 权限检查：所有登录用户都可以查看统计
    # 验证考试是否存在
    exam_result = await db.execute(
        select(Exam).where(Exam.id == exam_id)
    )
    exam = exam_result.scalar_one_or_none()
    if not exam:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="考试不存在"
        )

    # 构建查询条件
    conditions = [Score.exam_id == exam_id]

    if subject_id:
        conditions.append(Score.subject_id == subject_id)

    # 基础统计
    result = await db.execute(
        select(
            func.count(Score.id).label('total_count'),
            func.sum(case((Score.is_absent == True, 1), else_=0)).label('absent_count'),
            func.sum(case((Score.is_cheated == True, 1), else_=0)).label('cheated_count'),
            func.avg(Score.raw_score).label('average_score'),
            func.max(Score.raw_score).label('max_score'),
            func.min(Score.raw_score).label('min_score'),
        )
        .where(and_(*conditions))
    )
    stats = result.one()

    # 率指标统计（假设优秀线85，良好线75，及格线60）
    rate_result = await db.execute(
        select(
            func.sum(case((Score.raw_score >= 85, 1), else_=0)).label('excellent_count'),
            func.sum(case((Score.raw_score >= 75, 1), else_=0)).label('good_count'),
            func.sum(case((Score.raw_score >= 60, 1), else_=0)).label('pass_count'),
            func.sum(case((Score.raw_score < 60, 1), else_=0)).label('fail_count'),
        )
        .where(
            and_(*conditions, Score.is_absent == False, Score.is_cheated == False)
        )
    )
    rates = rate_result.one()

    total_valid = stats.total_count - (stats.absent_count or 0) - (stats.cheated_count or 0)

    # 分数段分布
    distribution_result = await db.execute(
        select(Score.raw_score)
        .where(
            and_(*conditions, Score.is_absent == False, Score.is_cheated == False)
        )
    )
    scores_list = [s[0] for s in distribution_result.all()]

    score_distribution = {
        "90-100": sum(1 for s in scores_list if s >= 90),
        "80-89": sum(1 for s in scores_list if 80 <= s < 90),
        "70-79": sum(1 for s in scores_list if 70 <= s < 80),
        "60-69": sum(1 for s in scores_list if 60 <= s < 70),
        "0-59": sum(1 for s in scores_list if s < 60),
    }

    return {
        "exam_id": exam_id,
        "subject_id": subject_id,
        "total_count": stats.total_count or 0,
        "absent_count": stats.absent_count or 0,
        "cheated_count": stats.cheated_count or 0,
        "valid_count": total_valid,
        "average_score": round(stats.average_score or 0, 2),
        "max_score": stats.max_score or 0,
        "min_score": stats.min_score or 0,
        "excellent_rate": round((rates.excellent_count or 0) / total_valid * 100, 2) if total_valid > 0 else 0,
        "good_rate": round((rates.good_count or 0) / total_valid * 100, 2) if total_valid > 0 else 0,
        "pass_rate": round((rates.pass_count or 0) / total_valid * 100, 2) if total_valid > 0 else 0,
        "fail_rate": round((rates.fail_count or 0) / total_valid * 100, 2) if total_valid > 0 else 0,
        "score_distribution": score_distribution,
    }


@router.get("/students/{student_id}/exams")
async def get_student_exam_scores(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    student_id: int,
    semester_id: Optional[int] = Query(None, description="学期ID筛选"),
) -> Any:
    """
    获取学生的所有考试成绩

    按考试分组返回
    """
    # 权限检查
    if current_user.role == UserRole.STUDENT and student_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只能查看自己的成绩"
        )

    # 构建查询条件
    conditions = [Score.student_id == student_id]

    if semester_id:
        # TODO: 通过exam关联查询semester_id
        pass

    # 查询成绩
    result = await db.execute(
        select(Score)
        .where(and_(*conditions))
        .order_by(desc(Score.exam_id), Score.subject_id)
    )
    scores = result.scalars().all()

    # 按考试分组
    from collections import defaultdict
    exams_scores = defaultdict(list)

    for score in scores:
        # 查询考试信息
        exam_result = await db.execute(
            select(Exam).where(Exam.id == score.exam_id)
        )
        exam = exam_result.scalar_one_or_none()
        if exam:
            exams_scores[exam.id].append({
                "exam_id": exam.id,
                "exam_name": exam.name,
                "exam_date": exam.exam_date,
                "exam_type": exam.exam_type,
                "subject_id": score.subject_id,
                "raw_score": score.raw_score,
                "standard_score": score.standard_score,
                "percentile": score.percentile,
                "grade_level": score.grade_level,
                "is_absent": score.is_absent,
                "is_cheated": score.is_cheated,
            })

    return {
        "student_id": student_id,
        "exams": list(exams_scores.values())
    }


@router.get("/classrooms/{classroom_id}/exams/{exam_id}")
async def get_classroom_exam_scores(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    classroom_id: int,
    exam_id: int,
    subject_id: Optional[int] = Query(None, description="科目ID筛选"),
) -> Any:
    """
    获取班级在某次考试中的成绩

    返回班级所有学生的成绩，按分数降序排列
    """
    # 权限检查：教师和管理员可以查看班级成绩
    if current_user.role not in [UserRole.ADMIN, UserRole.DISTRICT_ADMIN, UserRole.SCHOOL_ADMIN, UserRole.TEACHER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有教师和管理员可以查看班级成绩"
        )

    # TODO: 验证教师是否任教该班级

    # 查询班级所有学生ID
    from app.models import ClassroomMembership

    membership_result = await db.execute(
        select(ClassroomMembership.user_id)
        .where(
            and_(
                ClassroomMembership.classroom_id == classroom_id,
                ClassroomMembership.is_active == True
            )
        )
    )
    student_ids = [row[0] for row in membership_result.all()]

    if not student_ids:
        return {
            "classroom_id": classroom_id,
            "exam_id": exam_id,
            "subject_id": subject_id,
            "total_count": 0,
            "scores": []
        }

    # 构建查询条件
    conditions = [
        Score.exam_id == exam_id,
        Score.student_id.in_(student_ids)
    ]

    if subject_id:
        conditions.append(Score.subject_id == subject_id)

    # 查询成绩
    result = await db.execute(
        select(Score)
        .where(and_(*conditions))
        .order_by(desc(Score.raw_score))
    )
    scores = result.scalars().all()

    # 组装返回数据
    scores_data = []
    for score in scores:
        # 查询学生信息
        student_result = await db.execute(
            select(User).where(User.id == score.student_id)
        )
        student = student_result.scalar_one_or_none()

        scores_data.append({
            "score_id": score.id,
            "student_id": score.student_id,
            "student_name": student.full_name if student else "",
            "student_number": student.student_id_number if student else "",
            "subject_id": score.subject_id,
            "raw_score": score.raw_score,
            "standard_score": score.standard_score,
            "percentile": score.percentile,
            "grade_level": score.grade_level,
            "is_absent": score.is_absent,
            "is_cheated": score.is_cheated,
        })

    return {
        "classroom_id": classroom_id,
        "exam_id": exam_id,
        "subject_id": subject_id,
        "total_count": len(scores_data),
        "scores": scores_data
    }
