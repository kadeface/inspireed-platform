"""
学科教研组API接口
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models import (
    User,
    SubjectGroup,
    GroupMembership,
    SharedLesson,
    Lesson,
    Subject,
    Grade,
    School,
    Region,
    MemberRole,
    GroupScope,
)
from app.schemas.subject_group import (
    SubjectGroupCreate,
    SubjectGroupUpdate,
    SubjectGroupResponse,
    SubjectGroupListResponse,
    GroupMembershipCreate,
    GroupMembershipUpdate,
    GroupMembershipResponse,
    GroupMembershipListResponse,
    SharedLessonCreate,
    SharedLessonUpdate,
    SharedLessonResponse,
    SharedLessonListResponse,
    SubjectGroupStatistics,
)
from app.api.deps import get_current_user, get_current_teacher

router = APIRouter()


# ==================== 教研组管理 ====================


@router.post("/", response_model=SubjectGroupResponse)
async def create_subject_group(
    group_data: SubjectGroupCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_teacher),
) -> SubjectGroupResponse:
    """创建教研组（仅教师可用）"""

    # 验证学科是否存在
    subject = await db.get(Subject, group_data.subject_id)
    if not subject:
        raise HTTPException(status_code=404, detail="学科不存在")

    # 验证范围相关的ID
    if group_data.scope == GroupScope.SCHOOL:
        if not group_data.school_id:
            raise HTTPException(status_code=400, detail="校级教研组必须指定学校")
        school = await db.get(School, group_data.school_id)
        if not school:
            raise HTTPException(status_code=404, detail="学校不存在")
    elif group_data.scope == GroupScope.REGION:
        if not group_data.region_id:
            raise HTTPException(status_code=400, detail="区域级教研组必须指定区域")
        region = await db.get(Region, group_data.region_id)
        if not region:
            raise HTTPException(status_code=404, detail="区域不存在")

    # 创建教研组
    group = SubjectGroup(
        **group_data.model_dump(),
        creator_id=current_user.id,
        member_count=1,  # 创建者自动成为成员
    )
    db.add(group)
    await db.flush()

    # 创建创建者的成员关系（作为组长）
    membership = GroupMembership(group_id=group.id, user_id=current_user.id, role=MemberRole.OWNER)
    db.add(membership)

    await db.commit()
    await db.refresh(group)

    # 构建响应
    response = SubjectGroupResponse.model_validate(group)
    response.subject_name = subject.name
    response.creator_name = current_user.full_name or current_user.username
    response.user_role = MemberRole.OWNER

    if group.grade_id:
        grade = await db.get(Grade, group.grade_id)
        response.grade_name = grade.name if grade else None
    if group.school_id:
        school = await db.get(School, group.school_id)
        response.school_name = school.name if school else None
    if group.region_id:
        region = await db.get(Region, group.region_id)
        response.region_name = region.name if region else None

    return response


@router.get("/", response_model=SubjectGroupListResponse)
async def list_subject_groups(
    subject_id: Optional[int] = Query(None, description="学科ID"),
    grade_id: Optional[int] = Query(None, description="年级ID"),
    scope: Optional[GroupScope] = Query(None, description="教研组范围"),
    school_id: Optional[int] = Query(None, description="学校ID"),
    region_id: Optional[int] = Query(None, description="区域ID"),
    is_public: Optional[bool] = Query(None, description="是否公开"),
    my_groups: bool = Query(False, description="仅显示我的教研组"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SubjectGroupListResponse:
    """获取教研组列表"""

    # 构建查询
    query = select(SubjectGroup).where(SubjectGroup.is_active == True)

    # 应用过滤条件
    if subject_id:
        query = query.where(SubjectGroup.subject_id == subject_id)
    if grade_id:
        query = query.where(SubjectGroup.grade_id == grade_id)
    if scope:
        query = query.where(SubjectGroup.scope == scope)
    if school_id:
        query = query.where(SubjectGroup.school_id == school_id)
    if region_id:
        query = query.where(SubjectGroup.region_id == region_id)
    if is_public is not None:
        query = query.where(SubjectGroup.is_public == is_public)

    if my_groups:
        # 查询用户是成员的教研组
        membership_subquery = (
            select(GroupMembership.group_id)
            .where(GroupMembership.user_id == current_user.id)
            .where(GroupMembership.is_active == True)
        )
        query = query.where(SubjectGroup.id.in_(membership_subquery))

    # 计算总数
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)

    # 分页
    query = query.offset((page - 1) * page_size).limit(page_size)
    query = query.order_by(SubjectGroup.created_at.desc())

    # 执行查询
    result = await db.execute(query)
    groups = result.scalars().all()

    # 获取用户在这些组的角色
    user_roles = {}
    if groups:
        group_ids = [g.id for g in groups]
        membership_query = select(GroupMembership).where(
            and_(
                GroupMembership.group_id.in_(group_ids),
                GroupMembership.user_id == current_user.id,
                GroupMembership.is_active == True,
            )
        )
        memberships = await db.execute(membership_query)
        for membership in memberships.scalars():
            user_roles[membership.group_id] = membership.role

    # 获取关联信息
    subject_ids = list(set(g.subject_id for g in groups))
    subjects = {}
    if subject_ids:
        subject_result = await db.execute(select(Subject).where(Subject.id.in_(subject_ids)))
        subjects = {s.id: s for s in subject_result.scalars()}

    grade_ids = list(set(g.grade_id for g in groups if g.grade_id))
    grades = {}
    if grade_ids:
        grade_result = await db.execute(select(Grade).where(Grade.id.in_(grade_ids)))
        grades = {g.id: g for g in grade_result.scalars()}

    # 构建响应
    items = []
    for group in groups:
        response = SubjectGroupResponse.model_validate(group)
        response.subject_name = (
            subjects[group.subject_id].name if group.subject_id in subjects else None
        )
        response.grade_name = (
            grades[group.grade_id].name if group.grade_id and group.grade_id in grades else None
        )
        response.user_role = user_roles.get(group.id)
        items.append(response)

    return SubjectGroupListResponse(items=items, total=total, page=page, page_size=page_size)


@router.get("/{group_id}", response_model=SubjectGroupResponse)
async def get_subject_group(
    group_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SubjectGroupResponse:
    """获取教研组详情"""

    group = await db.get(SubjectGroup, group_id)
    if not group or not group.is_active:
        raise HTTPException(status_code=404, detail="教研组不存在")

    # 检查用户是否是成员（如果不是公开组）
    if not group.is_public:
        membership = await db.scalar(
            select(GroupMembership).where(
                and_(
                    GroupMembership.group_id == group_id,
                    GroupMembership.user_id == current_user.id,
                    GroupMembership.is_active == True,
                )
            )
        )
        if not membership:
            raise HTTPException(status_code=403, detail="无权访问此教研组")

    # 获取用户角色
    user_role = None
    membership = await db.scalar(
        select(GroupMembership).where(
            and_(
                GroupMembership.group_id == group_id,
                GroupMembership.user_id == current_user.id,
                GroupMembership.is_active == True,
            )
        )
    )
    if membership:
        user_role = membership.role

    # 获取关联信息
    subject = await db.get(Subject, group.subject_id)
    creator = await db.get(User, group.creator_id)
    grade = await db.get(Grade, group.grade_id) if group.grade_id else None

    response = SubjectGroupResponse.model_validate(group)
    response.subject_name = subject.name if subject else None
    response.grade_name = grade.name if grade else None
    response.creator_name = creator.full_name or creator.username if creator else None
    response.user_role = user_role

    if group.school_id:
        school = await db.get(School, group.school_id)
        response.school_name = school.name if school else None
    if group.region_id:
        region = await db.get(Region, group.region_id)
        response.region_name = region.name if region else None

    return response


@router.put("/{group_id}", response_model=SubjectGroupResponse)
async def update_subject_group(
    group_id: int,
    group_data: SubjectGroupUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_teacher),
) -> SubjectGroupResponse:
    """更新教研组（仅组长和管理员可用）"""

    group = await db.get(SubjectGroup, group_id)
    if not group or not group.is_active:
        raise HTTPException(status_code=404, detail="教研组不存在")

    # 检查权限
    membership = await db.scalar(
        select(GroupMembership).where(
            and_(
                GroupMembership.group_id == group_id,
                GroupMembership.user_id == current_user.id,
                GroupMembership.is_active == True,
            )
        )
    )
    if not membership or membership.role not in [MemberRole.OWNER, MemberRole.ADMIN]:
        raise HTTPException(status_code=403, detail="无权限修改此教研组")

    # 更新数据
    update_data = group_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(group, key, value)

    await db.commit()
    await db.refresh(group)

    # 构建响应
    response = SubjectGroupResponse.model_validate(group)
    response.user_role = membership.role

    subject = await db.get(Subject, group.subject_id)
    response.subject_name = subject.name if subject else None

    return response


@router.delete("/{group_id}")
async def delete_subject_group(
    group_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_teacher),
) -> dict:
    """删除教研组（仅组长可用）"""

    group = await db.get(SubjectGroup, group_id)
    if not group or not group.is_active:
        raise HTTPException(status_code=404, detail="教研组不存在")

    # 检查权限（仅组长可删除）
    membership = await db.scalar(
        select(GroupMembership).where(
            and_(
                GroupMembership.group_id == group_id,
                GroupMembership.user_id == current_user.id,
                GroupMembership.is_active == True,
            )
        )
    )
    if not membership or membership.role != MemberRole.OWNER:
        raise HTTPException(status_code=403, detail="仅组长可删除教研组")

    # 软删除
    group.is_active = False
    await db.commit()

    return {"message": "教研组已删除"}


# ==================== 成员管理 ====================


@router.get("/{group_id}/members", response_model=GroupMembershipListResponse)
async def list_group_members(
    group_id: int,
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> GroupMembershipListResponse:
    """获取教研组成员列表"""

    # 检查教研组是否存在
    group = await db.get(SubjectGroup, group_id)
    if not group or not group.is_active:
        raise HTTPException(status_code=404, detail="教研组不存在")

    # 检查用户是否是成员
    user_membership = await db.scalar(
        select(GroupMembership).where(
            and_(
                GroupMembership.group_id == group_id,
                GroupMembership.user_id == current_user.id,
                GroupMembership.is_active == True,
            )
        )
    )
    if not user_membership and not group.is_public:
        raise HTTPException(status_code=403, detail="无权访问此教研组成员列表")

    # 查询成员
    query = select(GroupMembership).where(
        and_(GroupMembership.group_id == group_id, GroupMembership.is_active == True)
    )

    # 计算总数
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)

    # 分页
    query = query.offset((page - 1) * page_size).limit(page_size)
    query = query.order_by(GroupMembership.joined_at.asc())

    # 执行查询
    result = await db.execute(query)
    memberships = result.scalars().all()

    # 获取用户信息
    user_ids = [m.user_id for m in memberships]
    users = {}
    if user_ids:
        user_result = await db.execute(select(User).where(User.id.in_(user_ids)))
        users = {u.id: u for u in user_result.scalars()}

    # 构建响应
    items = []
    for membership in memberships:
        response = GroupMembershipResponse.model_validate(membership)
        user = users.get(membership.user_id)
        if user:
            response.user_name = user.full_name or user.username
            response.user_email = user.email
            response.user_avatar_url = user.avatar_url
        items.append(response)

    return GroupMembershipListResponse(items=items, total=total, page=page, page_size=page_size)


@router.post("/{group_id}/members", response_model=GroupMembershipResponse)
async def add_group_member(
    group_id: int,
    member_data: GroupMembershipCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_teacher),
) -> GroupMembershipResponse:
    """添加教研组成员（仅组长和管理员可用）"""

    # 检查教研组是否存在
    group = await db.get(SubjectGroup, group_id)
    if not group or not group.is_active:
        raise HTTPException(status_code=404, detail="教研组不存在")

    # 检查权限
    user_membership = await db.scalar(
        select(GroupMembership).where(
            and_(
                GroupMembership.group_id == group_id,
                GroupMembership.user_id == current_user.id,
                GroupMembership.is_active == True,
            )
        )
    )
    if not user_membership or user_membership.role not in [
        MemberRole.OWNER,
        MemberRole.ADMIN,
    ]:
        raise HTTPException(status_code=403, detail="无权限添加成员")

    # 检查被添加用户是否存在
    new_user = await db.get(User, member_data.user_id)
    if not new_user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 检查是否已经是成员
    existing = await db.scalar(
        select(GroupMembership).where(
            and_(
                GroupMembership.group_id == group_id,
                GroupMembership.user_id == member_data.user_id,
            )
        )
    )
    if existing:
        if existing.is_active:
            raise HTTPException(status_code=400, detail="用户已是教研组成员")
        else:
            # 重新激活
            existing.is_active = True
            existing.role = member_data.role
            await db.commit()
            await db.refresh(existing)
            membership = existing
    else:
        # 创建新成员关系
        membership = GroupMembership(
            group_id=group_id, user_id=member_data.user_id, role=member_data.role
        )
        db.add(membership)

        # 更新教研组成员数
        group.member_count += 1

        await db.commit()
        await db.refresh(membership)

    # 构建响应
    response = GroupMembershipResponse.model_validate(membership)
    response.user_name = new_user.full_name or new_user.username
    response.user_email = new_user.email
    response.user_avatar_url = new_user.avatar_url

    return response


@router.put("/{group_id}/members/{user_id}", response_model=GroupMembershipResponse)
async def update_group_member(
    group_id: int,
    user_id: int,
    member_data: GroupMembershipUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_teacher),
) -> GroupMembershipResponse:
    """更新教研组成员（仅组长和管理员可用）"""

    # 检查教研组是否存在
    group = await db.get(SubjectGroup, group_id)
    if not group or not group.is_active:
        raise HTTPException(status_code=404, detail="教研组不存在")

    # 检查权限
    user_membership = await db.scalar(
        select(GroupMembership).where(
            and_(
                GroupMembership.group_id == group_id,
                GroupMembership.user_id == current_user.id,
                GroupMembership.is_active == True,
            )
        )
    )
    if not user_membership or user_membership.role not in [
        MemberRole.OWNER,
        MemberRole.ADMIN,
    ]:
        raise HTTPException(status_code=403, detail="无权限修改成员")

    # 查找要修改的成员
    target_membership = await db.scalar(
        select(GroupMembership).where(
            and_(
                GroupMembership.group_id == group_id,
                GroupMembership.user_id == user_id,
            )
        )
    )
    if not target_membership:
        raise HTTPException(status_code=404, detail="成员不存在")

    # 不能修改组长
    if target_membership.role == MemberRole.OWNER:
        raise HTTPException(status_code=403, detail="不能修改组长角色")

    # 更新数据
    update_data = member_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(target_membership, key, value)

    await db.commit()
    await db.refresh(target_membership)

    # 构建响应
    user = await db.get(User, user_id)
    response = GroupMembershipResponse.model_validate(target_membership)
    if user:
        response.user_name = user.full_name or user.username
        response.user_email = user.email
        response.user_avatar_url = user.avatar_url

    return response


@router.delete("/{group_id}/members/{user_id}")
async def remove_group_member(
    group_id: int,
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_teacher),
) -> dict:
    """移除教研组成员（组长和管理员可移除普通成员，用户可自己退出）"""

    # 检查教研组是否存在
    group = await db.get(SubjectGroup, group_id)
    if not group or not group.is_active:
        raise HTTPException(status_code=404, detail="教研组不存在")

    # 查找要移除的成员
    target_membership = await db.scalar(
        select(GroupMembership).where(
            and_(
                GroupMembership.group_id == group_id,
                GroupMembership.user_id == user_id,
                GroupMembership.is_active == True,
            )
        )
    )
    if not target_membership:
        raise HTTPException(status_code=404, detail="成员不存在")

    # 不能移除组长
    if target_membership.role == MemberRole.OWNER:
        raise HTTPException(status_code=403, detail="不能移除组长")

    # 检查权限：用户自己可以退出，或者组长/管理员可以移除其他成员
    if user_id != current_user.id:
        user_membership = await db.scalar(
            select(GroupMembership).where(
                and_(
                    GroupMembership.group_id == group_id,
                    GroupMembership.user_id == current_user.id,
                    GroupMembership.is_active == True,
                )
            )
        )
        if not user_membership or user_membership.role not in [
            MemberRole.OWNER,
            MemberRole.ADMIN,
        ]:
            raise HTTPException(status_code=403, detail="无权限移除成员")

    # 软删除成员关系
    target_membership.is_active = False

    # 更新教研组成员数
    group.member_count = max(0, group.member_count - 1)

    await db.commit()

    return {"message": "成员已移除"}


# ==================== 教学设计共享 ====================


@router.get("/{group_id}/lessons", response_model=SharedLessonListResponse)
async def list_shared_lessons(
    group_id: int,
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SharedLessonListResponse:
    """获取教研组共享教学设计列表"""

    # 检查教研组是否存在
    group = await db.get(SubjectGroup, group_id)
    if not group or not group.is_active:
        raise HTTPException(status_code=404, detail="教研组不存在")

    # 检查用户是否是成员
    user_membership = await db.scalar(
        select(GroupMembership).where(
            and_(
                GroupMembership.group_id == group_id,
                GroupMembership.user_id == current_user.id,
                GroupMembership.is_active == True,
            )
        )
    )
    if not user_membership and not group.is_public:
        raise HTTPException(status_code=403, detail="无权访问此教研组的共享教学设计")

    # 查询共享教学设计
    query = select(SharedLesson).where(
        and_(SharedLesson.group_id == group_id, SharedLesson.is_active == True)
    )

    # 计算总数
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)

    # 分页
    query = query.offset((page - 1) * page_size).limit(page_size)
    query = query.order_by(SharedLesson.shared_at.desc())

    # 执行查询
    result = await db.execute(query)
    shared_lessons = result.scalars().all()

    # 获取关联信息
    lesson_ids = [sl.lesson_id for sl in shared_lessons]
    lessons = {}
    if lesson_ids:
        lesson_result = await db.execute(select(Lesson).where(Lesson.id.in_(lesson_ids)))
        lessons = {lesson.id: lesson for lesson in lesson_result.scalars()}

    sharer_ids = [sl.sharer_id for sl in shared_lessons]
    sharers = {}
    if sharer_ids:
        sharer_result = await db.execute(select(User).where(User.id.in_(sharer_ids)))
        sharers = {u.id: u for u in sharer_result.scalars()}

    # 构建响应
    items = []
    for shared_lesson in shared_lessons:
        response = SharedLessonResponse.model_validate(shared_lesson)

        lesson = lessons.get(shared_lesson.lesson_id)
        if lesson:
            response.lesson_title = lesson.title
            response.lesson_description = lesson.description
            response.lesson_cover_image_url = lesson.cover_image_url
            response.lesson_cell_count = lesson.cell_count
            response.lesson_estimated_duration = lesson.estimated_duration

        sharer = sharers.get(shared_lesson.sharer_id)
        if sharer:
            response.sharer_name = sharer.full_name or sharer.username
            response.sharer_avatar_url = sharer.avatar_url

        response.group_name = group.name
        items.append(response)

    return SharedLessonListResponse(items=items, total=total, page=page, page_size=page_size)


@router.post("/{group_id}/lessons", response_model=SharedLessonResponse)
async def share_lesson_to_group(
    group_id: int,
    lesson_data: SharedLessonCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_teacher),
) -> SharedLessonResponse:
    """分享教学设计到教研组（仅教研组成员可用）"""

    # 检查教研组是否存在
    group = await db.get(SubjectGroup, group_id)
    if not group or not group.is_active:
        raise HTTPException(status_code=404, detail="教研组不存在")

    # 检查用户是否是成员
    user_membership = await db.scalar(
        select(GroupMembership).where(
            and_(
                GroupMembership.group_id == group_id,
                GroupMembership.user_id == current_user.id,
                GroupMembership.is_active == True,
            )
        )
    )
    if not user_membership:
        raise HTTPException(status_code=403, detail="仅教研组成员可分享教学设计")

    # 检查教学设计是否存在且属于当前用户
    lesson = await db.get(Lesson, lesson_data.lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="教学设计不存在")
    if lesson.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="只能分享自己的教学设计")

    # 检查是否已经分享过
    existing = await db.scalar(
        select(SharedLesson).where(
            and_(
                SharedLesson.group_id == group_id,
                SharedLesson.lesson_id == lesson_data.lesson_id,
            )
        )
    )
    if existing:
        if existing.is_active:
            raise HTTPException(status_code=400, detail="该教学设计已分享到此教研组")
        else:
            # 重新激活
            existing.is_active = True
            existing.share_note = lesson_data.share_note
            await db.commit()
            await db.refresh(existing)
            shared_lesson = existing
    else:
        # 创建共享记录
        shared_lesson = SharedLesson(
            group_id=group_id,
            lesson_id=lesson_data.lesson_id,
            sharer_id=current_user.id,
            share_note=lesson_data.share_note,
        )
        db.add(shared_lesson)

        # 更新教研组共享教案数
        group.lesson_count += 1

        await db.commit()
        await db.refresh(shared_lesson)

    # 构建响应
    response = SharedLessonResponse.model_validate(shared_lesson)
    response.lesson_title = lesson.title
    response.lesson_description = lesson.description
    response.lesson_cover_image_url = lesson.cover_image_url
    response.lesson_cell_count = lesson.cell_count
    response.lesson_estimated_duration = lesson.estimated_duration
    response.sharer_name = current_user.full_name or current_user.username
    response.sharer_avatar_url = current_user.avatar_url
    response.group_name = group.name

    return response


@router.put("/{group_id}/lessons/{lesson_id}", response_model=SharedLessonResponse)
async def update_shared_lesson(
    group_id: int,
    lesson_id: int,
    lesson_data: SharedLessonUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_teacher),
) -> SharedLessonResponse:
    """更新共享教学设计（仅分享者可用）"""

    # 查找共享记录
    shared_lesson = await db.scalar(
        select(SharedLesson).where(
            and_(
                SharedLesson.group_id == group_id,
                SharedLesson.lesson_id == lesson_id,
            )
        )
    )
    if not shared_lesson:
        raise HTTPException(status_code=404, detail="共享记录不存在")

    # 检查权限
    if shared_lesson.sharer_id != current_user.id:
        raise HTTPException(status_code=403, detail="只能修改自己分享的教学设计")

    # 更新数据
    update_data = lesson_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(shared_lesson, key, value)

    await db.commit()
    await db.refresh(shared_lesson)

    # 构建响应
    lesson = await db.get(Lesson, lesson_id)
    group = await db.get(SubjectGroup, group_id)

    response = SharedLessonResponse.model_validate(shared_lesson)
    if lesson:
        response.lesson_title = lesson.title
        response.lesson_description = lesson.description
        response.lesson_cover_image_url = lesson.cover_image_url
        response.lesson_cell_count = lesson.cell_count
        response.lesson_estimated_duration = lesson.estimated_duration
    response.sharer_name = current_user.full_name or current_user.username
    response.sharer_avatar_url = current_user.avatar_url
    if group:
        response.group_name = group.name

    return response


@router.delete("/{group_id}/lessons/{lesson_id}")
async def unshare_lesson(
    group_id: int,
    lesson_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_teacher),
) -> dict:
    """取消分享教学设计（分享者或组长/管理员可用）"""

    # 查找共享记录
    shared_lesson = await db.scalar(
        select(SharedLesson).where(
            and_(
                SharedLesson.group_id == group_id,
                SharedLesson.lesson_id == lesson_id,
                SharedLesson.is_active == True,
            )
        )
    )
    if not shared_lesson:
        raise HTTPException(status_code=404, detail="共享记录不存在")

    # 检查权限：分享者或组长/管理员
    if shared_lesson.sharer_id != current_user.id:
        user_membership = await db.scalar(
            select(GroupMembership).where(
                and_(
                    GroupMembership.group_id == group_id,
                    GroupMembership.user_id == current_user.id,
                    GroupMembership.is_active == True,
                )
            )
        )
        if not user_membership or user_membership.role not in [
            MemberRole.OWNER,
            MemberRole.ADMIN,
        ]:
            raise HTTPException(status_code=403, detail="无权限取消此分享")

    # 软删除共享记录
    shared_lesson.is_active = False

    # 更新教研组共享教案数
    group = await db.get(SubjectGroup, group_id)
    if group:
        group.lesson_count = max(0, group.lesson_count - 1)

    await db.commit()

    return {"message": "已取消分享"}


@router.post("/{group_id}/lessons/{lesson_id}/view")
async def increment_lesson_view(
    group_id: int,
    lesson_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """增加教学设计查看次数"""

    # 查找共享记录
    shared_lesson = await db.scalar(
        select(SharedLesson).where(
            and_(
                SharedLesson.group_id == group_id,
                SharedLesson.lesson_id == lesson_id,
                SharedLesson.is_active == True,
            )
        )
    )
    if not shared_lesson:
        raise HTTPException(status_code=404, detail="共享记录不存在")

    # 增加查看次数
    shared_lesson.view_count += 1
    await db.commit()

    return {"message": "查看次数已更新", "view_count": shared_lesson.view_count}


@router.post("/{group_id}/lessons/{lesson_id}/download")
async def increment_lesson_download(
    group_id: int,
    lesson_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """增加教学设计下载次数"""

    # 查找共享记录
    shared_lesson = await db.scalar(
        select(SharedLesson).where(
            and_(
                SharedLesson.group_id == group_id,
                SharedLesson.lesson_id == lesson_id,
                SharedLesson.is_active == True,
            )
        )
    )
    if not shared_lesson:
        raise HTTPException(status_code=404, detail="共享记录不存在")

    # 增加下载次数
    shared_lesson.download_count += 1
    await db.commit()

    return {
        "message": "下载次数已更新",
        "download_count": shared_lesson.download_count,
    }


# ==================== 统计信息 ====================


@router.get("/statistics/overview", response_model=SubjectGroupStatistics)
async def get_statistics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SubjectGroupStatistics:
    """获取教研组统计信息"""

    # 总教研组数
    total_groups = await db.scalar(
        select(func.count(SubjectGroup.id)).where(SubjectGroup.is_active == True)
    )

    # 总成员数
    total_members = await db.scalar(
        select(func.count(GroupMembership.id)).where(GroupMembership.is_active == True)
    )

    # 总共享教案数
    total_shared_lessons = await db.scalar(
        select(func.count(SharedLesson.id)).where(SharedLesson.is_active == True)
    )

    # 我的教研组数
    my_groups = await db.scalar(
        select(func.count(GroupMembership.id)).where(
            and_(
                GroupMembership.user_id == current_user.id,
                GroupMembership.is_active == True,
            )
        )
    )

    # 我的共享教案数
    my_shared_lessons = await db.scalar(
        select(func.count(SharedLesson.id)).where(
            and_(
                SharedLesson.sharer_id == current_user.id,
                SharedLesson.is_active == True,
            )
        )
    )

    return SubjectGroupStatistics(
        total_groups=total_groups or 0,
        total_members=total_members or 0,
        total_shared_lessons=total_shared_lessons or 0,
        my_groups=my_groups or 0,
        my_shared_lessons=my_shared_lessons or 0,
    )
