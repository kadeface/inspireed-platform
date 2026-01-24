"""Username generation utility

Format: school_code (4 digits) + last 6 digits of student_id_number
Total: 10 digits

Conflict resolution: Append letter suffix (A, B, C...)
"""
from sqlalchemy import select
from app.core.database import SessionLocal
from app.models.user import User


def generate_username(school_code: str, student_id_number: str) -> str:
    """
    Generate username: school_code + last 6 digits of student_id_number

    Args:
        school_code: 4-digit school code
        student_id_number: 18-digit student ID number

    Returns:
        10-digit username with conflict resolution

    Example:
        >>> generate_username("4401", "110101200501011234")
        "4401011234"
    """
    base_username = f"{school_code}{student_id_number[-6:]}"

    # Check for conflicts
    db = SessionLocal()
    try:
        existing = db.execute(
            select(User).where(User.username == base_username)
        ).scalar_one_or_none()

        if not existing:
            return base_username

        # Add letter suffix for conflicts
        suffix = 0
        while True:
            suffix += 1
            username = f"{base_username}{chr(64 + suffix)}"  # A=65, B=66...

            existing = db.execute(
                select(User).where(User.username == username)
            ).scalar_one_or_none()

            if not existing:
                return username

            if suffix >= 26:
                # If A-Z exhausted, use numbers
                username = f"{base_username}{suffix - 26}"
                existing = db.execute(
                    select(User).where(User.username == username)
                ).scalar_one_or_none()

                if not existing:
                    return username
    finally:
        db.close()
