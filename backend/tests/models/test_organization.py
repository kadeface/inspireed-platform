import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import Classroom, ClassroomMembership, RoleInClass, User, UserRole, School, Region, Grade


@pytest.fixture(scope="function")
async def db(async_session: AsyncSession):
    """Database session fixture."""
    return async_session


@pytest.fixture(scope="function")
async def region(db: AsyncSession):
    """Create a test region."""
    region = Region(name="Test Region", code="TEST", level=3)
    db.add(region)
    await db.flush()
    return region


@pytest.fixture(scope="function")
async def school(db: AsyncSession, region: Region):
    """Create a test school."""
    school = School(name="Test School", code="SCH001", region_id=region.id, school_type="小学")
    db.add(school)
    await db.flush()
    return school


@pytest.fixture(scope="function")
async def teacher_user(db: AsyncSession, school: School):
    """Create a teacher user."""
    teacher = User(
        username="teacher1",
        email="teacher1@test.com",
        hashed_password="hash",
        role=UserRole.TEACHER,
        school_id=school.id,
        is_active=True
    )
    db.add(teacher)
    await db.flush()
    return teacher


@pytest.fixture(scope="function")
async def another_teacher_user(db: AsyncSession, school: School):
    """Create another teacher user."""
    teacher = User(
        username="teacher2",
        email="teacher2@test.com",
        hashed_password="hash",
        role=UserRole.TEACHER,
        school_id=school.id,
        is_active=True
    )
    db.add(teacher)
    await db.flush()
    return teacher


@pytest.fixture(scope="function")
async def grade(db: AsyncSession):
    """Create a test grade."""
    grade = Grade(name="一年级", level=1, is_active=True)
    db.add(grade)
    await db.flush()
    return grade


@pytest.fixture(scope="function")
async def classroom(db: AsyncSession, school: School, grade: Grade):
    """Create a test classroom."""
    classroom = Classroom(
        name="Test Class 1",
        grade_id=grade.id,
        school_id=school.id,
        enrollment_year=2025
    )
    db.add(classroom)
    await db.flush()
    return classroom


@pytest.mark.asyncio
async def test_classroom_head_teacher_from_membership(
    db: AsyncSession, classroom: Classroom, teacher_user: User
):
    """Classroom.get_head_teacher() should use ClassroomMembership"""
    # Add head teacher via ClassroomMembership
    membership = ClassroomMembership(
        classroom_id=classroom.id,
        user_id=teacher_user.id,
        role_in_class=RoleInClass.HEAD_TEACHER_PRIMARY,
        is_active=True
    )
    db.add(membership)
    await db.commit()

    # The method should find the head teacher
    head_teacher = await classroom.get_head_teacher(db)
    assert head_teacher is not None
    assert head_teacher.id == teacher_user.id

@pytest.mark.asyncio
async def test_classroom_deputy_head_teacher_from_membership(
    db: AsyncSession, classroom: Classroom, teacher_user: User
):
    """Classroom.get_deputy_head_teacher() should use ClassroomMembership"""
    membership = ClassroomMembership(
        classroom_id=classroom.id,
        user_id=teacher_user.id,
        role_in_class=RoleInClass.HEAD_TEACHER_DEPUTY,
        is_active=True
    )
    db.add(membership)
    await db.commit()

    deputy = await classroom.get_deputy_head_teacher(db)
    assert deputy is not None
    assert deputy.id == teacher_user.id

@pytest.mark.asyncio
async def test_classroom_get_teachers(
    db: AsyncSession, classroom: Classroom, teacher_user: User, another_teacher_user: User
):
    """Classroom.get_teachers() should return all teachers via ClassroomMembership"""
    # Add multiple teachers
    membership1 = ClassroomMembership(
        classroom_id=classroom.id,
        user_id=teacher_user.id,
        role_in_class=RoleInClass.HEAD_TEACHER_PRIMARY,
        is_active=True
    )
    membership2 = ClassroomMembership(
        classroom_id=classroom.id,
        user_id=another_teacher_user.id,
        role_in_class=RoleInClass.SUBJECT_TEACHER,
        is_active=True
    )
    db.add_all([membership1, membership2])
    await db.commit()

    teachers = await classroom.get_teachers(db)
    assert len(teachers) == 2
    teacher_ids = {t.id for t in teachers}
    assert teacher_user.id in teacher_ids
    assert another_teacher_user.id in teacher_ids

@pytest.mark.asyncio
async def test_classroom_head_teacher_none_when_no_membership(
    db: AsyncSession, classroom: Classroom
):
    """get_head_teacher should return None when no membership exists"""
    head_teacher = await classroom.get_head_teacher(db)
    assert head_teacher is None
