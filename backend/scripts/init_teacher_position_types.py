"""
初始化教师职务类型

预设常用的职务类型：班主任、学科教师等
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

from app.core.config import settings
from app.models.teacher_position import TeacherPositionType
from app.core.database import Base


async def init_position_types():
    """初始化职务类型"""
    # 创建数据库引擎
    engine = create_async_engine(
        str(settings.DATABASE_URI),
        echo=False,
    )
    
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as db:
        # 预设职务类型
        default_positions = [
            {
                "name": "班主任",
                "code": "head_teacher",
                "description": "负责班级日常管理和学生教育工作",
                "category": "教学类",
                "sort_order": 1,
                "is_system": True,
                "is_active": True,
            },
            {
                "name": "学科教师",
                "code": "subject_teacher",
                "description": "负责特定学科的教学工作",
                "category": "教学类",
                "sort_order": 2,
                "is_system": True,
                "is_active": True,
            },
            {
                "name": "校长",
                "code": "principal",
                "description": "学校最高行政负责人",
                "category": "管理类",
                "sort_order": 10,
                "is_system": False,
                "is_active": True,
            },
            {
                "name": "副校长",
                "code": "vice_principal",
                "description": "协助校长管理学校事务",
                "category": "管理类",
                "sort_order": 11,
                "is_system": False,
                "is_active": True,
            },
            {
                "name": "教研室主任",
                "code": "research_director",
                "description": "负责学科教研组的管理和教研工作",
                "category": "管理类",
                "sort_order": 12,
                "is_system": False,
                "is_active": True,
            },
            {
                "name": "年级主任",
                "code": "grade_director",
                "description": "负责年级的管理和协调工作",
                "category": "管理类",
                "sort_order": 13,
                "is_system": False,
                "is_active": True,
            },
        ]
        
        for position_data in default_positions:
            # 检查是否已存在
            existing = await db.execute(
                select(TeacherPositionType).where(
                    TeacherPositionType.name == position_data["name"]
                )
            )
            if existing.scalar_one_or_none():
                print(f"职务类型 '{position_data['name']}' 已存在，跳过")
                continue
            
            # 创建职务类型
            position_type = TeacherPositionType(**position_data)
            db.add(position_type)
            print(f"创建职务类型：{position_data['name']}")
        
        await db.commit()
        print("职务类型初始化完成！")


if __name__ == "__main__":
    asyncio.run(init_position_types())
