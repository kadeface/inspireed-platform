# Feature: Unified Import System

The following plan should be complete, but its important that you validate documentation and codebase patterns and task sanity before you start implementing.

Pay special attention to naming of existing utils types and models. Import from the right files etc.

## Feature Description

Implement a unified import framework to consolidate 5 scattered import services (StudentImportService, TeacherAssignmentImportService, ClassroomImportService, SchoolImportService, ExcelImportService) totaling 3560 lines of duplicated code. The new system uses Strategy + Orchestrator patterns to provide consistent Excel parsing, validation, error handling, and progress tracking across all import types while reducing code duplication by ~58%.

## User Story

As a **platform developer**
I want to **unify all import functionality into a single, extensible framework**
So that **I can maintain consistent import behavior, reduce code duplication, and easily add new import types**

## Problem Statement

Current import functionality is scattered across 5 separate service files with significant code duplication:

- **StudentImportService** (592 lines): Imports student exam mappings with Excel parsing
- **TeacherAssignmentImportService** (1386 lines): Largest service, handles teacher assignments
- **ClassroomImportService** (623 lines): Dual-mode import (school/district level)
- **SchoolImportService** (487 lines): School information import
- **ExcelImportService** (472 lines): Score import with progress tracking

**Violated Principles:**
- **DRY**: Excel parsing, validation, error handling duplicated across all services
- **SRP**: Services handle parsing, validation, database operations, and progress tracking
- **OCP**: Adding new import types requires modifying existing code or creating entirely new services
- **ISP**: Services implement methods they don't use

**Current Issues:**
1. Each service reimplements Excel column mapping with slight variations
2. Validation logic duplicated across services
3. Error handling inconsistent (some use exceptions, some return error dicts)
4. Progress tracking only available in ExcelImportService
5. API endpoints scattered: `/api/v1/users/batch-import`, `/api/v1/teachers/assignments/import`, `/api/v1/exams/{id}/students/import`, `/api/v1/classrooms/import`, `/api/v1/schools/import`
6. Frontend has 6 different import UI implementations

## Solution Statement

Design a unified import framework using:

1. **Strategy Pattern**: Each import type implements a common interface (BaseImportStrategy)
2. **Orchestrator Pattern**: ImportOrchestrator coordinates the import process
3. **Base Importer Class**: Provides common Excel parsing, validation, and error handling
4. **Unified API Endpoint**: `/api/v1/import` with strategy selection via request body
5. **Frontend Unified Import Component**: Reusable import modal with strategy-based configuration

**Target Metrics:**
- Code reduction: 3560 → 1500 lines (58% reduction)
- Single API endpoint instead of 9+
- Single frontend component instead of 6
- Consistent error handling and progress tracking across all imports

## Feature Metadata

**Feature Type**: Refactor
**Estimated Complexity**: High
**Primary Systems Affected**:
- Backend: `backend/app/services/` (5 import services)
- Backend: `backend/app/api/v1/` (9+ import endpoints)
- Frontend: `frontend/src/pages/` (6 import UIs)

**Dependencies**:
- openpyxl (already installed: 3.1.2)
- FastAPI (already installed: 0.104.1)
- SQLAlchemy 2.0 async patterns (already in use)
- pypinyin (already installed: 0.50.0)

---

## CONTEXT REFERENCES

### Relevant Codebase Files IMPORTANT: YOU MUST READ THESE FILES BEFORE IMPLEMENTING!

**Backend Import Services (Current Implementation):**

- `backend/app/services/student_import_service.py` (lines 1-592)
  - Why: Shows Excel column mapping pattern, parsing with `load_workbook`, row iteration
  - Key patterns: `COLUMN_MAPPING` dict, `parse_*_excel()` returns `(records, errors)`, static methods for validation
  - Lines 38-67: Column mapping with multiple aliases
  - Lines 73-213: Excel parsing with openpyxl
  - Lines 216-256: `parse_classroom_code()` utility pattern

- `backend/app/services/teacher_assignment_import_service.py` (lines 1-1386)
  - Why: Most complex import example, shows all validation patterns
  - Lines 44-92: Extensive column mapping with multiple aliases
  - Lines 95-200: Excel parsing with header detection
  - Lines 200+: Data validation patterns

- `backend/app/services/classroom_import_service.py` (lines 1-623)
  - Why: Shows dual-mode import (school vs district), two column mappings
  - Lines 35-114: Two column mappings (DISTRICT_COLUMN_MAPPING, SCHOOL_COLUMN_MAPPING)
  - Lines 117-254: `parse_classroom_excel()` with mode selection
  - Lines 257-312: `parse_classroom_code()` pattern matching

- `backend/app/services/school_import_service.py` (lines 1-487)
  - Why: Shows auto-create pattern (find_or_create_region)
  - Lines 31-66: COLUMN_MAPPING pattern
  - Lines 193-244: `find_or_create_region()` with fuzzy matching
  - Lines 333-390: Code generation patterns

- `backend/app/services/excel_import_service.py` (lines 1-472)
  - Why: Only service with progress tracking via callback
  - Lines 283-390: `import_scores()` with `progress_callback` parameter
  - Lines 393-472: `process_import_task()` async task handling
  - Lines 431-440: Progress callback update pattern

**Backend Models (Database Schema):**

- `backend/app/models/user.py`
  - Why: User model structure for student/teacher imports
  - Fields: `student_id_number`, `classroom_id`, `role`

- `backend/app/models/__init__.py`
  - Why: Import all models, understand relationships
  - Key models: `Region`, `School`, `Grade`, `Classroom`, `Subject`, `Semester`, `TeacherTeachingAssignment`

**Backend API Endpoints (Current Endpoints):**

- `backend/app/api/v1/admin_users.py`
  - Why: Contains `/batch-import` endpoint for user import
  - Pattern: POST endpoint accepting UploadFile, returning import result

- `backend/app/api/v1/admin_organization.py`
  - Why: Contains `/schools/import` and `/classrooms/import` endpoints
  - Pattern: File upload → parse → validate → import → return results

- `backend/app/api/v1/teachers.py`
  - Why: Contains `/teachers/assignments/import` endpoint
  - Pattern: Complex import with teacher auto-creation

**Frontend Import UIs:**

- `frontend/src/pages/Admin/OrganizationManagement/SchoolManagementCard.vue`
  - Why: Shows school import UI with file upload, template download
  - Lines with "批量导入学校": Import dialog UI
  - Lines with `downloadSchoolTemplate()`: XLSX template generation
  - Lines with `startSchoolImport()`: File upload and progress tracking

- `frontend/src/pages/Admin/OrganizationManagement/TeacherAssignmentCard.vue`
  - Why: Shows complex import UI with multi-step wizard
  - Lines with "批量导入教学任务": Import dialog
  - Lines with `downloadAssignmentTemplate()`: Template generation
  - Lines with `exportCreatedTeachers()`: Export created accounts

- `frontend/src/pages/DistrictExamAdmin/StudentImport.vue`
  - Why: Shows student exam import UI
  - Pattern: File upload → validation → preview → confirm

**Frontend Services:**

- `frontend/src/services/admin.ts`
  - Why: Contains API service methods for imports
  - Methods: `batchImportUsers()`, `importSchools()`, `importClassrooms()`

- `frontend/src/services/teacher.ts`
  - Why: Teacher assignment import API
  - Methods: `importTeacherAssignments()`

### New Files to Create

**Backend:**
- `backend/app/services/import_base.py` - Base importer class with common Excel parsing
- `backend/app/services/import_strategies/` - Strategy implementations directory
  - `backend/app/services/import_strategies/__init__.py`
  - `backend/app/services/import_strategies/student_import_strategy.py` - Student import strategy
  - `backend/app/services/import_strategies/teacher_import_strategy.py` - Teacher assignment import strategy
  - `backend/app/services/import_strategies/classroom_import_strategy.py` - Classroom import strategy
  - `backend/app/services/import_strategies/school_import_strategy.py` - School import strategy
  - `backend/app/services/import_strategies/score_import_strategy.py` - Score import strategy
- `backend/app/services/import_orchestrator.py` - Import orchestrator
- `backend/app/api/v1/import.py` - Unified import API endpoint
- `backend/app/schemas/import.py` - Import request/response schemas

**Frontend:**
- `frontend/src/components/Import/UnifiedImportModal.vue` - Unified import modal component
- `frontend/src/components/Import/ImportTemplateGenerator.ts` - Template generation utility
- `frontend/src/services/import.ts` - Unified import service
- `frontend/src/composables/useImport.ts` - Import composable with common logic

**Tests:**
- `backend/tests/test_import_base.py` - Base importer tests
- `backend/tests/test_import_strategies.py` - Strategy tests
- `backend/tests/test_import_orchestrator.py` - Orchestrator tests

### Relevant Documentation YOU SHOULD READ THESE BEFORE IMPLEMENTING!

- [openpyxl Documentation](https://openpyxl.readthedocs.io/en/stable/)
  - Section: "Reading a spreadsheet"
  - Why: Excel file parsing patterns, `load_workbook()`, `iter_rows()`
  - Best practice: Use `read_only=True`, `data_only=True` for large files

- [SQLAlchemy 2.0 Async](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
  - Section: "AsyncSession established patterns"
  - Why: Async database operations patterns used throughout services
  - Pattern: `async with AsyncSession(db_engine) as session:`

- [FastAPI File Uploads](https://fastapi.tiangolo.com/tutorial/request-files/)
  - Section: "UploadFile"
  - Why: File upload handling pattern for all imports
  - Pattern: `file: UploadFile = File(...)` with async file operations

- [Python Strategy Pattern](https://refactoring.guru/design-patterns/strategy/python/example)
  - Section: Strategy pattern implementation
  - Why: Pattern to follow for strategy implementations
  - Pattern: Abstract base class with concrete strategy implementations

### Patterns to Follow

**Naming Conventions:**
- Services: PascalCase with suffix (e.g., `StudentImportStrategy`)
- Methods: snake_case (e.g., `parse_excel_file`, `validate_record`)
- Column mappings: UPPER_CASE with underscores (e.g., `COLUMN_MAPPING`, `REQUIRED_COLUMNS`)
- Private methods: prefix with underscore (e.g., `_generate_code`, `_find_entity`)

**Error Handling:**
- Custom exceptions inherit from Exception: `class StudentImportServiceError(Exception):`
- Validation errors return dict: `{"row": int, "field": str, "message": str}`
- Service methods raise custom exceptions on failure
- API endpoints catch exceptions and return appropriate HTTP status codes

**Logging Pattern:**
```python
logger = logging.getLogger(__name__)
logger.info(f"Import started: {total} records")
logger.warning(f"Validation failed: {error_msg}")
logger.error(f"Import failed: {error}", exc_info=True)
```

**Database Query Pattern:**
```python
result = await db.execute(
    select(Model).where(Model.field == value)
)
entity = result.scalar_one_or_none()
```

**Transaction Pattern:**
```python
try:
    # Operations
    await db.flush()  # Get IDs without committing
    await db.commit()
except IntegrityError:
    await db.rollback()
    raise
```

**Other Relevant Patterns:**

**Excel Parsing Pattern** (from student_import_service.py:86-113):
```python
wb = load_workbook(filename=file_path, read_only=True, data_only=True)
ws = wb.active
headers = [str(h).strip().rstrip('*').strip() if h else "" for h in ws[1]]
column_indices = {}
for col_name, field_name in COLUMN_MAPPING.items():
    if col_name in headers:
        column_indices[field_name] = headers.index(col_name)
```

**Column Mapping Pattern** (from student_import_service.py:39-67):
```python
COLUMN_MAPPING = {
    "区域名称": "region_name",
    "市(区)": "region_name",  # Multiple aliases
    "学校名称": "school_name",
    "学校": "school_name",
    # ...
}
```

**Validation Pattern** (from student_import_service.py:458-524):
```python
# 1. Validate and lookup entities
region = await find_region(db, region_name)
if not region:
    errors.append({"row": row_number, "field": "区域", "message": f"区域不存在"})
    result["failed"] += 1
    continue

# 2. Cache lookups for performance
if region_name in region_cache:
    region = region_cache[region_name]
else:
    region = await find_region(db, region_name)
    region_cache[region_name] = region
```

**Import Result Pattern**:
```python
return {
    "total": int,
    "success": int,
    "failed": int,
    "created": int,
    "updated": int,
    "skipped": int,
    "errors": List[Dict[str, Any]]
}
```

---

## IMPLEMENTATION PLAN

### Phase 1: Foundation

**Tasks:**

1. Create base importer class with common Excel parsing logic
2. Define import strategy interface (abstract base class)
3. Create import schemas for request/response validation
4. Set up directory structure for import strategies

### Phase 2: Core Implementation

**Tasks:**

1. Implement BaseImportStrategy abstract class
2. Migrate StudentImportService to StudentImportStrategy
3. Migrate SchoolImportService to SchoolImportStrategy
4. Migrate ClassroomImportService to ClassroomImportStrategy
5. Migrate TeacherAssignmentImportService to TeacherImportStrategy
6. Migrate ExcelImportService to ScoreImportStrategy

### Phase 3: Integration

**Tasks:**

1. Implement ImportOrchestrator to coordinate strategies
2. Create unified `/api/v1/import` endpoint
3. Add backward compatibility layer for existing endpoints
4. Create unified frontend import component
5. Update all frontend import UIs to use unified component

### Phase 4: Testing & Validation

**Tasks:**

1. Write unit tests for BaseImporter
2. Write unit tests for each strategy
3. Write integration tests for ImportOrchestrator
4. Write integration tests for unified API endpoint
5. Test all existing import functionality through new system

---

## STEP-BY-STEP TASKS

IMPORTANT: Execute every task in order, top to bottom. Each task is atomic and independently testable.

### Task Format Guidelines

Use information-dense keywords for clarity:

- **CREATE**: New files or components
- **UPDATE**: Modify existing files
- **ADD**: Insert new functionality into existing code
- **REMOVE**: Delete deprecated code
- **REFACTOR**: Restructure without changing behavior
- **MIRROR**: Copy pattern from elsewhere in codebase
- **MIGRATE**: Move existing code to new structure

### Phase 1: Foundation

#### 1. CREATE `backend/app/services/import_base.py`

- **IMPLEMENT**: BaseImporter class with common Excel parsing methods
- **PATTERN**: Mirror from `student_import_service.py:86-113`
- **IMPORTS**:
  ```python
  from openpyxl import load_workbook
  from typing import Any, Dict, List, Optional, Tuple
  from pathlib import Path
  import logging
  ```
- **METHODS**:
  - `parse_excel_headers(file_path: Path) -> Tuple[List[str], Dict[str, int]]`
  - `normalize_header(header: Optional[str]) -> str`
  - `build_column_indices(headers: List[str], column_mapping: Dict[str, str]) -> Dict[str, int]`
  - `validate_required_columns(column_indices: Dict[str, int], required_fields: List[str]) -> Optional[str]`
  - `extract_row_data(row: Tuple, column_indices: Dict[str, int], row_number: int) -> Dict[str, Any]`
- **GOTCHA**: Use `read_only=True, data_only=True` for performance with large files
- **VALIDATE**: `python -m pytest backend/tests/test_import_base.py -v`

#### 2. CREATE `backend/app/services/import_strategies/__init__.py`

- **IMPLEMENT**: Strategy package initialization
- **IMPORTS**: Export all strategy classes
- **PATTERN**: Mirror from `backend/app/services/__init__.py`
- **VALIDATE**: `python -c "from backend.app.services.import_strategies import StudentImportStrategy"`

#### 3. CREATE `backend/app/services/import_strategies/base_strategy.py`

- **IMPLEMENT**: BaseImportStrategy abstract base class
- **IMPORTS**:
  ```python
  from abc import ABC, abstractmethod
  from sqlalchemy.ext.asyncio import AsyncSession
  from typing import Any, Dict, List, Optional, Callable, Awaitable
  ```
- **ABSTRACT METHODS**:
  - `get_column_mapping() -> Dict[str, str]`
  - `get_required_columns() -> List[str]`
  - `validate_record(db: AsyncSession, record: Dict[str, Any], context: Dict[str, Any]) -> Tuple[bool, Optional[str], Optional[Dict[str, Any]]]`
  - `import_record(db: AsyncSession, validated_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]`
- **CONCRETE METHODS**:
  - `parse_excel(file_path: Path) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]`
  - `validate_all_records(db: AsyncSession, records: List[Dict[str, Any]], context: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]`
  - `import_all_records(db: AsyncSession, validated_records: List[Dict[str, Any]], context: Dict[str, Any], progress_callback: Optional[Callable] = None) -> Dict[str, Any]`
- **PATTERN**: Mirror interface from `student_import_service.py:73-213` (parse), `:216-256` (validate), `:420-592` (import)
- **GOTCHA**: Use TypeVar for generic record types if needed
- **VALIDATE**: `python -c "from backend.app.services.import_strategies.base_strategy import BaseImportStrategy; print(BaseImportStrategy.__abstractmethods__)">/dev/null`

#### 4. CREATE `backend/app/schemas/import.py`

- **IMPLEMENT**: Pydantic schemas for import requests/responses
- **IMPORTS**:
  ```python
  from pydantic import BaseModel
  from typing import List, Optional, Dict, Any, Literal
  from enum import Enum
  ```
- **SCHEMAS**:
  - `ImportStrategyType(str, Enum)`: STUDENT, TEACHER, CLASSROOM, SCHOOL, SCORE
  - `ImportRequest(BaseModel)`: strategy_type, file, context (dict)
  - `ImportResult(BaseModel)`: total, success, failed, created, updated, skipped, errors
  - `ImportError(BaseModel)`: row, field, message
  - `ImportContext(BaseModel)`: Flexible dict for strategy-specific context (exam_id, school_id, etc.)
- **PATTERN**: Mirror from `backend/app/schemas/user.py` or similar schema files
- **VALIDATE**: `python -c "from backend.app.schemas.import import ImportRequest; print(ImportRequest.schema_json())">/dev/null`

### Phase 2: Core Implementation

#### 5. MIGRATE `backend/app/services/import_strategies/student_import_strategy.py`

- **IMPLEMENT**: StudentImportStrategy class inheriting BaseImportStrategy
- **PATTERN**: Mirror from `student_import_service.py:1-592`
- **SOURCE METHODS TO MIGRATE**:
  - Lines 39-67: `COLUMN_MAPPING` → `get_column_mapping()`
  - Lines 70: `REQUIRED_COLUMNS` → `get_required_columns()`
  - Lines 216-256: `parse_classroom_code()` → keep as static method
  - Lines 259-286: `find_region()` → implement in `validate_record()`
  - Lines 289-325: `find_school()` → implement in `validate_record()`
  - Lines 328-397: `find_classroom()` → implement in `validate_record()`
  - Lines 400-417: `find_student()` → implement in `validate_record()`
  - Lines 420-592: `import_student_exam_mappings()` → implement in `import_record()`
- **CONTEXT PARAMETERS**: `exam_id` (required)
- **GOTCHA**: Preserve caching pattern (region_cache, school_cache) in `import_all_records()`
- **VALIDATE**: `python -m pytest backend/tests/test_import_strategies.py::test_student_import -v`

#### 6. MIGRATE `backend/app/services/import_strategies/school_import_strategy.py`

- **IMPLEMENT**: SchoolImportStrategy class
- **PATTERN**: Mirror from `school_import_service.py:1-487`
- **SOURCE METHODS TO MIGRATE**:
  - Lines 31-63: `COLUMN_MAPPING` → `get_column_mapping()`
  - Lines 66: `REQUIRED_COLUMNS` → `get_required_columns()`
  - Lines 193-244: `find_or_create_region()` → implement in `validate_record()`
  - Lines 247-330: `find_or_create_school()` → implement in `import_record()`
  - Lines 352-362: `_infer_region_level()` → static method
  - Lines 333-390: `_generate_region_code()`, `_generate_school_code()` → static methods
- **CONTEXT PARAMETERS**: `auto_create_region` (optional, default True)
- **GOTCHA**: Auto-create pattern differs from other strategies
- **VALIDATE**: `python -m pytest backend/tests/test_import_strategies.py::test_school_import -v`

#### 7. MIGRATE `backend/app/services/import_strategies/classroom_import_strategy.py`

- **IMPLEMENT**: ClassroomImportStrategy class
- **PATTERN**: Mirror from `classroom_import_service.py:1-623`
- **SOURCE METHODS TO MIGRATE**:
  - Lines 35-74: `DISTRICT_COLUMN_MAPPING` and `SCHOOL_COLUMN_MAPPING` → `get_column_mapping()` uses context to choose
  - Lines 111-114: `DISTRICT_REQUIRED_COLUMNS` and `SCHOOL_REQUIRED_COLUMNS` → `get_required_columns()` uses context
  - Lines 117-254: `parse_classroom_excel()` → use base class `parse_excel()`
  - Lines 257-312: `parse_classroom_code()` → static method
  - Lines 315-329: `find_grade_by_level()` → implement in `validate_record()`
  - Lines 332-343: `generate_classroom_name()` → static method
  - Lines 346-392: `find_school()` → implement in `validate_record()`
  - Lines 395-623: `import_classrooms()` → implement in `import_record()`
- **CONTEXT PARAMETERS**: `school_id` (optional for school admin), `region_id` (optional), `update_existing` (bool), `enrollment_year` (optional), `capacity` (optional)
- **GOTCHA**: Dual-mode mapping based on `is_school_admin` context flag
- **VALIDATE**: `python -m pytest backend/tests/test_import_strategies.py::test_classroom_import -v`

#### 8. MIGRATE `backend/app/services/import_strategies/teacher_import_strategy.py`

- **IMPLEMENT**: TeacherImportStrategy class
- **PATTERN**: Mirror from `teacher_assignment_import_service.py:1-1386`
- **SOURCE METHODS TO MIGRATE**:
  - Lines 44-92: `COLUMN_MAPPING` → `get_column_mapping()`
  - Lines 95-200: `parse_assignment_excel()` → use base class `parse_excel()` with custom header detection
  - Lines 200-1386: All validation and import logic → implement in `validate_record()` and `import_record()`
- **CONTEXT PARAMETERS**: None required, but may include options for teacher auto-creation
- **GOTCHA**: Most complex strategy with multiple entity lookups (teacher, school, grade, classroom, subject, semester)
- **GOTCHA**: Uses `pypinyin` for Chinese text processing
- **VALIDATE**: `python -m pytest backend/tests/test_import_strategies.py::test_teacher_import -v`

#### 9. MIGRATE `backend/app/services/import_strategies/score_import_strategy.py`

- **IMPLEMENT**: ScoreImportStrategy class
- **PATTERN**: Mirror from `excel_import_service.py:1-472`
- **SOURCE METHODS TO MIGRATE**:
  - Lines 40-68: `COLUMN_MAPPING` → `get_column_mapping()`
  - Lines 71: `REQUIRED_COLUMNS` → `get_required_columns()`
  - Lines 74-188: `parse_excel_file()` → use base class `parse_excel()`
  - Lines 191-280: `validate_record()` → implement
  - Lines 283-390: `import_scores()` → implement in `import_record()`
  - Lines 393-472: `process_import_task()` → NOT needed, handled by orchestrator
- **CONTEXT PARAMETERS**: `exam_id` (required), `task_id` (optional for progress tracking)
- **GOTCHA**: Only strategy with progress tracking - preserve callback pattern
- **VALIDATE**: `python -m pytest backend/tests/test_import_strategies.py::test_score_import -v`

### Phase 3: Integration

#### 10. CREATE `backend/app/services/import_orchestrator.py`

- **IMPLEMENT**: ImportOrchestrator class
- **IMPORTS**:
  ```python
  from sqlalchemy.ext.asyncio import AsyncSession
  from typing import Dict, Any, Optional, Callable, Awaitable
  from .import_strategies import *
  ```
- **METHODS**:
  - `__init__(self)`: Register all strategies
  - `get_strategy(strategy_type: ImportStrategyType) -> BaseImportStrategy`
  - `execute_import(db: AsyncSession, strategy_type: ImportStrategyType, file_path: Path, context: Dict[str, Any], progress_callback: Optional[Callable] = None) -> Dict[str, Any]`
- **LOGIC**:
  - Select strategy based on strategy_type
  - Call strategy.parse_excel()
  - Call strategy.validate_all_records()
  - Call strategy.import_all_records() with progress_callback
  - Return unified result format
- **PATTERN**: Orchestrator pattern - coordinates strategies without knowing implementation details
- **GOTCHA**: Handle unknown strategy_type gracefully
- **VALIDATE**: `python -m pytest backend/tests/test_import_orchestrator.py -v`

#### 11. CREATE `backend/app/api/v1/import.py`

- **IMPLEMENT**: Unified import API endpoint
- **IMPORTS**:
  ```python
  from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, BackgroundTasks
  from sqlalchemy.ext.asyncio import AsyncSession
  from ..schemas.import import ImportRequest, ImportResult
  from ...services.import_orchestrator import ImportOrchestrator
  from ...core.database import get_db
  import aiofiles
  import tempfile
  from pathlib import Path
  ```
- **ENDPOINTS**:
  - `POST /api/v1/import`: Main import endpoint
    - Request: UploadFile + strategy_type + context (form data)
    - Response: ImportResult
    - Logic: Save temp file → call orchestrator → delete temp file → return result
  - `GET /api/v1/import/strategies`: List available strategies
    - Response: List[str] of strategy names
  - `GET /api/v1/import/template/{strategy_type}`: Download Excel template
    - Response: File download
- **PATTERN**: Mirror from existing endpoints but generalized
- **GOTCHA**: Clean up temp files even on exception
- **GOTCHA**: Use `aiofiles` for async file operations
- **VALIDATE**: `curl -X POST http://localhost:8000/api/v1/import -F "file=@test.xlsx" -F "strategy_type=student" -F "context={\"exam_id\": 1}"`

#### 12. UPDATE `backend/app/api/v1/__init__.py`

- **ADD**: Include new import router
- **PATTERN**: Mirror existing router inclusions
- **LINE**: After other router imports, add: `from . import import`
- **VALIDATE**: `curl http://localhost:8000/docs | grep "/api/v1/import"`

#### 13. CREATE `frontend/src/components/Import/UnifiedImportModal.vue`

- **IMPLEMENT**: Unified import modal component
- **PROPS**:
  - `strategyType`: ImportStrategyType enum
  - `context`: Object for strategy-specific parameters
  - `title`: String (optional)
- **FEATURES**:
  - File upload with drag-and-drop
  - Template download button
  - Progress bar during import
  - Error display with row numbers
  - Success summary
- **PATTERN**: Mirror from `SchoolManagementCard.vue` import dialog (lines with "批量导入学校")
- **IMPORTS**:
  ```typescript
  import { ref } from 'vue'
  import { ElMessage } from 'element-plus'
  import { useImport } from '@/composables/useImport'
  import type { ImportResult } from '@/types/import'
  ```
- **GOTCHA**: Handle different context requirements per strategy type
- **VALIDATE**: Open Storybook or manually test in browser

#### 14. CREATE `frontend/src/services/import.ts`

- **IMPLEMENT**: Unified import API service
- **METHODS**:
  - `executeImport(strategyType: string, file: File, context: any): Promise<ImportResult>`
  - `downloadTemplate(strategyType: string): Promise<Blob>`
  - `getAvailableStrategies(): Promise<string[]>`
- **PATTERN**: Mirror from `frontend/src/services/admin.ts`
- **IMPORTS**: Axios or fetch API
- **VALIDATE**: `npm run type-check`

#### 15. CREATE `frontend/src/composables/useImport.ts`

- **IMPLEMENT**: Import composable with common logic
- **FEATURES**:
  - `importState`: reactive state (idle, uploading, importing, completed, error)
  - `importProgress`: 0-100
  - `importResult`: ImportResult or null
  - `importErrors`: ImportError[]
  - `executeImport()`: Main import function
  - `downloadTemplate()`: Template download
  - `resetState()`: Reset state
- **PATTERN**: Mirror from `frontend/src/composables/useToast.ts`
- **VALIDATE**: `npm run type-check`

#### 16. UPDATE `frontend/src/pages/Admin/OrganizationManagement/SchoolManagementCard.vue`

- **REFACTOR**: Replace existing import dialog with UnifiedImportModal
- **FIND**: Lines with "批量导入学校" dialog
- **REPLACE**: With `<UnifiedImportModal strategy-type="school" :context="{ auto_create_region: true }" />`
- **REMOVE**: Old import methods (`openSchoolImportDialog`, `downloadSchoolTemplate`, `startSchoolImport`)
- **VALIDATE**: Manual testing - import school data

#### 17. UPDATE `frontend/src/pages/Admin/OrganizationManagement/TeacherAssignmentCard.vue`

- **REFACTOR**: Replace existing import dialog with UnifiedImportModal
- **FIND**: Lines with "批量导入教学任务" dialog
- **REPLACE**: With `<UnifiedImportModal strategy-type="teacher" :context="{}" />`
- **REMOVE**: Old import methods
- **GOTCHA**: Preserve "export created teachers" feature if needed
- **VALIDATE**: Manual testing - import teacher assignments

#### 18. UPDATE `frontend/src/pages/DistrictExamAdmin/StudentImport.vue`

- **REFACTOR**: Replace entire page with UnifiedImportModal
- **REPLACE**: Page content with `<UnifiedImportModal strategy-type="student" :context="{ exam_id: examId }" />`
- **GOTCHA**: Extract examId from route params
- **VALIDATE**: Manual testing - import student exam mappings

### Phase 4: Backward Compatibility & Testing

#### 19. CREATE `backend/app/api/v1/legacy_import.py`

- **IMPLEMENT**: Legacy endpoints as proxy to unified endpoint
- **ENDPOINTS**:
  - `POST /api/v1/users/batch-import` → Proxy to `/api/v1/import` with strategy=student
  - `POST /api/v1/teachers/assignments/import` → Proxy to `/api/v1/import` with strategy=teacher
  - `POST /api/v1/exams/{exam_id}/students/import` → Proxy to `/api/v1/import` with strategy=student
  - `POST /api/v1/classrooms/import` → Proxy to `/api/v1/import` with strategy=classroom
  - `POST /api/v1/schools/import` → Proxy to `/api/v1/import` with strategy=school
- **PURPOSE**: Maintain backward compatibility for existing clients
- **PATTERN**: Adapter pattern - adapts old API to new unified API
- **VALIDATE**: Test existing import functionality still works

#### 20. CREATE `backend/tests/test_import_base.py`

- **IMPLEMENT**: Unit tests for BaseImporter
- **TEST CASES**:
  - `test_normalize_header()`: Test header normalization (strip, remove asterisks)
  - `test_build_column_indices()`: Test column mapping
  - `test_validate_required_columns()`: Test required column validation
  - `test_extract_row_data()`: Test row data extraction
- **PATTERN**: Mirror from existing test files in `backend/tests/`
- **IMPORTS**:
  ```python
  import pytest
  from backend.app.services.import_base import BaseImporter
  from openpyxl import Workbook
  import tempfile
  ```
- **VALIDATE**: `python -m pytest backend/tests/test_import_base.py -v`

#### 21. CREATE `backend/tests/test_import_strategies.py`

- **IMPLEMENT**: Unit tests for all strategies
- **TEST CASES**:
  - `test_student_import_strategy()`: Test student import with mock database
  - `test_school_import_strategy()`: Test school import with region auto-creation
  - `test_classroom_import_strategy()`: Test classroom import (both modes)
  - `test_teacher_import_strategy()`: Test teacher assignment import
  - `test_score_import_strategy()`: Test score import
- **PATTERN**: Use pytest-asyncio for async tests
- **FIXTURES**: Mock database session, mock Excel files
- **VALIDATE**: `python -m pytest backend/tests/test_import_strategies.py -v`

#### 22. CREATE `backend/tests/test_import_orchestrator.py`

- **IMPLEMENT**: Integration tests for orchestrator
- **TEST CASES**:
  - `test_orchestrator_student_import()`: End-to-end student import
  - `test_orchestrator_school_import()`: End-to-end school import
  - `test_orchestrator_invalid_strategy()`: Test error handling
  - `test_orchestrator_progress_callback()`: Test progress tracking
- **PATTERN**: Integration test with real database (test database)
- **FIXTURES**: Test database setup/teardown
- **VALIDATE**: `python -m pytest backend/tests/test_import_orchestrator.py -v`

#### 23. CREATE `backend/tests/test_import_api.py`

- **IMPLEMENT**: API endpoint tests
- **TEST CASES**:
  - `test_unified_import_endpoint()`: Test POST /api/v1/import
  - `test_get_strategies_endpoint()`: Test GET /api/v1/import/strategies
  - `test_template_download_endpoint()`: Test GET /api/v1/import/template/{type}
  - `test_legacy_endpoints()`: Test backward compatibility
- **PATTERN**: Use FastAPI TestClient
- **IMPORTS**:
  ```python
  from fastapi.testclient import TestClient
  from backend.app.main import app
  ```
- **VALIDATE**: `python -m pytest backend/tests/test_import_api.py -v`

#### 24. REMOVE deprecated import service files

- **DELETE**: `backend/app/services/student_import_service.py` (after verifying migration)
- **DELETE**: `backend/app/services/teacher_assignment_import_service.py` (after verifying migration)
- **DELETE**: `backend/app/services/classroom_import_service.py` (after verifying migration)
- **DELETE**: `backend/app/services/school_import_service.py` (after verifying migration)
- **DELETE**: `backend/app/services/excel_import_service.py` (after verifying migration)
- **GOTCHA**: Only delete after all tests pass and backward compatibility verified
- **VALIDATE**: `grep -r "StudentImportService\|TeacherAssignmentImportService\|ClassroomImportService\|SchoolImportService\|ExcelImportService" backend/app --exclude-dir=.git` (should return nothing)

---

## TESTING STRATEGY

### Unit Tests

**Scope:**
- BaseImporter class methods
- Individual strategy classes
- Orchestrator logic
- API endpoint handlers

**Framework:** pytest with pytest-asyncio

**Pattern:** Mirror existing tests in `backend/tests/`

**Fixtures Required:**
- Mock database session
- Sample Excel files (valid/invalid formats)
- Mock entity data (regions, schools, classrooms, users)

### Integration Tests

**Scope:**
- End-to-end import workflows
- Strategy selection and execution
- Progress tracking
- Error handling and rollback

**Database:** Use test database (SQLite or test PostgreSQL)

**Test Cases:**
- Import 100 students → verify all created in database
- Import with 50% invalid data → verify error reporting
- Import duplicate data → verify update vs skip behavior
- Import with progress callback → verify progress updates

### Edge Cases

**Test Cases:**
- Empty Excel file
- Excel with no headers
- Excel with missing required columns
- Excel with invalid data types (text in numeric fields)
- Excel with duplicate rows
- Excel with special characters in text fields
- Very large Excel files (10,000+ rows)
- Concurrent imports (multiple users importing simultaneously)
- Database connection failure during import
- File system errors (permissions, disk full)

### Frontend Tests

**Framework:** Vitest (project standard)

**Test Cases:**
- UnifiedImportModal renders correctly
- File upload triggers correct API call
- Template download works
- Progress bar updates correctly
- Errors display with row numbers
- Component handles different strategy types

---

## VALIDATION COMMANDS

Execute every command to ensure zero regressions and 100% feature correctness.

### Level 1: Syntax & Style

```bash
# Backend: Black formatting
cd backend
black app/services/import_base.py
black app/services/import_strategies/
black app/services/import_orchestrator.py
black app/api/v1/import.py
black app/schemas/import.py

# Backend: Flake8 linting
flake8 app/services/import_base.py
flake8 app/services/import_strategies/
flake8 app/services/import_orchestrator.py
flake8 app/api/v1/import.py
flake8 app/schemas/import.py

# Frontend: Type checking
cd frontend
pnpm type-check
```

### Level 2: Unit Tests

```bash
# Backend unit tests
cd backend
pytest tests/test_import_base.py -v
pytest tests/test_import_strategies.py -v
pytest tests/test_import_orchestrator.py -v
pytest tests/test_import_api.py -v

# Frontend unit tests
cd frontend
npm test
```

### Level 3: Integration Tests

```bash
# Backend integration tests
cd backend
pytest tests/test_import_integration.py -v

# Test all import types end-to-end
pytest tests/test_import_e2e.py -v
```

### Level 4: Manual Validation

**Test Student Import:**
1. Navigate to Exam Admin page
2. Click "Import Students"
3. Download template
4. Fill template with test data (10 students)
5. Upload file
6. Verify progress bar updates
7. Verify success message
8. Verify students appear in database

**Test School Import:**
1. Navigate to Organization Management
2. Click School Management card
3. Click "Import Schools"
4. Download template
5. Fill template with test data (5 schools)
6. Upload file
7. Verify schools created
8. Verify regions auto-created

**Test Teacher Assignment Import:**
1. Navigate to Organization Management
2. Click Teacher Assignments card
3. Click "Import Assignments"
4. Download template
5. Fill template with test data
6. Upload file
7. Verify assignments created
8. Verify teachers auto-created if needed

**Test Error Handling:**
1. Upload Excel with missing required columns → Verify error message
2. Upload Excel with invalid data → Verify specific error messages with row numbers
3. Upload Excel with duplicate data → Verify correct behavior (update/skip)
4. Upload non-Excel file → Verify file type error

**Test Backward Compatibility:**
1. Test old `/api/v1/users/batch-import` endpoint → Should still work
2. Test old `/api/v1/schools/import` endpoint → Should still work
3. Test old `/api/v1/classrooms/import` endpoint → Should still work

### Level 5: Additional Validation

**Performance Testing:**
```bash
# Test import performance with large files
cd backend
python scripts/benchmark_import.py --rows 10000 --strategy student
```

**Load Testing:**
```bash
# Test concurrent imports (if implemented)
ab -n 100 -c 10 -p import_request.json http://localhost:8000/api/v1/import
```

---

## ACCEPTANCE CRITERIA

- [ ] Feature implements all specified functionality
- [ ] All validation commands pass with zero errors
- [ ] Unit test coverage meets requirements (80%+)
- [ ] Integration tests verify end-to-end workflows
- [ ] Code follows project conventions and patterns
- [ ] No regressions in existing functionality
- [ ] Documentation is updated (if applicable)
- [ ] Performance meets requirements (import 1000 rows in <30 seconds)
- [ ] Security considerations addressed (file validation, SQL injection prevention)

**Specific Acceptance Criteria:**

1. **BaseImporter Class**
   - [ ] Common Excel parsing methods implemented
   - [ ] Header normalization works with various formats
   - [ ] Column mapping supports multiple aliases
   - [ ] Row data extraction handles missing values

2. **Import Strategies**
   - [ ] All 5 strategies migrated successfully
   - [ ] Each strategy implements required abstract methods
   - [ ] Column mappings preserved from original services
   - [ ] Validation logic preserved
   - [ ] Import logic preserved

3. **Import Orchestrator**
   - [ ] Selects correct strategy based on type
   - [ ] Coordinates import process
   - [ ] Handles errors gracefully
   - [ ] Supports progress tracking

4. **Unified API Endpoint**
   - [ ] `/api/v1/import` accepts all import types
   - [ ] Returns consistent result format
   - [ ] Handles file uploads correctly
   - [ ] Cleans up temp files

5. **Frontend Unified Import Component**
   - [ ] Works for all import types
   - [ ] File upload with drag-and-drop
   - [ ] Template download
   - [ ] Progress tracking
   - [ ] Error display with row numbers
   - [ ] Success summary

6. **Backward Compatibility**
   - [ ] All old API endpoints still work
   - [ ] Existing frontend pages work unchanged
   - [ ] No breaking changes for API clients

7. **Code Quality**
   - [ ] Total lines reduced by ~58% (3560 → 1500)
   - [ ] No code duplication in Excel parsing
   - [ ] Consistent error handling
   - [ ] All tests passing
   - [ ] Black formatted
   - [ ] Flake8 clean

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
- [ ] Old service files deleted (after verification)
- [ ] Documentation updated

---

## NOTES

**Design Decisions:**

1. **Strategy vs Template Pattern**: Chose Strategy pattern over Template Method because import types have significantly different validation and import logic, not just different steps in the same process.

2. **Orchestrator Pattern**: Added orchestrator to decouple API layer from strategy selection logic, making it easier to add new import types in future.

3. **Backward Compatibility**: Maintained all old API endpoints as proxies to avoid breaking existing clients (frontend, mobile apps, external integrations).

4. **Progress Tracking**: Only score import currently has progress tracking via callback. Other imports can be enhanced later if needed (orchestrator already supports callback parameter).

5. **Error Handling**: Chose to return error dicts instead of raising exceptions for validation errors because we need to collect all errors and return them together, not fail on first error.

6. **Context Parameters**: Used flexible dict for context instead of fixed parameters to allow strategy-specific context without breaking the interface.

**Trade-offs:**

1. **Complexity vs Flexibility**: The new system is more complex (more files, more abstraction) but much more flexible and maintainable. Worth it for a system of this size.

2. **Migration Risk**: Full migration is risky but maintaining duplicate code is worse. Mitigated by comprehensive tests and backward compatibility layer.

3. **Performance**: Slight overhead from abstraction layer but negligible compared to I/O (Excel parsing, database operations).

**Future Enhancements:**

1. **Async Import**: Add background task support for large imports using Celery or FastAPI BackgroundTasks
2. **Import History**: Track all imports in database for audit trail
3. **Rollback Support**: Ability to rollback an import batch
4. **Import Templates**: Generate templates dynamically based on strategy
5. **Validation Rules**: Configurable validation rules per strategy
6. **Import Scheduling**: Schedule imports for specific times
7. **Multi-sheet Excel**: Support importing from multiple sheets in one file
8. **CSV Support**: Extend beyond Excel to support CSV files

**Known Limitations:**

1. **Memory Usage**: Large Excel files (10,000+ rows) loaded entirely into memory during parsing. Could use streaming for better performance.
2. **Transaction Size**: All imports in single transaction. Very large imports could exceed transaction limits.
3. **Lock Contention**: Concurrent imports to same entities could cause lock contention.
4. **Template Validation**: No validation that uploaded Excel matches expected template format before parsing.

---

**Created**: 2026-01-16
**Status**: Ready for Implementation
**Estimated Confidence Score**: 9/10 for one-pass implementation success
