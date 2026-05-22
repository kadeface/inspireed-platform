"""
MathLab 课堂竞赛 API（挂在 classroom-sessions 下）
"""

from datetime import datetime, timedelta
from typing import Any, List, Optional, cast

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api import deps
from app.models.user import User, UserRole
from app.models.classroom_session import ClassSession, StudentSessionParticipation
from app.models.mathlab_contest import (
    MathlabContest,
    MathlabContestStatus,
    MathlabContestSubmission,
)
from app.models.cell import Cell
from app.schemas.mathlab_contest import (
    MathlabContestStartRequest,
    MathlabContestTaskUpdate,
    MathlabContestSubmitRequest,
    MathlabContestScoreUpdate,
    MathlabContestResponse,
    MathlabContestSubmissionResponse,
    MathlabContestLeaderboardResponse,
)
from app.core.classroom_utils import check_user_in_classroom
from app.services.websocket_manager import manager as ws_manager

router = APIRouter()


def _contest_to_response(contest: MathlabContest) -> MathlabContestResponse:
    ends_at = None
    if contest.time_limit_sec and contest.started_at:
        ends_at = contest.started_at + timedelta(seconds=int(contest.time_limit_sec))
    return MathlabContestResponse(
        id=contest.id,
        session_id=contest.session_id,
        cell_id=contest.cell_id,
        teacher_id=contest.teacher_id,
        task_id=contest.task_id,
        status=contest.status,
        time_limit_sec=contest.time_limit_sec,
        allow_resubmit=contest.allow_resubmit,
        pass_threshold=contest.pass_threshold,
        settings=contest.settings or {},
        started_at=contest.started_at,
        ended_at=contest.ended_at,
        ends_at=ends_at,
    )


async def _get_session_or_404(db: AsyncSession, session_id: int) -> ClassSession:
    session = await db.get(ClassSession, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")
    return session


async def _require_teacher(session: ClassSession, user: User) -> None:
    if cast(int, session.teacher_id) != cast(int, user.id):
        raise HTTPException(status_code=403, detail="无权操作")


async def _require_student_in_session(
    db: AsyncSession, session: ClassSession, user: User
) -> None:
    if cast(UserRole, user.role) != UserRole.STUDENT:
        raise HTTPException(status_code=403, detail="仅学生可提交")
    classroom_id = cast(int, session.classroom_id)
    if not await check_user_in_classroom(db, user, classroom_id):
        raise HTTPException(status_code=403, detail="不属于该班级")
    result = await db.execute(
        select(StudentSessionParticipation).where(
            and_(
                StudentSessionParticipation.session_id == session.id,
                StudentSessionParticipation.student_id == user.id,
                StudentSessionParticipation.is_active == True,
            )
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="请先加入课堂会话")


async def _broadcast_contest_event(
    session_id: int, event_type: str, data: dict
) -> None:
    msg = {
        "type": event_type,
        "timestamp": datetime.utcnow().isoformat(),
        "data": data,
    }
    try:
        await ws_manager.broadcast_to_session(message=msg, session_id=session_id)
        await ws_manager.send_to_teacher(
            event=msg, scope="session", channel_id=session_id
        )
    except Exception:
        pass


async def _end_running_contests(db: AsyncSession, session_id: int) -> None:
    result = await db.execute(
        select(MathlabContest).where(
            and_(
                MathlabContest.session_id == session_id,
                MathlabContest.status == MathlabContestStatus.RUNNING,
            )
        )
    )
    for c in result.scalars().all():
        c.status = MathlabContestStatus.ENDED
        c.ended_at = datetime.utcnow()


@router.post(
    "/sessions/{session_id}/mathlab-contest/start",
    response_model=MathlabContestResponse,
)
async def start_mathlab_contest(
    session_id: int,
    body: MathlabContestStartRequest,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """教师开始 MathLab 竞赛"""
    session = await _get_session_or_404(db, session_id)
    await _require_teacher(session, current_user)

    cell = await db.get(Cell, body.cell_id)
    if not cell:
        raise HTTPException(status_code=404, detail="单元不存在")

    task_id = body.task_id
    if not task_id:
        content = cell.content if isinstance(cell.content, dict) else {}
        task_id = content.get("mathlabTask") or content.get("mathlab_task")
    if not task_id:
        raise HTTPException(status_code=400, detail="请指定 task_id 或在 SimCell 中配置 mathlabTask")

    await _end_running_contests(db, session_id)

    settings = dict(body.settings or {})
    contest = MathlabContest(
        session_id=session_id,
        cell_id=body.cell_id,
        teacher_id=cast(int, current_user.id),
        task_id=task_id,
        status=MathlabContestStatus.RUNNING,
        time_limit_sec=body.time_limit_sec,
        allow_resubmit=body.allow_resubmit,
        pass_threshold=body.pass_threshold,
        settings=settings,
        started_at=datetime.utcnow(),
    )
    db.add(contest)
    await db.commit()
    await db.refresh(contest)

    resp = _contest_to_response(contest)
    await _broadcast_contest_event(
        session_id,
        "mathlab_contest_started",
        {
            "contest_id": contest.id,
            "session_id": session_id,
            "cell_id": body.cell_id,
            "task_id": task_id,
            "time_limit_sec": body.time_limit_sec,
            "ends_at": resp.ends_at.isoformat() if resp.ends_at else None,
            "pass_threshold": body.pass_threshold,
            "allow_resubmit": body.allow_resubmit,
            "settings": settings,
        },
    )
    return resp


@router.get(
    "/sessions/{session_id}/mathlab-contest/active",
    response_model=Optional[MathlabContestResponse],
)
async def get_active_mathlab_contest(
    session_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    await _get_session_or_404(db, session_id)
    result = await db.execute(
        select(MathlabContest)
        .where(
            and_(
                MathlabContest.session_id == session_id,
                MathlabContest.status == MathlabContestStatus.RUNNING,
            )
        )
        .order_by(MathlabContest.id.desc())
        .limit(1)
    )
    contest = result.scalar_one_or_none()
    if not contest:
        return None
    return _contest_to_response(contest)


@router.post("/mathlab-contest/{contest_id}/end", response_model=MathlabContestResponse)
async def end_mathlab_contest(
    contest_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    contest = await db.get(MathlabContest, contest_id)
    if not contest:
        raise HTTPException(status_code=404, detail="竞赛不存在")
    session = await _get_session_or_404(db, cast(int, contest.session_id))
    await _require_teacher(session, current_user)

    contest.status = MathlabContestStatus.ENDED
    contest.ended_at = datetime.utcnow()
    await db.commit()
    await db.refresh(contest)

    await _broadcast_contest_event(
        cast(int, contest.session_id),
        "mathlab_contest_ended",
        {"contest_id": contest.id, "session_id": contest.session_id},
    )
    return _contest_to_response(contest)


@router.patch("/mathlab-contest/{contest_id}/task", response_model=MathlabContestResponse)
async def update_contest_task(
    contest_id: int,
    body: MathlabContestTaskUpdate,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    contest = await db.get(MathlabContest, contest_id)
    if not contest:
        raise HTTPException(status_code=404, detail="竞赛不存在")
    if contest.status != MathlabContestStatus.RUNNING:
        raise HTTPException(status_code=400, detail="竞赛未进行中")
    session = await _get_session_or_404(db, cast(int, contest.session_id))
    await _require_teacher(session, current_user)

    contest.task_id = body.task_id
    await db.commit()
    await db.refresh(contest)

    await _broadcast_contest_event(
        cast(int, contest.session_id),
        "mathlab_contest_task_changed",
        {"contest_id": contest.id, "task_id": body.task_id},
    )
    return _contest_to_response(contest)


@router.get(
    "/mathlab-contest/{contest_id}/leaderboard",
    response_model=MathlabContestLeaderboardResponse,
)
async def get_contest_leaderboard(
    contest_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    result = await db.execute(
        select(MathlabContest)
        .where(MathlabContest.id == contest_id)
        .options(selectinload(MathlabContest.submissions).selectinload(MathlabContestSubmission.student))
    )
    contest = result.scalar_one_or_none()
    if not contest:
        raise HTTPException(status_code=404, detail="竞赛不存在")

    session = await _get_session_or_404(db, cast(int, contest.session_id))
    role = cast(UserRole, current_user.role)
    if role == UserRole.STUDENT:
        await _require_student_in_session(db, session, current_user)
    else:
        await _require_teacher(session, current_user)

    subs = sorted(
        list(contest.submissions),
        key=lambda s: (-float(s.final_score), float(s.elapsed_sec or 99999)),
    )
    rows: List[MathlabContestSubmissionResponse] = []
    for rank, sub in enumerate(subs, start=1):
        student = sub.student
        rows.append(
            MathlabContestSubmissionResponse(
                id=sub.id,
                contest_id=sub.contest_id,
                student_id=sub.student_id,
                student_name=(student.full_name or student.username) if student else None,
                auto_score=sub.auto_score,
                auto_passed=sub.auto_passed,
                final_score=sub.final_score,
                passed=sub.passed,
                elapsed_sec=sub.elapsed_sec,
                payload=sub.payload,
                submitted_at=sub.submitted_at,
                rank=rank,
            )
        )

    total = cast(int, session.total_students or 0)
    return MathlabContestLeaderboardResponse(
        contest=_contest_to_response(contest),
        submissions=rows,
        submitted_count=len(rows),
        total_students=total,
    )


@router.post(
    "/mathlab-contest/{contest_id}/submit",
    response_model=MathlabContestSubmissionResponse,
)
async def submit_contest_result(
    contest_id: int,
    body: MathlabContestSubmitRequest,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    contest = await db.get(MathlabContest, contest_id)
    if not contest:
        raise HTTPException(status_code=404, detail="竞赛不存在")
    if contest.status != MathlabContestStatus.RUNNING:
        raise HTTPException(status_code=400, detail="竞赛已结束")

    session = await _get_session_or_404(db, cast(int, contest.session_id))
    await _require_student_in_session(db, session, current_user)

    if contest.time_limit_sec and contest.started_at:
        ends = contest.started_at + timedelta(seconds=int(contest.time_limit_sec))
        if datetime.utcnow() > ends:
            contest.status = MathlabContestStatus.ENDED
            contest.ended_at = datetime.utcnow()
            await db.commit()
            raise HTTPException(status_code=400, detail="竞赛时间已到")

    auto_score = min(100.0, max(0.0, float(body.auto_score)))
    threshold = int(contest.pass_threshold or 85)
    auto_passed = body.auto_passed or auto_score >= threshold

    result = await db.execute(
        select(MathlabContestSubmission).where(
            and_(
                MathlabContestSubmission.contest_id == contest_id,
                MathlabContestSubmission.student_id == current_user.id,
            )
        )
    )
    existing = result.scalar_one_or_none()

    if existing and not contest.allow_resubmit:
        raise HTTPException(status_code=409, detail="已提交，不允许重复提交")

    if existing and contest.allow_resubmit:
        if auto_score <= float(existing.final_score):
            return MathlabContestSubmissionResponse(
                id=existing.id,
                contest_id=existing.contest_id,
                student_id=existing.student_id,
                student_name=current_user.full_name or current_user.username,
                auto_score=existing.auto_score,
                auto_passed=existing.auto_passed,
                final_score=existing.final_score,
                passed=existing.passed,
                elapsed_sec=existing.elapsed_sec,
                payload=existing.payload,
                submitted_at=existing.submitted_at,
            )
        existing.auto_score = auto_score
        existing.auto_passed = auto_passed
        existing.final_score = auto_score
        existing.passed = auto_passed
        existing.elapsed_sec = body.elapsed_sec
        existing.payload = body.payload
        existing.submitted_at = datetime.utcnow()
        sub = existing
    else:
        sub = MathlabContestSubmission(
            contest_id=contest_id,
            student_id=cast(int, current_user.id),
            auto_score=auto_score,
            auto_passed=auto_passed,
            final_score=auto_score,
            passed=auto_passed,
            elapsed_sec=body.elapsed_sec,
            payload=body.payload,
        )
        db.add(sub)

    await db.commit()
    await db.refresh(sub)

    resp = MathlabContestSubmissionResponse(
        id=sub.id,
        contest_id=sub.contest_id,
        student_id=sub.student_id,
        student_name=current_user.full_name or current_user.username,
        auto_score=sub.auto_score,
        auto_passed=sub.auto_passed,
        final_score=sub.final_score,
        passed=sub.passed,
        elapsed_sec=sub.elapsed_sec,
        payload=sub.payload,
        submitted_at=sub.submitted_at,
    )

    await _broadcast_contest_event(
        cast(int, contest.session_id),
        "mathlab_contest_submission",
        {
            "contest_id": contest_id,
            "student_id": current_user.id,
            "student_name": resp.student_name,
            "final_score": sub.final_score,
            "passed": sub.passed,
            "elapsed_sec": sub.elapsed_sec,
        },
    )
    return resp


@router.patch(
    "/mathlab-contest/submissions/{submission_id}/score",
    response_model=MathlabContestSubmissionResponse,
)
async def update_submission_score(
    submission_id: int,
    body: MathlabContestScoreUpdate,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    sub = await db.get(MathlabContestSubmission, submission_id)
    if not sub:
        raise HTTPException(status_code=404, detail="提交不存在")
    contest = await db.get(MathlabContest, sub.contest_id)
    if not contest:
        raise HTTPException(status_code=404, detail="竞赛不存在")
    session = await _get_session_or_404(db, cast(int, contest.session_id))
    await _require_teacher(session, current_user)

    sub.final_score = min(100.0, max(0.0, float(body.final_score)))
    sub.passed = body.passed if body.passed is not None else sub.final_score >= int(
        contest.pass_threshold or 85
    )
    await db.commit()
    await db.refresh(sub)

    student = await db.get(User, sub.student_id)
    name = (student.full_name or student.username) if student else None

    await _broadcast_contest_event(
        cast(int, contest.session_id),
        "mathlab_contest_submission",
        {
            "contest_id": contest.id,
            "student_id": sub.student_id,
            "student_name": name,
            "final_score": sub.final_score,
            "passed": sub.passed,
            "elapsed_sec": sub.elapsed_sec,
            "teacher_override": True,
        },
    )

    return MathlabContestSubmissionResponse(
        id=sub.id,
        contest_id=sub.contest_id,
        student_id=sub.student_id,
        student_name=name,
        auto_score=sub.auto_score,
        auto_passed=sub.auto_passed,
        final_score=sub.final_score,
        passed=sub.passed,
        elapsed_sec=sub.elapsed_sec,
        payload=sub.payload,
        submitted_at=sub.submitted_at,
    )
