"""
Tests for admin organization API endpoints.
"""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import testclient
from httpx import AsyncClient
from app.models import User, UserRole, Classroom, Lesson, LessonStatus, LessonClassroom, Course, School, Region, Subject, Grade


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
async def admin_user(db: AsyncSession, school: School):
    """Create an admin user."""
    admin = User(
        username="admin1",
        email="admin1@test.com",
        hashed_password="hash",
        role=UserRole.ADMIN,
        school_id=school.id,
        is_active=True
    )
    db.add(admin)
    await db.flush()
    return admin


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
async def grade(db: AsyncSession):
    """Create a test grade."""
    grade = Grade(name="一年级", level=1, is_active=True)
    db.add(grade)
    await db.flush()
    return grade


@pytest.fixture(scope="function")
async def subject(db: AsyncSession):
    """Create a test subject."""
    subject = Subject(name="数学", code="MATH", is_active=True)
    db.add(subject)
    await db.flush()
    return subject


@pytest.fixture(scope="function")
async def course(db: AsyncSession, grade: Grade, subject: Subject):
    """Create a test course."""
    course = Course(
        name="一年级数学",
        code="G1-MATH",
        grade_id=grade.id,
        subject_id=subject.id
    )
    db.add(course)
    await db.flush()
    return course


@pytest.fixture(scope="function")
async def classroom(db: AsyncSession, school: School, grade: Grade):
    """Create a test classroom."""
    classroom = Classroom(
        name="Test Class 1",
        school_id=school.id,
        grade_id=grade.id,
        is_active=True
    )
    db.add(classroom)
    await db.flush()
    return classroom


@pytest.mark.asyncio
async def test_delete_classroom_with_lesson_assignments_fails(
    db: AsyncSession,
    classroom: Classroom,
    course: Course,
    teacher_user: User,
):
    """Deleting a classroom with lesson assignments should fail"""
    from unittest.mock import Mock
    from app.api.v1.admin_organization import delete_classroom
    from fastapi import HTTPException

    # Create a lesson
    lesson = Lesson(
        title="Test Lesson",
        description="Test",
        creator_id=teacher_user.id,
        course_id=course.id,
        status=LessonStatus.PUBLISHED,
        content=[]
    )
    db.add(lesson)
    await db.flush()

    # Assign lesson to classroom
    lc = LessonClassroom(lesson_id=lesson.id, classroom_id=classroom.id)
    db.add(lc)
    await db.commit()

    # Create a mock admin user (the function checks for admin permissions)
    mock_admin = Mock(spec=User)
    mock_admin.role = UserRole.ADMIN
    mock_admin.id = 999

    # Try to delete classroom - should raise HTTPException
    try:
        await delete_classroom(
            classroom_id=classroom.id,
            db=db,
            current_user=mock_admin
        )
        # If we get here, the exception was not raised
        assert False, "Expected HTTPException to be raised"
    except HTTPException as exc:
        # This is what we expect
        assert exc.status_code == 400
        assert "lesson" in str(exc.detail).lower()


@pytest.mark.asyncio
async def test_deactivate_classroom_preserves_lesson_assignments(
    db: AsyncSession,
    classroom: Classroom,
    course: Course,
    teacher_user: User,
):
    """Deactivating a classroom should preserve lesson assignments"""
    from unittest.mock import Mock
    from app.api.v1.admin_organization import deactivate_classroom

    # Create a lesson
    lesson = Lesson(
        title="Test Lesson",
        description="Test",
        creator_id=teacher_user.id,
        course_id=course.id,
        status=LessonStatus.PUBLISHED,
        content=[]
    )
    db.add(lesson)
    await db.flush()

    # Assign lesson to classroom
    lc = LessonClassroom(lesson_id=lesson.id, classroom_id=classroom.id)
    db.add(lc)
    await db.commit()

    # Create a mock admin user
    mock_admin = Mock(spec=User)
    mock_admin.role = UserRole.ADMIN
    mock_admin.id = 999

    # Deactivate classroom
    result = await deactivate_classroom(
        classroom_id=classroom.id,
        db=db,
        current_user=mock_admin
    )

    assert result["lesson_assignments_preserved"] is True

    # Verify lesson assignment still exists
    lesson_result = await db.execute(
        select(LessonClassroom).where(
            LessonClassroom.lesson_id == lesson.id,
            LessonClassroom.classroom_id == classroom.id
        )
    )
    assert lesson_result.scalar_one_or_none() is not None

    # Verify classroom is deactivated
    await db.refresh(classroom)
    assert classroom.is_active is False
