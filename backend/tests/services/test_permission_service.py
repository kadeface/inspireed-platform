"""
Tests for PermissionService - centralized permission checking
"""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    User, UserRole, Classroom, ClassroomMembership, RoleInClass,
    Lesson, LessonStatus, LessonClassroom, Subject, Course, Chapter
)


@pytest.fixture(scope="function")
async def db(async_session: AsyncSession):
    """Database session fixture."""
    return async_session


@pytest.fixture(scope="function")
async def school(db: AsyncSession):
    """Create a test school."""
    from app.models import Region

    region = Region(name="Test Region", code="TEST", level=3)
    db.add(region)
    await db.flush()

    school = Region(name="Test School", code="SCH001", level=3)  # Using Region as School for simplicity
    db.add(school)
    await db.flush()
    return school


@pytest.fixture(scope="function")
async def teacher(db: AsyncSession, school):
    """Create a teacher user."""
    teacher = User(
        username="teacher1",
        email="teacher1@test.com",
        hashed_password="hash",
        role=UserRole.TEACHER,
        school_id=school.id,
    )
    db.add(teacher)
    await db.flush()
    return teacher


@pytest.fixture(scope="function")
async def classroom(db: AsyncSession, school):
    """Create a test classroom."""
    classroom = Classroom(name="Test Class", school_id=school.id, grade_id=1)
    db.add(classroom)
    await db.flush()
    return classroom


@pytest.fixture(scope="function")
async def student(db: AsyncSession, school):
    """Create a student user."""
    student = User(
        username="student1",
        email="student1@test.com",
        hashed_password="hash",
        role=UserRole.STUDENT,
        school_id=school.id,
        classroom_id=1,  # Default classroom ID
    )
    db.add(student)
    await db.flush()
    return student


@pytest.fixture(scope="function")
async def lesson(db: AsyncSession):
    """Create a test lesson."""
    from app.models import Subject, Course, Chapter

    subject = Subject(name="Math", code="MATH")
    db.add(subject)
    await db.flush()

    course = Course(name="Math Course", subject_id=subject.id, grade_id=1, is_active=True)
    db.add(course)
    await db.flush()

    chapter = Chapter(name="Test Chapter", course_id=course.id, is_active=True)
    db.add(chapter)
    await db.flush()

    lesson = Lesson(
        title="Test Lesson",
        description="Test Description",
        creator_id=1,
        course_id=course.id,
        chapter_id=chapter.id,
        content=[],
        status=LessonStatus.PUBLISHED,
    )
    db.add(lesson)
    await db.flush()
    return lesson


@pytest.mark.asyncio
async def test_teacher_can_publish_with_head_teacher_membership(
    db: AsyncSession, teacher: User, classroom: Classroom
):
    """Teacher can publish if they have HEAD_TEACHER_PRIMARY membership."""
    from app.services.permission_service import PermissionService

    # Create head teacher membership
    membership = ClassroomMembership(
        user_id=teacher.id,
        classroom_id=classroom.id,
        role_in_class=RoleInClass.HEAD_TEACHER_PRIMARY,
        is_active=True,
    )
    db.add(membership)
    await db.commit()

    service = PermissionService()
    result = await service.can_teacher_publish_to_classroom(db, teacher, classroom)

    assert result is True


@pytest.mark.asyncio
async def test_teacher_can_publish_with_subject_teacher_membership(
    db: AsyncSession, teacher: User, classroom: Classroom
):
    """Teacher can publish if they have SUBJECT_TEACHER membership."""
    from app.services.permission_service import PermissionService

    # Create subject teacher membership
    membership = ClassroomMembership(
        user_id=teacher.id,
        classroom_id=classroom.id,
        role_in_class=RoleInClass.SUBJECT_TEACHER,
        is_active=True,
    )
    db.add(membership)
    await db.commit()

    service = PermissionService()
    result = await service.can_teacher_publish_to_classroom(db, teacher, classroom)

    assert result is True


@pytest.mark.asyncio
async def test_teacher_can_publish_with_school_id_fallback(
    db: AsyncSession, teacher: User, classroom: Classroom
):
    """Teacher can publish if they belong to the same school."""
    from app.services.permission_service import PermissionService

    service = PermissionService()
    result = await service.can_teacher_publish_to_classroom(db, teacher, classroom)

    assert result is True


@pytest.mark.asyncio
async def test_teacher_cannot_publish_without_membership_or_school(
    db: AsyncSession, classroom: Classroom
):
    """Teacher cannot publish without membership or matching school."""
    from app.models import Region

    # Create different school
    other_region = Region(name="Other School", code="OTHER", level=3)
    db.add(other_region)
    await db.flush()

    other_teacher = User(
        username="other_teacher",
        email="other@test.com",
        hashed_password="hash",
        role=UserRole.TEACHER,
        school_id=other_region.id,
    )
    db.add(other_teacher)
    await db.flush()

    from app.services.permission_service import PermissionService

    service = PermissionService()
    result = await service.can_teacher_publish_to_classroom(db, other_teacher, classroom)

    assert result is False


@pytest.mark.asyncio
async def test_teacher_cannot_publish_with_inactive_membership(
    db: AsyncSession, teacher: User, classroom: Classroom
):
    """Teacher cannot publish with inactive membership."""
    from app.services.permission_service import PermissionService

    # Create inactive head teacher membership
    membership = ClassroomMembership(
        user_id=teacher.id,
        classroom_id=classroom.id,
        role_in_class=RoleInClass.HEAD_TEACHER_PRIMARY,
        is_active=False,
    )
    db.add(membership)
    await db.commit()

    service = PermissionService()
    result = await service.can_teacher_publish_to_classroom(db, teacher, classroom)

    assert result is False


@pytest.mark.asyncio
async def test_student_can_view_lesson_with_membership(
    db: AsyncSession, student: User, lesson: Classroom, lesson_id: lesson.id
):
    """Student can view lesson if they have membership and lesson is published."""
    from app.services.permission_service import PermissionService

    # Create student membership
    membership = ClassroomMembership(
        user_id=student.id,
        classroom_id=lesson_id,
        role_in_class=RoleInClass.STUDENT,
        is_active=True,
    )
    db.add(membership)

    # Create lesson assignment
    lesson_assignment = LessonClassroom(
        lesson_id=lesson_id,
        classroom_id=lesson_id,
    )
    db.add(lesson_assignment)
    await db.commit()

    service = PermissionService()
    result = await service.can_student_view_lesson(db, student, lesson_id)

    assert result is True


@pytest.mark.asyncio
async def test_student_cannot_view_unpublished_lesson(
    db: AsyncSession, student: User, lesson: Classroom, lesson_id: lesson.id
):
    """Student cannot view unpublished lesson."""
    from app.services.permission_service import PermissionService

    # Create student membership
    membership = ClassroomMembership(
        user_id=student.id,
        classroom_id=lesson_id,
        role_in_class=RoleInClass.STUDENT,
        is_active=True,
    )
    db.add(membership)

    # Create lesson assignment but set to DRAFT status
    lesson_assignment = LessonClassroom(
        lesson_id=lesson_id,
        classroom_id=lesson_id,
    )
    db.add(lesson_assignment)

    # Update lesson to DRAFT status
    lesson.status = LessonStatus.DRAFT
    await db.commit()

    service = PermissionService()
    result = await service.can_student_view_lesson(db, student, lesson_id)

    assert result is False


@pytest.mark.asyncio
async def test_student_cannot_view_lesson_without_membership(
    db: AsyncSession, student: User, lesson: Classroom, lesson_id: lesson.id
):
    """Student cannot view lesson if they don't have membership."""
    from app.services.permission_service import PermissionService

    # Create lesson assignment
    lesson_assignment = LessonClassroom(
        lesson_id=lesson_id,
        classroom_id=lesson_id,
    )
    db.add(lesson_assignment)
    await db.commit()

    service = PermissionService()
    result = await service.can_student_view_lesson(db, student, lesson_id)

    assert result is False


@pytest.mark.asyncio
async def test_student_cannot_view_lesson_without_memberships(
    db: AsyncSession, student: User, lesson: Classroom, lesson_id: lesson.id
):
    """Student cannot view lesson if they have no memberships at all."""
    from app.services.permission_service import PermissionService

    # Create lesson assignment
    lesson_assignment = LessonClassroom(
        lesson_id=lesson_id,
        classroom_id=lesson_id,
    )
    db.add(lesson_assignment)
    await db.commit()

    service = PermissionService()
    result = await service.can_student_view_lesson(db, student, lesson_id)

    assert result is False


@pytest.mark.asyncio
async def test_student_cannot_view_lesson_from_different_classroom(
    db: AsyncSession, student: User, lesson: Classroom, lesson_id: lesson.id
):
    """Student cannot view lesson assigned to a different classroom."""
    from app.services.permission_service import PermissionService

    # Create student membership for different classroom
    membership = ClassroomMembership(
        user_id=student.id,
        classroom_id=2,  # Different classroom
        role_in_class=RoleInClass.STUDENT,
        is_active=True,
    )
    db.add(membership)

    # Create lesson assignment for original classroom
    lesson_assignment = LessonClassroom(
        lesson_id=lesson_id,
        classroom_id=lesson_id,
    )
    db.add(lesson_assignment)
    await db.commit()

    service = PermissionService()
    result = await service.can_student_view_lesson(db, student, lesson_id)

    assert result is False