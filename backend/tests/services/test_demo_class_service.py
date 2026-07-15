"""
Tests for DemoClassService (provision idempotency, conflict pre-scan, reset
scoping) and the two places that consume it: the demo-classroom permission
bypass (PermissionService) and the teacher classroom-list injection
(ClassroomQueryService).
"""
from __future__ import annotations

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    Classroom,
    ClassroomMembership,
    Grade,
    RoleInClass,
    School,
    User,
    UserRole,
)


@pytest.fixture(scope="function")
async def db(async_session: AsyncSession):
    """Database session fixture."""
    return async_session


@pytest.fixture(scope="function")
async def grade(db: AsyncSession):
    """The grade DemoClassService.provision() requires to exist."""
    from app.services.demo_class import DEMO_GRADE_NAME

    grade = Grade(name=DEMO_GRADE_NAME, level=10)
    db.add(grade)
    await db.flush()
    return grade


@pytest.fixture(scope="function")
async def other_school(db: AsyncSession):
    """A non-DEMO school, used to create username conflicts."""
    from app.models import Region

    region = Region(name="Other Region", code="OTHERRG", level=1)
    db.add(region)
    await db.flush()

    school = School(
        name="Other School", code="OTHER", region_id=region.id, school_type="高中"
    )
    db.add(school)
    await db.flush()
    return school


@pytest.fixture(autouse=True)
def small_demo_account_count(monkeypatch):
    """Reduce DEMO_ACCOUNT_COUNT from 60 -> 1 for test speed and to sidestep
    an unrelated, pre-existing bug in the test DB dialect.

    Two independent reasons make a reduced count the right call here (per
    the task brief: "a reduced-path test ... is enough if you document the
    limit"):

    1. Each newly-created demo account is bcrypt-hashed, so provisioning all
       60 accounts is slow to run repeatedly.
    2. `ClassroomMembership`'s partial unique index
       (`uq_classroom_head_teacher`, restricted via `postgresql_where` to
       `role_in_class = 'head_teacher_primary'`) has no `sqlite_where`
       counterpart, so on the SQLite test engine it silently becomes a full
       unique index on `classroom_id` alone — i.e. at most one
       ClassroomMembership row can exist per classroom in this test DB,
       regardless of role. That's a pre-existing model/test-infra gap
       unrelated to Demo Class and out of scope to fix here, so tests below
       are written to never need two simultaneous membership rows in the
       same classroom.
    """
    import app.services.demo_class as demo_class_module

    monkeypatch.setattr(demo_class_module, "DEMO_ACCOUNT_COUNT", 1)


@pytest.mark.asyncio
async def test_provision_creates_school_classroom_and_accounts(
    db: AsyncSession, grade: Grade
):
    from app.services.demo_class import DemoClassService, all_demo_usernames

    service = DemoClassService()
    result = await service.provision(db)

    assert result["created_users"] == len(all_demo_usernames())
    assert result["skipped_users"] == 0
    assert result["conflicts"] == []

    classroom = await service.resolve_demo_classroom(db)
    assert classroom is not None
    assert classroom.id == result["classroom_id"]


@pytest.mark.asyncio
async def test_provision_is_idempotent(db: AsyncSession, grade: Grade):
    """Running provision() twice must not create duplicate users/memberships."""
    from app.services.demo_class import DemoClassService, all_demo_usernames

    service = DemoClassService()
    first = await service.provision(db)
    await db.commit()

    second = await service.provision(db)

    assert second["created_users"] == 0
    assert second["skipped_users"] == len(all_demo_usernames())
    assert second["school_id"] == first["school_id"]
    assert second["classroom_id"] == first["classroom_id"]

    # No duplicate memberships were created on the second pass.
    result = await db.execute(
        select(ClassroomMembership).where(
            ClassroomMembership.classroom_id == second["classroom_id"]
        )
    )
    memberships = result.scalars().all()
    assert len(memberships) == len(all_demo_usernames())

    # No duplicate users were created either.
    result = await db.execute(
        select(User).where(User.username.in_(all_demo_usernames()))
    )
    assert len(result.scalars().all()) == len(all_demo_usernames())


@pytest.mark.asyncio
async def test_provision_conflict_prescan_raises_without_writing(
    db: AsyncSession, grade: Grade, other_school: School
):
    """A username conflict must be detected up front, before any DEMO
    school/classroom/account is written."""
    from app.services.demo_class import DemoClassService, demo_username

    conflicting_username = demo_username(1)  # "st01"
    conflicting_user = User(
        email="conflict@other-school.example.com",
        username=conflicting_username,
        hashed_password="not-a-real-hash",
        full_name="Conflicting Student",
        role=UserRole.STUDENT,
        school_id=other_school.id,
    )
    db.add(conflicting_user)
    await db.flush()

    service = DemoClassService()
    with pytest.raises(ValueError, match=conflicting_username):
        await service.provision(db)

    # Nothing was written: no DEMO school, no DEMO classroom.
    assert await service.resolve_demo_school(db) is None
    assert await service.resolve_demo_classroom(db) is None

    # The conflicting user is untouched (still owned by the other school).
    await db.refresh(conflicting_user)
    assert conflicting_user.school_id == other_school.id

    # No other demo-named users were created as a side effect.
    result = await db.execute(select(User).where(User.role == UserRole.STUDENT))
    assert [u.username for u in result.scalars().all()] == [conflicting_username]


@pytest.mark.asyncio
async def test_reset_passwords_requires_existing_classroom(db: AsyncSession):
    from app.services.demo_class import DemoClassService

    service = DemoClassService()
    with pytest.raises(ValueError):
        await service.reset_passwords(db)


@pytest.mark.asyncio
async def test_reset_passwords_scoped_to_demo_classroom_membership(
    db: AsyncSession, grade: Grade
):
    """reset_passwords() must only touch demo-named users still linked to the
    Demo Class (via User.classroom_id or an active membership row) — not
    every user whose username happens to match the st01-stNN pattern.

    Exercised as a before/after sequence on a single account (rather than
    two accounts held in the demo classroom at once) to avoid the SQLite
    partial-unique-index gap documented on `small_demo_account_count` above.
    """
    from app.services.demo_class import DemoClassService, demo_username

    service = DemoClassService()
    await service.provision(db)

    demo_classroom = await service.resolve_demo_classroom(db)
    assert demo_classroom is not None

    username = demo_username(1)
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one()
    user.hashed_password = "stale-hash-1"
    await db.flush()

    # Still a normal demo classroom member: reset must touch them.
    reset_result = await service.reset_passwords(db)
    await db.refresh(user)
    assert reset_result["reset_count"] == 1
    assert user.hashed_password != "stale-hash-1"

    # Simulate the student being moved out of the Demo Class: classroom_id
    # repointed elsewhere and their membership row removed.
    other_classroom = Classroom(
        name="Some Other Class",
        school_id=demo_classroom.school_id,
        grade_id=grade.id,
        is_active=True,
    )
    db.add(other_classroom)
    await db.flush()

    result = await db.execute(
        select(ClassroomMembership).where(
            ClassroomMembership.user_id == user.id,
            ClassroomMembership.classroom_id == demo_classroom.id,
        )
    )
    membership = result.scalar_one()
    await db.delete(membership)
    user.classroom_id = other_classroom.id
    stale_hash = "stale-hash-should-not-change"
    user.hashed_password = stale_hash
    await db.flush()

    reset_result = await service.reset_passwords(db)
    await db.refresh(user)

    assert reset_result["reset_count"] == 0
    assert user.hashed_password == stale_hash


@pytest.mark.asyncio
async def test_teacher_may_publish_to_demo_classroom_without_same_school(
    db: AsyncSession, grade: Grade
):
    """can_teacher_publish_to_classroom() must allow any teacher/admin to
    publish to the Demo Class, even without matching school_id or a
    ClassroomMembership row (the demo-classroom permission bypass)."""
    from app.services.demo_class import DemoClassService
    from app.services.permission_service import PermissionService

    service = DemoClassService()
    await service.provision(db)
    await db.commit()

    demo_classroom = await service.resolve_demo_classroom(db)
    assert demo_classroom is not None

    from app.models import Region

    other_region = Region(name="Teacher Region", code="TEACHRG", level=1)
    db.add(other_region)
    await db.flush()
    unrelated_school = School(
        name="Unrelated School",
        code="UNRELATED",
        region_id=other_region.id,
        school_type="高中",
    )
    db.add(unrelated_school)
    await db.flush()

    teacher = User(
        username="teacher_no_demo_school",
        email="teacher_no_demo@test.com",
        hashed_password="hash",
        role=UserRole.TEACHER,
        school_id=unrelated_school.id,
    )
    db.add(teacher)
    await db.flush()

    permission_service = PermissionService()
    allowed = await permission_service.can_teacher_publish_to_classroom(
        db, teacher, demo_classroom
    )
    assert allowed is True


@pytest.mark.asyncio
async def test_student_from_other_school_may_not_publish_to_demo_classroom(
    db: AsyncSession, grade: Grade, other_school: School
):
    """The demo-classroom bypass is role-gated to teacher/admin/researcher.

    Note: `can_teacher_publish_to_classroom` also has a generic (non-demo,
    non-role-gated) "same school_id" fallback, so the negative case must use
    a user from a *different* school to actually exercise the demo-bypass
    role check rather than that fallback."""
    from app.services.demo_class import DemoClassService
    from app.services.permission_service import PermissionService

    service = DemoClassService()
    await service.provision(db)

    demo_classroom = await service.resolve_demo_classroom(db)
    assert demo_classroom is not None
    assert demo_classroom.school_id != other_school.id

    student = User(
        username="outside_student",
        email="outside_student@test.com",
        hashed_password="hash",
        role=UserRole.STUDENT,
        school_id=other_school.id,
    )
    db.add(student)
    await db.flush()

    permission_service = PermissionService()
    allowed = await permission_service.can_teacher_publish_to_classroom(
        db, student, demo_classroom
    )
    assert allowed is False


@pytest.mark.asyncio
async def test_demo_classroom_injected_for_teacher_outside_demo_school(
    db: AsyncSession, grade: Grade
):
    """ClassroomQueryService must inject the Demo Class into a teacher's
    classroom list even when the teacher belongs to a different school."""
    from app.models import Region
    from app.services.classroom_service import ClassroomQueryService
    from app.services.demo_class import DemoClassService

    service = DemoClassService()
    await service.provision(db)
    await db.commit()
    demo_classroom = await service.resolve_demo_classroom(db)
    assert demo_classroom is not None

    region = Region(name="Teacher Own Region", code="TOWNRG", level=1)
    db.add(region)
    await db.flush()
    own_school = School(
        name="Teacher Own School", code="TOWN", region_id=region.id, school_type="高中"
    )
    db.add(own_school)
    await db.flush()

    own_classroom = Classroom(
        name="Teacher Own Class", school_id=own_school.id, grade_id=grade.id
    )
    db.add(own_classroom)
    await db.flush()

    teacher = User(
        username="teacher_own_school",
        email="teacher_own@test.com",
        hashed_password="hash",
        role=UserRole.TEACHER,
        school_id=own_school.id,
    )
    db.add(teacher)
    await db.flush()

    membership = ClassroomMembership(
        user_id=teacher.id,
        classroom_id=own_classroom.id,
        role_in_class=RoleInClass.HEAD_TEACHER_PRIMARY,
        is_active=True,
    )
    db.add(membership)
    await db.commit()

    query_service = ClassroomQueryService()
    classrooms = await query_service.get_classrooms_for_user(db, teacher)

    classroom_ids = {c.id for c in classrooms}
    assert own_classroom.id in classroom_ids
    assert demo_classroom.id in classroom_ids


@pytest.mark.asyncio
async def test_demo_classroom_not_injected_when_school_filter_excludes_it(
    db: AsyncSession, grade: Grade
):
    """An explicit school_id filter that doesn't match the DEMO school must
    not have the Demo Class appended."""
    from app.models import Region
    from app.services.classroom_service import ClassroomQueryService
    from app.services.demo_class import DemoClassService

    service = DemoClassService()
    await service.provision(db)
    await db.commit()

    region = Region(name="Teacher Own Region 2", code="TOWNRG2", level=1)
    db.add(region)
    await db.flush()
    own_school = School(
        name="Teacher Own School 2",
        code="TOWN2",
        region_id=region.id,
        school_type="高中",
    )
    db.add(own_school)
    await db.flush()

    teacher = User(
        username="teacher_own_school_2",
        email="teacher_own_2@test.com",
        hashed_password="hash",
        role=UserRole.TEACHER,
        school_id=own_school.id,
    )
    db.add(teacher)
    await db.commit()

    query_service = ClassroomQueryService()
    classrooms = await query_service.get_classrooms_for_user(
        db, teacher, school_id=own_school.id
    )

    assert all(c.school_id == own_school.id for c in classrooms)
