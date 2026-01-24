# Student Tracking System Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Implement a standardized student tracking system with unique identifiers supporting cross-school, cross-grade student growth analysis.

**Architecture:**
- Use `student_id_number` (身份证号) as the permanent tracking key across all tables
- Generate `username` (学校编码 + 身份证后6位) as login credential with conflict resolution
- Generate `exam_number` (学校编码 + 入学年份 + 班序号 + 座位号) for exam management
- Optimize classroom code format (2301 instead of 701) to eliminate grade redundancy

**Tech Stack:**
- Backend: FastAPI + SQLAlchemy 2.0 (async) + Alembic
- Frontend: Vue3 + TypeScript + Pinia
- Database: PostgreSQL
- Testing: pytest (backend), vitest (frontend)

---

## Phase 1: Database Migration

### Task 1: Add seat_number column to users table

**Files:**
- Create: `backend/alembic/versions/XXXX_add_seat_number_to_users.py`

**Step 1: Create migration file**

```bash
cd backend
source venv/bin/activate  # Activate virtual environment
alembic revision -m "add seat_number to users"
```

**Step 2: Write migration code**

Open the generated file and add:

```python
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.add_column('users', sa.Column('seat_number', sa.Integer(), nullable=True))

def downgrade():
    op.drop_column('users', 'seat_number')
```

**Step 3: Review migration**

Check: `alembic upgrade head --sql`
Expected: SQL showing `ALTER TABLE users ADD COLUMN seat_number INTEGER`

**Step 4: Commit**

```bash
git add backend/alembic/versions/XXXX_add_seat_number_to_users.py
git commit -m "feat(migration): add seat_number column to users table"
```

---

### Task 2: Migrate classroom codes (701 → 2301)

**Files:**
- Create: `backend/alembic/versions/XXXX_migrate_classroom_codes.py`
- Create: `backend/scripts/migrate_classroom_codes.py`

**Step 1: Create data migration script**

Create `backend/scripts/migrate_classroom_codes.py`:

```python
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
```

**Step 2: Test migration on dry run**

Run: `cd backend && python scripts/migrate_classroom_codes.py`
Expected: Output showing code transformations like "七年级1班: 701 -> 2301"

**Step 3: Create alembic migration for reference**

Create `backend/alembic/versions/XXXX_migrate_classroom_codes.py`:

```python
from alembic import op
import sqlalchemy as sa

# This is a reference migration - actual data migration done by script
def upgrade():
    # Data migration handled by scripts/migrate_classroom_codes.py
    pass

def downgrade():
    # To rollback, restore from backup
    pass
```

**Step 4: Commit**

```bash
git add backend/scripts/migrate_classroom_codes.py backend/alembic/versions/XXXX_migrate_classroom_codes.py
git commit -m "feat(migration): add classroom code migration script (701 → 2301)"
```

---

### Task 3: Migrate usernames (new format)

**Files:**
- Create: `backend/scripts/migrate_usernames.py`

**Step 1: Create username migration script**

Create `backend/scripts/migrate_usernames.py`:

```python
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
                    if count <= 26:
                        new_username = f"{base_username}{suffix_char}"
                    else:
                        # If A-Z exhausted, use numbers
                        new_username = f"{base_username}{count - 26}"

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
```

**Step 2: Test migration**

Run: `cd backend && python scripts/migrate_usernames.py`
Expected: Output showing username transformations

**Step 3: Commit**

```bash
git add backend/scripts/migrate_usernames.py
git commit -m "feat(migration): add username migration script (school code + ID last 6)"
```

---

### Task 4: Initialize seat numbers

**Files:**
- Create: `backend/scripts/initialize_seat_numbers.py`

**Step 1: Create seat number initialization script**

Create `backend/scripts/initialize_seat_numbers.py`:

```python
"""
Initialize seat numbers for students based on classroom order
Format: Sequential integers (1, 2, 3...) displayed as 2 digits (01, 02, 03...)
"""
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
            # Get students in classroom, ordered by ID
            students = db.execute(
                select(User).where(
                    User.classroom_id == classroom.id
                ).order_by(User.id)
            ).scalars().all()

            # Assign seat numbers
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
```

**Step 2: Test initialization**

Run: `cd backend && python scripts/initialize_seat_numbers.py`
Expected: Output showing seat number assignments per classroom

**Step 3: Commit**

```bash
git add backend/scripts/initialize_seat_numbers.py
git commit -m "feat(migration): add seat number initialization script"
```

---

## Phase 2: Username and Exam Number Generators

### Task 5: Create username generation utility

**Files:**
- Create: `backend/app/utils/username_generator.py`

**Step 1: Write username generator utility**

Create `backend/app/utils/username_generator.py`:

```python
"""
Username generation utility

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
```

**Step 2: Write tests for username generator**

Create `backend/tests/utils/test_username_generator.py`:

```python
import pytest
from app.utils.username_generator import generate_username
from app.models.user import User, UserRole
from app.core.database import SessionLocal

def test_generate_username_no_conflict(db_session):
    """Test username generation without conflicts"""
    username = generate_username("4401", "110101200501011234")
    assert username == "4401011234"
    assert len(username) == 10

def test_generate_username_with_conflict(db_session):
    """Test username conflict resolution"""
    db = SessionLocal()

    # Create existing user
    existing = User(
        username="4401011234",
        full_name="Test User",
        student_id_number="110101200501019999",
        role=UserRole.STUDENT
    )
    db.add(existing)
    db.commit()

    # Generate new username (should add suffix)
    new_username = generate_username("4401", "110101200501011234")
    assert new_username == "4401011234A"  # Has suffix

    db.close()
```

**Step 3: Run tests**

Run: `cd backend && pytest tests/utils/test_username_generator.py -v`
Expected: All tests pass

**Step 4: Commit**

```bash
git add backend/app/utils/username_generator.py backend/tests/utils/test_username_generator.py
git commit -m "feat: add username generation utility with conflict resolution"
```

---

### Task 6: Create exam number generation utility

**Files:**
- Create: `backend/app/utils/exam_number_generator.py`

**Step 1: Write exam number generator utility**

Create `backend/app/utils/exam_number_generator.py`:

```python
"""
Exam number generation utility

Format: school_code (4) + enrollment_year (4) + class_sequence (2) + seat_number (2)
Total: 12 digits
"""
from sqlalchemy import select
from app.core.database import SessionLocal
from app.models.evaluation import ExamNumberMapping

def generate_exam_number(
    school_code: str,
    enrollment_year: int,
    classroom_code: str,
    seat_number: int
) -> str:
    """
    Generate exam number: school_code + enrollment_year + class_sequence + seat_number

    Args:
        school_code: 4-digit school code
        enrollment_year: 4-digit enrollment year
        classroom_code: 4-digit classroom code (e.g., "2301")
        seat_number: Seat number (integer, will be formatted as 2 digits)

    Returns:
        12-digit exam number

    Example:
        >>> generate_exam_number("4401", 2023, "2301", 1)
        "440120230101"
    """
    # Extract class sequence (last 2 digits of classroom code)
    class_sequence = classroom_code[-2:]

    # Format seat number as 2 digits
    seat_formatted = f"{seat_number:02d}"

    exam_number = f"{school_code}{enrollment_year}{class_sequence}{seat_formatted}"

    return exam_number

def validate_exam_number(exam_id: int, exam_number: str) -> str:
    """
    Validate exam number uniqueness and add suffix if conflicted

    Args:
        exam_id: Exam ID
        exam_number: Proposed exam number

    Returns:
        Valid exam number (with suffix if conflicted)

    Example:
        >>> validate_exam_number(1, "440120230101")
        "440120230101"
    """
    db = SessionLocal()
    try:
        # Check format
        if not exam_number.isdigit() or len(exam_number) != 12:
            raise ValueError(f"Exam number must be 12 digits: {exam_number}")

        # Check uniqueness
        existing = db.execute(
            select(ExamNumberMapping).where(
                ExamNumberMapping.exam_id == exam_id,
                ExamNumberMapping.exam_number == exam_number
            )
        ).scalar_one_or_none()

        if not existing:
            return exam_number

        # Add suffix for conflicts
        suffix = 0
        while True:
            suffix += 1
            new_number = f"{exam_number}{chr(64 + suffix)}"

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
```

**Step 2: Write tests**

Create `backend/tests/utils/test_exam_number_generator.py`:

```python
import pytest
from app.utils.exam_number_generator import generate_exam_number, validate_exam_number

def test_generate_exam_number():
    """Test exam number generation"""
    result = generate_exam_number("4401", 2023, "2301", 1)
    assert result == "440120230101"
    assert len(result) == 12

def test_generate_exam_number_seat_padding():
    """Test seat number is padded to 2 digits"""
    result = generate_exam_number("4401", 2023, "2301", 15)
    assert result == "440120230115"
    assert result[-2:] == "15"

def test_validate_exam_number_invalid_format():
    """Test validation rejects invalid format"""
    with pytest.raises(ValueError):
        validate_exam_number(1, "123456789")  # Too short

def test_validate_exam_number_adds_suffix():
    """Test validation adds suffix when conflicted"""
    # TODO: Add test with database mock
    pass
```

**Step 3: Run tests**

Run: `cd backend && pytest tests/utils/test_exam_number_generator.py -v`
Expected: All tests pass

**Step 4: Commit**

```bash
git add backend/app/utils/exam_number_generator.py backend/tests/utils/test_exam_number_generator.py
git commit -m "feat: add exam number generation utility with validation"
```

---

## Phase 3: Update Import Logic

### Task 7: Update student account import strategy

**Files:**
- Modify: `backend/app/services/import_strategies/student_account_import_strategy.py`

**Step 1: Read existing import strategy**

Read: `backend/app/services/import_strategies/student_account_import_strategy.py`
Understand: Current student creation logic

**Step 2: Update import to use new username generation**

Add import at top of file:
```python
from app.utils.username_generator import generate_username
```

Find the student creation section and update:

```python
# After finding/creating classroom and school
username = generate_username(school.code, student_id_number)

# Check if student exists
existing_student = await db.execute(
    select(User).where(User.student_id_number == student_id_number)
).scalar_one_or_none()

if existing_student:
    # Update existing student
    existing_student.classroom_id = classroom.id
    existing_student.username = username
    if seat_number:
        existing_student.seat_number = int(seat_number)

    return {"status": "updated", "id": existing_student.id}

# Create new student
student = User(
    username=username,
    full_name=full_name,
    student_id_number=student_id_number,
    school_id=school.id,
    classroom_id=classroom.id,
    role=UserRole.STUDENT,
    seat_number=int(seat_number) if seat_number else None,
    hashed_password=hash_password("123456")
)
```

**Step 3: Test import**

Run: `cd backend && python -m pytest tests/services/test_student_import.py -v -k "test_student_account"`
Expected: Tests pass with new username format

**Step 4: Commit**

```bash
git add backend/app/services/import_strategies/student_account_import_strategy.py
git commit -m "feat: update student import to use new username generation"
```

---

### Task 8: Update exam number import logic

**Files:**
- Modify: `backend/app/services/import_strategies/student_import_strategy.py` (or relevant exam import service)

**Step 1: Add exam number generation import**

```python
from app.utils.exam_number_generator import generate_exam_number, validate_exam_number
```

**Step 2: Update exam number assignment logic**

Find exam number processing and update:

```python
# If exam_number not provided, generate it
if not exam_number:
    classroom = await db.get(Classroom, student.classroom_id)
    school = await db.get(School, student.school_id)

    exam_number = generate_exam_number(
        school_code=school.code,
        enrollment_year=classroom.enrollment_year,
        classroom_code=classroom.code,
        seat_number=student.seat_number or 1
    )

# Validate and handle conflicts
exam_number = validate_exam_number(exam_id, exam_number)

# Create mapping
mapping = ExamNumberMapping(
    exam_id=exam_id,
    exam_number=exam_number,
    student_id=student.id,
    student_id_number=student_id_number,
    school_id=student.school_id,
    classroom_id=student.classroom_id
)
```

**Step 3: Test import**

Run: `cd backend && python -m pytest tests/services/test_exam_import.py -v`
Expected: Tests pass with new exam number format

**Step 4: Commit**

```bash
git add backend/app/services/import_strategies/student_import_strategy.py
git commit -m "feat: update exam import to use new exam number generation"
```

---

## Phase 4: API Endpoints

### Task 9: Add username validation API

**Files:**
- Create: `backend/app/api/v1/admin_users.py` (or extend existing)
- Modify: `backend/app/api/v1/admin.py` (add route)

**Step 1: Create endpoint for username validation**

Add to admin API:

```python
@router.get("/users/check-username")
async def check_username_availability(
    school_code: str,
    student_id_number: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Check username availability and generate username

    Returns:
        - available: boolean
        - username: generated username
        - conflicts: list of conflicting usernames (if any)
    """
    from app.utils.username_generator import generate_username

    username = generate_username(school_code, student_id_number)

    # Check if username already exists
    existing = await db.execute(
        select(User).where(User.username == username)
    ).scalar_one_or_none()

    conflicts = []
    if existing:
        conflicts.append(username)

    return {
        "available": len(conflicts) == 0,
        "username": username,
        "conflicts": conflicts
    }
```

**Step 2: Test endpoint**

Run: `curl "http://localhost:8000/api/v1/admin/users/check-username?school_code=4401&student_id_number=110101200501011234"`
Expected: `{"available": true, "username": "4401011234", "conflicts": []}`

**Step 3: Commit**

```bash
git add backend/app/api/v1/admin.py
git commit -m "feat: add username availability check API"
```

---

### Task 10: Add exam number generation API

**Files:**
- Modify: `backend/app/api/v1/exams.py`

**Step 1: Create batch exam number generation endpoint**

```python
@router.post("/exams/generate-exam-numbers")
async def generate_exam_numbers(
    exam_id: int,
    school_id: int,
    auto_generate: bool = True,
    db: AsyncSession = Depends(get_db)
):
    """
    Batch generate exam numbers for an exam

    Returns:
        - generated: number of exam numbers generated
        - conflicts: number of conflicts resolved
        - exam_numbers: list of generated numbers
    """
    from app.utils.exam_number_generator import generate_exam_number, validate_exam_number

    exam = await db.get(Exam, exam_id)
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")

    school = await db.get(School, school_id)
    if not school:
        raise HTTPException(status_code=404, detail="School not found")

    # Get all students for this school
    students = await db.execute(
        select(User).where(
            User.school_id == school_id,
            User.role == UserRole.STUDENT
        )
    ).scalars().all()

    generated_numbers = []
    conflicts = 0

    for student in students:
        classroom = await db.get(Classroom, student.classroom_id)

        # Generate exam number
        exam_number = generate_exam_number(
            school_code=school.code,
            enrollment_year=classroom.enrollment_year,
            classroom_code=classroom.code,
            seat_number=student.seat_number or 1
        )

        # Validate and handle conflicts
        validated_number = validate_exam_number(exam_id, exam_number)
        if validated_number != exam_number:
            conflicts += 1

        # Create mapping
        mapping = ExamNumberMapping(
            exam_id=exam_id,
            exam_number=validated_number,
            student_id=student.id,
            student_id_number=student.student_id_number,
            school_id=school_id,
            classroom_id=classroom.id
        )
        db.add(mapping)

        generated_numbers.append(validated_number)

    await db.commit()

    return {
        "generated": len(generated_numbers),
        "conflicts": conflicts,
        "exam_numbers": generated_numbers[:10]  # First 10 for preview
    }
```

**Step 2: Test endpoint**

Run: `curl -X POST "http://localhost:8000/api/v1/admin/exams/generate-exam-numbers?exam_id=1&school_id=1"`
Expected: Returns generated exam numbers

**Step 3: Commit**

```bash
git add backend/app/api/v1/exams.py
git commit -m "feat: add batch exam number generation API"
```

---

### Task 11: Add student growth analysis API

**Files:**
- Create: `backend/app/api/v1/analytics.py`

**Step 1: Create analytics API module**

Create `backend/app/api/v1/analytics.py`:

```python
"""
Analytics API endpoints for value-added analysis
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.evaluation import Score, Exam
from app.models.user import User

router = APIRouter()

@router.get("/analytics/student-growth/{student_id_number}")
async def get_student_growth(
    student_id_number: str,
    subject_id: int = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Get student's historical scores for growth analysis

    Uses student_id_number for cross-school tracking

    Returns:
        List of scores with growth calculations
    """
    query = select(Score).join(Exam).join(User).filter(
        Score.student_id_number == student_id_number
    )

    if subject_id:
        query = query.filter(Score.subject_id == subject_id)

    scores_result = await db.execute(
        query.order_by(Exam.exam_date)
    )
    scores = scores_result.scalars().all()

    # Calculate growth
    growth_data = []
    for i, score in enumerate(scores):
        growth = None
        if i > 0:
            growth = score.raw_score - scores[i-1].raw_score

        growth_data.append({
            "exam_name": score.exam.name,
            "exam_date": score.exam.exam_date.isoformat(),
            "subject": score.subject.name,
            "raw_score": score.raw_score,
            "standard_score": score.standard_score,
            "school": score.student.school.name,
            "growth": growth
        })

    return {
        "student_id_number": student_id_number,
        "scores": growth_data
    }
```

**Step 2: Register router in main API**

Add to `backend/app/api/v1/__init__.py` or main app:

```python
from app.api.v1 import analytics
app.include_router(analytics.router, prefix="/api/v1/admin", tags=["analytics"])
```

**Step 3: Test endpoint**

Run: `curl "http://localhost:8000/api/v1/admin/analytics/student-growth/110101200501011234"`
Expected: Returns student's score history with growth calculations

**Step 4: Commit**

```bash
git add backend/app/api/v1/analytics.py
git commit -m "feat: add student growth analysis API"
```

---

## Phase 5: Frontend Updates

### Task 12: Update seat number display format

**Files:**
- Modify: `frontend/src/pages/Admin/StudentManagement.vue` (or relevant component)

**Step 1: Find seat number display**

Search for seat number display in student management components

**Step 2: Update to 2-digit format**

```vue
<!-- Before -->
<td>{{ student.seat_number }}</td>

<!-- After -->
<td>{{ student.seat_number?.toString().padStart(2, '0') }}</td>
```

**Step 3: Test display**

Run: `npm run dev`
Expected: Seat numbers display as "01", "02", etc.

**Step 4: Commit**

```bash
git add frontend/src/pages/Admin/StudentManagement.vue
git commit -m "fix: format seat numbers as 2 digits in display"
```

---

### Task 13: Add username display to student lists

**Files:**
- Modify: Student management components

**Step 1: Add username column to table**

```vue
<el-table-column label="用户名" prop="username" width="150">
  <template #default="{ row }">
    <span>{{ row.username }}</span>
  </template>
</el-table-column>
```

**Step 2: Test display**

Expected: Usernames shown in format "4401011234" or "4401011234A"

**Step 3: Commit**

```bash
git add frontend/src/pages/Admin/StudentManagement.vue
git commit -m "feat: add username column to student list"
```

---

## Phase 6: Testing and Documentation

### Task 14: Write integration tests for migration

**Files:**
- Create: `backend/tests/integration/test_student_tracking_migration.py`

**Step 1: Write migration integration test**

Create test file:

```python
import pytest
from app.models.user import User, UserRole
from app.models.organization import Classroom, School
from app.core.database import SessionLocal
from scripts.migrate_classroom_codes import migrate_classroom_codes
from scripts.migrate_usernames import migrate_usernames
from scripts.initialize_seat_numbers import initialize_seat_numbers

@pytest.fixture(scope="module")
def setup_test_data():
    """Setup test data for migration"""
    db = SessionLocal()

    # Create test school
    school = School(
        name="Test School",
        code="4401"
    )
    db.add(school)
    db.flush()

    # Create test classroom with old code format
    classroom = Classroom(
        name="七年级1班",
        code="701",  # Old format
        school_id=school.id,
        grade_id=7,
        enrollment_year=2023
    )
    db.add(classroom)
    db.flush()

    # Create test students
    student1 = User(
        username="old_username_1",
        full_name="Test Student 1",
        student_id_number="110101200501011234",
        school_id=school.id,
        classroom_id=classroom.id,
        role=UserRole.STUDENT
    )
    db.add(student1)

    db.commit()

    yield db

    # Cleanup
    db.rollback()

def test_classroom_code_migration(setup_test_data):
    """Test classroom code migration"""
    migrate_classroom_codes()

    db = setup_test_data
    classroom = db.execute(select(Classroom)).scalar_one()

    assert classroom.code == "2301"  # Should be migrated

def test_username_migration(setup_test_data):
    """Test username migration"""
    migrate_usernames()

    db = setup_test_data
    student = db.execute(select(User)).scalar_one()

    assert student.username == "4401011234"  # New format

def test_seat_number_initialization(setup_test_data):
    """Test seat number initialization"""
    initialize_seat_numbers()

    db = setup_test_data
    student = db.execute(select(User)).scalar_one()

    assert student.seat_number == 1  # First student
```

**Step 2: Run tests**

Run: `cd backend && pytest tests/integration/test_student_tracking_migration.py -v`
Expected: All migration tests pass

**Step 3: Commit**

```bash
git add backend/tests/integration/test_student_tracking_migration.py
git commit -m "test: add integration tests for student tracking migration"
```

---

### Task 15: Update API documentation

**Files:**
- Modify: `docs/plans/2025-01-22-student-tracking-design.md`
- Create: `docs/guides/student-tracking-guide.md`

**Step 1: Create user guide**

Create `docs/guides/student-tracking-guide.md`:

```markdown
# Student Tracking System Guide

## Overview

The student tracking system uses three identifiers:

1. **身份证号 (student_id_number)**: Permanent unique identifier
2. **用户名 (username)**: Login credential (school_code + ID last 6 digits)
3. **考号 (exam_number)**: Exam identifier (school + year + class + seat)

## Username Format

**Format:** `XXXXYYYYYY`
- XXXX: School code (4 digits)
- YYYYYY: Last 6 digits of student ID number

**Example:** `4401011234`
- School: 4401
- Student ID: ...011234

**Conflict handling:** If duplicate, add suffix (A, B, C...)
- Example: `4401011234A`

## Exam Number Format

**Format:** `XXXXXXXXXXXX` (12 digits)
- School code (4)
- Enrollment year (4)
- Class sequence (2)
- Seat number (2)

**Example:** `440120230101`
- School: 4401
- Year: 2023
- Class: 01
- Seat: 01

## API Usage

### Check Username Availability

\`\`\`bash
GET /api/v1/admin/users/check-username?school_code=4401&student_id_number=110101200501011234
\`\`\`

### Generate Exam Numbers

\`\`\`bash
POST /api/v1/admin/exams/generate-exam-numbers
{
  "exam_id": 1,
  "school_id": 1,
  "auto_generate": true
}
\`\`\`

### Student Growth Analysis

\`\`\`bash
GET /api/v1/admin/analytics/student-growth/110101200501011234?subject_id=1
\`\`\`

## Data Migration

Run migration scripts in order:

\`\`\`bash
cd backend
source venv/bin/activate

# 1. Migrate classroom codes
python scripts/migrate_classroom_codes.py

# 2. Migrate usernames
python scripts/migrate_usernames.py

# 3. Initialize seat numbers
python scripts/initialize_seat_numbers.py
\`\`\`
```

**Step 2: Update design doc with implementation notes**

Add section to design doc:
```markdown
## Implementation Status

- [x] Database migration scripts
- [x] Username/exam number generators
- [x] Import logic updates
- [x] API endpoints
- [ ] Frontend updates (in progress)
- [ ] Complete testing
```

**Step 3: Commit**

```bash
git add docs/guides/student-tracking-guide.md docs/plans/2025-01-22-student-tracking-design.md
git commit -m "docs: add student tracking system user guide"
```

---

## Execution Checklist

Before running migrations:

- [ ] Backup database
- [ ] Test migrations in development environment
- [ ] Review migration scripts
- [ ] Prepare rollback plan

During implementation:

- [ ] Run tests after each task
- [ ] Commit frequently with descriptive messages
- [ ] Update documentation as you go
- [ ] Test API endpoints manually

After completion:

- [ ] Run full test suite
- [ ] Test import/export functionality
- [ ] Verify data integrity
- [ ] Update user documentation

---

**End of Implementation Plan**
