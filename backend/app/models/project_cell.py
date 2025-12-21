"""
项目Cell模型
"""

from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Enum as SQLEnum,
    JSON,
)
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.cell import CellType

# Import ProjectStage - no circular dependency since student_project doesn't import project_cell
from app.models.student_project import ProjectStage


class ProjectCell(Base):
    """项目Cell模型"""

    __tablename__ = "project_cells"

    id = Column(Integer, primary_key=True, index=True)

    # 所属项目
    project_id = Column(
        Integer, ForeignKey("student_projects.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # 所属5E阶段
    stage = Column(
        SQLEnum(
            ProjectStage,
            name="projectstage",
            native_enum=True,
            create_constraint=False,
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
        index=True,
        comment="5E阶段：engage, explore, explain, elaborate, evaluate",
    )

    # Cell类型（复用CellType枚举）
    cell_type = Column(SQLEnum(CellType, name="celltype"), nullable=False)

    # Cell标题
    title = Column(String(200), nullable=True)

    # Cell内容（JSON格式，根据类型不同结构不同）
    content = Column(JSON, nullable=False, default=dict)

    # Cell配置（如执行参数、显示选项等）
    config = Column(JSON, nullable=True, default=dict)

    # 顺序
    order = Column(Integer, default=0, nullable=False)

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # 关联关系
    project = relationship("StudentProject", foreign_keys=[project_id])

    def __repr__(self) -> str:
        return (
            f"<ProjectCell(id={self.id}, type={self.cell_type}, "
            f"project_id={self.project_id}, stage={self.stage})>"
        )

