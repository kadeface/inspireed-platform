"""
Analytics API endpoints for value-added analysis
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.evaluation import Score, Exam
from app.models.user import User
from app.models.organization import School
from app.models.curriculum import Subject

router = APIRouter()


@router.get("/analytics/student-growth/{student_id_number}")
async def get_student_growth(
    student_id_number: str,
    subject_id: Optional[int] = Query(None, description="科目ID筛选"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get student's historical scores for growth analysis

    Uses student_id_number for cross-school tracking

    Args:
        student_id_number: 学籍号/身份证号
        subject_id: 可选的科目ID，用于筛选特定科目的成绩
        db: 数据库会话

    Returns:
        {
            "student_id_number": "学籍号",
            "scores": [
                {
                    "exam_name": "考试名称",
                    "exam_date": "考试日期",
                    "subject": "科目名称",
                    "raw_score": 原始分,
                    "standard_score": 标准分,
                    "school": "学校名称",
                    "growth": 增长值（与前一次考试的差值）
                }
            ]
        }
    """
    # 构建查询 - 使用 student_id_number 追踪学生
    query = (
        select(Score)
        .join(Exam)
        .join(User, Score.student_id == User.id)
        .filter(Score.student_id_number == student_id_number)
    )

    # 如果指定了科目，添加科目过滤
    if subject_id:
        query = query.filter(Score.subject_id == subject_id)

    # 按考试日期排序
    query = query.order_by(Exam.exam_date)

    # 执行查询
    scores_result = await db.execute(query)
    scores = scores_result.scalars().all()

    # 如果没有找到成绩，返回空列表
    if not scores:
        return {
            "student_id_number": student_id_number,
            "scores": []
        }

    # 计算增长数据
    growth_data = []
    for i, score in enumerate(scores):
        # 获取关联的学校信息（通过学生）
        # 注意：需要使用 selectinload 或者在查询中 join School
        # 为了简化，我们通过 student 关联获取
        student_query = select(User).where(User.id == score.student_id)
        student_result = await db.execute(student_query)
        student = student_result.scalar_one_or_none()

        school_name = None
        if student and student.school_id:
            school_query = select(School).where(School.id == student.school_id)
            school_result = await db.execute(school_query)
            school = school_result.scalar_one_or_none()
            if school:
                school_name = school.name

        # 获取科目信息
        subject_query = select(Subject).where(Subject.id == score.subject_id)
        subject_result = await db.execute(subject_query)
        subject = subject_result.scalar_one_or_none()
        subject_name = subject.name if subject else "未知科目"

        # 计算增长值（与上一次考试的差值）
        growth = None
        if i > 0:
            growth = score.raw_score - scores[i-1].raw_score

        growth_data.append({
            "exam_name": score.exam.name,
            "exam_date": score.exam.exam_date.isoformat() if score.exam.exam_date else None,
            "subject": subject_name,
            "raw_score": score.raw_score,
            "standard_score": score.standard_score,
            "school": school_name,
            "growth": growth
        })

    return {
        "student_id_number": student_id_number,
        "scores": growth_data
    }
