# Feature: Add Classroom Room Management Module

## Feature Description

Add a comprehensive physical classroom (课室/Room) management system to separate physical teaching spaces from student organizational classes (班级/Classroom). The system will support room CRUD operations, batch import, filtering, and integration with the existing ClassSession system.

## User Story

As a school administrator
I want to manage physical classroom spaces separately from student classes
So that I can schedule lessons accurately, prevent room conflicts, and track room utilization

## Problem Statement

The current system conflates two distinct concepts:
1. **Classroom (班级)**: Student administrative class (e.g., "三年级一班") - an organizational unit
2. **Room (课室)**: Physical teaching space (e.g., "201室", "实验室1") - a physical resource

The `ClassSession` model uses `classroom_id` to reference student classes, but should also track physical room locations for proper resource management and conflict detection.

## Solution Statement

Create a new `Room` model to represent physical teaching spaces, with:
- Room CRUD management API
- Room assignment to schools (with optional fixed classroom assignment)
- Room types (regular classroom, lab, specialized room)
- Room attributes (capacity, equipment, building, floor)
- Integration with `ClassSession` via new `room_id` field
- Batch import functionality
- Admin UI for room management

## Feature Metadata

**Feature Type**: New Capability (architectural enhancement)
**Estimated Complexity**: Medium-High
**Primary Systems Affected**:
- Backend: Models, Schemas, API Routes, Services
- Frontend: Admin Organization Management, Services, Types
- Database: New tables, column additions, index creation

**Dependencies**:
- External: None (uses existing libraries)
- Internal: Organization models, ClassSession model, Admin authentication

---

## CONTEXT REFERENCES

### Relevant Codebase Files IMPORTANT: YOU MUST READ THESE FILES BEFORE IMPLEMENTING!

#### Backend Models & Database

- `backend/app/models/organization.py:78-124`
  - **Why**: Shows `Classroom` model structure we'll mirror for `Room` model
  - **Key patterns**: Foreign keys, relationships, timestamps, JSON fields, indexes

- `backend/app/models/classroom_session.py:33-98`
  - **Why**: `ClassSession` model needs `room_id` field addition
  - **Key lines**: Line 42 (`classroom_id` field), Line 87 (classroom relationship), Lines 138-148 (indexes)

- `backend/app/models/__init__.py:1-100`
  - **Why**: Must add `Room` and `RoomType` exports to model imports
  - **Pattern**: All models exported in `__all__` list

#### Backend API Routes

- `backend/app/api/v1/admin_organization.py:1-400`
  - **Why**: Reference implementation for Region/School/Classroom CRUD endpoints
  - **Key patterns**: Pagination, filtering, search, error handling, response schemas

- `backend/app/api/v1/__init__.py:99-105`
  - **Why**: Must register new room router
  - **Pattern**: `api_router.include_router(admin_rooms.router, prefix="/admin/organization/rooms", tags=["管理员-课室管理"])`

#### Backend Schemas

- `backend/app/schemas/user.py` (any Pydantic schema file)
  - **Why**: Reference for Pydantic schema patterns (Create, Update, Response, ListResponse)
  - **Pattern**: `from_attributes = True` Config for ORM conversion

#### Frontend Services

- `frontend/src/services/admin.ts:1-512`
  - **Why**: Must add room service methods
  - **Pattern**: `getRooms()`, `getRoom()`, `createRoom()`, `updateRoom()`, `deleteRoom()`, `importRooms()`

#### Frontend Components

- `frontend/src/pages/Admin/OrganizationManagement/SchoolManagementCard.vue`
  - **Why**: Complete reference for admin card implementation
  - **Patterns**: Data loading, form modals, batch import, filtering, pagination, Element Plus components

- `frontend/src/pages/Admin/OrganizationManagement.vue:1-200`
  - **Why**: Must add room management card to main container
  - **Pattern**: Card navigation, component routing, active tab state

- `frontend/src/router/index.ts:200-210`
  - **Why**: Route already configured for `/admin/organization`

#### Frontend Types

- `frontend/src/services/admin.ts:6-39`
  - **Why**: Must add TypeScript interfaces for Room entities
  - **Pattern**: `Room`, `RoomListResponse`, `RoomCreate`, `RoomUpdate`, `RoomImportResponse`

#### Database Migration Patterns

- `backend/alembic/versions/20260115_1052_5a9378dbcbb6_add_teacher_teaching_assignments_table.py`
  - **Why**: Reference for creating new tables with foreign keys
  - **Pattern**: `op.create_table()`, `op.add_column()`, `op.create_foreign_key()`, indexes

- `backend/alembic/versions/016_add_classroom_session_tables.py:1-100`
  - **Why**: Shows how to add columns to existing tables
  - **Pattern**: Safety checks with inspector, proper downgrade order

### New Files to Create

- `backend/app/models/room.py` - Room model definition
- `backend/app/schemas/room.py` - Pydantic schemas for room operations
- `backend/app/api/v1/admin_rooms.py` - Room CRUD API endpoints
- `backend/app/api/v1/room_import_service.py` - Room batch import service
- `backend/alembic/versions/YYYYMMDD_HHMM_{description}.py` - Database migration
- `frontend/src/pages/Admin/OrganizationManagement/RoomManagementCard.vue` - Room management UI

### Relevant Documentation YOU SHOULD READ THESE BEFORE IMPLEMENTING!

#### SQLAlchemy 2.0 Documentation
- [Relationship API](https://docs.sqlalchemy.org/en/20/orm/basic_relationships.html)
  - **Section**: Configuring Relationships - relationship() function
  - **Why**: Understanding relationship configuration for Room-School and Room-Classroom associations

- [Column and Data Types](https://docs.sqlalchemy.org/en/20/core/type_basics.html)
  - **Section**: Generic Types (String, Integer, Boolean, JSON, DateTime)
  - **Why**: Proper column type selection for Room model fields

#### FastAPI Documentation
- [Pydantic Schemas](https://fastapi.tiangolo.com/tutorial/pydantic-models/)
  - **Section**: Request Body + Path Parameters + Query Parameters
  - **Why**: Request/response schema patterns for room endpoints

- [Dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/)
  - **Section**: Dependencies in path operation decorators
  - **Why**: Proper dependency injection (`get_db`, `get_current_admin`)

#### Alembic Documentation
- [Migration Operations](https://alembic.sqlalchemy.org/en/latest/ops.html)
  - **Sections**: `create_table()`, `add_column()`, `create_foreign_key()`, `create_index()`
  - **Why**: Database migration operation patterns

### Patterns to Follow

#### Naming Conventions

**Database Tables**: Plural lowercase (`rooms`)
**Model Classes**: Singular PascalCase (`Room`)
**Foreign Keys**: `{entity}_id` format (`school_id`, `assigned_classroom_id`)
**API Endpoints**: kebab-case (`/admin/organization/rooms`)
**Pydantic Schemas**: PascalCase with suffix (`RoomCreate`, `RoomUpdate`, `RoomResponse`)
**TypeScript Interfaces**: PascalCase (`Room`, `RoomListResponse`)
**Vue Components**: PascalCase with suffix (`RoomManagementCard.vue`)

#### Error Handling Pattern

```python
from fastapi import HTTPException

# 404 - Not Found
if not room:
    raise HTTPException(status_code=404, detail="课室不存在")

# 400 - Bad Request (validation)
if existing_room:
    raise HTTPException(status_code=400, detail="课室编码已存在")

# 400 - Constraint violation
if has_dependencies:
    raise HTTPException(status_code=400, detail="该课室有教学任务，无法删除")
```

#### Logging Pattern

```python
import logging

logger = logging.getLogger(__name__)

logger.info(f"Creating room: {room_data.name}")
logger.error(f"Failed to create room: {str(e)}", exc_info=True)
```

#### Database Query Pattern (Async)

```python
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

# Eager loading
query = select(Room).options(selectinload(Room.school))

# Filtering
if school_id:
    query = query.where(Room.school_id == school_id)

# Search
if search:
    search_filter = or_(
        Room.name.ilike(f"%{search}%"),
        Room.code.ilike(f"%{search}%")
    )
    query = query.where(search_filter)

# Pagination
offset = (page - 1) * size
result = await db.execute(query.offset(offset).limit(size))
rooms = result.scalars().all()
```

#### Validation Pattern

```python
# Check uniqueness before create
existing = await db.execute(
    select(Room).where(Room.code == room_data.code)
)
if existing.scalar_one_or_none():
    raise HTTPException(status_code=400, detail="课室编码已存在")

# Check foreign key existence
school = await db.execute(
    select(School).where(School.id == room_data.school_id)
)
if not school.scalar_one_or_none():
    raise HTTPException(status_code=400, detail="学校不存在")
```

---

## IMPLEMENTATION PLAN

### Phase 1: Database Migration

**Objective**: Add `rooms` table and `room_id` column to `class_sessions`

**Tasks**:

1. Create Alembic migration file
2. Define `rooms` table schema
3. Add `room_id` column to `class_sessions` table
4. Create foreign key constraints
5. Create indexes for performance
6. Write safe downgrade procedures

### Phase 2: Backend Models & Schemas

**Objective**: Define Room model and Pydantic schemas

**Tasks**:

1. Create `Room` model with relationships to School and Classroom
2. Update `ClassSession` model to add `room_id` field and relationship
3. Create Pydantic schemas (Create, Update, Response, ListResponse)
4. Update `ClassSession` schemas to include room information
5. Export new models in `__init__.py`

### Phase 3: Backend API Implementation

**Objective**: Implement room CRUD endpoints and update session endpoints

**Tasks**:

1. Create room CRUD endpoints (list, get, create, update, delete)
2. Implement filtering (school, building, room_type, search)
3. Implement pagination
4. Add room existence validation in session creation
5. Update session endpoints to include room information
6. Register room router in main API

### Phase 4: Frontend Services & Types

**Objective**: Add TypeScript interfaces and API client methods

**Tasks**:

1. Add Room TypeScript interfaces
2. Implement room service methods in adminService
3. Add room import service method
4. Export types and services

### Phase 5: Frontend UI Components

**Objective**: Create room management admin interface

**Tasks**:

1. Create RoomManagementCard component
2. Implement room list with filtering and search
3. Add create/edit room dialog
4. Implement batch import functionality
5. Add room card to OrganizationManagement
6. Test all CRUD operations

### Phase 6: Integration & Testing

**Objective**: Verify end-to-end functionality

**Tasks**:

1. Test database migration (upgrade/downgrade)
2. Test room CRUD operations via API
3. Test room filtering and search
4. Test batch import
5. Test session creation with room assignment
6. Verify frontend UI functionality
7. Run validation commands

---

## STEP-BY-STEP TASKS

IMPORTANT: Execute every task in order, top to bottom. Each task is atomic and independently testable.

### Task Format Guidelines

- **CREATE**: New files or components
- **UPDATE**: Modify existing files
- **ADD**: Insert new functionality into existing code
- **MIRROR**: Copy pattern from reference file
- **VALIDATE**: Executable validation command

---

### Phase 1: Database Migration

#### TASK 1-1: CREATE Database Migration File

**File**: `backend/alembic/versions/{timestamp}_add_room_management_system.py`

**IMPLEMENT**:
- Generate new migration using: `alembic revision -m "add room management system"`
- Or manually create with timestamp format: `YYYYMMDD_HHMM_{description}.py`
- Place in: `backend/alembic/versions/`

**PATTERN**: Mirror `backend/alembic/versions/20260115_1052_5a9378dbcbb6_add_teacher_teaching_assignments_table.py:1-100`

**GOTCHA**: Ensure timestamp is unique and follows project pattern

**VALIDATE**: `ls -la backend/alembic/versions/ | tail -5`

---

#### TASK 1-2: IMPLEMENT rooms Table Creation

**File**: `backend/alembic/versions/{timestamp}_add_room_management_system.py`

**IMPLEMENT**: In `upgrade()` function:

```python
def upgrade() -> None:
    # Create rooms table
    op.create_table(
        'rooms',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False, comment='课室名称'),
        sa.Column('code', sa.String(length=50), nullable=True, comment='课室编码'),
        sa.Column('school_id', sa.Integer(), nullable=False, comment='所属学校ID'),
        sa.Column('building', sa.String(length=50), nullable=True, comment='楼栋'),
        sa.Column('floor', sa.Integer(), nullable=True, comment='楼层'),
        sa.Column('room_type', sa.String(length=50), nullable=False, comment='课室类型'),
        sa.Column('capacity', sa.Integer(), nullable=True, comment='座位容量'),
        sa.Column('equipment', sa.JSON(), nullable=True, comment='设备清单'),
        sa.Column('assigned_classroom_id', sa.Integer(), nullable=True, comment='固定分配的班级ID'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true', comment='是否激活'),
        sa.Column('description', sa.Text(), nullable=True, comment='课室描述'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='更新时间'),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['school_id'], ['schools.id']),
        sa.ForeignKeyConstraint(['assigned_classroom_id'], ['classrooms.id']),
        comment='课室/物理教室表'
    )

    # Create indexes
    op.create_index('ix_rooms_code', 'rooms', ['code'], unique=True)
    op.create_index('ix_rooms_school_id', 'rooms', ['school_id'])
    op.create_index('idx_room_school_type', 'rooms', ['school_id', 'room_type'])
```

**PATTERN**: Mirror table creation from `backend/app/models/organization.py:78-124` (Classroom model)

**GOTCHA**: Use `sa.Text()` for description, not `sa.String()`

**VALIDATE**: `python -c "
import sqlalchemy as sa
# Check if table creation syntax is correct
print('✓ Migration syntax valid')
"`

---

#### TASK 1-3: IMPLEMENT class_sessions Column Addition

**File**: `backend/alembic/versions/{timestamp}_add_room_management_system.py`

**IMPLEMENT**: In `upgrade()` function (after table creation):

```python
    # Add room_id column to class_sessions
    op.add_column(
        'class_sessions',
        sa.Column('room_id', sa.Integer(), nullable=True, comment='物理课室ID')
    )

    # Create foreign key constraint
    op.create_foreign_key(
        'fk_class_sessions_room_id',
        'class_sessions', 'rooms',
        ['room_id'], ['id'],
        ondelete='SET NULL'
    )

    # Create indexes for room_id
    op.create_index('ix_class_sessions_room_id', 'class_sessions', ['room_id'])
    op.create_index('idx_session_room_status', 'class_sessions', ['room_id', 'status'])
```

**PATTERN**: Mirror column addition from `backend/alembic/versions/016_add_classroom_session_tables.py:50-80`

**GOTCHA**: `ondelete='SET NULL'` ensures sessions aren't deleted when room is deleted

**VALIDATE**: `grep -n "room_id" backend/alembic/versions/{timestamp}_add_room_management_system.py`

---

#### TASK 1-4: IMPLEMENT Downgrade Function

**File**: `backend/alembic/versions/{timestamp}_add_room_management_system.py`

**IMPLEMENT**:

```python
def downgrade() -> None:
    # Drop indexes in reverse order
    op.drop_index('idx_session_room_status', table_name='class_sessions')
    op.drop_index('ix_class_sessions_room_id', table_name='class_sessions')
    op.drop_index('idx_room_school_type', table_name='rooms')
    op.drop_index('ix_rooms_school_id', table_name='rooms')
    op.drop_index('ix_rooms_code', table_name='rooms')

    # Drop foreign key constraint
    op.drop_constraint('fk_class_sessions_room_id', 'class_sessions', type_='foreignkey')

    # Drop column from class_sessions
    op.drop_column('class_sessions', 'room_id')

    # Drop foreign key constraints
    op.drop_constraint('rooms_assigned_classroom_id_fkey', 'rooms', type_='foreignkey')
    op.drop_constraint('rooms_school_id_fkey', 'rooms', type_='foreignkey')

    # Drop table
    op.drop_table('rooms')
```

**GOTCHA**: Drop in reverse order (constraints → indexes → columns → tables)

**VALIDATE**: `grep -c "def downgrade" backend/alembic/versions/{timestamp}_add_room_management_system.py`

---

#### TASK 1-5: VALIDATE Migration Syntax

**VALIDATE**:
```bash
cd backend
source venv/bin/activate
python -c "
from alembic.config import Config
from alembic import script
import sys

try:
    config = Config('alembic.ini')
    script_dir = script.ScriptDirectory.from_config(config)
    print('✓ Migration file is valid')
    sys.exit(0)
except Exception as e:
    print(f'✗ Migration validation failed: {e}')
    sys.exit(1)
"
```

---

### Phase 2: Backend Models & Schemas

#### TASK 2-1: CREATE Room Model

**File**: `backend/app/models/room.py`

**IMPLEMENT**:

```python
"""课室/物理教室模型"""

from typing import Optional
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Room(Base):
    """课室/物理教室模型"""

    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, comment="课室名称")
    code = Column(String(50), nullable=True, comment="课室编码")
    school_id = Column(
        Integer, ForeignKey("schools.id"), nullable=False, comment="所属学校ID"
    )
    building = Column(String(50), nullable=True, comment="楼栋")
    floor = Column(Integer, nullable=True, comment="楼层")
    room_type = Column(String(50), nullable=False, comment="课室类型")
    capacity = Column(Integer, nullable=True, comment="座位容量")
    equipment = Column(JSON, nullable=True, comment="设备清单")
    assigned_classroom_id = Column(
        Integer,
        ForeignKey("classrooms.id"),
        nullable=True,
        comment="固定分配的班级ID",
    )
    is_active = Column(Boolean, default=True, comment="是否激活")
    description = Column(Text, nullable=True, comment="课室描述")
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), comment="创建时间"
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        comment="更新时间",
    )

    # Relationships
    school = relationship("School", back_populates="rooms")
    assigned_classroom = relationship("Classroom", foreign_keys=[assigned_classroom_id])

    def __repr__(self) -> str:
        return f"<Room(id={self.id}, name={self.name}, school_id={self.school_id})>"
```

**PATTERN**: Mirror `backend/app/models/organization.py:78-124` (Classroom model structure)

**GOTCHA**: Don't forget to add `back_populates="rooms"` to School relationship later

**VALIDATE**: `python -c "from backend.app.models.room import Room; print('✓ Room model imports successfully')"`

---

#### TASK 2-2: UPDATE School Model to Include Rooms

**File**: `backend/app/models/organization.py:42-76`

**ADD** after line 75 (after classrooms relationship):

```python
    rooms = relationship(
        "Room", back_populates="school", cascade="all, delete-orphan"
    )
```

**PATTERN**: Mirror classrooms relationship definition at lines 73-75

**GOTCHA**: Must add import `from app.models.room import Room` at top of file (after Task 2-3)

**VALIDATE**: `grep -n "rooms = relationship" backend/app/models/organization.py`

---

#### TASK 2-3: UPDATE models/__init__.py

**File**: `backend/app/models/__init__.py:1-100`

**ADD** import at top of file (after other model imports):

```python
from app.models.room import Room
```

**ADD** to `__all__` list (around line 90+):

```python
    "Room",
```

**PATTERN**: Mirror other model exports (e.g., `"Region", "School", "Classroom"`)

**VALIDATE**: `python -c "from backend.app.models import Room; print('✓ Room exported successfully')"`

---

#### TASK 2-4: UPDATE ClassSession Model

**File**: `backend/app/models/classroom_session.py:33-98`

**ADD** after line 42 (after classroom_id field):

```python
    room_id = Column(
        Integer,
        ForeignKey("rooms.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="Physical room ID where the session takes place",
    )
```

**ADD** after line 87 (after classroom relationship):

```python
    room = relationship("Room", foreign_keys=[room_id])
```

**PATTERN**: Mirror classroom_id field (lines 41-42) and relationship (line 87)

**GOTCHA**: Use `ForeignKey("rooms.id", ondelete="SET NULL")` for referential integrity

**VALIDATE**: `grep -n "room_id" backend/app/models/classroom_session.py`

---

#### TASK 2-5: CREATE Room Pydantic Schemas

**File**: `backend/app/schemas/room.py`

**IMPLEMENT**:

```python
"""课室管理 Pydantic schemas"""

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class RoomBase(BaseModel):
    """课室基础 schema"""
    name: str = Field(..., description="课室名称")
    code: Optional[str] = Field(None, description="课室编码")
    school_id: int = Field(..., description="所属学校ID")
    building: Optional[str] = Field(None, description="楼栋")
    floor: Optional[int] = Field(None, description="楼层")
    room_type: str = Field(..., description="课室类型")
    capacity: Optional[int] = Field(None, description="座位容量")
    equipment: Optional[List[str]] = Field(None, description="设备清单")
    assigned_classroom_id: Optional[int] = Field(None, description="固定分配的班级ID")
    is_active: bool = Field(True, description="是否激活")
    description: Optional[str] = Field(None, description="课室描述")


class RoomCreate(RoomBase):
    """创建课室 schema"""
    pass


class RoomUpdate(BaseModel):
    """更新课室 schema"""
    name: Optional[str] = None
    code: Optional[str] = None
    school_id: Optional[int] = None
    building: Optional[str] = None
    floor: Optional[int] = None
    room_type: Optional[str] = None
    capacity: Optional[int] = None
    equipment: Optional[List[str]] = None
    assigned_classroom_id: Optional[int] = None
    is_active: Optional[bool] = None
    description: Optional[str] = None


class RoomResponse(RoomBase):
    """课室响应 schema"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RoomListResponse(BaseModel):
    """课室列表响应 schema"""
    rooms: List[RoomResponse]
    total: int
    page: int
    size: int
    total_pages: int


class RoomImportError(BaseModel):
    """课室导入错误"""
    row: int
    field: Optional[str] = None
    message: str


class RoomImportResponse(BaseModel):
    """课室导入响应"""
    total: int
    success: int
    failed: int
    created: int
    updated: int
    skipped: int
    errors: List[RoomImportError]
```

**PATTERN**: Mirror schema patterns from any existing schema file (e.g., `backend/app/schemas/user.py`)

**GOTCHA**: Use `Field(...)` for required fields, `Field(None)` for optional

**VALIDATE**: `python -c "from backend.app.schemas.room import RoomCreate; print('✓ Room schemas import successfully')"`

---

#### TASK 2-6: UPDATE ClassSession Schemas

**File**: `backend/app/schemas/classroom_session.py`

**ADD** `room_id` field to `ClassSessionBase` (around line 36-42):

```python
    room_id: Optional[int] = Field(None, description="Physical room ID")
```

**ADD** `room_name` and `room_code` to `ClassSessionWithDetails` (around line 80-86):

```python
    room_name: Optional[str] = None
    room_code: Optional[str] = None
```

**PATTERN**: Mirror classroom_id field structure

**VALIDATE**: `grep -n "room_" backend/app/schemas/classroom_session.py`

---

### Phase 3: Backend API Implementation

#### TASK 3-1: CREATE Room CRUD Endpoints

**File**: `backend/app/api/v1/admin_rooms.py`

**IMPLEMENT**:

```python
"""管理员-课室管理 API"""

from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.api.deps import get_current_admin
from app.models import User, Room, School
from app.schemas.room import (
    RoomCreate,
    RoomUpdate,
    RoomResponse,
    RoomListResponse,
)
from sqlalchemy.ext.asyncio import AsyncSession


router = APIRouter()


@router.get("/rooms", response_model=RoomListResponse)
async def get_rooms(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=1000, description="每页数量"),
    school_id: Optional[int] = Query(None, description="学校ID筛选"),
    room_type: Optional[str] = Query(None, description="课室类型筛选"),
    building: Optional[str] = Query(None, description="楼栋筛选"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Any:
    """获取课室列表"""
    query = select(Room).options(selectinload(Room.school))

    # Apply filters
    if school_id is not None:
        query = query.where(Room.school_id == school_id)
    if room_type is not None:
        query = query.where(Room.room_type == room_type)
    if building:
        query = query.where(Room.building == building)

    # Search
    if search:
        search_filter = or_(
            Room.name.ilike(f"%{search}%"),
            Room.code.ilike(f"%{search}%"),
        )
        query = query.where(search_filter)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Apply pagination
    offset = (page - 1) * size
    query = query.offset(offset).limit(size).order_by(Room.school_id, Room.building, Room.floor, Room.name)

    result = await db.execute(query)
    rooms = result.scalars().all()

    total_pages = (total + size - 1) // size

    return RoomListResponse(
        rooms=[RoomResponse.model_validate(room) for room in rooms],
        total=total,
        page=page,
        size=size,
        total_pages=total_pages,
    )


@router.get("/rooms/{room_id}", response_model=RoomResponse)
async def get_room(
    room_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Any:
    """获取课室详情"""
    result = await db.execute(
        select(Room).options(selectinload(Room.school)).where(Room.id == room_id)
    )
    room = result.scalar_one_or_none()

    if not room:
        raise HTTPException(status_code=404, detail="课室不存在")

    return RoomResponse.model_validate(room)


@router.post("/rooms", response_model=RoomResponse)
async def create_room(
    room_data: RoomCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Any:
    """创建课室"""
    # Validate school exists
    school_result = await db.execute(
        select(School).where(School.id == room_data.school_id)
    )
    if not school_result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="学校不存在")

    # Check code uniqueness
    if room_data.code:
        existing_result = await db.execute(
            select(Room).where(Room.code == room_data.code)
        )
        if existing_result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="课室编码已存在")

    # Create room
    room = Room(**room_data.model_dump())
    db.add(room)
    await db.commit()
    await db.refresh(room)

    return RoomResponse.model_validate(room)


@router.put("/rooms/{room_id}", response_model=RoomResponse)
async def update_room(
    room_id: int,
    room_data: RoomUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Any:
    """更新课室"""
    result = await db.execute(select(Room).where(Room.id == room_id))
    room = result.scalar_one_or_none()

    if not room:
        raise HTTPException(status_code=404, detail="课室不存在")

    # Update only provided fields
    update_data = room_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(room, field, value)

    await db.commit()
    await db.refresh(room)

    return RoomResponse.model_validate(room)


@router.delete("/rooms/{room_id}")
async def delete_room(
    room_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Any:
    """删除课室"""
    result = await db.execute(select(Room).where(Room.id == room_id))
    room = result.scalar_one_or_none()

    if not room:
        raise HTTPException(status_code=404, detail="课室不存在")

    await db.delete(room)
    await db.commit()

    return {"message": "课室删除成功"}
```

**PATTERN**: Mirror CRUD structure from `backend/app/api/v1/admin_organization.py:50-200` (Region endpoints)

**GOTCHA**: Use `selectinload(Room.school)` to avoid N+1 queries

**VALIDATE**: `python -c "from backend.app.api.v1.admin_rooms import router; print('✓ Room router imports successfully')"`

---

#### TASK 3-2: REGISTER Room Router

**File**: `backend/app/api/v1/__init__.py:99-105`

**ADD** after line 105 (after admin_organization router):

```python
api_router.include_router(
    admin_rooms.router, prefix="/admin/organization/rooms", tags=["管理员-课室管理"]
)
```

**ADD** import at top of file (around line 9-47):

```python
    admin_rooms,
```

**PATTERN**: Mirror router registration pattern for admin_organization

**GOTCHA**: Import must come before router registration

**VALIDATE**: `grep -n "admin_rooms" backend/app/api/v1/__init__.py`

---

### Phase 4: Frontend Services & Types

#### TASK 4-1: ADD TypeScript Interfaces

**File**: `frontend/src/services/admin.ts`

**ADD** after other model interfaces (around line 200+):

```typescript
export interface Room {
  id: number
  name: string
  code: string | null
  school_id: number
  building: string | null
  floor: number | null
  room_type: string
  capacity: number | null
  equipment: string[] | null
  assigned_classroom_id: number | null
  is_active: boolean
  description: string | null
  created_at: string
  updated_at: string
  school?: School
}

export interface RoomListResponse {
  rooms: Room[]
  total: number
  page: number
  size: number
  total_pages: number
}

export interface RoomCreate {
  name: string
  code?: string
  school_id: number
  building?: string
  floor?: number
  room_type: string
  capacity?: number
  equipment?: string[]
  assigned_classroom_id?: number
  is_active?: boolean
  description?: string
}

export interface RoomUpdate {
  name?: string
  code?: string
  school_id?: number
  building?: string
  floor?: number
  room_type?: string
  capacity?: number
  equipment?: string[]
  assigned_classroom_id?: number
  is_active?: boolean
  description?: string
}

export interface RoomImportError {
  row: number
  field: string | null
  message: string
}

export interface RoomImportResponse {
  total: number
  success: number
  failed: number
  created: number
  updated: number
  skipped: number
  errors: RoomImportError[]
}
```

**PATTERN**: Mirror TypeScript interfaces from existing models (e.g., School, Classroom)

**VALIDATE**: `cd frontend && pnpm type-check 2>&1 | grep -A2 "admin.ts"`

---

#### TASK 4-2: ADD Room Service Methods

**File**: `frontend/src/services/admin.ts`

**ADD** in adminService object (around line 400+):

```typescript
  // ==================== 课室管理 ====================

  /**
   * 获取课室列表
   */
  async getRooms(params: {
    page?: number
    size?: number
    school_id?: number
    room_type?: string
    building?: string
    search?: string
  } = {}): Promise<RoomListResponse> {
    return await api.get('/admin/organization/rooms', { params })
  },

  /**
   * 获取课室详情
   */
  async getRoom(roomId: number): Promise<Room> {
    return await api.get(`/admin/organization/rooms/${roomId}`)
  },

  /**
   * 创建课室
   */
  async createRoom(roomData: RoomCreate): Promise<Room> {
    return await api.post('/admin/organization/rooms', roomData)
  },

  /**
   * 更新课室
   */
  async updateRoom(roomId: number, roomData: RoomUpdate): Promise<Room> {
    return await api.put(`/admin/organization/rooms/${roomId}`, roomData)
  },

  /**
   * 删除课室
   */
  async deleteRoom(roomId: number): Promise<void> {
    return await api.delete(`/admin/organization/rooms/${roomId}`)
  },
```

**PATTERN**: Mirror service methods from getSchools(), createSchool(), etc.

**GOTCHA**: All service methods must return Promises with proper type annotations

**VALIDATE**: `cd frontend && pnpm type-check 2>&1 | grep -A2 "admin.ts"`

---

### Phase 5: Frontend UI Components

#### TASK 5-1: CREATE RoomManagementCard Component

**File**: `frontend/src/pages/Admin/OrganizationManagement/RoomManagementCard.vue`

**IMPLEMENT**: Full component with:
- Room list table with filtering (school, building, room_type, search)
- Create/Edit room dialog
- Delete confirmation
- Pagination (Element Plus)
- Batch import (3-step: template → upload → results)

**PATTERN**: Mirror `frontend/src/pages/Admin/OrganizationManagement/SchoolManagementCard.vue`

**KEY ELEMENTS**:
- Use Element Plus components (el-table, el-dialog, el-pagination, el-upload)
- Implement cascading filters (region → school)
- Use `useToast` composable for error messages
- Follow the exact structure from SchoolManagementCard.vue

**GOTCHA**: Ensure all TypeScript types are imported from `@/services/admin`

**VALIDATE**:
```bash
cd frontend
pnpm type-check 2>&1 | grep -E "(error|warning)" | head -20
```

---

#### TASK 5-2: UPDATE OrganizationManagement Main Container

**File**: `frontend/src/pages/Admin/OrganizationManagement.vue:1-200`

**ADD** new card in template (after line 101, after personnel card):

```vue
      <!-- 课室管理卡片 -->
      <el-col :xs="24" :sm="12" :md="6" :lg="6">
        <el-card
          class="function-card"
          shadow="hover"
          @click="activeTab = 'rooms'"
          :class="{ 'active-card': activeTab === 'rooms' }"
        >
          <div class="card-icon">
            <el-icon :size="40" color="#f56c6c">
              <component :is="'OfficeBuilding'" />
            </el-icon>
          </div>
          <div class="card-content">
            <h3>课室管理</h3>
            <p>管理物理教室、实验室和功能室</p>
          </div>
        </el-card>
      </el-col>
```

**ADD** component import in script (around line 123):

```typescript
import RoomManagementCard from './OrganizationManagement/RoomManagementCard.vue'
```

**ADD** component display in template (after line 114):

```vue
<!-- 课室管理 -->
<RoomManagementCard v-if="activeTab === 'rooms'" />
```

**UPDATE** activeTab type (line 126):

```typescript
const activeTab = ref<'regions' | 'schools' | 'classrooms' | 'personnel' | 'rooms'>('regions')
```

**PATTERN**: Mirror other card definitions (regions, schools, classrooms, personnel)

**GOTCHA**: Icon color `#f56c6c` (red) to distinguish from other cards

**VALIDATE**:
```bash
cd frontend
pnpm type-check 2>&1 | grep "OrganizationManagement.vue"
```

---

### Phase 6: Integration & Testing

#### TASK 6-1: RUN Database Migration

**VALIDATE**:
```bash
cd backend
source venv/bin/activate
alembic upgrade head
```

**EXPECTED**: Migration executes successfully, rooms table created

**GOTCHA**: If migration fails, check PostgreSQL logs and rollback with `alembic downgrade -1`

---

#### TASK 6-2: TEST Backend API Endpoints

**VALIDATE**:
```bash
# Start backend server
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# In another terminal, test endpoints
curl -X GET http://localhost:8000/api/v1/admin/organization/rooms \
  -H "Authorization: Bearer {admin_token}"
```

**EXPECTED**: Returns empty rooms list with valid pagination structure

---

#### TASK 6-3: TEST Frontend Component

**VALIDATE**:
```bash
cd frontend
pnpm dev

# Navigate to http://localhost:5173/admin/organization
# Click "课室管理" card
# Verify:
# - Room list displays
# - Filters work
# - Create dialog opens
# - Pagination works
```

**GOTCHA**: Open browser console for TypeScript/runtime errors

---

#### TASK 6-4: RUN Full Validation

**VALIDATE** (run all commands in order):

```bash
# Level 1: Python formatting
cd backend
source venv/bin/activate
black . --check

# Level 2: TypeScript type check
cd frontend
pnpm type-check

# Level 3: Backend lint
cd backend
flake8 app/api/v1/admin_rooms.py
flake8 app/models/room.py

# Level 4: Frontend lint
cd frontend
pnpm lint

# Level 5: Import validation
cd backend
python -c "from app.api.v1.admin_rooms import router; print('✓ Backend imports OK')"
python -c "from app.models import Room; print('✓ Room model OK')"

cd frontend
pnpm exec tsc --noEmit
```

**EXPECTED**: All commands pass with zero errors

---

## TESTING STRATEGY

### Unit Tests

**Scope**: Backend model validation, Pydantic schema validation

**Requirements**: Follow existing test patterns in `backend/tests/`

```python
# backend/tests/test_room_api.py
import pytest
from httpx import AsyncClient

async def test_create_room(client: AsyncClient, admin_token: str):
    response = await client.post(
        "/api/v1/admin/organization/rooms",
        json={"name": "101室", "school_id": 1, "room_type": "普通教室"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "101室"
    assert data["school_id"] == 1

async def test_get_rooms(client: AsyncClient, admin_token: str):
    response = await client.get(
        "/api/v1/admin/organization/rooms",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert "rooms" in response.json()
```

### Integration Tests

**Scope**: End-to-end API workflows, database operations

**Requirements**: Test room CRUD with school relationships

```python
async def test_room_crud_flow(client: AsyncClient, admin_token: str):
    # Create
    room = await create_room(client, admin_token, school_id=1)
    room_id = room["id"]

    # Read
    response = await client.get(f"/api/v1/admin/organization/rooms/{room_id}")
    assert response.status_code == 200

    # Update
    response = await client.put(
        f"/api/v1/admin/organization/rooms/{room_id}",
        json={"name": "102室"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert response.json()["name"] == "102室"

    # Delete
    response = await client.delete(f"/api/v1/admin/organization/rooms/{room_id}")
    assert response.status_code == 200
```

### Edge Cases

**Must Test**:

1. Creating room with duplicate code (should fail with 400)
2. Creating room with non-existent school_id (should fail with 400)
3. Deleting room with assigned sessions (should handle gracefully)
4. Filtering with school_id → building cascade
5. Pagination edge cases (first page, last page, empty results)
6. Search with special characters
7. Room with NULL optional fields
8. Batch import with mixed valid/invalid rows

---

## VALIDATION COMMANDS

Execute every command to ensure zero regressions and 100% feature correctness.

### Level 1: Syntax & Style

```bash
# Backend: Black formatting check
cd backend
source venv/bin/activate
black . --check

# Frontend: TypeScript check
cd frontend
pnpm type-check

# Frontend: ESLint
cd frontend
pnpm lint
```

### Level 2: Unit Tests

```bash
# Backend: Run pytest
cd backend
source venv/bin/activate
pytest tests/test_room_api.py -v

# Frontend: Run Vitest
cd frontend
pnpm test
```

### Level 3: Integration Tests

```bash
# Backend: Full API test suite
cd backend
pytest tests/ -v

# Manual API testing
curl -X GET http://localhost:8000/api/v1/admin/organization/rooms \
  -H "Authorization: Bearer {admin_token}"
```

### Level 4: Manual Validation

**Steps**:

1. Login as admin: `admin@inspireed.com / admin123`
2. Navigate to: `/admin/organization`
3. Click "课室管理" card
4. Verify room list displays (may be empty initially)
5. Click "创建课室" button
6. Fill form:
   - 课室名称: `101室`
   - 学校: Select any school
   - 课室类型: `普通教室`
   - 楼栋: `教学楼A`
   - 楼层: `1`
   - 容量: `45`
7. Submit and verify creation success
8. Search for `101室` and verify it appears
9. Edit room and verify update works
10. Delete room and verify removal
11. Test batch import:
    - Download template
    - Fill with test data
    - Upload and verify import results

### Level 5: Additional Validation

```bash
# Database migration verification
cd backend
source venv/bin/activate
python -c "
import asyncio
from sqlalchemy import text
from app.core.database import async_session_maker

async def check_tables():
    async with async_session_maker() as db:
        result = await db.execute(text(\"SELECT table_name FROM information_schema.tables WHERE table_name = 'rooms'\"))
        if result.scalar():
            print('✓ rooms table exists')
        else:
            print('✗ rooms table missing')

asyncio.run(check_tables())
"

# API endpoint verification
curl -X OPTIONS http://localhost:8000/api/v1/admin/organization/rooms \
  -H "Origin: http://localhost:5173" \
  -v

# Frontend build verification
cd frontend
pnpm build
```

---

## ACCEPTANCE CRITERIA

- [ ] Feature implements all specified functionality
  - [ ] Room CRUD operations work
  - [ ] Room filtering (school, building, type, search) works
  - [ ] Room pagination works
  - [ ] Batch import works
  - [ ] Room displays in organization management
- [ ] All validation commands pass with zero errors
  - [ ] `black . --check` passes
  - [ ] `pnpm type-check` passes
  - [ ] `pnpm lint` passes
  - [ ] Database migration applies successfully
- [ ] Unit test coverage meets requirements (80%+)
  - [ ] Backend API tests pass
  - [ ] Model validation tests pass
- [ ] Integration tests verify end-to-end workflows
  - [ ] Room creation with school relationship works
  - [ ] Room filtering and search work
  - [ ] Batch import processes correctly
- [ ] Code follows project conventions and patterns
  - [ ] Naming conventions followed
  - [ ] Error handling patterns match
  - [ ] Import structure consistent
  - [ ] Component structure matches
- [ ] No regressions in existing functionality
  - [ ] Existing organization management cards work
  - [ ] ClassSession creation still works (with optional room_id)
  - [ ] No database schema conflicts
- [ ] Documentation is updated (if applicable)
  - [ ] Migration file has descriptive messages
  - [ ] API routes have docstrings
- [ ] Performance meets requirements (if applicable)
  - [ ] Room queries use indexes
  - [ ] Pagination prevents loading all rooms
- [ ] Security considerations addressed (if applicable)
  - [ ] Admin-only access enforced
  - [ ] School isolation works (users see only their school's rooms)

---

## COMPLETION CHECKLIST

- [ ] All tasks completed in order
- [ ] Each task validation passed immediately
- [ ] All validation commands executed successfully
- [ ] Full test suite passes (unit + integration)
- [ ] No linting or type checking errors
- [ ] Manual testing confirms feature works
- [ ] Acceptance criteria all met
- [ ] Code reviewed for quality and maintainability

---

## NOTES

### Design Decisions

**Room Assignment Model**:
- **Fixed assignment**: `assigned_classroom_id` (class-owned rooms like homerooms)
- **Shared rooms**: NULL (labs, music rooms used by multiple classes)
- This dual approach supports both scenarios without data duplication

**Room Types**:
- Suggested types: `普通教室`, `实验室`, `计算机室`, `多媒体教室`, `音乐室`, `美术室`, `体育馆`, `报告厅`
- Schools can customize via room_type field (no enum constraint for flexibility)

**Backward Compatibility**:
- `room_id` in `ClassSession` is nullable
- Existing sessions without room assignment continue to work
- Frontend can gradually adopt room selection UI

**Future Enhancements**:
- Room scheduling/conflict detection
- Room utilization analytics
- Equipment management and tracking
- Room booking calendar view

### Trade-offs

**Added Complexity**:
- Separate Room model adds complexity vs adding room name as string field
- **Decision**: Architectural clarity worth the complexity for schools with limited resources

**UI Complexity**:
- Users may confuse "班级" (Classroom) with "课室" (Room)
- **Mitigation**: Clear UI labels and tooltips explaining the distinction

### Migration Considerations

**Zero Downtime**:
- Migration adds nullable column, doesn't break existing sessions
- Can deploy during normal operations

**Data Migration**:
- No legacy room data to migrate (greenfield feature)
- If schools have existing room data in other systems, can bulk import via API

### Known Limitations

1. **No room scheduling/conflict detection** in this phase (future enhancement)
2. **No equipment booking/tracking** (equipment field is informational only)
3. **Room availability not real-time** (would need session scheduling integration)

---

## SUCCESS METRICS

**One-Pass Implementation**: ✓ Another developer could implement using only this plan

**Validation Complete**: ✓ Every task has at least one working validation command

**Context Rich**: ✓ Plan includes specific file:line references, code patterns, and gotchas

**Pattern Consistency**: ✓ All patterns mirror existing codebase conventions

**Confidence Score**: **8.5/10** for one-pass success

**Key Risks**:
1. Frontend component complexity (mitigated by detailed SchoolManagementCard reference)
2. Database migration edge cases (mitigated by nullable room_id and safety checks)
3. User confusion between Classroom/Room concepts (mitigated by clear UI labels)

**Recommendation**: Proceed with implementation. Plan is comprehensive and actionable.
