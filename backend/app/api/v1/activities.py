"""
教学活动 API
"""

from datetime import datetime
from statistics import mean
from typing import Any, Dict, List, Optional, cast
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, Integer, cast as sql_cast
from sqlalchemy.orm import selectinload

from app.api import deps
from app.models.user import User, UserRole
from app.models.activity import (
    ActivitySubmission,
    ActivitySubmissionStatus,
    PeerReview,
    PeerReviewStatus,
    ActivityStatistics,
    ActivityItemStatistic,
    FlowchartSnapshot,
    FormativeAssessment,
)
from app.models.lesson import Lesson
from app.models.cell import Cell, CellType
from app.schemas.activity import (
    ActivitySubmissionCreate,
    ActivitySubmissionUpdate,
    ActivitySubmissionSubmit,
    ActivitySubmissionGrade,
    ActivitySubmissionResponse,
    ActivitySubmissionWithStudent,
    ActivityItemStatisticResponse,
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
    FlowchartSnapshotResponse,
    FormativeAssessmentResponse,
    FlowchartSnapshotPayload,
)
from app.services.formative_assessment import (
    recompute_formative_assessment,
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
    
    try:
        # 验证 Lesson 存在
        lesson = await db.get(Lesson, data.lesson_id)
        if not lesson:
            raise HTTPException(status_code=404, detail="教案不存在")

        # 处理 cell_id：可能是 int 或 UUID 字符串
        cell_id_value = data.cell_id
        cell: Optional[Cell] = None
        
        # 如果 cell_id 是字符串（UUID），需要从 lesson.content 中查找并创建
        if isinstance(cell_id_value, str):
            # UUID 格式，需要从 lesson.content 中查找对应的 cell
            lesson_content = cast(Optional[List[Dict[str, Any]]], getattr(lesson, "content", None))
            if lesson_content:
                # 在 lesson.content 中查找匹配的 cell（通过 UUID）
                matched_cell_data = None
                for cell_data in lesson_content:
                    cell_id_in_content = cell_data.get("id")
                    if str(cell_id_in_content) == cell_id_value:
                        # 找到了匹配的 cell 数据
                        matched_cell_data = cell_data
                        break
                
                if matched_cell_data:
                    cell_order = matched_cell_data.get("order")
                    cell_type = matched_cell_data.get("type") or matched_cell_data.get("cell_type")
                    
                    # 检查是否已经有相同 order 和 type 的 cell
                    if cell_order is not None:
                        # 使用 cast 进行类型转换以避免 PostgreSQL 枚举类型比较问题
                        from sqlalchemy import Text
                        existing_cell_query = select(Cell).where(
                            and_(
                                Cell.lesson_id == data.lesson_id,
                                Cell.order == cell_order,
                                sql_cast(Cell.cell_type, Text) == "ACTIVITY",
                            )
                        )
                        existing_result = await db.execute(existing_cell_query)
                        existing_cell = existing_result.scalar_one_or_none()
                        
                        if existing_cell:
                            # 使用已存在的 cell
                            cell = existing_cell
                            cell_id_value = cast(int, cell.id)
                        else:
                            # 创建新的 cell 记录
                            new_cell = Cell(
                                lesson_id=data.lesson_id,
                                cell_type=CellType.ACTIVITY,
                                title=matched_cell_data.get("title", ""),
                                content=matched_cell_data.get("content", {}),
                                config=matched_cell_data.get("config", {}),
                                order=cell_order,
                                editable=matched_cell_data.get("editable", False),
                            )
                            db.add(new_cell)
                            await db.flush()  # 获取 ID 但不提交
                            cell = new_cell
                            cell_id_value = cast(int, cell.id)
        else:
            # cell_id 是数字，直接查询
            cell = await db.get(Cell, cell_id_value)
        
        # 如果仍然没有 cell，返回错误
        if not cell:
            raise HTTPException(
                status_code=404, 
                detail=f"Cell 不存在 (cell_id: {cell_id_value})"
            )
        
        # 更新 data.cell_id 为数字 ID（用于后续操作）
        data.cell_id = cast(int, cell.id)
        
        # 确保 cell_id 是整数类型（用于后续操作）
        final_cell_id = cast(int, data.cell_id)
        
        # 检查是否已有提交（草稿）
        result = await db.execute(
            select(ActivitySubmission).where(
                and_(
                    ActivitySubmission.cell_id == final_cell_id,
                    ActivitySubmission.student_id == current_user.id,
                    ActivitySubmission.status == ActivitySubmissionStatus.DRAFT,
                )
            )
        )
        existing = result.scalar_one_or_none()

        if existing:
            # 更新现有草稿
            setattr(existing, "responses", cast(dict[str, Any], data.responses or {}))
            if data.process_trace is not None:
                setattr(existing, "process_trace", cast(List[Dict[str, Any]], data.process_trace))
            if data.context is not None:
                setattr(existing, "context", cast(Dict[str, Any], data.context))
            if data.activity_phase is not None:
                setattr(existing, "activity_phase", data.activity_phase)
            if data.attempt_no is not None:
                setattr(existing, "attempt_no", cast(int, data.attempt_no))
            setattr(existing, "updated_at", datetime.utcnow())
            await db.commit()
            await db.refresh(existing)
            return existing

        # 创建新提交
        # 注意：session_id 应该从请求上下文或参数中获取，暂时先不处理
        # 处理 started_at：如果带时区，转换为不带时区的 UTC 时间
        started_at_value = data.started_at or datetime.utcnow()
        if started_at_value and hasattr(started_at_value, 'tzinfo') and started_at_value.tzinfo is not None:
            # 转换为 UTC 并移除时区信息
            started_at_value = started_at_value.replace(tzinfo=None)
        
        submission = ActivitySubmission(
            cell_id=final_cell_id,
            lesson_id=data.lesson_id,
            student_id=cast(int, current_user.id),
            responses=data.responses or {},
            status=ActivitySubmissionStatus.DRAFT,
            started_at=started_at_value,
            process_trace=data.process_trace or [],
            context=data.context or {},
            activity_phase=data.activity_phase,
            attempt_no=data.attempt_no or 1,
            session_id=None,  # 暂时为None，后续可以从请求中获取
        )

        db.add(submission)
        await db.commit()
        await db.refresh(submission)

        return submission
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error in create_submission: {e}")
        import traceback
        traceback.print_exc()
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"创建提交失败: {str(e)}"
        )


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
    current_role = cast(UserRole, current_user.role)
    submission_student_id = cast(int, submission.student_id)
    current_user_id = cast(int, current_user.id)
    if current_role == UserRole.STUDENT and submission_student_id != current_user_id:
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
    submission_student_id = cast(int, submission.student_id)
    current_user_id = cast(int, current_user.id)
    if submission_student_id != current_user_id:
        raise HTTPException(status_code=403, detail="无权修改")

    # 已提交的不能再修改（除非允许多次提交）
    submission_status = cast(ActivitySubmissionStatus, submission.status)
    if submission_status != ActivitySubmissionStatus.DRAFT:
        raise HTTPException(status_code=400, detail="已提交的作业不能修改")

    # 更新字段
    if data.responses is not None:
        setattr(submission, "responses", cast(dict[str, Any], data.responses))
    if data.status is not None:
        setattr(submission, "status", cast(ActivitySubmissionStatus, data.status))
    if data.time_spent is not None:
        setattr(submission, "time_spent", cast(int, data.time_spent))
    if data.process_trace is not None:
        setattr(submission, "process_trace", cast(List[Dict[str, Any]], data.process_trace))
    if data.context is not None:
        setattr(submission, "context", cast(Dict[str, Any], data.context))
    if data.activity_phase is not None:
        setattr(submission, "activity_phase", data.activity_phase)
    if data.attempt_no is not None:
        setattr(submission, "attempt_no", cast(int, data.attempt_no))
    if data.flowchart_snapshot is not None:
        await _save_flowchart_snapshot(
            db,
            submission,
            data.flowchart_snapshot,
            student_id=submission_student_id,
        )
    if data.flowchart_snapshot is not None:
        await _save_flowchart_snapshot(
            db,
            submission,
            data.flowchart_snapshot,
            student_id=submission_student_id,
        )

    setattr(submission, "updated_at", datetime.utcnow())

    await db.commit()
    await db.refresh(submission)

    return submission


@router.post(
    "/submissions/{submission_id}/submit", response_model=ActivitySubmissionResponse
)
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
    submission_student_id = cast(int, submission.student_id)
    current_user_id = cast(int, current_user.id)
    if submission_student_id != current_user_id:
        raise HTTPException(status_code=403, detail="无权操作")

    # 更新提交数据
    setattr(submission, "responses", cast(dict[str, Any], data.responses))
    setattr(submission, "status", ActivitySubmissionStatus.SUBMITTED)
    setattr(submission, "submitted_at", datetime.utcnow())
    if data.time_spent:
        setattr(submission, "time_spent", cast(int, data.time_spent))
    if data.process_trace is not None:
        setattr(submission, "process_trace", cast(List[Dict[str, Any]], data.process_trace))
    if data.context is not None:
        setattr(submission, "context", cast(Dict[str, Any], data.context))
    if data.activity_phase is not None:
        setattr(submission, "activity_phase", data.activity_phase)
    if data.attempt_no is not None:
        setattr(submission, "attempt_no", cast(int, data.attempt_no))

    # 获取 Cell 内容以进行自动评分
    cell = await db.get(Cell, cast(int, submission.cell_id))
    if not cell:
        raise HTTPException(status_code=404, detail="Cell 不存在")
    
    # 实现自动评分逻辑
    cell_content = cast(Dict[str, Any], cell.content)
    auto_graded, total_score, max_score, graded_responses = _auto_grade_submission(
        cast(dict[str, Any], data.responses),
        cell_content
    )
    
    # 更新 responses（包含正确性判断）
    setattr(submission, "responses", graded_responses)
    
    # 如果启用了自动评分，更新分数
    grading_config = cell_content.get("grading", {})
    if auto_graded and grading_config.get("autoGrade", False):
        setattr(submission, "score", total_score)
        setattr(submission, "max_score", max_score)
        setattr(submission, "auto_graded", True)
    else:
        setattr(submission, "auto_graded", False)

    await db.commit()
    await db.refresh(submission)

    # 更新统计数据
    await _update_statistics(
        db,
        cast(int, submission.cell_id),
        cast(int, submission.lesson_id),
    )

    phase_value = cast(Optional[str], getattr(submission, "activity_phase", None))

    await recompute_formative_assessment(
        db,
        cast(int, submission.lesson_id),
        cast(int, submission.student_id),
        phase=phase_value,
    )

    # ===== WebSocket 实时通知 =====
    # 发送通知给教师
    try:
        from app.services.realtime import (
            resolve_teacher_targets,
            build_event,
            get_submission_statistics,
            Channel
        )
        from app.services.websocket_manager import manager
        
        # 获取学生信息
        student = await db.get(User, submission.student_id)
        
        # 解析教师目标
        teacher_target = await resolve_teacher_targets(db, submission)
        if teacher_target:
            # 发送新提交通知
            event = build_event(
                type="new_submission",
                channel=teacher_target.channel,
                delivery_mode="cast" if teacher_target.is_broadcast else "unicast",
                data={
                    "submission_id": submission.id,
                    "cell_id": submission.cell_id,
                    "lesson_id": submission.lesson_id,
                    "student_id": submission.student_id,
                    "student_name": student.full_name or student.username if student else "Unknown",
                    "student_email": student.email if student else "",
                    "status": submission.status.value,
                    "score": submission.score,
                    "submitted_at": submission.submitted_at.isoformat() if submission.submitted_at is not None else None,
                    "time_spent": submission.time_spent,
                },
            )
            
            await manager.send_to_teacher(
                event=event,
                scope=teacher_target.channel.scope,
                channel_id=teacher_target.channel.id,
                teacher_ids=teacher_target.recipient_ids if not teacher_target.is_broadcast else []
            )
            
            # 发送统计更新通知
            stats = await get_submission_statistics(
                db,
                cell_id=cast(int, submission.cell_id),
                lesson_id=cast(int, submission.lesson_id),
                session_id=cast(Optional[int], submission.session_id)
            )
            
            stats_event = build_event(
                type="submission_statistics_updated",
                channel=teacher_target.channel,
                delivery_mode="cast",
                data=stats
            )
            
            await manager.broadcast(
                event=stats_event,
                scope=teacher_target.channel.scope,
                channel_id=teacher_target.channel.id
            )
    except Exception as e:
        # WebSocket 通知失败不影响主流程
        print(f"❌ WebSocket 通知失败: {str(e)}")
        import traceback
        traceback.print_exc()

    return submission


@router.get(
    "/cells/{cell_id}/submissions", response_model=List[ActivitySubmissionWithStudent]
)
async def get_cell_submissions(
    cell_id: int,
    status: Optional[ActivitySubmissionStatus] = None,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """获取某个 Cell 的所有提交（教师端）"""

    # 只有教师可以查看
    current_role = cast(UserRole, current_user.role)
    if current_role != UserRole.TEACHER:
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


@router.get(
    "/cells/{cell_id}/item-statistics",
    response_model=List[ActivityItemStatisticResponse],
)
async def get_cell_item_statistics(
    cell_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """获取某个 Cell 的题目级统计（教师端）"""

    current_role = cast(UserRole, current_user.role)
    if current_role != UserRole.TEACHER:
        raise HTTPException(status_code=403, detail="权限不足")

    result = await db.execute(
        select(ActivityItemStatistic).where(ActivityItemStatistic.cell_id == cell_id)
    )
    return result.scalars().all()


@router.get(
    "/cells/{cell_id}/flowchart-snapshots",
    response_model=List[FlowchartSnapshotResponse],
)
async def get_cell_flowchart_snapshots(
    cell_id: int,
    student_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """获取流程图快照列表"""

    current_role = cast(UserRole, current_user.role)
    if current_role != UserRole.TEACHER:
        raise HTTPException(status_code=403, detail="权限不足")

    query = select(FlowchartSnapshot).where(FlowchartSnapshot.cell_id == cell_id)
    if student_id is not None:
        query = query.where(FlowchartSnapshot.student_id == student_id)

    query = query.order_by(FlowchartSnapshot.updated_at.desc())

    result = await db.execute(query)
    return result.scalars().all()


@router.get(
    "/cells/{cell_id}/my-submission",
    response_model=ActivitySubmissionResponse,
)
async def get_my_cell_submission(
    cell_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """获取我在某个 Cell 的提交（学生端）"""

    result = await db.execute(
        select(ActivitySubmission).where(
            and_(
                ActivitySubmission.cell_id == cell_id,
                ActivitySubmission.student_id == current_user.id,
            )
        ).order_by(ActivitySubmission.created_at.desc())
    )
    submission = result.scalar_one_or_none()

    if not submission:
        raise HTTPException(status_code=404, detail="提交不存在")

    return submission


@router.get(
    "/lessons/{lesson_id}/my-submissions",
    response_model=List[ActivitySubmissionResponse],
)
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


@router.get(
    "/lessons/{lesson_id}/formative-assessments",
    response_model=List[FormativeAssessmentResponse],
)
async def get_formative_assessments(
    lesson_id: int,
    student_id: Optional[int] = Query(None),
    phase: Optional[str] = Query(None),
    risk_level: Optional[str] = Query(None),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """获取课程的过程性评估数据（教师端）"""

    current_role = cast(UserRole, current_user.role)
    if current_role != UserRole.TEACHER:
        raise HTTPException(status_code=403, detail="权限不足")

    query = select(FormativeAssessment).where(
        FormativeAssessment.lesson_id == lesson_id
    )
    if student_id is not None:
        query = query.where(FormativeAssessment.student_id == student_id)
    if phase:
        query = query.where(FormativeAssessment.phase == phase)
    if risk_level:
        query = query.where(FormativeAssessment.risk_level == risk_level)

    query = query.order_by(FormativeAssessment.updated_at.desc())

    result = await db.execute(query)
    return result.scalars().all()


@router.post(
    "/lessons/{lesson_id}/formative-assessments/{student_id}/recompute",
    response_model=FormativeAssessmentResponse,
)
async def recompute_formative_assessment_endpoint(
    lesson_id: int,
    student_id: int,
    phase: Optional[str] = Query(None),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """重新计算指定学生的过程性评估"""

    current_role = cast(UserRole, current_user.role)
    if current_role != UserRole.TEACHER:
        raise HTTPException(status_code=403, detail="权限不足")

    record = await recompute_formative_assessment(
        db, lesson_id=lesson_id, student_id=student_id, phase=phase
    )
    return record


# ========== 评分相关 API ==========


@router.post(
    "/submissions/{submission_id}/grade", response_model=ActivitySubmissionResponse
)
async def grade_submission(
    submission_id: int,
    data: ActivitySubmissionGrade,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """评分"""

    # 只有教师可以评分
    current_role = cast(UserRole, current_user.role)
    if current_role != UserRole.TEACHER:
        raise HTTPException(status_code=403, detail="权限不足")

    submission = await db.get(ActivitySubmission, submission_id)
    if not submission:
        raise HTTPException(status_code=404, detail="提交不存在")

    submission_status = cast(ActivitySubmissionStatus, submission.status)
    if submission_status != ActivitySubmissionStatus.SUBMITTED:
        raise HTTPException(status_code=400, detail="只能评分已提交的作业")

    # 更新评分
    setattr(submission, "score", cast(float, data.score))
    setattr(submission, "teacher_feedback", cast(str, data.teacher_feedback))
    setattr(submission, "graded_by", cast(int, current_user.id))
    setattr(submission, "graded_at", datetime.utcnow())
    setattr(submission, "status", ActivitySubmissionStatus.GRADED)

    # 如果有分项分数，更新 responses 中的 score 字段
    if data.item_scores:
        for item_id, item_score in data.item_scores.items():
            if item_id in cast(dict[str, Any], submission.responses):
                cast(dict[str, Any], submission.responses)[item_id][
                    "score"
                ] = item_score

    await db.commit()
    await db.refresh(submission)

    # 更新统计数据
    await _update_statistics(
        db, cast(int, submission.cell_id), cast(int, submission.lesson_id)
    )

    phase_value = cast(Optional[str], getattr(submission, "activity_phase", None))

    await recompute_formative_assessment(
        db,
        cast(int, submission.lesson_id),
        cast(int, submission.student_id),
        phase=phase_value,
    )

    # ===== WebSocket 实时通知 =====
    # 发送评分通知给学生
    try:
        from app.services.realtime import (
            resolve_student_target,
            build_event,
        )
        from app.services.websocket_manager import manager
        
        # 解析学生目标
        student_target = await resolve_student_target(db, submission)
        if student_target:
            # 发送评分通知
            event = build_event(
                type="submission_graded",
                channel=student_target.channel,
                delivery_mode="unicast",
                data={
                    "submission_id": submission.id,
                    "cell_id": submission.cell_id,
                    "lesson_id": submission.lesson_id,
                    "score": submission.score,
                    "max_score": submission.max_score,
                    "teacher_feedback": submission.teacher_feedback,
                    "graded_at": submission.graded_at.isoformat() if submission.graded_at is not None else None,
                    "graded_by": submission.graded_by,
                    "graded_by_name": current_user.full_name or current_user.username,
                },
            )
            
            await manager.send_to_student(
                event=event,
                scope=student_target.channel.scope,
                channel_id=student_target.channel.id,
                student_ids=student_target.recipient_ids
            )
    except Exception as e:
        # WebSocket 通知失败不影响主流程
        print(f"❌ WebSocket 评分通知失败: {str(e)}")
        import traceback
        traceback.print_exc()

    return submission


@router.post("/submissions/bulk-grade", response_model=dict)
async def bulk_grade_submissions(
    data: BulkGradeRequest,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """批量评分"""

    current_role = cast(UserRole, current_user.role)
    if current_role != UserRole.TEACHER:
        raise HTTPException(status_code=403, detail="权限不足")

    graded_count = 0
    cells_to_update: set[tuple[int, int]] = set()
    recompute_targets: set[tuple[int, int, Optional[str]]] = set()

    for submission_id in data.submission_ids:
        submission = await db.get(ActivitySubmission, submission_id)
        if (
            submission
            and cast(ActivitySubmissionStatus, submission.status)
            == ActivitySubmissionStatus.SUBMITTED
        ):
            phase_value = cast(Optional[str], getattr(submission, "activity_phase", None))
            setattr(submission, "score", cast(float, data.score))
            setattr(submission, "teacher_feedback", cast(str, data.teacher_feedback))
            setattr(submission, "graded_by", cast(int, current_user.id))
            setattr(submission, "graded_at", datetime.utcnow())
            setattr(submission, "status", ActivitySubmissionStatus.GRADED)
            graded_count += 1
            cells_to_update.add(
                (cast(int, submission.cell_id), cast(int, submission.lesson_id))
            )
            recompute_targets.add(
                (
                    cast(int, submission.lesson_id),
                    cast(int, submission.student_id),
                    phase_value,
                )
            )

    await db.commit()

    for cell_id, lesson_id in cells_to_update:
        await _update_statistics(db, cell_id, lesson_id)

    for lesson_id, student_id, phase in recompute_targets:
        await recompute_formative_assessment(
            db, lesson_id, student_id, phase=phase
        )

    # ===== WebSocket 实时通知 =====
    # 批量发送评分通知给学生
    try:
        from app.services.realtime import resolve_student_target, build_event
        from app.services.websocket_manager import manager
        
        # 为每个学生发送通知
        for submission_id in data.submission_ids:
            submission = await db.get(ActivitySubmission, submission_id)
            if submission and cast(ActivitySubmissionStatus, submission.status) == ActivitySubmissionStatus.GRADED:
                student_target = await resolve_student_target(db, submission)
                if student_target:
                    event = build_event(
                        type="submission_graded",
                        channel=student_target.channel,
                        delivery_mode="unicast",
                        data={
                            "submission_id": submission.id,
                            "cell_id": submission.cell_id,
                            "lesson_id": submission.lesson_id,
                            "score": submission.score,
                            "max_score": submission.max_score,
                            "teacher_feedback": submission.teacher_feedback,
                            "graded_at": submission.graded_at.isoformat() if submission.graded_at is not None else None,
                            "graded_by": submission.graded_by,
                            "graded_by_name": current_user.full_name or current_user.username,
                        },
                    )
                    
                    await manager.send_to_student(
                        event=event,
                        scope=student_target.channel.scope,
                        channel_id=student_target.channel.id,
                        student_ids=student_target.recipient_ids
                    )
    except Exception as e:
        print(f"❌ 批量 WebSocket 评分通知失败: {str(e)}")

    return {"graded_count": graded_count}


# ========== 互评相关 API ==========


@router.post("/peer-reviews/assign", response_model=dict)
async def assign_peer_reviews(
    data: PeerReviewAssignment,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """分配互评任务（教师端）"""

    current_role = cast(UserRole, current_user.role)
    if current_role != UserRole.TEACHER:
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
            reviewer_submission_student_id = cast(int, reviewer_submission.student_id)
            submission_student_id = cast(int, submission.student_id)
            if reviewer_submission_student_id == submission_student_id:
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


@router.get(
    "/submissions/{submission_id}/peer-reviews",
    response_model=List[PeerReviewWithReviewer],
)
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
    current_role = cast(UserRole, current_user.role)
    submission_student_id = cast(int, submission.student_id)
    current_user_id = cast(int, current_user.id)
    if current_role == UserRole.STUDENT and submission_student_id != current_user_id:
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
            "reviewer_name": None
            if review.is_anonymous
            else (user.full_name or user.username),
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

    reviewer_id = cast(int, review.reviewer_id)
    current_user_id = cast(int, current_user.id)
    if reviewer_id != current_user_id:
        raise HTTPException(status_code=403, detail="无权操作")

    # 更新互评数据
    setattr(review, "review_data", cast(dict[str, Any], data.review_data))
    setattr(review, "score", cast(float, data.score))
    setattr(review, "comment", cast(str, data.comment))
    setattr(review, "status", PeerReviewStatus.COMPLETED)
    setattr(review, "completed_at", datetime.utcnow())

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

    current_role = cast(UserRole, current_user.role)
    if current_role != UserRole.TEACHER:
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
            lesson_id=cast(int, cell.lesson_id),
        )
        db.add(statistics)
        await db.commit()
        await db.refresh(statistics)

        # 立即计算统计数据
        await _update_statistics(db, cast(int, cell_id), cast(int, cell.lesson_id))

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
                setattr(
                    existing,
                    "responses",
                    cast(dict[str, Any], submission_data["responses"]),
                )
                if "process_trace" in submission_data:
                    setattr(
                        existing,
                        "process_trace",
                        cast(
                            List[Dict[str, Any]],
                            submission_data.get("process_trace") or [],
                        ),
                    )
                if "context" in submission_data:
                    setattr(
                        existing,
                        "context",
                        cast(Dict[str, Any], submission_data.get("context") or {}),
                    )
                if "activity_phase" in submission_data:
                    setattr(existing, "activity_phase", submission_data["activity_phase"])
                if "attempt_no" in submission_data:
                    setattr(
                        existing,
                        "attempt_no",
                        cast(int, submission_data.get("attempt_no") or 1),
                    )
                if submission_data.get("flowchart_snapshot"):
                    snapshot_payload = FlowchartSnapshotPayload.model_validate(
                        submission_data["flowchart_snapshot"]
                    )
                    await _save_flowchart_snapshot(
                        db,
                        existing,
                        snapshot_payload,
                        student_id=cast(int, current_user.id),
                    )
                setattr(existing, "version", cast(int, existing.version) + 1)
                setattr(existing, "synced", cast(bool, True))
                setattr(existing, "updated_at", cast(datetime, datetime.utcnow()))
                synced_count += 1
            else:
                # 创建新提交
                submission = ActivitySubmission(
                    cell_id=submission_data["cell_id"],
                    lesson_id=submission_data["lesson_id"],
                    student_id=cast(int, current_user.id),
                    responses=submission_data["responses"],
                    status=ActivitySubmissionStatus.DRAFT,
                    synced=cast(bool, True),
                    process_trace=submission_data.get("process_trace") or [],
                    context=submission_data.get("context") or {},
                    activity_phase=submission_data.get("activity_phase"),
                    attempt_no=submission_data.get("attempt_no") or 1,
                )
                db.add(submission)
                await db.flush()
                if submission_data.get("flowchart_snapshot"):
                    snapshot_payload = FlowchartSnapshotPayload.model_validate(
                        submission_data["flowchart_snapshot"]
                    )
                    await _save_flowchart_snapshot(
                        db,
                        submission,
                        snapshot_payload,
                        student_id=cast(int, current_user.id),
                    )
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


def _auto_grade_submission(
    responses: Dict[str, Any],
    cell_content: Dict[str, Any]
) -> tuple[bool, float, float, Dict[str, Any]]:
    """
    自动评分函数
    
    参数:
        responses: 学生答案字典 {item_id: answer}
        cell_content: Cell 内容，包含题目配置
    
    返回:
        (auto_graded, total_score, max_score, graded_responses)
        - auto_graded: 是否可以进行自动评分
        - total_score: 总分
        - max_score: 满分
        - graded_responses: 包含正确性判断的答案字典
    """
    items = cell_content.get("items", [])
    graded_responses: Dict[str, Any] = {}
    total_score = 0.0
    max_score = 0.0
    has_auto_gradable_items = False
    
    for item in items:
        item_id = str(item.get("id", ""))
        item_type = item.get("type", "")
        item_config = item.get("config", {})
        item_points = item.get("points", 0)
        max_score += float(item_points) if item_points else 0.0
        
        # 获取学生答案
        student_answer = responses.get(item_id)
        if student_answer is None:
            # 未作答，跳过
            if item_id in responses:
                graded_responses[item_id] = responses[item_id]
            continue
        
        # 初始化答案对象（如果还不是字典）
        if not isinstance(student_answer, dict):
            graded_answer: Dict[str, Any] = {}
            if item_type == "single-choice":
                graded_answer["answer"] = student_answer
            elif item_type == "multiple-choice":
                graded_answer["answer"] = student_answer if isinstance(student_answer, list) else [student_answer]
            elif item_type == "true-false":
                graded_answer["answer"] = student_answer
            else:
                graded_answer = {"text": student_answer} if isinstance(student_answer, str) else student_answer
        else:
            graded_answer = student_answer.copy()
        
        # 判断选择题的正确性
        is_correct = None
        correct_answer = None
        
        if item_type == "single-choice":
            has_auto_gradable_items = True
            correct_answer_id = item_config.get("correctAnswer")
            student_answer_id = graded_answer.get("answer") or student_answer
            
            if correct_answer_id is not None:
                is_correct = str(student_answer_id) == str(correct_answer_id)
                # 找到正确答案的文本和ID（都保存以便前端使用）
                options = item_config.get("options", [])
                correct_answer_text = None
                for opt in options:
                    if str(opt.get("id", "")) == str(correct_answer_id):
                        correct_answer_text = opt.get("text", correct_answer_id)
                        break
                if not correct_answer_text:
                    correct_answer_text = correct_answer_id
                
                # 保存正确答案（文本形式，方便显示）
                correct_answer = correct_answer_text
                # 同时保存正确答案ID（用于前端比较）
                graded_answer["correctAnswerId"] = correct_answer_id
                
                # 计算分数
                if is_correct and item_points:
                    graded_answer["score"] = float(item_points)
                    total_score += float(item_points)
                else:
                    graded_answer["score"] = 0.0
                
                graded_answer["correct"] = is_correct
                graded_answer["correctAnswer"] = correct_answer
        
        elif item_type == "multiple-choice":
            has_auto_gradable_items = True
            correct_answer_ids = item_config.get("correctAnswers", [])
            student_answer_ids = graded_answer.get("answer") or (student_answer if isinstance(student_answer, list) else [student_answer])
            
            if correct_answer_ids:
                # 转换为字符串列表以便比较
                correct_set = set(str(id) for id in correct_answer_ids)
                student_set = set(str(id) for id in student_answer_ids)
                
                is_correct = correct_set == student_set
                
                # 找到正确答案的文本
                options = item_config.get("options", [])
                correct_texts = []
                for opt in options:
                    if str(opt.get("id", "")) in correct_set:
                        correct_texts.append(opt.get("text", opt.get("id", "")))
                correct_answer = ", ".join(correct_texts) if correct_texts else ", ".join(correct_answer_ids)
                
                # 计算分数
                if is_correct and item_points:
                    graded_answer["score"] = float(item_points)
                    total_score += float(item_points)
                else:
                    graded_answer["score"] = 0.0
                
                graded_answer["correct"] = is_correct
                graded_answer["correctAnswer"] = correct_answer
        
        elif item_type == "true-false":
            has_auto_gradable_items = True
            correct_answer_value = item_config.get("correctAnswer")
            student_answer_value = graded_answer.get("answer")
            
            if student_answer_value is None:
                student_answer_value = student_answer
            
            if correct_answer_value is not None:
                is_correct = bool(student_answer_value) == bool(correct_answer_value)
                correct_answer = "正确" if correct_answer_value else "错误"
                
                # 计算分数
                if is_correct and item_points:
                    graded_answer["score"] = float(item_points)
                    total_score += float(item_points)
                else:
                    graded_answer["score"] = 0.0
                
                graded_answer["correct"] = is_correct
                graded_answer["correctAnswer"] = correct_answer
        
        # 保存评分后的答案
        graded_responses[item_id] = graded_answer
    
    return has_auto_gradable_items, total_score, max_score, graded_responses


async def _save_flowchart_snapshot(
    db: AsyncSession,
    submission: ActivitySubmission,
    snapshot: FlowchartSnapshotPayload,
    student_id: int,
) -> FlowchartSnapshot:
    """
    保存流程图快照。
    """

    version = snapshot.version
    if version is None:
        result = await db.execute(
            select(func.max(FlowchartSnapshot.version)).where(
                FlowchartSnapshot.submission_id == submission.id
            )
        )
        latest_version = result.scalar()
        version = cast(int, (latest_version or 0) + 1)

    flowchart_snapshot = FlowchartSnapshot(
        submission_id=submission.id,
        student_id=student_id,
        lesson_id=cast(int, submission.lesson_id),
        cell_id=cast(int, submission.cell_id),
        graph=snapshot.graph,
        analysis=snapshot.analysis or {},
        version=version,
    )
    db.add(flowchart_snapshot)
    await db.flush()

    return flowchart_snapshot


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
                func.cast(
                    ActivitySubmission.status == ActivitySubmissionStatus.DRAFT, Integer
                )
            ).label("draft"),
            func.sum(
                func.cast(
                    ActivitySubmission.status == ActivitySubmissionStatus.SUBMITTED,
                    Integer,
                )
            ).label("submitted"),
            func.sum(
                func.cast(
                    ActivitySubmission.status == ActivitySubmissionStatus.GRADED,
                    Integer,
                )
            ).label("graded"),
            func.avg(ActivitySubmission.score).label("avg_score"),
            func.max(ActivitySubmission.score).label("max_score"),
            func.min(ActivitySubmission.score).label("min_score"),
            func.avg(ActivitySubmission.time_spent).label("avg_time"),
        ).where(ActivitySubmission.cell_id == cell_id)
    )
    stats = result.one()

    total_students = int(stats.total or 0)
    draft_count = int(stats.draft or 0)
    submitted_count = int(stats.submitted or 0)
    graded_count = int(stats.graded or 0)
    average_score = float(stats.avg_score) if stats.avg_score is not None else None
    highest_score = float(stats.max_score) if stats.max_score is not None else None
    lowest_score = float(stats.min_score) if stats.min_score is not None else None
    average_time_spent = int(stats.avg_time) if stats.avg_time is not None else None

    setattr(statistics, "total_students", total_students)
    setattr(statistics, "draft_count", draft_count)
    setattr(statistics, "submitted_count", submitted_count)
    setattr(statistics, "graded_count", graded_count)
    setattr(statistics, "average_score", average_score)
    setattr(statistics, "highest_score", highest_score)
    setattr(statistics, "lowest_score", lowest_score)
    setattr(statistics, "average_time_spent", average_time_spent)
    setattr(statistics, "updated_at", datetime.utcnow())

    # 互评统计
    result = await db.execute(
        select(func.count(PeerReview.id), func.avg(PeerReview.score)).where(
            PeerReview.cell_id == cell_id
        )
    )
    peer_stats = result.one()
    peer_review_count = int(peer_stats[0] or 0)
    avg_peer_review_score = float(peer_stats[1]) if peer_stats[1] is not None else None

    setattr(statistics, "peer_review_count", peer_review_count)
    setattr(statistics, "avg_peer_review_score", avg_peer_review_score)

    # 题目级统计
    submissions_result = await db.execute(
        select(ActivitySubmission).where(ActivitySubmission.cell_id == cell_id)
    )
    submissions = submissions_result.scalars().all()

    item_aggregates: Dict[str, Dict[str, Any]] = {}
    for submission in submissions:
        responses = submission.responses or {}
        for item_id, item_value in responses.items():
            if not isinstance(item_value, dict):
                continue
            aggregate = item_aggregates.setdefault(
                item_id,
                {
                    "attempts": 0,
                    "correct_count": 0,
                    "scores": [],
                    "options": {},
                    "knowledge": {},
                    "times": [],
                },
            )
            aggregate["attempts"] += 1

            if item_value.get("is_correct"):
                aggregate["correct_count"] += 1

            score = item_value.get("score")
            if isinstance(score, (int, float)):
                aggregate["scores"].append(float(score))

            time_spent = item_value.get("time_spent")
            if isinstance(time_spent, (int, float)):
                aggregate["times"].append(float(time_spent))

            answer = item_value.get("answer") or item_value.get("value")
            if isinstance(answer, list):
                for option in answer:
                    key = str(option)
                    aggregate["options"][key] = aggregate["options"].get(key, 0) + 1
            elif answer is not None:
                key = str(answer)
                aggregate["options"][key] = aggregate["options"].get(key, 0) + 1

            knowledge_tags = item_value.get("knowledge_tags") or item_value.get("tags")
            if isinstance(knowledge_tags, list):
                for tag in knowledge_tags:
                    tag_key = str(tag)
                    aggregate["knowledge"][tag_key] = (
                        aggregate["knowledge"].get(tag_key, 0) + 1
                    )

    existing_stats_result = await db.execute(
        select(ActivityItemStatistic).where(ActivityItemStatistic.cell_id == cell_id)
    )
    existing_stats = {
        cast(str, stat.item_id): stat
        for stat in existing_stats_result.scalars().all()
    }

    summary_payload: Dict[str, Any] = {}

    for item_id, aggregate in item_aggregates.items():
        attempts = aggregate["attempts"]
        accuracy = (
            round(aggregate["correct_count"] / attempts, 4) if attempts else None
        )
        avg_score = (
            round(mean(aggregate["scores"]), 2) if aggregate["scores"] else None
        )
        avg_time = round(mean(aggregate["times"]), 2) if aggregate["times"] else None

        summary_payload[item_id] = {
            "attempts": attempts,
            "correct_count": aggregate["correct_count"],
            "accuracy": accuracy,
            "avg_score": avg_score,
            "avg_time_spent": avg_time,
            "option_distribution": aggregate["options"],
            "knowledge_stats": aggregate["knowledge"],
        }

        stat_record = existing_stats.get(item_id)
        if stat_record:
            setattr(stat_record, "attempts", attempts)
            setattr(stat_record, "correct_count", aggregate["correct_count"])
            setattr(stat_record, "avg_score", avg_score)
            setattr(stat_record, "avg_time_spent", avg_time)
            setattr(stat_record, "option_distribution", aggregate["options"])
            setattr(
                stat_record, "score_distribution", {"values": aggregate["scores"]}
            )
            setattr(stat_record, "knowledge_stats", aggregate["knowledge"])
            setattr(stat_record, "updated_at", datetime.utcnow())
        else:
            stat_record = ActivityItemStatistic(
                cell_id=cell_id,
                lesson_id=lesson_id,
                item_id=item_id,
                attempts=attempts,
                correct_count=aggregate["correct_count"],
                avg_score=avg_score,
                avg_time_spent=avg_time,
                option_distribution=aggregate["options"],
                score_distribution={"values": aggregate["scores"]},
                knowledge_stats=aggregate["knowledge"],
            )
            db.add(stat_record)

    # 移除已经不存在的题目统计
    removed_item_ids = set(existing_stats.keys()) - set(item_aggregates.keys())
    for item_id in removed_item_ids:
        await db.delete(existing_stats[item_id])

    setattr(statistics, "item_statistics", summary_payload or None)

    # 流程图统计
    flowchart_result = await db.execute(
        select(FlowchartSnapshot).where(FlowchartSnapshot.cell_id == cell_id)
    )
    flowchart_snapshots = flowchart_result.scalars().all()

    flowchart_metrics: Optional[Dict[str, Any]] = None
    if flowchart_snapshots:
        updated_values = [
            cast(datetime, snapshot.updated_at)
            for snapshot in flowchart_snapshots
            if snapshot.updated_at is not None
        ]
        version_values = [
            cast(int, snapshot.version or 0) for snapshot in flowchart_snapshots
        ]

        latest_updated = max(updated_values) if updated_values else None
        max_version = max(version_values) if version_values else None

        flowchart_metrics = {
            "snapshot_count": len(flowchart_snapshots),
            "latest_updated_at": latest_updated.isoformat() if latest_updated is not None else None,
            "max_version": max_version,
        }
        numeric_aggregates: Dict[str, List[float]] = {}
        for snapshot in flowchart_snapshots:
            analysis_data = snapshot.analysis or {}
            if not isinstance(analysis_data, dict):
                continue
            for key, value in analysis_data.items():
                if isinstance(value, (int, float)):
                    numeric_aggregates.setdefault(key, []).append(float(value))

        for key, values in numeric_aggregates.items():
            flowchart_metrics[f"avg_{key}"] = round(mean(values), 2)

    setattr(statistics, "flowchart_metrics", flowchart_metrics)

    await db.commit()
