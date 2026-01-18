"""
Import Schemas

Pydantic schemas for unified import API requests and responses.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum


class ImportStrategyType(str, Enum):
    """Import strategy types"""
    SCHOOL = "school"
    CLASSROOM = "classroom"
    STUDENT = "student"
    STUDENT_ACCOUNT = "student_account"
    TEACHER = "teacher"
    CITY_EXAM_NUMBER = "city_exam_number"


class ImportError(BaseModel):
    """Import error details"""
    row: int = Field(..., description="Row number (1-indexed, or 'unknown')")
    field: Optional[str] = Field(None, description="Field name that caused error")
    message: str = Field(..., description="Error message")

    class Config:
        from_attributes = True


class ImportResult(BaseModel):
    """Import result"""
    total: int = Field(..., description="Total records processed")
    success: int = Field(..., description="Successfully imported records")
    failed: int = Field(..., description="Failed records")
    created: int = Field(0, description="New records created")
    updated: int = Field(0, description="Existing records updated")
    skipped: int = Field(0, description="Records skipped (already exist)")
    errors: List[ImportError] = Field(
        default_factory=list,
        description="List of errors (limited to first 100)"
    )

    class Config:
        from_attributes = True


class SchoolImportResult(ImportResult):
    """School import result with additional fields"""
    created_regions: int = Field(0, description="Number of regions auto-created")


class TeacherImportResult(ImportResult):
    """Teacher import result with additional fields"""
    created_teachers: int = Field(0, description="Number of teachers auto-created")
    created_semesters: int = Field(0, description="Number of semesters auto-created")


# Legacy response schemas (for backward compatibility)

class SchoolImportError(BaseModel):
    """School import error (legacy format)"""
    row: int
    field: Optional[str] = None
    message: str


class SchoolImportResponse(BaseModel):
    """School import response (legacy format)"""
    total: int
    success: int
    failed: int
    created_regions: int = 0
    created_schools: int = 0
    updated_schools: int = 0
    skipped_schools: int = 0
    errors: List[SchoolImportError] = Field(default_factory=list)


class ClassroomImportResponse(BaseModel):
    """Classroom import response (legacy format)"""
    total: int
    success: int
    failed: int
    created: int = 0
    updated: int = 0
    skipped: int = 0
    errors: List[SchoolImportError] = Field(default_factory=list)
