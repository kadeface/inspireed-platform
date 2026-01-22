"""Initialize seat numbers for students based on classroom order"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from app.core.database import SessionLocal
from app.models.organization import Classroom
from app.models.user import User

def initialize_seat_numbers():
    db = SessionLocal()
    try:
        classrooms = db.execute(select(Classroom)).scalars().all()

        for classroom in classrooms:
            students = db.execute(
                select(User).where(
                    User.classroom_id == classroom.id
                ).order_by(User.id)
            ).scalars().all()

            for idx, student in enumerate(students, start=1):
                student.seat_number = idx
                db.add(student)

            print(f"Classroom {classroom.name}: assigned {len(students)} seat numbers")

        db.commit()
        print("✅ Seat number initialization completed")

    except Exception as e:
        db.rollback()
        print(f"❌ Initialization failed: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    initialize_seat_numbers()
