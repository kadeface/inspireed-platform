"""Tests for username generator utility"""
import pytest
from app.utils.username_generator import generate_username
from app.models.user import User, UserRole
from app.core.database import SessionLocal


@pytest.fixture(autouse=True)
def cleanup_test_users():
    """Cleanup test users before and after each test"""
    db = SessionLocal()
    try:
        # Cleanup before test
        db.query(User).filter(User.username.like("4401%")).delete()
        db.commit()
        yield
        # Cleanup after test
        db.query(User).filter(User.username.like("4401%")).delete()
        db.commit()
    finally:
        db.close()


def test_generate_username_no_conflict():
    """Test username generation without conflicts"""
    username = generate_username("4401", "110101200501011234")
    assert username == "4401011234"
    assert len(username) == 10


def test_generate_username_with_conflict():
    """Test username conflict resolution with single conflict"""
    db = SessionLocal()

    try:
        # Create existing user
        existing = User(
            username="4401011234",
            email="existing@test.com",
            hashed_password="hash",
            full_name="Test User",
            student_id_number="110101200501019999",
            role=UserRole.STUDENT
        )
        db.add(existing)
        db.commit()

        # Generate new username (should add suffix)
        new_username = generate_username("4401", "110101200501011234")
        assert new_username == "4401011234A"  # Has suffix
        assert len(new_username) == 11
    finally:
        db.close()


def test_generate_username_with_multiple_conflicts():
    """Test username conflict resolution with multiple conflicts"""
    db = SessionLocal()

    try:
        # Create existing users with sequential suffixes
        for i in range(5):
            suffix = "" if i == 0 else chr(64 + i)  # '', A, B, C, D
            username = f"4401011234{suffix}"
            user = User(
                username=username,
                email=f"test{i}@test.com",
                hashed_password="hash",
                full_name=f"Test User {i}",
                student_id_number=f"11010120050101999{i}",
                role=UserRole.STUDENT
            )
            db.add(user)
        db.commit()

        # Generate new username (should skip to E)
        new_username = generate_username("4401", "110101200501011234")
        assert new_username == "4401011234E"  # Should skip to E
        assert len(new_username) == 11
    finally:
        db.close()


def test_generate_username_different_school_codes():
    """Test that different school codes produce different usernames"""
    username1 = generate_username("4401", "110101200501011234")
    username2 = generate_username("4402", "110101200501011234")
    username3 = generate_username("4403", "110101200501011234")

    assert username1 == "4401011234"
    assert username2 == "4402011234"
    assert username3 == "4403011234"

    # All should be different
    assert username1 != username2
    assert username2 != username3


def test_generate_username_different_student_ids():
    """Test that different student ID numbers produce different usernames"""
    username1 = generate_username("4401", "110101200501011234")
    username2 = generate_username("4401", "999999999999019999")
    username3 = generate_username("4401", "888888888888018888")

    assert username1 == "4401011234"
    assert username2 == "4401019999"
    assert username3 == "4401018888"

    # All should be different
    assert username1 != username2
    assert username2 != username3


def test_generate_username_format():
    """Test that generated username follows correct format"""
    username = generate_username("1234", "110101200501011234")

    # Should be 10 characters for base case
    assert len(username) == 10

    # Should be alphanumeric
    assert username.isalnum()

    # Should start with school code
    assert username.startswith("1234")

    # Should end with last 6 digits of student ID
    assert username.endswith("011234")


def test_generate_username_edge_cases():
    """Test edge cases for username generation"""
    # Test with minimum values
    username1 = generate_username("0001", "000000000000000001")
    assert username1 == "0001000001"
    assert len(username1) == 10

    # Test with maximum values
    username2 = generate_username("9999", "999999999999999999")
    assert username2 == "9999999999"
    assert len(username2) == 10
