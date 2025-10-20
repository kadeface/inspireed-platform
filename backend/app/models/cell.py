"""
Cell（单元）模型
"""
from datetime import datetime
from enum import Enum
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime,
    ForeignKey, Enum as SQLEnum, JSON
)
from sqlalchemy.orm import relationship

from app.core.database import Base


class CellType(str, Enum):
    """Cell类型枚举"""
    TEXT = "text"           # 教学内容单元
    PARAM = "param"         # 参数设置单元
    CODE = "code"           # 可执行代码单元
    SIM = "sim"             # 仿真单元
    QA = "qa"               # 问答交互单元
    CHART = "chart"         # 数据可视化单元
    CONTEST = "contest"     # 竞技任务单元


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
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # 关联关系
    lesson = relationship("Lesson", foreign_keys=[lesson_id])
    # execution_logs = relationship("ExecutionLog", back_populates="cell")
    
    def __repr__(self) -> str:
        return f"<Cell(id={self.id}, type={self.cell_type}, lesson_id={self.lesson_id})>"

