"""
Tests for multi-classroom student support in lessons API
"""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import User, Classroom, Lesson, LessonStatus, LessonClassroom, ClassroomMembership, RoleInClass
from fastapi import testclient


@pytest.mark.asyncio
async def test_student_sees_lessons_from_multiple_classrooms(
    db: AsyncSession,
    auth_client: testclient.TestClient,
    student_user: User,
    classroom: Classroom,
    school,
):
    """Students should see lessons from all classrooms they're members of"""
    # Create a second classroom in the same school
    from app.models import Grade
    grade = await db.execute(select(Grade).where(Grade.id == classroom.grade_id))
    grade_obj = grade.scalar_one()

    classroom2 = Classroom(
        name="Second Class",
        school_id=classroom.school_id,
        grade_id=grade_obj.id,
        is_active=True
    )
    db.add(classroom2)
    await db.flush()

    # Add student to both classrooms via ClassroomMembership
    membership1 = ClassroomMembership(
        classroom_id=classroom.id,
        user_id=student_user.id,
        role_in_class=RoleInClass.STUDENT,
        is_active=True
    )
    membership2 = ClassroomMembership(
        classroom_id=classroom2.id,
        user_id=student_user.id,
        role_in_class=RoleInClass.STUDENT,
        is_active=True
    )
    db.add_all([membership1, membership2])
    await db.commit()

    # Create a teacher user for lessons
    teacher = User(
        email="multiclass_teacher@test.com",
        full_name="Multi Class Teacher",
        role="teacher",
        school_id=classroom.school_id,
        is_active=True
    )
    db.add(teacher)
    await db.flush()

    # Create lessons for each classroom
    from app.models import Course, Subject
    subject = Subject(name="Test Subject", code="TEST", school_id=classroom.school_id)
    db.add(subject)
    await db.flush()

    course = Course(
        name="Test Course",
        subject_id=subject.id,
        grade_id=grade_obj.id,
        school_id=classroom.school_id,
        is_active=True
    )
    db.add(course)
    await db.flush()

    lesson1 = Lesson(
        title="Lesson 1",
        creator_id=teacher.id,
        course_id=course.id,
        status=LessonStatus.PUBLISHED,
        content=[]
    )
    lesson2 = Lesson(
        title="Lesson 2",
        creator_id=teacher.id,
        course_id=course.id,
        status=LessonStatus.PUBLISHED,
        content=[]
    )
    db.add_all([lesson1, lesson2])
    await db.flush()

    lc1 = LessonClassroom(lesson_id=lesson1.id, classroom_id=classroom.id)
    lc2 = LessonClassroom(lesson_id=lesson2.id, classroom_id=classroom2.id)
    db.add_all([lc1, lc2])
    await db.commit()

    # Student should see both lessons
    response = auth_client.get("/api/v1/lessons/")

    assert response.status_code == 200
    data = response.json()
    lesson_ids = [item["id"] for item in data["items"]]

    assert lesson1.id in lesson_ids
    assert lesson2.id in lesson_ids
