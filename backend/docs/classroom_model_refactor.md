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

## Implementation Tasks

### Completed Tasks (1-5)

- Task 1: Create ClassroomQueryService
- Task 2: Refactor get_available_classrooms to use ClassroomQueryService
- Task 3: Add Pre-Delete Checks to prevent cascade issues
- Task 4: Deprecate head_teacher_id fields
- Task 5: Update Permission Check to Use ClassroomMembership

### New Tasks (6-10)

- Task 6: Support Multiple Classrooms for Students
  - Modified `app/api/v1/lessons.py` list_lessons to use ClassroomMembership
  - Students can now be members of multiple classrooms
  - Added test in `tests/api/v1/test_lessons_multiclassroom.py`

- Task 7: Add Validation for Head Teachers
  - Added unique partial index on ClassroomMembership for HEAD_TEACHER_PRIMARY
  - Created migration `20260131_1400_add_unique_head_teacher_constraint.py`
  - Migration cleans up duplicates before adding constraint

- Task 8: Update Admin Classroom List
  - Modified `app/api/v1/admin_organization.py` get_classrooms
  - Now uses ClassroomQueryService for centralized filtering logic

- Task 9: Update get_lesson endpoint
  - Modified `app/api/v1/lessons.py` get_lesson
  - Now uses PermissionService.can_student_view_lesson for multi-classroom support

- Task 10: Documentation
  - Created `backend/docs/classroom_model_refactor.md`
  - This document provides migration guide and implementation details

## Files Modified

### Backend API
- `app/api/v1/lessons.py` - Multi-classroom support for list_lessons, get_recommended_lessons, get_lesson
- `app/api/v1/admin_organization.py` - Refactored get_classrooms to use ClassroomQueryService

### Models
- `app/models/classroom_assistant.py` - Added unique constraint for HEAD_TEACHER_PRIMARY

### Services
- `app/services/classroom_service.py` - Already created in Task 1
- `app/services/permission_service.py` - Already created in Task 5

### Migrations
- `alembic/versions/20260131_1400_add_unique_head_teacher_constraint.py` - New migration for Task 7

### Tests
- `tests/api/v1/test_lessons_multiclassroom.py` - New test for multi-classroom students

### Documentation
- `docs/classroom_model_refactor.md` - This file

## Commits

All tasks have been batched into commits for easier review:

1. Task 6: Multi-classroom student support
2. Task 7: Head teacher validation
3. Task 8: Admin classroom list refactor
4. Task 9: get_lesson endpoint update
5. Task 10: Documentation

## Benefits

1. **Data Consistency:** ClassroomMembership is now the single source of truth for teacher-classroom relationships
2. **Multi-Classroom Support:** Students can be enrolled in multiple classrooms simultaneously
3. **Validation:** Database constraints prevent duplicate head teachers per classroom
4. **Centralized Logic:** All classroom queries go through ClassroomQueryService
5. **Permission Management:** PermissionService provides consistent access control
6. **Backward Compatibility:** Deprecated fields remain for gradual migration
