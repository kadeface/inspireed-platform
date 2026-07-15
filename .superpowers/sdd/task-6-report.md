# Task 6 Report: End-to-end verification checklist for Demo Class

## Status: DONE_WITH_CONCERNS

## Method

Backend was already running (`restart.sh`, uvicorn --reload, port 8000) against the real
local Postgres DB. Rather than bypass the API, I drove verification via **live HTTP** (curl)
against `http://localhost:8000`, using an existing admin account and existing/repurposed
teacher accounts, plus small one-off `AsyncSessionLocal` scripts only for things HTTP can't do
(inspecting/seeding test-account passwords, querying raw DB state to explain results).

## Commit

`6497899` — fix(demo-class): avoid `*.local` email domain rejected by EmailStr

## Bug found and fixed

`DEMO_EMAIL_DOMAIN = "demo.inspireed.local"` generates emails like `st01@demo.inspireed.local`.
Pydantic's `EmailStr` (backed by `email-validator`) rejects `*.local` as an IANA special-use
domain **even with no network/deliverability check enabled**. Since `UserResponse.email` is
`EmailStr`, this raised a `ResponseValidationError` → HTTP 500 on **every** endpoint that
serializes a demo student through `UserResponse`, most importantly `GET /auth/me` (the call
most frontends make right after login). Confirmed via `logs/backend.log` traceback.

- Fixed: `DEMO_EMAIL_DOMAIN = "demo.inspireed.internal"` (verified this passes `EmailStr` with
  the repo's installed `email-validator`, unlike `.local`/`.test`/`.invalid`).
- Updated `test_demo_class.py`'s `test_email` expectation to match.
- **Data fix (not code):** the 60 demo users already provisioned during this verification run
  had the old `@...local` emails; updated them in-place to `@...internal` via a one-off script
  so the live DEMO account data is internally consistent with the new code (this was a data
  migration for demo accounts intentionally left in the DB, not a schema/business-data change).
- Added a short code comment on the constant explaining the constraint, so it isn't
  reintroduced.

## Verification results

| # | Step | Result |
|---|---|---|
| 1 | Provision via admin API, idempotent 2nd run | **PASS** — 1st run: `created_users:60, skipped_users:0`, status `ready_accounts:60/60`. 2nd run: `created_users:0, skipped_users:60`, still 60/60. 3rd run (after the email fix + data migration): still `created_users:0`, 60/60. |
| 2 | Student login `st01`/`123456` | **PASS** (after fix) — login returns a token, role `student`; `GET /auth/me` returns full profile (`school_name: "DEMO School"`, `classroom_id: 212`). Before the fix, login itself worked but `/auth/me` 500'd. |
| 3 | Teacher classroom list includes Demo Class (teacher not in DEMO school) | **PASS for `/lessons/available-classrooms`**; **blocked by an unrelated pre-existing bug for `/classroom-assistant/classrooms/mine`** for teachers with real memberships (see Concerns). Verified `available-classrooms` for `teacher1` (school_id=1, 20 items) includes `Demo Class` (`id 212, school_id 574`) appended at the end. Verified `classrooms/mine` for a different teacher (`guan`, school_id=566, no other memberships) returns exactly `[Demo Class]`, confirming the injection code itself is correct. |
| 4 | Teach smoke: publish + session, no 403; student sees it | **PASS** — as `teacher1` (school 1, not DEMO): `POST /lessons/17/publish {classroom_ids:[212]}` → 200 (lesson_classrooms row created); `POST /classroom-sessions/lessons/17/sessions {classroom_id:212}` → **201**, no 403. `st01` → `GET /classroom-sessions/student/pending-sessions` → 200, includes the new session (`classroom_name: "Demo Class"`). |
| 5 | Reset passwords | **PASS** — changed `st01`'s password directly in DB; login with `123456` → 401 as expected; `POST /admin/demo-class/reset-passwords` → `reset_count:60`; login with `123456` → 200 again. |
| 6 | Conflict case (optional) | **SKIPPED** (marked optional in the brief). Would require temporarily hijacking one of the 60 already-live demo accounts (all `st01`-`st60` slots are now real demo users) to manufacture a conflict, then restoring it — a disruptive, higher-risk action for a case whose logic is already covered by `test_conflict_detection_helper` (unit test) and by direct code review of `DemoClassService.provision()`, which scans **all** usernames for conflicts *before* creating the school/classroom/any accounts, raises `ValueError` (→ HTTP 400) with the conflicting usernames, and writes nothing on conflict. |
| — | `unittest test_demo_class` | **PASS** — `Ran 8 tests ... OK` (before and after the fix). |

## Concerns

1. **Pre-existing, unrelated data bug**: `classroom_memberships.role_in_class` has 63 rows with
   the value `'teacher'`, which is not a member of the `RoleInClass` enum
   (`head_teacher_primary/deputy`, `subject_teacher`, `cadre`, `student`). These rows were
   created 2026-01-30 — long before this feature's work started today — so this is not caused
   by Demo Class. It breaks `GET /classroom-assistant/classrooms/mine` (500,
   `LookupError: 'teacher' is not among the defined enum values`) for **any** account with such
   a row, including several teacher test accounts I tried first (`teacher1`, `teacher@inspireed.com`
   has a null school so wasn't affected, but others were). This is out of scope for Task 6/Demo
   Class and was **not fixed** — flagging for a separate ticket. It does not affect the Demo
   Class feature itself: `available-classrooms` (used for actual lesson publishing) uses a
   different code path (`ClassroomQueryService`) that is unaffected, and I independently verified
   the Demo Class injection logic in `get_my_classrooms` works correctly against a clean account.
2. Step 6 (conflict case) was not exercised live, for the reasons above (optional + disruptive to
   already-provisioned live demo data). Logic reviewed instead.
3. Two test/seed accounts had their passwords reset to known values purely for verification
   (`teacher1@inspireed.com` → `teacher123`, `guan@inspireed.com` → `teacher123`), matching the
   existing `backend/reset_teacher_password.py` pattern in this repo. `st01`'s password was
   restored to `123456` by the end of the run (Step 5).
4. Left in place (intentionally, per task instructions): 1 DEMO school, 1 Demo Class, 60
   `st01`-`st60` accounts (password `123456`), all memberships — this is the desired end state
   for the feature.

## Report path

`/Users/382241106qq.com/inspireed-platform-main/.superpowers/sdd/task-6-report.md`

## Final-review fixes

Addressed the Important/cleanup findings from the final whole-branch review.

### 1. Automated coverage (Important)

Added `backend/tests/services/test_demo_class_service.py` — 9 async pytest
tests using the existing `async_session`/`db` fixture pattern from
`backend/tests/conftest.py` (SQLite in-memory via `aiosqlite`, which was
missing from the venv; installed it and pinned it in `requirements.txt`
under "Testing and code quality").

Coverage:
- `test_provision_creates_school_classroom_and_accounts`,
  `test_provision_is_idempotent` — provision idempotency (2nd run: 0 created,
  N skipped, no duplicate users/memberships).
- `test_provision_conflict_prescan_raises_without_writing` — proves the
  conflict pre-scan raises `ValueError` **before** writing anything: no DEMO
  school/classroom is created, the conflicting user is untouched, and no
  other demo accounts leak into existence.
- `test_reset_passwords_requires_existing_classroom`,
  `test_reset_passwords_scoped_to_demo_classroom_membership` — proves
  `reset_passwords()` is scoped by classroom link (`User.classroom_id` OR an
  active `ClassroomMembership` row), not just by username pattern: a demo
  account moved out of the Demo Class (classroom_id repointed + membership
  row removed) is excluded from a subsequent reset, and re-included as long
  as it's still linked.
- `test_teacher_may_publish_to_demo_classroom_without_same_school`,
  `test_student_from_other_school_may_not_publish_to_demo_classroom` — async
  test of `PermissionService.can_teacher_publish_to_classroom` for the DEMO
  school code: any teacher (regardless of school) may publish to the Demo
  Class, but a non-demo-school student (role-gated out) may not. Note: this
  function also has a generic non-demo "matching school_id" fallback that
  isn't role-gated by itself (role gating for the demo bypass specifically is
  `{TEACHER, ADMIN, RESEARCHER}`); the negative test uses a user from a
  different school so it actually exercises the demo-bypass gate instead of
  that fallback.
- `test_demo_classroom_injected_for_teacher_outside_demo_school`,
  `test_demo_classroom_not_injected_when_school_filter_excludes_it` —
  `ClassroomQueryService._append_demo_classroom` injection path: the Demo
  Class is appended to a teacher's classroom list even when they belong to a
  different school, but is correctly excluded when an explicit `school_id`
  filter doesn't match the DEMO school.

**Documented limit:** `DEMO_ACCOUNT_COUNT` is monkeypatched to `1` for these
tests (see the `small_demo_account_count` fixture docstring), for two
reasons: (a) each new account is bcrypt-hashed, so provisioning all 60
repeatedly is slow; (b) a **pre-existing, unrelated** model/test-infra gap —
`ClassroomMembership`'s partial unique index
(`uq_classroom_head_teacher`, meant to be restricted via `postgresql_where`
to `role_in_class = 'head_teacher_primary'`) has no `sqlite_where`
counterpart, so on the SQLite test engine it silently becomes a full unique
index on `classroom_id` alone — at most one `ClassroomMembership` row can
exist per classroom in this test DB, regardless of role. Not fixed (out of
scope, not a Demo Class bug, not touched per the "do not fix unrelated
things" instruction) — tests were written to never need two simultaneous
membership rows in the same classroom.

### 2. `conflicts` field cleanup (Minor)

Left the `conflicts` field in `DemoClassProvisionResponse` / the frontend
`ProvisionResult` type for API stability (nothing else references it beyond
declaration, so removing it wasn't required, and the schema is harmless).
Added a one-line comment in `DemoClassService.provision()`'s return
statement documenting that it is always empty on a successful return (the
pre-scan raises `ValueError` on any conflict before writing).

### 3. Unused `is_demo_classroom` (Minor)

Removed `DemoClassService.is_demo_classroom()` — confirmed zero callers
(the actual demo-classroom checks in the codebase go through
`resolve_demo_classroom()` + `School.code` directly, e.g. in
`ClassroomQueryService._append_demo_classroom` and
`teacher_may_access_demo_classroom()`).

## Tests re-run

```
cd backend && ./venv/bin/python3 -m unittest test_demo_class -v
# Ran 8 tests in 0.001s — OK

./venv/bin/python3 -m pytest tests/services/test_demo_class_service.py -q
# 9 passed

./venv/bin/python3 -m pytest tests/services/test_demo_class_service.py \
    tests/services/test_classroom_service.py \
    tests/services/test_session_state_machine.py -q
# 38 passed (confirms no regression in sibling suites)
```

Note: `tests/services/test_permission_service.py` and a full `pytest tests/`
run were **not** used as regression gates — both fail for reasons unrelated
to this change (`test_permission_service.py` has a pre-existing broken
fixture default `lesson_id: lesson.id` referencing an undefined name at
collection time; a full-suite run segfaults inside `numpy`/`pandas` import
triggered by an unrelated API test module). Neither touches Demo Class code.

## Commit

`fix(demo-class): remove dead is_demo_classroom, add regression tests for provision/reset/permission/inject`

## Concerns

- The SQLite partial-unique-index gap above should probably get its own
  ticket (add `sqlite_where` alongside `postgresql_where`, or accept SQLite
  is not a faithful substitute here) — flagging, not fixing.
- `test_permission_service.py`'s broken fixture (`lesson_id: lesson.id`) is
  pre-existing and unrelated; also flagging, not fixing.
