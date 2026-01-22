"""Exam number generation utility

Format: school_code (4) + enrollment_year (4) + class_sequence (2) + seat_number (2)
Total: 12 digits
"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import SessionLocal
from app.models.evaluation import ExamNumberMapping


def generate_exam_number(
    school_code: str,
    enrollment_year: int,
    classroom_code: str,
    seat_number: int
) -> str:
    """Generate exam number with proper formatting

    Args:
        school_code: 4-digit school code
        enrollment_year: 4-digit enrollment year
        classroom_code: Classroom code (last 2 digits used for class sequence)
        seat_number: Seat number (will be formatted as 2 digits)

    Returns:
        12-digit exam number string

    Example:
        >>> generate_exam_number("4401", 2023, "2301", 1)
        '440120230101'
    """
    # Extract last 2 digits of classroom code as class sequence
    class_sequence = classroom_code[-2:]

    # Format seat number as 2 digits with leading zero
    seat_formatted = f"{seat_number:02d}"

    # Combine all parts
    return f"{school_code}{enrollment_year}{class_sequence}{seat_formatted}"


def validate_exam_number(exam_id: int, exam_number: str) -> str:
    """Validate uniqueness and add suffix if conflicted

    Args:
        exam_id: Exam ID to check against
        exam_number: 12-digit exam number to validate

    Returns:
        Valid exam number (original or with suffix if conflicted)

    Raises:
        ValueError: If exam_number format is invalid

    Example:
        >>> validate_exam_number(1, "440120230101")
        '440120230101'  # No conflict
        >>> validate_exam_number(1, "440120230101")  # If conflict exists
        '440120230101A'  # With suffix
    """
    # Validate format: must be 12 digits
    if not exam_number.isdigit() or len(exam_number) != 12:
        raise ValueError(f"Exam number must be 12 digits: {exam_number}")

    db = SessionLocal()
    try:
        # Check if exam number already exists for this exam
        existing = db.execute(
            select(ExamNumberMapping).where(
                ExamNumberMapping.exam_id == exam_id,
                ExamNumberMapping.exam_number == exam_number
            )
        ).scalar_one_or_none()

        # No conflict, return original
        if not existing:
            return exam_number

        # Conflict detected, add letter suffix
        suffix = 0
        while True:
            suffix += 1
            # Generate suffix: A, B, C, ...
            new_number = f"{exam_number}{chr(64 + suffix)}"

            # Check if new number is available
            existing = db.execute(
                select(ExamNumberMapping).where(
                    ExamNumberMapping.exam_id == exam_id,
                    ExamNumberMapping.exam_number == new_number
                )
            ).scalar_one_or_none()

            if not existing:
                return new_number
    finally:
        db.close()


async def validate_exam_number_async(
    db: AsyncSession,
    exam_id: int,
    exam_number: str
) -> str:
    """Validate uniqueness and add suffix if conflicted (async version)

    Args:
        db: Async database session
        exam_id: Exam ID to check against
        exam_number: 12-digit exam number to validate

    Returns:
        Valid exam number (original or with suffix if conflicted)

    Raises:
        ValueError: If exam_number format is invalid

    Example:
        >>> await validate_exam_number_async(db, 1, "440120230101")
        '440120230101'  # No conflict
        >>> await validate_exam_number_async(db, 1, "440120230101")  # If conflict exists
        '440120230101A'  # With suffix
    """
    # Validate format: must be 12 digits
    if not exam_number.isdigit() or len(exam_number) != 12:
        raise ValueError(f"Exam number must be 12 digits: {exam_number}")

    # Check if exam number already exists for this exam
    existing = await db.execute(
        select(ExamNumberMapping).where(
            ExamNumberMapping.exam_id == exam_id,
            ExamNumberMapping.exam_number == exam_number
        )
    )
    existing_mapping = existing.scalar_one_or_none()

    # No conflict, return original
    if not existing_mapping:
        return exam_number

    # Conflict detected, add letter suffix
    suffix = 0
    while True:
        suffix += 1
        # Generate suffix: A, B, C, ...
        new_number = f"{exam_number}{chr(64 + suffix)}"

        # Check if new number is available
        existing = await db.execute(
            select(ExamNumberMapping).where(
                ExamNumberMapping.exam_id == exam_id,
                ExamNumberMapping.exam_number == new_number
            )
        )
        existing_mapping = existing.scalar_one_or_none()

        if not existing_mapping:
            return new_number
