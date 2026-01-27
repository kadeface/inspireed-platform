"""
数据中心API

提供考试统计数据和分析报告
"""

import logging
from typing import Any, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, case
from sqlalchemy.orm import selectinload

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field

from app.api.deps import get_db, get_current_active_user
from app.models import User, UserRole
from app.models.evaluation import (
    Exam,
    ExamSubject,
    Score,
    EvaluationMetric,
    MetricCategory,
)
from app.models.organization import School, Classroom, Region
from app.models.curriculum import Subject, Grade

router = APIRouter()
logger = logging.getLogger(__name__)


# ==================== Schema 定义 ====================

class SubjectStatistics(BaseModel):
    """科目统计"""

    subject_id: int
    subject_name: str
    subject_code: str
    full_score: int
    average_score: float
    max_score: int
    min_score: int
    student_count: int
    excellent_rate: float = Field(..., description="优秀率")
    good_rate: float = Field(..., description="优良率")
    pass_rate: float = Field(..., description="合格率")
    low_rate: float = Field(..., description="低分率")


class SchoolStatistics(BaseModel):
    """学校统计"""

    school_id: int
    school_name: str
    school_code: str
    student_count: int
    class_count: int
    subjects: List[SubjectStatistics]


class ClassroomStatistics(BaseModel):
    """班级统计"""

    classroom_id: int
    classroom_name: str
    school_name: str
    student_count: int
    subjects: List[SubjectStatistics]


class ExamOverview(BaseModel):
    """考试概览"""

    exam_id: int
    exam_name: str
    exam_type: str
    exam_level: str
    exam_date: str
    grade_name: str
    semester_name: str

    # 整体统计
    total_students: int
    total_schools: int
    total_classes: int
    total_subjects: int

    # 科目统计
    subject_statistics: List[SubjectStatistics]


class DistrictExamStatistics(BaseModel):
    """区县统考统计数据"""

    overview: ExamOverview
    school_statistics: List[SchoolStatistics]
    classroom_statistics: List[ClassroomStatistics]


class SchoolExamStatistics(BaseModel):
    """校级考试统计数据"""

    overview: ExamOverview
    classroom_statistics: List[ClassroomStatistics]


# ==================== 辅助函数 ====================

async def get_exam_with_details(db: AsyncSession, exam_id: int) -> Exam:
    """获取考试详细信息"""
    result = await db.execute(
        select(Exam)
        .options(
            selectinload(Exam.exam_subjects).selectinload(ExamSubject.subject),
            selectinload(Exam.grade),
            selectinload(Exam.semester),
            selectinload(Exam.region),
            selectinload(Exam.school),
        )
        .where(Exam.id == exam_id)
    )
    exam = result.scalar_one_or_none()
    if not exam:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"考试 {exam_id} 不存在"
        )
    return exam


async def calculate_subject_statistics(
    db: AsyncSession,
    exam_id: int,
    subject_id: int,
    scope_type: str = "all",
    scope_id: Optional[int] = None,
) -> SubjectStatistics:
    """计算科目统计数据"""

    # 获取科目配置
    exam_subject_result = await db.execute(
        select(ExamSubject, Subject)
        .join(Subject, ExamSubject.subject_id == Subject.id)
        .where(
            and_(
                ExamSubject.exam_id == exam_id,
                ExamSubject.subject_id == subject_id,
            )
        )
    )
    row = exam_subject_result.first()
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"考试 {exam_id} 的科目 {subject_id} 配置不存在"
        )
    exam_subject, subject = row

    # 构建查询
    query = select(
        func.count(Score.student_id).label("student_count"),
        func.avg(Score.raw_score).label("avg_score"),
        func.max(Score.raw_score).label("max_score"),
        func.min(Score.raw_score).label("min_score"),
    ).where(
        and_(
            Score.exam_id == exam_id,
            Score.subject_id == subject_id,
            Score.is_absent == False,
            Score.is_cheated == False,
        )
    )

    # 根据范围过滤
    if scope_type == "school" and scope_id:
        # 通过学生关联合过滤学校
        query = query.join(User, Score.student_id == User.id).where(User.school_id == scope_id)
    elif scope_type == "classroom" and scope_id:
        query = query.where(Score.student_id.in_(
            select(User.id).where(User.classroom_id == scope_id)
        ))

    result = await db.execute(query)
    stats = result.one()

    if stats.student_count == 0:
        return SubjectStatistics(
            subject_id=subject.id,
            subject_name=subject.name,
            subject_code=subject.code,
            full_score=exam_subject.full_score,
            average_score=0,
            max_score=0,
            min_score=0,
            student_count=0,
            excellent_rate=0,
            good_rate=0,
            pass_rate=0,
            low_rate=0,
        )

    # 计算率指标
    excellent_line = exam_subject.excellent_line or 85
    good_line = exam_subject.good_line or 75
    pass_line = exam_subject.pass_line or 60

    rate_query = select(
        func.sum(
            case(
                (Score.raw_score >= excellent_line, 1),
                else_=0
            )
        ).label("excellent_count"),
        func.sum(
            case(
                (Score.raw_score >= good_line, 1),
                else_=0
            )
        ).label("good_count"),
        func.sum(
            case(
                (Score.raw_score >= pass_line, 1),
                else_=0
            )
        ).label("pass_count"),
        func.sum(
            case(
                (Score.raw_score < pass_line, 1),
                else_=0
            )
        ).label("low_count"),
    ).where(
        and_(
            Score.exam_id == exam_id,
            Score.subject_id == subject_id,
            Score.is_absent == False,
            Score.is_cheated == False,
        )
    )

    # 根据范围过滤
    if scope_type == "school" and scope_id:
        rate_query = rate_query.join(User, Score.student_id == User.id).where(User.school_id == scope_id)
    elif scope_type == "classroom" and scope_id:
        rate_query = rate_query.where(Score.student_id.in_(
            select(User.id).where(User.classroom_id == scope_id)
        ))

    rate_result = await db.execute(rate_query)
    rates = rate_result.one()

    total = stats.student_count
    return SubjectStatistics(
        subject_id=subject.id,
        subject_name=subject.name,
        subject_code=subject.code,
        full_score=exam_subject.full_score,
        average_score=round(float(stats.avg_score or 0), 2),
        max_score=int(stats.max_score or 0),
        min_score=int(stats.min_score or 0),
        student_count=int(stats.student_count),
        excellent_rate=round(float((rates.excellent_count or 0) / total * 100), 2),
        good_rate=round(float((rates.good_count or 0) / total * 100), 2),
        pass_rate=round(float((rates.pass_count or 0) / total * 100), 2),
        low_rate=round(float((rates.low_count or 0) / total * 100), 2),
    )


# ==================== API 端点 ====================

@router.get("/exams/{exam_id}/statistics/overview", response_model=ExamOverview)
async def get_exam_overview(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    exam_id: int,
) -> Any:
    """
    获取考试概览数据

    包含整体统计和各科目统计
    """
    # 获取考试信息
    exam = await get_exam_with_details(db, exam_id)

    # 获取统计学生数
    student_subq = (
        select(Score.student_id)
        .where(
            and_(
                Score.exam_id == exam_id,
                Score.is_absent == False,
                Score.is_cheated == False,
            )
        )
        .distinct()
    )
    student_result = await db.execute(select(func.count()).select_from(student_subq))
    total_students = student_result.scalar() or 0

    # 获取统计学校数
    if exam.exam_level == "school":
        total_schools = 1
    else:
        school_subq = (
            select(User.school_id)
            .where(User.id.in_(student_subq))
            .distinct()
        )
        school_result = await db.execute(select(func.count()).select_from(school_subq))
        total_schools = school_result.scalar() or 0

    # 获取统计班级数
    class_subq = (
        select(User.classroom_id)
        .where(User.id.in_(student_subq))
        .distinct()
    )
    class_result = await db.execute(select(func.count()).select_from(class_subq))
    total_classes = class_result.scalar() or 0

    # 计算各科目统计
    subject_statistics = []
    for exam_subject in exam.exam_subjects:
        stats = await calculate_subject_statistics(db, exam_id, exam_subject.subject_id)
        subject_statistics.append(stats)

    return ExamOverview(
        exam_id=exam.id,
        exam_name=exam.name,
        exam_type=exam.exam_type,
        exam_level=exam.exam_level,
        exam_date=exam.exam_date.isoformat(),
        grade_name=exam.grade.name if exam.grade else "",
        semester_name=exam.semester.name if exam.semester else "",
        total_students=total_students,
        total_schools=total_schools,
        total_classes=total_classes,
        total_subjects=len(exam.exam_subjects),
        subject_statistics=subject_statistics,
    )


@router.get("/exams/{exam_id}/statistics/district", response_model=DistrictExamStatistics)
async def get_district_exam_statistics(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    exam_id: int,
) -> Any:
    """
    获取区县统考统计数据

    包含：
    - 整体概览
    - 各学校统计
    - 各班级统计
    """
    # 获取考试信息
    exam = await get_exam_with_details(db, exam_id)

    if exam.exam_level == "school":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="校级考试不能使用区县统计接口"
        )

    # 获取概览
    overview = await get_exam_overview(
        db=db, current_user=current_user, exam_id=exam_id
    )

    # 获取参与的学生
    student_subq = (
        select(Score.student_id)
        .where(
            and_(
                Score.exam_id == exam_id,
                Score.is_absent == False,
                Score.is_cheated == False,
            )
        )
        .distinct()
    )

    # 获取各学校统计
    school_result = await db.execute(
        select(User.school_id)
        .where(User.id.in_(student_subq))
        .distinct()
        .order_by(User.school_id)
    )
    school_ids = [row[0] for row in school_result.all()]

    school_statistics = []
    for school_id in school_ids:
        # 获取学校信息
        school_query_result = await db.execute(select(School).where(School.id == school_id))
        school = school_query_result.scalar_one_or_none()
        if not school:
            continue

        # 获取学校的学生和班级数
        school_student_count_result = await db.execute(
            select(func.count())
            .select_from(select(User.id).where(User.school_id == school_id).distinct().subquery())
        )
        school_student_count = school_student_count_result.scalar() or 0

        school_class_result = await db.execute(
            select(func.count())
            .select_from(
                select(User.classroom_id)
                .where(User.school_id == school_id)
                .distinct()
                .subquery()
            )
        )
        school_class_count = school_class_result.scalar() or 0

        # 计算各科目统计
        subjects = []
        for exam_subject in exam.exam_subjects:
            stats = await calculate_subject_statistics(
                db, exam_id, exam_subject.subject_id, scope_type="school", scope_id=school_id
            )
            subjects.append(stats)

        school_statistics.append(
            SchoolStatistics(
                school_id=school.id,
                school_name=school.name,
                school_code=school.code,
                student_count=school_student_count,
                class_count=school_class_count,
                subjects=subjects,
            )
        )

    # 获取各班级统计
    class_result = await db.execute(
        select(User.classroom_id)
        .where(User.id.in_(student_subq))
        .distinct()
        .order_by(User.classroom_id)
    )
    class_ids = [row[0] for row in class_result.all()]

    classroom_statistics = []
    for classroom_id in class_ids:
        # 获取班级信息
        classroom_query_result = await db.execute(
            select(Classroom, School)
            .join(School, Classroom.school_id == School.id)
            .where(Classroom.id == classroom_id)
        )
        row = classroom_query_result.first()
        if not row:
            continue
        classroom, school = row

        # 获取班级学生数
        class_student_count_result = await db.execute(
            select(func.count())
            .select_from(
                select(User.id)
                .where(User.classroom_id == classroom_id)
                .distinct()
                .subquery()
            )
        )
        class_student_count = class_student_count_result.scalar() or 0

        # 计算各科目统计
        subjects = []
        for exam_subject in exam.exam_subjects:
            stats = await calculate_subject_statistics(
                db, exam_id, exam_subject.subject_id, scope_type="classroom", scope_id=classroom_id
            )
            subjects.append(stats)

        classroom_statistics.append(
            ClassroomStatistics(
                classroom_id=classroom.id,
                classroom_name=classroom.name,
                school_name=school.name,
                student_count=class_student_count,
                subjects=subjects,
            )
        )

    return DistrictExamStatistics(
        overview=overview,
        school_statistics=school_statistics,
        classroom_statistics=classroom_statistics,
    )


@router.get("/exams/{exam_id}/statistics/school", response_model=SchoolExamStatistics)
async def get_school_exam_statistics(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    exam_id: int,
) -> Any:
    """
    获取校级考试统计数据

    包含：
    - 整体概览
    - 各班级统计
    """
    # 获取考试信息
    exam = await get_exam_with_details(db, exam_id)

    # 获取概览
    overview = await get_exam_overview(
        db=db, current_user=current_user, exam_id=exam_id
    )

    # 获取参与的学生
    student_subq = (
        select(Score.student_id)
        .where(
            and_(
                Score.exam_id == exam_id,
                Score.is_absent == False,
                Score.is_cheated == False,
            )
        )
        .distinct()
    )

    # 获取各班级统计
    class_result = await db.execute(
        select(User.classroom_id)
        .where(User.id.in_(student_subq))
        .distinct()
        .order_by(User.classroom_id)
    )
    class_ids = [row[0] for row in class_result.all()]

    classroom_statistics = []
    for classroom_id in class_ids:
        # 获取班级信息
        classroom_query_result = await db.execute(
            select(Classroom, School)
            .join(School, Classroom.school_id == School.id)
            .where(Classroom.id == classroom_id)
        )
        row = classroom_query_result.first()
        if not row:
            continue
        classroom, school = row

        # 获取班级学生数
        class_student_count_result = await db.execute(
            select(func.count())
            .select_from(
                select(User.id)
                .where(User.classroom_id == classroom_id)
                .distinct()
                .subquery()
            )
        )
        class_student_count = class_student_count_result.scalar() or 0

        # 计算各科目统计
        subjects = []
        for exam_subject in exam.exam_subjects:
            stats = await calculate_subject_statistics(
                db, exam_id, exam_subject.subject_id, scope_type="classroom", scope_id=classroom_id
            )
            subjects.append(stats)

        classroom_statistics.append(
            ClassroomStatistics(
                classroom_id=classroom.id,
                classroom_name=classroom.name,
                school_name=school.name,
                student_count=class_student_count,
                subjects=subjects,
            )
        )

    return SchoolExamStatistics(
        overview=overview,
        classroom_statistics=classroom_statistics,
    )
