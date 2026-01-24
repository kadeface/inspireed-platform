"""Tests for exam number generator utility"""
import pytest
from app.utils.exam_number_generator import generate_exam_number, validate_exam_number
from app.models.evaluation import ExamNumberMapping
from app.models.user import User, UserRole
from app.core.database import SessionLocal


@pytest.fixture(autouse=True)
def cleanup_test_data():
    """Cleanup test exam number mappings before and after each test"""
    db = SessionLocal()
    try:
        # Cleanup before test
        db.query(ExamNumberMapping).filter(ExamNumberMapping.exam_number.like("4401%")).delete()
        db.commit()
        yield
        # Cleanup after test
        db.query(ExamNumberMapping).filter(ExamNumberMapping.exam_number.like("4401%")).delete()
        db.commit()
    finally:
        db.close()


def test_generate_exam_number():
    """Test basic exam number generation"""
    result = generate_exam_number("4401", 2023, "2301", 1)
    assert result == "440120230101"
    assert len(result) == 12
    assert result.isdigit()


def test_generate_exam_number_seat_padding():
    """Test exam number generation with seat number padding"""
    # Single digit seat number
    result1 = generate_exam_number("4401", 2023, "2301", 5)
    assert result1 == "440120230105"
    assert result1[-2:] == "05"

    # Double digit seat number
    result2 = generate_exam_number("4401", 2023, "2301", 15)
    assert result2 == "440120230115"
    assert result2[-2:] == "15"

    # Maximum seat number
    result3 = generate_exam_number("4401", 2023, "2301", 99)
    assert result3 == "440120230199"
    assert result3[-2:] == "99"


def test_generate_exam_number_different_classrooms():
    """Test exam number generation for different classrooms"""
    result1 = generate_exam_number("4401", 2023, "2301", 1)
    result2 = generate_exam_number("4401", 2023, "2302", 1)
    result3 = generate_exam_number("4401", 2023, "2303", 1)

    assert result1 == "440120230101"
    assert result2 == "440120230201"
    assert result3 == "440120230301"


def test_generate_exam_number_different_years():
    """Test exam number generation for different enrollment years"""
    result1 = generate_exam_number("4401", 2023, "2301", 1)
    result2 = generate_exam_number("4401", 2024, "2301", 1)
    result3 = generate_exam_number("4401", 2025, "2301", 1)

    assert result1 == "440120230101"
    assert result2 == "440120240101"
    assert result3 == "440120250101"


def test_generate_exam_number_different_schools():
    """Test exam number generation for different schools"""
    result1 = generate_exam_number("4401", 2023, "2301", 1)
    result2 = generate_exam_number("4402", 2023, "2301", 1)
    result3 = generate_exam_number("4403", 2023, "2301", 1)

    assert result1 == "440120230101"
    assert result2 == "440220230101"
    assert result3 == "440320230101"


def test_validate_exam_number_no_conflict():
    """Test exam number validation without conflicts"""
    result = validate_exam_number(1, "440120230101")
    assert result == "440120230101"
    assert len(result) == 12


def test_validate_exam_number_with_conflict():
    """Test exam number conflict resolution with single conflict"""
    db = SessionLocal()

    try:
        # Create existing exam number mapping
        existing = ExamNumberMapping(
            exam_id=1,
            student_id=1,
            exam_number="440120230101",
            student_id_number="110101200501011234",
            school_id=1,
            classroom_id=1
        )
        db.add(existing)
        db.commit()

        # Validate exam number (should add suffix)
        new_number = validate_exam_number(1, "440120230101")
        assert new_number == "440120230101A"  # Has suffix
        assert len(new_number) == 13
    finally:
        db.close()


def test_validate_exam_number_with_multiple_conflicts():
    """Test exam number conflict resolution with multiple conflicts"""
    db = SessionLocal()

    try:
        # Create existing exam number mappings with sequential suffixes
        for i in range(5):
            suffix = "" if i == 0 else chr(64 + i)  # '', A, B, C, D
            exam_number = f"440120230101{suffix}"
            mapping = ExamNumberMapping(
                exam_id=1,
                student_id=i,
                exam_number=exam_number,
                student_id_number=f"11010120050101123{i}",
                school_id=1,
                classroom_id=1
            )
            db.add(mapping)
        db.commit()

        # Validate exam number (should skip to E)
        new_number = validate_exam_number(1, "440120230101")
        assert new_number == "440120230101E"  # Should skip to E
        assert len(new_number) == 13
    finally:
        db.close()


def test_validate_exam_number_different_exams():
    """Test that conflicts are only checked within the same exam"""
    db = SessionLocal()

    try:
        # Create existing exam number mapping for exam 1
        existing = ExamNumberMapping(
            exam_id=1,
            student_id=1,
            exam_number="440120230101",
            student_id_number="110101200501011234",
            school_id=1,
            classroom_id=1
        )
        db.add(existing)
        db.commit()

        # Validate for exam 2 (should not conflict with exam 1)
        result = validate_exam_number(2, "440120230101")
        assert result == "440120230101"  # No conflict
        assert len(result) == 12
    finally:
        db.close()


def test_validate_exam_number_invalid_format():
    """Test exam number validation with invalid format"""
    # Too short
    with pytest.raises(ValueError, match="Exam number must be 12 digits"):
        validate_exam_number(1, "123456789")

    # Too long
    with pytest.raises(ValueError, match="Exam number must be 12 digits"):
        validate_exam_number(1, "1234567890123")

    # Contains non-digit characters
    with pytest.raises(ValueError, match="Exam number must be 12 digits"):
        validate_exam_number(1, "44012023010A")

    # Empty string
    with pytest.raises(ValueError, match="Exam number must be 12 digits"):
        validate_exam_number(1, "")


def test_generate_exam_number_edge_cases():
    """Test edge cases for exam number generation"""
    # Test with minimum seat number
    result1 = generate_exam_number("0001", 2000, "0001", 1)
    assert result1 == "000120000101"
    assert len(result1) == 12

    # Test with maximum values
    result2 = generate_exam_number("9999", 9999, "9999", 99)
    assert result2 == "999999999999"
    assert len(result2) == 12


def test_exam_number_format_consistency():
    """Test that exam numbers maintain consistent format"""
    # All exam numbers should be exactly 12 digits
    test_cases = [
        ("4401", 2023, "2301", 1),
        ("4401", 2023, "2301", 99),
        ("0001", 2000, "0001", 1),
        ("9999", 9999, "9999", 99),
    ]

    for school_code, year, classroom, seat in test_cases:
        result = generate_exam_number(school_code, year, classroom, seat)
        assert len(result) == 12, f"Length mismatch for {school_code}, {year}, {classroom}, {seat}"
        assert result.isdigit(), f"Non-digit result for {school_code}, {year}, {classroom}, {seat}"


def test_class_sequence_extraction():
    """Test that class sequence is correctly extracted from classroom code"""
    # Classroom code "2301" should extract "01"
    result1 = generate_exam_number("4401", 2023, "2301", 5)
    assert result1[8:10] == "01"

    # Classroom code "2315" should extract "15"
    result2 = generate_exam_number("4401", 2023, "2315", 5)
    assert result2[8:10] == "15"

    # Classroom code "9999" should extract "99"
    result3 = generate_exam_number("4401", 2023, "9999", 5)
    assert result3[8:10] == "99"
