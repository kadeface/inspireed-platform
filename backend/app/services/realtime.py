"""
实时通知服务
提供统一的 WebSocket 消息构建和目标解析
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Literal, Optional, cast
from uuid import uuid4
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.lesson import Lesson
from app.models.organization import Classroom
from app.models.classroom_session import ClassSession
from app.models.activity import ActivitySubmission
from app.models.user import User


@dataclass(frozen=True)
class Channel:
    """WebSocket 通道描述符"""
    scope: Literal["session", "lesson"]
    id: int


@dataclass
class RealtimeTarget:
    """实时通知目标描述符"""
    channel: Channel
    recipient_ids: list[int]

    @property
    def is_broadcast(self) -> bool:
        """是否为广播模式（所有人）"""
        return len(self.recipient_ids) == 0

    @classmethod
    def session(cls, session_id: int, teacher_ids: Optional[list[int]] = None):
        """创建课堂会话目标"""
        return cls(
            channel=Channel(scope="session", id=session_id),
            recipient_ids=teacher_ids or []
        )

    @classmethod
    def lesson(cls, lesson_id: int, teacher_ids: Optional[list[int]] = None):
        """创建课后教案目标"""
        return cls(
            channel=Channel(scope="lesson", id=lesson_id),
            recipient_ids=teacher_ids or []
        )


def build_event(
    *,
    type: str,
    channel: Channel,
    delivery_mode: Literal["cast", "unicast"],
    data: dict,
    ack_token: Optional[str] = None
) -> dict:
    """
    构建统一的 WebSocket 事件消息
    
    参数:
        type: 事件类型（如 'new_submission', 'submission_graded'）
        channel: 消息通道
        delivery_mode: 投递模式（cast=广播, unicast=单播）
        data: 事件数据
        ack_token: 可选的确认令牌
    
    返回:
        标准化的事件消息字典
    """
    return {
        "event_id": str(uuid4()),
        "version": 1,
        "type": type,
        "timestamp": datetime.utcnow().isoformat(),
        "channel": {
            "scope": channel.scope,
            "id": channel.id
        },
        "delivery_mode": delivery_mode,
        "data": data,
        "ack_token": ack_token,
    }


async def resolve_teacher_targets(
    db: AsyncSession,
    submission: ActivitySubmission
) -> Optional[RealtimeTarget]:
    """
    解析教师通知目标
    
    课堂模式：channel.scope = session，绑定 session_id
    课后模式：channel.scope = lesson，获取所有相关教师
    
    参数:
        db: 数据库会话
        submission: 活动提交
    
    返回:
        RealtimeTarget 或 None（如果无法确定目标）
    """
    # 课堂模式：有 session_id
    session_id = cast(int, submission.session_id) if submission.session_id is not None else None
    if session_id is not None:
        session = await db.get(ClassSession, session_id)
        teacher_id = cast(int, session.teacher_id) if session and session.teacher_id is not None else None
        if session is not None and teacher_id is not None:
            return RealtimeTarget.session(
                session_id=session_id,
                teacher_ids=[teacher_id]
            )
    
    # 课后模式：根据 lesson -> classroom -> teacher 映射
    lesson_id = cast(int, submission.lesson_id)
    teacher_ids = await fetch_teachers_by_lesson(db, lesson_id)
    if teacher_ids:
        return RealtimeTarget.lesson(
            lesson_id=lesson_id,
            teacher_ids=teacher_ids
        )
    
    return None


async def resolve_student_target(
    db: AsyncSession,
    submission: ActivitySubmission
) -> Optional[RealtimeTarget]:
    """
    解析学生通知目标
    
    课堂模式：channel.scope = session
    课后模式：channel.scope = lesson
    
    参数:
        db: 数据库会话
        submission: 活动提交
    
    返回:
        RealtimeTarget 或 None
    """
    student_id = cast(int, submission.student_id)
    session_id = cast(int, submission.session_id) if submission.session_id is not None else None
    lesson_id = cast(int, submission.lesson_id)
    
    # 课堂模式
    if session_id is not None:
        return RealtimeTarget.session(
            session_id=session_id,
            teacher_ids=[student_id]  # 复用 teacher_ids 字段存储学生ID
        )
    
    # 课后模式
    return RealtimeTarget.lesson(
        lesson_id=lesson_id,
        teacher_ids=[student_id]
    )


async def fetch_teachers_by_lesson(
    db: AsyncSession,
    lesson_id: int
) -> list[int]:
    """
    获取有权访问指定教案的所有教师ID
    
    通过 lesson -> classroom -> teacher 关系查询
    
    参数:
        db: 数据库会话
        lesson_id: 教案ID
    
    返回:
        教师ID列表
    """
    # 查询所有使用该教案的班级
    result = await db.execute(
        select(Classroom.teacher_id)
        .where(Classroom.lesson_id == lesson_id)
        .distinct()
    )
    teacher_ids = [row[0] for row in result.all() if row[0] is not None]
    
    # 如果没有班级，尝试从 lesson 的创建者获取
    if not teacher_ids:
        lesson = await db.get(Lesson, lesson_id)
        if lesson and lesson.teacher_id:
            teacher_ids = [lesson.teacher_id]
    
    return teacher_ids


async def get_submission_statistics(
    db: AsyncSession,
    cell_id: int,
    lesson_id: int,
    session_id: Optional[int] = None,
) -> dict:
    """
    获取提交统计信息
    
    课堂模式：统计参与该会话的学生
    课后模式：统计所有班级的学生
    
    参数:
        db: 数据库会话
        cell_id: Cell ID
        lesson_id: 教案ID
        session_id: 可选的会话ID（课堂模式）
    
    返回:
        统计信息字典
    """
    from sqlalchemy import func
    from app.models.activity import ActivitySubmissionStatus
    from app.models.classroom_session import StudentSessionParticipation
    
    # 计算总学生数
    if session_id:
        # 课堂模式：统计参与该会话的学生数
        total_students_result = await db.execute(
            select(func.count(StudentSessionParticipation.id))
            .where(StudentSessionParticipation.session_id == session_id)
        )
        total_students = int(total_students_result.scalar() or 0)
    else:
        # 课后模式：当前未实现完整的课后模式统计
        # TODO: 实现课后模式的学生统计逻辑
        # 可以考虑从 lesson 的 creator 的 classroom 统计，或者从提交记录推断
        total_students = 0
    
    # 统计各状态的提交数
    from app.models.activity import ActivitySubmission
    
    query = (
        select(
            ActivitySubmission.status,
            func.count(ActivitySubmission.id).label("count")
        )
        .where(ActivitySubmission.cell_id == cell_id)
        .where(ActivitySubmission.lesson_id == lesson_id)
    )
    
    if session_id:
        query = query.where(ActivitySubmission.session_id == session_id)
    
    query = query.group_by(ActivitySubmission.status)
    
    status_counts_result = await db.execute(query)
    status_dict: dict[str, int] = {
        row.status.value: cast(int, row.count)
        for row in status_counts_result.all()
    }
    
    # 计算平均分和平均用时
    avg_query = (
        select(
            func.avg(ActivitySubmission.score).label("avg_score"),
            func.avg(ActivitySubmission.time_spent).label("avg_time")
        )
        .where(ActivitySubmission.cell_id == cell_id)
        .where(ActivitySubmission.lesson_id == lesson_id)
        .where(
            ActivitySubmission.status.in_([
                ActivitySubmissionStatus.SUBMITTED,
                ActivitySubmissionStatus.GRADED
            ])
        )
    )
    
    if session_id:
        avg_query = avg_query.where(ActivitySubmission.session_id == session_id)
    
    avg_result = await db.execute(avg_query)
    avg_row = avg_result.first()
    
    # 计算已处理的提交数（已提交+已评分+已退回）
    submitted_count = status_dict.get("submitted", 0)
    graded_count = status_dict.get("graded", 0)
    returned_count = status_dict.get("returned", 0)
    draft_count = status_dict.get("draft", 0)
    
    processed_count = submitted_count + graded_count + returned_count
    not_started_count = max(0, total_students - processed_count - draft_count)
    
    return {
        "cell_id": cell_id,
        "lesson_id": lesson_id,
        "total_students": total_students,
        "submitted_count": submitted_count + graded_count,  # 已提交包括已评分
        "draft_count": draft_count,
        "not_started_count": not_started_count,
        "average_score": float(avg_row.avg_score) if avg_row and avg_row.avg_score else None,
        "average_time_spent": int(avg_row.avg_time) if avg_row and avg_row.avg_time else 0,
    }

