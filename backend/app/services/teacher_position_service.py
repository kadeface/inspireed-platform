"""
教师职务类型服务

提供教师职务类型的CRUD操作和业务逻辑
"""

import logging
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from sqlalchemy.exc import IntegrityError

from app.models.teacher_position import TeacherPositionType
from app.schemas.teacher_position import (
    TeacherPositionTypeCreate,
    TeacherPositionTypeUpdate,
)

logger = logging.getLogger(__name__)


class TeacherPositionServiceError(Exception):
    """教师职务类型服务错误"""
    pass


class TeacherPositionService:
    """教师职务类型服务"""

    @staticmethod
    async def create_position_type(
        db: AsyncSession,
        position_type_in: TeacherPositionTypeCreate,
    ) -> TeacherPositionType:
        """
        创建教师职务类型

        Args:
            db: 数据库会话
            position_type_in: 职务类型创建数据

        Returns:
            创建的职务类型对象

        Raises:
            TeacherPositionServiceError: 如果创建失败
        """
        try:
            # 检查名称是否已存在
            existing = await db.execute(
                select(TeacherPositionType).where(TeacherPositionType.name == position_type_in.name)
            )
            if existing.scalar_one_or_none():
                raise TeacherPositionServiceError(f"职务类型名称 '{position_type_in.name}' 已存在")

            # 检查代码是否已存在（如果提供了代码）
            if position_type_in.code:
                existing_code = await db.execute(
                    select(TeacherPositionType).where(TeacherPositionType.code == position_type_in.code)
                )
                if existing_code.scalar_one_or_none():
                    raise TeacherPositionServiceError(f"职务类型代码 '{position_type_in.code}' 已存在")

            # 创建职务类型
            position_type = TeacherPositionType(**position_type_in.model_dump())
            db.add(position_type)
            await db.commit()
            await db.refresh(position_type)
            return position_type

        except IntegrityError as e:
            await db.rollback()
            logger.error(f"创建职务类型失败（数据库约束错误）：{str(e)}")
            raise TeacherPositionServiceError("创建职务类型失败：数据约束冲突")
        except TeacherPositionServiceError:
            raise
        except Exception as e:
            await db.rollback()
            logger.error(f"创建职务类型失败：{str(e)}", exc_info=True)
            raise TeacherPositionServiceError(f"创建职务类型失败：{str(e)}")

    @staticmethod
    async def get_position_type(
        db: AsyncSession,
        position_type_id: int,
    ) -> Optional[TeacherPositionType]:
        """
        获取单个职务类型

        Args:
            db: 数据库会话
            position_type_id: 职务类型ID

        Returns:
            职务类型对象，如果未找到返回None
        """
        result = await db.execute(
            select(TeacherPositionType).where(TeacherPositionType.id == position_type_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_position_type_by_name(
        db: AsyncSession,
        name: str,
    ) -> Optional[TeacherPositionType]:
        """
        根据名称查找职务类型

        Args:
            db: 数据库会话
            name: 职务类型名称

        Returns:
            职务类型对象，如果未找到返回None
        """
        result = await db.execute(
            select(TeacherPositionType).where(
                and_(
                    TeacherPositionType.name == name,
                    TeacherPositionType.is_active == True,
                )
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_position_type_by_code(
        db: AsyncSession,
        code: str,
    ) -> Optional[TeacherPositionType]:
        """
        根据代码查找职务类型

        Args:
            db: 数据库会话
            code: 职务类型代码

        Returns:
            职务类型对象，如果未找到返回None
        """
        if not code:
            return None
        
        result = await db.execute(
            select(TeacherPositionType).where(
                and_(
                    TeacherPositionType.code == code,
                    TeacherPositionType.is_active == True,
                )
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def list_position_types(
        db: AsyncSession,
        category: Optional[str] = None,
        is_active: Optional[bool] = None,
        search: Optional[str] = None,
    ) -> List[TeacherPositionType]:
        """
        获取职务类型列表

        Args:
            db: 数据库会话
            category: 职务分类筛选
            is_active: 是否激活筛选
            search: 搜索关键词（名称、代码、描述）

        Returns:
            职务类型列表
        """
        query = select(TeacherPositionType)

        if category is not None:
            query = query.where(TeacherPositionType.category == category)

        if is_active is not None:
            query = query.where(TeacherPositionType.is_active == is_active)

        if search:
            search_filter = or_(
                TeacherPositionType.name.ilike(f"%{search}%"),
                TeacherPositionType.code.ilike(f"%{search}%"),
                TeacherPositionType.description.ilike(f"%{search}%"),
            )
            query = query.where(search_filter)

        # 按排序权重和名称排序
        query = query.order_by(TeacherPositionType.sort_order, TeacherPositionType.name)

        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def update_position_type(
        db: AsyncSession,
        position_type_id: int,
        position_type_in: TeacherPositionTypeUpdate,
    ) -> TeacherPositionType:
        """
        更新职务类型

        Args:
            db: 数据库会话
            position_type_id: 职务类型ID
            position_type_in: 更新数据

        Returns:
            更新后的职务类型对象

        Raises:
            TeacherPositionServiceError: 如果更新失败
        """
        position_type = await TeacherPositionService.get_position_type(db, position_type_id)
        if not position_type:
            raise TeacherPositionServiceError(f"职务类型ID {position_type_id} 不存在")

        # 系统预设的职务类型不能修改名称和代码
        if position_type.is_system:
            if position_type_in.name and position_type_in.name != position_type.name:
                raise TeacherPositionServiceError("系统预设的职务类型不能修改名称")
            if position_type_in.code and position_type_in.code != position_type.code:
                raise TeacherPositionServiceError("系统预设的职务类型不能修改代码")

        try:
            # 检查名称是否已被其他记录使用
            if position_type_in.name and position_type_in.name != position_type.name:
                existing = await db.execute(
                    select(TeacherPositionType).where(
                        and_(
                            TeacherPositionType.name == position_type_in.name,
                            TeacherPositionType.id != position_type_id,
                        )
                    )
                )
                if existing.scalar_one_or_none():
                    raise TeacherPositionServiceError(f"职务类型名称 '{position_type_in.name}' 已被使用")

            # 检查代码是否已被其他记录使用
            if position_type_in.code and position_type_in.code != position_type.code:
                existing_code = await db.execute(
                    select(TeacherPositionType).where(
                        and_(
                            TeacherPositionType.code == position_type_in.code,
                            TeacherPositionType.id != position_type_id,
                        )
                    )
                )
                if existing_code.scalar_one_or_none():
                    raise TeacherPositionServiceError(f"职务类型代码 '{position_type_in.code}' 已被使用")

            # 更新字段
            update_data = position_type_in.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(position_type, field, value)

            await db.commit()
            await db.refresh(position_type)
            return position_type

        except IntegrityError as e:
            await db.rollback()
            logger.error(f"更新职务类型失败（数据库约束错误）：{str(e)}")
            raise TeacherPositionServiceError("更新职务类型失败：数据约束冲突")
        except TeacherPositionServiceError:
            raise
        except Exception as e:
            await db.rollback()
            logger.error(f"更新职务类型失败：{str(e)}", exc_info=True)
            raise TeacherPositionServiceError(f"更新职务类型失败：{str(e)}")

    @staticmethod
    async def delete_position_type(
        db: AsyncSession,
        position_type_id: int,
    ) -> bool:
        """
        删除职务类型

        Args:
            db: 数据库会话
            position_type_id: 职务类型ID

        Returns:
            True如果删除成功

        Raises:
            TeacherPositionServiceError: 如果删除失败
        """
        position_type = await TeacherPositionService.get_position_type(db, position_type_id)
        if not position_type:
            raise TeacherPositionServiceError(f"职务类型ID {position_type_id} 不存在")

        # 系统预设的职务类型不能删除
        if position_type.is_system:
            raise TeacherPositionServiceError("系统预设的职务类型不能删除，只能停用")

        # 检查是否有关联的教学任务
        # 注意：这里需要检查TeacherTeachingAssignment表，但由于循环导入问题，我们使用原始SQL
        from sqlalchemy import text
        result = await db.execute(
            text("SELECT COUNT(*) FROM teacher_teaching_assignments WHERE position_type_id = :id"),
            {"id": position_type_id}
        )
        count = result.scalar()
        if count and count > 0:
            raise TeacherPositionServiceError(f"该职务类型正在被 {count} 条教学任务使用，无法删除")

        try:
            await db.delete(position_type)
            await db.commit()
            return True

        except Exception as e:
            await db.rollback()
            logger.error(f"删除职务类型失败：{str(e)}", exc_info=True)
            raise TeacherPositionServiceError(f"删除职务类型失败：{str(e)}")
