# Feature: Exam Room Arrangement System

## Feature Description

Add comprehensive exam room arrangement functionality to the InspireEd platform's exam management system. This feature enables automatic exam room assignment, exam number generation, proctor (invigilator) assignment, and export of various exam-related documents (seating charts, exam tickets, proctor handbooks).

The implementation follows a 5-step workflow:
1. Select classes (students, grade, semester, date)
2. Set exam subjects (subjects, max scores, duration)
3. **Arrange exam rooms** ⭐ (assign rooms, generate exam numbers, assign proctors)
4. Preview & confirm (review all information)
5. Complete & export (download various documents)

## User Story

**As a** school administrator or district exam admin
**I want to** automatically arrange exam rooms, assign exam numbers to students, and designate proctors for each exam room
**So that** I can efficiently organize exams with proper seating arrangements, clear exam number identification, and adequate proctor coverage, then export all necessary documents for exam day operations.

## Problem Statement

Currently, the exam management system lacks physical exam administration capabilities:
- ❌ No exam room assignment - students not assigned to specific rooms
- ❌ No exam number generation - no systematic student identification for exams
- ❌ No proctor assignment - no system for assigning teachers to proctor exams
- ❌ No seating arrangements - no seat allocation within exam rooms
- ❌ No exportable documents - cannot generate seating charts, exam tickets, or proctor handbooks

This forces administrators to manually manage these tasks using spreadsheets or paper systems, which is error-prone and inefficient.

## Solution Statement

Implement a comprehensive exam room arrangement system that:
1. Automatically assigns students to exam rooms based on configurable rules (capacity, class grouping, mixed seating)
2. Generates unique exam numbers for each student using standardized format
3. Assigns proctors (main + assistant) to each exam room with conflict avoidance
4. Provides exportable PDF documents for seating charts, exam tickets, and proctor handbooks
5. Integrates seamlessly with existing exam creation workflow (steps 3-5)

## Feature Metadata

**Feature Type**: New Capability
**Estimated Complexity**: High
**Primary Systems Affected**:
- Backend: `app/models/evaluation.py`, `app/api/v1/exams.py`, `app/services/`
- Frontend: `frontend/src/pages/DistrictExamAdmin/Dashboard.vue`
- Database: New tables for exam_rooms, exam_room_students, exam_proctors

**Dependencies**:
- reportlab (PDF generation)
- Python standard library for document generation
- Existing openpyxl for Excel export

---

## CONTEXT REFERENCES

### Relevant Codebase Files

**CRITICAL - Must read before implementing:**

#### Backend Models
- `/Users/382241106qq.com/inspireed-platform-main/backend/app/models/evaluation.py`
  - Lines 116-217: Exam, ExamSubject, ExamNumberMapping models - understand existing exam structure
  - Lines 37-56: ExamType and ExamStatus enums - use for exam type validation
  - Why: Must mirror existing model patterns for consistency

- `/Users/382241106qq.com/inspireed-platform-main/backend/app/models/room.py`
  - Lines 11-47: Room model - capacity, school_id, room_type, equipment fields
  - Why: Use existing Room model for exam room assignments

- `/Users/382241106qq.com/inspireed-platform-main/backend/app/models/user.py`
  - Lines 22-38: UserRole enum - teacher role for proctors
  - Why: Need to assign teachers as proctors

#### Frontend Components
- `/Users/382241106qq.com/inspireed-platform-main/frontend/src/pages/DistrictExamAdmin/Dashboard.vue`
  - Lines 636-988: Step 1 UI (select classes) - existing form patterns
  - Lines 990-1045: Step 2 UI (select subjects) - recently updated subject selection table
  - Why: Need to integrate Step 3 (room arrangement) into this workflow
  - Lines 1298-1366: Multi-step dialog patterns and validation

#### API Services
- `/Users/382241106qq.com/inspireed-platform-main/frontend/src/services/evaluation.ts`
  - Lines 30-90: API client setup with authentication and error handling
  - Lines 140-250: examApi methods (create, update, get, list, etc.)
  - Why: Follow these patterns for new room arrangement APIs

#### Export/Document Patterns
- `/Users/382241106qq.com/inspireed-platform-main/backend/app/api/v1/course_export.py`
  - Complete file: Export service with StreamingResponse pattern
  - Why: Use for exam document export (PDF, Excel generation)

- `/Users/382241106qq.com/inspireed-platform-main/backend/app/services/excel_import_service.py`
  - Lines 1-50: openpyxl usage for Excel operations
  - Why: Use for Excel export of exam room lists

### New Files to Create

**Backend Models:**
- `/Users/382241106qq.com/inspireed-platform-main/backend/app/models/exam_room.py` - ExamRoom, ExamRoomStudent, ExamProctor models
- `/Users/382241106qq.com/inspireed-platform-main/backend/app/services/exam_room_service.py` - Room arrangement business logic
- `/Users/382241106qq.com/inspireed-platform-main/backend/app/services/exam_document_generator.py` - PDF document generation service

**Backend APIs:**
- `/Users/382241106qq.com/inspireed-platform-main/backend/app/api/v1/exam_rooms.py` - Exam room management endpoints
- `/Users/382241106qq.com/inspireed-platform-main/backend/app/api/v1/exam_documents.py` - Document export endpoints

**Backend Schemas:**
- `/Users/382241106qq.com/inspireed-platform-main/backend/app/schemas/exam_room.py` - Pydantic schemas for request/response

**Frontend Components:**
- `/Users/382241106qq.com/inspireed-platform-main/frontend/src/components/Exam/RoomArrangementPanel.vue` - Room arrangement UI component
- `/Users/382241106qq.com/inspireed-platform-main/frontend/src/components/Exam/RoomPreviewDialog.vue` - Room detail preview dialog

**Frontend Services:**
- `/Users/382241106qq.com/inspireed-platform-main/frontend/src/services/examRoom.ts` - Exam room API client

**Database Migration:**
- `/Users/382241106qq.com/inspireed-platform-main/backend/alembic/versions/{timestamp}_add_exam_room_system.py` - Database migration

**Tests:**
- `/Users/382241106qq.com/inspireed-platform-main/backend/tests/test_exam_room_service.py` - Service layer tests
- `/Users/382241106qq.com/inspireed-platform-main/backend/tests/test_exam_room_api.py` - API endpoint tests

### Relevant Documentation

**Must Read Before Implementation:**

- [SQLAlchemy 2.0 Async ORM](https://docs.sqlalchemy.org/en/20/orm/quickstart.html)
  - Section: Async ORM Session
  - Why: Database operations use async/await pattern

- [FastAPI File Responses](https://fastapi.tiangolo.com/advanced/custom-response/#streamingresponse)
  - Section: StreamingResponse for file downloads
  - Why: Need to generate PDF/Excel files for download

- [ReportLab PDF Library](https://reportlab.com/reportlab-userguide.pdf)
  - Chapter 5: Page Layout and Typography
  - Chapter 6: Tables and Grids
  - Why: Primary tool for PDF generation (seating charts, exam tickets)

- [Python-docx Documentation](https://python-docx.readthedocs.io/)
  - Section: Working with Tables
  - Why: Alternative PDF generation option for simpler documents

**Project-Specific:**
- `/Users/382241106qq.com/inspireed-platform-main/CLAUDE.md`
  - Complete file: Project overview, patterns, and conventions
  - Why: Must follow project-specific rules and architecture

### Patterns to Follow

**Naming Conventions:**
- Backend: snake_case for models, schemas, API endpoints
  - Example: `exam_room`, `exam_room_student`, `generate_exam_numbers`
- Frontend: camelCase for components, TypeScript interfaces
  - Example: `RoomArrangementPanel`, `ExamRoomDetail`, `loadExamRooms`
- Database: lowercase_with_underscores for table and column names
  - Example: `exam_rooms`, `exam_room_students`, `proctor_type`

**Error Handling:**
- Backend API error pattern (from `backend/app/api/v1/exams.py`):
```python
from fastapi import HTTPException, status

async def create_exam(...):
    # Validation
    if not semester:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="学期不存在"
        )

    # Business logic errors
    if exam_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该考试已存在"
        )
```

- Frontend error handling (from `frontend/src/services/evaluation.ts`):
```typescript
try {
  const result = await examApi.create(data);
  ElMessage.success('创建成功');
} catch (error: any) {
  ElMessage.error(error.response?.data?.detail || '创建失败');
}
```

**Logging Pattern:**
- Backend logging (from `backend/app/api/v1/exams.py`):
```python
import logging

logger = logging.getLogger(__name__)

# In endpoints
logger.info(f"Creating exam: {exam_in.name}")
logger.error(f"Failed to create exam: {str(e)}")
```

**Async Database Operations:**
- Always use async pattern (from `backend/app/api/v1/exams.py`):
```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

async def get_exam(exam_id: int, db: AsyncSession):
    result = await db.execute(
        select(Exam).where(Exam.id == exam_id)
    )
    exam = result.scalar_one_or_none()
    if not exam:
        raise HTTPException(status_code=404, detail="考试不存在")
    return exam
```

**Frontend Service Pattern:**
- API client methods (from `frontend/src/services/evaluation.ts`):
```typescript
async createExam(data: ExamCreate): Promise<Exam> {
  return await apiClient.post(`/exams/`, data);
}

async getExam(id: number): Promise<Exam> {
  return await apiClient.get(`/exams/${id}`);
}
```

---

## IMPLEMENTATION PLAN

### Phase 1: Foundation (Database Models & Schemas)

**Goal**: Establish data model for exam room arrangement system

**Tasks:**
- Create database models with relationships
- Create Pydantic schemas for validation
- Generate database migration
- Define TypeScript interfaces for frontend

### Phase 2: Core Service Layer

**Goal**: Implement business logic for room arrangement

**Tasks:**
- Exam room assignment algorithms
- Exam number generation logic
- Proctor assignment logic
- Conflict detection and resolution

### Phase 3: API Endpoints

**Goal**: Expose room arrangement functionality via REST API

**Tasks:**
- Room assignment endpoints
- Proctor management endpoints
- Bulk operations (auto-assign all)
- Document generation endpoints

### Phase 4: Document Generation Service

**Goal**: Create PDF/Excel export functionality

**Tasks:**
- Seating chart PDF generation
- Exam ticket PDF generation
- Proctor handbook PDF generation
- Excel export for room lists

### Phase 5: Frontend Integration

**Goal**: Integrate room arrangement into exam creation workflow

**Tasks:**
- Add Step 3 UI to Dashboard.vue
- Create room arrangement panel component
- Implement room preview dialog
- Add export functionality UI

### Phase 6: Testing & Validation

**Goal**: Ensure functionality works correctly

**Tasks:**
- Unit tests for service layer
- Integration tests for API endpoints
- End-to-end workflow testing
- Manual validation of document generation

---

## STEP-BY-STEP TASKS

### Phase 1: Foundation

### TASK 1.1: CREATE ExamRoom Models

**File**: `/Users/382241106qq.com/inspireed-platform-main/backend/app/models/exam_room.py`

**IMPLEMENT**: Create three SQLAlchemy models for exam room management

**PATTERN**: Mirror existing model patterns from `evaluation.py:116-217`

```python
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, JSON, Index as SQLIndex
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime

class ExamRoom(Base):
    """考场模型"""
    __tablename__ = "exam_rooms"

    id = Column(Integer, primary_key=True, index=True)
    exam_id = Column(Integer, ForeignKey("exams.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False, comment="考场名称：第1考场")
    school_id = Column(Integer, ForeignKey("schools.id"), nullable=False)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=True, comment="使用的教室ID")
    capacity = Column(Integer, nullable=False, default=30, comment="考场容量")
    seat_count = Column(Integer, nullable=False, default=0, comment="实际座位数")

    # 考号范围
    exam_number_start = Column(String(20), comment="起始考号")
    exam_number_end = Column(String(20), comment="结束考号")

    # 考场配置
    arrangement_type = Column(String(20), default="by_class", comment="编排类型：by_class/mixed")
    seat_pattern = Column(String(20), default="s_shape", comment="座位排列：sequential/s_shape")

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    exam = relationship("Exam", back_populates="exam_rooms")
    school = relationship("School")
    room = relationship("Room")
    students = relationship("ExamRoomStudent", back_populates="exam_room", cascade="all, delete-orphan")
    proctors = relationship("ExamProctor", back_populates="exam_room", cascade="all, delete-orphan")

class ExamRoomStudent(Base):
    """考场学生关联模型"""
    __tablename__ = "exam_room_students"

    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("exam_rooms.id", ondelete="CASCADE"), nullable=False, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    exam_number = Column(String(20), nullable=False, comment="考号")
    seat_number = Column(Integer, nullable=False, comment="座位号 1-30")
    table_number = Column(Integer, nullable=True, comment="桌子号（可选）")

    # 冗余字段（加速查询）
    student_id_number = Column(String(50), comment="学籍号")
    student_name = Column(String(100), comment="学生姓名（快照）")
    school_id = Column(Integer, ForeignKey("schools.id"))
    classroom_id = Column(Integer, ForeignKey("classrooms.id"))

    unique_constraint = UniqueConstraint("room_id", "exam_number", name="uq_room_exam_number")
    unique_constraint = UniqueConstraint("room_id", "seat_number", name="uq_room_seat_number")

    created_at = Column(DateTime, default=datetime.utcnow)

    # 关系
    exam_room = relationship("ExamRoom", back_populates="students")
    student = relationship("User")

class ExamProctor(Base):
    """监考教师模型"""
    __tablename__ = "exam_proctors"

    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("exam_rooms.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    proctor_type = Column(String(20), nullable=False, comment="监考类型：primary/assistant")
    responsibilities = Column(JSON, nullable=True, comment="职责列表")

    created_at = Column(DateTime, default=datetime.utcnow)

    # 关系
    exam_room = relationship("ExamRoom", back_populates="proctors")
    user = relationship("User")
```

**GOTCHA**:
- Must add `back_populates` to Exam model in `evaluation.py` after creation
- Cascade delete is critical for referential integrity
- Unique constraints prevent duplicate assignments

**VALIDATE**: `cd backend && python -c "from app.models.exam_room import ExamRoom, ExamRoomStudent, ExamProctor; print('Models imported successfully')"`

### TASK 1.2: UPDATE Exam Model

**File**: `/Users/382241106qq.com/inspireed-platform-main/backend/app/models/evaluation.py`

**ADD**: Add relationship to ExamRoom model

**FIND**: Locate Exam model class (around line 116)

**IMPORTS**: Add `from sqlalchemy.orm import relationship` if not present

```python
# In Exam class (around line 150-160, after created_by field)
# Add this relationship:
exam_rooms = relationship("ExamRoom", back_populates="exam", cascade="all, delete-orphan")
```

**VALIDATE**: `cd backend && python -c "from app.models.evaluation import Exam; print('Exam model loaded'); print(hasattr(Exam, 'exam_rooms'))"`

### TASK 1.3: CREATE Pydantic Schemas

**File**: `/Users/382241106qq.com/inspireed-platform-main/backend/app/schemas/exam_room.py`

**IMPLEMENT**: Create request/response schemas following pattern from `schemas/evaluation.py`

```python
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

# Base Schemas
class ExamRoomStudentBase(BaseModel):
    student_id: int
    exam_number: str = Field(..., max_length=20, description="考号")
    seat_number: int = Field(..., ge=1, le=50, description="座位号")
    student_id_number: Optional[str] = None
    student_name: Optional[str] = None
    school_id: Optional[int] = None
    classroom_id: Optional[int] = None

class ExamProctorBase(BaseModel):
    user_id: int
    proctor_type: str = Field(..., pattern="^(primary|assistant)$", description="监考类型")

# Exam Room Schemas
class ExamRoomBase(BaseModel):
    name: str = Field(..., max_length=100, description="考场名称")
    room_id: Optional[int] = Field(None, description="使用的教室ID")
    capacity: int = Field(30, ge=1, le=100, description="考场容量")
    arrangement_type: str = Field("by_class", pattern="^(by_class|mixed)$")
    seat_pattern: str = Field("s_shape", pattern="^(sequential|s_shape)$")

class ExamRoomCreate(ExamRoomBase):
    pass

class ExamRoomUpdate(BaseModel):
    capacity: Optional[int] = Field(None, ge=1, le=100)
    arrangement_type: Optional[str] = None
    seat_pattern: Optional[str] = None

class ExamRoomResponse(ExamRoomBase):
    id: int
    exam_id: int
    school_id: int
    seat_count: int
    exam_number_start: Optional[str]
    exam_number_end: Optional[str]
    students: List[ExamRoomStudentBase] = []
    proctors: List[ExamProctorBase] = []
    created_at: datetime
    updated_at: datetime

# Bulk Operations
class AutoAssignRoomsRequest(BaseModel):
    capacity_per_room: int = Field(30, ge=10, le=100, description="每个考场人数")
    arrangement_type: str = Field("by_class", pattern="^(by_class|mixed)$")
    seat_pattern: str = Field("s_shape", pattern="^(sequential|s_shape)$")
    use_existing_rooms: bool = Field(True, description="是否使用现有教室作为考场")

class AutoAssignProctorsRequest(BaseModel):
    auto_assign: bool = True
    avoid_own_class: bool = Field(True, description="避免监考本班")
    same_school_only: bool = Field(True, description="仅本校教师")
```

**PATTERN**: Follow schema patterns from `schemas/evaluation.py:10-100`

**VALIDATE**: `cd backend && python -c "from app.schemas.exam_room import ExamRoomCreate; print('Schemas imported successfully')"`

### TASK 1.4: CREATE Database Migration

**File**: `/Users/382241106qq.com/inspireed-platform-main/backend/alembic/versions/{generate_timestamp}_add_exam_room_system.py`

**IMPLEMENT**: Generate Alembic migration for new tables

**PATTERN**: Follow migration patterns from `alembic/versions/20260116_2108_add_room_management_system.py`

```python
"""add exam room system

Revision ID: {timestamp}
Revises: 20260113_1400_add_value_added_evaluation_system
Create Date: 2024-01-17

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '{timestamp}'
down_revision = '20260113_1400_add_value_added_evaluation_system'
branch_labels = None
depends_on = None

def upgrade():
    # Create exam_rooms table
    op.create_table(
        'exam_rooms',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('exam_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['exam_rooms.exam_id'], ['exams.id'], ondelete='CASCADE'),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('school_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['exam_rooms.school_id'], ['schools.id'], ),
        sa.Column('room_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['exam_rooms.room_id'], ['rooms.id'], ),
        sa.Column('capacity', sa.Integer(), nullable=False, server_default='30'),
        sa.Column('seat_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('exam_number_start', sa.String(length=20), nullable=True),
        sa.Column('exam_number_end', sa.String(length=20), nullable=True),
        sa.Column('arrangement_type', sa.String(length=20), nullable=False, server_default='by_class'),
        sa.Column('seat_pattern', sa.String(length=20), nullable=False, server_default='s_shape'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('idx_exam_rooms_exam_id', 'exam_id')
    )

    # Create exam_room_students table
    op.create_table(
        'exam_room_students',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('room_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['exam_room_students.room_id'], ['exam_rooms.id'], ondelete='CASCADE'),
        sa.Column('student_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['exam_room_students.student_id'], ['users.id'], ),
        sa.Column('exam_number', sa.String(length=20), nullable=False),
        sa.Column('seat_number', sa.Integer(), nullable=False),
        sa.Column('table_number', sa.Integer(), nullable=True),
        sa.Column('student_id_number', sa.String(length=50), nullable=True),
        sa.Column('student_name', sa.String(length=100), nullable=True),
        sa.Column('school_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['exam_room_students.school_id'], ['schools.id'], ),
        sa.Column('classroom_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['exam_room_students.classroom_id'], ['classrooms.id'], ),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('idx_exam_room_students_room_id', 'room_id'),
        sa.UniqueConstraint('room_id', 'exam_number', name='uq_room_exam_number'),
        sa.UniqueConstraint('room_id', 'seat_number', name='uq_room_seat_number')
    )

    # Create exam_proctors table
    op.create_table(
        'exam_proctors',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('room_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['exam_proctors.room_id'], ['exam_rooms.id'], ondelete='CASCADE'),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['exam_proctors.user_id'], ['users.id'], ),
        sa.Column('proctor_type', sa.String(length=20), nullable=False),
        sa.Column('responsibilities', postgresql.JSON(astext_type='json'), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('idx_exam_proctors_room_id', 'room_id')
    )

def downgrade():
    op.drop_table('exam_proctors')
    op.drop_table('exam_room_students')
    op.drop_table('exam_rooms')
```

**GOTCHA**:
- Must set correct down_revision (check latest migration in `alembic/versions/`)
- Use `{timestamp}` format: run `alembic revision -m "add exam room system"` to generate

**VALIDATE**: `cd backend && alembic upgrade head && echo "Migration applied successfully"`

---

### Phase 2: Core Service Layer

### TASK 2.1: CREATE ExamRoomService

**File**: `/Users/382241106qq.com/inspireed-platform-main/backend/app/services/exam_room_service.py`

**IMPLEMENT**: Implement core business logic for room arrangement

**PATTERN**: Follow service patterns from `services/excel_import_service.py`

```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from sqlalchemy.orm import selectinload
from typing import List, Optional
import logging

from app.models.evaluation import Exam, ExamNumberMapping
from app.models.exam_room import ExamRoom, ExamRoomStudent, ExamProctor
from app.models.user import User, UserRole
from app.models.organization import School, Classroom
from app.models.room import Room
from app.schemas.exam_room import AutoAssignRoomsRequest, AutoAssignProctorsRequest

logger = logging.getLogger(__name__)

class ExamRoomService:
    """考场安排服务"""

    async def auto_assign_rooms(
        self,
        exam_id: int,
        request: AutoAssignRoomsRequest,
        db: AsyncSession
    ) -> List[ExamRoom]:
        """自动分配考场"""
        logger.info(f"Auto-assigning rooms for exam {exam_id}")

        # 1. Get exam
        result = await db.execute(
            select(Exam).options(selectinload(Exam.exam_subjects)).where(Exam.id == exam_id)
        )
        exam = result.scalar_one_or_none()
        if not exam:
            raise ValueError("考试不存在")

        # 2. Get students to assign (from exam number mappings or class_ids)
        students = await self._get_exam_students(exam, db)

        # 3. Calculate number of rooms needed
        num_students = len(students)
        capacity_per_room = request.capacity_per_room
        num_rooms = (num_students + capacity_per_room - 1) // capacity_per_room

        logger.info(f"Assigning {num_students} students to {num_rooms} rooms")

        # 4. Create exam rooms
        exam_rooms = []
        for i in range(num_rooms):
            room = ExamRoom(
                exam_id=exam_id,
                name=f"第{i+1}考场",
                school_id=exam.school_id,
                capacity=capacity_per_room,
                arrangement_type=request.arrangement_type,
                seat_pattern=request.seat_pattern,
                seat_count=0  # Will be updated when students assigned
            )

            if request.use_existing_rooms:
                # Try to find existing room
                assigned_room = await self._find_available_room(exam.school_id, capacity_per_room, db)
                if assigned_room:
                    room.room_id = assigned_room.id
                    room.name = assigned_room.name

            db.add(room)
            await db.flush()  # Get room.id

            exam_rooms.append(room)

        await db.commit()

        # 5. Assign students to rooms
        await self._assign_students_to_rooms(exam_rooms, students, request, db)

        # 6. Generate exam numbers
        await self._generate_exam_numbers(exam_rooms, db)

        logger.info(f"Successfully created {len(exam_rooms)} exam rooms")
        return exam_rooms

    async def _get_exam_students(self, exam: Exam, db: AsyncSession) -> List[User]:
        """获取考试的学生"""
        # This would typically come from pre-selected students
        # For now, get from class_id if available, or return empty list
        result = await db.execute(
            select(User).where(
                and_(
                    User.role == UserRole.STUDENT,
                    User.grade_id == exam.grade_id,
                    User.school_id == exam.school_id
                )
            ).order_by(User.classroom_id, User.id)
        )
        return result.scalars().all()

    async def _find_available_room(
        self,
        school_id: int,
        min_capacity: int,
        db: AsyncSession
    ) -> Optional[Room]:
        """查找可用的教室"""
        result = await db.execute(
            select(Room).where(
                and_(
                    Room.school_id == school_id,
                    Room.capacity >= min_capacity
                )
            ).order_by(Room.capacity.asc()).limit(1)
        )
        return result.scalar_one_or_none()

    async def _assign_students_to_rooms(
        self,
        exam_rooms: List[ExamRoom],
        students: List[User],
        request: AutoAssignRoomsRequest,
        db: AsyncSession
    ):
        """将学生分配到考场"""
        room_capacity = request.capacity_per_room

        if request.arrangement_type == "by_class":
            # 按班级编排
            await self._assign_by_class(exam_rooms, students, room_capacity, db)
        else:
            # 混排编排
            await self._assign_mixed(exam_rooms, students, room_capacity, db)

    async def _assign_by_class(
        self,
        exam_rooms: List[ExamRoom],
        students: List[User],
        capacity: int,
        db: AsyncSession
    ):
        """按班级分配学生"""
        room_index = 0
        room = exam_rooms[room_index]
        current_seat = 1

        for student in students:
            # Check if room is full
            if current_seat > capacity:
                room_index += 1
                if room_index >= len(exam_rooms):
                    break
                room = exam_rooms[room_index]
                current_seat = 1

            # Create seat assignment
            seat = ExamRoomStudent(
                room_id=room.id,
                student_id=student.id,
                seat_number=current_seat,
                student_id_number=student.student_id_number,
                student_name=student.full_name,
                school_id=student.school_id,
                classroom_id=student.classroom_id
            )
            db.add(seat)

            current_seat += 1

        # Update room seat counts
        for i, room in enumerate(exam_rooms):
            result = await db.execute(
                select(func.count(ExamRoomStudent.id))
                .where(ExamRoomStudent.room_id == room.id)
            )
            room.seat_count = result.scalar()

        await db.commit()

    async def _assign_mixed(
        self,
        exam_rooms: List[ExamRoom],
        students: List[User],
        capacity: int,
        db: AsyncSession
    ):
        """混排分配学生"""
        # Simple round-robin for mixed seating
        for i, student in enumerate(students):
            room_index = i % len(exam_rooms)
            room = exam_rooms[room_index]
            seat_number = (i // len(exam_rooms)) + 1

            if seat_number > capacity:
                break

            seat = ExamRoomStudent(
                room_id=room.id,
                student_id=student.id,
                seat_number=seat_number,
                student_id_number=student.student_id_number,
                student_name=student.full_name,
                school_id=student.school_id,
                classroom_id=student.classroom_id
            )
            db.add(seat)

        # Update room seat counts
        for room in exam_rooms:
            result = await db.execute(
                select(func.count(ExamRoomStudent.id))
                .where(ExamRoomStudent.room_id == room.id)
            )
            room.seat_count = result.scalar()

        await db.commit()

    async def _generate_exam_numbers(
        self,
        exam_rooms: List[ExamRoom],
        db: AsyncSession
    ):
        """生成考号"""
        year = datetime.now().year

        for room in exam_rooms:
            # Get students in this room ordered by seat number
            result = await db.execute(
                select(ExamRoomStudent)
                .where(ExamRoomStudent.room_id == room.id)
                .order_by(ExamRoomStudent.seat_number)
            )
            students = result.scalars().all()

            if not students:
                continue

            # Generate exam numbers: {year}{room_idx:02d}{seat:03d}
            room_idx = int(room.name.replace("第", "").replace("考场", ""))
            start_number = f"{year}{room_idx:02d}001"

            for student in students:
                exam_number = f"{year}{room_idx:02d}{student.seat_number:03d}"
                student.exam_number = exam_number

            room.exam_number_start = start_number
            room.exam_number_end = f"{year}{room_idx:02d}{room.seat_count:03d}"

        await db.commit()

    async def auto_assign_proctors(
        self,
        exam_id: int,
        request: AutoAssignProctorsRequest,
        db: AsyncSession
    ) -> List[ExamProctor]:
        """自动分配监考教师"""
        logger.info(f"Auto-assigning proctors for exam {exam_id}")

        # 1. Get exam rooms
        result = await db.execute(
            select(ExamRoom).where(ExamRoom.exam_id == exam_id)
        )
        rooms = result.scalars().all()

        # 2. Get available teachers
        exam = await db.get(Exam, exam_id)
        teachers_result = await db.execute(
            select(User).where(
                and_(
                    User.role == UserRole.TEACHER,
                    User.school_id == exam.school_id
                )
            )
        )
        teachers = teachers_result.scalars().all()

        if len(teachers) < len(rooms) * 2:
            raise ValueError(f"教师数量不足：需要 {len(rooms) * 2} 名教师，当前 {len(teachers)} 名")

        # 3. Assign 2 proctors per room
        proctors = []
        teacher_idx = 0

        for room in rooms:
            # Get room students to check for conflicts
            students_result = await db.execute(
                select(ExamRoomStudent).where(ExamRoomStudent.room_id == room.id)
            )
            students = students_result.scalars().all()
            student_class_ids = set(s.classroom_id for s in students)

            # Find available teachers (avoid conflicts if requested)
            primary_teacher, assistant_teacher = await self._find_proctors_for_room(
                teachers, student_class_ids, request, db
            )

            # Create proctor assignments
            primary = ExamProctor(
                room_id=room.id,
                user_id=primary_teacher.id,
                proctor_type="primary"
            )

            assistant = ExamProctor(
                room_id=room.id,
                user_id=assistant_teacher.id,
                proctor_type="assistant"
            )

            db.add(primary)
            db.add(assistant)
            proctors.extend([primary, assistant])

        await db.commit()
        logger.info(f"Successfully assigned {len(proctors)} proctors")
        return proctors

    async def _find_proctors_for_room(
        self,
        teachers: List[User],
        student_class_ids: set,
        request: AutoAssignProctorsRequest,
        db: AsyncSession
    ):
        """为考场查找合适的监考教师"""
        available = []
        used_teacher_ids = set()

        for teacher in teachers:
            if teacher.id in used_teacher_ids:
                continue

            # Check if teacher should avoid this room
            if request.avoid_own_class:
                # Check if teacher is homeroom teacher for any class in this room
                teacher_classes_result = await db.execute(
                    select(Classroom).where(Classroom.head_teacher_id == teacher.id)
                )
                teacher_classes = set(c.id for c in teacher_classes_result.scalars().all())

                if teacher_classes & student_class_ids:
                    continue  # Skip this teacher

            available.append(teacher)
            if len(available) >= 2:
                break

        if len(available) < 2:
            # Fallback: just use first 2 teachers
            return teachers[0], teachers[1] if len(teachers) > 1 else None

        return available[0], available[1]
```

**PATTERN**: Async database operations pattern from `backend/app/api/v1/exams.py`

**VALIDATE**: `cd backend && python -c "from app.services.exam_room_service import ExamRoomService; print('Service imported successfully')"`

---

### Phase 3: API Endpoints

### TASK 3.1: CREATE Exam Room API Endpoints

**File**: `/Users/382241106qq.com/inspireed-platform-main/backend/app/api/v1/exam_rooms.py`

**IMPLEMENT**: Create REST API endpoints for exam room management

**PATTERN**: Follow API patterns from `api/v1/exams.py` (authentication, validation, error handling)

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.database import get_db
from app.core.auth import get_current_active_user
from app.models.user import User, UserRole
from app.models.exam_room import ExamRoom, ExamProctor
from app.schemas.exam_room import (
    ExamRoomCreate, ExamRoomUpdate, ExamRoomResponse,
    AutoAssignRoomsRequest, AutoAssignProctorsRequest
)
from app.services.exam_room_service import ExamRoomService

router = APIRouter(prefix="/exams/{exam_id}/rooms", tags=["exam-rooms"])

@router.post("/auto-assign", response_model=List[ExamRoomResponse])
async def auto_assign_exam_rooms(
    exam_id: int,
    request: AutoAssignRoomsRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """自动分配考场"""
    # Permission check
    if current_user.role not in [UserRole.ADMIN, UserRole.DISTRICT_ADMIN, UserRole.SCHOOL_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )

    # Validate exam exists
    from app.models.evaluation import Exam
    exam = await db.get(Exam, exam_id)
    if not exam:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="考试不存在"
        )

    # Auto assign rooms
    service = ExamRoomService()
    try:
        rooms = await service.auto_assign_rooms(exam_id, request, db)
        return rooms
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/proctors/auto-assign")
async def auto_assign_proctors(
    exam_id: int,
    request: AutoAssignProctorsRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """自动分配监考教师"""
    if current_user.role not in [UserRole.ADMIN, UserRole.DISTRICT_ADMIN, UserRole.SCHOOL_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )

    service = ExamRoomService()
    try:
        proctors = await service.auto_assign_proctors(exam_id, request, db)
        return {"message": f"成功分配 {len(proctors)} 名监考教师"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("", response_model=List[ExamRoomResponse])
async def list_exam_rooms(
    exam_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """获取考试的所有考场"""
    from sqlalchemy import select

    result = await db.execute(
        select(ExamRoom)
        .options(selectinload(ExamRoom.students))
        .options(selectinload(ExamRoom.proctors))
        .where(ExamRoom.exam_id == exam_id)
        .order_by(ExamRoom.id)
    )
    rooms = result.scalars().all()
    return rooms

@router.get("/{room_id}", response_model=ExamRoomResponse)
async def get_exam_room(
    exam_id: int,
    room_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """获取考场详情"""
    result = await db.execute(
        select(ExamRoom)
        .options(selectinload(ExamRoom.students))
        .options(selectinload(ExamRoom.proctors))
        .where(and_(ExamRoom.id == room_id, ExamRoom.exam_id == exam_id))
    )
    room = result.scalar_one_or_none()

    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="考场不存在"
        )

    return room

@router.put("/{room_id}")
async def update_exam_room(
    exam_id: int,
    room_id: int,
    room_update: ExamRoomUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """更新考场信息"""
    # Implementation...
    pass

@router.delete("/{room_id}")
async def delete_exam_room(
    exam_id: int,
    room_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """删除考场"""
    # Implementation...
    pass
```

**GOTCHA**:
- Must import `and_` from sqlalchemy
- Permission check must happen before database operations
- Use `selectinload` to eager load relationships

**VALIDATE**: `cd backend && curl -X GET http://localhost:8000/api/v1/exams/1/rooms -H "Authorization: Bearer test-token"`

---

### Phase 4: Document Generation Service

### TASK 4.1: CREATE Document Generator Service

**File**: `/Users/382241106qq.com/inspireed-platform-main/backend/app/services/exam_document_generator.py`

**IMPLEMENT**: Create PDF generation service using reportlab

```python
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from io import BytesIO
from typing import List
import logging

from app.models.exam_room import ExamRoom
from app.models.evaluation import Exam

logger = logging.getLogger(__name__)

# Register Chinese fonts (assuming system has these fonts)
try:
    pdfmetrics.registerFont(TTFont('SimSun', 'SimSun.ttf'))
    pdfmetrics.registerFont(TTFont('SimHei', 'SimHei.ttf'))
except:
    logger.warning("Chinese fonts not found, using default fonts")

class ExamDocumentGenerator:
    """考试文档生成器"""

    def generate_seating_chart_pdf(self, room: ExamRoom, exam: Exam) -> bytes:
        """生成座位表PDF"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)

        # Get room data
        students = sorted(room.students, key=lambda s: s.seat_number)

        # Build story
        story = []
        styles = getSampleStyleSheet()

        # Title
        title_style = ParagraphStyle(
            'Title',
            parent=styles['Heading1'],
            alignment=TA_CENTER,
            fontSize=18,
            spaceAfter=12
        )
        story.append(Paragraph(f"{exam.name} - 座位表", title_style))
        story.append(Paragraph(f"{room.name}", styles['Heading2']))

        # Room info
        info_data = [
            ['考场位置', room.room.name if room.room else '未指定'],
            ['监考教师', self._get_proctor_names(room)],
            ['考号范围', f"{room.exam_number_start} - {room.exam_number_end}"],
            ['考试时间', exam.exam_date.strftime('%Y-%m-%d %H:%M')]
        ]

        info_table = Table(info_data, colWidths=[2*inch, 4*inch])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, 1), colors.grey),
            ('TEXTCOLOR', (0, 0), (0, 1), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
        ]))
        story.append(info_table)
        story.append(Spacer(1*inch))

        # Seating arrangement
        seats_per_row = 10
        rows = (len(students) + seats_per_row - 1) // seats_per_row

        for row in range(rows):
            start_idx = row * seats_per_row
            end_idx = min(start_idx + seats_per_row, len(students))
            row_students = students[start_idx:end_idx]

            # Create seat grid
            seat_data = []
            seat_row = []
            for student in row_students:
                seat_row.extend([
                    str(student.seat_number),
                    student.student_name,
                    student.exam_number
                ])

            while len(seat_row) < seats_per_row * 3:
                seat_row.extend(['', '', ''])

            seat_data.append(seat_row)

            # Create table
            seat_table = Table(seat_data, colWidths=[0.5*inch, 1.5*inch, 1.5*inch])
            seat_table.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ]))
            story.append(seat_table)
            story.append(Spacer(0.3*inch))

        doc.build(story)
        return buffer.getvalue()

    def _get_proctor_names(self, room: ExamRoom) -> str:
        """获取监考教师姓名"""
        names = []
        for proctor in room.proctors:
            if proctor.proctor_type == 'primary':
                names.append(f"{proctor.user.full_name}(主监考)" if proctor.user.full_name else "")
            else:
                names.append(f"{proctor.user.full_name}(副监考)" if proctor.user.full_name else "")
        return "、".join(names)
```

**PATTERN**: Export pattern from `course_export.py`

**VALIDATE**: `cd backend && python -c "from app.services.exam_document_generator import ExamDocumentGenerator; print('Document generator imported')"`

---

### Phase 5: Frontend Integration

### TASK 5.1: CREATE TypeScript Interfaces

**File**: `/Users/382241106qq.com/inspireed-platform-main/frontend/src/types/exam.ts`

**ADD**: Add exam room type definitions

**FIND**: Locate end of file (around line 150+)

```typescript
// Exam Room Types
export interface ExamRoom {
  id: number
  exam_id: number
  name: string
  school_id: number
  room_id?: number
  capacity: number
  seat_count: number
  exam_number_start?: string
  exam_number_end?: string
  arrangement_type: 'by_class' | 'mixed'
  seat_pattern: 'sequential' | 's_shape'
  students: ExamRoomStudent[]
  proctors: ExamProctor[]
  created_at: string
  updated_at: string
}

export interface ExamRoomStudent {
  id: number
  room_id: number
  student_id: number
  exam_number: string
  seat_number: number
  table_number?: number
  student_id_number?: string
  student_name?: string
  school_id?: number
  classroom_id?: number
}

export interface ExamProctor {
  id: number
  room_id: number
  user_id: number
  proctor_type: 'primary' | 'assistant'
  responsibilities?: any
  user?: {
    id: number
    full_name: string
    username: string
  }
}

export interface AutoAssignRoomsRequest {
  capacity_per_room: number
  arrangement_type: 'by_class' | 'mixed'
  seat_pattern: 'sequential' | 's_shape'
  use_existing_rooms: boolean
}

export interface AutoAssignProctorsRequest {
  auto_assign: boolean
  avoid_own_class: boolean
  same_school_only: boolean
}
```

**PATTERN**: Follow existing type definitions in same file

**VALIDATE**: `cd frontend && npm run type-check`

### TASK 5.2: CREATE Exam Room API Service

**File**: `/Users/382241106qq.com/inspireed-platform-main/frontend/src/services/examRoom.ts`

**IMPLEMENT**: Create API client for exam room operations

**PATTERN**: Follow service patterns from `evaluation.ts:62-120`

```typescript
import axios from 'axios'
import type {
  ExamRoom,
  AutoAssignRoomsRequest,
  AutoAssignProctorsRequest
} from '@/types/exam'

function getApiBaseUrl(): string {
  const hostname = window.location.hostname
  const protocol = window.location.protocol

  if (import.meta.env.VITE_API_BASE_URL) {
    return import.meta.env.VITE_API_BASE_URL
  }

  if (hostname.includes('cloudstudio.club')) {
    if (hostname.includes('--')) {
      return `https://${hostname.replace(/--\d+/, '--8000')}/api/v1`
    }
  }

  return `${protocol}//${hostname}:8000/api/v1`
}

const apiClient = axios.create({
  baseURL: getApiBaseUrl(),
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' }
})

// Request interceptor
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
}, (error) => Promise.reject(error))

// Response interceptor
apiClient.interceptors.response.use(
  (response) => response.data,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export const examRoomService = {
  // Auto assign rooms
  async autoAssignRooms(
    examId: number,
    data: AutoAssignRoomsRequest
  ): Promise<ExamRoom[]> {
    return await apiClient.post(`/exams/${examId}/rooms/auto-assign`, data)
  },

  // List exam rooms
  async getExamRooms(examId: number): Promise<ExamRoom[]> {
    return await apiClient.get(`/exams/${examId}/rooms`)
  },

  // Get room details
  async getExamRoom(examId: number, roomId: number): Promise<ExamRoom> {
    return await apiClient.get(`/exams/${examId}/rooms/${roomId}`)
  },

  // Update room
  async updateExamRoom(
    examId: number,
    roomId: number,
    data: Partial<ExamRoom>
  ): Promise<ExamRoom> {
    return await apiClient.put(`/exams/${examId}/rooms/${roomId}`, data)
  },

  // Delete room
  async deleteExamRoom(examId: number, roomId: number): Promise<void> {
    return await apiClient.delete(`/exams/${examId}/rooms/${roomId}`)
  },

  // Auto assign proctors
  async autoAssignProctors(
    examId: number,
    data: AutoAssignProctorsRequest
  ): Promise<{ message: string }> {
    return await apiClient.post(`/exams/${examId}/rooms/proctors/auto-assign`, data)
  },

  // Export seating chart PDF
  async exportSeatingChart(examId: number, roomId: number): Promise<Blob> {
    const response = await apiClient.get(
      `/exams/${examId}/rooms/${roomId}/export/seating-chart`,
      { responseType: 'blob' }
    )
    return response.data
  },

  // Export exam tickets
  async exportExamTickets(examId: number): Promise<Blob> {
    const response = await apiClient.get(
      `/exams/${examId}/export/tickets`,
      { responseType: 'blob' }
    )
    return response.data
  },

  // Export proctor handbook
  async exportProctorHandbook(examId: number, roomId: number): Promise<Blob> {
    const response = await apiClient.get(
      `/exams/${examId}/rooms/${roomId}/export/proctor-handbook`,
      { responseType: 'blob' }
    )
    return response.data
  }
}
```

**VALIDATE**: `cd frontend && npm run type-check`

### TASK 5.3: INTEGRATE Step 3 UI into Dashboard

**File**: `/Users/382241106qq.com/inspireed-platform-main/frontend/src/pages/DistrictExamAdmin/Dashboard.vue`

**ADD**: Insert Step 3 (Exam Room Arrangement) after Step 2

**FIND**: Locate line 1045 (end of Step 2) and line 1047 (start of Step 3)

**IMPLEMENT**: Replace current Step 3 and Step 4 with new structure

```vue
<!-- Step 3: 考场安排 ⭐ NEW -->
<div v-show="schoolExamStep === 2" class="step-content">
  <h4>🏫 考场安排</h4>

  <!-- 考场信息概览 -->
  <el-alert
    type="info"
    :closable="false"
    show-icon
    style="margin-bottom: 20px;"
  >
    <template #title>
      当前考试科目：<strong>{{ selectedSubjectsCount }}</strong> 门
      参考学生：<strong>{{ estimatedStudentCount }}</strong> 名
      预计考场数：<strong>{{ estimatedRoomsCount }}</strong> 个
    </template>
  </el-alert>

  <!-- 编排规则 -->
  <el-form :model="roomArrangementForm" label-width="140px" style="margin-bottom: 20px;">
    <el-row :gutter="20">
      <el-col :span="12">
        <el-form-item label="每个考场人数">
          <el-input-number
            v-model="roomArrangementForm.capacityPerRoom"
            :min="10"
            :max="100"
            :step="5"
            @change="updateEstimatedRoomsCount"
          />
        </el-form-item>
      </el-col>
      <el-col :span="12">
        <el-form-item label="编排方式">
          <el-radio-group v-model="roomArrangementForm.arrangementType">
            <el-radio label="by_class">按班级</el-radio>
            <el-radio label="mixed">混排</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-col>
    </el-row>
    <el-row :gutter="20">
      <el-col :span="12">
        <el-form-item label="座位排列">
          <el-radio-group v-model="roomArrangementForm.seatPattern">
            <el-radio label="s_shape">S型</el-radio>
            <el-radio label="sequential">顺序</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-col>
      <el-col :span="12">
        <el-form-item label="考场位置">
          <el-checkbox v-model="roomArrangementForm.useExistingRooms">
            使用现有教室作为考场
          </el-checkbox>
        </el-form-item>
      </el-col>
    </el-row>
  </el-form>

  <!-- 操作按钮 -->
  <div style="margin-bottom: 20px;">
    <el-button
      type="primary"
      size="large"
      @click="autoAssignExamRooms"
      :loading="arrangingRooms"
      :icon="MagicStick"
    >
      自动编排考场
    </el-button>
    <el-button
      v-if="examRooms.length > 0"
      @click="autoAssignProctors"
      :loading="assigningProctors"
    >
      分配监考教师
    </el-button>
  </div>

  <!-- 考场列表 -->
  <div v-if="examRooms.length > 0">
    <h5 style="margin-bottom: 10px;">考场列表</h5>
    <el-table :data="examRooms" border stripe>
      <el-table-column prop="name" label="考场" width="120" />
      <el-table-column label="容量" width="80">
        <template #default="{ row }">
          {{ row.seat_count }}/{{ row.capacity }}
        </template>
      </el-table-column>
      <el-table-column label="监考教师" width="200">
        <template #default="{ row }">
          {{ getProctorNames(row) }}
        </template>
      </el-table-column>
      <el-table-column label="考号范围" width="180">
        <template #default="{ row }">
          {{ row.exam_number_start }} - {{ row.exam_number_end }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200">
        <template #default="{ row }">
          <el-button size="small" @click="viewRoomDetail(row)">详情</el-button>
          <el-button size="small" @click="exportSeatingChart(row)">导出座位表</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</div>

<!-- Step 4: 预览确认 ⭐ UPDATED -->
<div v-show="schoolExamStep === 3" class="step-content">
  <h4>👥 预览确认</h4>

  <!-- 考试基本信息 -->
  <el-descriptions :column="2" border style="margin-bottom: 20px;">
    <el-descriptions-item label="考试名称">{{ schoolExamForm.name }}</el-descriptions-item>
    <el-descriptions-item label="学期">{{ getSemesterName(schoolExamForm.semester_id) }}</el-descriptions-item>
    <el-descriptions-item label="考试日期">{{ schoolExamForm.exam_date }}</el-descriptions-item>
    <el-descriptions-item label="参考班级">{{ schoolExamForm.class_ids.length }} 个班级</el-descriptions-item>
    <el-descriptions-item label="参考学生">{{ confirmedStudents.length }} 名</el-descriptions-item>
    <el-descriptions-item label="考试科目">{{ selectedSubjectsCount }} 门</el-descriptions-item>
    <el-descriptions-item label="考场数量">{{ examRooms.length }} 个</el-descriptions-item>
  </el-descriptions>

  <!-- 考试科目列表 -->
  <h5 style="margin: 20px 0 10px 0;">考试科目</h5>
  <el-table :data="getSelectedSubjectsList()" border stripe size="small">
    <el-table-column prop="name" label="科目" width="120" />
    <el-table-column prop="max_score" label="满分值" width="80" />
    <el-table-column prop="duration" label="时长" width="80">
      <template #default="{ row }">
        {{ row.duration }}分钟
      </template>
    </el-table-column>
  </el-table>

  <!-- 导出选项 -->
  <div style="margin-top: 30px;">
    <h5 style="margin-bottom: 10px;">导出文档</h5>
    <el-checkbox-group v-model="exportOptions">
      <el-checkbox label="roomList">考场安排表 (Excel)</el-checkbox>
      <el-checkbox label="seatingCharts">座位表 (PDF)</el-checkbox>
      <el-checkbox label="examTickets">准考证 (PDF)</el-checkbox>
      <el-checkbox label="proctorHandbooks">监考手册 (PDF)</el-checkbox>
    </el-checkbox-group>
    <div style="margin-top: 15px;">
      <el-button
        type="primary"
        @click="exportExamDocuments"
        :loading="exporting"
        :icon="Download"
      >
        导出选中文档
      </el-button>
    </div>
  </div>
</div>

<!-- Step 5: 完成 ⭐ UPDATED -->
<div v-show="schoolExamStep === 4" class="step-content">
  <el-result
    icon="success"
    title="考试创建成功！"
    sub-title="所有信息已保存，可以开始导出文档了"
  >
    <template #extra>
      <el-space>
        <el-button @click="exportExamDocuments">导出文档</el-button>
        <el-button type="primary" @click="closeSchoolQuickExamDialog">
          返回首页
        </el-button>
      </el-space>
    </template>
  </el-result>
</div>
```

**ADD** reactive data and computed properties:

```typescript
// In <script setup> section
import { examRoomService } from '@/services/examRoom'
import { MagicStick, Download } from '@element-plus/icons-vue'

// Room arrangement state
const roomArrangementForm = reactive({
  capacityPerRoom: 30,
  arrangementType: 'by_class' as 'by_class' | 'mixed',
  seatPattern: 's_shape' as 'sequential' | 's_shape',
  useExistingRooms: true
})

const examRooms = ref<ExamRoom[]>([])
const arrangingRooms = ref(false)
const assigningProctors = ref(false)

// Computed properties
const estimatedRoomsCount = computed(() => {
  const students = estimatedStudentCount.value || 0
  const capacity = roomArrangementForm.capacityPerRoom
  return Math.ceil(students / capacity)
})

// Methods
const autoAssignExamRooms = async () => {
  arrangingRooms.value = true
  try {
    const examId = createdExamId.value // from previous step
    const rooms = await examRoomService.autoAssignRooms(examId, roomArrangementForm)
    examRooms.value = rooms
    ElMessage.success(`成功创建 ${rooms.length} 个考场`)
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '编排考场失败')
  } finally {
    arrangingRooms.value = false
  }
}

const autoAssignProctors = async () => {
  assigningProctors.value = true
  try {
    await examRoomService.autoAssignProctors(createdExamId.value, {
      auto_assign: true,
      avoid_own_class: true,
      same_school_only: true
    })
    ElMessage.success('监考教师分配成功')
    // Refresh room data to show proctors
    await loadExamRooms()
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '分配监考失败')
  } finally {
    assigningProctors.value = false
  }
}
```

**GOTCHA**:
- Step indices change: Step 3 becomes room arrangement, Step 4 becomes preview, Step 5 becomes complete
- Must update `schoolExamStep` references in nextStep() and prevStep()
- Must add Icons import for MagicStick and Download

**VALIDATE**: `cd frontend && npm run type-check && npm run lint`

---

### Phase 6: Testing & Validation

### TASK 6.1: CREATE Backend Unit Tests

**File**: `/Users/382241106qq.com/inspireed-platform-main/backend/tests/test_exam_room_service.py`

**IMPLEMENT**: Create comprehensive unit tests for service layer

**PATTERN**: Follow test patterns from `tests/test_basic.py`

```python
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.exam_room import ExamRoom, ExamRoomStudent, ExamProctor
from app.models.evaluation import Exam
from app.models.user import User, UserRole
from app.schemas.exam_room import AutoAssignRoomsRequest
from app.services.exam_room_service import ExamRoomService

@pytest.mark.asyncio
async def test_auto_assign_rooms_by_class(db: AsyncSession):
    """测试按班级编排考场"""
    # Setup: Create exam and students
    exam = Exam(name="期末考试", semester_id=1, grade_id=1, exam_date="2024-01-20")
    db.add(exam)
    await db.commit()

    # Create test students
    students = []
    for i in range(90):  # 3 classrooms, 30 students each
        student = User(
            username=f"student{i}",
            full_name=f"学生{i}",
            role=UserRole.STUDENT,
            grade_id=1,
            school_id=1,
            classroom_id=1 + (i // 30)
        )
        db.add(student)
        students.append(student)
    await db.commit()

    # Execute
    service = ExamRoomService()
    request = AutoAssignRoomsRequest(
        capacity_per_room=30,
        arrangement_type="by_class",
        seat_pattern="s_shape",
        use_existing_rooms=False
    )

    rooms = await service.auto_assign_rooms(exam.id, request, db)

    # Assert
    assert len(rooms) == 3
    assert rooms[0].name == "第1考场"
    assert rooms[0].seat_count == 30
    assert rooms[0].exam_number_start is not None

@pytest.mark.asyncio
async def test_generate_exam_numbers(db: AsyncSession):
    """测试考号生成"""
    # Setup...

    # Execute
    service = ExamRoomService()
    await service._generate_exam_numbers(rooms, db)

    # Assert exam numbers follow format: YYYYMMSSS
    for room in rooms:
        assert room.exam_number_start is not None
        assert room.exam_number_end is not None
        assert room.exam_number_start.startswith("2024")  # Year format

@pytest.mark.asyncio
async def test_auto_assign_proctors_avoid_conflicts(db: AsyncSession):
    """测试监考教师自动分配（避免冲突）"""
    # Setup...

    # Execute
    service = ExamRoomService()
    proctors = await service.auto_assign_proctors(exam.id, request, db)

    # Assert each room has 2 proctors
    for room in rooms:
        room_proctors = [p for p in proctors if p.room_id == room.id]
        assert len(room_proctors) == 2
        assert any(p.proctor_type == 'primary' for p in room_proctors)
        assert any(p.proctor_type == 'assistant' for p in room_proctors)
```

**VALIDATE**: `cd backend && pytest tests/test_exam_room_service.py -v`

### TASK 6.2: CREATE API Integration Tests

**File**: `/Users/382241106qq.com/inspireed-platform-main/backend/tests/test_exam_room_api.py`

**IMPLEMENT**: Test API endpoints

```python
import pytest
from httpx import AsyncClient

BASE_URL = "http://localhost:8000/api/v1"

@pytest.mark.asyncio
async def test_auto_assign_rooms_endpoint():
    """测试考场自动编排API"""
    async with AsyncClient() as client:
        # Login first
        response = await client.post(
            f"{BASE_URL}/auth/login",
            json={"username": "admin@inspireed.com", "password": "admin123"}
        )
        assert response.status_code == 200
        token = response.json()["access_token"]

        # Create exam
        exam_response = await client.post(
            f"{BASE_URL}/exams/",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "name": "测试考试",
                "exam_type": "final",
                "semester_id": 1,
                "grade_id": 1,
                "exam_date": "2024-06-20T09:00:00"
            }
        )
        assert exam_response.status_code == 201
        exam_id = exam_response.json()["id"]

        # Auto assign rooms
        rooms_response = await client.post(
            f"{BASE_URL}/exams/{exam_id}/rooms/auto-assign",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "capacity_per_room": 30,
                "arrangement_type": "by_class",
                "seat_pattern": "s_shape",
                "use_existing_rooms": False
            }
        )
        assert rooms_response.status_code == 200
        rooms = rooms_response.json()
        assert len(rooms) > 0

@pytest.mark.asyncio
async def test_export_seating_chart():
    """测试导出座位表"""
    # Similar pattern for export endpoints
    pass
```

**VALIDATE**: `cd backend && pytest tests/test_exam_room_api.py -v`

---

## TESTING STRATEGY

### Unit Tests

**Scope**: Test business logic in isolation

- `test_auto_assign_rooms_by_class`: Verify students grouped by classroom
- `test_auto_assign_rooms_mixed`: Verify mixed classroom arrangement
- `test_generate_exam_numbers`: Verify exam number format uniqueness
- `test_auto_assign_proctors`: Verify proctor assignment rules
- `test_calculate_room_capacity`: Verify room capacity calculations

**Test Organization**: Use `pytest` with async support

### Integration Tests

**Scope**: Test API endpoints and database operations

- `test_auto_assign_rooms_endpoint`: Full request/response cycle
- `test_export_seating_chart`: PDF generation and download
- `test_exam_room_crud`: Create, read, update, delete operations
- `test_proctor_assignment_conflicts`: Verify conflict avoidance logic

**Fixtures Needed**:
- `db_session`: Async database session fixture
- `test_user`: Authenticated test user fixture
- `test_exam`: Sample exam fixture

### Edge Cases

**Must Test**:
- Empty student list handling
- Student count not divisible by room capacity
- Insufficient teachers for proctor assignment
- All teachers are homeroom teachers of exam classes
- Exam room capacity limits (min=10, max=100)
- Exam number uniqueness (no duplicates across rooms)
- Concurrent room assignments (race conditions)

---

## VALIDATION COMMANDS

### Level 1: Syntax & Style

```bash
# Backend type checking and linting
cd backend
# Check Python syntax
python -m py_compile app/models/exam_room.py
python -m py_compile app/services/exam_room_service.py
python -m py_compile app/api/v1/exam_rooms.py

# Format code (must pass before commit)
black . --check
```

```bash
# Frontend type checking
cd frontend
npm run type-check
npm run lint
```

### Level 2: Unit Tests

```bash
cd backend
# Run room arrangement service tests
pytest tests/test_exam_room_service.py -v

# Run API endpoint tests
pytest tests/test_exam_room_api.py -v

# Run with coverage
pytest --cov=app.services.exam_room_service tests/test_exam_room_service.py
pytest --cov=app.api.v1.exam_rooms tests/test_exam_room_api.py
```

### Level 3: Integration Tests

```bash
cd backend
# Test full workflow
pytest tests/test_complete_exam_workflow.py -v

# Test with real database
pytest --db-url=postgresql://postgres:postgres@localhost/inspireed tests/test_exam_room_integration.py
```

### Level 4: Manual Validation

**Required Manual Testing Steps:**

1. **Create Exam with Room Arrangement**:
   - [ ] Login as school admin
   - [ ] Navigate to exam management → Create exam
   - [ ] Fill in basic info (name, date, semester, classes)
   - [ ] Select subjects (enable "needs exam room" checkbox)
   - [ ] Click "Next" to room arrangement step
   - [ ] Configure room settings (capacity=30, by_class, s_shape)
   - [ ] Click "Auto Assign Rooms"
   - [ ] Verify 3 rooms created with 30 students each
   - [ ] Click "Assign Proctors"
   - [ ] Verify 2 proctors assigned per room
   - [ ] Click "View Details" for first room
   - [ ] Verify seating chart shows student names and exam numbers

2. **Export Documents**:
   - [ ] Click "Export Seating Chart" for room 1
   - [ ] Verify PDF downloads with correct filename
   - [ ] Open PDF and verify:
     - Exam name displayed
     - Room number displayed
     - Seating grid with 10 columns
     - Student names and exam numbers visible
     - Proctor names displayed
   - [ ] Export all documents (room list, tickets, handbooks)
   - [ ] Verify all files download correctly

3. **Edge Cases**:
   - [ ] Test with 0 students (should show error)
   - [ ] Test with 35 students (should create 2 rooms, one with 5)
   - [ ] Test mixed arrangement (students from different classes)
   - [ ] Test S-shape vs sequential patterns

4. **Browser Compatibility**:
   - [ ] Test in Chrome
   - [ ] Test in Firefox
   - [ ] Test PDF download in Safari

### Level 5: Additional Validation

```bash
# Check database migration
cd backend
alembic current
alembic history

# Verify model relationships
python -c "
from app.models.exam_room import ExamRoom, ExamRoomStudent, ExamProctor
from app.models.evaluation import Exam
print('Models loaded successfully')
print('Exam has exam_rooms:', hasattr(Exam, 'exam_rooms'))
"

# Frontend build validation
cd frontend
npm run build
```

---

## ACCEPTANCE CRITERIA

- [ ] All database tables created with proper relationships
- [ ] Auto-assign rooms creates correct number of rooms based on student count
- [ ] By-class arrangement groups students from same classroom
- [ ] Mixed arrangement distributes students across classrooms
- [ ] Exam numbers follow format: {year}{room_idx:02d}{seat:03d}
- [ ] Each room has exactly 2 proctors (1 primary, 1 assistant)
- [ ] Proctor assignment respects "avoid own class" rule
- [ ] Seating chart PDF shows 10-column grid with student info
- [ ] Exam ticket PDF includes student photo placeholder and exam details
- [ ] Proctor handbook PDF lists all students in room
- [ ] All unit tests pass with 80%+ coverage
- [ ] All API endpoints return correct status codes
- [ ] Frontend integrates seamlessly into existing 5-step workflow
- [ ] Export functionality downloads correct files (PDF/Excel)
- [ ] Code follows project conventions (naming, patterns)
- [ ] No regressions in existing exam functionality
- [ ] Documentation updated with new features

---

## COMPLETION CHECKLIST

- [ ] Phase 1: Database models, schemas, migration created
- [ ] Phase 2: Service layer implemented with all algorithms
- [ ] Phase 3: API endpoints created and tested
- [ ] Phase 4: Document generation service working
- [ ] Phase 5: Frontend UI integrated into workflow
- [ ] Phase 6: All tests passing (unit + integration)
- [ ] Level 1: All Python and TypeScript files compile
- [ ] Level 1: Black formatting passes
- [ ] Level 2: Unit test coverage ≥80%
- [ ] Level 3: Integration tests pass
- [ ] Level 4: Manual testing confirms features work
- [ ] Level 4: PDF documents generate correctly
- [ ] Level 5: Build succeeds, no type errors
- [ ] All acceptance criteria met

---

## NOTES

### Design Decisions

**1. Workflow Order (Subjects → Rooms)**:
- Chose this order because subject information (count, duration) affects room planning
- Certain subjects may require special rooms (labs for physics/chemistry)
- Knowing subjects helps estimate proctor requirements

**2. Exam Number Format**: `{year}{room_idx:02d}{seat:03d}`
- Example: 202401001 = 2024年, 第01考场, 第01号座位
- Simple, human-readable format
- Supports up to 99 rooms and 999 seats per room

**3. Default Room Capacity**: 30 students
- Standard classroom size in China
- Adjustable from 10-100 for flexibility
- Aligns with typical school infrastructure

**4. Two Proctors per Room**:
- Standard educational practice
- Primary + assistant roles
- Ensures adequate supervision

**5. Room Arrangement Types**:
- **By_class**: Keeps students from same classroom together
  - Pros: Familiar classmates, easier management
  - Cons: Can enable cheating
- **Mixed**: Distributes students from different classes
  - Pros: Reduces cheating opportunities
  - Cons: Students less familiar with neighbors

**6. Seat Pattern Types**:
- **S_shape**: Zigzag pattern to prevent copying
- **Sequential**: Straight row-by-row

### Technical Considerations

**ReportLab for PDF Generation**:
- Chosen because it's pure Python, no external dependencies
- Provides precise control over layout
- Supports Chinese fonts with proper configuration
- Industry standard for PDF generation

**Alternative Considered But Not Chosen**:
- WeasyPrint: More features but heavier dependency
- Browser print: Inconsistent across browsers, limited control
- External services: Requires internet, adds latency

**Future Enhancement Opportunities**:
- Visual drag-and-drop seating editor
- Conflict detection for teacher schedules
- Multiple exam sessions in one day
- Parent portal for viewing student seating
- QR codes on exam tickets for verification
- Automated seating optimization algorithms

### Known Limitations

1. **Chinese Fonts**: ReportLab requires system fonts for Chinese characters
   - Fallback: Use English for critical info if fonts missing
   - Solution: Include SimSun.ttf/SimHei.ttf in project or document font requirements

2. **Performance**: Large exams (1000+ students) may be slow
   - Optimization: Use background tasks for room assignment
   - Progress bar for long-running operations

3. **Concurrent Exam Creation**: Race conditions if multiple admins create same exam
   - Mitigation: Database unique constraints and optimistic locking

4. **PDF File Size**: Large documents (e.g., all exam tickets) may be slow
   - Solution: Stream downloads, offer individual downloads instead of bulk

5. **Room Capacity Limits**: Must match physical room constraints
   - Validation: Check Room.capacity doesn't exceed assigned students
