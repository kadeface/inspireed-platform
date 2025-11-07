"""
教学活动 API
"""

from datetime import datetime
from typing import List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload

from app.api import deps
from app.models.user import User, UserRole
from app.models.activity import (
    ActivitySubmission,
    ActivitySubmissionStatus,
    PeerReview,
    PeerReviewStatus,
    ActivityStatistics,
)
from app.models.lesson import Lesson
from app.models.cell import Cell
from app.schemas.activity import (
    ActivitySubmissionCreate,
    ActivitySubmissionUpdate,
    ActivitySubmissionSubmit,
    ActivitySubmissionGrade,
    ActivitySubmissionResponse,
    ActivitySubmissionWithStudent,
    PeerReviewCreate,
    PeerReviewUpdate,
    PeerReviewResponse,
    PeerReviewWithReviewer,
    PeerReviewAssignment,
    ActivityStatisticsResponse,
    BulkGradeRequest,
    BulkReturnRequest,
    OfflineSyncRequest,
    OfflineSyncResponse,
)

router = APIRouter()


# ========== 活动提交相关 API ==========

@router.post("/submissions", response_model=ActivitySubmissionResponse, status_code=201)
async def create_submission(
    data: ActivitySubmissionCreate,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """创建活动提交（或草稿）"""

    # 验证 Cell 存在
    cell = await db.get(Cell, data.cell_id)
    if not cell:
        raise HTTPException(status_code=404, detail="Cell 不存在")

    # 验证 Lesson 存在
    lesson = await db.get(Lesson, data.lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="教案不存在")

    # 检查是否已有提交（草稿）
    result = await db.execute(
        select(ActivitySubmission).where(
            and_(
                ActivitySubmission.cell_id == data.cell_id,
                ActivitySubmission.student_id == current_user.id,
                ActivitySubmission.status == ActivitySubmissionStatus.DRAFT,
            )
        )
    )
    existing = result.scalar_one_or_none()

    if existing:
        # 更新现有草稿
        existing.responses = data.responses
        existing.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(existing)
        return existing

    # 创建新提交
    submission = ActivitySubmission(
        cell_id=data.cell_id,
        lesson_id=data.lesson_id,
        student_id=current_user.id,
        responses=data.responses,
        status=ActivitySubmissionStatus.DRAFT,
        started_at=data.started_at or datetime.utcnow(),
    )

    db.add(submission)
    await db.commit()
    await db.refresh(submission)

    return submission


@router.get("/submissions/{submission_id}", response_model=ActivitySubmissionResponse)
async def get_submission(
    submission_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """获取单个活动提交"""

    submission = await db.get(ActivitySubmission, submission_id)
    if not submission:
        raise HTTPException(status_code=404, detail="提交不存在")

    # 权限检查：学生只能查看自己的，教师可以查看所有
    if current_user.role == UserRole.STUDENT and submission.student_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权访问")

    return submission


@router.patch("/submissions/{submission_id}", response_model=ActivitySubmissionResponse)
async def update_submission(
    submission_id: int,
    data: ActivitySubmissionUpdate,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """更新活动提交（草稿）"""

    submission = await db.get(ActivitySubmission, submission_id)
    if not submission:
        raise HTTPException(status_code=404, detail="提交不存在")

    # 只有学生本人可以更新草稿
    if submission.student_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权修改")

    # 已提交的不能再修改（除非允许多次提交）
    if submission.status != ActivitySubmissionStatus.DRAFT:
        raise HTTPException(status_code=400, detail="已提交的作业不能修改")

    # 更新字段
    if data.responses is not None:
        submission.responses = data.responses
    if data.status is not None:
        submission.status = data.status
    if data.time_spent is not None:
        submission.time_spent = data.time_spent

    submission.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(submission)

    return submission


@router.post("/submissions/{submission_id}/submit", response_model=ActivitySubmissionResponse)
async def submit_activity(
    submission_id: int,
    data: ActivitySubmissionSubmit,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """正式提交活动"""

    submission = await db.get(ActivitySubmission, submission_id)
    if not submission:
        raise HTTPException(status_code=404, detail="提交不存在")

    # 只有学生本人可以提交
    if submission.student_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权操作")

    # 更新提交数据
    submission.responses = data.responses
    submission.status = ActivitySubmissionStatus.SUBMITTED
    submission.submitted_at = datetime.utcnow()
    if data.time_spent:
        submission.time_spent = data.time_spent

    # TODO: 实现自动评分逻辑
    # 如果是选择题等可自动评分的题型，这里自动计算分数
    # submission.score = calculate_auto_score(submission.responses, cell_content)
    # submission.auto_graded = True

    await db.commit()
    await db.refresh(submission)

    # 更新统计数据
    await _update_statistics(db, submission.cell_id, submission.lesson_id)

    return submission


@router.get("/cells/{cell_id}/submissions", response_model=List[ActivitySubmissionWithStudent])
async def get_cell_submissions(
    cell_id: int,
    status: Optional[ActivitySubmissionStatus] = None,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """获取某个 Cell 的所有提交（教师端）"""

    # 只有教师可以查看
    if current_user.role != UserRole.TEACHER:
        raise HTTPException(status_code=403, detail="权限不足")

    # 构建查询
    query = (
        select(ActivitySubmission, User)
        .join(User, ActivitySubmission.student_id == User.id)
        .where(ActivitySubmission.cell_id == cell_id)
    )

    if status:
        query = query.where(ActivitySubmission.status == status)

    result = await db.execute(query)
    rows = result.all()

    # 组装响应
    submissions = []
    for submission, user in rows:
        submission_dict = {
            **submission.__dict__,
            "student_email": user.email,
            "student_name": user.full_name or user.username,
        }
        submissions.append(submission_dict)

    return submissions


@router.get("/lessons/{lesson_id}/my-submissions", response_model=List[ActivitySubmissionResponse])
async def get_my_lesson_submissions(
    lesson_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """获取我在某个教案中的所有活动提交（学生端）"""

    result = await db.execute(
        select(ActivitySubmission).where(
            and_(
                ActivitySubmission.lesson_id == lesson_id,
                ActivitySubmission.student_id == current_user.id,
            )
        )
    )
    submissions = result.scalars().all()

    return submissions


# ========== 评分相关 API ==========

@router.post("/submissions/{submission_id}/grade", response_model=ActivitySubmissionResponse)
async def grade_submission(
    submission_id: int,
    data: ActivitySubmissionGrade,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """评分"""

    # 只有教师可以评分
    if current_user.role != UserRole.TEACHER:
        raise HTTPException(status_code=403, detail="权限不足")

    submission = await db.get(ActivitySubmission, submission_id)
    if not submission:
        raise HTTPException(status_code=404, detail="提交不存在")

    if submission.status != ActivitySubmissionStatus.SUBMITTED:
        raise HTTPException(status_code=400, detail="只能评分已提交的作业")

    # 更新评分
    submission.score = data.score
    submission.teacher_feedback = data.teacher_feedback
    submission.graded_by = current_user.id
    submission.graded_at = datetime.utcnow()
    submission.status = ActivitySubmissionStatus.GRADED

    # 如果有分项分数，更新 responses 中的 score 字段
    if data.item_scores:
        for item_id, item_score in data.item_scores.items():
            if item_id in submission.responses:
                submission.responses[item_id]["score"] = item_score

    await db.commit()
    await db.refresh(submission)

    # 更新统计数据
    await _update_statistics(db, submission.cell_id, submission.lesson_id)

    return submission


@router.post("/submissions/bulk-grade", response_model=dict)
async def bulk_grade_submissions(
    data: BulkGradeRequest,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """批量评分"""

    if current_user.role != UserRole.TEACHER:
        raise HTTPException(status_code=403, detail="权限不足")

    graded_count = 0
    for submission_id in data.submission_ids:
        submission = await db.get(ActivitySubmission, submission_id)
        if submission and submission.status == ActivitySubmissionStatus.SUBMITTED:
            submission.score = data.score
            submission.teacher_feedback = data.teacher_feedback
            submission.graded_by = current_user.id
            submission.graded_at = datetime.utcnow()
            submission.status = ActivitySubmissionStatus.GRADED
            graded_count += 1

    await db.commit()

    return {"graded_count": graded_count}


# ========== 互评相关 API ==========

@router.post("/peer-reviews/assign", response_model=dict)
async def assign_peer_reviews(
    data: PeerReviewAssignment,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """分配互评任务（教师端）"""

    if current_user.role != UserRole.TEACHER:
        raise HTTPException(status_code=403, detail="权限不足")

    # 获取所有已提交的作业
    result = await db.execute(
        select(ActivitySubmission).where(
            and_(
                ActivitySubmission.cell_id == data.cell_id,
                ActivitySubmission.status == ActivitySubmissionStatus.SUBMITTED,
            )
        )
    )
    submissions = result.scalars().all()

    if len(submissions) < data.reviews_per_student + 1:
        raise HTTPException(
            status_code=400,
            detail=f"提交数量不足，至少需要 {data.reviews_per_student + 1} 份提交才能进行互评",
        )

    # 简单的分配算法：轮流分配
    assigned_count = 0
    for i, submission in enumerate(submissions):
        for j in range(1, data.reviews_per_student + 1):
            reviewer_index = (i + j) % len(submissions)
            reviewer_submission = submissions[reviewer_index]

            # 不能评价自己的作业
            if reviewer_submission.student_id == submission.student_id:
                continue

            # 检查是否已分配
            existing = await db.execute(
                select(PeerReview).where(
                    and_(
                        PeerReview.submission_id == submission.id,
                        PeerReview.reviewer_id == reviewer_submission.student_id,
                    )
                )
            )
            if existing.scalar_one_or_none():
                continue

            # 创建互评任务
            peer_review = PeerReview(
                submission_id=submission.id,
                reviewer_id=reviewer_submission.student_id,
                lesson_id=data.lesson_id,
                cell_id=data.cell_id,
                is_anonymous=data.is_anonymous,
            )
            db.add(peer_review)
            assigned_count += 1

    await db.commit()

    return {"assigned_count": assigned_count}


@router.get("/submissions/{submission_id}/peer-reviews", response_model=List[PeerReviewWithReviewer])
async def get_submission_peer_reviews(
    submission_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """获取某个提交收到的所有互评"""

    submission = await db.get(ActivitySubmission, submission_id)
    if not submission:
        raise HTTPException(status_code=404, detail="提交不存在")

    # 权限检查
    if current_user.role == UserRole.STUDENT and submission.student_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权访问")

    result = await db.execute(
        select(PeerReview, User)
        .join(User, PeerReview.reviewer_id == User.id)
        .where(PeerReview.submission_id == submission_id)
    )
    rows = result.all()

    reviews = []
    for review, user in rows:
        review_dict = {
            **review.__dict__,
            "reviewer_name": None if review.is_anonymous else (user.full_name or user.username),
        }
        reviews.append(review_dict)

    return reviews


@router.get("/my-peer-review-tasks", response_model=List[PeerReviewResponse])
async def get_my_peer_review_tasks(
    status: Optional[PeerReviewStatus] = None,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """获取我的互评任务（学生端）"""

    query = select(PeerReview).where(PeerReview.reviewer_id == current_user.id)

    if status:
        query = query.where(PeerReview.status == status)

    result = await db.execute(query)
    reviews = result.scalars().all()

    return reviews


@router.post("/peer-reviews/{review_id}/submit", response_model=PeerReviewResponse)
async def submit_peer_review(
    review_id: int,
    data: PeerReviewCreate,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """提交互评"""

    review = await db.get(PeerReview, review_id)
    if not review:
        raise HTTPException(status_code=404, detail="互评任务不存在")

    if review.reviewer_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权操作")

    # 更新互评数据
    review.review_data = data.review_data
    review.score = data.score
    review.comment = data.comment
    review.status = PeerReviewStatus.COMPLETED
    review.completed_at = datetime.utcnow()

    await db.commit()
    await db.refresh(review)

    return review


# ========== 统计相关 API ==========

@router.get("/cells/{cell_id}/statistics", response_model=ActivityStatisticsResponse)
async def get_cell_statistics(
    cell_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """获取活动统计数据"""

    if current_user.role != UserRole.TEACHER:
        raise HTTPException(status_code=403, detail="权限不足")

    result = await db.execute(
        select(ActivityStatistics).where(ActivityStatistics.cell_id == cell_id)
    )
    statistics = result.scalar_one_or_none()

    if not statistics:
        # 如果不存在，创建一个
        cell = await db.get(Cell, cell_id)
        if not cell:
            raise HTTPException(status_code=404, detail="Cell 不存在")

        statistics = ActivityStatistics(
            cell_id=cell_id,
            lesson_id=cell.lesson_id,
        )
        db.add(statistics)
        await db.commit()
        await db.refresh(statistics)

        # 立即计算统计数据
        await _update_statistics(db, cell_id, cell.lesson_id)

        # 重新加载
        result = await db.execute(
            select(ActivityStatistics).where(ActivityStatistics.cell_id == cell_id)
        )
        statistics = result.scalar_one()

    return statistics


# ========== 离线同步 API ==========

@router.post("/submissions/sync", response_model=OfflineSyncResponse)
async def sync_offline_submissions(
    data: OfflineSyncRequest,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """同步离线提交的数据"""

    synced_count = 0
    failed_count = 0
    conflicts = []

    for submission_data in data.submissions:
        try:
            # 查找现有提交
            result = await db.execute(
                select(ActivitySubmission).where(
                    and_(
                        ActivitySubmission.cell_id == submission_data["cell_id"],
                        ActivitySubmission.student_id == current_user.id,
                    )
                )
            )
            existing = result.scalar_one_or_none()

            if existing:
                # 检查版本冲突
                if existing.version > submission_data.get("version", 1):
                    conflicts.append(
                        {
                            "submission_id": existing.id,
                            "server_version": existing.version,
                            "client_version": submission_data.get("version", 1),
                        }
                    )
                    failed_count += 1
                    continue

                # 更新现有提交
                existing.responses = submission_data["responses"]
                existing.version += 1
                existing.synced = True
                existing.updated_at = datetime.utcnow()
                synced_count += 1
            else:
                # 创建新提交
                submission = ActivitySubmission(
                    cell_id=submission_data["cell_id"],
                    lesson_id=submission_data["lesson_id"],
                    student_id=current_user.id,
                    responses=submission_data["responses"],
                    status=ActivitySubmissionStatus.DRAFT,
                    synced=True,
                )
                db.add(submission)
                synced_count += 1

        except Exception as e:
            print(f"同步失败: {e}")
            failed_count += 1

    await db.commit()

    return OfflineSyncResponse(
        synced_count=synced_count,
        failed_count=failed_count,
        conflicts=conflicts,
    )


# ========== 辅助函数 ==========

async def _update_statistics(db: AsyncSession, cell_id: int, lesson_id: int):
    """更新活动统计数据"""

    # 查找或创建统计记录
    result = await db.execute(
        select(ActivityStatistics).where(ActivityStatistics.cell_id == cell_id)
    )
    statistics = result.scalar_one_or_none()

    if not statistics:
        statistics = ActivityStatistics(cell_id=cell_id, lesson_id=lesson_id)
        db.add(statistics)

    # 计算各种统计数据
    result = await db.execute(
        select(
            func.count(ActivitySubmission.id).label("total"),
            func.sum(
                func.cast(ActivitySubmission.status == ActivitySubmissionStatus.DRAFT, Integer)
            ).label("draft"),
            func.sum(
                func.cast(ActivitySubmission.status == ActivitySubmissionStatus.SUBMITTED, Integer)
            ).label("submitted"),
            func.sum(
                func.cast(ActivitySubmission.status == ActivitySubmissionStatus.GRADED, Integer)
            ).label("graded"),
            func.avg(ActivitySubmission.score).label("avg_score"),
            func.max(ActivitySubmission.score).label("max_score"),
            func.min(ActivitySubmission.score).label("min_score"),
            func.avg(ActivitySubmission.time_spent).label("avg_time"),
        ).where(ActivitySubmission.cell_id == cell_id)
    )
    stats = result.one()

    statistics.total_students = stats.total or 0
    statistics.draft_count = stats.draft or 0
    statistics.submitted_count = stats.submitted or 0
    statistics.graded_count = stats.graded or 0
    statistics.average_score = float(stats.avg_score) if stats.avg_score else None
    statistics.highest_score = float(stats.max_score) if stats.max_score else None
    statistics.lowest_score = float(stats.min_score) if stats.min_score else None
    statistics.average_time_spent = int(stats.avg_time) if stats.avg_time else None
    statistics.updated_at = datetime.utcnow()

    # 互评统计
    result = await db.execute(
        select(func.count(PeerReview.id), func.avg(PeerReview.score)).where(
            PeerReview.cell_id == cell_id
        )
    )
    peer_stats = result.one()
    statistics.peer_review_count = peer_stats[0] or 0
    statistics.avg_peer_review_score = float(peer_stats[1]) if peer_stats[1] else None

    await db.commit()

