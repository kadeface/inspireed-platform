"""
Cell（单元）模型
"""

from datetime import datetime
from enum import Enum
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Boolean,
    DateTime,
    ForeignKey,
    Enum as SQLEnum,
    JSON,
)
from sqlalchemy.orm import relationship

from app.core.database import Base


class CellType(str, Enum):
    """Cell类型枚举"""

    TEXT = "text"  # 教学内容单元
    VIDEO = "video"  # 视频教学单元
    CODE = "code"  # 可执行代码单元
    SIM = "sim"  # 仿真单元
    QA = "qa"  # 问答交互单元
    CHART = "chart"  # 数据可视化单元
    CONTEST = "contest"  # 竞技任务单元
    PARAM = "param"  # 参数设置单元
    ACTIVITY = "activity"  # 教学活动单元（测验、问卷、作业、评价）
    FLOWCHART = "flowchart"  # 流程图单元


class CognitiveLevel(str, Enum):
    """认知层级（基于Bloom分类学）"""

    REMEMBER = "remember"  # 记忆：识别、回忆事实和基本概念
    UNDERSTAND = "understand"  # 理解：解释思想或概念，用自己的话表述
    APPLY = "apply"  # 应用：在新情境中使用信息
    ANALYZE = "analyze"  # 分析：将信息分解为组成部分，找出关系
    EVALUATE = "evaluate"  # 评价：根据标准进行判断和批判
    CREATE = "create"  # 创造：将元素组合成新的整体，产生新事物


class Cell(Base):
    """Cell单元模型"""

    __tablename__ = "cells"

    id = Column(Integer, primary_key=True, index=True)

    # 所属教案
    lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=False)

    # Cell类型
    cell_type = Column(SQLEnum(CellType), nullable=False)

    # Cell标题
    title = Column(String(200), nullable=True)

    # Cell内容（JSON格式，根据类型不同结构不同）
    content = Column(JSON, nullable=False, default=dict)

    # Cell配置（如执行参数、显示选项等）
    config = Column(JSON, nullable=True, default=dict)

    # 顺序
    order = Column(Integer, default=0, nullable=False)

    # 是否可编辑（对学生）
    editable = Column(Boolean, default=False, nullable=False)

    # 【学习科学优化】认知层级（基于Bloom分类学）
    cognitive_level = Column(
        SQLEnum(CognitiveLevel),
        nullable=True,
        comment="认知层级：remember/understand/apply/analyze/evaluate/create",
    )

    # 【学习科学优化】前置Cell依赖（必须先完成才能解锁）
    prerequisite_cells = Column(
        JSON, nullable=True, default=list, comment="前置依赖的Cell ID列表，例如: [1, 2, 3]"
    )

    # 【学习科学优化】掌握标准（自动评估配置）
    mastery_criteria = Column(
        JSON,
        nullable=True,
        comment='掌握标准配置，例如: {"min_attempts": 1, "min_accuracy": 0.8, "max_time_seconds": 300}',
    )

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # 关联关系
    lesson = relationship("Lesson", foreign_keys=[lesson_id])
    # execution_logs = relationship("ExecutionLog", back_populates="cell")

    def __repr__(self) -> str:
        return f"<Cell(id={self.id}, type={self.cell_type}, lesson_id={self.lesson_id})>"
