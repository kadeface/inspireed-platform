"""
Migrate usernames to new format: school_code + last 6 digits of ID
Format: XXXXYYYYYY (10 digits total)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from app.core.database import SessionLocal
from app.models.user import User, UserRole
from app.models.organization import School

def migrate_usernames():
    db = SessionLocal()

    try:
        # Get all schools
        schools = db.execute(select(School)).scalars().all()

        for school in schools:
            # Get students for this school
            students = db.execute(
                select(User).where(
                    User.school_id == school.id,
                    User.role == UserRole.STUDENT,
                    User.student_id_number.isnot(None)
                )
            ).scalars().all()

            # Track username conflicts
            username_counts = {}

            for student in students:
                # Generate base username
                base_username = f"{school.code}{student.student_id_number[-6:]}"

                # Handle conflicts
                count = username_counts.get(base_username, 0)

                if count == 0:
                    new_username = base_username
                else:
                    # Add letter suffix: A, B, C...
                    suffix_char = chr(65 + (count - 1) % 26)
                    new_username = f"{base_username}{suffix_char}"

                print(f"Student {student.full_name}: {student.username} -> {new_username}")
                student.username = new_username
                db.add(student)

                username_counts[base_username] = count + 1

        db.commit()
        print("✅ Username migration completed")

    except Exception as e:
        db.rollback()
        print(f"❌ Migration failed: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    migrate_usernames()
