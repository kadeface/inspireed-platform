"""
教师职务类型模型

支持自定义职务类型，如：班主任、学科教师、校长、教研室主任等
"""

from datetime import datetime
from sqlalchemy import (
    Boolean,
    Column,
    Integer,
    String,
    DateTime,
    Text,
    Index,
)
from sqlalchemy.orm import relationship

from app.core.database import Base


class TeacherPositionType(Base):
    """教师职务类型表（支持自定义）"""
    __tablename__ = "teacher_position_types"

    id = Column(Integer, primary_key=True, index=True)
    
    # 职务名称
    name = Column(String(50), nullable=False, unique=True, index=True, comment="职务名称，如：班主任、学科教师、校长、教研室主任")
    
    # 职务代码（用于系统识别，可选）
    code = Column(String(50), nullable=True, unique=True, index=True, comment="职务代码，如：head_teacher、subject_teacher、principal")
    
    # 职务描述
    description = Column(Text, nullable=True, comment="职务描述")
    
    # 职务分类（用于分组显示）
    category = Column(String(50), nullable=True, index=True, comment="职务分类，如：教学类、管理类、行政类")
    
    # 排序权重（用于显示顺序）
    sort_order = Column(Integer, default=0, nullable=False, comment="排序权重，数字越小越靠前")
    
    # 是否系统预设（系统预设的职务不能删除，只能停用）
    is_system = Column(Boolean, default=False, nullable=False, comment="是否系统预设")
    
    # 状态
    is_active = Column(Boolean, default=True, nullable=False, index=True, comment="是否激活")
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False, comment="更新时间")
    
    # 关联关系（TeacherTeachingAssignment在teacher.py中定义，使用backref）
    # assignments = relationship("TeacherTeachingAssignment", back_populates="position_type")
    
    # 索引
    __table_args__ = (
        Index('idx_position_category_active', 'category', 'is_active'),
    )
    
    def __repr__(self) -> str:
        return f"<TeacherPositionType(id={self.id}, name={self.name}, code={self.code})>"
