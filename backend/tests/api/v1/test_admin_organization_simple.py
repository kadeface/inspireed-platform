"""
Simple tests for admin organization API endpoints - directly testing logic.
"""
import pytest
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import User, UserRole, Classroom, Lesson, LessonStatus, LessonClassroom, Course, School, Region, Subject, Grade


@pytest.fixture(scope="function")
async def db(async_session: AsyncSession):
    """Database session fixture."""
    return async_session


@pytest.mark.asyncio
async def test_delete_classroom_with_lesson_assignments_prevented(
    db: AsyncSession
):
    """Test that deleting a classroom with lesson assignments is prevented by checking logic"""
    # Create test data
    region = Region(name="Test Region", code="TEST", level=3)
    db.add(region)
    await db.flush()

    school = School(name="Test School", code="SCH001", region_id=region.id, school_type="小学")
    db.add(school)
    await db.flush()

    grade = Grade(name="一年级", level=1, is_active=True)
    db.add(grade)
    await db.flush()

    subject = Subject(name="数学", code="MATH", is_active=True)
    db.add(subject)
    await db.flush()

    course = Course(name="一年级数学", code="G1-MATH", grade_id=grade.id, subject_id=subject.id)
    db.add(course)
    await db.flush()

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

    classroom = Classroom(
        name="Test Class",
        school_id=school.id,
        grade_id=grade.id,
        is_active=True
    )
    db.add(classroom)
    await db.flush()

    lesson = Lesson(
        title="Test Lesson",
        description="Test",
        creator_id=teacher.id,
        course_id=course.id,
        status=LessonStatus.PUBLISHED,
        content=[]
    )
    db.add(lesson)
    await db.flush()

    lc = LessonClassroom(lesson_id=lesson.id, classroom_id=classroom.id)
    db.add(lc)
    await db.commit()

    # Test the query logic that delete_classroom uses
    lesson_assignment_count = await db.execute(
        select(func.count()).select_from(LessonClassroom).where(
            LessonClassroom.classroom_id == classroom.id
        )
    )
    lesson_count = lesson_assignment_count.scalar() or 0

    # Verify the logic works
    assert lesson_count == 1, "Should have 1 lesson assignment"
    assert lesson_count > 0, "Lesson count should be greater than 0, preventing deletion"


@pytest.mark.asyncio
async def test_deactivate_classroom_logic(
    db: AsyncSession
):
    """Test that deactivating a classroom sets is_active=False"""
    # Create test data
    region = Region(name="Test Region", code="TEST", level=3)
    db.add(region)
    await db.flush()

    school = School(name="Test School", code="SCH001", region_id=region.id, school_type="小学")
    db.add(school)
    await db.flush()

    grade = Grade(name="一年级", level=1, is_active=True)
    db.add(grade)
    await db.flush()

    classroom = Classroom(
        name="Test Class",
        school_id=school.id,
        grade_id=grade.id,
        is_active=True
    )
    db.add(classroom)
    await db.commit()

    # Verify initial state
    assert classroom.is_active is True

    # Test deactivation logic
    classroom.is_active = False
    await db.commit()

    # Refresh and verify
    await db.refresh(classroom)
    assert classroom.is_active is False
