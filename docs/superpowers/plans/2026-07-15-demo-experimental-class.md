# Demo Class Experimental Accounts Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Provision a virtual `DEMO School` / `Demo Class` with 60 student accounts (`st01`–`st60` / `123456`), let every teacher select and teach that class, and give admins a one-click provision/reset UI.

**Architecture:** A single `DemoClassService` owns DEMO org resolution, idempotent provisioning, password reset, and “is this the demo class?” checks. Teacher visibility is implemented by injecting Demo Class into `ClassroomQueryService` and `get_my_classrooms`, and by allowing any teacher in `PermissionService.can_teacher_publish_to_classroom`. Admin API + Vue page call the service.

**Tech Stack:** FastAPI, SQLAlchemy async, Pydantic, Vue 3 + TypeScript, existing Element Plus admin patterns, `unittest` (repo convention).

## Global Constraints

- School: name `DEMO School`, code `DEMO` (lookup key)
- Class: name `Demo Class`, grade name `高一` (Grade catalog; typically `level=10`)
- Accounts: usernames `st01`–`st60`, password `123456`, role `student`, display names `ST01`–`ST60`
- Emails: `st{nn}@demo.inspireed.local` (unique placeholders)
- Admin-only management; school admins must not access demo-class APIs
- Reset passwords only; do not wipe lesson/session history
- Do not create a new user role
- Do not write permanent teacher `ClassroomMembership` rows for all teachers
- `docs/` is gitignored in this repo — use `git add -f` when committing plan/spec docs

---

## File Structure

| File | Responsibility |
|---|---|
| `backend/app/services/demo_class.py` | Constants + DemoClassService (resolve / provision / reset / status) |
| `backend/app/schemas/demo_class.py` | Status / provision / reset response schemas |
| `backend/app/api/v1/admin_demo_class.py` | Admin routes: status, provision, reset-passwords |
| `backend/app/api/v1/__init__.py` | Register `/admin/demo-class` router |
| `backend/app/services/classroom_service.py` | Inject Demo Class into teacher classroom lists |
| `backend/app/services/permission_service.py` | Allow any teacher to publish/teach Demo Class |
| `backend/app/api/v1/classroom_assistant.py` | Inject Demo Class into `GET /classrooms/mine` for teachers |
| `backend/test_demo_class.py` | Unit tests for helpers + service logic (mocked DB where needed) |
| `frontend/src/services/demoClass.ts` | Admin API client |
| `frontend/src/pages/Admin/DemoClass.vue` | Admin ops page |
| `frontend/src/router/index.ts` | Route `/admin/demo-class` |
| `frontend/src/components/Admin/Dashboard/DashboardQuickNav.vue` | Nav card entry |

---

### Task 1: DemoClass helpers + constants (TDD)

**Files:**
- Create: `backend/app/services/demo_class.py`
- Test: `backend/test_demo_class.py`

**Interfaces:**
- Produces:
  - `DEMO_SCHOOL_CODE = "DEMO"`
  - `DEMO_SCHOOL_NAME = "DEMO School"`
  - `DEMO_CLASS_NAME = "Demo Class"`
  - `DEMO_CLASS_CODE = "DEMO"`
  - `DEMO_REGION_CODE = "DEMO"`
  - `DEMO_REGION_NAME = "Demo Region"`
  - `DEMO_GRADE_NAME = "高一"`
  - `DEMO_PASSWORD = "123456"`
  - `DEMO_ACCOUNT_COUNT = 60`
  - `demo_username(n: int) -> str`  # 1 → "st01"
  - `demo_display_name(n: int) -> str`  # 1 → "ST01"
  - `demo_email(n: int) -> str`  # 1 → "st01@demo.inspireed.local"
  - `is_demo_username(username: str) -> bool`
  - `all_demo_usernames() -> list[str]`

- [ ] **Step 1: Write the failing tests**

```python
# backend/test_demo_class.py
from __future__ import annotations

import unittest

from app.services.demo_class import (
    DEMO_ACCOUNT_COUNT,
    DEMO_PASSWORD,
    all_demo_usernames,
    demo_display_name,
    demo_email,
    demo_username,
    is_demo_username,
)


class DemoClassHelpersTests(unittest.TestCase):
    def test_username_padding(self) -> None:
        self.assertEqual(demo_username(1), "st01")
        self.assertEqual(demo_username(60), "st60")

    def test_display_name(self) -> None:
        self.assertEqual(demo_display_name(1), "ST01")
        self.assertEqual(demo_display_name(60), "ST60")

    def test_email(self) -> None:
        self.assertEqual(demo_email(1), "st01@demo.inspireed.local")

    def test_all_usernames_count_and_bounds(self) -> None:
        names = all_demo_usernames()
        self.assertEqual(len(names), DEMO_ACCOUNT_COUNT)
        self.assertEqual(names[0], "st01")
        self.assertEqual(names[-1], "st60")

    def test_is_demo_username(self) -> None:
        self.assertTrue(is_demo_username("st01"))
        self.assertTrue(is_demo_username("st60"))
        self.assertFalse(is_demo_username("st00"))
        self.assertFalse(is_demo_username("st61"))
        self.assertFalse(is_demo_username("student01"))

    def test_password_constant(self) -> None:
        self.assertEqual(DEMO_PASSWORD, "123456")
        self.assertGreaterEqual(len(DEMO_PASSWORD), 6)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd backend && python -m unittest test_demo_class.DemoClassHelpersTests -v`  
Expected: FAIL with `ModuleNotFoundError` or `ImportError` for `app.services.demo_class`

- [ ] **Step 3: Implement helpers**

```python
# backend/app/services/demo_class.py
from __future__ import annotations

DEMO_SCHOOL_CODE = "DEMO"
DEMO_SCHOOL_NAME = "DEMO School"
DEMO_CLASS_NAME = "Demo Class"
DEMO_CLASS_CODE = "DEMO"
DEMO_REGION_CODE = "DEMO"
DEMO_REGION_NAME = "Demo Region"
DEMO_GRADE_NAME = "高一"
DEMO_PASSWORD = "123456"
DEMO_ACCOUNT_COUNT = 60
DEMO_EMAIL_DOMAIN = "demo.inspireed.local"


def demo_username(n: int) -> str:
    return f"st{n:02d}"


def demo_display_name(n: int) -> str:
    return f"ST{n:02d}"


def demo_email(n: int) -> str:
    return f"{demo_username(n)}@{DEMO_EMAIL_DOMAIN}"


def all_demo_usernames() -> list[str]:
    return [demo_username(i) for i in range(1, DEMO_ACCOUNT_COUNT + 1)]


def is_demo_username(username: str) -> bool:
    if len(username) != 4 or not username.startswith("st"):
        return False
    try:
        n = int(username[2:])
    except ValueError:
        return False
    return 1 <= n <= DEMO_ACCOUNT_COUNT
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd backend && python -m unittest test_demo_class.DemoClassHelpersTests -v`  
Expected: PASS (6 tests)

- [ ] **Step 5: Commit**

```bash
git add backend/app/services/demo_class.py backend/test_demo_class.py
git commit -m "feat(demo-class): add account naming helpers and constants"
```

---

### Task 2: DemoClassService — resolve + status + provision + reset

**Files:**
- Modify: `backend/app/services/demo_class.py`
- Create: `backend/app/schemas/demo_class.py`
- Test: `backend/test_demo_class.py`

**Interfaces:**
- Consumes: helpers from Task 1; models `Region`, `School`, `Classroom`, `Grade`, `User`, `ClassroomMembership`, `RoleInClass`, `UserRole`; `get_password_hash`
- Produces:
  - `class DemoClassService`
  - `async def resolve_demo_classroom(self, db) -> Classroom | None`
  - `async def resolve_demo_school(self, db) -> School | None`
  - `async def is_demo_classroom(self, db, classroom: Classroom) -> bool`
  - `async def get_status(self, db) -> dict` matching schema fields below
  - `async def provision(self, db) -> dict` (raises `ValueError` with message on hard failures like missing grade / username conflict)
  - `async def reset_passwords(self, db) -> dict`

**Schemas (`backend/app/schemas/demo_class.py`):**

```python
from pydantic import BaseModel, Field
from typing import List, Optional


class DemoClassStatusResponse(BaseModel):
    school_ready: bool
    classroom_ready: bool
    school_id: Optional[int] = None
    classroom_id: Optional[int] = None
    school_name: str = "DEMO School"
    classroom_name: str = "Demo Class"
    target_accounts: int = 60
    ready_accounts: int = 0
    missing_usernames: List[str] = Field(default_factory=list)
    account_rule: str = "st01–st60 / password 123456"


class DemoClassProvisionResponse(BaseModel):
    school_id: int
    classroom_id: int
    created_users: int
    skipped_users: int
    created_memberships: int
    conflicts: List[str] = Field(default_factory=list)
    message: str


class DemoClassResetPasswordsResponse(BaseModel):
    reset_count: int
    message: str
```

- [ ] **Step 1: Write failing service-behavior tests (pure conflict / membership rules)**

Append to `backend/test_demo_class.py`:

```python
class DemoClassServiceLogicTests(unittest.TestCase):
    def test_conflict_detection_helper(self) -> None:
        from app.services.demo_class import classify_existing_user

        # existing is demo-owned when school code DEMO
        self.assertEqual(
            classify_existing_user(username="st01", school_code="DEMO"),
            "owned",
        )
        self.assertEqual(
            classify_existing_user(username="st01", school_code="OTHER"),
            "conflict",
        )
        self.assertEqual(
            classify_existing_user(username="st01", school_code=None),
            "conflict",
        )
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && python -m unittest test_demo_class.DemoClassServiceLogicTests -v`  
Expected: FAIL — `classify_existing_user` missing

- [ ] **Step 3: Implement `classify_existing_user` + full `DemoClassService`**

Add to `backend/app/services/demo_class.py`:

```python
def classify_existing_user(*, username: str, school_code: str | None) -> str:
    """Return 'owned' if user belongs to DEMO school, else 'conflict'."""
    if school_code == DEMO_SCHOOL_CODE:
        return "owned"
    return "conflict"
```

Implement `DemoClassService` with this provision algorithm:

1. `select(Grade).where(Grade.name == DEMO_GRADE_NAME)` — if missing, `raise ValueError("年级「高一」不存在，请先在课程体系中配置年级")`
2. Ensure `Region(code=DEMO_REGION_CODE)` exists (create with `name=DEMO_REGION_NAME`, `level=1` if absent)
3. Ensure `School(code=DEMO_SCHOOL_CODE)` exists (`name=DEMO_SCHOOL_NAME`, `school_type="高中"`, `region_id=...`, `is_active=True`)
4. Ensure one `Classroom` under that school with `name=DEMO_CLASS_NAME` (set `code=DEMO_CLASS_CODE`, `grade_id`, `is_active=True`, `capacity=60`)
5. For `n` in 1..60:
   - Look up `User` by `username == demo_username(n)`
   - If exists: load related school code; if `classify_existing_user(...) == "conflict"`, collect username into `conflicts` and **do not modify**; if owned, ensure scope FKs + membership, count skip
   - If missing: create `User(email=demo_email(n), username=..., hashed_password=get_password_hash(DEMO_PASSWORD), full_name=demo_display_name(n), role=UserRole.STUDENT, is_active=True, school_id, grade_id, classroom_id)`
   - Ensure `ClassroomMembership(classroom_id, user_id, role_in_class=RoleInClass.STUDENT, is_primary_class=True, is_active=True)`
6. If `conflicts` non-empty at end: still commit owned/created work, but set `message` to include conflicts; **raise `ValueError` only when conflicts prevent completing the 60-account target and you choose fail-fast** — per spec: fail and list conflicts without overwriting. Prefer: if any conflict, `raise ValueError("用户名冲突: " + ",".join(conflicts))` **before** creating anything in that run’s conflicting slots; already-created demo users remain. Simplest correct approach: scan all 60 for conflicts first; if any, raise without writes; else proceed idempotently.

Reset algorithm:

1. Resolve demo classroom; if missing, raise `ValueError("Demo Class 尚未创建")`
2. Select users where `username.in_(all_demo_usernames())` AND (`classroom_id == demo.id` OR membership in demo)
3. Set `hashed_password = get_password_hash(DEMO_PASSWORD)` for each; return `reset_count`

`resolve_demo_classroom`: School by code DEMO → Classroom by school_id and name `Demo Class`.

`is_demo_classroom`: True if classroom.school.code == DEMO (join/load school) or classroom.id == resolved demo id.

`get_status`: return readiness flags and `ready_accounts` = count of demo usernames that exist with membership in Demo Class.

Use `await db.flush()` / `await db.commit()` consistent with other admin services in this repo (prefer caller commits in API layer: service uses `flush`, API calls `commit` — match `admin_users` pattern).

- [ ] **Step 4: Run helper/logic tests**

Run: `cd backend && python -m unittest test_demo_class -v`  
Expected: PASS for helper + classify tests

- [ ] **Step 5: Commit**

```bash
git add backend/app/services/demo_class.py backend/app/schemas/demo_class.py backend/test_demo_class.py
git commit -m "feat(demo-class): add DemoClassService provision and reset"
```

---

### Task 3: Admin API routes

**Files:**
- Create: `backend/app/api/v1/admin_demo_class.py`
- Modify: `backend/app/api/v1/__init__.py`

**Interfaces:**
- Consumes: `DemoClassService`, schemas from Task 2, `get_current_admin` from `app.api.deps`
- Produces:
  - `GET /api/v1/admin/demo-class/status` → `DemoClassStatusResponse`
  - `POST /api/v1/admin/demo-class/provision` → `DemoClassProvisionResponse`
  - `POST /api/v1/admin/demo-class/reset-passwords` → `DemoClassResetPasswordsResponse`

- [ ] **Step 1: Implement router**

```python
# backend/app/api/v1/admin_demo_class.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_admin, get_db
from app.models.user import User
from app.schemas.demo_class import (
    DemoClassProvisionResponse,
    DemoClassResetPasswordsResponse,
    DemoClassStatusResponse,
)
from app.services.demo_class import DemoClassService

router = APIRouter()
service = DemoClassService()


@router.get("/status", response_model=DemoClassStatusResponse)
async def demo_class_status(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    data = await service.get_status(db)
    return DemoClassStatusResponse(**data)


@router.post("/provision", response_model=DemoClassProvisionResponse)
async def demo_class_provision(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    try:
        data = await service.provision(db)
        await db.commit()
        return DemoClassProvisionResponse(**data)
    except ValueError as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/reset-passwords", response_model=DemoClassResetPasswordsResponse)
async def demo_class_reset_passwords(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    try:
        data = await service.reset_passwords(db)
        await db.commit()
        return DemoClassResetPasswordsResponse(**data)
    except ValueError as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
```

- [ ] **Step 2: Register router in `backend/app/api/v1/__init__.py`**

Add import `admin_demo_class` alongside other admin modules, then:

```python
api_router.include_router(
    admin_demo_class.router,
    prefix="/admin/demo-class",
    tags=["管理员-实验班"],
)
```

- [ ] **Step 3: Smoke-import check**

Run: `cd backend && python -c "from app.api.v1 import admin_demo_class; print('ok', admin_demo_class.router.routes)"`  
Expected: prints `ok` and route list including `/status`, `/provision`, `/reset-passwords`

- [ ] **Step 4: Commit**

```bash
git add backend/app/api/v1/admin_demo_class.py backend/app/api/v1/__init__.py
git commit -m "feat(demo-class): add admin demo-class API routes"
```

---

### Task 4: Teacher visibility — query inject + publish permission

**Files:**
- Modify: `backend/app/services/classroom_service.py`
- Modify: `backend/app/services/permission_service.py`
- Modify: `backend/app/api/v1/classroom_assistant.py` (`get_my_classrooms`)
- Test: `backend/test_demo_class.py`

**Interfaces:**
- Consumes: `DemoClassService.resolve_demo_classroom`, `DemoClassService.is_demo_classroom`
- Produces: teachers always see Demo Class in classroom lists; `can_teacher_publish_to_classroom` returns True for Demo Class for any `UserRole.TEACHER` (and keep existing admin paths unchanged)

- [ ] **Step 1: Write failing permission unit test**

```python
class DemoClassPermissionTests(unittest.TestCase):
    def test_demo_classroom_allowed_without_same_school(self) -> None:
        from app.services.demo_class import DEMO_SCHOOL_CODE
        from app.services.permission_service import PermissionService

        # Pure helper extracted for sync check used by async method
        from app.services.permission_service import teacher_may_access_demo_classroom

        self.assertTrue(
            teacher_may_access_demo_classroom(school_code=DEMO_SCHOOL_CODE)
        )
        self.assertFalse(
            teacher_may_access_demo_classroom(school_code="OTHER")
        )
```

Note: implement `teacher_may_access_demo_classroom(school_code: str | None) -> bool` as `return school_code == DEMO_SCHOOL_CODE`. The async method will load classroom.school and call this after membership/school checks fail.

- [ ] **Step 2: Run test — expect fail, then implement helper + wire permission**

In `PermissionService.can_teacher_publish_to_classroom`, after existing membership and `school_id` checks, before `return False`:

```python
from app.services.demo_class import DEMO_SCHOOL_CODE
# ensure school loaded
school = classroom.school
if school is None:
    school = await db.get(School, classroom.school_id)
if school is not None and teacher_may_access_demo_classroom(school.code):
    # only teachers/admins/researchers reach publish flows; still require teacher role here
    role_value = teacher.role.value if hasattr(teacher.role, "value") else teacher.role
    if role_value in {UserRole.TEACHER.value, UserRole.ADMIN.value, UserRole.RESEARCHER.value}:
        return True
return False
```

Add at module level:

```python
def teacher_may_access_demo_classroom(school_code: str | None) -> bool:
    from app.services.demo_class import DEMO_SCHOOL_CODE
    return school_code == DEMO_SCHOOL_CODE
```

- [ ] **Step 3: Inject in `ClassroomQueryService.get_classrooms_for_user`**

At end of method, before return, for roles that teach (`TEACHER`, and optionally leave ADMIN as-is since they already see all):

```python
from app.services.demo_class import DemoClassService

# ... after building `classrooms` list (including early-return paths for teachers with no school)

async def _append_demo(classrooms: list[Classroom]) -> list[Classroom]:
    demo = await DemoClassService().resolve_demo_classroom(db)
    if demo is None:
        return classrooms
    if is_active is not None and demo.is_active != is_active:
        return classrooms
    if school_id is not None and demo.school_id != school_id:
        # Explicit school filter: only include if filtering DEMO school
        return classrooms
    if any(c.id == demo.id for c in classrooms):
        return classrooms
    return list(classrooms) + [demo]

# Change teacher early `return []` when school_id is None to:
#   classrooms = []
#   return await _append_demo(classrooms)
# And replace final `return list(...)` with append helper.
```

Apply the same early-return fix so teachers without `school_id` still get Demo Class.

- [ ] **Step 4: Inject in `get_my_classrooms`**

After building `classrooms` list in `classroom_assistant.py`, if current user role is teacher (or always for non-students):

```python
from app.services.demo_class import DemoClassService
from app.models.user import UserRole

role_value = getattr(current_user.role, "value", current_user.role)
if role_value == UserRole.TEACHER.value:
    demo = await DemoClassService().resolve_demo_classroom(db)
    if demo and all(c.id != demo.id for c in classrooms):
        classrooms.append(ClassroomInfo(
            id=demo.id,
            name=demo.name,
            code=demo.code,
            school_id=demo.school_id,
            grade_id=demo.grade_id,
            head_teacher_id=demo.head_teacher_id,
            deputy_head_teacher_id=demo.deputy_head_teacher_id,
            role_in_class=None,
        ))
```

- [ ] **Step 5: Run unit tests**

Run: `cd backend && python -m unittest test_demo_class -v`  
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add backend/app/services/classroom_service.py backend/app/services/permission_service.py backend/app/api/v1/classroom_assistant.py backend/test_demo_class.py
git commit -m "feat(demo-class): inject Demo Class into teacher classroom access"
```

---

### Task 5: Admin frontend — service, page, route, nav

**Files:**
- Create: `frontend/src/services/demoClass.ts`
- Create: `frontend/src/pages/Admin/DemoClass.vue`
- Modify: `frontend/src/router/index.ts`
- Modify: `frontend/src/components/Admin/Dashboard/DashboardQuickNav.vue`

**Interfaces:**
- Consumes: admin APIs from Task 3
- Produces: `/admin/demo-class` page with status, provision, reset, copy account list

- [ ] **Step 1: Add API client**

```typescript
// frontend/src/services/demoClass.ts
import api from './api'

export interface DemoClassStatus {
  school_ready: boolean
  classroom_ready: boolean
  school_id: number | null
  classroom_id: number | null
  school_name: string
  classroom_name: string
  target_accounts: number
  ready_accounts: number
  missing_usernames: string[]
  account_rule: string
}

export interface DemoClassProvisionResult {
  school_id: number
  classroom_id: number
  created_users: number
  skipped_users: number
  created_memberships: number
  conflicts: string[]
  message: string
}

export interface DemoClassResetResult {
  reset_count: number
  message: string
}

export const demoClassService = {
  async getStatus(): Promise<DemoClassStatus> {
    return await api.get('/admin/demo-class/status')
  },
  async provision(): Promise<DemoClassProvisionResult> {
    return await api.post('/admin/demo-class/provision')
  },
  async resetPasswords(): Promise<DemoClassResetResult> {
    return await api.post('/admin/demo-class/reset-passwords')
  },
}

export function buildAccountListText(): string {
  const lines: string[] = []
  for (let i = 1; i <= 60; i++) {
    const u = `st${String(i).padStart(2, '0')}`
    lines.push(`${u} / 123456`)
  }
  return lines.join('\n')
}
```

(Adjust `api.get/post` unwrap to match how `frontend/src/services/admin.ts` returns data.)

- [ ] **Step 2: Add Vue page**

Create `frontend/src/pages/Admin/DemoClass.vue` following existing admin page style (Element Plus cards/buttons):

- On mount: load status
- Show school/class ready, ready_accounts/60, account_rule
- Buttons:「一键创建/补齐」「一键重置密码」「复制账号清单」
- Confirm dialogs before provision/reset
- Toast success/error from API `detail` / `message`

Keep UI minimal — one purpose page, no extra marketing chrome.

- [ ] **Step 3: Register route**

In `frontend/src/router/index.ts`, next to other admin routes:

```typescript
{
  path: '/admin/demo-class',
  name: 'AdminDemoClass',
  component: () => import('../pages/Admin/DemoClass.vue'),
  meta: { requiresAuth: true, role: 'admin', title: '实验班 - InspireEd' },
},
```

- [ ] **Step 4: Add dashboard nav card**

In `DashboardQuickNav.vue`, add a card:

- title: `实验班`
- description: `演示账号一键开通与重置`
- `@click="router.push('/admin/demo-class')"`

- [ ] **Step 5: Manual UI check**

Run frontend dev server if needed; open `/admin/demo-class` as admin — page loads, buttons visible.

- [ ] **Step 6: Commit**

```bash
git add frontend/src/services/demoClass.ts frontend/src/pages/Admin/DemoClass.vue frontend/src/router/index.ts frontend/src/components/Admin/Dashboard/DashboardQuickNav.vue
git commit -m "feat(demo-class): add admin Demo Class provisioning page"
```

---

### Task 6: End-to-end verification checklist

**Files:** none new (manual / API verification)

- [ ] **Step 1: Provision via API (admin token)**

```bash
# obtain admin JWT via existing login, then:
curl -s -X POST "$API/api/v1/admin/demo-class/provision" \
  -H "Authorization: Bearer $TOKEN" | jq .
curl -s "$API/api/v1/admin/demo-class/status" \
  -H "Authorization: Bearer $TOKEN" | jq .
```

Expected: `ready_accounts: 60`, school/classroom ready true. Second provision: `created_users: 0`, still 60.

- [ ] **Step 2: Student login**

Login `st01` / `123456` — succeeds, role student.

- [ ] **Step 3: Teacher classroom list**

As a teacher whose `school_id` is **not** DEMO: call `GET /api/v1/lessons/available-classrooms` and `GET /api/v1/classroom-assistant/classrooms/mine` — both include `Demo Class`.

- [ ] **Step 4: Teach smoke**

Teacher publishes/assigns a lesson to Demo Class and creates a session — must **not** 403. Student `st01` sees the session/lesson via membership.

- [ ] **Step 5: Reset passwords**

Change `st01` password in admin users UI (or DB), then `POST .../reset-passwords`, login again with `123456`.

- [ ] **Step 6: Conflict case (optional staging)**

Create a non-demo user `st05` under another school; provision must return 400 with conflict mentioning `st05` and must not overwrite that user.

- [ ] **Step 7: Final commit if any fixes**

```bash
git add -A
git commit -m "fix(demo-class): address verification findings"
```

(Only if fixes were needed; skip empty commit.)

---

## Spec Coverage Self-Review

| Spec requirement | Task |
|---|---|
| DEMO School + Demo Class + 高一 | Task 2 |
| st01–st60 / 123456 / membership | Task 2 |
| Idempotent provision + conflict fail | Task 2 |
| Reset passwords only | Task 2 |
| Admin status/provision/reset API | Task 3 |
| All teachers see Demo Class | Task 4 (query + mine) |
| All teachers can teach Demo Class | Task 4 (permission — required; list-only would 403) |
| Admin UI one-click | Task 5 |
| Copy account list | Task 5 |
| Tests: idempotent helpers, conflict classify, permission | Tasks 1–4, 6 |
| No new role / no mass teacher membership | Global + Task 4 |

## Placeholder / consistency check

- No TBD left.
- Password consistently `123456`.
- Injection points named: `ClassroomQueryService`, `get_my_classrooms`, `can_teacher_publish_to_classroom`.
- Service name consistently `DemoClassService`.
