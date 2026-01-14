"""
考试管理API

提供考试的CRUD操作
"""

from typing import Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, and_
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, Query

from app.api.deps import get_db, get_current_active_user
from app.models import User, Exam, UserRole, Semester
from app.schemas.evaluation import (
    ExamCreate,
    ExamUpdate,
    ExamResponse,
    ExamSubjectCreate,
    ExamSubjectResponse,
)

router = APIRouter()


@router.post("/", response_model=ExamResponse, status_code=status.HTTP_201_CREATED)
async def create_exam(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    exam_in: ExamCreate,
) -> Any:
    """
    创建新考试

    需要管理员权限
    """
    # 权限检查：只有管理员可以创建考试
    if current_user.role not in [UserRole.ADMIN, UserRole.DISTRICT_ADMIN, UserRole.SCHOOL_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有管理员可以创建考试"
        )

    # 验证学期是否存在
    semester_result = await db.execute(
        select(Semester).where(Semester.id == exam_in.semester_id)
    )
    semester = semester_result.scalar_one_or_none()
    if not semester:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="学期不存在"
        )

    # 创建考试
    exam = Exam(**exam_in.model_dump(), created_by=current_user.id)
    db.add(exam)
    await db.commit()
    await db.refresh(exam)

    return exam


@router.get("/", response_model=list[ExamResponse])
async def list_exams(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(100, ge=1, le=100, description="返回记录数"),
    semester_id: Optional[int] = Query(None, description="学期ID筛选"),
    exam_type: Optional[str] = Query(None, description="考试类型筛选"),
    status: Optional[str] = Query(None, description="状态筛选"),
    grade_id: Optional[int] = Query(None, description="年级ID筛选"),
    region_id: Optional[int] = Query(None, description="区县ID筛选"),
    school_id: Optional[int] = Query(None, description="学校ID筛选"),
) -> Any:
    """
    获取考试列表

    权限说明：
    - 管理员：可查看所有考试
    - 教研员：可查看所属区县/学校的考试
    - 教师：只能查看所教年级的考试
    - 学生：只能查看自己的考试
    """
    # 构建查询条件
    conditions = []

    # 根据角色限制数据访问
    if current_user.role == UserRole.STUDENT:
        # 学生只能查看自己年级和学校的考试
        if current_user.grade_id:
            conditions.append(Exam.grade_id == current_user.grade_id)
        if current_user.school_id:
            conditions.append(Exam.school_id == current_user.school_id)
    elif current_user.role == UserRole.TEACHER:
        # 教师只能查看所教年级的考试
        # TODO: 根据教师的任教年级筛选
        pass
    # 教研员和管理员可以查看更多数据

    # 应用筛选条件
    if semester_id:
        conditions.append(Exam.semester_id == semester_id)

    if exam_type:
        conditions.append(Exam.exam_type == exam_type)

    if status:
        conditions.append(Exam.status == status)

    if grade_id:
        conditions.append(Exam.grade_id == grade_id)

    if region_id:
        conditions.append(Exam.region_id == region_id)

    if school_id:
        conditions.append(Exam.school_id == school_id)

    # 执行查询
    if conditions:
        query = select(Exam).where(
            and_(*conditions)
        ).order_by(desc(Exam.exam_date)).offset(skip).limit(limit)
    else:
        query = select(Exam).order_by(
            desc(Exam.exam_date)
        ).offset(skip).limit(limit)

    result = await db.execute(query)
    exams = result.scalars().all()

    return exams


@router.get("/{exam_id}", response_model=ExamResponse)
async def get_exam(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    exam_id: int,
) -> Any:
    """
    获取单个考试详情
    """
    result = await db.execute(
        select(Exam).where(Exam.id == exam_id)
    )
    exam = result.scalar_one_or_none()

    if not exam:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="考试不存在"
        )

    # 权限检查
    # TODO: 根据角色检查数据访问权限

    return exam


@router.put("/{exam_id}", response_model=ExamResponse)
async def update_exam(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    exam_id: int,
    exam_in: ExamUpdate,
) -> Any:
    """
    更新考试信息

    需要管理员权限
    """
    # 权限检查：只有管理员和创建者可以更新考试
    result = await db.execute(
        select(Exam).where(Exam.id == exam_id)
    )
    exam = result.scalar_one_or_none()

    if not exam:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="考试不存在"
        )

    if current_user.role not in [UserRole.ADMIN, UserRole.DISTRICT_ADMIN, UserRole.SCHOOL_ADMIN]:
        if exam.created_by != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有创建者和管理员可以更新考试"
            )

    # 更新字段
    update_data = exam_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(exam, field, value)

    await db.commit()
    await db.refresh(exam)

    return exam


@router.delete("/{exam_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_exam(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    exam_id: int,
) -> None:
    """
    删除考试

    需要管理员权限
    """
    # 权限检查：只有管理员可以删除考试
    if current_user.role not in [UserRole.ADMIN, UserRole.DISTRICT_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有超级管理员和区县管理员可以删除考试"
        )

    result = await db.execute(
        select(Exam).where(Exam.id == exam_id)
    )
    exam = result.scalar_one_or_none()

    if not exam:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="考试不存在"
        )

    # TODO: 检查是否有关联的成绩，如果有则提示用户先删除成绩

    await db.delete(exam)
    await db.commit()

    return None


@router.post("/{exam_id}/subjects", response_model=ExamSubjectResponse)
async def add_exam_subject(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    exam_id: int,
    subject_in: ExamSubjectCreate,
) -> Any:
    """
    为考试添加科目

    需要管理员权限
    """
    # 权限检查
    if current_user.role not in [UserRole.ADMIN, UserRole.DISTRICT_ADMIN, UserRole.SCHOOL_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有管理员可以添加考试科目"
        )

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

    # 创建考试科目关联
    from app.models import ExamSubject

    exam_subject = ExamSubject(
        exam_id=exam_id,
        **subject_in.model_dump()
    )
    db.add(exam_subject)
    await db.commit()
    await db.refresh(exam_subject)

    return exam_subject


@router.get("/{exam_id}/subjects", response_model=list[ExamSubjectResponse])
async def list_exam_subjects(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    exam_id: int,
) -> Any:
    """
    获取考试的所有科目
    """
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

    # 查询考试科目（包含科目名称）
    from app.models import ExamSubject, Subject
    from sqlalchemy.orm import selectinload

    result = await db.execute(
        select(ExamSubject)
        .options(selectinload(ExamSubject.subject))
        .where(ExamSubject.exam_id == exam_id)
        .order_by(ExamSubject.display_order, ExamSubject.id)
    )
    exam_subjects = result.scalars().all()

    # 构建响应，包含科目名称
    response = []
    for exam_subject in exam_subjects:
        # 通过relationship获取subject
        subject_name = exam_subject.subject.name if exam_subject.subject else None
        # 构建响应字典
        subject_dict = {
            'id': exam_subject.id,
            'exam_id': exam_subject.exam_id,
            'subject_id': exam_subject.subject_id,
            'full_score': exam_subject.full_score,
            'pass_line': exam_subject.pass_line,
            'excellent_line': exam_subject.excellent_line,
            'good_line': exam_subject.good_line,
            'display_order': exam_subject.display_order,
            'is_active': exam_subject.is_active,
            'created_at': exam_subject.created_at,
            'subject_name': subject_name,
        }
        response.append(subject_dict)

    return response
