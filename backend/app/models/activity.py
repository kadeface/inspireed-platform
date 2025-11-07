"""
教学活动提交模型
"""

from datetime import datetime
from enum import Enum
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Boolean,
    Float,
    DateTime,
    ForeignKey,
    Enum as SQLEnum,
    JSON,
    Index,
)
from sqlalchemy.orm import relationship

from app.core.database import Base


class ActivitySubmissionStatus(str, Enum):
    """活动提交状态"""

    DRAFT = "draft"  # 草稿
    SUBMITTED = "submitted"  # 已提交
    GRADED = "graded"  # 已评分
    RETURNED = "returned"  # 已退回（需要修改）


class PeerReviewStatus(str, Enum):
    """互评状态"""

    PENDING = "pending"  # 待互评
    IN_PROGRESS = "in_progress"  # 互评中
    COMPLETED = "completed"  # 已完成


class ActivitySubmission(Base):
    """学生活动提交记录（统一表）"""

    __tablename__ = "activity_submissions"

    id = Column(Integer, primary_key=True, index=True)

    # 关联信息
    cell_id = Column(Integer, ForeignKey("cells.id"), nullable=False, index=True)
    lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=False, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # 提交内容（JSON格式，包含所有题目的答案）
    # 示例：
    # {
    #   "item_1": {"answer": "A", "correct": true, "score": 10},
    #   "item_2": {"answer": ["A", "C"], "correct": false, "score": 0},
    #   "item_3": {"text": "这是我的答案...", "score": 8},
    #   "item_4": {"files": ["url1.pdf", "url2.docx"], "score": null}
    # }
    responses = Column(JSON, nullable=False, default=dict)

    # 评分
    score = Column(Float, nullable=True)  # 实际得分
    max_score = Column(Float, nullable=True)  # 满分
    auto_graded = Column(Boolean, default=False, nullable=False)  # 是否自动评分

    # 状态
    status = Column(
        SQLEnum(ActivitySubmissionStatus),
        default=ActivitySubmissionStatus.DRAFT,
        nullable=False,
        index=True,
    )

    # 教师反馈
    teacher_feedback = Column(Text, nullable=True)
    graded_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    # 时间戳
    started_at = Column(DateTime, nullable=True)  # 开始答题时间
    submitted_at = Column(DateTime, nullable=True)  # 提交时间
    graded_at = Column(DateTime, nullable=True)  # 评分时间

    # 元数据
    submission_count = Column(Integer, default=1, nullable=False)  # 第几次提交
    time_spent = Column(Integer, nullable=True)  # 花费时间（秒）
    is_late = Column(Boolean, default=False, nullable=False)  # 是否迟交

    # 离线支持：本地保存的版本号
    version = Column(Integer, default=1, nullable=False)
    # 离线数据同步标记
    synced = Column(Boolean, default=True, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # 关联关系
    student = relationship("User", foreign_keys=[student_id])
    grader = relationship("User", foreign_keys=[graded_by])
    lesson = relationship("Lesson", foreign_keys=[lesson_id])
    peer_reviews_received = relationship(
        "PeerReview", foreign_keys="PeerReview.submission_id", back_populates="submission"
    )
    peer_reviews_given = relationship(
        "PeerReview", foreign_keys="PeerReview.reviewer_id", back_populates="reviewer"
    )

    def __repr__(self) -> str:
        return f"<ActivitySubmission(id={self.id}, student_id={self.student_id}, status={self.status})>"


class PeerReview(Base):
    """学生互评记录"""

    __tablename__ = "peer_reviews"

    id = Column(Integer, primary_key=True, index=True)

    # 关联信息
    submission_id = Column(
        Integer, ForeignKey("activity_submissions.id"), nullable=False, index=True
    )
    reviewer_id = Column(
        Integer, ForeignKey("users.id"), nullable=False, index=True
    )  # 评价者
    lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=False, index=True)
    cell_id = Column(Integer, ForeignKey("cells.id"), nullable=False, index=True)

    # 评价内容
    # 示例（使用评分标准）：
    # {
    #   "criterion_1": {"level": 4, "score": 25, "comment": "代码质量很好"},
    #   "criterion_2": {"level": 3, "score": 20, "comment": "功能基本完整"},
    #   "overall_comment": "整体表现不错，建议改进..."
    # }
    review_data = Column(JSON, nullable=False, default=dict)

    # 评分
    score = Column(Float, nullable=True)  # 互评给出的分数
    max_score = Column(Float, nullable=True)

    # 文本反馈
    comment = Column(Text, nullable=True)

    # 状态
    status = Column(
        SQLEnum(PeerReviewStatus),
        default=PeerReviewStatus.PENDING,
        nullable=False,
    )

    # 是否匿名互评
    is_anonymous = Column(Boolean, default=True, nullable=False)

    # 时间戳
    assigned_at = Column(DateTime, default=datetime.utcnow, nullable=False)  # 分配时间
    completed_at = Column(DateTime, nullable=True)  # 完成时间

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # 关联关系
    submission = relationship(
        "ActivitySubmission", foreign_keys=[submission_id], back_populates="peer_reviews_received"
    )
    reviewer = relationship(
        "User", foreign_keys=[reviewer_id], back_populates="peer_reviews_given"
    )
    lesson = relationship("Lesson", foreign_keys=[lesson_id])

    def __repr__(self) -> str:
        return f"<PeerReview(id={self.id}, submission_id={self.submission_id}, reviewer_id={self.reviewer_id})>"


class ActivityStatistics(Base):
    """活动统计数据（用于快速查询）"""

    __tablename__ = "activity_statistics"

    id = Column(Integer, primary_key=True, index=True)
    cell_id = Column(Integer, ForeignKey("cells.id"), nullable=False, unique=True)
    lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=False, index=True)

    # 提交统计
    total_students = Column(Integer, default=0, nullable=False)
    draft_count = Column(Integer, default=0, nullable=False)
    submitted_count = Column(Integer, default=0, nullable=False)
    graded_count = Column(Integer, default=0, nullable=False)

    # 成绩统计
    average_score = Column(Float, nullable=True)
    highest_score = Column(Float, nullable=True)
    lowest_score = Column(Float, nullable=True)
    median_score = Column(Float, nullable=True)

    # 时间统计
    average_time_spent = Column(Integer, nullable=True)  # 平均用时（秒）

    # 题目级别的统计
    # 示例：
    # {
    #   "item_1": {
    #     "type": "single-choice",
    #     "total": 30,
    #     "correct_count": 25,
    #     "accuracy": 0.83,
    #     "option_distribution": {"A": 25, "B": 3, "C": 2}
    #   },
    #   "item_2": {
    #     "type": "rubric-item",
    #     "avg_score": 7.5,
    #     "score_distribution": {"level_1": 2, "level_2": 8, "level_3": 15, "level_4": 5}
    #   }
    # }
    item_statistics = Column(JSON, nullable=True, default=dict)

    # 互评统计
    peer_review_count = Column(Integer, default=0, nullable=False)
    avg_peer_review_score = Column(Float, nullable=True)

    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # 关联关系
    lesson = relationship("Lesson", foreign_keys=[lesson_id])

    def __repr__(self) -> str:
        return f"<ActivityStatistics(id={self.id}, cell_id={self.cell_id})>"


# 创建索引以优化查询性能
Index("idx_activity_sub_cell_student", ActivitySubmission.cell_id, ActivitySubmission.student_id)
Index("idx_activity_sub_lesson_status", ActivitySubmission.lesson_id, ActivitySubmission.status)
Index("idx_peer_review_submission", PeerReview.submission_id)
Index("idx_peer_review_reviewer", PeerReview.reviewer_id)

