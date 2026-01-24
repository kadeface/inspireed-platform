"""
考试考场安排API

提供考场管理、自动分配、监考安排、PDF导出等功能
"""

import logging
import zipfile
import io
from typing import Any, List
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import selectinload

from app.api.deps import get_db, get_current_active_user
from app.models import User, UserRole
from app.models.evaluation import Exam
from app.models.exam_room import ExamRoom, ExamProctor
from app.schemas.exam_room import (
    ExamRoomCreate,
    ExamRoomUpdate,
    ExamRoomResponse,
    ExamRoomStudentResponse,
    ExamProctorResponse,
    AutoAssignRoomsRequest,
    AutoAssignProctorsRequest,
    ProctorAssignmentResponse,
)
from app.services.exam_room_service import ExamRoomService
from app.services.exam_document_generator import ExamDocumentGenerator

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/auto-assign", response_model=List[ExamRoomResponse])
async def auto_assign_exam_rooms(
    exam_id: int,
    request: AutoAssignRoomsRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    自动分配考场

    权限说明：
    - 管理员、区县管理员、学校管理员可以分配考场

    功能：
    - 根据学生数量和考场容量自动创建考场
    - 支持按班级编排或混排
    - 自动生成考号
    - 可选择使用现有教室作为考场
    """
    # 权限检查
    if current_user.role not in [
        UserRole.ADMIN,
        UserRole.DISTRICT_ADMIN,
        UserRole.SCHOOL_ADMIN,
    ]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="权限不足")

    # 验证考试是否存在
    exam = await db.get(Exam, exam_id)
    if not exam:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="考试不存在")

    # 自动分配考场
    service = ExamRoomService()
    try:
        rooms = await service.auto_assign_rooms(exam_id, request, db)

        # 重新查询考场以预加载所有关系
        from sqlalchemy.orm import selectinload
        from app.models.exam_room import ExamRoom

        room_ids = [r.id for r in rooms]
        result = await db.execute(
            select(ExamRoom)
            .options(
                selectinload(ExamRoom.students),
                selectinload(ExamRoom.proctors),
            )
            .where(ExamRoom.id.in_(room_ids))
        )
        loaded_rooms = result.scalars().all()

        # 按原始顺序排序
        room_dict = {r.id: r for r in loaded_rooms}
        ordered_rooms = [room_dict[rid] for rid in room_ids if rid in room_dict]

        return ordered_rooms
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to auto-assign rooms: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"分配考场失败: {str(e)}"
        )


@router.post("/proctors/auto-assign", response_model=ProctorAssignmentResponse)
async def auto_assign_proctors(
    exam_id: int,
    request: AutoAssignProctorsRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    自动分配监考教师

    权限说明：
    - 管理员、区县管理员、学校管理员可以分配监考

    功能：
    - 每个考场自动分配2名监考（1主1副）
    - 避免监考本班（可选）
    - 仅使用本校教师（可选）
    """
    # 权限检查
    if current_user.role not in [
        UserRole.ADMIN,
        UserRole.DISTRICT_ADMIN,
        UserRole.SCHOOL_ADMIN,
    ]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="权限不足")

    service = ExamRoomService()
    try:
        proctors = await service.auto_assign_proctors(exam_id, request, db)
        return ProctorAssignmentResponse(
            message=f"成功分配 {len(proctors)} 名监考教师",
            total_proctors=len(proctors),
            rooms_assigned=len(proctors) // 2,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to auto-assign proctors: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"分配监考失败: {str(e)}"
        )


@router.get("", response_model=List[ExamRoomResponse])
async def list_exam_rooms(
    exam_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    获取考试的所有考场

    权限说明：
    - 所有登录用户可以查看考场
    """
    result = await db.execute(
        select(ExamRoom)
        .options(selectinload(ExamRoom.students))
        .options(selectinload(ExamRoom.proctors))
        .where(ExamRoom.exam_id == exam_id)
        .order_by(ExamRoom.id)
    )
    rooms = result.scalars().all()
    return rooms


@router.get("/{room_id}", response_model=ExamRoomResponse)
async def get_exam_room(
    exam_id: int,
    room_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    获取考场详情

    权限说明：
    - 所有登录用户可以查看考场详情
    """
    result = await db.execute(
        select(ExamRoom)
        .options(selectinload(ExamRoom.students))
        .options(selectinload(ExamRoom.proctors))
        .where(and_(ExamRoom.id == room_id, ExamRoom.exam_id == exam_id))
    )
    room = result.scalar_one_or_none()

    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="考场不存在")

    return room


@router.put("/{room_id}", response_model=ExamRoomResponse)
async def update_exam_room(
    exam_id: int,
    room_id: int,
    room_update: ExamRoomUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    更新考场信息

    权限说明：
    - 管理员、区县管理员、学校管理员可以更新考场
    """
    # 权限检查
    if current_user.role not in [
        UserRole.ADMIN,
        UserRole.DISTRICT_ADMIN,
        UserRole.SCHOOL_ADMIN,
    ]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="权限不足")

    # 获取考场
    result = await db.execute(
        select(ExamRoom).where(and_(ExamRoom.id == room_id, ExamRoom.exam_id == exam_id))
    )
    room = result.scalar_one_or_none()

    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="考场不存在")

    # 更新字段
    if room_update.capacity is not None:
        room.capacity = room_update.capacity
    if room_update.arrangement_type is not None:
        room.arrangement_type = room_update.arrangement_type
    if room_update.seat_pattern is not None:
        room.seat_pattern = room_update.seat_pattern

    await db.commit()
    await db.refresh(room)

    return room


@router.delete("/{room_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_exam_room(
    exam_id: int,
    room_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> None:
    """
    删除考场

    权限说明：
    - 管理员、区县管理员、学校管理员可以删除考场

    注意：
    - 删除考场将同时删除该考场的所有学生分配和监考分配
    """
    # 权限检查
    if current_user.role not in [
        UserRole.ADMIN,
        UserRole.DISTRICT_ADMIN,
        UserRole.SCHOOL_ADMIN,
    ]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="权限不足")

    # 获取考场
    result = await db.execute(
        select(ExamRoom).where(and_(ExamRoom.id == room_id, ExamRoom.exam_id == exam_id))
    )
    room = result.scalar_one_or_none()

    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="考场不存在")

    # 删除考场（级联删除学生和监考）
    await db.delete(room)
    await db.commit()


@router.delete("/clear-all", status_code=status.HTTP_204_NO_CONTENT)
async def clear_all_exam_rooms(
    exam_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> None:
    """
    清空考试的所有考场编排

    权限说明：
    - 管理员、区县管理员、学校管理员可以清空考场

    注意：
    - 将删除该考试的所有考场、学生分配和监考分配
    - 此操作不可恢复，请谨慎使用
    """
    # 权限检查
    if current_user.role not in [
        UserRole.ADMIN,
        UserRole.DISTRICT_ADMIN,
        UserRole.SCHOOL_ADMIN,
    ]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="权限不足")

    # 检查考试是否存在
    exam = await db.get(Exam, exam_id)
    if not exam:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="考试不存在")

    # 获取所有考场
    result = await db.execute(
        select(ExamRoom).where(ExamRoom.exam_id == exam_id)
    )
    rooms = result.scalars().all()

    # 删除所有考场（级联删除学生和监考）
    count = 0
    for room in rooms:
        await db.delete(room)
        count += 1

    await db.commit()

    logger.info(f"Cleared {count} exam rooms for exam {exam_id}")


@router.get("/{room_id}/students", response_model=List[ExamRoomStudentResponse])
async def list_room_students(
    exam_id: int,
    room_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    获取考场的所有学生

    权限说明：
    - 所有登录用户可以查看考场学生
    """
    from app.models.exam_room import ExamRoomStudent

    # 验证考场是否存在
    room = await db.get(ExamRoom, room_id)
    if not room or room.exam_id != exam_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="考场不存在")

    # 获取学生
    result = await db.execute(
        select(ExamRoomStudent)
        .where(ExamRoomStudent.room_id == room_id)
        .order_by(ExamRoomStudent.seat_number)
    )
    students = result.scalars().all()
    return students


@router.get("/{room_id}/proctors", response_model=List[ExamProctorResponse])
async def list_room_proctors(
    exam_id: int,
    room_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    获取考场的所有监考教师

    权限说明：
    - 所有登录用户可以查看监考教师
    """
    from app.models.exam_room import ExamProctor

    # 验证考场是否存在
    room = await db.get(ExamRoom, room_id)
    if not room or room.exam_id != exam_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="考场不存在")

    # 获取监考
    result = await db.execute(
        select(ExamProctor).where(ExamProctor.room_id == room_id).order_by(ExamProctor.proctor_type)
    )
    proctors = result.scalars().all()
    return proctors


@router.get("/{room_id}/export/seating-chart.pdf")
async def export_seating_chart(
    exam_id: int,
    room_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    导出考场座位表PDF

    权限说明：
    - 所有登录用户可以导出座位表

    返回：
    - PDF文件下载
    """
    from app.models.exam_room import ExamRoom

    # 获取考场
    result = await db.execute(
        select(ExamRoom).where(and_(ExamRoom.id == room_id, ExamRoom.exam_id == exam_id))
    )
    room = result.scalar_one_or_none()

    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="考场不存在")

    # 获取考试信息
    exam = await db.get(Exam, exam_id)
    if not exam:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="考试不存在")

    # 生成PDF
    try:
        generator = ExamDocumentGenerator()
        pdf_bytes = await generator.generate_seating_chart(room, exam, db)

        # 返回文件
        from urllib.parse import quote
        filename = f"{exam.name}_{room.name}_座位表_{datetime.now().strftime('%Y%m%d')}.pdf"
        filename = filename.replace(" ", "_")
        encoded_filename = quote(filename.encode('utf-8'))

        return StreamingResponse(
            iter([pdf_bytes]),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"},
        )
    except Exception as e:
        logger.error(f"Failed to generate seating chart PDF: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"生成座位表失败: {str(e)}"
        )


@router.get("/{room_id}/export/exam-tickets.pdf")
async def export_exam_tickets(
    exam_id: int,
    room_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    导出考场准考证PDF

    权限说明：
    - 所有登录用户可以导出准考证

    返回：
    - PDF文件下载
    """
    from app.models.exam_room import ExamRoom

    # 获取考场
    result = await db.execute(
        select(ExamRoom).where(and_(ExamRoom.id == room_id, ExamRoom.exam_id == exam_id))
    )
    room = result.scalar_one_or_none()

    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="考场不存在")

    # 获取考试信息
    exam = await db.get(Exam, exam_id)
    if not exam:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="考试不存在")

    # 生成PDF
    try:
        generator = ExamDocumentGenerator()
        pdf_bytes = await generator.generate_exam_tickets(room, exam, db)

        # 返回文件
        from urllib.parse import quote
        filename = f"{exam.name}_{room.name}_准考证_{datetime.now().strftime('%Y%m%d')}.pdf"
        filename = filename.replace(" ", "_")
        encoded_filename = quote(filename.encode('utf-8'))

        return StreamingResponse(
            iter([pdf_bytes]),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"},
        )
    except Exception as e:
        logger.error(f"Failed to generate exam tickets PDF: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"生成准考证失败: {str(e)}"
        )


@router.get("/{room_id}/export/proctor-handbook.pdf")
async def export_proctor_handbook(
    exam_id: int,
    room_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    导出监考手册PDF

    权限说明：
    - 所有登录用户可以导出监考手册

    返回：
    - PDF文件下载
    """
    from app.models.exam_room import ExamRoom

    # 获取考场
    result = await db.execute(
        select(ExamRoom).where(and_(ExamRoom.id == room_id, ExamRoom.exam_id == exam_id))
    )
    room = result.scalar_one_or_none()

    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="考场不存在")

    # 获取考试信息
    exam = await db.get(Exam, exam_id)
    if not exam:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="考试不存在")

    # 生成PDF
    try:
        generator = ExamDocumentGenerator()
        pdf_bytes = await generator.generate_proctor_handbook(room, exam, db)

        # 返回文件
        from urllib.parse import quote
        filename = f"{exam.name}_{room.name}_监考手册_{datetime.now().strftime('%Y%m%d')}.pdf"
        filename = filename.replace(" ", "_")
        encoded_filename = quote(filename.encode('utf-8'))

        return StreamingResponse(
            iter([pdf_bytes]),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"},
        )
    except Exception as e:
        logger.error(f"Failed to generate proctor handbook PDF: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"生成监考手册失败: {str(e)}"
        )


@router.get("/export/all-documents.zip")
async def export_all_documents(
    exam_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    批量导出考试所有文档（座位表、准考证、监考手册）
    
    权限说明：
    - 所有登录用户可以批量导出文档
    
    返回：
    - ZIP文件包含所有考场的座位表、准考证、监考手册
    """
    from app.models.exam_room import ExamRoom, ExamRoomStudent
    
    # 获取考试信息
    exam = await db.get(Exam, exam_id)
    if not exam:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="考试不存在")
    
    # 获取所有考场
    result = await db.execute(
        select(ExamRoom).where(ExamRoom.exam_id == exam_id)
        .options(selectinload(ExamRoom.students))
    )
    rooms = result.scalars().all()
    
    if not rooms:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="暂无考场")
    
    # 创建ZIP文件
    zip_buffer = io.BytesIO()
    
    try:
        generator = ExamDocumentGenerator()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # 为每个考场生成文档
            for room in rooms:
                room_name_safe = room.name.replace(" ", "_")
                
                # 1. 生成座位表
                try:
                    seating_chart_bytes = await generator.generate_seating_chart(room, exam, db)
                    seating_chart_filename = f"{room_name_safe}_座位表.pdf"
                    zip_file.writestr(seating_chart_filename, seating_chart_bytes)
                    logger.info(f"Generated seating chart for room {room.id}")
                except Exception as e:
                    logger.error(f"Failed to generate seating chart for room {room.id}: {str(e)}")
                
                # 2. 生成准考证
                try:
                    exam_tickets_bytes = await generator.generate_exam_tickets(room, exam, db)
                    exam_tickets_filename = f"{room_name_safe}_准考证.pdf"
                    zip_file.writestr(exam_tickets_filename, exam_tickets_bytes)
                    logger.info(f"Generated exam tickets for room {room.id}")
                except Exception as e:
                    logger.error(f"Failed to generate exam tickets for room {room.id}: {str(e)}")
                
                # 3. 生成监考手册
                try:
                    proctor_handbook_bytes = await generator.generate_proctor_handbook(room, exam, db)
                    proctor_handbook_filename = f"{room_name_safe}_监考手册.pdf"
                    zip_file.writestr(proctor_handbook_filename, proctor_handbook_bytes)
                    logger.info(f"Generated proctor handbook for room {room.id}")
                except Exception as e:
                    logger.error(f"Failed to generate proctor handbook for room {room.id}: {str(e)}")
        
        # 准备ZIP文件下载
        zip_buffer.seek(0)
        zip_bytes = zip_buffer.getvalue()
        
        # 生成ZIP文件名
        from urllib.parse import quote
        zip_filename = f"{exam.name}_全部文档_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        zip_filename = zip_filename.replace(" ", "_")
        encoded_zip_filename = quote(zip_filename.encode('utf-8'))
        
        return StreamingResponse(
            iter([zip_bytes]),
            media_type="application/zip",
            headers={
                "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_zip_filename}"
            },
        )
        
    except Exception as e:
        logger.error(f"Failed to generate ZIP file: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"批量导出失败: {str(e)}"
        )
