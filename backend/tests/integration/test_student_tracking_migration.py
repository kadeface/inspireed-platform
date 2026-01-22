"""
Integration tests for student tracking migration scripts.

Tests the end-to-end migration of:
1. Classroom codes (old format -> new format)
2. Usernames (old format -> new format)
3. Seat number initialization
"""
import pytest
from sqlalchemy import select

from app.models.user import User, UserRole
from app.models.organization import Classroom, School
from app.core.database import SessionLocal


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.rollback()
        db.close()


@pytest.fixture(scope="function")
def setup_test_data(db_session):
    """Setup test data for migration tests."""
    # Create test school
    school = School(
        name="Test School",
        code="4401"
    )
    db_session.add(school)
    db_session.flush()

    # Create test classroom with old code format
    classroom = Classroom(
        name="七年级1班",
        code="701",  # Old format
        school_id=school.id,
        grade_id=7,
        enrollment_year=2023
    )
    db_session.add(classroom)
    db_session.flush()

    # Create test students with old username format
    student1 = User(
        username="old_username_1",
        full_name="Test Student 1",
        student_id_number="110101200501011234",
        school_id=school.id,
        classroom_id=classroom.id,
        role=UserRole.STUDENT
    )
    db_session.add(student1)

    student2 = User(
        username="old_username_2",
        full_name="Test Student 2",
        student_id_number="110101200501011235",
        school_id=school.id,
        classroom_id=classroom.id,
        role=UserRole.STUDENT
    )
    db_session.add(student2)

    db_session.commit()

    return {
        "db": db_session,
        "school": school,
        "classroom": classroom,
        "student1": student1,
        "student2": student2
    }


def test_classroom_code_migration(setup_test_data):
    """Test classroom code migration from old format to new format."""
    from scripts.migrate_classroom_codes import migrate_classroom_codes

    db = setup_test_data["db"]
    classroom = setup_test_data["classroom"]

    # Verify old format
    assert classroom.code == "701"

    # Run migration
    migrate_classroom_codes()

    # Refresh from database
    db.refresh(classroom)

    # Verify new format: enrollment_year suffix (23) + class sequence (01)
    assert classroom.code == "2301", f"Expected '2301', got '{classroom.code}'"


def test_classroom_code_migration_with_zero_padding(setup_test_data):
    """Test classroom code migration with zero-padding."""
    from scripts.migrate_classroom_codes import migrate_classroom_codes

    db = setup_test_data["db"]
    school = setup_test_data["school"]

    # Create classroom with single-digit class sequence
    classroom2 = Classroom(
        name="七年级2班",
        code="702",  # Old format
        school_id=school.id,
        grade_id=7,
        enrollment_year=2023
    )
    db.add(classroom2)
    db.commit()

    # Run migration
    migrate_classroom_codes()

    # Refresh from database
    db.refresh(classroom2)

    # Verify zero-padding
    assert classroom2.code == "2302", f"Expected '2302', got '{classroom2.code}'"


def test_classroom_code_migration_skip_missing_data(db_session):
    """Test that migration skips classrooms with missing data."""
    from scripts.migrate_classroom_codes import migrate_classroom_codes

    # Create classroom without enrollment_year
    classroom = Classroom(
        name="Test Classroom",
        code="701",
        school_id=None,
        grade_id=7,
        enrollment_year=None
    )
    db_session.add(classroom)
    db_session.commit()

    # Get original code
    original_code = classroom.code

    # Run migration (should skip this classroom)
    migrate_classroom_codes()

    # Refresh from database
    db_session.refresh(classroom)

    # Verify code unchanged
    assert classroom.code == original_code, "Classroom without enrollment_year should be skipped"


def test_username_migration_single_student(setup_test_data):
    """Test username migration for a single student."""
    from scripts.migrate_usernames import migrate_usernames

    db = setup_test_data["db"]
    school = setup_test_data["school"]
    student1 = setup_test_data["student1"]

    # Verify old format
    assert student1.username == "old_username_1"

    # Run migration
    migrate_usernames()

    # Refresh from database
    db.refresh(student1)

    # Verify new format: school_code (4401) + last 6 digits of ID (011234)
    expected_username = "4401011234"
    assert student1.username == expected_username, f"Expected '{expected_username}', got '{student1.username}'"


def test_username_migration_multiple_students(setup_test_data):
    """Test username migration for multiple students."""
    from scripts.migrate_usernames import migrate_usernames

    db = setup_test_data["db"]
    student1 = setup_test_data["student1"]
    student2 = setup_test_data["student2"]

    # Run migration
    migrate_usernames()

    # Refresh from database
    db.refresh(student1)
    db.refresh(student2)

    # Verify both students migrated
    assert student1.username == "4401011234", f"Expected '4401011234', got '{student1.username}'"
    assert student2.username == "4401011235", f"Expected '4401011235', got '{student2.username}'"


def test_username_migration_with_conflicts(db_session):
    """Test username migration with conflicting ID numbers."""
    from scripts.migrate_usernames import migrate_usernames

    # Create school
    school = School(
        name="Conflict Test School",
        code="4402"
    )
    db_session.add(school)
    db_session.flush()

    # Create classroom
    classroom = Classroom(
        name="Test Class",
        code="801",
        school_id=school.id,
        grade_id=8,
        enrollment_year=2023
    )
    db_session.add(classroom)
    db_session.flush()

    # Create students with same last 6 digits (conflict)
    student1 = User(
        username="student1",
        full_name="Student One",
        student_id_number="110101200501011111",  # Ends in 111111
        school_id=school.id,
        classroom_id=classroom.id,
        role=UserRole.STUDENT
    )
    db_session.add(student1)

    student2 = User(
        username="student2",
        full_name="Student Two",
        student_id_number="110101200501021111",  # Also ends in 111111
        school_id=school.id,
        classroom_id=classroom.id,
        role=UserRole.STUDENT
    )
    db_session.add(student2)

    student3 = User(
        username="student3",
        full_name="Student Three",
        student_id_number="110101200501031111",  # Also ends in 111111
        school_id=school.id,
        classroom_id=classroom.id,
        role=UserRole.STUDENT
    )
    db_session.add(student3)

    db_session.commit()

    # Run migration
    migrate_usernames()

    # Refresh from database
    db_session.refresh(student1)
    db_session.refresh(student2)
    db_session.refresh(student3)

    # Verify conflict resolution
    # First student gets base username
    assert student1.username == "4402111111", f"Expected '4402111111', got '{student1.username}'"
    # Second student gets 'A' suffix
    assert student2.username == "4402111111A", f"Expected '4402111111A', got '{student2.username}'"
    # Third student gets 'B' suffix
    assert student3.username == "4402111111B", f"Expected '4402111111B', got '{student3.username}'"


def test_seat_number_initialization(setup_test_data):
    """Test seat number initialization for students."""
    from scripts.initialize_seat_numbers import initialize_seat_numbers

    db = setup_test_data["db"]
    classroom = setup_test_data["classroom"]
    student1 = setup_test_data["student1"]
    student2 = setup_test_data["student2"]

    # Run initialization
    initialize_seat_numbers()

    # Refresh from database
    db.refresh(student1)
    db.refresh(student2)

    # Verify seat numbers assigned in order
    assert student1.seat_number == 1, f"Expected seat_number=1, got {student1.seat_number}"
    assert student2.seat_number == 2, f"Expected seat_number=2, got {student2.seat_number}"


def test_seat_number_initialization_multiple_classrooms(db_session):
    """Test seat number initialization across multiple classrooms."""
    from scripts.initialize_seat_numbers import initialize_seat_numbers

    # Create school
    school = School(
        name="Multi-Class School",
        code="4403"
    )
    db_session.add(school)
    db_session.flush()

    # Create two classrooms
    classroom1 = Classroom(
        name="Class 1",
        code="901",
        school_id=school.id,
        grade_id=9,
        enrollment_year=2023
    )
    db_session.add(classroom1)
    db_session.flush()

    classroom2 = Classroom(
        name="Class 2",
        code="902",
        school_id=school.id,
        grade_id=9,
        enrollment_year=2023
    )
    db_session.add(classroom2)
    db_session.flush()

    # Create students for classroom1
    for i in range(3):
        student = User(
            username=f"student1_{i}",
            full_name=f"Student 1-{i}",
            student_id_number=f"11010120050101000{i}",
            school_id=school.id,
            classroom_id=classroom1.id,
            role=UserRole.STUDENT
        )
        db_session.add(student)

    # Create students for classroom2
    for i in range(2):
        student = User(
            username=f"student2_{i}",
            full_name=f"Student 2-{i}",
            student_id_number=f"11010120050102000{i}",
            school_id=school.id,
            classroom_id=classroom2.id,
            role=UserRole.STUDENT
        )
        db_session.add(student)

    db_session.commit()

    # Run initialization
    initialize_seat_numbers()

    # Verify classroom1 students have seats 1-3
    students1 = db_session.execute(
        select(User).where(User.classroom_id == classroom1.id).order_by(User.seat_number)
    ).scalars().all()

    assert len(students1) == 3
    assert students1[0].seat_number == 1
    assert students1[1].seat_number == 2
    assert students1[2].seat_number == 3

    # Verify classroom2 students have seats 1-2 (independent numbering)
    students2 = db_session.execute(
        select(User).where(User.classroom_id == classroom2.id).order_by(User.seat_number)
    ).scalars().all()

    assert len(students2) == 2
    assert students2[0].seat_number == 1
    assert students2[1].seat_number == 2


def test_full_migration_pipeline(setup_test_data):
    """Test running all migrations in sequence."""
    from scripts.migrate_classroom_codes import migrate_classroom_codes
    from scripts.migrate_usernames import migrate_usernames
    from scripts.initialize_seat_numbers import initialize_seat_numbers

    db = setup_test_data["db"]
    classroom = setup_test_data["classroom"]
    student1 = setup_test_data["student1"]
    student2 = setup_test_data["student2"]

    # Run all migrations
    migrate_classroom_codes()
    migrate_usernames()
    initialize_seat_numbers()

    # Refresh from database
    db.refresh(classroom)
    db.refresh(student1)
    db.refresh(student2)

    # Verify all migrations completed successfully
    # Classroom code migrated
    assert classroom.code == "2301"

    # Usernames migrated
    assert student1.username == "4401011234"
    assert student2.username == "4401011235"

    # Seat numbers assigned
    assert student1.seat_number == 1
    assert student2.seat_number == 2


def test_migration_idempotency(setup_test_data):
    """Test that migrations can be run multiple times safely."""
    from scripts.migrate_classroom_codes import migrate_classroom_codes
    from scripts.migrate_usernames import migrate_usernames
    from scripts.initialize_seat_numbers import initialize_seat_numbers

    db = setup_test_data["db"]
    classroom = setup_test_data["classroom"]
    student1 = setup_test_data["student1"]

    # Run migrations first time
    migrate_classroom_codes()
    migrate_usernames()
    initialize_seat_numbers()

    # Get results
    db.refresh(classroom)
    db.refresh(student1)
    classroom_code_after_first = classroom.code
    username_after_first = student1.username
    seat_after_first = student1.seat_number

    # Run migrations second time
    migrate_classroom_codes()
    migrate_usernames()
    initialize_seat_numbers()

    # Get results again
    db.refresh(classroom)
    db.refresh(student1)

    # Verify no changes
    assert classroom.code == classroom_code_after_first
    assert student1.username == username_after_first
    assert student1.seat_number == seat_after_first
