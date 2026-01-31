# Classroom Data Model Refactor Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Fix data inconsistency, permission validation, duplicate definitions, cascading issues, and query/sync problems in the classroom-lesson relationship system by deprecating `Classroom.head_teacher_id` in favor of `ClassroomMembership` as the single source of truth.

**Architecture:**
1. Create a centralized `ClassroomQueryService` to unify all classroom queries
2. Deprecate `Classroom.head_teacher_id` and `Classroom.deputy_head_teacher_id` fields
3. Make `ClassroomMembership` the single source of truth for teacher-classroom relationships
4. Add pre-delete checks and soft delete functionality
5. Support multiple active classroom memberships for students
6. Add validation to prevent inconsistent state

**Tech Stack:**
- Python 3.11+
- SQLAlchemy (async ORM)
- FastAPI
- Pytest (testing)
- Alembic (database migrations)

---

## Task 1: Create ClassroomQueryService (Unified Query Layer)

**Files:**
- Create: `backend/app/services/classroom_service.py`
- Create: `backend/tests/services/test_classroom_service.py`

**Step 1: Write failing tests for ClassroomQueryService**

Create `backend/tests/services/test_classroom_service.py`:

```python
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.classroom_service import ClassroomQueryService
from app.models import User, UserRole, Classroom, School

@pytest.mark.asyncio
async def test_teacher_gets_only_their_school_classrooms(db: AsyncSession, teacher_user: User, school: School):
    """Teachers should only see classrooms from their school"""
    service = ClassroomQueryService()

    # Create classroom in teacher's school
    classroom1 = Classroom(name="Class 1", school_id=school.id, grade_id=1)
    db.add(classroom1)

    # Create classroom in different school
    other_school = School(name="Other School", code="OTHER", region_id=school.region_id, school_type="小学")
    db.add(other_school)
    await db.flush()
    classroom2 = Classroom(name="Class 2", school_id=other_school.id, grade_id=1)
    db.add(classroom2)
    await db.commit()

    # Teacher should only see classroom from their school
    result = await service.get_classrooms_for_user(db, teacher_user)

    assert len(result) == 1
    assert result[0].id == classroom1.id

@pytest.mark.asyncio
async def test_is_active_filter_respected(db: AsyncSession, admin_user: User, school: School):
    """is_active filter should be applied"""
    service = ClassroomQueryService()

    active_classroom = Classroom(name="Active", school_id=school.id, grade_id=1, is_active=True)
    inactive_classroom = Classroom(name="Inactive", school_id=school.id, grade_id=1, is_active=False)
    db.add_all([active_classroom, inactive_classroom])
    await db.commit()

    # Query only active
    result = await service.get_classrooms_for_user(db, admin_user, is_active=True)

    assert len(result) == 1
    assert result[0].name == "Active"

@pytest.mark.asyncio
async def test_admin_sees_all_classrooms(db: AsyncSession, admin_user: User):
    """Admins should see all classrooms regardless of school"""
    service = ClassroomQueryService()

    # Create multiple schools with classrooms
    school1 = School(name="School 1", code="S1", region_id=1, school_type="小学")
    school2 = School(name="School 2", code="S2", region_id=1, school_type="小学")
    db.add_all([school1, school2])
    await db.flush()

    classroom1 = Classroom(name="C1", school_id=school1.id, grade_id=1)
    classroom2 = Classroom(name="C2", school_id=school2.id, grade_id=1)
    db.add_all([classroom1, classroom2])
    await db.commit()

    result = await service.get_classrooms_for_user(db, admin_user)

    assert len(result) == 2
```

**Step 2: Run tests to verify they fail**

```bash
cd /root/inspireed-platform/backend
pytest tests/services/test_classroom_service.py -v
```

Expected output:
```
FAILED - ImportError: No module named 'app.services.classroom_service'
```

**Step 3: Create ClassroomQueryService implementation**

Create `backend/app/services/classroom_service.py`:

```python
"""
Unified classroom query service - single source of truth for classroom access
"""
from typing import List, Optional
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Classroom, School, User, UserRole


class ClassroomQueryService:
    """
    Centralized service for querying classrooms.

    This is the ONLY service that should be used to query classrooms
    for both organizational management and lesson publication.
    Ensures consistent filtering logic across the entire application.
    """

    async def get_classrooms_for_user(
        self,
        db: AsyncSession,
        user: User,
        is_active: Optional[bool] = None,
        grade_id: Optional[int] = None,
        school_id: Optional[int] = None,
        region_id: Optional[int] = None,
        search: Optional[str] = None,
    ) -> List[Classroom]:
        """
        Get classrooms accessible to the user based on their role.

        Args:
            db: Database session
            user: The user making the request
            is_active: Filter by active status
            grade_id: Filter by grade
            school_id: Filter by school
            region_id: Filter by region (requires JOIN with School)
            search: Search in classroom name, code, or school name

        Returns:
            List of Classroom objects
        """
        # Build query with School JOIN (needed for region filtering and search)
        query = select(Classroom).join(School)

        # Apply role-based filtering
        role_value = user.role.value if hasattr(user.role, 'value') else user.role

        if role_value == UserRole.TEACHER.value:
            # Teachers can only see classrooms from their school
            if user.school_id is None:
                return []  # Teacher not assigned to a school
            query = query.where(Classroom.school_id == user.school_id)

        elif role_value == UserRole.DISTRICT_ADMIN.value:
            # District admins see classrooms from their region
            if user.region_id is not None:
                query = query.where(School.region_id == user.region_id)
            # If no region_id set, return empty (or could return all)

        elif role_value == UserRole.SCHOOL_ADMIN.value:
            # School admins see classrooms from their school only
            if user.school_id is not None:
                query = query.where(School.id == user.school_id)
            else:
                return []  # School admin not assigned to a school

        # ADMIN role: no filtering (can see all classrooms)

        # Apply additional filters
        if is_active is not None:
            query = query.where(Classroom.is_active == is_active)

        if grade_id is not None:
            query = query.where(Classroom.grade_id == grade_id)

        if school_id is not None:
            query = query.where(Classroom.school_id == school_id)

        if region_id is not None:
            query = query.where(School.region_id == region_id)

        if search:
            # Search in classroom name, code, description, and school name
            from sqlalchemy import or_
            search_filter = or_(
                Classroom.name.ilike(f"%{search}%"),
                Classroom.code.ilike(f"%{search}%"),
                Classroom.description.ilike(f"%{search}%"),
                School.name.ilike(f"%{search}%"),
            )
            query = query.where(search_filter)

        # Execute query
        result = await db.execute(query.order_by(Classroom.grade_id, Classroom.name))
        return list(result.scalars().all())

    async def get_classroom_by_id(
        self,
        db: AsyncSession,
        classroom_id: int,
        user: User,
    ) -> Optional[Classroom]:
        """
        Get a specific classroom if the user has access to it.

        Args:
            db: Database session
            classroom_id: ID of classroom to fetch
            user: User making the request

        Returns:
            Classroom object or None if not found or no access
        """
        classrooms = await self.get_classrooms_for_user(db, user)
        for classroom in classrooms:
            if classroom.id == classroom_id:
                return classroom
        return None
```

**Step 4: Run tests to verify they pass**

```bash
cd /root/inspireed-platform/backend
pytest tests/services/test_classroom_service.py -v
```

Expected output:
```
PASSED test_teacher_gets_only_their_school_classrooms
PASSED test_is_active_filter_respected
PASSED test_admin_sees_all_classrooms
```

**Step 5: Commit**

```bash
cd /root/inspireed-platform
git add backend/app/services/classroom_service.py backend/tests/services/test_classroom_service.py
git commit -m "feat: create ClassroomQueryService for unified classroom queries

- Add centralized service layer for all classroom queries
- Implement role-based filtering (teacher, admin, district admin, school admin)
- Support filtering by is_active, grade, school, region, and search
- Add comprehensive test coverage"
```

---

## Task 2: Refactor get_available_classrooms to Use ClassroomQueryService

**Files:**
- Modify: `backend/app/api/v1/lessons.py:625-654`
- Modify: `backend/tests/api/v1/test_lessons.py` (create if not exists)

**Step 1: Write failing test for is_active check**

Create or modify `backend/tests/api/v1/test_lessons.py`:

```python
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import User, Classroom, Lesson, LessonStatus, LessonClassroom
from fastapi import testclient

@pytest.mark.asyncio
async def test_publish_lesson_rejects_inactive_classroom(
    db: AsyncSession,
    auth_client: testclient.TestClient,
    teacher_user: User,
    lesson: Lesson,
    inactive_classroom: Classroom,
):
    """Publishing to an inactive classroom should fail"""
    response = auth_client.post(
        f"/api/v1/lessons/{lesson.id}/publish",
        json={"classroom_ids": [inactive_classroom.id]}
    )

    assert response.status_code == 404
    assert "classroom" in response.json()["detail"].lower()
```

**Step 2: Run test to verify it fails**

```bash
cd /root/inspireed-platform/backend
pytest tests/api/v1/test_lessons.py::test_publish_lesson_rejects_inactive_classroom -v
```

Expected: FAIL (current implementation doesn't check is_active)

**Step 3: Refactor get_available_classrooms endpoint**

Modify `backend/app/api/v1/lessons.py`:

```python
# At the top of the file, add import
from app.services.classroom_service import ClassroomQueryService

@router.get("/available-classrooms", response_model=List[LessonClassroomInfo])
async def get_available_classrooms(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """获取教师可选的班级列表"""
    from app.models import UserRole

    # Validate user role
    role_value = cast(str, getattr(current_user.role, "value", current_user.role))
    try:
        user_role = UserRole(role_value)
    except ValueError:
        raise HTTPException(status_code=403, detail="当前用户角色无效")

    # Only teachers, admins, and researchers can publish lessons
    if user_role not in {UserRole.TEACHER, UserRole.ADMIN, UserRole.RESEARCHER}:
        raise HTTPException(status_code=403, detail="仅教师或管理员可查看班级列表")

    # Use unified service to get active classrooms only
    service = ClassroomQueryService()
    classrooms = await service.get_classrooms_for_user(
        db, current_user, is_active=True
    )

    return [
        LessonClassroomInfo.model_validate(classroom) for classroom in classrooms
    ]
```

**Step 4: Add is_active check to publish_lesson**

Modify `backend/app/api/v1/lessons.py` (around line 1140):

```python
@router.post("/{lesson_id}/publish", response_model=LessonResponse)
async def publish_lesson(
    lesson_id: int,
    request: Request,
    publish_in: LessonPublishRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """发布教案"""
    lesson = await _get_lesson_with_relations(db, lesson_id)

    if not lesson:
        raise HTTPException(status_code=404, detail="教案不存在")

    if cast(Optional[int], lesson.creator_id) != current_user.id:
        raise HTTPException(status_code=403, detail="无权发布该教案")

    classroom_ids = set(publish_in.classroom_ids)
    if not classroom_ids:
        raise HTTPException(status_code=400, detail="发布教案时必须指定至少一个班级")

    # Use ClassroomQueryService to validate classrooms (checks is_active)
    service = ClassroomQueryService()
    classrooms_result = await db.execute(
        select(Classroom).where(
            Classroom.id.in_(classroom_ids),
            Classroom.is_active == True  # ✅ Explicitly check is_active
        )
    )
    classrooms = classrooms_result.scalars().all()
    existing_classroom_ids = {cast(int, classroom.id) for classroom in classrooms}
    missing_ids = classroom_ids - existing_classroom_ids

    if missing_ids:
        missing_str = ", ".join(str(cid) for cid in sorted(missing_ids))
        raise HTTPException(status_code=404, detail=f"班级不存在或未激活: {missing_str}")

    # ... rest of the function remains the same
```

**Step 5: Run tests to verify they pass**

```bash
cd /root/inspireed-platform/backend
pytest tests/api/v1/test_lessons.py::test_publish_lesson_rejects_inactive_classroom -v
```

Expected: PASS

**Step 6: Commit**

```bash
cd /root/inspireed-platform
git add backend/app/api/v1/lessons.py backend/tests/api/v1/test_lessons.py
git commit -m "refactor: use ClassroomQueryService for available-classrooms

- Refactor get_available_classrooms to use ClassroomQueryService
- Add is_active check to publish_lesson endpoint
- Add test for rejecting inactive classrooms during publish"
```

---

## Task 3: Add Pre-Delete Checks to prevent cascade issues

**Files:**
- Modify: `backend/app/api/v1/admin_organization.py:1381-1403`
- Create: `backend/tests/api/v1/test_admin_organization.py` (add tests)

**Step 1: Write failing test for lesson assignment check**

Add to `backend/tests/api/v1/test_admin_organization.py`:

```python
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Classroom, Lesson, LessonClassroom, LessonStatus, User
from fastapi import testclient

@pytest.mark.asyncio
async def test_delete_classroom_with_lesson_assignments_fails(
    db: AsyncSession,
    admin_client: testclient.TestClient,
    classroom: Classroom,
    lesson: Lesson,
):
    """Deleting a classroom with lesson assignments should fail"""
    # Assign lesson to classroom
    lc = LessonClassroom(lesson_id=lesson.id, classroom_id=classroom.id)
    db.add(lc)
    await db.commit()

    # Try to delete classroom
    response = admin_client.delete(f"/api/v1/admin/classrooms/{classroom.id}")

    assert response.status_code == 400
    assert "lesson" in response.json()["detail"].lower()

@pytest.mark.asyncio
async def test_deactivate_classroom_preserves_lesson_assignments(
    db: AsyncSession,
    admin_client: testclient.TestClient,
    classroom: Classroom,
    lesson: Lesson,
):
    """Deactivating a classroom should preserve lesson assignments"""
    # Assign lesson to classroom
    lc = LessonClassroom(lesson_id=lesson.id, classroom_id=classroom.id)
    db.add(lc)
    await db.commit()

    # Deactivate classroom
    response = admin_client.post(f"/api/v1/admin/classrooms/{classroom.id}/deactivate")

    assert response.status_code == 200

    # Verify lesson assignment still exists
    result = await db.execute(
        select(LessonClassroom).where(
            LessonClassroom.lesson_id == lesson.id,
            LessonClassroom.classroom_id == classroom.id
        )
    )
    assert result.scalar_one_or_none() is not None
```

**Step 2: Run tests to verify they fail**

```bash
cd /root/inspireed-platform/backend
pytest tests/api/v1/test_admin_organization.py::test_delete_classroom_with_lesson_assignments_fails -v
```

Expected: FAIL (current implementation doesn't check lesson assignments)

**Step 3: Update delete_classroom to check lesson assignments**

Modify `backend/app/api/v1/admin_organization.py`:

```python
@router.delete("/classrooms/{classroom_id}")
async def delete_classroom(
    classroom_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Any:
    """删除班级"""
    from app.models import LessonClassroom

    classroom = await db.scalar(select(Classroom).where(Classroom.id == classroom_id))
    if not classroom:
        raise HTTPException(status_code=404, detail="班级不存在")

    # ✅ NEW: Check lesson assignments BEFORE allowing delete
    lesson_assignment_count = await db.execute(
        select(func.count()).select_from(LessonClassroom).where(
            LessonClassroom.classroom_id == classroom_id
        )
    )
    lesson_count = lesson_assignment_count.scalar() or 0

    if lesson_count > 0:
        raise HTTPException(
            status_code=400,
            detail=f"无法删除班级：该班级有 {lesson_count} 个教案关联。请先取消发布相关教案，或使用停用接口。"
        )

    # Existing student check
    student_count_result = await db.execute(
        select(func.count()).select_from(User).where(User.classroom_id == classroom_id)
    )
    student_count = student_count_result.scalar() or 0

    if student_count > 0:
        raise HTTPException(status_code=400, detail="班级下仍有关联学生，无法删除")

    await db.delete(classroom)
    await db.commit()

    return {"message": "班级删除成功"}


@router.post("/classrooms/{classroom_id}/deactivate", status_code=200)
async def deactivate_classroom(
    classroom_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Any:
    """安全停用班级（保留教案关联历史）

    相比硬删除，停用班级：
    - 保留教案分配历史
    - 保留学生考勤和行为记录
    - 防止数据丢失
    """
    classroom = await db.scalar(select(Classroom).where(Classroom.id == classroom_id))
    if not classroom:
        raise HTTPException(status_code=404, detail="班级不存在")

    classroom.is_active = False
    await db.commit()

    return {
        "message": "班级已停用",
        "classroom_id": classroom_id,
        "lesson_assignments_preserved": True
    }
```

**Step 4: Run tests to verify they pass**

```bash
cd /root/inspireed-platform/backend
pytest tests/api/v1/test_admin_organization.py::test_delete_classroom_with_lesson_assignments_fails -v
pytest tests/api/v1/test_admin_organization.py::test_deactivate_classroom_preserves_lesson_assignments -v
```

Expected: PASS for both

**Step 5: Commit**

```bash
cd /root/inspireed-platform
git add backend/app/api/v1/admin_organization.py backend/tests/api/v1/test_admin_organization.py
git commit -m "feat: add lesson assignment check to classroom deletion

- Block classroom deletion if lesson assignments exist
- Add new /deactivate endpoint for safe soft delete
- Preserve lesson history when deactivating classrooms
- Add tests for deletion safety and deactivation"
```

---

## Task 4: Deprecate head_teacher_id fields

**Files:**
- Modify: `backend/app/models/organization.py:96-101`
- Create: `backend/alembic/versions/xxxx_deprecate_head_teacher_id.py`
- Create: `backend/tests/models/test_organization.py`

**Step 1: Write test for ClassroomMembership-based head teacher**

Create `backend/tests/models/test_organization.py`:

```python
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Classroom, ClassroomMembership, RoleInClass, User

@pytest.mark.asyncio
async def test_classroom_head_teacher_from_membership(
    db: AsyncSession,
    classroom: Classroom,
    teacher_user: User,
):
    """Classroom.head_teacher property should use ClassroomMembership"""
    # Add head teacher via ClassroomMembership
    membership = ClassroomMembership(
        classroom_id=classroom.id,
        user_id=teacher_user.id,
        role_in_class=RoleInClass.HEAD_TEACHER_PRIMARY,
        is_active=True
    )
    db.add(membership)
    await db.commit()

    # The property should find the head teacher
    head_teacher = await classroom.get_head_teacher(db)
    assert head_teacher is not None
    assert head_teacher.id == teacher_user.id

@pytest.mark.asyncio
async def test_classroom_deputy_head_teacher_from_membership(
    db: AsyncSession,
    classroom: Classroom,
    teacher_user: User,
):
    """Classroom.deputy_head_teacher property should use ClassroomMembership"""
    membership = ClassroomMembership(
        classroom_id=classroom.id,
        user_id=teacher_user.id,
        role_in_class=RoleInClass.HEAD_TEACHER_DEPUTY,
        is_active=True
    )
    db.add(membership)
    await db.commit()

    deputy = await classroom.get_deputy_head_teacher(db)
    assert deputy is not None
    assert deputy.id == teacher_user.id
```

**Step 2: Run tests to verify they fail**

```bash
cd /root/inspireed-platform/backend
pytest tests/models/test_organization.py -v
```

Expected: FAIL (get_head_teacher method doesn't exist)

**Step 3: Add helper methods to Classroom model**

Modify `backend/app/models/organization.py`:

```python
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.classroom_assistant import ClassroomMembership, RoleInClass

class Classroom(Base):
    """班级模型"""

    __tablename__ = "classrooms"

    # ... existing fields ...

    # ✅ DEPRECATED: These fields are kept for backward compatibility
    # but should not be used for new code. Use ClassroomMembership instead.
    head_teacher_id = Column(
        Integer, ForeignKey("users.id"), nullable=True, comment="正班主任ID (已弃用，请使用ClassroomMembership)"
    )
    deputy_head_teacher_id = Column(
        Integer, ForeignKey("users.id"), nullable=True, comment="副班主任ID (已弃用，请使用ClassroomMembership)"
    )

    # ... rest of the model ...

    async def get_head_teacher(self, db: AsyncSession) -> Optional["User"]:
        """
        Get head teacher from ClassroomMembership (single source of truth).

        This method queries ClassroomMembership instead of using head_teacher_id.
        The head_teacher_id field is deprecated.

        Args:
            db: Database session

        Returns:
            User object if head teacher exists, None otherwise
        """
        from sqlalchemy import select

        result = await db.execute(
            select(User).join(ClassroomMembership).where(
                ClassroomMembership.classroom_id == self.id,
                ClassroomMembership.role_in_class == RoleInClass.HEAD_TEACHER_PRIMARY,
                ClassroomMembership.is_active == True
            )
        )
        return result.scalar_one_or_none()

    async def get_deputy_head_teacher(self, db: AsyncSession) -> Optional["User"]:
        """
        Get deputy head teacher from ClassroomMembership (single source of truth).

        Args:
            db: Database session

        Returns:
            User object if deputy exists, None otherwise
        """
        from sqlalchemy import select

        result = await db.execute(
            select(User).join(ClassroomMembership).where(
                ClassroomMembership.classroom_id == self.id,
                ClassroomMembership.role_in_class == RoleInClass.HEAD_TEACHER_DEPUTY,
                ClassroomMembership.is_active == True
            )
        )
        return result.scalar_one_or_none()

    async def get_teachers(self, db: AsyncSession) -> List["User"]:
        """
        Get all teachers associated with this classroom via ClassroomMembership.

        Args:
            db: Database session

        Returns:
            List of User objects with teacher roles
        """
        from sqlalchemy import select

        result = await db.execute(
            select(User).join(ClassroomMembership).where(
                ClassroomMembership.classroom_id == self.id,
                ClassroomMembership.role_in_class.in_([
                    RoleInClass.HEAD_TEACHER_PRIMARY,
                    RoleInClass.HEAD_TEACHER_DEPUTY,
                    RoleInClass.SUBJECT_TEACHER,
                ]),
                ClassroomMembership.is_active == True
            )
        )
        return list(result.scalars().all())
```

**Step 4: Run tests to verify they pass**

```bash
cd /root/inspireed-platform/backend
pytest tests/models/test_organization.py -v
```

Expected: PASS

**Step 5: Create migration to deprecate fields**

Create `backend/alembic/versions/xxxx_deprecate_head_teacher_id.py`:

```python
"""deprecate head_teacher_id and deputy_head_teacher_id fields

Revision ID: xxxx
Revises: previous_migration_id
Create Date: 2025-01-31

This migration:
1. Adds comment to mark head_teacher_id as deprecated
2. Creates migration script to sync existing data to ClassroomMembership
3. Does NOT remove the fields (for backward compatibility)

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
import sqlalchemy as sql

# revision identifiers, used by Alembic.
revision = 'xxxx_deprecate_head_teacher'
down_revision = 'previous_migration_id'  # Update this
branch_labels = None
depends_on = None


def upgrade():
    """Migrate head_teacher_id to ClassroomMembership"""

    # Get database connection
    conn = op.get_bind()

    # Step 1: Migrate existing head_teacher_id to ClassroomMembership
    # We need to do this in raw SQL since we're using the migration

    # First, migrate head_teacher_id
    conn.execute(sa.text("""
        INSERT INTO classroom_memberships (classroom_id, user_id, role_in_class, is_active, is_primary_class, created_at, updated_at)
        SELECT id, head_teacher_id, 'head_teacher_primary', true, false, NOW(), NOW()
        FROM classrooms
        WHERE head_teacher_id IS NOT NULL
        AND NOT EXISTS (
            SELECT 1 FROM classroom_memberships
            WHERE classroom_id = classrooms.id
            AND user_id = classrooms.head_teacher_id
            AND role_in_class = 'head_teacher_primary'
        )
    """))

    # Then, migrate deputy_head_teacher_id
    conn.execute(sa.text("""
        INSERT INTO classroom_memberships (classroom_id, user_id, role_in_class, is_active, is_primary_class, created_at, updated_at)
        SELECT id, deputy_head_teacher_id, 'head_teacher_deputy', true, false, NOW(), NOW()
        FROM classrooms
        WHERE deputy_head_teacher_id IS NOT NULL
        AND NOT EXISTS (
            SELECT 1 FROM classroom_memberships
            WHERE classroom_id = classrooms.id
            AND user_id = classrooms.deputy_head_teacher_id
            AND role_in_class = 'head_teacher_deputy'
        )
    """))

    # Step 2: Add comment to mark fields as deprecated
    # PostgreSQL supports COMMENT ON COLUMN
    conn.execute(sa.text("""
        COMMENT ON COLUMN classrooms.head_teacher_id IS 'DEPRECATED: Use ClassroomMembership with role=head_teacher_primary instead. Kept for backward compatibility.'
    """))

    conn.execute(sa.text("""
        COMMENT ON COLUMN classrooms.deputy_head_teacher_id IS 'DEPRECATED: Use ClassroomMembership with role=head_teacher_deputy instead. Kept for backward compatibility.'
    """))


def downgrade():
    """Reverse migration: Remove ClassroomMembership entries created from head_teacher_id"""

    conn = op.get_bind()

    # Note: We can't reliably reverse this without potentially data loss
    # So we'll leave the ClassroomMembership entries in place
    # In production, you might want a different strategy

    # Remove comments
    conn.execute(sa.text("""
        COMMENT ON COLUMN classrooms.head_teacher_id IS '正班主任ID'
    """))

    conn.execute(sa.text("""
        COMMENT ON COLUMN classrooms.deputy_head_teacher_id IS '副班主任ID'
    """))
```

**Step 6: Run migration**

```bash
cd /root/inspireed-platform/backend
alembic upgrade head
```

**Step 7: Commit**

```bash
cd /root/inspireed-platform
git add backend/app/models/organization.py backend/alembic/versions/xxxx_deprecate_head_teacher_id.py backend/tests/models/test_organization.py
git commit -m "refactor: deprecate head_teacher_id in favor of ClassroomMembership

- Add get_head_teacher(), get_deputy_head_teacher(), get_teachers() methods to Classroom
- Make ClassroomMembership the single source of truth for teacher-classroom relationships
- Add migration to sync existing head_teacher_id data to ClassroomMembership
- Add deprecation comments to head_teacher_id and deputy_head_teacher_id fields
- Add tests for new helper methods"
```

---

## Task 5: Update Permission Check to Use ClassroomMembership

**Files:**
- Create: `backend/app/services/permission_service.py`
- Modify: `backend/app/api/v1/lessons.py:1156-1169`
- Create: `backend/tests/services/test_permission_service.py`

**Step 1: Write failing test for permission check via ClassroomMembership**

Create `backend/tests/services/test_permission_service.py`:

```python
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.permission_service import PermissionService
from app.models import User, Classroom, ClassroomMembership, RoleInClass, UserRole

@pytest.mark.asyncio
async def test_subject_teacher_can_publish_to_classroom(
    db: AsyncSession,
    classroom: Classroom,
    teacher_user: User,
):
    """Subject teachers should be able to publish to their classrooms"""
    # Add teacher as SUBJECT_TEACHER via ClassroomMembership
    membership = ClassroomMembership(
        classroom_id=classroom.id,
        user_id=teacher_user.id,
        role_in_class=RoleInClass.SUBJECT_TEACHER,
        is_active=True
    )
    db.add(membership)
    await db.commit()

    service = PermissionService()
    result = await service.can_teacher_publish_to_classroom(db, teacher_user, classroom)

    assert result is True

@pytest.mark.asyncio
async def test_unrelated_teacher_cannot_publish(
    db: AsyncSession,
    classroom: Classroom,
    teacher_user: User,
):
    """Teachers without ClassroomMembership or school relationship cannot publish"""
    # Teacher is in different school, no ClassroomMembership
    teacher_user.school_id = 999  # Different school
    await db.commit()

    service = PermissionService()
    result = await service.can_teacher_publish_to_classroom(db, teacher_user, classroom)

    assert result is False

@pytest.mark.asyncio
async def test_head_teacher_can_publish_via_membership(
    db: AsyncSession,
    classroom: Classroom,
    teacher_user: User,
):
    """Head teachers via ClassroomMembership can publish (even if different school)"""
    # Different school
    teacher_user.school_id = 999

    # But has ClassroomMembership
    membership = ClassroomMembership(
        classroom_id=classroom.id,
        user_id=teacher_user.id,
        role_in_class=RoleInClass.HEAD_TEACHER_PRIMARY,
        is_active=True
    )
    db.add(membership)
    await db.commit()

    service = PermissionService()
    result = await service.can_teacher_publish_to_classroom(db, teacher_user, classroom)

    assert result is True
```

**Step 2: Run tests to verify they fail**

```bash
cd /root/inspireed-platform/backend
pytest tests/services/test_permission_service.py -v
```

Expected: FAIL (PermissionService doesn't exist)

**Step 3: Create PermissionService**

Create `backend/app/services/permission_service.py`:

```python
"""
Permission checking service for classroom and lesson access
"""
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Classroom, ClassroomMembership, RoleInClass, UserRole


class PermissionService:
    """Centralized permission checking for classroom-related operations"""

    async def can_teacher_publish_to_classroom(
        self,
        db: AsyncSession,
        teacher: "User",
        classroom: Classroom,
    ) -> bool:
        """
        Check if a teacher can publish lessons to a classroom.

        Permission rules (in order of priority):
        1. Teacher has active ClassroomMembership with teacher role (HEAD_TEACHER_PRIMARY, HEAD_TEACHER_DEPUTY, SUBJECT_TEACHER)
        2. Teacher's school_id matches classroom's school_id

        Args:
            db: Database session
            teacher: The user attempting to publish
            classroom: The target classroom

        Returns:
            True if teacher can publish, False otherwise
        """
        # Rule 1: Check ClassroomMembership first (single source of truth)
        membership = await db.execute(
            select(ClassroomMembership).where(
                ClassroomMembership.classroom_id == classroom.id,
                ClassroomMembership.user_id == teacher.id,
                ClassroomMembership.role_in_class.in_([
                    RoleInClass.HEAD_TEACHER_PRIMARY,
                    RoleInClass.HEAD_TEACHER_DEPUTY,
                    RoleInClass.SUBJECT_TEACHER,
                ]),
                ClassroomMembership.is_active == True
            )
        )
        if membership.scalar_one_or_none():
            return True

        # Rule 2: Check school_id (fallback for teachers without explicit membership)
        if teacher.school_id is not None and teacher.school_id == classroom.school_id:
            return True

        return False

    async def can_student_view_lesson(
        self,
        db: AsyncSession,
        student: "User",
        lesson_id: int,
    ) -> bool:
        """
        Check if a student can view a lesson.

        Student can view if:
        - Lesson is published
        - Student has active ClassroomMembership with role=STUDENT for any classroom assigned to the lesson

        Args:
            db: Database session
            student: The student user
            lesson_id: The lesson ID to check

        Returns:
            True if student can view, False otherwise
        """
        from app.models import LessonClassroom, LessonStatus

        # Get all student's active classroom memberships
        memberships = await db.execute(
            select(ClassroomMembership).where(
                ClassroomMembership.user_id == student.id,
                ClassroomMembership.role_in_class == RoleInClass.STUDENT,
                ClassroomMembership.is_active == True
            )
        )
        classroom_ids = [m.classroom_id for m in memberships.scalars()]

        if not classroom_ids:
            return False

        # Check if lesson is published and assigned to any of these classrooms
        assignment = await db.execute(
            select(LessonClassroom).join(Lesson).where(
                LessonClassroom.lesson_id == lesson_id,
                LessonClassroom.classroom_id.in_(classroom_ids),
                Lesson.status == LessonStatus.PUBLISHED
            )
        )

        return assignment.scalar_one_or_none() is not None
```

**Step 4: Update publish_lesson to use PermissionService**

Modify `backend/app/api/v1/lessons.py`:

```python
# At the top of the file, add import
from app.services.permission_service import PermissionService

@router.post("/{lesson_id}/publish", response_model=LessonResponse)
async def publish_lesson(
    lesson_id: int,
    request: Request,
    publish_in: LessonPublishRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """发布教案"""
    from app.services.classroom_service import ClassroomQueryService
    from app.services.permission_service import PermissionService

    lesson = await _get_lesson_with_relations(db, lesson_id)

    if not lesson:
        raise HTTPException(status_code=404, detail="教案不存在")

    if cast(Optional[int], lesson.creator_id) != current_user.id:
        raise HTTPException(status_code=403, detail="无权发布该教案")

    classroom_ids = set(publish_in.classroom_ids)
    if not classroom_ids:
        raise HTTPException(status_code=400, detail="发布教案时必须指定至少一个班级")

    # Use ClassroomQueryService to validate active classrooms
    classroom_service = ClassroomQueryService()
    classrooms_result = await db.execute(
        select(Classroom).where(
            Classroom.id.in_(classroom_ids),
            Classroom.is_active == True
        )
    )
    classrooms = classrooms_result.scalars().all()
    existing_classroom_ids = {cast(int, classroom.id) for classroom in classrooms}
    missing_ids = classroom_ids - existing_classroom_ids

    if missing_ids:
        missing_str = ", ".join(str(cid) for cid in sorted(missing_ids))
        raise HTTPException(status_code=404, detail=f"班级不存在或未激活: {missing_str}")

    role_value = cast(str, getattr(current_user.role, "value", current_user.role))
    try:
        user_role = UserRole(role_value)
    except ValueError:
        raise HTTPException(status_code=403, detail="当前用户角色无效")

    # ✅ Use PermissionService for permission checking
    permission_service = PermissionService()

    if user_role == UserRole.TEACHER:
        if current_user.school_id is None:
            raise HTTPException(status_code=400, detail="教师缺少所属学校信息，无法分配班级")

        for classroom in classrooms:
            can_publish = await permission_service.can_teacher_publish_to_classroom(
                db, current_user, classroom
            )
            if not can_publish:
                raise HTTPException(
                    status_code=403,
                    detail=f"无权将教案发布到班级 {classroom.name}",
                )

    # ... rest of the function remains the same (existing_relations handling, etc.)
```

**Step 5: Run tests to verify they pass**

```bash
cd /root/inspireed-platform/backend
pytest tests/services/test_permission_service.py -v
```

Expected: PASS

**Step 6: Commit**

```bash
cd /root/inspireed-platform
git add backend/app/services/permission_service.py backend/app/api/v1/lessons.py backend/tests/services/test_permission_service.py
git commit -m "feat: use ClassroomMembership for lesson publish permissions

- Create PermissionService for centralized permission checking
- Update publish_lesson to check ClassroomMembership for teacher roles
- Support subject teachers publishing to their assigned classrooms
- Support cross-school publishing via explicit ClassroomMembership
- Add comprehensive tests for permission scenarios"
```

---

## Task 6: Support Multiple Active Classrooms for Students

**Files:**
- Modify: `backend/app/api/v1/lessons.py:348-362`
- Modify: `backend/tests/api/v1/test_lessons.py`

**Step 1: Write failing test for multi-classroom students**

Add to `backend/tests/api/v1/test_lessons.py`:

```python
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import User, Classroom, Lesson, LessonStatus, LessonClassroom, ClassroomMembership, RoleInClass

@pytest.mark.asyncio
async def test_student_sees_lessons_from_multiple_classrooms(
    db: AsyncSession,
    auth_client: testclient.TestClient,
    student_user: User,
    classroom1: Classroom,
    classroom2: Classroom,
):
    """Students should see lessons from all classrooms they're members of"""
    # Add student to both classrooms via ClassroomMembership
    membership1 = ClassroomMembership(
        classroom_id=classroom1.id,
        user_id=student_user.id,
        role_in_class=RoleInClass.STUDENT,
        is_active=True
    )
    membership2 = ClassroomMembership(
        classroom_id=classroom2.id,
        user_id=student_user.id,
        role_in_class=RoleInClass.STUDENT,
        is_active=True
    )
    db.add_all([membership1, membership2])
    await db.commit()

    # Create lessons for each classroom
    lesson1 = Lesson(
        title="Lesson 1",
        creator_id=1,  # Some teacher
        course_id=1,
        status=LessonStatus.PUBLISHED,
        content=[]
    )
    lesson2 = Lesson(
        title="Lesson 2",
        creator_id=1,
        course_id=1,
        status=LessonStatus.PUBLISHED,
        content=[]
    )
    db.add_all([lesson1, lesson2])
    await db.flush()

    lc1 = LessonClassroom(lesson_id=lesson1.id, classroom_id=classroom1.id)
    lc2 = LessonClassroom(lesson_id=lesson2.id, classroom_id=classroom2.id)
    db.add_all([lc1, lc2])
    await db.commit()

    # Student should see both lessons
    response = auth_client.get("/api/v1/lessons/")

    assert response.status_code == 200
    data = response.json()
    lesson_ids = [item["id"] for item in data["items"]]

    assert lesson1.id in lesson_ids
    assert lesson2.id in lesson_ids
```

**Step 2: Run test to verify it fails**

```bash
cd /root/inspireed-platform/backend
pytest tests/api/v1/test_lessons.py::test_student_sees_lessons_from_multiple_classrooms -v
```

Expected: FAIL (current implementation only checks User.classroom_id)

**Step 3: Update list_lessons to support multiple classrooms**

Modify `backend/app/api/v1/lessons.py`:

```python
@router.get("/", response_model=LessonListResponse)
async def list_lessons(
    request: Request,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None, description="状态筛选: draft, published, archived"),
    search: Optional[str] = None,
    course_id: Optional[int] = Query(None, description="按课程ID筛选"),
    chapter_id: Optional[int] = Query(None, description="按章节ID筛选"),
    subject_id: Optional[int] = Query(None, description="按学科ID筛选"),
    grade_id: Optional[int] = Query(None, description="按年级ID筛选"),
    creator_only: bool = Query(False, description="是否只返回当前用户创建的教案"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """获取教案列表"""
    from app.models.classroom_assistant import ClassroomMembership, RoleInClass

    try:
        status_enum = LessonStatus(status.lower()) if status else None
    except ValueError:
        raise HTTPException(status_code=400, detail=f"无效的状态值: {status}")

    role_value = cast(str, getattr(current_user.role, "value", current_user.role))
    try:
        user_role = UserRole(role_value)
    except ValueError:
        raise HTTPException(status_code=403, detail="当前用户角色无效")

    base_query = select(Lesson).options(
        selectinload(Lesson.course).selectinload(Course.subject),
        selectinload(Lesson.course).selectinload(Course.grade),
        selectinload(Lesson.creator),
        selectinload(Lesson.lesson_classrooms).selectinload(
            LessonClassroom.classroom
        ),
    )

    if user_role == UserRole.STUDENT:
        # ✅ UPDATED: Get ALL active classroom memberships, not just User.classroom_id
        memberships_result = await db.execute(
            select(ClassroomMembership).where(
                ClassroomMembership.user_id == current_user.id,
                ClassroomMembership.role_in_class == RoleInClass.STUDENT,
                ClassroomMembership.is_active == True
            )
        )
        classroom_ids = [m.classroom_id for m in memberships_result.scalars()]

        if not classroom_ids:
            return LessonListResponse(
                items=[],
                total=0,
                page=page,
                page_size=page_size,
            )

        base_query = (
            base_query.join(LessonClassroom)
            .where(Lesson.status == LessonStatus.PUBLISHED)
            .where(LessonClassroom.classroom_id.in_(classroom_ids))
            .distinct(Lesson.id)
        )
    # ... rest of the function remains the same
```

**Step 4: Run test to verify it passes**

```bash
cd /root/inspireed-platform/backend
pytest tests/api/v1/test_lessons.py::test_student_sees_lessons_from_multiple_classrooms -v
```

Expected: PASS

**Step 5: Commit**

```bash
cd /root/inspireed-platform
git add backend/app/api/v1/lessons.py backend/tests/api/v1/test_lessons.py
git commit -m "feat: support multiple active classrooms for students

- Update list_lessons to use ClassroomMembership instead of User.classroom_id
- Students can now be members of multiple classrooms simultaneously
- Lessons from all active classroom memberships are visible to students
- Add test for multi-classroom lesson visibility"
```

---

## Task 7: Add Validation to Prevent Duplicate Head Teachers

**Files:**
- Modify: `backend/app/models/classroom_assistant.py`
- Create: `backend/tests/models/test_classroom_assistant.py`

**Step 1: Write failing test for duplicate head teacher prevention**

Create `backend/tests/models/test_classroom_assistant.py`:

```python
import pytest
from sqlalchemy import exc
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Classroom, ClassroomMembership, RoleInClass, User

@pytest.mark.asyncio
async def test_cannot_have_duplicate_head_teachers(
    db: AsyncSession,
    classroom: Classroom,
    teacher_user: User,
    another_teacher_user: User,
):
    """Only one HEAD_TEACHER_PRIMARY can exist per classroom"""
    # Add first head teacher
    membership1 = ClassroomMembership(
        classroom_id=classroom.id,
        user_id=teacher_user.id,
        role_in_class=RoleInClass.HEAD_TEACHER_PRIMARY,
        is_active=True
    )
    db.add(membership1)
    await db.commit()

    # Try to add second head teacher
    membership2 = ClassroomMembership(
        classroom_id=classroom.id,
        user_id=another_teacher_user.id,
        role_in_class=RoleInClass.HEAD_TEACHER_PRIMARY,
        is_active=True
    )
    db.add(membership2)

    with pytest.raises(exc.IntegrityError):
        await db.commit()
```

**Step 2: Run test to verify it fails**

```bash
cd /root/inspireed-platform/backend
pytest tests/models/test_classroom_assistant.py::test_cannot_have_duplicate_head_teachers -v
```

Expected: FAIL (no constraint exists yet)

**Step 3: Add unique index to ClassroomMembership**

Modify `backend/app/models/classroom_assistant.py`:

```python
class ClassroomMembership(Base):
    """班级成员关系"""

    __tablename__ = "classroom_memberships"

    # ... existing fields ...

    __table_args__ = (
        UniqueConstraint("classroom_id", "user_id", name="uq_classroom_user"),
        Index("idx_membership_user_active", "user_id", "is_active"),
        Index("idx_membership_classroom_role", "classroom_id", "role_in_class"),

        # ✅ NEW: Ensure only one HEAD_TEACHER_PRIMARY per classroom
        Index(
            "uq_classroom_head_teacher",
            "classroom_id",
            unique=True,
            postgresql_where=text("role_in_class = 'head_teacher_primary' AND is_active = TRUE")
        ),
    )
```

**Step 4: Create migration for new constraint**

Create `backend/alembic/versions/xxxx_add_unique_head_teacher_constraint.py`:

```python
"""add unique constraint for head teachers

Revision ID: xxxx
Revises: previous_migration_id
Create Date: 2025-01-31
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'xxxx_unique_head_teacher'
down_revision = 'previous_migration_id'
branch_labels = None
depends_on = None


def upgrade():
    """Add unique partial index for head teachers"""

    # First, clean up any existing duplicates (keep the first one)
    op.execute("""
        DELETE FROM classroom_memberships
        WHERE id IN (
            SELECT id FROM (
                SELECT id, ROW_NUMBER() OVER (
                    PARTITION BY classroom_id
                    ORDER BY created_at ASC
                ) as row_num
                FROM classroom_memberships
                WHERE role_in_class = 'head_teacher_primary'
                AND is_active = TRUE
            ) sub
            WHERE row_num > 1
        )
    """)

    # Add the unique partial index
    # PostgreSQL syntax for partial unique index
    op.execute("""
        CREATE UNIQUE INDEX uq_classroom_head_teacher
        ON classroom_memberships (classroom_id)
        WHERE role_in_class = 'head_teacher_primary' AND is_active = TRUE
    """)


def downgrade():
    """Remove the unique index"""
    op.execute("DROP INDEX IF EXISTS uq_classroom_head_teacher")
```

**Step 5: Run migration**

```bash
cd /root/inspireed-platform/backend
alembic upgrade head
```

**Step 6: Run tests to verify they pass**

```bash
cd /root/inspireed-platform/backend
pytest tests/models/test_classroom_assistant.py::test_cannot_have_duplicate_head_teachers -v
```

Expected: PASS

**Step 7: Commit**

```bash
cd /root/inspireed-platform
git add backend/app/models/classroom_assistant.py backend/alembic/versions/xxxx_add_unique_head_teacher_constraint.py backend/tests/models/test_classroom_assistant.py
git commit -m "feat: add unique constraint for head teachers

- Add partial unique index to prevent multiple HEAD_TEACHER_PRIMARY per classroom
- Migration cleans up existing duplicates before adding constraint
- Add test for duplicate head teacher prevention"
```

---

## Task 8: Update Admin Classroom List Endpoint

**Files:**
- Modify: `backend/app/api/v1/admin_organization.py:1072-1164`

**Step 1: Refactor get_classrooms to use ClassroomQueryService**

Modify `backend/app/api/v1/admin_organization.py`:

```python
@router.get("/classrooms", response_model=ClassroomListResponse)
async def get_classrooms(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=1000, description="每页数量"),
    school_id: Optional[int] = Query(None, description="学校筛选"),
    grade_id: Optional[int] = Query(None, description="年级筛选"),
    region_id: Optional[int] = Query(None, description="区域筛选"),
    school_type: Optional[str] = Query(None, description="学段筛选（小学/初中/高中）"),
    is_active: Optional[bool] = Query(None, description="激活状态筛选"),
    search: Optional[str] = Query(None, description="搜索关键词（支持班级名称、班级编码、学校名称）"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Any:
    """获取班级列表"""
    from app.services.classroom_service import ClassroomQueryService

    # ✅ Use unified service
    service = ClassroomQueryService()

    # Get filtered classrooms
    all_classrooms = await service.get_classrooms_for_user(
        db,
        current_user,
        grade_id=grade_id,
        school_id=school_id,
        region_id=region_id,
        is_active=is_active,
        search=search,
    )

    # Apply school_type filter (not in service, need to filter after)
    if school_type is not None:
        from sqlalchemy import select
        # Get schools of this type
        schools_result = await db.execute(
            select(School.id).where(School.school_type == school_type)
        )
        school_ids = set(s[0] for s in schools_result.all())
        all_classrooms = [c for c in all_classrooms if c.school_id in school_ids]

    # Pagination (in-memory since we already have the list)
    total = len(all_classrooms)
    total_pages = (total + size - 1) // size

    offset = (page - 1) * size
    paginated_classrooms = all_classrooms[offset:offset + size]

    return ClassroomListResponse(
        classrooms=[
            ClassroomResponse.model_validate(classroom) for classroom in paginated_classrooms
        ],
        total=total,
        page=page,
        size=size,
        total_pages=total_pages,
    )
```

**Step 2: Test the endpoint**

```bash
cd /root/inspireed-platform/backend
pytest tests/api/v1/test_admin_organization.py -k "get_classrooms" -v
```

**Step 3: Commit**

```bash
cd /root/inspireed-platform
git add backend/app/api/v1/admin_organization.py
git commit -m "refactor: use ClassroomQueryService in admin classroom list

- Refactor get_classrooms endpoint to use ClassroomQueryService
- Centralize filtering logic through service layer
- Maintain backward compatibility with all existing filters"
```

---

## Task 9: Update get_lesson endpoint for multi-classroom students

**Files:**
- Modify: `backend/app/api/v1/lessons.py:657-697`

**Step 1: Update get_lesson to check ClassroomMembership**

Modify `backend/app/api/v1/lessons.py`:

```python
@router.get("/{lesson_id}", response_model=LessonResponse)
async def get_lesson(
    lesson_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """获取教案详情"""
    from app.models.classroom_assistant import ClassroomMembership, RoleInClass
    from app.services.permission_service import PermissionService

    lesson = await _get_lesson_with_relations(db, lesson_id)

    if not lesson:
        raise HTTPException(status_code=404, detail="教案不存在")

    role_value = cast(str, getattr(current_user.role, "value", current_user.role))
    try:
        user_role = UserRole(role_value)
    except ValueError:
        raise HTTPException(status_code=403, detail="当前用户角色无效")

    lesson_status = LessonStatus(cast(str, lesson.status))
    creator_id = cast(Optional[int], lesson.creator_id)

    if user_role == UserRole.STUDENT:
        if lesson_status != LessonStatus.PUBLISHED:
            raise HTTPException(status_code=403, detail="无权访问该教案")

        # ✅ Use PermissionService to check access via ClassroomMembership
        permission_service = PermissionService()
        has_access = await permission_service.can_student_view_lesson(db, current_user, lesson_id)

        if not has_access:
            raise HTTPException(status_code=403, detail="该教案未分配到你的班级")
    elif user_role in {UserRole.ADMIN, UserRole.RESEARCHER}:
        pass
    else:
        if creator_id != current_user.id and lesson_status != LessonStatus.PUBLISHED:
            raise HTTPException(status_code=403, detail="无权访问该教案")

    return _lesson_to_response(lesson, request)
```

**Step 2: Test the endpoint**

```bash
cd /root/inspireed-platform/backend
pytest tests/api/v1/test_lessons.py -k "get_lesson" -v
```

**Step 3: Commit**

```bash
cd /root/inspireed-platform
git add backend/app/api/v1/lessons.py
git commit -m "feat: use ClassroomMembership for student lesson access

- Update get_lesson to check ClassroomMembership instead of User.classroom_id
- Use PermissionService.can_student_view_lesson for consistent access control
- Support students with multiple classroom memberships"
```

---

## Task 10: Documentation and Cleanup

**Files:**
- Create: `backend/docs/classroom_model_refactor.md`
- Modify: Add docstrings to affected files

**Step 1: Create documentation**

Create `backend/docs/classroom_model_refactor.md`:

```markdown
# Classroom Data Model Refactor

## Summary of Changes

This document describes the refactor of the classroom-lesson relationship system to address data inconsistency, permission validation, and query issues.

## Key Changes

### 1. Unified Query Layer

**New Service:** `app/services/classroom_service.py`

`ClassroomQueryService` is now the single source of truth for querying classrooms. All classroom access should go through this service.

**Usage:**
```python
from app.services.classroom_service import ClassroomQueryService

service = ClassroomQueryService()
classrooms = await service.get_classrooms_for_user(db, user, is_active=True)
```

### 2. Permission Service

**New Service:** `app/services/permission_service.py`

`PermissionService` handles all permission checking for classroom and lesson access.

**Usage:**
```python
from app.services.permission_service import PermissionService

service = PermissionService()
can_publish = await service.can_teacher_publish_to_classroom(db, teacher, classroom)
can_view = await service.can_student_view_lesson(db, student, lesson_id)
```

### 3. ClassroomMembership as Single Source of Truth

**Deprecated:** `Classroom.head_teacher_id` and `Classroom.deputy_head_teacher_id`

These fields are kept for backward compatibility but should NOT be used for new code.

**Use Instead:** `ClassroomMembership` with appropriate `role_in_class`:
- `HEAD_TEACHER_PRIMARY`
- `HEAD_TEACHER_DEPUTY`
- `SUBJECT_TEACHER`
- `STUDENT`
- `CADRE`

**Migration:** Existing `head_teacher_id` values are migrated to `ClassroomMembership` entries.

### 4. Soft Delete over Hard Delete

**New Endpoint:** `POST /api/v1/admin/classrooms/{id}/deactivate`

Preferred over `DELETE /api/v1/admin/classrooms/{id}` because:
- Preserves lesson assignment history
- Preserves student attendance/behavior records
- Prevents accidental data loss

### 5. Multi-Classroom Students

Students can now be members of multiple classrooms via `ClassroomMembership`.

**Old behavior:** `User.classroom_id` (single classroom)
**New behavior:** Query `ClassroomMembership` for all active memberships

## Migration Guide

### For Frontend Developers

1. **Classroom Selection:** No changes needed. `/api/v1/lessons/available-classrooms` still returns the same format.

2. **Student Views:** Students will now see lessons from all their enrolled classrooms.

### For Backend Developers

1. **Querying Classrooms:**
   ```python
   # OLD (don't use):
   # result = await db.execute(select(Classroom).where(...))

   # NEW (use this):
   from app.services.classroom_service import ClassroomQueryService
   service = ClassroomQueryService()
   classrooms = await service.get_classrooms_for_user(db, user, ...)
   ```

2. **Checking Permissions:**
   ```python
   # OLD (don't use):
   # if teacher.id == classroom.head_teacher_id:

   # NEW (use this):
   from app.services.permission_service import PermissionService
   service = PermissionService()
   if await service.can_teacher_publish_to_classroom(db, teacher, classroom):
   ```

3. **Getting Head Teachers:**
   ```python
   # OLD (don't use):
   # head_teacher = classroom.head_teacher

   # NEW (use this):
   head_teacher = await classroom.get_head_teacher(db)
   all_teachers = await classroom.get_teachers(db)
   ```

## Testing

All changes include comprehensive tests. Run tests with:

```bash
pytest tests/services/test_classroom_service.py -v
pytest tests/services/test_permission_service.py -v
pytest tests/api/v1/test_lessons.py -v
pytest tests/api/v1/test_admin_organization.py -v
```

## Rollback Plan

If issues arise, migrations can be rolled back:

```bash
alembic downgrade -1
```

The deprecated `head_teacher_id` fields remain in the database for fallback.
```

**Step 2: Add docstrings to new services**

Add docstrings to `backend/app/services/classroom_service.py` and `backend/app/services/permission_service.py` (already included in code above).

**Step 3: Commit**

```bash
cd /root/inspireed-platform
git add backend/docs/classroom_model_refactor.md
git commit -m "docs: add classroom model refactor documentation

- Document all changes made during the refactor
- Add migration guide for developers
- Include testing and rollback instructions"
```

---

## Summary

This implementation plan addresses all 5 identified issues:

| Issue | Solution | Tasks |
|-------|----------|-------|
| 1. Data Inconsistency | `ClassroomQueryService` | 1, 2, 8 |
| 2. Permission Issues | `PermissionService` + deprecate `head_teacher_id` | 4, 5, 7 |
| 3. Duplicate Definitions | Unique constraints on `ClassroomMembership` | 4, 7 |
| 4. Cascading Issues | Pre-delete checks + soft delete | 3 |
| 5. Query/Sync Issues | Multi-classroom support + `is_active` checks | 6, 9 |

**Total Tasks:** 10
**Estimated Time:** 2-3 days
**Risk Level:** Medium (backward compatible, includes migration rollback plan)

---

**Ready to implement?**
