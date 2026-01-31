"""
Tests for ClassroomQueryService - the unified query layer for classroom access.
"""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User, UserRole, Classroom, School, Region


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
    )
    db.add(teacher)
    await db.flush()
    return teacher


@pytest.fixture(scope="function")
async def admin_user(db: AsyncSession):
    """Create an admin user."""
    admin = User(
        username="admin1",
        email="admin1@test.com",
        hashed_password="hash",
        role=UserRole.ADMIN,
    )
    db.add(admin)
    await db.flush()
    return admin


@pytest.fixture(scope="function")
async def district_admin_user(db: AsyncSession, region: Region):
    """Create a district admin user."""
    admin = User(
        username="district_admin",
        email="district_admin@test.com",
        hashed_password="hash",
        role=UserRole.DISTRICT_ADMIN,
        region_id=region.id,
    )
    db.add(admin)
    await db.flush()
    return admin


@pytest.fixture(scope="function")
async def school_admin_user(db: AsyncSession, school: School):
    """Create a school admin user."""
    admin = User(
        username="school_admin",
        email="school_admin@test.com",
        hashed_password="hash",
        role=UserRole.SCHOOL_ADMIN,
        school_id=school.id,
    )
    db.add(admin)
    await db.flush()
    return admin


@pytest.mark.asyncio
async def test_teacher_gets_only_their_school_classrooms(
    db: AsyncSession, teacher_user: User, school: School
):
    """Teachers should only see classrooms from their school."""
    from app.services.classroom_service import ClassroomQueryService

    service = ClassroomQueryService()

    # Create classroom in teacher's school
    classroom1 = Classroom(name="Class 1", school_id=school.id, grade_id=1)
    db.add(classroom1)

    # Create classroom in different school
    other_school = School(
        name="Other School", code="OTHER", region_id=school.region_id, school_type="小学"
    )
    db.add(other_school)
    await db.flush()
    classroom2 = Classroom(name="Class 2", school_id=other_school.id, grade_id=1)
    db.add(classroom2)
    await db.commit()

    # Teacher should only see classroom from their school
    result = await service.get_classrooms_for_user(db, teacher_user)

    assert len(result) == 1
    assert result[0].id == classroom1.id


@pytest.mark.asyncio
async def test_is_active_filter_respected(db: AsyncSession, admin_user: User, school: School):
    """is_active filter should be applied."""
    from app.services.classroom_service import ClassroomQueryService

    service = ClassroomQueryService()

    active_classroom = Classroom(name="Active", school_id=school.id, grade_id=1, is_active=True)
    inactive_classroom = Classroom(
        name="Inactive", school_id=school.id, grade_id=1, is_active=False
    )
    db.add_all([active_classroom, inactive_classroom])
    await db.commit()

    # Query only active
    result = await service.get_classrooms_for_user(db, admin_user, is_active=True)

    assert len(result) == 1
    assert result[0].name == "Active"


@pytest.mark.asyncio
async def test_admin_sees_all_classrooms(db: AsyncSession, admin_user: User, region: Region):
    """Admins should see all classrooms regardless of school."""
    from app.services.classroom_service import ClassroomQueryService

    service = ClassroomQueryService()

    # Create multiple schools with classrooms
    school1 = School(name="School 1", code="S1", region_id=region.id, school_type="小学")
    school2 = School(name="School 2", code="S2", region_id=region.id, school_type="小学")
    db.add_all([school1, school2])
    await db.flush()

    classroom1 = Classroom(name="C1", school_id=school1.id, grade_id=1)
    classroom2 = Classroom(name="C2", school_id=school2.id, grade_id=1)
    db.add_all([classroom1, classroom2])
    await db.commit()

    result = await service.get_classrooms_for_user(db, admin_user)

    assert len(result) == 2


@pytest.mark.asyncio
async def test_district_admin_sees_only_their_region(
    db: AsyncSession, district_admin_user: User, region: Region
):
    """District admins should only see classrooms from their region."""
    from app.services.classroom_service import ClassroomQueryService

    service = ClassroomQueryService()

    # Create schools in different regions
    other_region = Region(name="Other Region", code="OTHER", level=3)
    db.add(other_region)
    await db.flush()

    school1 = School(name="School 1", code="S1", region_id=region.id, school_type="小学")
    school2 = School(name="School 2", code="S2", region_id=other_region.id, school_type="小学")
    db.add_all([school1, school2])
    await db.flush()

    classroom1 = Classroom(name="C1", school_id=school1.id, grade_id=1)
    classroom2 = Classroom(name="C2", school_id=school2.id, grade_id=1)
    db.add_all([classroom1, classroom2])
    await db.commit()

    result = await service.get_classrooms_for_user(db, district_admin_user)

    assert len(result) == 1
    assert result[0].school_id == school1.id


@pytest.mark.asyncio
async def test_school_admin_sees_only_their_school(
    db: AsyncSession, school_admin_user: User, school: School, region: Region
):
    """School admins should only see classrooms from their school."""
    from app.services.classroom_service import ClassroomQueryService

    service = ClassroomQueryService()

    # Create another school in the same region
    other_school = School(name="Other School", code="OTHER", region_id=region.id, school_type="小学")
    db.add(other_school)
    await db.flush()

    classroom1 = Classroom(name="C1", school_id=school.id, grade_id=1)
    classroom2 = Classroom(name="C2", school_id=other_school.id, grade_id=1)
    db.add_all([classroom1, classroom2])
    await db.commit()

    result = await service.get_classrooms_for_user(db, school_admin_user)

    assert len(result) == 1
    assert result[0].school_id == school.id


@pytest.mark.asyncio
async def test_grade_id_filter(db: AsyncSession, admin_user: User, school: School):
    """Filtering by grade_id should work."""
    from app.services.classroom_service import ClassroomQueryService

    service = ClassroomQueryService()

    classroom1 = Classroom(name="Grade 1", school_id=school.id, grade_id=1)
    classroom2 = Classroom(name="Grade 2", school_id=school.id, grade_id=2)
    db.add_all([classroom1, classroom2])
    await db.commit()

    result = await service.get_classrooms_for_user(db, admin_user, grade_id=1)

    assert len(result) == 1
    assert result[0].grade_id == 1


@pytest.mark.asyncio
async def test_school_id_filter(db: AsyncSession, admin_user: User, region: Region):
    """Filtering by school_id should work."""
    from app.services.classroom_service import ClassroomQueryService

    service = ClassroomQueryService()

    school1 = School(name="School 1", code="S1", region_id=region.id, school_type="小学")
    school2 = School(name="School 2", code="S2", region_id=region.id, school_type="小学")
    db.add_all([school1, school2])
    await db.flush()

    classroom1 = Classroom(name="C1", school_id=school1.id, grade_id=1)
    classroom2 = Classroom(name="C2", school_id=school2.id, grade_id=1)
    db.add_all([classroom1, classroom2])
    await db.commit()

    result = await service.get_classrooms_for_user(db, admin_user, school_id=school1.id)

    assert len(result) == 1
    assert result[0].school_id == school1.id


@pytest.mark.asyncio
async def test_region_id_filter(db: AsyncSession, admin_user: User, region: Region):
    """Filtering by region_id should work."""
    from app.services.classroom_service import ClassroomQueryService

    service = ClassroomQueryService()

    other_region = Region(name="Other Region", code="OTHER", level=3)
    db.add(other_region)
    await db.flush()

    school1 = School(name="School 1", code="S1", region_id=region.id, school_type="小学")
    school2 = School(name="School 2", code="S2", region_id=other_region.id, school_type="小学")
    db.add_all([school1, school2])
    await db.flush()

    classroom1 = Classroom(name="C1", school_id=school1.id, grade_id=1)
    classroom2 = Classroom(name="C2", school_id=school2.id, grade_id=1)
    db.add_all([classroom1, classroom2])
    await db.commit()

    result = await service.get_classrooms_for_user(db, admin_user, region_id=region.id)

    assert len(result) == 1
    assert result[0].school_id == school1.id


@pytest.mark.asyncio
async def test_search_filter(db: AsyncSession, admin_user: User, school: School):
    """Search filter should work across name, code, description, and school name."""
    from app.services.classroom_service import ClassroomQueryService

    service = ClassroomQueryService()

    classroom1 = Classroom(name="Math Class", code="MATH", school_id=school.id, grade_id=1)
    classroom2 = Classroom(
        name="Science Class",
        code="SCI",
        school_id=school.id,
        grade_id=1,
        description="Learning science",
    )
    classroom3 = Classroom(name="Art Class", code="ART", school_id=school.id, grade_id=1)
    db.add_all([classroom1, classroom2, classroom3])
    await db.commit()

    # Search by name
    result = await service.get_classrooms_for_user(db, admin_user, search="Math")
    assert len(result) == 1
    assert result[0].name == "Math Class"

    # Search by code
    result = await service.get_classrooms_for_user(db, admin_user, search="SCI")
    assert len(result) == 1
    assert result[0].code == "SCI"

    # Search by description
    result = await service.get_classrooms_for_user(db, admin_user, search="science")
    assert len(result) == 1
    assert result[0].name == "Science Class"

    # Search by school name
    result = await service.get_classrooms_for_user(db, admin_user, search="Test School")
    assert len(result) == 3


@pytest.mark.asyncio
async def test_teacher_without_school_returns_empty(db: AsyncSession, region: Region):
    """Teacher without school_id should get empty list."""
    from app.services.classroom_service import ClassroomQueryService

    service = ClassroomQueryService()

    teacher = User(
        username="no_school_teacher",
        email="no_school@test.com",
        hashed_password="hash",
        role=UserRole.TEACHER,
        school_id=None,
    )
    db.add(teacher)
    await db.flush()

    school = School(name="Test School", code="SCH001", region_id=region.id, school_type="小学")
    db.add(school)
    await db.flush()

    classroom = Classroom(name="Class 1", school_id=school.id, grade_id=1)
    db.add(classroom)
    await db.commit()

    result = await service.get_classrooms_for_user(db, teacher)

    assert len(result) == 0


@pytest.mark.asyncio
async def test_get_classroom_by_id(db: AsyncSession, admin_user: User, school: School):
    """get_classroom_by_id should return classroom if user has access."""
    from app.services.classroom_service import ClassroomQueryService

    service = ClassroomQueryService()

    classroom = Classroom(name="Test Class", school_id=school.id, grade_id=1)
    db.add(classroom)
    await db.commit()

    result = await service.get_classroom_by_id(db, classroom.id, admin_user)

    assert result is not None
    assert result.id == classroom.id


@pytest.mark.asyncio
async def test_get_classroom_by_id_not_accessible(
    db: AsyncSession, teacher_user: User, school: School, region: Region
):
    """get_classroom_by_id should return None if user doesn't have access."""
    from app.services.classroom_service import ClassroomQueryService

    service = ClassroomQueryService()

    # Create classroom in different school
    other_school = School(name="Other School", code="OTHER", region_id=region.id, school_type="小学")
    db.add(other_school)
    await db.flush()

    classroom = Classroom(name="Other Class", school_id=other_school.id, grade_id=1)
    db.add(classroom)
    await db.commit()

    result = await service.get_classroom_by_id(db, classroom.id, teacher_user)

    assert result is None


@pytest.mark.asyncio
async def test_combined_filters(db: AsyncSession, admin_user: User, school: School):
    """Multiple filters should work together."""
    from app.services.classroom_service import ClassroomQueryService

    service = ClassroomQueryService()

    classroom1 = Classroom(
        name="Active Math", code="MATH1", school_id=school.id, grade_id=1, is_active=True
    )
    classroom2 = Classroom(
        name="Inactive Math", code="MATH2", school_id=school.id, grade_id=1, is_active=False
    )
    classroom3 = Classroom(
        name="Active Science", code="SCI1", school_id=school.id, grade_id=2, is_active=True
    )
    db.add_all([classroom1, classroom2, classroom3])
    await db.commit()

    # Combine is_active, grade_id, and search
    result = await service.get_classrooms_for_user(
        db, admin_user, is_active=True, grade_id=1, search="Math"
    )

    assert len(result) == 1
    assert result[0].name == "Active Math"
