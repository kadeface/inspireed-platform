# Enum Type Best Practices

A comprehensive guide for using enum types in FastAPI + SQLAlchemy + PostgreSQL applications.

---

## Table of Contents

1. [The Problem](#1-the-problem)
2. [Solution Architecture](#2-solution-architecture)
3. [Implementation Approaches](#3-implementation-approaches)
4. [Best Practices](#4-best-practices)
5. [Migration from Strings](#5-migration-from-strings)
6. [Common Pitfalls](#6-common-pitfalls)

---

## 1. The Problem

### The Case Mismatch Issue

```python
# ❌ BAD: Inconsistent enum values

# Python Enum (uppercase names, lowercase values)
class Status(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"

# PostgreSQL ENUM (must match values)
CREATE TYPE status_enum AS ENUM ('active', 'inactive');

# FastAPI Response (what goes in JSON)
{"status": "active"}

# What happens when you mess up:
db.session.query(Model).filter(Model.status == Status.ACTIVE)  # Wrong!
# Should be: .filter(Model.status == "active")
```

### Why This Happens

| Layer | Typical Convention | Conflict Point |
|-------|-------------------|----------------|
| **Python Enum** | Name: `ACTIVE`, Value: `"active"` | Using `.value` vs using name directly |
| **PostgreSQL** | Stores values: `'active'` | Case-sensitive string matching |
| **FastAPI JSON** | Lowercase: `"active"` | API consumers expect lowercase |
| **SQLAlchemy** | Mixed approaches | ORM layer can be confusing |

---

## 2. Solution Architecture

### Recommended Pattern

```python
from enum import Enum
from sqlalchemy import Enum as SQLEnum

# ✅ GOOD: Single source of truth
class CompletionStatus(str, Enum):
    """Enum for completion status."""
    COMPLETED = "completed"
    SKIPPED = "skipped"

    def __str__(self):
        return self.value

# ✅ GOOD: Database uses the enum directly
class Completion(Base):
    status: Mapped[CompletionStatus] = mapped_column(
        SQLEnum(CompletionStatus, name="completion_status", create_type=True),
        default=CompletionStatus.COMPLETED,
        nullable=False
    )

# ✅ GOOD: Pydantic uses the same enum
class CompletionResponse(BaseModel):
    status: CompletionStatus

# ✅ GOOD: Consistent usage everywhere
completion = Completion(
    habit_id=1,
    completed_date="2025-01-15",
    status=CompletionStatus.COMPLETED,  # ✅ Enum instance
    notes="Great job!"
)

# Database stores: 'completed'
# JSON response: {"status": "completed"}
# Type checking: ✅ Pass
```

---

## 3. Implementation Approaches

### Approach 1: Native SQLAlchemy Enum (Recommended)

**Pros:**
- Type-safe
- Database-level validation
- Automatic ENUM type creation
- Works with PostgreSQL's native ENUM

```python
# models.py
from enum import Enum
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column

class CompletionStatus(str, Enum):
    """Status of a habit completion."""
    COMPLETED = "completed"
    SKIPPED = "skipped"

class Completion(Base):
    __tablename__ = "completions"

    id: Mapped[int] = mapped_column(primary_key=True)
    habit_id: Mapped[int] = mapped_column(ForeignKey("habits.id"))
    completed_date: Mapped[str] = mapped_column(String(10))
    status: Mapped[CompletionStatus] = mapped_column(
        SQLEnum(
            CompletionStatus,
            name="completion_status",
            create_type=True,  # Create ENUM type in PostgreSQL
            values_callable=lambda obj: [e.value for e in obj]
        ),
        default=CompletionStatus.COMPLETED,
        nullable=False
    )
```

**Generated SQL (PostgreSQL):**
```sql
CREATE TYPE completion_status AS ENUM ('completed', 'skipped');

CREATE TABLE completions (
    id SERIAL PRIMARY KEY,
    habit_id INTEGER NOT NULL,
    completed_date VARCHAR(10) NOT NULL,
    status completion_status NOT NULL DEFAULT 'completed'
);
```

### Approach 2: String with CheckConstraint (SQLite Compatible)

**Pros:**
- Works with SQLite (no ENUM support)
- Simple and straightforward
- No database type creation needed

```python
# models.py
from enum import Enum
from sqlalchemy import String, CheckConstraint

class CompletionStatus(str, Enum):
    """Status of a habit completion."""
    COMPLETED = "completed"
    SKIPPED = "skipped"

class Completion(Base):
    __tablename__ = "completions"

    status: Mapped[str] = mapped_column(
        String(10),
        default=CompletionStatus.COMPLETED.value,
        nullable=False
    )

    __table_args__ = (
        CheckConstraint(
            f"status IN ({', '.join([f\"'{e.value}'\" for e in CompletionStatus])})",
            name="valid_status"
        ),
    )
```

### Approach 3: Pydantic Enum + SQLAlchemy String (Maximum Flexibility)

**Pros:**
- Pydantic validates at API layer
- Database stores simple strings
- Easy to migrate between databases
- No ENUM type management

```python
# enums.py
from enum import Enum

class CompletionStatus(str, Enum):
    """Status of a habit completion."""
    COMPLETED = "completed"
    SKIPPED = "skipped"

# models.py
class Completion(Base):
    __tablename__ = "completions"

    status: Mapped[str] = mapped_column(
        String(10),
        default=CompletionStatus.COMPLETED.value,
        nullable=False
    )

    __table_args__ = (
        CheckConstraint("status IN ('completed', 'skipped')", name="valid_status"),
    )

# schemas.py
from pydantic import BaseModel, Field

class CompletionResponse(BaseModel):
    status: CompletionStatus = Field(..., description="Completion status")

# routers.py
@router.post("/complete")
def complete_habit(
    habit_id: int,
    completion_data: CompletionCreate,
    db: Session = Depends(get_db)
):
    completion = Completion(
        habit_id=habit_id,
        completed_date=completion_data.date,
        status=CompletionStatus.COMPLETED.value,  # Enum -> string
        notes=completion_data.notes
    )
    db.add(completion)
    db.commit()
    db.refresh(completion)

    # Response uses enum automatically
    return CompletionResponse(
        date=completion.completed_date,
        status=CompletionStatus(completion.status),  # string -> Enum
        notes=completion.notes
    )
```

---

## 4. Best Practices

### Rule 1: Single Source of Truth

```python
# ❌ BAD: Duplicate enum definitions

# enums.py
class Status(Enum):
    ACTIVE = "active"

# models.py
class StatusModel(Enum):
    ACTIVE = "active"

# schemas.py
class StatusSchema(Enum):
    ACTIVE = "active"

# ✅ GOOD: One enum definition, import everywhere

# common/enums.py
class Status(str, Enum):
    ACTIVE = "active"

# models.py
from common.enums import Status

# schemas.py
from common.enums import Status
```

### Rule 2: Use `str` as Enum Base

```python
# ❌ BAD: Regular enum
class Status(Enum):
    ACTIVE = "active"

# Problem: JSON serialization fails
status.value  # Need .value everywhere
json.dumps({"status": status})  # Error!

# ✅ GOOD: String enum
class Status(str, Enum):
    ACTIVE = "active"

# Works with JSON directly
json.dumps({"status": status})  # {"status": "active"}
```

### Rule 3: Enum Values Are Always Lowercase

```python
# ❌ BAD: Mixed case values
class Status(str, Enum):
    ACTIVE = "Active"      # ❌ Don't do this
    COMPLETED = "Completed"  # ❌ Or this

# ✅ GOOD: Lowercase values
class Status(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
```

**Why:**
- JSON APIs conventionally use lowercase
- PostgreSQL ENUM values are case-sensitive but typically lowercase
- Avoids confusion between enum name (`ACTIVE`) and value (`active`)

### Rule 4: Use Enum in Pydantic Models

```python
# ✅ GOOD: Pydantic validates enum values
from pydantic import BaseModel, ValidationError

class CompletionResponse(BaseModel):
    status: CompletionStatus

try:
    response = CompletionResponse(status="invalid")
except ValidationError as e:
    # Error: value is not a valid enumeration member
    print(e)
```

### Rule 5: Database Migrations

```python
# ❌ BAD: Changing enum values without migration
class Status(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"  # New value added

# PostgreSQL will error if you try to insert 'archived'

# ✅ GOOD: Create migration to alter enum type
# alembic revision --autogenerate -m "add archived status"

# In migration file:
def upgrade():
    op.execute("ALTER TYPE status_enum ADD VALUE 'archived' BEFORE 'inactive'")

def downgrade():
    # Can't easily remove enum values in PostgreSQL
    pass
```

---

## 5. Migration from Strings

### Step 1: Create Enum Definition

```python
# app/enums.py
from enum import Enum

class CompletionStatus(str, Enum):
    """Status of a habit completion."""
    COMPLETED = "completed"
    SKIPPED = "skipped"
```

### Step 2: Update SQLAlchemy Model

```python
# Before (String)
status: Mapped[str] = mapped_column(
    String(10),
    default="completed",
    nullable=False
)

# After (Enum)
from sqlalchemy import Enum as SQLEnum

status: Mapped[CompletionStatus] = mapped_column(
    SQLEnum(CompletionStatus, name="completion_status", create_type=True),
    default=CompletionStatus.COMPLETED,
    nullable=False
)
```

### Step 3: Update Pydantic Schemas

```python
# Before
class CompletionResponse(BaseModel):
    status: str

# After
class CompletionResponse(BaseModel):
    status: CompletionStatus
```

### Step 4: Update Business Logic

```python
# Before
if completion.status == "completed":
    streak += 1

# After
if completion.status == CompletionStatus.COMPLETED:
    streak += 1
```

### Step 5: Create Database Migration (Alembic)

```python
# alembic/versions/001_add_completion_status_enum.py
from alembic import op
import sqlalchemy as sa

def upgrade():
    # Create enum type
    op.execute("CREATE TYPE completion_status AS ENUM ('completed', 'skipped')")

    # Alter column to use enum
    op.execute("""
        ALTER TABLE completions
        ALTER COLUMN status TYPE completion_status
        USING status::completion_status
    """)

def downgrade():
    # Convert back to VARCHAR
    op.execute("""
        ALTER TABLE completions
        ALTER COLUMN status TYPE VARCHAR(10)
        USING status::text
    """)

    # Drop enum type
    op.execute("DROP TYPE completion_status")
```

---

## 6. Common Pitfalls

### Pitfall 1: Forgetting `.value` in Database Operations

```python
# ❌ BAD
completion = Completion(
    status=CompletionStatus.COMPLETED  # Wrong for non-Enum column
)

# ✅ GOOD (when column is String)
completion = Completion(
    status=CompletionStatus.COMPLETED.value
)

# ✅ BEST (when column is SQLEnum)
completion = Completion(
    status=CompletionStatus.COMPLETED  # SQLAlchemy handles it
)
```

### Pitfall 2: Mixing Enum Names and Values

```python
# ❌ BAD
if completion.status == CompletionStatus.COMPLETED:
    pass
elif completion.status == "COMPLETED":  # ❌ Wrong!
    pass

# ✅ GOOD
if completion.status == CompletionStatus.COMPLETED:
    pass
elif completion.status == "completed":  # Still wrong enum value!
    pass

# ✅ BEST - Always use Enum constants
if completion.status == CompletionStatus.COMPLETED:
    pass
elif completion.status == CompletionStatus.SKIPPED:
    pass
```

### Pitfall 3: JSON Serialization Issues

```python
# ❌ BAD - Regular Enum doesn't serialize well
from enum import Enum

class Status(Enum):
    ACTIVE = "active"

json.dumps({"status": Status.ACTIVE})  # TypeError: Object of type Status is not JSON serializable

# ✅ GOOD - String Enum works
class Status(str, Enum):
    ACTIVE = "active"

json.dumps({"status": Status.ACTIVE})  # {"status": "active"}
```

### Pitfall 4: ENUM Type Name Conflicts

```python
# ❌ BAD - Multiple tables using same enum with different names
class Completion1(Base):
    status: Mapped[CompletionStatus] = mapped_column(
        SQLEnum(CompletionStatus, name="status_enum1")
    )

class Completion2(Base):
    status: Mapped[CompletionStatus] = mapped_column(
        SQLEnum(CompletionStatus, name="status_enum2")
    )

# Creates two identical enum types in PostgreSQL

# ✅ GOOD - Shared enum type
SHARED_ENUM_NAME = "completion_status"

class Completion1(Base):
    status: Mapped[CompletionStatus] = mapped_column(
        SQLEnum(CompletionStatus, name=SHARED_ENUM_NAME)
    )

class Completion2(Base):
    status: Mapped[CompletionStatus] = mapped_column(
        SQLEnum(CompletionStatus, name=SHARED_ENUM_NAME)
    )
```

### Pitfall 5: Hardcoding String Values

```python
# ❌ BAD - Magic strings everywhere
if completion.status == "completed":
    streak += 1

response = {"status": "completed"}

# ✅ GOOD - Use Enum
if completion.status == CompletionStatus.COMPLETED:
    streak += 1

response = {"status": CompletionStatus.COMPLETED}
```

---

## Complete Working Example

### Project Structure

```
project/
├── app/
│   ├── enums.py          # Enum definitions
│   ├── models.py         # SQLAlchemy models
│   ├── schemas.py        # Pydantic schemas
│   └── routers.py        # FastAPI routes
```

### enums.py

```python
from enum import Enum


class CompletionStatus(str, Enum):
    """Status of a habit completion."""
    COMPLETED = "completed"
    SKIPPED = "skipped"

    @classmethod
    def from_string(cls, value: str) -> "CompletionStatus":
        """Convert string to enum, raising ValueError if invalid."""
        try:
            return cls(value)
        except ValueError:
            valid_values = ", ".join([e.value for e in cls])
            raise ValueError(f"Invalid status '{value}'. Must be one of: {valid_values}")
```

### models.py

```python
from sqlalchemy import Enum as SQLEnum, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.enums import CompletionStatus


class Completion(Base):
    __tablename__ = "completions"

    id: Mapped[int] = mapped_column(primary_key=True)
    habit_id: Mapped[int] = mapped_column(ForeignKey("habits.id"))
    completed_date: Mapped[str] = mapped_column(String(10))
    status: Mapped[CompletionStatus] = mapped_column(
        SQLEnum(
            CompletionStatus,
            name="completion_status",
            create_type=True,
            values_callable=lambda obj: [e.value for e in obj]
        ),
        default=CompletionStatus.COMPLETED,
        nullable=False
    )
    notes: Mapped[str | None] = mapped_column(String(500))
```

### schemas.py

```python
from pydantic import BaseModel, Field

from app.enums import CompletionStatus


class CompletionResponse(BaseModel):
    date: str
    status: CompletionStatus = Field(..., description="Completion status")
    notes: str | None = None

    class Config:
        json_schema_extra = {
            "example": {
                "date": "2025-01-15",
                "status": "completed",
                "notes": "Great job!"
            }
        }


class CompletionCreate(BaseModel):
    date: str
    notes: str | None = None
```

### routers.py

```python
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.enums import CompletionStatus
from app.models import Completion
from app.schemas import CompletionResponse


@router.post("/complete", response_model=CompletionResponse, status_code=status.HTTP_201_CREATED)
def complete_habit(
    habit_id: int,
    completion_data: CompletionCreate,
    db: Session = Depends(get_db),
) -> CompletionResponse:
    """Mark a habit as completed for a specific date."""
    habit = get_habit_or_404(habit_id, db)

    # Check if already exists
    existing = db.query(Completion).filter(
        Completion.habit_id == habit_id,
        Completion.completed_date == completion_data.date
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Habit already completed/skipped for {completion_data.date}"
        )

    # Create completion with enum
    completion = Completion(
        habit_id=habit.id,
        completed_date=completion_data.date,
        status=CompletionStatus.COMPLETED,  # ✅ Enum instance
        notes=completion_data.notes,
    )

    db.add(completion)
    db.commit()
    db.refresh(completion)

    # Response automatically serializes enum
    return CompletionResponse(
        date=completion.completed_date,
        status=completion.status,  # ✅ Enum instance
        notes=completion.notes,
    )


@router.post("/skip", response_model=CompletionResponse, status_code=status.HTTP_201_CREATED)
def skip_habit(
    habit_id: int,
    skip_data: CompletionCreate,
    db: Session = Depends(get_db),
) -> CompletionResponse:
    """Mark a habit as skipped for a specific date."""
    habit = get_habit_or_404(habit_id, db)

    # Check if already exists
    existing = db.query(Completion).filter(
        Completion.habit_id == habit_id,
        Completion.completed_date == skip_data.date
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Habit already completed/skipped for {skip_data.date}"
        )

    # Create completion with enum
    completion = Completion(
        habit_id=habit.id,
        completed_date=skip_data.date,
        status=CompletionStatus.SKIPPED,  # ✅ Different enum value
        notes=skip_data.notes,
    )

    db.add(completion)
    db.commit()
    db.refresh(completion)

    return CompletionResponse(
        date=completion.completed_date,
        status=completion.status,  # ✅ Enum instance
        notes=completion.notes,
    )
```

### Testing

```python
import pytest
from app.enums import CompletionStatus
from app.models import Completion


def test_enum_values():
    """Test enum values are correct."""
    assert CompletionStatus.COMPLETED.value == "completed"
    assert CompletionStatus.SKIPPED.value == "skipped"


def test_enum_from_string():
    """Test string to enum conversion."""
    status = CompletionStatus.from_string("completed")
    assert status == CompletionStatus.COMPLETED

    with pytest.raises(ValueError):
        CompletionStatus.from_string("invalid")


def test_completion_with_enum(db_session):
    """Test creating completion with enum."""
    completion = Completion(
        habit_id=1,
        completed_date="2025-01-15",
        status=CompletionStatus.COMPLETED,
        notes="Great job!"
    )
    db_session.add(completion)
    db_session.commit()
    db_session.refresh(completion)

    assert completion.status == CompletionStatus.COMPLETED
    assert isinstance(completion.status, CompletionStatus)


def test_api_returns_enum(client):
    """Test API response includes enum."""
    response = client.post(
        "/api/habits/1/complete",
        json={"date": "2025-01-15"}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "completed"  # JSON string
    assert CompletionStatus(data["status"]) == CompletionStatus.COMPLETED
```

---

## Summary Checklist

- [ ] Use `str, Enum` as base for all enums
- [ ] Keep enum values lowercase
- [ ] Define enums in a single location
- [ ] Use `SQLEnum` in SQLAlchemy models
- [ ] Use same enum in Pydantic schemas
- [ ] Always use enum constants, not string literals
- [ ] Test enum serialization/deserialization
- [ ] Create proper migrations for enum changes
- [ ] Document enum values in API docs
- [ ] Handle enum conversion errors gracefully

---

## Resources

- [Python Enum Documentation](https://docs.python.org/3/library/enum.html)
- [SQLAlchemy Enum Documentation](https://docs.sqlalchemy.org/en/20/core/type_basics.html#sqlalchemy.types.Enum)
- [PostgreSQL ENUM Documentation](https://www.postgresql.org/docs/current/datatype-enum.html)
- [Pydantic Enum Documentation](https://docs.pydantic.dev/latest/concepts/types/#enums)
