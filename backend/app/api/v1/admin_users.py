"""
管理员用户管理 API
提供用户账号的增删改查、状态管理、密码重置等功能
"""

from typing import Any, List, Optional, cast
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, or_, delete, text
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime
import logging

from app.core.database import get_db
from app.core.validators import normalize_user_role
from app.models import User, UserRole, Region, School, Grade, Classroom
from app.models.evaluation import ExamNumberMapping, Score
from app.models.exam_room import ExamRoom, ExamRoomStudent
from app.models.activity import ActivitySubmission, PeerReview, FlowchartSnapshot, FormativeAssessment
from app.models.classroom_session import StudentSessionParticipation
from app.models.classroom_assistant import ClassroomMembership, AttendanceEntry, PositiveBehavior, DisciplineRecord, DutyAssignment
from app.models.question import Question, Answer, QuestionVote
from app.models.student_project import StudentProject
from app.models.project_cell import ProjectCell
from app.models.favorite import Favorite
from app.models.review import Review
from app.models.subject_group import GroupMembership
from app.models.teacher import TeacherTeachingAssignment
from app.models.exam_room import ExamProctor
from app.models.classroom_session import ClassSession
from app.models.lesson import Lesson, LessonClassroom
from app.models.cell import Cell
from app.api.deps import get_current_admin, get_current_admin_or_staff
from app.core.security import get_password_hash
from app.core.config import settings
import secrets
import string
from sqlalchemy.orm import selectinload


router = APIRouter()
logger = logging.getLogger(__name__)


# ==================== Request/Response Models ====================


class UserCreate(BaseModel):
    """创建用户请求"""

    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    role: UserRole
    is_active: bool = True
    region_id: Optional[int] = None
    school_id: Optional[int] = None
    grade_id: Optional[int] = None
    classroom_id: Optional[int] = None

    @field_validator("role", mode="before")
    @classmethod
    def normalize_role(cls, value: object) -> UserRole:
        normalized = normalize_user_role(value)
        if normalized is None:
            raise ValueError("用户角色不能为空")
        return normalized


class UserUpdate(BaseModel):
    """更新用户请求"""

    username: Optional[str] = None
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    region_id: Optional[int] = None
    school_id: Optional[int] = None
    grade_id: Optional[int] = None
    classroom_id: Optional[int] = None

    @field_validator("role", mode="before")
    @classmethod
    def normalize_role(cls, value: object) -> Optional[UserRole]:
        normalized = normalize_user_role(value, allow_none=True)
        return normalized


class UserResponse(BaseModel):
    """用户响应"""

    id: int
    username: str
    email: str
    full_name: Optional[str] = None
    role: UserRole
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    region_id: Optional[int] = None
    school_id: Optional[int] = None
    grade_id: Optional[int] = None
    classroom_id: Optional[int] = None
    region_name: Optional[str] = None
    school_name: Optional[str] = None
    grade_name: Optional[str] = None
    classroom_name: Optional[str] = None

    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    """用户列表响应"""

    users: List[UserResponse]
    total: int
    page: int
    size: int
    total_pages: int


class PasswordResetRequest(BaseModel):
    """密码重置请求"""

    user_id: int


class BatchImportRequest(BaseModel):
    """批量导入请求"""

    users: List[UserCreate]


class BatchDeleteByFilterRequest(BaseModel):
    """按条件批量删除请求"""

    role: UserRole = Field(..., description="用户角色（student/teacher）")
    region_id: Optional[int] = Field(None, description="区域ID（可选，不填则删除所有区域的）")
    school_id: Optional[int] = Field(None, description="学校ID（可选，不填则删除所有学校的）")
    grade_id: Optional[int] = Field(None, description="年级ID（可选，不填则删除所有年级的）")
    classroom_id: Optional[int] = Field(None, description="班级ID（可选，不填则删除所有班级的）")
    confirm: bool = Field(False, description="确认删除（需要先调用预览接口确认）")


class UnifiedImportItem(BaseModel):
    """统一导入项 - 支持创建用户和添加到班级"""
    
    # 用户标识字段（用于匹配已存在的用户）
    student_id_number: Optional[str] = Field(None, max_length=50, description="学籍号（唯一标识，推荐使用）")
    username: Optional[str] = Field(None, max_length=100, description="用户名/学号")
    email: Optional[str] = Field(None, max_length=255, description="邮箱")
    full_name: Optional[str] = Field(None, max_length=100, description="姓名")
    
    # 用户创建/更新字段
    password: Optional[str] = Field(None, min_length=6, max_length=50, description="密码（创建新用户时必需）")
    role: Optional[UserRole] = Field(None, description="用户角色")
    is_active: Optional[bool] = Field(True, description="是否激活")
    
    # 组织信息
    region_id: Optional[int] = Field(None, description="区域ID")
    school_id: Optional[int] = Field(None, description="学校ID")
    grade_id: Optional[int] = Field(None, description="年级ID")
    classroom_id: Optional[int] = Field(None, description="班级ID（如果提供，会自动将用户添加到班级）")
    
    # 班级成员信息（当提供classroom_id时使用）
    seat_no: Optional[int] = Field(None, description="座号")
    role_in_class: Optional[str] = Field(None, description="班级内角色：学生/正班主任/副班主任/任课教师/班干部")
    cadre_title: Optional[str] = Field(None, max_length=50, description="职务名称")
    is_primary_class: Optional[bool] = Field(False, description="是否为主班级")
    student_no: Optional[str] = Field(None, max_length=50, description="班级内的学号")
    
    @field_validator("role", mode="before")
    @classmethod
    def normalize_role(cls, value: object) -> Optional[UserRole]:
        if value is None:
            return None
        normalized = normalize_user_role(value, allow_none=True)
        return normalized


class UnifiedImportRequest(BaseModel):
    """统一导入请求 - 支持创建用户和添加到班级"""
    
    items: List[UnifiedImportItem]


class UnifiedImportResponse(BaseModel):
    """统一导入响应"""
    
    message: str
    created_users: List[UserResponse]
    added_members: List[dict]  # 添加到班级的成员信息
    errors: List[str]
    success_count: int
    error_count: int
    created_user_count: int
    added_member_count: int


def _user_with_relations_query():
    return select(User).options(
        selectinload(User.region),
        selectinload(User.school),
        selectinload(User.grade),
        selectinload(User.classroom),
    )


async def _fetch_user_with_relations(db: AsyncSession, user_id: int) -> Optional[User]:
    result = await db.execute(_user_with_relations_query().where(User.id == user_id))
    return result.scalar_one_or_none()


def _scope_users_query_for_org_staff(query, current_user: User):
    """按区县/学校管理员的数据范围限制用户列表查询；平台管理员不加限制。"""
    if current_user.role == UserRole.ADMIN:
        return query
    if current_user.role == UserRole.DISTRICT_ADMIN:
        if current_user.region_id is None:
            return None
        schools_in_region = select(School.id).where(
            School.region_id == current_user.region_id
        )
        return query.where(
            or_(
                User.region_id == current_user.region_id,
                User.school_id.in_(schools_in_region),
            )
        )
    if current_user.role == UserRole.SCHOOL_ADMIN:
        if current_user.school_id is None:
            return None
        return query.where(User.school_id == current_user.school_id)
    raise HTTPException(
        status_code=403,
        detail="需要管理员、区县管理员或学校管理员权限",
    )


def _serialize_user(user: User) -> UserResponse:
    """Serialize user with related organization names."""
    return UserResponse(
        id=cast(int, user.id),
        username=cast(str, user.username),
        email=cast(str, user.email),
        full_name=cast(Optional[str], user.full_name),
        role=cast(UserRole, user.role),
        is_active=cast(bool, user.is_active),
        created_at=cast(datetime, user.created_at),
        last_login=cast(Optional[datetime], getattr(user, "last_login", None)),
        region_id=cast(Optional[int], user.region_id),
        school_id=cast(Optional[int], user.school_id),
        grade_id=cast(Optional[int], user.grade_id),
        classroom_id=cast(Optional[int], user.classroom_id),
        region_name=user.region.name if user.region else None,
        school_name=user.school.name if user.school else None,
        grade_name=user.grade.name if user.grade else None,
        classroom_name=user.classroom.name if user.classroom else None,
    )


async def _validate_scope_ids(
    db: AsyncSession,
    *,
    region_id: Optional[int] = None,
    school_id: Optional[int] = None,
    grade_id: Optional[int] = None,
    classroom_id: Optional[int] = None,
) -> dict:
    """验证并整理区域/学校/年级/班级信息"""

    resolved: dict[str, Optional[int]] = {
        "region_id": region_id,
        "school_id": school_id,
        "grade_id": grade_id,
        "classroom_id": classroom_id,
    }

    school_obj: Optional[School] = None

    if classroom_id is not None:
        classroom = await db.scalar(
            select(Classroom).where(Classroom.id == classroom_id)
        )
        if not classroom:
            raise HTTPException(status_code=404, detail="班级不存在")

        resolved["classroom_id"] = cast(int, classroom.id)
        resolved["grade_id"] = cast(Optional[int], classroom.grade_id)
        resolved["school_id"] = cast(Optional[int], classroom.school_id)
        school_obj = await db.scalar(
            select(School).where(School.id == classroom.school_id)
        )

    if resolved["grade_id"] is not None:
        grade = await db.scalar(select(Grade).where(Grade.id == resolved["grade_id"]))
        if not grade:
            raise HTTPException(status_code=404, detail="年级不存在")

    if resolved["school_id"] is not None:
        school_obj = school_obj or await db.scalar(
            select(School).where(School.id == resolved["school_id"])
        )
        if not school_obj:
            raise HTTPException(status_code=404, detail="学校不存在")
        resolved["school_id"] = cast(Optional[int], school_obj.id)

        if resolved["region_id"] is None:
            resolved["region_id"] = cast(Optional[int], school_obj.region_id)
        elif resolved["region_id"] != cast(Optional[int], school_obj.region_id):
            raise HTTPException(status_code=400, detail="学校与区域不匹配")

    if resolved["region_id"] is not None:
        region = await db.scalar(
            select(Region).where(Region.id == resolved["region_id"])
        )
        if not region:
            raise HTTPException(status_code=404, detail="区域不存在")

    return resolved


# ==================== Endpoints ====================


@router.get("", response_model=UserListResponse)
@router.get("/", response_model=UserListResponse)
async def get_users(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=1000, description="每页数量"),
    role: Optional[UserRole] = Query(None, description="角色筛选"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_or_staff),
) -> Any:
    """获取用户列表（平台管理员全量；区县/学校管理员仅本区县或本校范围）"""

    # 构建查询
    query = _user_with_relations_query()

    # 角色筛选
    if role:
        query = query.where(User.role == role)

    # 搜索筛选
    if search:
        search_filter = or_(
            User.username.ilike(f"%{search}%"), User.email.ilike(f"%{search}%")
        )
        query = query.where(search_filter)

    query = _scope_users_query_for_org_staff(query, current_user)
    if query is None:
        return UserListResponse(
            users=[], total=0, page=page, size=size, total_pages=0
        )

    # 获取总数
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # 分页查询
    offset = (page - 1) * size
    query = query.offset(offset).limit(size).order_by(User.created_at.desc())

    result = await db.execute(query)
    users = result.scalars().all()

    total_pages = (total + size - 1) // size

    return UserListResponse(
        users=[_serialize_user(user) for user in users],
        total=total,
        page=page,
        size=size,
        total_pages=total_pages,
    )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Any:
    """获取用户详情"""

    user = await _fetch_user_with_relations(db, user_id)

    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    return _serialize_user(user)


@router.post("", response_model=UserResponse)
@router.post("/", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Any:
    """创建用户"""

    # 检查用户名是否已存在
    existing_user = await db.execute(
        select(User).where(User.username == user_data.username)
    )
    if existing_user.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="用户名已存在")

    # 检查邮箱是否已存在
    existing_email = await db.execute(select(User).where(User.email == user_data.email))
    if existing_email.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="邮箱已存在")

    # 创建用户
    hashed_password = get_password_hash(user_data.password)
    scope_ids = await _validate_scope_ids(
        db,
        region_id=user_data.region_id,
        school_id=user_data.school_id,
        grade_id=user_data.grade_id,
        classroom_id=user_data.classroom_id,
    )
    # 确保 is_active 有默认值，如果为 None 则设为 True
    is_active = user_data.is_active if user_data.is_active is not None else True
    user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
        role=user_data.role,
        is_active=is_active,
        **scope_ids,
    )

    db.add(user)
    await db.commit()

    refreshed_user = await _fetch_user_with_relations(db, cast(int, user.id))
    if refreshed_user is None:
        raise HTTPException(status_code=404, detail="用户不存在")

    return _serialize_user(refreshed_user)


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Any:
    """更新用户"""

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 检查用户名是否已被其他用户使用
    if user_data.username and user_data.username != user.username:
        existing_user = await db.execute(
            select(User).where(User.username == user_data.username, User.id != user_id)
        )
        if existing_user.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="用户名已存在")

    # 检查邮箱是否已被其他用户使用
    if user_data.email and user_data.email != user.email:
        existing_email = await db.execute(
            select(User).where(User.email == user_data.email, User.id != user_id)
        )
        if existing_email.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="邮箱已存在")

    # 更新用户信息
    update_data = user_data.model_dump(exclude_unset=True)
    scope_fields = {"region_id", "school_id", "grade_id", "classroom_id"}

    if any(field in update_data for field in scope_fields):
        scope_kwargs = {
            field: update_data.get(field, getattr(user, field))
            for field in scope_fields
        }
        resolved_scope = await _validate_scope_ids(db, **scope_kwargs)
        for field, value in resolved_scope.items():
            setattr(user, field, value)
        for field in scope_fields:
            update_data.pop(field, None)

    for field, value in update_data.items():
        setattr(user, field, value)

    await db.commit()

    refreshed_user = await _fetch_user_with_relations(db, cast(int, user.id))
    if refreshed_user is None:
        raise HTTPException(status_code=404, detail="用户不存在")

    return _serialize_user(refreshed_user)


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Any:
    """删除用户"""

    # 不能删除自己
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="不能删除自己的账号")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    await db.delete(user)
    await db.commit()

    return {"message": "用户删除成功"}


@router.post("/batch-delete")
async def batch_delete_users(
    user_ids: List[int],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Any:
    """批量删除用户

    Args:
        user_ids: 要删除的用户ID列表

    Returns:
        删除结果统计
    """

    if not user_ids:
        raise HTTPException(status_code=400, detail="用户ID列表不能为空")

    # 不能删除自己
    if current_user.id in user_ids:
        raise HTTPException(status_code=400, detail="不能删除自己的账号")

    # 查询用户
    result = await db.execute(
        select(User).where(User.id.in_(user_ids))
    )
    users = result.scalars().all()

    if not users:
        raise HTTPException(status_code=404, detail="未找到任何用户")

    # 统计删除结果（使用与 batch_delete_by_filter 相同的完整删除逻辑）
    deleted_count = 0
    mappings_deleted = 0
    room_students_deleted = 0
    activity_submissions_deleted = 0
    peer_reviews_deleted = 0
    flowchart_snapshots_deleted = 0
    session_participations_deleted = 0
    classroom_memberships_deleted = 0
    attendance_entries_deleted = 0
    positive_behaviors_deleted = 0
    discipline_records_deleted = 0
    scores_deleted = 0
    formative_assessments_deleted = 0
    questions_deleted = 0
    student_projects_deleted = 0
    project_cells_deleted = 0
    favorites_deleted = 0
    reviews_deleted = 0
    question_votes_deleted = 0
    answers_deleted = 0
    group_memberships_deleted = 0
    duty_assignments_deleted = 0
    teaching_assignments_deleted = 0
    exam_proctors_deleted = 0
    class_sessions_deleted = 0
    lessons_deleted = 0
    lesson_classrooms_deleted = 0
    cells_deleted = 0

    try:
        # 第一步：删除考号映射记录（批量删除）
        delete_mappings_result = await db.execute(
            delete(ExamNumberMapping).where(
                ExamNumberMapping.student_id.in_(user_ids)
            )
        )
        mappings_deleted = delete_mappings_result.rowcount
        logger.info(f"Deleted {mappings_deleted} exam number mappings for users: {user_ids}")

        # 第二步：删除考场学生关联记录（批量删除）
        delete_room_students_result = await db.execute(
            delete(ExamRoomStudent).where(
                ExamRoomStudent.student_id.in_(user_ids)
            )
        )
        room_students_deleted = delete_room_students_result.rowcount
        logger.info(f"Deleted {room_students_deleted} exam room student assignments for users: {user_ids}")

        # 第三步：获取学生的活动提交ID（用于删除相关的互评和流程图快照）
        submissions_result = await db.execute(
            select(ActivitySubmission.id).where(
                ActivitySubmission.student_id.in_(user_ids)
            )
        )
        submission_ids = [row[0] for row in submissions_result.all()]
        logger.info(f"Found {len(submission_ids)} activity submissions to delete")

        # 第四步：删除流程图快照（通过 submission_id 和 student_id 关联）
        conditions = [FlowchartSnapshot.student_id.in_(user_ids)]
        if submission_ids:
            conditions.append(FlowchartSnapshot.submission_id.in_(submission_ids))
        
        delete_flowchart_snapshots_result = await db.execute(
            delete(FlowchartSnapshot).where(
                or_(*conditions)
            )
        )
        flowchart_snapshots_deleted = delete_flowchart_snapshots_result.rowcount
        logger.info(f"Deleted {flowchart_snapshots_deleted} flowchart snapshots")

        # 第五步：删除互评记录（包括学生作为评审者的互评，以及评审这些学生提交的互评）
        delete_reviewer_peer_reviews_result = await db.execute(
            delete(PeerReview).where(
                PeerReview.reviewer_id.in_(user_ids)
            )
        )
        reviewer_peer_reviews_deleted = delete_reviewer_peer_reviews_result.rowcount
        if submission_ids:
            delete_submission_peer_reviews_result = await db.execute(
                delete(PeerReview).where(
                    PeerReview.submission_id.in_(submission_ids)
                )
            )
            submission_peer_reviews_deleted = delete_submission_peer_reviews_result.rowcount
        else:
            submission_peer_reviews_deleted = 0
        peer_reviews_deleted = reviewer_peer_reviews_deleted + submission_peer_reviews_deleted
        logger.info(f"Deleted {peer_reviews_deleted} peer reviews")

        # 第六步：删除活动提交记录（批量删除）
        delete_activity_submissions_result = await db.execute(
            delete(ActivitySubmission).where(
                ActivitySubmission.student_id.in_(user_ids)
            )
        )
        activity_submissions_deleted = delete_activity_submissions_result.rowcount
        logger.info(f"Deleted {activity_submissions_deleted} activity submissions")

        # 第七步：删除课堂会话参与记录（批量删除）
        delete_session_participations_result = await db.execute(
            delete(StudentSessionParticipation).where(
                StudentSessionParticipation.student_id.in_(user_ids)
            )
        )
        session_participations_deleted = delete_session_participations_result.rowcount
        logger.info(f"Deleted {session_participations_deleted} session participations")

        # 第八步：删除班级成员关系（批量删除）
        delete_classroom_memberships_result = await db.execute(
            delete(ClassroomMembership).where(
                ClassroomMembership.user_id.in_(user_ids)
            )
        )
        classroom_memberships_deleted = delete_classroom_memberships_result.rowcount
        logger.info(f"Deleted {classroom_memberships_deleted} classroom memberships")

        # 第九步：删除考勤记录（批量删除）
        delete_attendance_entries_result = await db.execute(
            delete(AttendanceEntry).where(
                AttendanceEntry.student_id.in_(user_ids)
            )
        )
        attendance_entries_deleted = delete_attendance_entries_result.rowcount
        logger.info(f"Deleted {attendance_entries_deleted} attendance entries")

        # 第十步：删除正面行为记录（批量删除）
        delete_positive_behaviors_result = await db.execute(
            delete(PositiveBehavior).where(
                PositiveBehavior.student_id.in_(user_ids)
            )
        )
        positive_behaviors_deleted = delete_positive_behaviors_result.rowcount
        logger.info(f"Deleted {positive_behaviors_deleted} positive behaviors")

        # 第十一步：删除纪律记录（批量删除）
        delete_discipline_records_result = await db.execute(
            delete(DisciplineRecord).where(
                DisciplineRecord.student_id.in_(user_ids)
            )
        )
        discipline_records_deleted = delete_discipline_records_result.rowcount
        logger.info(f"Deleted {discipline_records_deleted} discipline records")

        # 第十二步：删除成绩记录（批量删除）
        delete_scores_result = await db.execute(
            delete(Score).where(
                Score.student_id.in_(user_ids)
            )
        )
        scores_deleted = delete_scores_result.rowcount
        logger.info(f"Deleted {scores_deleted} scores")

        # 第十三步：删除过程性评估记录（批量删除）
        delete_formative_assessments_result = await db.execute(
            delete(FormativeAssessment).where(
                FormativeAssessment.student_id.in_(user_ids)
            )
        )
        formative_assessments_deleted = delete_formative_assessments_result.rowcount
        logger.info(f"Deleted {formative_assessments_deleted} formative assessments")

        # 第十四步：删除问题记录（批量删除）
        delete_questions_result = await db.execute(
            delete(Question).where(
                Question.student_id.in_(user_ids)
            )
        )
        questions_deleted = delete_questions_result.rowcount
        logger.info(f"Deleted {questions_deleted} questions")

        # 第十五步：获取学生项目ID（用于删除相关的项目Cell）
        projects_result = await db.execute(
            select(StudentProject.id).where(
                StudentProject.creator_id.in_(user_ids)
            )
        )
        project_ids = [row[0] for row in projects_result.all()]
        logger.info(f"Found {len(project_ids)} student projects to delete")

        # 第十六步：删除项目Cell
        if project_ids:
            delete_project_cells_result = await db.execute(
                delete(ProjectCell).where(
                    ProjectCell.project_id.in_(project_ids)
                )
            )
            project_cells_deleted = delete_project_cells_result.rowcount
        else:
            project_cells_deleted = 0
        logger.info(f"Deleted {project_cells_deleted} project cells")

        # 第十七步：删除学生项目（批量删除）
        delete_student_projects_result = await db.execute(
            delete(StudentProject).where(
                StudentProject.creator_id.in_(user_ids)
            )
        )
        student_projects_deleted = delete_student_projects_result.rowcount
        logger.info(f"Deleted {student_projects_deleted} student projects")

        # 第十八步：删除收藏记录（批量删除）
        delete_favorites_result = await db.execute(
            delete(Favorite).where(
                Favorite.user_id.in_(user_ids)
            )
        )
        favorites_deleted = delete_favorites_result.rowcount
        logger.info(f"Deleted {favorites_deleted} favorites")

        # 第十九步：删除评分评论记录（批量删除）
        delete_reviews_result = await db.execute(
            delete(Review).where(
                Review.user_id.in_(user_ids)
            )
        )
        reviews_deleted = delete_reviews_result.rowcount
        logger.info(f"Deleted {reviews_deleted} reviews")

        # 第二十步：删除问题点赞记录（批量删除）
        delete_question_votes_result = await db.execute(
            delete(QuestionVote).where(
                QuestionVote.user_id.in_(user_ids)
            )
        )
        question_votes_deleted = delete_question_votes_result.rowcount
        logger.info(f"Deleted {question_votes_deleted} question votes")

        # 第二十一步：删除回答记录（批量删除）
        delete_answers_result = await db.execute(
            delete(Answer).where(
                Answer.answerer_id.in_(user_ids)
            )
        )
        answers_deleted = delete_answers_result.rowcount
        logger.info(f"Deleted {answers_deleted} answers")

        # 第二十二步：删除教研组成员关系（批量删除）
        delete_group_memberships_result = await db.execute(
            delete(GroupMembership).where(
                GroupMembership.user_id.in_(user_ids)
            )
        )
        group_memberships_deleted = delete_group_memberships_result.rowcount
        logger.info(f"Deleted {group_memberships_deleted} group memberships")

        # 第二十三步：删除值日任务分配记录（批量删除，包括被分配者和完成者）
        delete_duty_assignments_result = await db.execute(
            delete(DutyAssignment).where(
                or_(
                    DutyAssignment.assignee_user_id.in_(user_ids),
                    DutyAssignment.completed_by_user_id.in_(user_ids)
                )
            )
        )
        duty_assignments_deleted = delete_duty_assignments_result.rowcount
        logger.info(f"Deleted {duty_assignments_deleted} duty assignments")

        # 第二十四步：删除教师教学任务分配（批量删除）
        delete_teaching_assignments_result = await db.execute(
            delete(TeacherTeachingAssignment).where(
                TeacherTeachingAssignment.teacher_id.in_(user_ids)
            )
        )
        teaching_assignments_deleted = delete_teaching_assignments_result.rowcount
        logger.info(f"Deleted {teaching_assignments_deleted} teaching assignments")

        # 第二十五步：删除考场监考安排（批量删除）
        delete_exam_proctors_result = await db.execute(
            delete(ExamProctor).where(
                ExamProctor.user_id.in_(user_ids)
            )
        )
        exam_proctors_deleted = delete_exam_proctors_result.rowcount
        logger.info(f"Deleted {exam_proctors_deleted} exam proctors")

        # 第二十六步：删除课堂会话（教师创建的会话，批量删除）
        delete_class_sessions_result = await db.execute(
            delete(ClassSession).where(
                ClassSession.teacher_id.in_(user_ids)
            )
        )
        class_sessions_deleted = delete_class_sessions_result.rowcount
        logger.info(f"Deleted {class_sessions_deleted} class sessions")

        # 第二十七步：获取教师创建的课程ID（用于删除相关的 LessonClassroom）
        lessons_result = await db.execute(
            select(Lesson.id).where(
                Lesson.creator_id.in_(user_ids)
            )
        )
        lesson_ids = [row[0] for row in lessons_result.all()]
        logger.info(f"Found {len(lesson_ids)} lessons created by users to delete")

        # 第二十八步：删除课程-班级关联（批量删除，虽然设置了CASCADE，但为了明确先删除）
        if lesson_ids:
            delete_lesson_classrooms_result = await db.execute(
                delete(LessonClassroom).where(
                    LessonClassroom.lesson_id.in_(lesson_ids)
                )
            )
            lesson_classrooms_deleted = delete_lesson_classrooms_result.rowcount
        else:
            lesson_classrooms_deleted = 0
        logger.info(f"Deleted {lesson_classrooms_deleted} lesson classrooms")

        # 第二十九步：删除课程的Cell（批量删除，因为Cell没有CASCADE设置）
        if lesson_ids:
            delete_cells_result = await db.execute(
                delete(Cell).where(
                    Cell.lesson_id.in_(lesson_ids)
                )
            )
            cells_deleted = delete_cells_result.rowcount
        else:
            cells_deleted = 0
        logger.info(f"Deleted {cells_deleted} cells")

        # 第三十步：删除课程（教师创建的课程，批量删除）
        delete_lessons_result = await db.execute(
            delete(Lesson).where(
                Lesson.creator_id.in_(user_ids)
            )
        )
        lessons_deleted = delete_lessons_result.rowcount
        logger.info(f"Deleted {lessons_deleted} lessons")

        # 使用flush确保操作执行但保持事务
        await db.flush()
        logger.info("Flushed all user-related data deletions")

        # 第三十一步：批量删除用户（使用批量删除更高效）
        delete_users_result = await db.execute(
            delete(User).where(User.id.in_(user_ids))
        )
        deleted_count = delete_users_result.rowcount
        logger.info(f"Deleted {deleted_count} users")

        # 提交所有删除操作
        await db.commit()
        logger.info(f"Successfully committed batch delete of {deleted_count} users")

    except Exception as e:
        logger.error(f"Batch delete failed: {str(e)}", exc_info=True)
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"批量删除失败: {str(e)}"
        )

    response_data = {
        "message": f"成功删除 {deleted_count} 个用户",
        "deleted_count": deleted_count,
        "total_requested": len(user_ids),
        "exam_mappings_deleted": mappings_deleted,
        "exam_room_students_deleted": room_students_deleted,
        "activity_submissions_deleted": activity_submissions_deleted,
        "peer_reviews_deleted": peer_reviews_deleted,
        "flowchart_snapshots_deleted": flowchart_snapshots_deleted,
        "session_participations_deleted": session_participations_deleted,
        "classroom_memberships_deleted": classroom_memberships_deleted,
        "attendance_entries_deleted": attendance_entries_deleted,
        "positive_behaviors_deleted": positive_behaviors_deleted,
        "discipline_records_deleted": discipline_records_deleted,
        "scores_deleted": scores_deleted,
        "formative_assessments_deleted": formative_assessments_deleted,
        "questions_deleted": questions_deleted,
        "student_projects_deleted": student_projects_deleted,
        "project_cells_deleted": project_cells_deleted,
        "favorites_deleted": favorites_deleted,
        "reviews_deleted": reviews_deleted,
        "question_votes_deleted": question_votes_deleted,
        "answers_deleted": answers_deleted,
        "group_memberships_deleted": group_memberships_deleted,
        "duty_assignments_deleted": duty_assignments_deleted,
        "teaching_assignments_deleted": teaching_assignments_deleted,
        "exam_proctors_deleted": exam_proctors_deleted,
        "class_sessions_deleted": class_sessions_deleted,
        "lessons_deleted": lessons_deleted,
        "lesson_classrooms_deleted": lesson_classrooms_deleted,
        "cells_deleted": cells_deleted
    }

    return response_data


@router.post("/batch-delete-by-filter/preview")
async def preview_batch_delete_by_filter(
    filters: BatchDeleteByFilterRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Any:
    """预览按条件批量删除的用户数量

    Args:
        filters: 删除条件

    Returns:
        将要删除的用户统计信息
    """
    # 构建查询条件
    conditions = [User.role == filters.role]

    if filters.region_id:
        conditions.append(User.region_id == filters.region_id)
    if filters.school_id:
        conditions.append(User.school_id == filters.school_id)
    if filters.grade_id:
        conditions.append(User.grade_id == filters.grade_id)
    if filters.classroom_id:
        conditions.append(User.classroom_id == filters.classroom_id)

    # 查询符合条件的用户数量
    count_result = await db.execute(
        select(func.count(User.id)).where(*conditions)
    )
    total_count = count_result.scalar() or 0

    if total_count == 0:
        return {
            "total_count": 0,
            "message": "没有找到符合条件的用户"
        }

    # 查询部分用户详情用于显示（最多返回前100个）
    users_result = await db.execute(
        select(User).where(*conditions).limit(100)
    )
    users = users_result.scalars().all()

    return {
        "total_count": total_count,
        "preview_users": [
            {
                "id": u.id,
                "username": u.username,
                "full_name": u.full_name,
                "email": u.email,
                "school_name": getattr(u, "school_name", None),
                "grade_name": getattr(u, "grade_name", None),
                "classroom_name": getattr(u, "classroom_name", None),
            }
            for u in users
        ],
        "showing": min(100, total_count),
        "message": f"将删除 {total_count} 个用户" + (
            f"（显示前{min(100, total_count)}个）" if total_count > 100 else ""
        )
    }


@router.post("/batch-delete-by-filter")
async def batch_delete_by_filter(
    filters: BatchDeleteByFilterRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Any:
    """按条件批量删除用户（支持大规模删除）

    Args:
        filters: 删除条件

    Returns:
        删除结果统计
    """
    # 要求必须先确认
    if not filters.confirm:
        raise HTTPException(
            status_code=400,
            detail="请先调用预览接口确认删除操作，设置 confirm=true"
        )

    # 构建查询条件
    conditions = [User.role == filters.role]

    if filters.region_id:
        conditions.append(User.region_id == filters.region_id)
    if filters.school_id:
        conditions.append(User.school_id == filters.school_id)
    if filters.grade_id:
        conditions.append(User.grade_id == filters.grade_id)
    if filters.classroom_id:
        conditions.append(User.classroom_id == filters.classroom_id)

    # 查询符合条件的用户ID
    result = await db.execute(
        select(User.id).where(*conditions)
    )
    user_ids = [row[0] for row in result.all()]

    if not user_ids:
        raise HTTPException(status_code=404, detail="未找到符合条件的用户")

    logger.info(f"Batch delete by filter: {len(user_ids)} users matched criteria")

    # 不能删除自己
    if current_user.id in user_ids:
        raise HTTPException(status_code=400, detail="删除条件包含当前登录用户，不能删除自己的账号")

    deleted_count = 0
    mappings_deleted = 0
    room_students_deleted = 0
    activity_submissions_deleted = 0
    peer_reviews_deleted = 0
    flowchart_snapshots_deleted = 0
    session_participations_deleted = 0
    classroom_memberships_deleted = 0
    attendance_entries_deleted = 0
    positive_behaviors_deleted = 0
    discipline_records_deleted = 0
    scores_deleted = 0
    formative_assessments_deleted = 0
    questions_deleted = 0
    student_projects_deleted = 0
    project_cells_deleted = 0
    favorites_deleted = 0
    reviews_deleted = 0
    question_votes_deleted = 0
    answers_deleted = 0
    group_memberships_deleted = 0

    try:
        # 第一步：删除考号映射记录（批量删除）
        delete_mappings_result = await db.execute(
            delete(ExamNumberMapping).where(
                ExamNumberMapping.student_id.in_(user_ids)
            )
        )
        mappings_deleted = delete_mappings_result.rowcount
        logger.info(f"Deleted {mappings_deleted} exam number mappings")

        # 第二步：删除考场学生关联记录（批量删除）
        delete_room_students_result = await db.execute(
            delete(ExamRoomStudent).where(
                ExamRoomStudent.student_id.in_(user_ids)
            )
        )
        room_students_deleted = delete_room_students_result.rowcount
        logger.info(f"Deleted {room_students_deleted} exam room student assignments")

        # 第三步：获取学生的活动提交ID（用于删除相关的互评和流程图快照）
        submissions_result = await db.execute(
            select(ActivitySubmission.id).where(
                ActivitySubmission.student_id.in_(user_ids)
            )
        )
        submission_ids = [row[0] for row in submissions_result.all()]
        logger.info(f"Found {len(submission_ids)} activity submissions to delete")

        # 第四步：删除流程图快照（通过 submission_id 和 student_id 关联）
        conditions = [FlowchartSnapshot.student_id.in_(user_ids)]
        if submission_ids:
            conditions.append(FlowchartSnapshot.submission_id.in_(submission_ids))
        
        delete_flowchart_snapshots_result = await db.execute(
            delete(FlowchartSnapshot).where(
                or_(*conditions)
            )
        )
        flowchart_snapshots_deleted = delete_flowchart_snapshots_result.rowcount
        logger.info(f"Deleted {flowchart_snapshots_deleted} flowchart snapshots")

        # 第五步：删除互评记录（包括学生作为评审者的互评，以及评审这些学生提交的互评）
        # 删除学生作为评审者的互评记录
        delete_reviewer_peer_reviews_result = await db.execute(
            delete(PeerReview).where(
                PeerReview.reviewer_id.in_(user_ids)
            )
        )
        reviewer_peer_reviews_deleted = delete_reviewer_peer_reviews_result.rowcount
        # 删除评审这些学生提交的互评记录
        if submission_ids:
            delete_submission_peer_reviews_result = await db.execute(
                delete(PeerReview).where(
                    PeerReview.submission_id.in_(submission_ids)
                )
            )
            submission_peer_reviews_deleted = delete_submission_peer_reviews_result.rowcount
        else:
            submission_peer_reviews_deleted = 0
        peer_reviews_deleted = reviewer_peer_reviews_deleted + submission_peer_reviews_deleted
        logger.info(f"Deleted {peer_reviews_deleted} peer reviews ({reviewer_peer_reviews_deleted} as reviewer, {submission_peer_reviews_deleted} on submissions)")

        # 第六步：删除活动提交记录（批量删除）
        delete_activity_submissions_result = await db.execute(
            delete(ActivitySubmission).where(
                ActivitySubmission.student_id.in_(user_ids)
            )
        )
        activity_submissions_deleted = delete_activity_submissions_result.rowcount
        logger.info(f"Deleted {activity_submissions_deleted} activity submissions")

        # 第六步：删除课堂会话参与记录（批量删除）
        delete_session_participations_result = await db.execute(
            delete(StudentSessionParticipation).where(
                StudentSessionParticipation.student_id.in_(user_ids)
            )
        )
        session_participations_deleted = delete_session_participations_result.rowcount
        logger.info(f"Deleted {session_participations_deleted} session participations")

        # 第七步：删除班级成员关系（批量删除）
        delete_classroom_memberships_result = await db.execute(
            delete(ClassroomMembership).where(
                ClassroomMembership.user_id.in_(user_ids)
            )
        )
        classroom_memberships_deleted = delete_classroom_memberships_result.rowcount
        logger.info(f"Deleted {classroom_memberships_deleted} classroom memberships")

        # 第八步：删除考勤记录（批量删除）
        delete_attendance_entries_result = await db.execute(
            delete(AttendanceEntry).where(
                AttendanceEntry.student_id.in_(user_ids)
            )
        )
        attendance_entries_deleted = delete_attendance_entries_result.rowcount
        logger.info(f"Deleted {attendance_entries_deleted} attendance entries")

        # 第九步：删除正面行为记录（批量删除）
        delete_positive_behaviors_result = await db.execute(
            delete(PositiveBehavior).where(
                PositiveBehavior.student_id.in_(user_ids)
            )
        )
        positive_behaviors_deleted = delete_positive_behaviors_result.rowcount
        logger.info(f"Deleted {positive_behaviors_deleted} positive behaviors")

        # 第十步：删除纪律记录（批量删除）
        delete_discipline_records_result = await db.execute(
            delete(DisciplineRecord).where(
                DisciplineRecord.student_id.in_(user_ids)
            )
        )
        discipline_records_deleted = delete_discipline_records_result.rowcount
        logger.info(f"Deleted {discipline_records_deleted} discipline records")

        # 第十一步：删除成绩记录（批量删除）
        delete_scores_result = await db.execute(
            delete(Score).where(
                Score.student_id.in_(user_ids)
            )
        )
        scores_deleted = delete_scores_result.rowcount
        logger.info(f"Deleted {scores_deleted} scores")

        # 第十二步：删除过程性评估记录（批量删除）
        delete_formative_assessments_result = await db.execute(
            delete(FormativeAssessment).where(
                FormativeAssessment.student_id.in_(user_ids)
            )
        )
        formative_assessments_deleted = delete_formative_assessments_result.rowcount
        logger.info(f"Deleted {formative_assessments_deleted} formative assessments")

        # 第十三步：删除问题记录（批量删除）
        delete_questions_result = await db.execute(
            delete(Question).where(
                Question.student_id.in_(user_ids)
            )
        )
        questions_deleted = delete_questions_result.rowcount
        logger.info(f"Deleted {questions_deleted} questions")

        # 第十四步：获取学生项目ID（用于删除相关的项目Cell）
        projects_result = await db.execute(
            select(StudentProject.id).where(
                StudentProject.creator_id.in_(user_ids)
            )
        )
        project_ids = [row[0] for row in projects_result.all()]
        logger.info(f"Found {len(project_ids)} student projects to delete")

        # 第十五步：删除项目Cell（虽然CASCADE会自动删除，但为了完整性先删除）
        if project_ids:
            delete_project_cells_result = await db.execute(
                delete(ProjectCell).where(
                    ProjectCell.project_id.in_(project_ids)
                )
            )
            project_cells_deleted = delete_project_cells_result.rowcount
        else:
            project_cells_deleted = 0
        logger.info(f"Deleted {project_cells_deleted} project cells")

        # 第十六步：删除学生项目（批量删除）
        delete_student_projects_result = await db.execute(
            delete(StudentProject).where(
                StudentProject.creator_id.in_(user_ids)
            )
        )
        student_projects_deleted = delete_student_projects_result.rowcount
        logger.info(f"Deleted {student_projects_deleted} student projects")

        # 第十七步：删除收藏记录（批量删除）
        delete_favorites_result = await db.execute(
            delete(Favorite).where(
                Favorite.user_id.in_(user_ids)
            )
        )
        favorites_deleted = delete_favorites_result.rowcount
        logger.info(f"Deleted {favorites_deleted} favorites")

        # 第十八步：删除评分评论记录（批量删除）
        delete_reviews_result = await db.execute(
            delete(Review).where(
                Review.user_id.in_(user_ids)
            )
        )
        reviews_deleted = delete_reviews_result.rowcount
        logger.info(f"Deleted {reviews_deleted} reviews")

        # 第十九步：删除问题点赞记录（批量删除）
        delete_question_votes_result = await db.execute(
            delete(QuestionVote).where(
                QuestionVote.user_id.in_(user_ids)
            )
        )
        question_votes_deleted = delete_question_votes_result.rowcount
        logger.info(f"Deleted {question_votes_deleted} question votes")

        # 第二十步：删除回答记录（批量删除，学生可能回答过问题）
        delete_answers_result = await db.execute(
            delete(Answer).where(
                Answer.answerer_id.in_(user_ids)
            )
        )
        answers_deleted = delete_answers_result.rowcount
        logger.info(f"Deleted {answers_deleted} answers")

        # 第二十一步：删除教研组成员关系（批量删除）
        delete_group_memberships_result = await db.execute(
            delete(GroupMembership).where(
                GroupMembership.user_id.in_(user_ids)
            )
        )
        group_memberships_deleted = delete_group_memberships_result.rowcount
        logger.info(f"Deleted {group_memberships_deleted} group memberships")

        # 第二十二步：删除值日任务分配记录（批量删除，包括被分配者和完成者）
        delete_duty_assignments_result = await db.execute(
            delete(DutyAssignment).where(
                or_(
                    DutyAssignment.assignee_user_id.in_(user_ids),
                    DutyAssignment.completed_by_user_id.in_(user_ids)
                )
            )
        )
        duty_assignments_deleted = delete_duty_assignments_result.rowcount
        logger.info(f"Deleted {duty_assignments_deleted} duty assignments")

        # 第二十三步：删除教师教学任务分配（批量删除）
        delete_teaching_assignments_result = await db.execute(
            delete(TeacherTeachingAssignment).where(
                TeacherTeachingAssignment.teacher_id.in_(user_ids)
            )
        )
        teaching_assignments_deleted = delete_teaching_assignments_result.rowcount
        logger.info(f"Deleted {teaching_assignments_deleted} teaching assignments")

        # 第二十四步：删除考场监考安排（批量删除）
        delete_exam_proctors_result = await db.execute(
            delete(ExamProctor).where(
                ExamProctor.user_id.in_(user_ids)
            )
        )
        exam_proctors_deleted = delete_exam_proctors_result.rowcount
        logger.info(f"Deleted {exam_proctors_deleted} exam proctors")

        # 第二十五步：删除课堂会话（教师创建的会话，批量删除）
        delete_class_sessions_result = await db.execute(
            delete(ClassSession).where(
                ClassSession.teacher_id.in_(user_ids)
            )
        )
        class_sessions_deleted = delete_class_sessions_result.rowcount
        logger.info(f"Deleted {class_sessions_deleted} class sessions")

        # 第二十六步：获取教师创建的课程ID（用于删除相关的表）
        lessons_result = await db.execute(
            select(Lesson.id).where(
                Lesson.creator_id.in_(user_ids)
            )
        )
        lesson_ids = [row[0] for row in lessons_result.all()]
        logger.info(f"Found {len(lesson_ids)} lessons created by users to delete")

        # 第二十七步：删除课程-班级关联（批量删除，虽然设置了CASCADE，但为了明确先删除）
        if lesson_ids:
            delete_lesson_classrooms_result = await db.execute(
                delete(LessonClassroom).where(
                    LessonClassroom.lesson_id.in_(lesson_ids)
                )
            )
            lesson_classrooms_deleted = delete_lesson_classrooms_result.rowcount
        else:
            lesson_classrooms_deleted = 0
        logger.info(f"Deleted {lesson_classrooms_deleted} lesson classrooms")

        # 第二十八步：删除课程的Cell（批量删除，因为Cell没有CASCADE设置）
        if lesson_ids:
            delete_cells_result = await db.execute(
                delete(Cell).where(
                    Cell.lesson_id.in_(lesson_ids)
                )
            )
            cells_deleted = delete_cells_result.rowcount
        else:
            cells_deleted = 0
        logger.info(f"Deleted {cells_deleted} cells")

        # 第二十九步：删除课程（教师创建的课程，批量删除）
        delete_lessons_result = await db.execute(
            delete(Lesson).where(
                Lesson.creator_id.in_(user_ids)
            )
        )
        lessons_deleted = delete_lessons_result.rowcount
        logger.info(f"Deleted {lessons_deleted} lessons")

        # 使用flush确保操作执行但保持事务
        await db.flush()
        logger.info("Flushed all student-related data deletions")

        # 第三十步：批量删除用户（使用批量删除更高效）
        delete_users_result = await db.execute(
            delete(User).where(User.id.in_(user_ids))
        )
        deleted_count = delete_users_result.rowcount
        logger.info(f"Deleted {deleted_count} users")

        # 提交所有删除操作
        await db.commit()
        logger.info(f"Successfully committed batch delete of {deleted_count} users")

    except Exception as e:
        logger.error(f"Batch delete by filter failed: {str(e)}", exc_info=True)
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"批量删除失败: {str(e)}"
        )

    return {
        "message": f"成功删除 {deleted_count} 个用户",
        "deleted_count": deleted_count,
        "exam_mappings_deleted": mappings_deleted,
        "exam_room_students_deleted": room_students_deleted,
        "activity_submissions_deleted": activity_submissions_deleted,
        "peer_reviews_deleted": peer_reviews_deleted,
        "flowchart_snapshots_deleted": flowchart_snapshots_deleted,
        "session_participations_deleted": session_participations_deleted,
        "classroom_memberships_deleted": classroom_memberships_deleted,
        "attendance_entries_deleted": attendance_entries_deleted,
        "positive_behaviors_deleted": positive_behaviors_deleted,
        "discipline_records_deleted": discipline_records_deleted,
        "scores_deleted": scores_deleted,
        "formative_assessments_deleted": formative_assessments_deleted,
        "questions_deleted": questions_deleted,
        "student_projects_deleted": student_projects_deleted,
        "project_cells_deleted": project_cells_deleted,
        "favorites_deleted": favorites_deleted,
        "reviews_deleted": reviews_deleted,
        "question_votes_deleted": question_votes_deleted,
        "answers_deleted": answers_deleted,
        "group_memberships_deleted": group_memberships_deleted,
        "duty_assignments_deleted": duty_assignments_deleted,
        "teaching_assignments_deleted": teaching_assignments_deleted,
        "exam_proctors_deleted": exam_proctors_deleted,
        "class_sessions_deleted": class_sessions_deleted,
        "lessons_deleted": lessons_deleted,
        "lesson_classrooms_deleted": lesson_classrooms_deleted
    }


@router.patch("/{user_id}/toggle-status")
async def toggle_user_status(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Any:
    """切换用户状态（激活/禁用）"""

    # 不能禁用自己
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="不能禁用自己的账号")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    current_status = bool(getattr(user, "is_active"))
    setattr(user, "is_active", not current_status)
    await db.commit()

    updated_status = bool(getattr(user, "is_active"))
    return {
        "message": f"用户已{'启用' if updated_status else '禁用'}",
        "is_active": updated_status,
    }


@router.post("/{user_id}/reset-password")
async def reset_user_password(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Any:
    """重置用户密码"""

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 生成新密码（8位随机密码，包含字母和数字）
    alphabet = string.ascii_letters + string.digits
    new_password = "".join(secrets.choice(alphabet) for _ in range(8))
    setattr(user, "hashed_password", get_password_hash(new_password))

    await db.commit()

    return {
        "message": "密码重置成功",
        "password_length": len(new_password),
        "note": "新密码已生成，请通过安全渠道告知用户。密码不会在响应中返回。",
    }


@router.post("/batch-import")
async def batch_import_users(
    import_data: BatchImportRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Any:
    """批量导入用户"""

    created_user_ids: list[int] = []
    errors = []

    for i, user_data in enumerate(import_data.users):
        try:
            # 检查用户名是否已存在
            existing_user = await db.execute(
                select(User).where(User.username == user_data.username)
            )
            if existing_user.scalar_one_or_none():
                errors.append(f"第{i+1}行：用户名 {user_data.username} 已存在")
                continue

            # 检查邮箱是否已存在
            existing_email = await db.execute(
                select(User).where(User.email == user_data.email)
            )
            if existing_email.scalar_one_or_none():
                errors.append(f"第{i+1}行：邮箱 {user_data.email} 已存在")
                continue

            # 创建用户
            hashed_password = get_password_hash(user_data.password)
            scope_ids = await _validate_scope_ids(
                db,
                region_id=user_data.region_id,
                school_id=user_data.school_id,
                grade_id=user_data.grade_id,
                classroom_id=user_data.classroom_id,
            )
            # 确保 is_active 有默认值，如果为 None 则设为 True
            is_active = user_data.is_active if user_data.is_active is not None else True
            user = User(
                username=user_data.username,
                email=user_data.email,
                hashed_password=hashed_password,
                full_name=user_data.full_name,
                role=user_data.role,
                is_active=is_active,
                **scope_ids,
            )

            db.add(user)
            await db.flush()  # 获取ID但不提交
            created_user_ids.append(cast(int, user.id))

        except HTTPException as exc:
            errors.append(f"第{i+1}行：{exc.detail}")
        except Exception as e:
            errors.append(f"第{i+1}行：{str(e)}")

    await db.commit()

    created_users: list[UserResponse] = []
    if created_user_ids:
        result = await db.execute(
            _user_with_relations_query().where(User.id.in_(created_user_ids))
        )
        created_user_objs = result.scalars().all()
        # 按创建顺序排序
        created_users_map: dict[int, User] = {
            cast(int, user.id): user
            for user in created_user_objs
            if user.id is not None
        }
        for user_id in created_user_ids:
            user_obj = created_users_map.get(user_id)
            if user_obj:
                created_users.append(_serialize_user(user_obj))

    return {
        "message": f"批量导入完成，成功创建 {len(created_users)} 个用户",
        "created_users": created_users,
        "errors": errors,
        "success_count": len(created_users),
        "error_count": len(errors),
    }


@router.get("/export/template")
async def download_import_template(
    current_user: User = Depends(get_current_admin),
) -> Any:
    """下载批量导入模板"""

    # 返回CSV模板内容（中文字段，包含备注说明）
    template_content = (
        "学号/用户名,姓名,邮箱,密码,角色,是否激活,区域ID(可选),学校ID(可选),年级ID(可选),班级ID(可选),备注\n"
    )
    template_content += "202301001,张慧,student01@example.com,student123,学生,是,1,101,3,1001,学生账户请填写学号作为登录名\n"
    template_content += (
        "teacher01,李老师,teacher01@example.com,teacher123,教师,是,,,,,教师/管理员可留空组织信息\n"
    )

    return {
        "template": template_content,
        "filename": "user_import_template.csv",
        "note": (
            "请按照模板格式填写用户信息，角色支持：管理员、教研员、教师、学生（或对应英文缩写）；"
            "学生账号的“学号/用户名”需使用学号；“是否激活”可填写 是/否 或 true/false；"
            "组织信息字段可留空，若填写请使用系统中的数值ID。"
        ),
    }


@router.get("/export/unified-template")
async def download_unified_import_template(
    current_user: User = Depends(get_current_admin),
) -> Any:
    """下载统一导入模板（支持创建用户和添加到班级）"""
    
    # 统一模板包含所有字段，添加详细的说明注释
    template_content = "# 统一数据导入模板\n"
    template_content += "# 说明：本模板支持一次导入完成用户创建和班级成员添加\n"
    template_content += "# \n"
    template_content += "# 【重要】组织架构ID获取方式：\n"
    template_content += "# \n"
    template_content += "# 1. 区域ID、学校ID、班级ID：\n"
    template_content += "#    访问路径：管理员后台 -> 组织架构管理\n"
    template_content += "#    在这些页面中，每个组织单位的ID会显示在列表中（通常在表格的第一列）\n"
    template_content += "#    班级ID说明：\n"
    template_content += "#      - 班级ID是数据库中的数字ID，需要在组织架构管理页面的班级列表中查看\n"
    template_content += "#      - 班级编码（code）格式为\"入学年份+班级编号\"，例如：202501（表示2025年入学的01班）\n"
    template_content += "#      - 导入时填写的是班级ID（数字），不是班级编码\n"
    template_content += "#      - 班级编码仅用于显示和识别，不能用作导入时的ID\n"
    template_content += "# \n"
    template_content += "# 2. 年级ID（重要说明）：\n"
    template_content += "#    方法一：访问 管理员后台 -> 课程管理 页面，在课程树结构中查看年级信息\n"
    template_content += "#    方法二：在组织架构管理 -> 创建/编辑班级时，年级下拉框中显示\"年级名称 (ID: 年级ID)\"格式\n"
    template_content += "#    方法三：系统标准年级ID对应关系（按顺序递增）：\n"
    template_content += "#            一年级→ID:1, 二年级→ID:2, 三年级→ID:3, 四年级→ID:4, 五年级→ID:5, 六年级→ID:6\n"
    template_content += "#            七年级→ID:7, 八年级→ID:8, 九年级→ID:9, 高一→ID:10, 高二→ID:11, 高三→ID:12, 未分类→ID:13\n"
    template_content += "#    提示：年级ID从1开始按顺序递增，与年级级别（level）基本一致\n"
    template_content += "# \n"
    template_content += "# 3. 如果组织架构尚未建立，请先到'组织架构管理'页面创建相应的区域、学校、班级\n"
    template_content += "#    注意：年级信息通常在课程系统中管理，而非组织架构管理中\n"
    template_content += "# \n"
    template_content += "# 4. 组织架构ID为数字，例如：区域ID=1, 学校ID=101, 年级ID=3, 班级ID=5（数据库数字ID）\n"
    template_content += "#    注意：班级ID是数据库中的数字ID（如：5），不是班级编码（如：202501）\n"
    template_content += "# 5. 这些字段为可选字段，如果用户不属于特定组织，可以留空\n"
    template_content += "# \n"
    template_content += "# 字段说明：\n"
    template_content += "# - 学籍号（推荐）：唯一标识，用于匹配已存在的用户，如果用户已存在则更新，不存在则创建\n"
    template_content += "# - 如果用户不存在，需要提供：学号/用户名、邮箱、密码\n"
    template_content += "# - 如果用户已存在，系统会根据学籍号/用户名/邮箱匹配并更新信息（密码可选）\n"
    template_content += "# - 如果提供了班级ID，系统会自动将用户添加到班级\n"
    template_content += "# - 角色可选值：管理员、教研员、教师、学生（或admin、researcher、teacher、student）\n"
    template_content += "# - 班级角色可选值：学生、正班主任、副班主任、任课教师、班干部\n"
    template_content += "# - 主班级：true/false，表示是否为主班级\n"
    template_content += "# - 是否激活：是/否 或 true/false\n"
    template_content += "# \n"
    template_content += "学籍号,学号/用户名,姓名,邮箱,密码,角色,是否激活,区域ID,学校ID,年级ID,班级ID,座号,班级角色,职务名称,主班级,班级学号\n"
    template_content += "2024001001,2024001,张三,zhangsan@example.com,123456,学生,是,1,101,3,5,1,学生,,true,2024001\n"
    template_content += ",teacher01,李老师,teacher01@example.com,123456,教师,是,1,101,,,,,任课教师,,,\n"
    
    return {
        "template": template_content,
        "filename": "unified_import_template.csv",
        "note": (
            "统一导入模板说明：\n\n"
            "【组织架构ID获取方式】\n"
            "区域ID、学校ID、年级ID、班级ID等组织架构ID可以通过以下方式获取：\n\n"
            "1. 区域ID、学校ID、班级ID：\n"
            "   访问路径：管理员后台 -> 组织架构管理页面\n"
            "   在组织架构管理页面中，每个组织单位的ID会显示在列表中（通常在表格的第一列）\n"
            "   班级ID说明：\n"
            "     - 班级ID是数据库中的数字ID，需要在组织架构管理页面的班级列表中查看\n"
            "     - 班级编码（code）格式为\"入学年份+班级编号\"，例如：202501（表示2025年入学的01班）\n"
            "     - 导入时填写的是班级ID（数字），不是班级编码\n"
            "     - 班级编码仅用于显示和识别，不能用作导入时的ID\n\n"
            "2. 年级ID（重要说明）：\n"
            "   方法一：访问 管理员后台 -> 课程管理 页面，在课程树结构中查看年级信息\n"
            "   方法二：在组织架构管理 -> 创建/编辑班级时，年级下拉框中显示\"年级名称 (ID: 年级ID)\"格式\n"
            "   方法三：系统标准年级ID对应关系（按顺序递增）：\n"
            "           一年级→ID:1, 二年级→ID:2, 三年级→ID:3, 四年级→ID:4, 五年级→ID:5, 六年级→ID:6\n"
            "           七年级→ID:7, 八年级→ID:8, 九年级→ID:9, 高一→ID:10, 高二→ID:11, 高三→ID:12, 未分类→ID:13\n"
            "   提示：年级ID从1开始按顺序递增，与年级级别（level）基本一致\n"
            "   注意：年级信息通常在课程系统中管理，而非组织架构管理中\n\n"
            "3. 如果组织架构尚未建立，请先到组织架构管理页面创建相应的区域、学校、班级\n"
            "4. 这些字段为可选字段，如果用户不属于特定组织，可以留空\n\n"
            "【字段说明】\n"
            "1. 学籍号（推荐）：唯一标识，用于匹配已存在的用户\n"
            "2. 如果用户不存在，系统会根据学号/用户名、邮箱、姓名创建新用户（需要提供密码）\n"
            "3. 如果用户已存在，系统会更新用户信息（密码可选）\n"
            "4. 如果提供了班级ID，系统会自动将用户添加到班级\n"
            "5. 角色可选值：管理员、教研员、教师、学生\n"
            "6. 班级角色可选值：学生、正班主任、副班主任、任课教师、班干部\n"
            "7. 主班级：true/false，表示是否为主班级\n"
            "8. 班级学号：班级内的学号，可能与学籍号不同"
        ),
    }


@router.post("/unified-import")
async def unified_import(
    import_data: UnifiedImportRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Any:
    """统一导入 - 支持创建用户和添加到班级"""
    
    from app.api.v1.classroom_assistant import find_user_by_identifiers
    from app.models.classroom_assistant import ClassroomMembership, RoleInClass
    
    created_users: List[UserResponse] = []
    added_members: List[dict] = []
    errors: List[str] = []
    
    for i, item in enumerate(import_data.items):
        try:
            # 1. 查找或创建用户
            user: Optional[User] = None
            
            # 尝试根据标识字段查找用户
            if item.student_id_number or item.username or item.email or item.full_name:
                user = await find_user_by_identifiers(
                    db,
                    student_id_number=item.student_id_number,
                    username=item.username,
                    email=item.email,
                    full_name=item.full_name,
                )
            
            if user:
                # 用户已存在，更新信息
                if item.full_name and item.full_name != user.full_name:
                    setattr(user, 'full_name', item.full_name)
                if item.email and item.email != user.email:
                    # 检查新邮箱是否已被使用
                    existing = await db.execute(
                        select(User).where(User.email == item.email, User.id != user.id)
                    )
                    if existing.scalar_one_or_none():
                        errors.append(f"第{i+1}行：邮箱 {item.email} 已被其他用户使用")
                        continue
                    setattr(user, 'email', item.email)
                if item.username and item.username != user.username:
                    # 检查新用户名是否已被使用
                    existing = await db.execute(
                        select(User).where(User.username == item.username, User.id != user.id)
                    )
                    if existing.scalar_one_or_none():
                        errors.append(f"第{i+1}行：用户名 {item.username} 已被其他用户使用")
                        continue
                    setattr(user, 'username', item.username)
                if item.student_id_number and item.student_id_number != user.student_id_number:
                    # 检查学籍号是否已被使用
                    if item.student_id_number:
                        existing = await db.execute(
                            select(User).where(
                                User.student_id_number == item.student_id_number,
                                User.id != user.id
                            )
                        )
                        if existing.scalar_one_or_none():
                            errors.append(f"第{i+1}行：学籍号 {item.student_id_number} 已被其他用户使用")
                            continue
                    setattr(user, 'student_id_number', item.student_id_number)
                if item.password:
                    setattr(user, 'hashed_password', get_password_hash(item.password))
                if item.role is not None:
                    setattr(user, 'role', item.role)
                if item.is_active is not None:
                    setattr(user, 'is_active', item.is_active)
                
                # 更新组织信息
                if item.region_id is not None or item.school_id is not None or \
                   item.grade_id is not None or item.classroom_id is not None:
                    scope_ids = await _validate_scope_ids(
                        db,
                        region_id=item.region_id,
                        school_id=item.school_id,
                        grade_id=item.grade_id,
                        classroom_id=item.classroom_id,
                    )
                    for key, value in scope_ids.items():
                        setattr(user, key, value)
                
                await db.flush()
            else:
                # 用户不存在，创建新用户
                if not item.username:
                    errors.append(f"第{i+1}行：创建新用户需要提供用户名/学号")
                    continue
                if not item.email:
                    errors.append(f"第{i+1}行：创建新用户需要提供邮箱")
                    continue
                if not item.password:
                    errors.append(f"第{i+1}行：创建新用户需要提供密码")
                    continue
                
                # 检查用户名和邮箱是否已存在
                existing_username = await db.execute(
                    select(User).where(User.username == item.username)
                )
                if existing_username.scalar_one_or_none():
                    errors.append(f"第{i+1}行：用户名 {item.username} 已存在")
                    continue
                
                existing_email = await db.execute(
                    select(User).where(User.email == item.email)
                )
                if existing_email.scalar_one_or_none():
                    errors.append(f"第{i+1}行：邮箱 {item.email} 已存在")
                    continue
                
                # 检查学籍号是否已存在
                if item.student_id_number:
                    existing_sid = await db.execute(
                        select(User).where(User.student_id_number == item.student_id_number)
                    )
                    if existing_sid.scalar_one_or_none():
                        errors.append(f"第{i+1}行：学籍号 {item.student_id_number} 已存在")
                        continue
                
                # 创建用户
                hashed_password = get_password_hash(item.password)
                scope_ids = await _validate_scope_ids(
                    db,
                    region_id=item.region_id,
                    school_id=item.school_id,
                    grade_id=item.grade_id,
                    classroom_id=item.classroom_id,
                )
                
                user = User(
                    username=item.username,
                    email=item.email,
                    hashed_password=hashed_password,
                    full_name=item.full_name,
                    student_id_number=item.student_id_number,
                    role=item.role if item.role is not None else UserRole.STUDENT,
                    is_active=item.is_active if item.is_active is not None else True,
                    **scope_ids,
                )
                
                db.add(user)
                await db.flush()
            
            # 2. 如果提供了班级ID，将用户添加到班级
            if item.classroom_id:
                classroom = await db.get(Classroom, item.classroom_id)
                if not classroom:
                    errors.append(f"第{i+1}行：班级 {item.classroom_id} 不存在")
                    continue
                
                # 检查是否已是成员
                existing_membership = await db.execute(
                    select(ClassroomMembership).where(
                        ClassroomMembership.classroom_id == item.classroom_id,
                        ClassroomMembership.user_id == user.id,
                    )
                )
                membership = existing_membership.scalar_one_or_none()
                
                # 解析班级角色
                role_in_class = RoleInClass.STUDENT
                if item.role_in_class:
                    role_map = {
                        "学生": RoleInClass.STUDENT,
                        "正班主任": RoleInClass.HEAD_TEACHER_PRIMARY,
                        "副班主任": RoleInClass.HEAD_TEACHER_DEPUTY,
                        "任课教师": RoleInClass.SUBJECT_TEACHER,
                        "班干部": RoleInClass.CADRE,
                    }
                    role_in_class = role_map.get(item.role_in_class, RoleInClass.STUDENT)
                
                if membership:
                    # 更新现有成员关系
                    if not bool(membership.is_active):
                        setattr(membership, 'is_active', True)
                    setattr(membership, 'role_in_class', role_in_class)
                    if item.seat_no is not None:
                        setattr(membership, 'seat_no', item.seat_no)
                    if item.cadre_title is not None:
                        setattr(membership, 'cadre_title', item.cadre_title)
                    if item.is_primary_class is not None:
                        setattr(membership, 'is_primary_class', item.is_primary_class)
                    if item.student_no is not None:
                        setattr(membership, 'student_no', item.student_no)
                    await db.flush()
                else:
                    # 创建新成员关系
                    membership = ClassroomMembership(
                        classroom_id=item.classroom_id,
                        user_id=user.id,
                        role_in_class=role_in_class,
                        seat_no=item.seat_no,
                        cadre_title=item.cadre_title,
                        is_primary_class=item.is_primary_class if item.is_primary_class is not None else False,
                        student_no=item.student_no,
                        is_active=True,
                    )
                    db.add(membership)
                    await db.flush()
                
                added_members.append({
                    "user_id": user.id,
                    "username": user.username,
                    "full_name": user.full_name,
                    "classroom_id": item.classroom_id,
                    "classroom_name": classroom.name if classroom else None,
                })
            
            # 记录创建的用户
            if user.id not in [u.id for u in created_users]:
                result = await db.execute(
                    _user_with_relations_query().where(User.id == user.id)
                )
                user_obj = result.scalar_one_or_none()
                if user_obj:
                    created_users.append(_serialize_user(user_obj))
            
        except HTTPException as exc:
            errors.append(f"第{i+1}行：{exc.detail}")
        except Exception as e:
            errors.append(f"第{i+1}行：{str(e)}")
    
    await db.commit()
    
    return UnifiedImportResponse(
        message=f"统一导入完成，成功创建/更新 {len(created_users)} 个用户，添加到班级 {len(added_members)} 个成员",
        created_users=created_users,
        added_members=added_members,
        errors=errors,
        success_count=len(created_users) + len(added_members),
        error_count=len(errors),
        created_user_count=len(created_users),
        added_member_count=len(added_members),
    )


@router.get("/check-username")
async def check_username_availability(
    school_code: str = Query(..., description="4-digit school code"),
    student_id_number: str = Query(..., description="18-digit student ID number"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Any:
    """
    Check username availability and generate username

    Args:
        school_code: 4-digit school code
        student_id_number: 18-digit student ID number

    Returns:
        - available: boolean - whether the username is available
        - username: generated username
        - conflicts: list of conflicting usernames (if any)

    Example:
        GET /api/v1/admin/users/check-username?school_code=4401&student_id_number=110101200501011234

        Response:
        {
            "available": true,
            "username": "4401011234",
            "conflicts": []
        }
    """
    from app.utils.username_generator import generate_username

    username = generate_username(school_code, student_id_number)

    # Check if username already exists
    existing = await db.execute(
        select(User).where(User.username == username)
    ).scalar_one_or_none()

    conflicts = []
    if existing:
        conflicts.append(username)

    return {
        "available": len(conflicts) == 0,
        "username": username,
        "conflicts": conflicts
    }
