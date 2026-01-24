"""
Migrate classroom codes from format '701' to '2301'
Format: enrollment_year suffix (2 digits) + class sequence (2 digits)
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from app.core.database import SessionLocal
from app.models.organization import Classroom

def migrate_classroom_codes():
    db = SessionLocal()

    try:
        classrooms = db.execute(select(Classroom)).scalars().all()

        for classroom in classrooms:
            if not classroom.code or not classroom.enrollment_year:
                print(f"Skipping classroom {classroom.id}: missing code or enrollment_year")
                continue

            # Extract old code parts
            old_code = str(classroom.code)
            year_suffix = str(classroom.enrollment_year)[-2:]  # Last 2 digits of year
            class_seq = old_code[-2:].zfill(2)  # Last 2 digits, zero-padded

            # Generate new code
            new_code = f"{year_suffix}{class_seq}"

            print(f"Classroom {classroom.name}: {old_code} -> {new_code}")
            classroom.code = new_code
            db.add(classroom)

        db.commit()
        print("✅ Classroom code migration completed")

    except Exception as e:
        db.rollback()
        print(f"❌ Migration failed: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    migrate_classroom_codes()
