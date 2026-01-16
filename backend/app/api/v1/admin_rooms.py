"""管理员-课室管理 API"""

import logging
from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload
import pandas as pd

from app.core.database import get_db
from app.api.deps import get_current_admin
from app.models import User, Room, School
from app.schemas.room import (
    RoomCreate,
    RoomUpdate,
    RoomResponse,
    RoomListResponse,
    RoomImportError,
    RoomImportResponse,
)
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/", response_model=RoomListResponse)
async def get_rooms(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=1000, description="每页数量"),
    school_id: Optional[int] = Query(None, description="学校ID筛选"),
    room_type: Optional[str] = Query(None, description="课室类型筛选"),
    building: Optional[str] = Query(None, description="楼栋筛选"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Any:
    """获取课室列表"""
    query = select(Room).options(selectinload(Room.school))

    # Apply filters
    if school_id is not None:
        query = query.where(Room.school_id == school_id)
    if room_type is not None:
        query = query.where(Room.room_type == room_type)
    if building:
        query = query.where(Room.building == building)

    # Search
    if search:
        search_filter = or_(
            Room.name.ilike(f"%{search}%"),
            Room.code.ilike(f"%{search}%"),
        )
        query = query.where(search_filter)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Apply pagination
    offset = (page - 1) * size
    query = (
        query.offset(offset)
        .limit(size)
        .order_by(Room.school_id, Room.building, Room.floor, Room.name)
    )

    result = await db.execute(query)
    rooms = result.scalars().all()

    total_pages = (total + size - 1) // size

    return RoomListResponse(
        rooms=[RoomResponse.model_validate(room) for room in rooms],
        total=total,
        page=page,
        size=size,
        total_pages=total_pages,
    )


@router.get("/{room_id}", response_model=RoomResponse)
async def get_room(
    room_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Any:
    """获取课室详情"""
    result = await db.execute(
        select(Room).options(selectinload(Room.school)).where(Room.id == room_id)
    )
    room = result.scalar_one_or_none()

    if not room:
        raise HTTPException(status_code=404, detail="课室不存在")

    return RoomResponse.model_validate(room)


@router.post("/", response_model=RoomResponse)
async def create_room(
    room_data: RoomCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Any:
    """创建课室"""
    # Validate school exists
    school_result = await db.execute(select(School).where(School.id == room_data.school_id))
    if not school_result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="学校不存在")

    # Check code uniqueness
    if room_data.code:
        existing_result = await db.execute(select(Room).where(Room.code == room_data.code))
        if existing_result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="课室编码已存在")

    # Create room
    room = Room(**room_data.model_dump())
    db.add(room)
    await db.commit()
    await db.refresh(room)

    return RoomResponse.model_validate(room)


@router.put("/{room_id}", response_model=RoomResponse)
async def update_room(
    room_id: int,
    room_data: RoomUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Any:
    """更新课室"""
    result = await db.execute(select(Room).where(Room.id == room_id))
    room = result.scalar_one_or_none()

    if not room:
        raise HTTPException(status_code=404, detail="课室不存在")

    # Update only provided fields
    update_data = room_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(room, field, value)

    await db.commit()
    await db.refresh(room)

    return RoomResponse.model_validate(room)


@router.delete("/{room_id}")
async def delete_room(
    room_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Any:
    """删除课室"""
    result = await db.execute(select(Room).where(Room.id == room_id))
    room = result.scalar_one_or_none()

    if not room:
        raise HTTPException(status_code=404, detail="课室不存在")

    await db.delete(room)
    await db.commit()

    return {"message": "课室删除成功"}


@router.post("/import", response_model=RoomImportResponse)
async def import_rooms(
    file: UploadFile = File(...),
    update_existing: bool = Query(False, description="是否更新已存在的课室"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Any:
    """批量导入课室

    Excel格式要求：
    - 必填列：学校名称、课室名称、课室类型
    - 可选列：课室编码、楼栋、楼层、座位容量、设备清单、固定分配班级、课室描述、是否激活
    - 支持格式：.xlsx, .xls

    课室类型可选值：普通教室、实验室、多媒体教室、计算机教室、音乐教室、美术教室、体育馆、报告厅
    """
    import tempfile
    import json
    from pathlib import Path as PathLib

    # 验证文件类型
    if not file.filename:
        raise HTTPException(status_code=400, detail="必须上传文件")

    file_ext = PathLib(file.filename).suffix.lower()
    if file_ext not in [".xlsx", ".xls"]:
        raise HTTPException(
            status_code=400, detail=f"只支持Excel文件格式 (.xlsx, .xls)，当前文件格式: {file_ext}"
        )

    # 保存文件到临时目录
    temp_file_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
            content = await file.read()
            if not content:
                raise HTTPException(status_code=400, detail="上传的文件为空")
            temp_file.write(content)
            temp_file_path = PathLib(temp_file.name)

        # 读取Excel文件
        try:
            df = pd.read_excel(temp_file_path)
        except Exception as e:
            logger.error(f"读取Excel文件失败: {str(e)}")
            raise HTTPException(status_code=400, detail=f"读取Excel文件失败: {str(e)}")

        # 验证必填列
        required_columns = ["学校名称", "课室名称", "课室类型"]
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise HTTPException(
                status_code=400,
                detail=f"Excel文件缺少必填列: {', '.join(missing_columns)}。"
                f"必填列: {', '.join(required_columns)}",
            )

        # 统计数据
        total = len(df)
        created = 0
        updated = 0
        skipped = 0
        errors: List[RoomImportError] = []

        # 处理每一行
        for idx, row in df.iterrows():
            row_num = idx + 2  # Excel行号（从1开始，标题行是第1行）

            try:
                # 获取必填字段
                school_name = str(row["学校名称"]).strip()
                room_name = str(row["课室名称"]).strip()
                room_type = str(row["课室类型"]).strip()

                # 验证必填字段
                if not school_name or school_name == "nan":
                    errors.append(RoomImportError(row=row_num, field="学校名称", message="学校名称不能为空"))
                    continue
                if not room_name or room_name == "nan":
                    errors.append(RoomImportError(row=row_num, field="课室名称", message="课室名称不能为空"))
                    continue
                if not room_type or room_type == "nan":
                    errors.append(RoomImportError(row=row_num, field="课室类型", message="课室类型不能为空"))
                    continue

                # 查找学校
                school_result = await db.execute(select(School).where(School.name == school_name))
                school = school_result.scalar_one_or_none()
                if not school:
                    errors.append(
                        RoomImportError(
                            row=row_num, field="学校名称", message=f"学校 '{school_name}' 不存在"
                        )
                    )
                    continue

                # 获取可选字段
                code = str(row.get("课室编码", "")).strip() if "课室编码" in row else None
                if code == "nan" or not code:
                    code = None

                building = str(row.get("楼栋", "")).strip() if "楼栋" in row else None
                if building == "nan" or not building:
                    building = None

                floor = None
                if "楼层" in row and pd.notna(row["楼层"]):
                    try:
                        floor = int(row["楼层"])
                    except (ValueError, TypeError):
                        pass

                capacity = None
                if "座位容量" in row and pd.notna(row["座位容量"]):
                    try:
                        capacity = int(row["座位容量"])
                    except (ValueError, TypeError):
                        pass

                # 解析设备清单（支持逗号分隔或JSON数组）
                equipment = None
                if "设备清单" in row and pd.notna(row["设备清单"]):
                    equipment_str = str(row["设备清单"]).strip()
                    if equipment_str and equipment_str != "nan":
                        try:
                            # 尝试解析为JSON
                            equipment = json.loads(equipment_str)
                            if not isinstance(equipment, list):
                                equipment = [equipment_str]
                        except (json.JSONDecodeError, TypeError):
                            # 按逗号分隔
                            equipment = [e.strip() for e in equipment_str.split(",") if e.strip()]

                # 固定分配班级
                assigned_classroom_id = None
                if "固定分配班级" in row and pd.notna(row["固定分配班级"]):
                    classroom_name = str(row["固定分配班级"]).strip()
                    if classroom_name and classroom_name != "nan":
                        from app.models import Classroom

                        classroom_result = await db.execute(
                            select(Classroom).where(
                                Classroom.name == classroom_name, Classroom.school_id == school.id
                            )
                        )
                        classroom = classroom_result.scalar_one_or_none()
                        if classroom:
                            assigned_classroom_id = classroom.id

                # 课室描述
                description = None
                if "课室描述" in row and pd.notna(row["课室描述"]):
                    description = str(row["课室描述"]).strip()
                    if description == "nan":
                        description = None

                # 是否激活
                is_active = True  # 默认激活
                if "是否激活" in row and pd.notna(row["是否激活"]):
                    is_active_str = str(row["是否激活"]).strip().lower()
                    if is_active_str in ["否", "false", "0", "关闭", "停用"]:
                        is_active = False

                # 检查是否存在（按学校+名称）
                existing_result = await db.execute(
                    select(Room).where(Room.school_id == school.id, Room.name == room_name)
                )
                existing_room = existing_result.scalar_one_or_none()

                if existing_room:
                    if update_existing:
                        # 更新现有课室
                        update_data = {
                            "room_type": room_type,
                            "is_active": is_active,
                        }
                        if code is not None:
                            update_data["code"] = code
                        if building is not None:
                            update_data["building"] = building
                        if floor is not None:
                            update_data["floor"] = floor
                        if capacity is not None:
                            update_data["capacity"] = capacity
                        if equipment is not None:
                            update_data["equipment"] = equipment
                        if assigned_classroom_id is not None:
                            update_data["assigned_classroom_id"] = assigned_classroom_id
                        if description is not None:
                            update_data["description"] = description

                        for field, value in update_data.items():
                            setattr(existing_room, field, value)

                        updated += 1
                    else:
                        skipped += 1
                else:
                    # 检查编码唯一性
                    if code:
                        code_check_result = await db.execute(select(Room).where(Room.code == code))
                        if code_check_result.scalar_one_or_none():
                            errors.append(
                                RoomImportError(
                                    row=row_num, field="课室编码", message=f"课室编码 '{code}' 已存在"
                                )
                            )
                            continue

                    # 创建新课室
                    new_room = Room(
                        name=room_name,
                        code=code,
                        school_id=school.id,
                        building=building,
                        floor=floor,
                        room_type=room_type,
                        capacity=capacity,
                        equipment=equipment,
                        assigned_classroom_id=assigned_classroom_id,
                        is_active=is_active,
                        description=description,
                    )
                    db.add(new_room)
                    created += 1

            except Exception as e:
                logger.error(f"处理第 {row_num} 行时出错: {str(e)}")
                errors.append(RoomImportError(row=row_num, message=f"处理失败: {str(e)}"))

        # 提交所有更改
        await db.commit()

        # 清理临时文件
        if temp_file_path and temp_file_path.exists():
            temp_file_path.unlink()

        return RoomImportResponse(
            total=total,
            success=created + updated,
            failed=len(errors),
            created=created,
            updated=updated,
            skipped=skipped,
            errors=errors,
        )

    except HTTPException:
        # 清理临时文件
        if temp_file_path and temp_file_path.exists():
            temp_file_path.unlink()
        raise
    except Exception as e:
        logger.error(f"导入课室失败: {str(e)}")
        # 清理临时文件
        if temp_file_path and temp_file_path.exists():
            temp_file_path.unlink()
        raise HTTPException(status_code=500, detail=f"导入失败: {str(e)}")
