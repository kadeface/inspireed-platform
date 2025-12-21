"""
班级教学助手 API
提供点名、考勤、课堂表现、纪律记录、值日等功能
"""

from datetime import datetime, timedelta, date
from typing import Any, List, Optional, Dict, cast
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, and_, or_, desc, asc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models import (
    User,
    UserRole,
    Classroom,
    ClassroomMembership,
    RoleInClass,
    AttendanceSession,
    AttendanceEntry,
    AttendanceStatus,
    PositiveBehavior,
    PositiveBehaviorType,
    DisciplineRecord,
    DisciplineEventType,
    DutyRule,
    DutyAssignment,
    DutyRotationType,
    DutyAssignmentStatus,
)
from app.schemas.classroom_assistant import (
    ClassroomInfo,
    StudentInfo,
    ClassroomMembershipCreate,
    ClassroomMembershipUpdate,
    ClassroomMembershipResponse,
    ClassroomMemberBatchImportRequest,
    ClassroomMemberBatchImportResponse,
    AttendanceSessionCreate,
    AttendanceSessionResponse,
    AttendanceSessionWithEntries,
    AttendanceEntryUpdate,
    AttendanceEntryResponse,
    PositiveBehaviorTypeInfo,
    PositiveBehaviorCreate,
    PositiveBehaviorResponse,
    PositiveBehaviorLeaderboardEntry,
    DisciplineEventTypeInfo,
    DisciplineRecordCreate,
    DisciplineRecordResponse,
    DutyRuleCreate,
    DutyRuleResponse,
    DutyGenerateRequest,
    DutyAssignmentResponse,
    DutyAssignmentUpdate,
    ClassroomSettingsUpdate,
    ClassroomSettingsResponse,
    AttendanceStats,
    PositiveBehaviorStats,
    DisciplineStats,
    DutyStats,
    ClassroomStatsResponse,
    StudentStatsResponse,
)
from app.api.deps import (
    get_current_user,
    get_current_admin,
    require_classroom_management_permission,
    require_classroom_duty_setting_permission,
    require_classroom_member,
    check_classroom_permission,
    get_classroom_membership,
)

router = APIRouter()


# ==================== 工具函数 ====================


async def find_user_by_identifiers(
    db: AsyncSession,
    user_id: Optional[int] = None,
    full_name: Optional[str] = None,
    email: Optional[str] = None,
    username: Optional[str] = None,
    student_no: Optional[str] = None,
    student_id_number: Optional[str] = None,
    classroom_id: Optional[int] = None,
) -> Optional[User]:
    """
    根据多个标识字段查找用户
    
    查找优先级：
    1. user_id（如果提供，直接查询）
    2. student_id_number（学籍号，唯一标识，跟随学生整个学习经历） - 最优先
    3. email（如果提供，直接查询）
    4. username（如果提供，直接查询）
    5. student_no（通过ClassroomMembership查找，班级内的学号）
    6. full_name（如果提供，模糊匹配）
    """
    # 优先级1: 如果提供了user_id，直接查询
    if user_id:
        return await db.get(User, user_id)
    
    # 优先级2: 通过学籍号查找（最优先，因为学籍号是唯一且不变的）
    if student_id_number:
        result = await db.execute(
            select(User).where(User.student_id_number == student_id_number)
        )
        user = result.scalar_one_or_none()
        if user:
            return user
    
    # 优先级3: 通过email查找
    if email:
        result = await db.execute(
            select(User).where(User.email == email)
        )
        user = result.scalar_one_or_none()
        if user:
            return user
    
    # 优先级4: 通过username查找
    if username:
        result = await db.execute(
            select(User).where(User.username == username)
        )
        user = result.scalar_one_or_none()
        if user:
            return user
    
    # 优先级5: 通过student_no查找（班级内的学号，通过ClassroomMembership查找）
    if student_no:
        # 如果提供了classroom_id，优先在该班级中查找
        if classroom_id:
            result = await db.execute(
                select(ClassroomMembership)
                .options(selectinload(ClassroomMembership.user))
                .where(
                    ClassroomMembership.student_no == student_no,
                    ClassroomMembership.classroom_id == classroom_id,
                )
            )
            membership = result.scalar_one_or_none()
            if membership and membership.user:
                return membership.user
        
        # 在其他班级中查找
        result = await db.execute(
            select(ClassroomMembership)
            .options(selectinload(ClassroomMembership.user))
            .where(ClassroomMembership.student_no == student_no)
            .limit(1)
        )
        membership = result.scalar_one_or_none()
        if membership and membership.user:
            return membership.user
    
    # 优先级6: 通过full_name查找（模糊匹配，如果只有一个结果则返回）
    if full_name:
        result = await db.execute(
            select(User).where(User.full_name.ilike(f"%{full_name}%"))
        )
        users = result.scalars().all()
        if len(users) == 1:
            return users[0]
        elif len(users) > 1:
            # 如果有多个匹配，尝试精确匹配
            for user in users:
                if user.full_name == full_name:
                    return user
    
    return None


def get_behavior_type_points(behavior_type: PositiveBehaviorType) -> int:
    """获取行为类型对应的积分"""
    points_map = {
        PositiveBehaviorType.ACTIVE_RESPONSE: 2,
        PositiveBehaviorType.CORRECT_ANSWER: 3,
        PositiveBehaviorType.HELP_CLASSMATE: 3,
        PositiveBehaviorType.EXCELLENT_HOMEWORK: 2,
        PositiveBehaviorType.PROACTIVE_THINKING: 2,
        PositiveBehaviorType.COLLABORATIVE_WORK: 3,
        PositiveBehaviorType.OTHER: 1,
    }
    return points_map.get(behavior_type, 1)


# ==================== 班级和成员管理 ====================


@router.get("/classrooms/mine", response_model=List[ClassroomInfo])
async def get_my_classrooms(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """获取我可进入的班级列表"""
    # 查询用户的所有成员关系
    result = await db.execute(
        select(ClassroomMembership)
        .options(selectinload(ClassroomMembership.classroom))
        .where(
            ClassroomMembership.user_id == current_user.id,
            ClassroomMembership.is_active == True,
        )
        .order_by(desc(ClassroomMembership.is_primary_class), asc(ClassroomMembership.created_at))
    )
    memberships = result.scalars().all()
    
    classrooms = []
    for membership in memberships:
        if membership.classroom:
            classroom = membership.classroom
            classrooms.append(ClassroomInfo(
                id=classroom.id,
                name=classroom.name,
                code=classroom.code,
                school_id=classroom.school_id,
                grade_id=classroom.grade_id,
                head_teacher_id=classroom.head_teacher_id,
                deputy_head_teacher_id=classroom.deputy_head_teacher_id,
                role_in_class=membership.role_in_class,
            ))
    
    # 兼容：如果没有成员关系但有 classroom_id，也包含进去
    if not classrooms and current_user.classroom_id:
        classroom = await db.get(Classroom, current_user.classroom_id)
        if classroom:
            classrooms.append(ClassroomInfo(
                id=classroom.id,
                name=classroom.name,
                code=classroom.code,
                school_id=classroom.school_id,
                grade_id=classroom.grade_id,
                head_teacher_id=classroom.head_teacher_id,
                deputy_head_teacher_id=classroom.deputy_head_teacher_id,
                role_in_class=None,
            ))
    
    return classrooms


@router.get("/classrooms/{classroom_id}/members", response_model=List[ClassroomMembershipResponse])
async def get_classroom_members(
    classroom_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """获取班级所有成员列表（管理员可直接访问，否则需要是班级成员）"""
    # 检查班级是否存在
    classroom = await db.get(Classroom, classroom_id)
    if not classroom:
        raise HTTPException(status_code=404, detail="班级不存在")
    
    # 管理员可以直接访问，否则需要检查是否是班级成员
    is_admin = isinstance(current_user.role, UserRole) and cast(UserRole, current_user.role) == UserRole.ADMIN
    if not is_admin:
        # 非管理员需要检查是否是班级成员
        membership = await get_classroom_membership(db, cast(int, current_user.id), classroom_id)
        if not membership:
            raise HTTPException(status_code=403, detail="您不是该班级的成员")
    
    # 查询班级成员列表
    result = await db.execute(
        select(ClassroomMembership)
        .options(selectinload(ClassroomMembership.user))
        .where(
            ClassroomMembership.classroom_id == classroom_id,
            ClassroomMembership.is_active == True,
        )
        .order_by(asc(ClassroomMembership.role_in_class), asc(ClassroomMembership.seat_no), asc(ClassroomMembership.created_at))
    )
    memberships = result.scalars().all()

    # 构建响应，包含用户信息
    responses = []
    for m in memberships:
        response_dict = ClassroomMembershipResponse.model_validate(m).model_dump()
        if m.user:
            response_dict["user_name"] = m.user.full_name or m.user.username
            response_dict["user_full_name"] = m.user.full_name
            response_dict["user_email"] = m.user.email
            response_dict["user_username"] = m.user.username
        responses.append(ClassroomMembershipResponse(**response_dict))
    
    return responses


@router.get("/classrooms/{classroom_id}/students", response_model=List[StudentInfo])
async def get_classroom_students(
    classroom_id: int,
    db: AsyncSession = Depends(get_db),
    membership: ClassroomMembership = Depends(require_classroom_member),
) -> Any:
    """获取班级学生列表（按座号排序）"""
    result = await db.execute(
        select(ClassroomMembership)
        .options(selectinload(ClassroomMembership.user))
        .where(
            ClassroomMembership.classroom_id == classroom_id,
            ClassroomMembership.role_in_class == RoleInClass.STUDENT,
            ClassroomMembership.is_active == True,
        )
        .order_by(asc(ClassroomMembership.seat_no), asc(ClassroomMembership.created_at))
    )
    memberships = result.scalars().all()
    
    students = []
    for membership in memberships:
        if membership.user:
            students.append(StudentInfo(
                id=membership.user.id,
                username=membership.user.username,
                full_name=membership.user.full_name,
                student_no=membership.student_no,
                seat_no=membership.seat_no,
                cadre_title=membership.cadre_title,
            ))
    
    return students


@router.post("/classrooms/{classroom_id}/members", response_model=ClassroomMembershipResponse, status_code=201)
async def add_classroom_member(
    classroom_id: int,
    data: ClassroomMembershipCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """添加班级成员（管理员可直接添加，否则需要班级管理权限）"""
    # 确保 classroom_id 匹配
    if data.classroom_id != classroom_id:
        raise HTTPException(status_code=400, detail="路径中的班级ID与请求体不一致")
    
    # 管理员可以直接添加，否则检查管理权限
    is_admin = isinstance(current_user.role, UserRole) and cast(UserRole, current_user.role) == UserRole.ADMIN
    if not is_admin:
        # 非管理员需要检查班级管理权限
        membership_check = await check_classroom_permission(
            db,
            current_user,
            classroom_id,
            [
                RoleInClass.HEAD_TEACHER_PRIMARY,
                RoleInClass.HEAD_TEACHER_DEPUTY,
                RoleInClass.SUBJECT_TEACHER,
                RoleInClass.CADRE,
            ],
        )
    
    # 检查用户是否存在
    user = await db.get(User, data.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 检查是否已是成员
    existing_result = await db.execute(
        select(ClassroomMembership).where(
            ClassroomMembership.classroom_id == classroom_id,
            ClassroomMembership.user_id == data.user_id,
        )
    )
    existing = existing_result.scalar_one_or_none()
    
    if existing:
        if existing.is_active:
            raise HTTPException(status_code=400, detail="用户已是该班级的成员")
        else:
            # 重新激活并更新信息
            existing.role_in_class = data.role_in_class
            existing.is_active = True
            existing.student_no = data.student_no
            existing.seat_no = data.seat_no
            existing.cadre_title = data.cadre_title
            existing.is_primary_class = data.is_primary_class
            await db.commit()
            await db.refresh(existing)
            return ClassroomMembershipResponse.model_validate(existing)
    
    # 创建新成员关系
    new_membership = ClassroomMembership(
        classroom_id=classroom_id,
        user_id=data.user_id,
        role_in_class=data.role_in_class,
        student_no=data.student_no,
        seat_no=data.seat_no,
        cadre_title=data.cadre_title,
        is_primary_class=data.is_primary_class,
        is_active=True,
    )
    db.add(new_membership)
    await db.commit()
    await db.refresh(new_membership)
    
    return ClassroomMembershipResponse.model_validate(new_membership)


@router.put("/classrooms/{classroom_id}/members/{user_id}", response_model=ClassroomMembershipResponse)
async def update_classroom_member(
    classroom_id: int,
    user_id: int,
    data: ClassroomMembershipUpdate,
    db: AsyncSession = Depends(get_db),
    membership: ClassroomMembership = Depends(require_classroom_management_permission),
) -> Any:
    """更新班级成员信息（仅班主任/副班主任/任课教师可用）"""
    # 查找成员关系
    member_result = await db.execute(
        select(ClassroomMembership).where(
            ClassroomMembership.classroom_id == classroom_id,
            ClassroomMembership.user_id == user_id,
        )
    )
    member = member_result.scalar_one_or_none()
    
    if not member:
        raise HTTPException(status_code=404, detail="该用户不是该班级的成员")
    
    # 更新字段
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(member, field, value)
    
    await db.commit()
    await db.refresh(member)
    
    return ClassroomMembershipResponse.model_validate(member)


@router.post("/classrooms/{classroom_id}/members/batch-import", response_model=ClassroomMemberBatchImportResponse)
async def batch_import_classroom_members(
    classroom_id: int,
    data: ClassroomMemberBatchImportRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """批量导入班级成员（管理员可直接导入，否则需要班级管理权限）"""
    # 检查班级是否存在
    classroom = await db.get(Classroom, classroom_id)
    if not classroom:
        raise HTTPException(status_code=404, detail="班级不存在")
    
    # 管理员可以直接导入，否则检查管理权限
    is_admin = isinstance(current_user.role, UserRole) and cast(UserRole, current_user.role) == UserRole.ADMIN
    if not is_admin:
        await check_classroom_permission(
            db,
            current_user,
            classroom_id,
            [
                RoleInClass.HEAD_TEACHER_PRIMARY,
                RoleInClass.HEAD_TEACHER_DEPUTY,
                RoleInClass.SUBJECT_TEACHER,
                RoleInClass.CADRE,
            ],
        )
    
    created_members: List[ClassroomMembershipResponse] = []
    errors: List[str] = []
    
    for i, member_data in enumerate(data.members):
        try:
            # 根据提供的标识字段查找用户
            user = await find_user_by_identifiers(
                db,
                user_id=member_data.user_id,
                student_id_number=member_data.student_id_number,
                full_name=member_data.full_name,
                email=member_data.email,
                username=member_data.username,
                student_no=member_data.student_no,
                classroom_id=classroom_id,
            )
            
            if not user:
                # 构建错误信息，显示尝试匹配的字段
                identifiers = []
                if member_data.user_id:
                    identifiers.append(f"用户ID={member_data.user_id}")
                if member_data.student_id_number:
                    identifiers.append(f"学籍号={member_data.student_id_number}")
                if member_data.full_name:
                    identifiers.append(f"姓名={member_data.full_name}")
                if member_data.email:
                    identifiers.append(f"邮箱={member_data.email}")
                if member_data.username:
                    identifiers.append(f"用户名={member_data.username}")
                if member_data.student_no:
                    identifiers.append(f"学号={member_data.student_no}")
                
                errors.append(f"第{i+1}行：未找到匹配的用户（{', '.join(identifiers)}）")
                continue
            
            # 检查是否已是成员
            existing_result = await db.execute(
                select(ClassroomMembership).where(
                    ClassroomMembership.classroom_id == classroom_id,
                    ClassroomMembership.user_id == user.id,
                )
            )
            existing = existing_result.scalar_one_or_none()
            
            # 使用提供的student_no或保持现有的
            final_student_no = member_data.student_no if member_data.student_no else existing.student_no if existing else None
            
            if existing:
                if existing.is_active:
                    errors.append(f"第{i+1}行：用户 {user.username} ({user.full_name or '未设置姓名'}) 已是该班级的成员")
                    continue
                else:
                    # 重新激活并更新信息
                    existing.role_in_class = member_data.role_in_class
                    existing.is_active = True
                    existing.student_no = final_student_no
                    existing.seat_no = member_data.seat_no
                    existing.cadre_title = member_data.cadre_title
                    existing.is_primary_class = member_data.is_primary_class
                    await db.flush()
                    await db.refresh(existing)
                    created_members.append(ClassroomMembershipResponse.model_validate(existing))
                    continue
            
            # 创建新成员关系
            new_membership = ClassroomMembership(
                classroom_id=classroom_id,
                user_id=user.id,
                role_in_class=member_data.role_in_class,
                student_no=final_student_no,
                seat_no=member_data.seat_no,
                cadre_title=member_data.cadre_title,
                is_primary_class=member_data.is_primary_class,
                is_active=True,
            )
            db.add(new_membership)
            await db.flush()
            await db.refresh(new_membership)
            created_members.append(ClassroomMembershipResponse.model_validate(new_membership))
            
        except Exception as e:
            errors.append(f"第{i+1}项：处理失败 - {str(e)}")
            continue
    
    await db.commit()
    
    return ClassroomMemberBatchImportResponse(
        message=f"批量导入完成，成功导入 {len(created_members)} 个成员",
        success_count=len(created_members),
        error_count=len(errors),
        errors=errors,
        created_members=created_members,
    )


@router.delete("/classrooms/{classroom_id}/members/{user_id}", status_code=204)
async def remove_classroom_member(
    classroom_id: int,
    user_id: int,
    db: AsyncSession = Depends(get_db),
    membership: ClassroomMembership = Depends(require_classroom_management_permission),
):
    """移除班级成员（软删除，设置为非活跃状态）"""
    # 查找成员关系
    member_result = await db.execute(
        select(ClassroomMembership).where(
            ClassroomMembership.classroom_id == classroom_id,
            ClassroomMembership.user_id == user_id,
            ClassroomMembership.is_active == True,
        )
    )
    member = member_result.scalar_one_or_none()
    
    if not member:
        raise HTTPException(status_code=404, detail="该用户不是该班级的活跃成员")
    
    # 软删除：设置为非活跃
    member.is_active = False
    await db.commit()
    
    # 204状态码不能有响应体，所以不返回任何内容


@router.patch("/classrooms/{classroom_id}/settings", response_model=ClassroomSettingsResponse)
async def update_classroom_settings(
    classroom_id: int,
    settings: ClassroomSettingsUpdate,
    db: AsyncSession = Depends(get_db),
    membership: ClassroomMembership = Depends(require_classroom_management_permission),
) -> Any:
    """更新班级设置（仅教师/班主任）"""
    classroom = await db.get(Classroom, classroom_id)
    if not classroom:
        raise HTTPException(status_code=404, detail="班级不存在")
    
    # 获取当前设置或初始化
    current_settings = classroom.settings or {}
    
    # 更新设置
    if settings.show_positive_behaviors_publicly is not None:
        current_settings["show_positive_behaviors_publicly"] = settings.show_positive_behaviors_publicly
    if settings.show_discipline_publicly is not None:
        current_settings["show_discipline_publicly"] = settings.show_discipline_publicly
    
    classroom.settings = current_settings
    await db.commit()
    await db.refresh(classroom)
    
    return ClassroomSettingsResponse(
        show_positive_behaviors_publicly=current_settings.get("show_positive_behaviors_publicly", False),
        show_discipline_publicly=current_settings.get("show_discipline_publicly", False),
    )


# ==================== 考勤 ====================


@router.post("/classrooms/{classroom_id}/attendance/sessions", response_model=AttendanceSessionResponse, status_code=201)
async def create_attendance_session(
    classroom_id: int,
    data: AttendanceSessionCreate,
    db: AsyncSession = Depends(get_db),
    membership: ClassroomMembership = Depends(require_classroom_management_permission),
) -> Any:
    """创建考勤会话"""
    # 检查是否有未完成的会话
    existing_session_result = await db.execute(
        select(AttendanceSession)
        .where(
            AttendanceSession.classroom_id == classroom_id,
            AttendanceSession.ended_at.is_(None),  # 未结束的会话
        )
        .order_by(desc(AttendanceSession.started_at))
        .limit(1)
    )
    existing_session = existing_session_result.scalar_one_or_none()
    if existing_session:
        raise HTTPException(
            status_code=400,
            detail=f"该班级已有未完成的点名会话（ID: {existing_session.id}），请先完成该会话后再创建新的",
        )
    
    # 获取班级所有学生
    students_result = await db.execute(
        select(ClassroomMembership)
        .where(
            ClassroomMembership.classroom_id == classroom_id,
            ClassroomMembership.role_in_class == RoleInClass.STUDENT,
            ClassroomMembership.is_active == True,
        )
    )
    students = students_result.scalars().all()
    
    if not students:
        raise HTTPException(status_code=400, detail="班级中没有学生，无法创建考勤会话")
    
    # 创建会话
    now = datetime.utcnow()
    session = AttendanceSession(
        classroom_id=classroom_id,
        initiated_by_user_id=membership.user_id,
        started_at=now,
        window_seconds=data.window_seconds,
    )
    db.add(session)
    await db.flush()  # 获取 session.id
    
    # 为所有学生创建默认出勤记录
    entries = []
    for student_membership in students:
        entry = AttendanceEntry(
            session_id=session.id,
            student_id=student_membership.user_id,
            status=AttendanceStatus.PRESENT,
            updated_by_user_id=membership.user_id,
        )
        entries.append(entry)
    
    db.add_all(entries)
    await db.commit()
    await db.refresh(session)
    
    return AttendanceSessionResponse.model_validate(session)


@router.get("/attendance/sessions/{session_id}", response_model=AttendanceSessionWithEntries)
async def get_attendance_session(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """获取考勤会话详情"""
    session = await db.get(AttendanceSession, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="考勤会话不存在")
    
    # 权限检查：必须是班级成员
    membership = await db.execute(
        select(ClassroomMembership).where(
            ClassroomMembership.user_id == current_user.id,
            ClassroomMembership.classroom_id == session.classroom_id,
            ClassroomMembership.is_active == True,
        )
    )
    if not membership.scalar_one_or_none():
        # 兼容：检查是否有 classroom_id
        if not (current_user.classroom_id == session.classroom_id):
            raise HTTPException(status_code=403, detail="无权访问该考勤会话")
    
    # 加载所有记录
    entries_result = await db.execute(
        select(AttendanceEntry)
        .where(AttendanceEntry.session_id == session_id)
        .order_by(asc(AttendanceEntry.id))
    )
    entries = entries_result.scalars().all()
    
    return AttendanceSessionWithEntries(
        **AttendanceSessionResponse.model_validate(session).model_dump(),
        entries=[AttendanceEntryResponse.model_validate(e) for e in entries],
    )


@router.put(
    "/attendance/sessions/{session_id}/entries/{student_id}",
    response_model=AttendanceEntryResponse,
)
async def update_attendance_entry(
    session_id: int,
    student_id: int,
    data: AttendanceEntryUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    membership: ClassroomMembership = Depends(require_classroom_management_permission),
) -> Any:
    """更新考勤记录（幂等）"""
    session = await db.get(AttendanceSession, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="考勤会话不存在")
    
    if session.classroom_id != membership.classroom_id:
        raise HTTPException(status_code=400, detail="会话与班级不匹配")
    
    # 查找或创建记录
    entry_result = await db.execute(
        select(AttendanceEntry).where(
            AttendanceEntry.session_id == session_id,
            AttendanceEntry.student_id == student_id,
        )
    )
    entry = entry_result.scalar_one_or_none()
    
    if not entry:
        entry = AttendanceEntry(
            session_id=session_id,
            student_id=student_id,
            status=data.status,
            updated_by_user_id=current_user.id,
        )
        db.add(entry)
    else:
        entry.status = data.status
        entry.updated_by_user_id = current_user.id
        entry.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(entry)
    
    return AttendanceEntryResponse.model_validate(entry)


@router.post("/attendance/sessions/{session_id}/mark-all-present")
async def mark_all_present(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    membership: ClassroomMembership = Depends(require_classroom_management_permission),
) -> Any:
    """一键全到"""
    session = await db.get(AttendanceSession, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="考勤会话不存在")
    
    if session.classroom_id != membership.classroom_id:
        raise HTTPException(status_code=400, detail="会话与班级不匹配")
    
    # 批量更新所有记录为出勤
    entries_result = await db.execute(
        select(AttendanceEntry).where(AttendanceEntry.session_id == session_id)
    )
    entries = entries_result.scalars().all()
    for entry in entries:
        entry.status = AttendanceStatus.PRESENT
        entry.updated_by_user_id = current_user.id
        entry.updated_at = datetime.utcnow()
    await db.commit()
    
    return {"message": "已标记全部出勤"}


@router.post("/attendance/sessions/{session_id}/complete")
async def complete_attendance_session(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    membership: ClassroomMembership = Depends(require_classroom_management_permission),
) -> Any:
    """完成考勤会话"""
    session = await db.get(AttendanceSession, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="考勤会话不存在")
    
    if session.classroom_id != membership.classroom_id:
        raise HTTPException(status_code=400, detail="会话与班级不匹配")
    
    if session.ended_at:
        raise HTTPException(status_code=400, detail="考勤会话已完成")
    
    session.ended_at = datetime.utcnow()
    await db.commit()
    await db.refresh(session)
    
    return {"message": "考勤会话已完成", "ended_at": session.ended_at}


# ==================== 正面行为 ====================


@router.get("/positive-behaviors/types", response_model=List[PositiveBehaviorTypeInfo])
async def get_positive_behavior_types() -> Any:
    """获取正面行为类型列表"""
    return [
        PositiveBehaviorTypeInfo(
            type=PositiveBehaviorType.ACTIVE_RESPONSE,
            name="积极回答",
            points=2,
            description="主动回答问题",
        ),
        PositiveBehaviorTypeInfo(
            type=PositiveBehaviorType.CORRECT_ANSWER,
            name="回答正确",
            points=3,
            description="回答正确或有深度",
        ),
        PositiveBehaviorTypeInfo(
            type=PositiveBehaviorType.HELP_CLASSMATE,
            name="帮助同学",
            points=3,
            description="主动帮助其他同学",
        ),
        PositiveBehaviorTypeInfo(
            type=PositiveBehaviorType.EXCELLENT_HOMEWORK,
            name="优秀作业",
            points=2,
            description="作业完成优秀",
        ),
        PositiveBehaviorTypeInfo(
            type=PositiveBehaviorType.PROACTIVE_THINKING,
            name="主动思考",
            points=2,
            description="主动思考并提出问题",
        ),
        PositiveBehaviorTypeInfo(
            type=PositiveBehaviorType.COLLABORATIVE_WORK,
            name="团队协作",
            points=3,
            description="团队协作表现突出",
        ),
        PositiveBehaviorTypeInfo(
            type=PositiveBehaviorType.OTHER,
            name="其他",
            points=1,
            description="其他正面行为",
        ),
    ]


@router.post(
    "/classrooms/{classroom_id}/positive-behaviors",
    response_model=PositiveBehaviorResponse,
    status_code=201,
)
async def create_positive_behavior(
    classroom_id: int,
    data: PositiveBehaviorCreate,
    db: AsyncSession = Depends(get_db),
    membership: ClassroomMembership = Depends(require_classroom_management_permission),
) -> Any:
    """创建正面行为记录"""
    # 验证学生属于该班级
    student_membership = await db.execute(
        select(ClassroomMembership).where(
            ClassroomMembership.classroom_id == classroom_id,
            ClassroomMembership.user_id == data.student_id,
            ClassroomMembership.is_active == True,
        )
    )
    if not student_membership.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="学生不属于该班级")
    
    # 计算积分
    points = get_behavior_type_points(data.behavior_type)
    
    behavior = PositiveBehavior(
        classroom_id=classroom_id,
        student_id=data.student_id,
        behavior_type=data.behavior_type,
        custom_behavior_text=data.custom_behavior_text,
        points=points,
        note=data.note,
        recorded_by_user_id=membership.user_id,
    )
    db.add(behavior)
    await db.commit()
    await db.refresh(behavior)
    
    return PositiveBehaviorResponse.model_validate(behavior)


@router.get("/classrooms/{classroom_id}/positive-behaviors", response_model=List[PositiveBehaviorResponse])
async def get_positive_behaviors(
    classroom_id: int,
    student_id: Optional[int] = Query(None, description="学生ID筛选"),
    from_date: Optional[datetime] = Query(None, description="开始日期"),
    to_date: Optional[datetime] = Query(None, description="结束日期"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """查询正面行为记录（受可见性控制）"""
    # 权限检查
    membership_result = await db.execute(
        select(ClassroomMembership).where(
            ClassroomMembership.user_id == current_user.id,
            ClassroomMembership.classroom_id == classroom_id,
            ClassroomMembership.is_active == True,
        )
    )
    membership = membership_result.scalar_one_or_none()
    
    if not membership:
        raise HTTPException(status_code=403, detail="您不是该班级的成员")
    
    # 判断是否是管理角色
    is_management = membership.role_in_class in [
        RoleInClass.HEAD_TEACHER_PRIMARY,
        RoleInClass.HEAD_TEACHER_DEPUTY,
        RoleInClass.SUBJECT_TEACHER,
        RoleInClass.CADRE,
    ]
    
    # 检查可见性设置
    classroom = await db.get(Classroom, classroom_id)
    settings = classroom.settings or {} if classroom else {}
    show_publicly = settings.get("show_positive_behaviors_publicly", False)
    
    # 构建查询
    query = select(PositiveBehavior).where(PositiveBehavior.classroom_id == classroom_id)
    
    # 如果学生查询且未公开，只返回本人记录
    if not is_management and not show_publicly:
        query = query.where(PositiveBehavior.student_id == current_user.id)
    elif student_id:
        query = query.where(PositiveBehavior.student_id == student_id)
    
    # 时间范围筛选
    if from_date:
        query = query.where(PositiveBehavior.recorded_at >= from_date)
    if to_date:
        query = query.where(PositiveBehavior.recorded_at <= to_date)
    
    query = query.order_by(desc(PositiveBehavior.recorded_at))
    
    result = await db.execute(query)
    behaviors = result.scalars().all()
    
    return [PositiveBehaviorResponse.model_validate(b) for b in behaviors]


@router.get(
    "/classrooms/{classroom_id}/positive-behaviors/leaderboard",
    response_model=List[PositiveBehaviorLeaderboardEntry],
)
async def get_positive_behavior_leaderboard(
    classroom_id: int,
    from_date: Optional[datetime] = Query(None, description="开始日期"),
    to_date: Optional[datetime] = Query(None, description="结束日期"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """获取积分榜（受可见性控制）"""
    # 权限检查
    membership_result = await db.execute(
        select(ClassroomMembership).where(
            ClassroomMembership.user_id == current_user.id,
            ClassroomMembership.classroom_id == classroom_id,
            ClassroomMembership.is_active == True,
        )
    )
    membership = membership_result.scalar_one_or_none()
    
    if not membership:
        raise HTTPException(status_code=403, detail="您不是该班级的成员")
    
    # 判断是否是管理角色
    is_management = membership.role_in_class in [
        RoleInClass.HEAD_TEACHER_PRIMARY,
        RoleInClass.HEAD_TEACHER_DEPUTY,
        RoleInClass.SUBJECT_TEACHER,
        RoleInClass.CADRE,
    ]
    
    # 检查可见性设置
    classroom = await db.get(Classroom, classroom_id)
    settings = classroom.settings or {} if classroom else {}
    show_publicly = settings.get("show_positive_behaviors_publicly", False)
    
    # 如果学生查询且未公开，只返回本人
    if not is_management and not show_publicly:
        # 只返回当前用户的统计
        query = select(
            PositiveBehavior.student_id,
            func.sum(PositiveBehavior.points).label("total_points"),
            func.count(PositiveBehavior.id).label("record_count"),
        ).where(
            PositiveBehavior.classroom_id == classroom_id,
            PositiveBehavior.student_id == current_user.id,
        )
    else:
        # 返回全班统计
        query = select(
            PositiveBehavior.student_id,
            func.sum(PositiveBehavior.points).label("total_points"),
            func.count(PositiveBehavior.id).label("record_count"),
        ).where(PositiveBehavior.classroom_id == classroom_id)
    
    # 时间范围筛选
    if from_date:
        query = query.where(PositiveBehavior.recorded_at >= from_date)
    if to_date:
        query = query.where(PositiveBehavior.recorded_at <= to_date)
    
    query = query.group_by(PositiveBehavior.student_id).order_by(desc("total_points"))
    
    result = await db.execute(query)
    rows = result.all()
    
    # 加载用户信息
    leaderboard = []
    for row in rows:
        user = await db.get(User, row.student_id)
        if user:
            leaderboard.append(PositiveBehaviorLeaderboardEntry(
                student_id=user.id,
                student_name=user.full_name or user.username,
                total_points=int(row.total_points) if row.total_points else 0,
                record_count=int(row.record_count) if row.record_count else 0,
            ))
    
    return leaderboard


@router.get("/users/me/positive-behaviors", response_model=List[PositiveBehaviorResponse])
async def get_my_positive_behaviors(
    from_date: Optional[datetime] = Query(None, description="开始日期"),
    to_date: Optional[datetime] = Query(None, description="结束日期"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """学生查看本人的正面行为记录"""
    query = select(PositiveBehavior).where(PositiveBehavior.student_id == current_user.id)
    
    if from_date:
        query = query.where(PositiveBehavior.recorded_at >= from_date)
    if to_date:
        query = query.where(PositiveBehavior.recorded_at <= to_date)
    
    query = query.order_by(desc(PositiveBehavior.recorded_at))
    
    result = await db.execute(query)
    behaviors = result.scalars().all()
    
    return [PositiveBehaviorResponse.model_validate(b) for b in behaviors]


# ==================== 纪律记录 ====================


@router.get("/discipline/event-types", response_model=List[DisciplineEventTypeInfo])
async def get_discipline_event_types() -> Any:
    """获取纪律事件类型列表"""
    return [
        # 课堂行为类
        DisciplineEventTypeInfo(type=DisciplineEventType.TALKING, name="上课讲话", category="课堂行为类"),
        DisciplineEventTypeInfo(type=DisciplineEventType.WALKING, name="上课走动", category="课堂行为类"),
        DisciplineEventTypeInfo(type=DisciplineEventType.NOT_PARTICIPATING, name="未按要求参与活动", category="课堂行为类"),
        DisciplineEventTypeInfo(type=DisciplineEventType.SLEEPING, name="上课睡觉", category="课堂行为类"),
        DisciplineEventTypeInfo(type=DisciplineEventType.DISTRACTED, name="注意力分散", category="课堂行为类"),
        # 课堂秩序类
        DisciplineEventTypeInfo(type=DisciplineEventType.INTERRUPTING, name="随意插话", category="课堂秩序类"),
        DisciplineEventTypeInfo(type=DisciplineEventType.DISTURBING_OTHERS, name="影响他人学习", category="课堂秩序类"),
        DisciplineEventTypeInfo(type=DisciplineEventType.NOT_FOLLOWING_INSTRUCTIONS, name="未按指令行动", category="课堂秩序类"),
        # 作业与学习准备类
        DisciplineEventTypeInfo(type=DisciplineEventType.MISSING_MATERIALS, name="未携带学习用品", category="作业与学习准备类"),
        DisciplineEventTypeInfo(type=DisciplineEventType.HOMEWORK_INCOMPLETE, name="未完成作业", category="作业与学习准备类"),
        DisciplineEventTypeInfo(type=DisciplineEventType.HOMEWORK_NOT_AS_REQUIRED, name="作业未按要求完成", category="作业与学习准备类"),
        # 课间与公共区域行为
        DisciplineEventTypeInfo(type=DisciplineEventType.HALLWAY_ROUGHHOUSING, name="下课走廊打闹", category="课间与公共区域行为"),
        DisciplineEventTypeInfo(type=DisciplineEventType.RUNNING_IN_HALLWAY, name="课间追逐奔跑", category="课间与公共区域行为"),
        DisciplineEventTypeInfo(type=DisciplineEventType.LOUD_NOISE, name="大声喧哗", category="课间与公共区域行为"),
        # 其他
        DisciplineEventTypeInfo(type=DisciplineEventType.OTHER, name="其他", category="其他"),
    ]


@router.post(
    "/classrooms/{classroom_id}/discipline/records",
    response_model=DisciplineRecordResponse,
    status_code=201,
)
async def create_discipline_record(
    classroom_id: int,
    data: DisciplineRecordCreate,
    db: AsyncSession = Depends(get_db),
    membership: ClassroomMembership = Depends(require_classroom_management_permission),
) -> Any:
    """创建纪律记录"""
    # 验证学生属于该班级
    student_membership = await db.execute(
        select(ClassroomMembership).where(
            ClassroomMembership.classroom_id == classroom_id,
            ClassroomMembership.user_id == data.student_id,
            ClassroomMembership.is_active == True,
        )
    )
    if not student_membership.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="学生不属于该班级")
    
    record = DisciplineRecord(
        classroom_id=classroom_id,
        student_id=data.student_id,
        event_type=data.event_type,
        custom_event_text=data.custom_event_text,
        note=data.note,
        recorded_by_user_id=membership.user_id,
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)
    
    return DisciplineRecordResponse.model_validate(record)


@router.get("/classrooms/{classroom_id}/discipline/records", response_model=List[DisciplineRecordResponse])
async def get_discipline_records(
    classroom_id: int,
    student_id: Optional[int] = Query(None, description="学生ID筛选"),
    from_date: Optional[datetime] = Query(None, description="开始日期"),
    to_date: Optional[datetime] = Query(None, description="结束日期"),
    db: AsyncSession = Depends(get_db),
    membership: ClassroomMembership = Depends(require_classroom_member),
) -> Any:
    """查询纪律记录"""
    # 判断是否是管理角色
    is_management = membership.role_in_class in [
        RoleInClass.HEAD_TEACHER_PRIMARY,
        RoleInClass.HEAD_TEACHER_DEPUTY,
        RoleInClass.SUBJECT_TEACHER,
        RoleInClass.CADRE,
    ]
    
    # 构建查询
    query = select(DisciplineRecord).where(DisciplineRecord.classroom_id == classroom_id)
    
    # 学生只能查看本人记录
    if not is_management:
        query = query.where(DisciplineRecord.student_id == membership.user_id)
    elif student_id:
        query = query.where(DisciplineRecord.student_id == student_id)
    
    # 时间范围筛选
    if from_date:
        query = query.where(DisciplineRecord.recorded_at >= from_date)
    if to_date:
        query = query.where(DisciplineRecord.recorded_at <= to_date)
    
    query = query.order_by(desc(DisciplineRecord.recorded_at))
    
    result = await db.execute(query)
    records = result.scalars().all()
    
    return [DisciplineRecordResponse.model_validate(r) for r in records]


# ==================== 值日 ====================


@router.post(
    "/classrooms/{classroom_id}/duty/rules",
    response_model=DutyRuleResponse,
    status_code=201,
)
async def create_duty_rule(
    classroom_id: int,
    data: DutyRuleCreate,
    db: AsyncSession = Depends(get_db),
    membership: ClassroomMembership = Depends(require_classroom_duty_setting_permission),
) -> Any:
    """创建值日规则"""
    # 验证所有学生都属于该班级
    for user_id in data.member_user_ids:
        student_membership = await db.execute(
            select(ClassroomMembership).where(
                ClassroomMembership.classroom_id == classroom_id,
                ClassroomMembership.user_id == user_id,
                ClassroomMembership.is_active == True,
            )
        )
        if not student_membership.scalar_one_or_none():
            raise HTTPException(status_code=400, detail=f"用户 {user_id} 不属于该班级")
    
    rule = DutyRule(
        classroom_id=classroom_id,
        rotation_type=data.rotation_type,
        start_date=data.start_date,
        member_user_ids=data.member_user_ids,
        group_size=data.group_size,
    )
    db.add(rule)
    await db.commit()
    await db.refresh(rule)
    
    return DutyRuleResponse.model_validate(rule)


@router.post("/classrooms/{classroom_id}/duty/generate")
async def generate_duty_assignments(
    classroom_id: int,
    data: DutyGenerateRequest,
    db: AsyncSession = Depends(get_db),
    membership: ClassroomMembership = Depends(require_classroom_duty_setting_permission),
) -> Any:
    """生成值日任务"""
    # 获取最新的规则
    rule_result = await db.execute(
        select(DutyRule)
        .where(DutyRule.classroom_id == classroom_id)
        .order_by(desc(DutyRule.created_at))
        .limit(1)
    )
    rule = rule_result.scalar_one_or_none()
    
    if not rule:
        raise HTTPException(status_code=404, detail="请先创建值日规则")
    
    # 计算生成日期范围
    start_date = rule.start_date
    if rule.rotation_type == DutyRotationType.DAILY:
        end_date = start_date + timedelta(days=data.days)
    else:  # WEEKLY
        end_date = start_date + timedelta(weeks=data.weeks)
    
    # 生成任务
    member_ids = rule.member_user_ids
    group_size = rule.group_size
    current_index = 0
    assignments = []
    current_date = start_date
    
    while current_date < end_date:
        # 为这一天生成 group_size 个任务
        for _ in range(group_size):
            if current_index >= len(member_ids):
                current_index = 0
            
            assignee_id = member_ids[current_index]
            
            # 检查是否已存在
            existing = await db.execute(
                select(DutyAssignment).where(
                    DutyAssignment.classroom_id == classroom_id,
                    DutyAssignment.duty_date == current_date,
                    DutyAssignment.assignee_user_id == assignee_id,
                )
            )
            if not existing.scalar_one_or_none():
                assignment = DutyAssignment(
                    classroom_id=classroom_id,
                    rule_id=rule.id,
                    duty_date=current_date,
                    assignee_user_id=assignee_id,
                    status=DutyAssignmentStatus.PENDING,
                )
                assignments.append(assignment)
            
            current_index += 1
        
        # 移动到下一天/周
        if rule.rotation_type == DutyRotationType.DAILY:
            current_date += timedelta(days=1)
        else:
            current_date += timedelta(weeks=1)
    
    if assignments:
        db.add_all(assignments)
        await db.commit()
    
    return {"message": f"已生成 {len(assignments)} 个值日任务"}


@router.get("/classrooms/{classroom_id}/duty/today", response_model=List[DutyAssignmentResponse])
async def get_today_duty(
    classroom_id: int,
    db: AsyncSession = Depends(get_db),
    membership: ClassroomMembership = Depends(require_classroom_member),
) -> Any:
    """获取今日值日任务"""
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    
    result = await db.execute(
        select(DutyAssignment)
        .options(selectinload(DutyAssignment.assignee))
        .where(
            DutyAssignment.classroom_id == classroom_id,
            DutyAssignment.duty_date == today,
        )
        .order_by(asc(DutyAssignment.id))
    )
    assignments = result.scalars().all()
    
    return [DutyAssignmentResponse.model_validate(a) for a in assignments]


@router.patch("/duty/assignments/{assignment_id}", response_model=DutyAssignmentResponse)
async def update_duty_assignment(
    assignment_id: int,
    data: DutyAssignmentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    membership: ClassroomMembership = Depends(require_classroom_member),
) -> Any:
    """更新值日任务状态"""
    assignment = await db.get(DutyAssignment, assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="值日任务不存在")
    
    if assignment.classroom_id != membership.classroom_id:
        raise HTTPException(status_code=403, detail="无权操作该任务")
    
    assignment.status = data.status
    if data.status == DutyAssignmentStatus.COMPLETED:
        assignment.completed_by_user_id = current_user.id
        assignment.completed_at = datetime.utcnow()
    else:
        assignment.completed_by_user_id = None
        assignment.completed_at = None
    
    await db.commit()
    await db.refresh(assignment)
    
    return DutyAssignmentResponse.model_validate(assignment)


# ==================== 统计 ====================


@router.get("/classrooms/{classroom_id}/stats", response_model=ClassroomStatsResponse)
async def get_classroom_stats(
    classroom_id: int,
    from_date: Optional[datetime] = Query(None, description="开始日期"),
    to_date: Optional[datetime] = Query(None, description="结束日期"),
    db: AsyncSession = Depends(get_db),
    membership: ClassroomMembership = Depends(require_classroom_member),
) -> Any:
    """获取班级统计"""
    # 默认时间范围：最近30天
    if not to_date:
        to_date = datetime.utcnow()
    if not from_date:
        from_date = to_date - timedelta(days=30)
    
    # 出勤统计
    attendance_query = select(
        func.count(AttendanceSession.id).label("total_sessions"),
        func.sum(
            func.case((AttendanceEntry.status == AttendanceStatus.PRESENT, 1), else_=0)
        ).label("present_count"),
        func.sum(
            func.case((AttendanceEntry.status == AttendanceStatus.LATE, 1), else_=0)
        ).label("late_count"),
        func.sum(
            func.case((AttendanceEntry.status == AttendanceStatus.LEAVE, 1), else_=0)
        ).label("leave_count"),
        func.sum(
            func.case((AttendanceEntry.status == AttendanceStatus.ABSENT, 1), else_=0)
        ).label("absent_count"),
    ).select_from(
        AttendanceSession.join(AttendanceEntry, AttendanceSession.id == AttendanceEntry.session_id)
    ).where(
        AttendanceSession.classroom_id == classroom_id,
        AttendanceSession.started_at >= from_date,
        AttendanceSession.started_at <= to_date,
    )
    
    attendance_result = await db.execute(attendance_query)
    attendance_row = attendance_result.first()
    
    attendance_stats = None
    if attendance_row and attendance_row.total_sessions:
        total_entries = (
            (attendance_row.present_count or 0)
            + (attendance_row.late_count or 0)
            + (attendance_row.leave_count or 0)
            + (attendance_row.absent_count or 0)
        )
        attendance_rate = (
            (attendance_row.present_count or 0) / total_entries if total_entries > 0 else 0.0
        )
        attendance_stats = AttendanceStats(
            total_sessions=int(attendance_row.total_sessions),
            present_count=int(attendance_row.present_count or 0),
            late_count=int(attendance_row.late_count or 0),
            leave_count=int(attendance_row.leave_count or 0),
            absent_count=int(attendance_row.absent_count or 0),
            attendance_rate=attendance_rate,
        )
    
    # 正面行为统计
    positive_query = select(
        func.sum(PositiveBehavior.points).label("total_points"),
        func.count(PositiveBehavior.id).label("total_records"),
    ).where(
        PositiveBehavior.classroom_id == classroom_id,
        PositiveBehavior.recorded_at >= from_date,
        PositiveBehavior.recorded_at <= to_date,
    )
    
    positive_result = await db.execute(positive_query)
    positive_row = positive_result.first()
    
    positive_stats = None
    if positive_row and positive_row.total_records:
        # 按类型统计积分
        points_by_type_query = select(
            PositiveBehavior.behavior_type,
            func.sum(PositiveBehavior.points).label("points"),
        ).where(
            PositiveBehavior.classroom_id == classroom_id,
            PositiveBehavior.recorded_at >= from_date,
            PositiveBehavior.recorded_at <= to_date,
        ).group_by(PositiveBehavior.behavior_type)
        
        points_by_type_result = await db.execute(points_by_type_query)
        points_by_type = {
            row.behavior_type: int(row.points) for row in points_by_type_result.all()
        }
        positive_stats = PositiveBehaviorStats(
            total_points=int(positive_row.total_points or 0),
            total_records=int(positive_row.total_records),
            points_by_type=points_by_type,
        )
    
    # 纪律统计
    discipline_query = select(
        func.count(DisciplineRecord.id).label("total_records"),
    ).where(
        DisciplineRecord.classroom_id == classroom_id,
        DisciplineRecord.recorded_at >= from_date,
        DisciplineRecord.recorded_at <= to_date,
    )
    
    discipline_result = await db.execute(discipline_query)
    discipline_row = discipline_result.first()
    
    discipline_stats = None
    if discipline_row and discipline_row.total_records:
        # 按类型统计
        records_by_type_query = select(
            DisciplineRecord.event_type,
            func.count(DisciplineRecord.id).label("count"),
        ).where(
            DisciplineRecord.classroom_id == classroom_id,
            DisciplineRecord.recorded_at >= from_date,
            DisciplineRecord.recorded_at <= to_date,
        ).group_by(DisciplineRecord.event_type)
        
        records_by_type_result = await db.execute(records_by_type_query)
        records_by_type = {
            row.event_type: int(row.count) for row in records_by_type_result.all()
        }
        discipline_stats = DisciplineStats(
            total_records=int(discipline_row.total_records),
            records_by_type=records_by_type,
        )
    
    # 值日统计
    duty_query = select(
        func.count(DutyAssignment.id).label("total_assignments"),
        func.sum(
            func.case((DutyAssignment.status == DutyAssignmentStatus.COMPLETED, 1), else_=0)
        ).label("completed_count"),
    ).where(
        DutyAssignment.classroom_id == classroom_id,
        DutyAssignment.duty_date >= from_date,
        DutyAssignment.duty_date <= to_date,
    )
    
    duty_result = await db.execute(duty_query)
    duty_row = duty_result.first()
    
    total_duty = int(duty_row.total_assignments or 0)
    completed_duty = int(duty_row.completed_count or 0)
    duty_completion_rate = completed_duty / total_duty if total_duty > 0 else 0.0
    
    duty_stats = None
    if total_duty:
        duty_stats = DutyStats(
            total_assignments=total_duty,
            completed_count=completed_duty,
            pending_count=total_duty - completed_duty,
            completion_rate=duty_completion_rate,
        )
    
    return ClassroomStatsResponse(
        classroom_id=classroom_id,
        period_start=from_date,
        period_end=to_date,
        attendance=attendance_stats,
        positive_behaviors=positive_stats,
        discipline=discipline_stats,
        duty=duty_stats,
    )


@router.get("/users/me/stats", response_model=StudentStatsResponse)
async def get_my_stats(
    from_date: Optional[datetime] = Query(None, description="开始日期"),
    to_date: Optional[datetime] = Query(None, description="结束日期"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """获取学生本人统计"""
    # 默认时间范围：最近30天
    if not to_date:
        to_date = datetime.utcnow()
    if not from_date:
        from_date = to_date - timedelta(days=30)
    
    # 获取学生所在的班级
    membership_result = await db.execute(
        select(ClassroomMembership).where(
            ClassroomMembership.user_id == current_user.id,
            ClassroomMembership.role_in_class == RoleInClass.STUDENT,
            ClassroomMembership.is_active == True,
        )
    )
    memberships = membership_result.scalars().all()
    
    if not memberships:
        raise HTTPException(status_code=404, detail="您不是任何班级的学生")
    
    # 使用第一个班级（或主班级）
    primary_membership = next(
        (m for m in memberships if m.is_primary_class), memberships[0]
    )
    classroom_id = primary_membership.classroom_id
    
    # 出勤统计
    attendance_query = select(
        func.count(AttendanceSession.id).label("total_sessions"),
        func.sum(
            func.case((AttendanceEntry.status == AttendanceStatus.PRESENT, 1), else_=0)
        ).label("present_count"),
        func.sum(
            func.case((AttendanceEntry.status == AttendanceStatus.LATE, 1), else_=0)
        ).label("late_count"),
        func.sum(
            func.case((AttendanceEntry.status == AttendanceStatus.LEAVE, 1), else_=0)
        ).label("leave_count"),
        func.sum(
            func.case((AttendanceEntry.status == AttendanceStatus.ABSENT, 1), else_=0)
        ).label("absent_count"),
    ).select_from(
        AttendanceSession.join(AttendanceEntry, AttendanceSession.id == AttendanceEntry.session_id)
    ).where(
        AttendanceSession.classroom_id == classroom_id,
        AttendanceEntry.student_id == current_user.id,
        AttendanceSession.started_at >= from_date,
        AttendanceSession.started_at <= to_date,
    )
    
    attendance_result = await db.execute(attendance_query)
    attendance_row = attendance_result.first()
    
    attendance_stats = None
    if attendance_row and attendance_row.total_sessions:
        total_entries = (
            (attendance_row.present_count or 0)
            + (attendance_row.late_count or 0)
            + (attendance_row.leave_count or 0)
            + (attendance_row.absent_count or 0)
        )
        attendance_rate = (
            (attendance_row.present_count or 0) / total_entries if total_entries > 0 else 0.0
        )
        attendance_stats = AttendanceStats(
            total_sessions=int(attendance_row.total_sessions),
            present_count=int(attendance_row.present_count or 0),
            late_count=int(attendance_row.late_count or 0),
            leave_count=int(attendance_row.leave_count or 0),
            absent_count=int(attendance_row.absent_count or 0),
            attendance_rate=attendance_rate,
        )
    
    # 正面行为统计
    positive_query = select(
        func.sum(PositiveBehavior.points).label("total_points"),
        func.count(PositiveBehavior.id).label("total_records"),
    ).where(
        PositiveBehavior.student_id == current_user.id,
        PositiveBehavior.classroom_id == classroom_id,
        PositiveBehavior.recorded_at >= from_date,
        PositiveBehavior.recorded_at <= to_date,
    )
    
    positive_result = await db.execute(positive_query)
    positive_row = positive_result.first()
    
    positive_stats = None
    if positive_row and positive_row.total_records:
        points_by_type_query = select(
            PositiveBehavior.behavior_type,
            func.sum(PositiveBehavior.points).label("points"),
        ).where(
            PositiveBehavior.student_id == current_user.id,
            PositiveBehavior.classroom_id == classroom_id,
            PositiveBehavior.recorded_at >= from_date,
            PositiveBehavior.recorded_at <= to_date,
        ).group_by(PositiveBehavior.behavior_type)
        
        points_by_type_result = await db.execute(points_by_type_query)
        points_by_type = {
            row.behavior_type: int(row.points) for row in points_by_type_result.all()
        }
        positive_stats = PositiveBehaviorStats(
            total_points=int(positive_row.total_points or 0),
            total_records=int(positive_row.total_records),
            points_by_type=points_by_type,
        )
    
    # 纪律统计
    discipline_query = select(
        func.count(DisciplineRecord.id).label("total_records"),
    ).where(
        DisciplineRecord.student_id == current_user.id,
        DisciplineRecord.classroom_id == classroom_id,
        DisciplineRecord.recorded_at >= from_date,
        DisciplineRecord.recorded_at <= to_date,
    )
    
    discipline_result = await db.execute(discipline_query)
    discipline_row = discipline_result.first()
    
    discipline_stats = None
    if discipline_row and discipline_row.total_records:
        records_by_type_query = select(
            DisciplineRecord.event_type,
            func.count(DisciplineRecord.id).label("count"),
        ).where(
            DisciplineRecord.student_id == current_user.id,
            DisciplineRecord.classroom_id == classroom_id,
            DisciplineRecord.recorded_at >= from_date,
            DisciplineRecord.recorded_at <= to_date,
        ).group_by(DisciplineRecord.event_type)
        
        records_by_type_result = await db.execute(records_by_type_query)
        records_by_type = {
            row.event_type: int(row.count) for row in records_by_type_result.all()
        }
        discipline_stats = DisciplineStats(
            total_records=int(discipline_row.total_records),
            records_by_type=records_by_type,
        )
    
    # 值日统计
    duty_query = select(
        func.count(DutyAssignment.id).label("total_assignments"),
        func.sum(
            func.case((DutyAssignment.status == DutyAssignmentStatus.COMPLETED, 1), else_=0)
        ).label("completed_count"),
    ).where(
        DutyAssignment.assignee_user_id == current_user.id,
        DutyAssignment.classroom_id == classroom_id,
        DutyAssignment.duty_date >= from_date,
        DutyAssignment.duty_date <= to_date,
    )
    
    duty_result = await db.execute(duty_query)
    duty_row = duty_result.first()
    
    total_duty = int(duty_row.total_assignments or 0)
    completed_duty = int(duty_row.completed_count or 0)
    duty_completion_rate = completed_duty / total_duty if total_duty > 0 else 0.0
    
    duty_stats = None
    if total_duty:
        duty_stats = DutyStats(
            total_assignments=total_duty,
            completed_count=completed_duty,
            pending_count=total_duty - completed_duty,
            completion_rate=duty_completion_rate,
        )
    
    return StudentStatsResponse(
        student_id=current_user.id,
        period_start=from_date,
        period_end=to_date,
        attendance=attendance_stats,
        positive_behaviors=positive_stats,
        discipline=discipline_stats,
        duty=duty_stats,
    )
