"""
资源库资产模型
"""

from datetime import datetime
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Integer,
    String,
    Text,
    ForeignKey,
    Index,
)
from sqlalchemy.orm import relationship

from app.core.database import Base


class LibraryAsset(Base):
    """资源库资产模型（学校级别的共享资源库）"""

    __tablename__ = "library_assets"

    id = Column(Integer, primary_key=True, index=True)
    
    # 归属与权限
    school_id = Column(
        Integer, ForeignKey("schools.id"), nullable=False, comment="所属学校ID"
    )
    owner_user_id = Column(
        Integer, ForeignKey("users.id"), nullable=False, comment="上传者ID"
    )
    subject_id = Column(
        Integer, ForeignKey("subjects.id"), nullable=True, comment="学科ID（可选）"
    )
    grade_id = Column(
        Integer, ForeignKey("grades.id"), nullable=True, comment="年级ID（可选，NULL表示跨年级通用）"
    )
    
    # 知识点分类（用于小学奥数等知识点资源）
    knowledge_point_category = Column(
        String(100), nullable=True, comment="知识点分类（如：计算类/速算技巧、几何类/图形认知）"
    )
    knowledge_point_name = Column(
        String(200), nullable=True, comment="具体知识点名称（如：乘法口诀可视化）"
    )
    
    # 基本信息
    title = Column(String(200), nullable=False, comment="资源标题")
    description = Column(Text, nullable=True, comment="资源描述")
    
    # 资源类型与元数据
    asset_type = Column(
        String(20), nullable=False, comment="资源类型：pdf/video/image/audio/document/link/zip/interactive/other"
    )
    mime_type = Column(String(100), nullable=True, comment="MIME类型")
    size_bytes = Column(Integer, nullable=True, comment="文件大小（字节）")
    
    # 存储信息
    storage_provider = Column(
        String(20), default="local", nullable=False, comment="存储提供商：local/minio"
    )
    storage_key = Column(
        String(500), nullable=False, comment="存储键/相对路径"
    )
    public_url = Column(
        String(500), nullable=True, comment="公开访问URL（如 /uploads/resources/xxx）"
    )
    sha256 = Column(String(64), nullable=True, comment="文件SHA256哈希（用于去重）")
    
    # 预览与附加信息
    thumbnail_url = Column(String(500), nullable=True, comment="缩略图URL")
    page_count = Column(Integer, nullable=True, comment="页数（PDF）")
    duration_seconds = Column(Integer, nullable=True, comment="时长（视频/音频，秒）")
    
    # 可见性与状态
    visibility = Column(
        String(20), 
        default="teacher_only", 
        nullable=False, 
        comment="可见性：teacher_only（仅上传者）/school（全校可见）"
    )
    status = Column(
        String(20), 
        default="active", 
        nullable=False, 
        comment="状态：active/processing/disabled/deleted"
    )
    
    # 统计数据
    view_count = Column(
        Integer,
        default=0,
        nullable=False,
        comment="点击/查看次数"
    )
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    
    # 关联关系
    school = relationship("School", foreign_keys=[school_id])
    owner = relationship("User", foreign_keys=[owner_user_id])
    subject = relationship("Subject", foreign_keys=[subject_id])
    grade = relationship("Grade", foreign_keys=[grade_id])
    
    # 索引（性能优化）
    # 注意：ix_library_assets_school_subject 和 ix_library_assets_school_grade 
    # 在迁移文件中创建，避免重复定义
    __table_args__ = (
        Index("ix_library_assets_school_updated", "school_id", "updated_at"),
        Index("ix_library_assets_school_type", "school_id", "asset_type"),
        Index("ix_library_assets_school_visibility_status", "school_id", "visibility", "status"),
        # ix_library_assets_school_subject 在迁移 018 中创建
        # ix_library_assets_school_grade 在迁移 20251214_0826 中创建
        # ix_library_assets_knowledge_point 在迁移中添加
        Index("ix_library_assets_sha256", "sha256"),
    )
    
    def __repr__(self) -> str:
        return f"<LibraryAsset(id={self.id}, title={self.title}, type={self.asset_type})>"
