"""
教师教学任务管理 API

提供教师教学任务的CRUD操作接口
"""

from typing import Any, List, Optional, Dict, cast
from pathlib import Path
import tempfile
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.deps import get_current_admin
from app.models import User, TeacherTeachingAssignment
from app.schemas.teacher import (
    TeacherTeachingAssignmentCreate,
    TeacherTeachingAssignmentUpdate,
    TeacherTeachingAssignmentResponse,
    TeacherTeachingAssignmentListResponse,
    TeacherAssignmentImportResponse,
)
from app.services.teacher_service import TeacherService, TeacherServiceError
from app.services.teacher_assignment_import_service import (
    TeacherAssignmentImportService,
    TeacherAssignmentImportServiceError,
)

# 导入相关的 Response schemas
from app.api.v1.admin_organization import SchoolResponse, ClassroomResponse
from app.api.v1.admin_users import UserResponse
from app.schemas.curriculum import SubjectResponse, GradeResponse
from app.schemas.evaluation import SemesterResponse

router = APIRouter(prefix="/teachers", tags=["teachers"])


def _serialize_assignment(assignment: TeacherTeachingAssignment) -> Dict[str, Any]:
    """
    序列化教学任务对象为字典
    
    Args:
        assignment: 教学任务对象
        
    Returns:
        序列化后的字典
    """
    # 处理 assignment_type：如果为 None，尝试从 position_type 推导
    assignment_type_value = None
    if assignment.assignment_type:
        assignment_type_value = assignment.assignment_type.value if hasattr(assignment.assignment_type, 'value') else str(assignment.assignment_type)
    else:
        # 从 position_type 推导 assignment_type（向后兼容）
        # 使用 getattr 安全访问，避免触发懒加载
        position_type = getattr(assignment, 'position_type', None)
        if position_type:
            position_code = getattr(position_type, 'code', None)
            if position_code == "head_teacher":
                assignment_type_value = "head_teacher"
            elif position_code == "subject_teacher":
                assignment_type_value = "subject_teacher"
    
    # 序列化关联对象（使用 getattr 安全访问，避免触发懒加载）
    teacher_dict = None
    teacher = getattr(assignment, 'teacher', None)
    if teacher:
        teacher_dict = {
            "id": cast(int, teacher.id),
            "username": cast(str, teacher.username),
            "email": cast(str, teacher.email),
            "full_name": getattr(teacher, 'full_name', None),
            "role": str(teacher.role.value) if hasattr(teacher.role, 'value') else str(teacher.role),
        }
    
    school_dict = None
    school = getattr(assignment, 'school', None)
    if school:
        school_dict = SchoolResponse.model_validate(school).model_dump()
    
    grade_dict = None
    grade = getattr(assignment, 'grade', None)
    if grade:
        grade_dict = GradeResponse.model_validate(grade).model_dump()
    
    classroom_dict = None
    classroom = getattr(assignment, 'classroom', None)
    if classroom:
        classroom_dict = ClassroomResponse.model_validate(classroom).model_dump()
    
    subject_dict = None
    subject = getattr(assignment, 'subject', None)
    if subject:
        subject_dict = SubjectResponse.model_validate(subject).model_dump()
    
    semester_dict = None
    semester = getattr(assignment, 'semester', None)
    if semester:
        semester_dict = SemesterResponse.model_validate(semester).model_dump()
    
    return {
        "id": cast(int, assignment.id),
        "teacher_id": cast(int, assignment.teacher_id),
        "school_id": cast(int, assignment.school_id),
        "grade_id": cast(int, assignment.grade_id),
        "classroom_id": cast(int, assignment.classroom_id),
        "subject_id": cast(int, assignment.subject_id),
        "semester_id": cast(int, assignment.semester_id),
        "academic_year": cast(str, assignment.academic_year),
        "assignment_type": assignment_type_value,
        "is_active": cast(bool, assignment.is_active),
        "created_at": assignment.created_at,
        "updated_at": assignment.updated_at,
        "teacher": teacher_dict,
        "school": school_dict,
        "grade": grade_dict,
        "classroom": classroom_dict,
        "subject": subject_dict,
        "semester": semester_dict,
    }


@router.post("/assignments", response_model=TeacherTeachingAssignmentResponse, status_code=201)
async def create_assignment(
    assignment_data: TeacherTeachingAssignmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Any:
    """创建教师教学任务"""
    try:
        assignment = await TeacherService.create_assignment(db, assignment_data)
        # 重新加载关联对象
        assignment = await TeacherService.get_assignment(db, cast(int, assignment.id))
        if not assignment:
            raise HTTPException(status_code=404, detail="创建的教学任务不存在")
        return TeacherTeachingAssignmentResponse.model_validate(_serialize_assignment(assignment))
    except TeacherServiceError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建教学任务失败: {str(e)}")


@router.get("/assignments", response_model=TeacherTeachingAssignmentListResponse)
async def list_assignments(
    teacher_id: Optional[int] = Query(None, description="教师ID筛选"),
    school_id: Optional[int] = Query(None, description="学校ID筛选"),
    grade_id: Optional[int] = Query(None, description="年级ID筛选"),
    classroom_id: Optional[int] = Query(None, description="班级ID筛选"),
    subject_id: Optional[int] = Query(None, description="学科ID筛选"),
    semester_id: Optional[int] = Query(None, description="学期ID筛选"),
    region_id: Optional[int] = Query(None, description="区域ID筛选"),
    is_active: Optional[bool] = Query(None, description="是否激活筛选"),
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=100, description="每页数量"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Any:
    """获取教学任务列表"""
    try:
        assignments, total = await TeacherService.list_assignments(
            db=db,
            teacher_id=teacher_id,
            school_id=school_id,
            grade_id=grade_id,
            classroom_id=classroom_id,
            subject_id=subject_id,
            semester_id=semester_id,
            region_id=region_id,
            is_active=is_active,
            page=page,
            size=size,
        )
        total_pages = (total + size - 1) // size
        
        # 序列化教学任务列表
        serialized_assignments = [
            TeacherTeachingAssignmentResponse.model_validate(_serialize_assignment(assignment))
            for assignment in assignments
        ]
        
        return TeacherTeachingAssignmentListResponse(
            assignments=serialized_assignments,
            total=total,
            page=page,
            size=size,
            total_pages=total_pages,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取教学任务列表失败: {str(e)}")


@router.get("/assignments/{assignment_id}", response_model=TeacherTeachingAssignmentResponse)
async def get_assignment(
    assignment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Any:
    """获取单个教学任务"""
    assignment = await TeacherService.get_assignment(db, assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail=f"教学任务ID {assignment_id} 不存在")
    return TeacherTeachingAssignmentResponse.model_validate(_serialize_assignment(assignment))


@router.put("/assignments/{assignment_id}", response_model=TeacherTeachingAssignmentResponse)
async def update_assignment(
    assignment_id: int,
    assignment_data: TeacherTeachingAssignmentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Any:
    """更新教学任务"""
    try:
        assignment = await TeacherService.update_assignment(db, assignment_id, assignment_data)
        # 重新加载关联对象
        assignment = await TeacherService.get_assignment(db, assignment_id)
        if not assignment:
            raise HTTPException(status_code=404, detail=f"教学任务ID {assignment_id} 不存在")
        return TeacherTeachingAssignmentResponse.model_validate(_serialize_assignment(assignment))
    except TeacherServiceError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新教学任务失败: {str(e)}")


@router.delete("/assignments/{assignment_id}")
async def delete_assignment(
    assignment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Any:
    """删除教学任务"""
    try:
        deleted = await TeacherService.delete_assignment(db, assignment_id)
        if not deleted:
            raise HTTPException(status_code=404, detail=f"教学任务ID {assignment_id} 不存在")
        return {"message": "教学任务删除成功"}
    except TeacherServiceError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除教学任务失败: {str(e)}")


@router.get("/{teacher_id}/assignments", response_model=TeacherTeachingAssignmentListResponse)
async def get_teacher_assignments(
    teacher_id: int,
    semester_id: Optional[int] = Query(None, description="学期ID筛选"),
    is_active: Optional[bool] = Query(True, description="是否激活筛选"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Any:
    """获取某教师的所有教学任务"""
    try:
        assignments = await TeacherService.get_teacher_assignments(
            db=db,
            teacher_id=teacher_id,
            semester_id=semester_id,
            is_active=is_active,
        )
        # 序列化教学任务列表
        serialized_assignments = [
            TeacherTeachingAssignmentResponse.model_validate(_serialize_assignment(assignment))
            for assignment in assignments
        ]
        
        return TeacherTeachingAssignmentListResponse(
            assignments=serialized_assignments,
            total=len(assignments),
            page=1,
            size=len(assignments),
            total_pages=1,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取教师教学任务失败: {str(e)}")


@router.post("/assignments/import", response_model=TeacherAssignmentImportResponse)
async def import_assignments(
    file: UploadFile = File(..., description="Excel文件"),
    update_existing: bool = Query(False, description="是否更新已存在的任务"),
    auto_create_teachers: bool = Query(False, description="如果教师不存在，是否自动创建"),
    auto_create_semesters: bool = Query(False, description="如果学期不存在，是否自动创建"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Any:
    """批量导入教师教学任务"""
    # 验证文件类型
    if not file.filename:
        raise HTTPException(status_code=400, detail="文件名为空")
    
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in [".xlsx", ".xls"]:
        raise HTTPException(status_code=400, detail="只支持Excel文件（.xlsx, .xls）")
    
    # 保存临时文件
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
        try:
            # 读取上传的文件内容
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = Path(tmp_file.name)
            
            # 导入数据
            try:
                result = await TeacherAssignmentImportService.import_assignments(
                    db=db,
                    file_path=tmp_file_path,
                    update_existing=update_existing,
                    auto_create_teachers=auto_create_teachers,
                    auto_create_semesters=auto_create_semesters,
                )
                return result
            except TeacherAssignmentImportServiceError as e:
                raise HTTPException(status_code=400, detail=str(e))
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"导入失败: {str(e)}")
        finally:
            # 清理临时文件
            if tmp_file_path.exists():
                tmp_file_path.unlink()
