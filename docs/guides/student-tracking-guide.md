# Student Tracking System Guide

## Overview

The student tracking system uses three identifiers to manage student data across schools, grades, and time:

1. **身份证号 (student_id_number)**: Permanent unique identifier
2. **用户名 (username)**: Login credential (school_code + ID last 6 digits)
3. **考号 (exam_number)**: Exam identifier (school + year + class + seat)

## Three Identifiers

### Identity Card Number (student_id_number)

**Format:** 18-digit standard Chinese ID number

**Purpose:**
- Permanent unique identifier for each student
- Primary key for cross-school tracking
- Used for grade association and value-added analysis
- Never changes

**Example:** `110101200501011234`
- Region code: 110101
- Birth date: 2005-01-01
- Check digits: 1234

**Storage:**
- `users.student_id_number` (primary table)
- `scores.student_id_number` (redundant, for traceability)
- `exam_number_mappings.student_id_number` (redundant)

### Username (username)

**Format:** `XXXXYYYYYY`
- XXXX: School code (4 digits)
- YYYYYY: Last 6 digits of student ID number

**Example:** `4401011234`
- School code: 4401
- Student ID: ...011234

**Conflict Handling:**
- Probability: ~0.0001% (extremely low)
- Resolution: Add letter suffix (A, B, C...)
- If A-Z exhausted, use numbers (0, 1, 2...)

**Examples:**
```
Student A: ID ending in 011234 → 4401011234
Student B: ID ending in 999999 → 4401999999
Student C: ID also ending in 011234 → 4401011234A (conflict)
Student D: Same conflict → 4401011234B
```

**Invariance:**
- Within same school: Remains constant
- After transfer: Updates to new school's username
- Historical data linked via student_id_number

### Exam Number (exam_number)

**Format:** `XXXXXXXXXXXXX` (12 digits)
- School code (4 digits)
- Enrollment year (4 digits)
- Class sequence (2 digits)
- Seat number (2 digits)

**Example:** `440120230101`
- School: 4401
- Enrollment year: 2023
- Class: 01
- Seat: 01

**Generation Modes:**
1. **Automatic:** System generates based on rules
2. **Manual:** Import via Excel with custom exam numbers

**Stability:**
- Same academic year: Usually stable
- Grade advancement: May remain the same
- Different exams: Can vary if needed

## API Usage

### Check Username Availability

Check if a username is available before creating a student account.

**Endpoint:** `GET /api/v1/admin/users/check-username`

**Parameters:**
- `school_code` (string): 4-digit school code
- `student_id_number` (string): 18-digit ID number

**Example:**
```bash
curl "http://localhost:8000/api/v1/admin/users/check-username?school_code=4401&student_id_number=110101200501011234"
```

**Response:**
```json
{
  "available": true,
  "username": "4401011234"
}
```

### Generate Exam Numbers

Batch generate exam numbers for all students in a school.

**Endpoint:** `POST /api/v1/admin/exams/generate-exam-numbers`

**Request Body:**
```json
{
  "exam_id": 1,
  "school_id": 1,
  "auto_generate": true
}
```

**Response:**
```json
{
  "generated": 1200,
  "exam_numbers": [
    {
      "student_id": 123,
      "exam_number": "440120230101"
    }
  ]
}
```

### Student Growth Analysis

Retrieve historical scores and growth data for a specific student.

**Endpoint:** `GET /api/v1/admin/analytics/student-growth/{student_id_number}`

**Parameters:**
- `student_id_number` (path): 18-digit ID number
- `subject_id` (query, optional): Filter by subject

**Example:**
```bash
curl "http://localhost:8000/api/v1/admin/analytics/student-growth/110101200501011234?subject_id=1"
```

**Response:**
```json
[
  {
    "exam_name": "2023 Midterm Exam",
    "exam_date": "2023-11-15",
    "raw_score": 85,
    "school": "School 44",
    "growth": null
  },
  {
    "exam_name": "2024 Final Exam",
    "exam_date": "2024-01-20",
    "raw_score": 90,
    "school": "School 55",
    "growth": 5
  }
]
```

### Value-Added Report

Generate aggregate value-added analysis for a group of students.

**Endpoint:** `POST /api/v1/admin/analytics/value-added-report`

**Request Body:**
```json
{
  "exam_start_id": 1,
  "exam_end_id": 2,
  "school_id": 1,
  "grade_id": 7,
  "subject_id": 1
}
```

**Response:**
```json
{
  "summary": {
    "total_students": 300,
    "avg_growth": 5.2,
    "positive_growth": 240,
    "negative_growth": 60
  },
  "students": [
    {
      "student_id_number": "110101200501011234",
      "student_name": "Zhang San",
      "current_school": "School 44",
      "scores": [
        {"exam_id": 1, "score": 85},
        {"exam_id": 2, "score": 90}
      ],
      "total_growth": 5
    }
  ]
}
```

## Data Migration

Run migration scripts in the following order to upgrade existing data.

### Prerequisites

```bash
cd backend
source venv/bin/activate  # REQUIRED before running migrations
```

### Step 1: Migrate Classroom Codes

Convert classroom codes from grade-based (e.g., "701") to enrollment-based (e.g., "2301").

```bash
python scripts/migrate_classroom_codes.py
```

**Before:**
- Classroom code: "701" (Grade 7, Class 01)
- Contains grade info (redundant with grade_id)

**After:**
- Classroom code: "2301" (Enrolled 2023, Class 01)
- No redundancy with grade_id

### Step 2: Migrate Usernames

Regenerate all usernames according to the new format (school_code + ID last 6 digits).

```bash
python scripts/migrate_usernames.py
```

**What it does:**
- Generates new usernames for all students
- Handles conflicts with letter suffixes
- Updates users table in bulk
- Logs all changes for audit

### Step 3: Initialize Seat Numbers

Assign sequential seat numbers to students within each classroom.

```bash
python scripts/initialize_seat_numbers.py
```

**What it does:**
- Orders students by ID within each classroom
- Assigns seat numbers 1, 2, 3, ...
- Ensures no duplicate seat numbers in same classroom

### Verification

After migration, verify data integrity:

```bash
# Check for duplicate usernames
python -c "
from backend.app.database import SessionLocal
from backend.app.models import User

db = SessionLocal()
duplicates = db.execute('''
    SELECT username, COUNT(*) as count
    FROM users
    GROUP BY username
    HAVING COUNT(*) > 1
''').fetchall()

if duplicates:
    print('ERROR: Duplicate usernames found:', duplicates)
else:
    print('OK: No duplicate usernames')
"

# Check classroom code format
python -c "
from backend.app.database import SessionLocal
from backend.app.models import Classroom

db = SessionLocal()
invalid = db.execute('''
    SELECT code FROM classrooms
    WHERE code !~ '^\\d{4}$'
''').fetchall()

if invalid:
    print('ERROR: Invalid classroom codes:', invalid)
else:
    print('OK: All classroom codes valid')
"
```

## Student Import

### Excel Template Format

**Required Columns:**
- 学校名称 (School Name)
- 年级级别 (Grade Level)
- 班级编号 (Classroom Number)
- 身份证号 (Student ID Number)
- 姓名 (Name)

**Optional Columns:**
- 座位号 (Seat Number) - Auto-assigned if not provided

**Example:**

| 学校名称 | 年级级别 | 班级编号 | 身份证号 | 姓名 | 座位号 |
|---------|---------|---------|---------|------|--------|
| 四十四中 | 7 | 01班 | 110101200501011234 | 张三 | 01 |
| 四十四中 | 7 | 02班 | 110101200501019999 | 李四 | 02 |
| 四十四中 | 7 | 01班 | 110101200501018888 | 王五 | 03 |

### Import Process

1. **Prepare Excel file** with the required columns
2. **Upload** via admin interface
3. **System automatically:**
   - Creates/updates classrooms with new code format
   - Generates usernames (checks for conflicts)
   - Assigns seat numbers if not provided
   - Links to existing students by ID number

### Conflict Handling

**Duplicate Student ID:**
- Updates existing student's classroom and username
- Preserves historical score data

**Username Conflict:**
- Adds letter suffix (A, B, C...)
- Logs conflict for review

## Exam Number Import

### Excel Template Format

**Required Columns:**
- 身份证号 (Student ID Number)
- 考试ID (Exam ID)

**Optional Columns:**
- 考号 (Exam Number) - Auto-generated if not provided

**Example:**

| 考号 | 身份证号 | 姓名 | 考试ID |
|-----------|---------|------|--------|
| 440120230101 | 110101200501011234 | 张三 | 1 |
| | 110101200501019999 | 李四 | 1 |

If exam number is not provided, system generates:
```
{school_code}{enrollment_year}{class_sequence}{seat_number:02d}
Example: 440120230101
```

## Cross-School Student Tracking

### Scenario: Student Transfer

When a student transfers from School A to School B:

1. **Username updates** to new school's format
2. **Student ID number remains unchanged**
3. **Historical scores preserved** and linked via ID number
4. **Growth analysis includes** both schools' data

### Query Example

```python
# Get all scores for a student across schools
scores = db.query(Score).join(Exam).filter(
    Score.student_id_number == "110101200501011234"
).order_by(Exam.exam_date).all()

# Result includes scores from both schools
for score in scores:
    print(f"{score.exam.exam_date}: {score.raw_score} at {score.student.school.name}")
```

## Best Practices

### For Administrators

1. **Always verify student ID numbers** before import
2. **Check username availability** for bulk operations
3. **Backup data** before running migration scripts
4. **Test migration** in staging environment first

### For Developers

1. **Use student_id_number** for cross-school queries
2. **Handle username conflicts** gracefully with suffixes
3. **Validate ID number format** (18 digits, checksum)
4. **Index student_id_number** in all relevant tables

### For Data Analysts

1. **Join on student_id_number** for longitudinal analysis
2. **Filter by exam_date** for time-series studies
3. **Use value-added endpoints** for growth metrics
4. **Track school changes** for mobility analysis

## Troubleshooting

### Duplicate Username Error

**Problem:** Username already exists when creating student

**Solution:**
1. Check if student already exists with same ID number
2. Use conflict resolution endpoint to generate unique username
3. System will auto-add suffix (A, B, C...)

### Invalid Classroom Code

**Problem:** Classroom code not in 4-digit format

**Solution:**
1. Run classroom code migration script
2. Verify all codes match pattern: `^\d{4}$`
3. Update frontend validation to enforce format

### Missing Seat Numbers

**Problem:** Seat numbers not assigned after import

**Solution:**
1. Run seat number initialization script
2. Verify no duplicates within same classroom
3. Check that seat_number column exists in users table

### Broken Score Tracking

**Problem:** Scores not linking to students after transfer

**Solution:**
1. Verify scores.student_id_number is populated
2. Check that student_id_number matches users table
3. Use exam_number_mappings for exam-specific linking

## Related Documentation

- **Design Document:** `/docs/plans/2025-01-22-student-tracking-design.md`
- **API Documentation:** http://localhost:8000/docs
- **Database Schema:** `/backend/app/models/`

## Support

For issues or questions:
1. Check API documentation at /docs endpoint
2. Review migration logs in backend/logs/
3. Contact system administrator

---

**Last Updated:** 2025-01-22
**Version:** 1.0
