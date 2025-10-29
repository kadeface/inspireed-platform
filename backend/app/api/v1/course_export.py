"""
课程导出导入 API
"""
from typing import Any, List, Optional, Dict
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload
import json
import io
from datetime import datetime

from app.core.database import get_db
from app.models import (
    Subject, Grade, Course, Chapter, Lesson, Resource, User, UserRole
)
from app.api.deps import get_current_user, get_current_admin, get_current_researcher

router = APIRouter()


def require_admin_or_researcher(current_user: User = Depends(get_current_user)) -> User:
    """要求管理员或研究员权限"""
    if current_user.role not in [UserRole.ADMIN, UserRole.RESEARCHER]:
        raise HTTPException(status_code=403, detail="需要管理员或研究员权限")
    return current_user


@router.get("/export-template")
async def get_export_template():
    """获取课程导出模板"""
    
    template_data = {
        "version": "1.0",
        "export_time": datetime.utcnow().isoformat(),
        "description": "课程导出模板 - 包含完整的课程体系数据",
        "data": {
            "subjects": [
                {
                    "name": "数学",
                    "code": "math",
                    "description": "数学学科",
                    "is_active": True,
                    "display_order": 1
                }
            ],
            "grades": [
                {
                    "name": "一年级",
                    "level": 1,
                    "is_active": True
                }
            ],
            "courses": [
                {
                    "subject_code": "math",
                    "grade_level": 1,
                    "name": "一年级数学",
                    "code": "grade1-math",
                    "description": "一年级数学课程",
                    "is_active": True,
                    "display_order": 1
                }
            ],
            "chapters": [
                {
                    "course_code": "grade1-math",
                    "name": "第一章：数的认识",
                    "code": "chapter-1",
                    "description": "学习数的基本概念",
                    "display_order": 1,
                    "parent_code": None,
                    "is_active": True
                }
            ],
            "lessons": [
                {
                    "course_code": "grade1-math",
                    "chapter_code": "chapter-1",
                    "title": "数的认识教案",
                    "description": "学习1-10的数字",
                    "status": "published",
                    "content": [],
                    "tags": ["基础", "数字"],
                    "difficulty_level": "beginner",
                    "estimated_duration": 40
                }
            ],
            "resources": [
                {
                    "chapter_code": "chapter-1",
                    "title": "数字卡片",
                    "description": "1-10的数字卡片",
                    "resource_type": "pdf",
                    "file_url": "https://example.com/numbers.pdf",
                    "is_official": True,
                    "is_downloadable": True,
                    "display_order": 1
                }
            ]
        }
    }
    
    # 转换为JSON字符串
    json_str = json.dumps(template_data, ensure_ascii=False, indent=2)
    
    # 创建字节流
    output = io.BytesIO()
    output.write(json_str.encode('utf-8'))
    output.seek(0)
    
    # 返回文件下载
    import urllib.parse
    filename = urllib.parse.quote("课程导出模板.json")
    return StreamingResponse(
        output,
        media_type="application/json",
        headers={
            "Content-Disposition": f"attachment; filename*=UTF-8''{filename}"
        }
    )


@router.get("/courses/{course_id}/export")
async def export_course(
    course_id: int,
    include_lessons: bool = True,
    include_resources: bool = True,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin_or_researcher)
):
    """导出单个课程的完整数据"""
    
    # 获取课程及其关联数据
    course_result = await db.execute(
        select(Course)
        .options(
            selectinload(Course.subject),
            selectinload(Course.grade),
            selectinload(Course.chapters).selectinload(Chapter.resources),
            selectinload(Course.lessons)
        )
        .where(Course.id == course_id)
    )
    course = course_result.scalar_one_or_none()
    
    if not course:
        raise HTTPException(404, "课程不存在")
    
    # 构建导出数据
    export_data = {
        "version": "1.0",
        "export_time": datetime.utcnow().isoformat(),
        "exported_by": current_user.username,
        "description": f"课程导出：{course.name}",
        "data": {
            "subjects": [{
                "name": course.subject.name,
                "code": course.subject.code,
                "description": course.subject.description,
                "is_active": course.subject.is_active,
                "display_order": course.subject.display_order
            }],
            "grades": [{
                "name": course.grade.name,
                "level": course.grade.level,
                "is_active": course.grade.is_active
            }],
            "courses": [{
                "subject_code": course.subject.code,
                "grade_level": course.grade.level,
                "name": course.name,
                "code": course.code,
                "description": course.description,
                "is_active": course.is_active,
                "display_order": course.display_order
            }],
            "chapters": [],
            "lessons": [],
            "resources": []
        }
    }
    
    # 处理章节数据
    chapter_code_map = {}
    for chapter in course.chapters:
        chapter_data = {
            "course_code": course.code,
            "name": chapter.name,
            "code": chapter.code,
            "description": chapter.description,
            "display_order": chapter.display_order,
            "parent_code": None,
            "is_active": chapter.is_active
        }
        
        # 处理父章节关系
        if chapter.parent_id:
            # 查找父章节的code
            parent_chapter = next((c for c in course.chapters if c.id == chapter.parent_id), None)
            if parent_chapter:
                chapter_data["parent_code"] = parent_chapter.code
        
        export_data["data"]["chapters"].append(chapter_data)
        chapter_code_map[chapter.id] = chapter.code
        
        # 处理资源数据
        if include_resources:
            for resource in chapter.resources:
                resource_data = {
                    "chapter_code": chapter.code,
                    "title": resource.title,
                    "description": resource.description,
                    "resource_type": resource.resource_type,
                    "file_url": resource.file_url,
                    "file_size": resource.file_size,
                    "page_count": resource.page_count,
                    "thumbnail_url": resource.thumbnail_url,
                    "is_official": resource.is_official,
                    "is_downloadable": resource.is_downloadable,
                    "is_active": resource.is_active,
                    "display_order": resource.display_order
                }
                export_data["data"]["resources"].append(resource_data)
    
    # 处理教案数据
    if include_lessons:
        for lesson in course.lessons:
            lesson_data = {
                "course_code": course.code,
                "chapter_code": chapter_code_map.get(lesson.chapter_id) if lesson.chapter_id else None,
                "title": lesson.title,
                "description": lesson.description,
                "status": lesson.status.value,
                "content": lesson.content,
                "tags": lesson.tags,
                "cover_image_url": lesson.cover_image_url,
                "difficulty_level": lesson.difficulty_level.value if lesson.difficulty_level else None,
                "estimated_duration": lesson.estimated_duration,
                "reference_notes": lesson.reference_notes
            }
            export_data["data"]["lessons"].append(lesson_data)
    
    # 转换为JSON字符串
    json_str = json.dumps(export_data, ensure_ascii=False, indent=2, default=str)
    
    # 创建字节流
    output = io.BytesIO()
    output.write(json_str.encode('utf-8'))
    output.seek(0)
    
    # 返回文件下载
    import urllib.parse
    filename = urllib.parse.quote(f"{course.name}_导出.json")
    return StreamingResponse(
        output,
        media_type="application/json",
        headers={
            "Content-Disposition": f"attachment; filename*=UTF-8''{filename}"
        }
    )


@router.get("/export-all")
async def export_all_courses(
    include_lessons: bool = True,
    include_resources: bool = True,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin_or_researcher)
):
    """导出所有课程的完整数据"""
    
    # 获取所有课程及其关联数据
    courses_result = await db.execute(
        select(Course)
        .options(
            selectinload(Course.subject),
            selectinload(Course.grade),
            selectinload(Course.chapters).selectinload(Chapter.resources),
            selectinload(Course.lessons)
        )
        .where(Course.is_active == True)
        .order_by(Course.subject_id, Course.grade_id)
    )
    courses = courses_result.scalars().all()
    
    if not courses:
        raise HTTPException(404, "没有找到任何课程")
    
    # 构建导出数据
    export_data = {
        "version": "1.0",
        "export_time": datetime.utcnow().isoformat(),
        "exported_by": current_user.username,
        "description": "完整课程体系导出",
        "data": {
            "subjects": [],
            "grades": [],
            "courses": [],
            "chapters": [],
            "lessons": [],
            "resources": []
        }
    }
    
    # 收集所有学科和年级
    subjects_dict = {}
    grades_dict = {}
    
    for course in courses:
        # 收集学科
        if course.subject.id not in subjects_dict:
            subjects_dict[course.subject.id] = {
                "name": course.subject.name,
                "code": course.subject.code,
                "description": course.subject.description,
                "is_active": course.subject.is_active,
                "display_order": course.subject.display_order
            }
        
        # 收集年级
        if course.grade.id not in grades_dict:
            grades_dict[course.grade.id] = {
                "name": course.grade.name,
                "level": course.grade.level,
                "is_active": course.grade.is_active
            }
        
        # 添加课程数据
        course_data = {
            "subject_code": course.subject.code,
            "grade_level": course.grade.level,
            "name": course.name,
            "code": course.code,
            "description": course.description,
            "is_active": course.is_active,
            "display_order": course.display_order
        }
        export_data["data"]["courses"].append(course_data)
        
        # 处理章节数据
        chapter_code_map = {}
        for chapter in course.chapters:
            chapter_data = {
                "course_code": course.code,
                "name": chapter.name,
                "code": chapter.code,
                "description": chapter.description,
                "display_order": chapter.display_order,
                "parent_code": None,
                "is_active": chapter.is_active
            }
            
            # 处理父章节关系
            if chapter.parent_id:
                parent_chapter = next((c for c in course.chapters if c.id == chapter.parent_id), None)
                if parent_chapter:
                    chapter_data["parent_code"] = parent_chapter.code
            
            export_data["data"]["chapters"].append(chapter_data)
            chapter_code_map[chapter.id] = chapter.code
            
            # 处理资源数据
            if include_resources:
                for resource in chapter.resources:
                    resource_data = {
                        "chapter_code": chapter.code,
                        "title": resource.title,
                        "description": resource.description,
                        "resource_type": resource.resource_type,
                        "file_url": resource.file_url,
                        "file_size": resource.file_size,
                        "page_count": resource.page_count,
                        "thumbnail_url": resource.thumbnail_url,
                        "is_official": resource.is_official,
                        "is_downloadable": resource.is_downloadable,
                        "is_active": resource.is_active,
                        "display_order": resource.display_order
                    }
                    export_data["data"]["resources"].append(resource_data)
        
        # 处理教案数据
        if include_lessons:
            for lesson in course.lessons:
                lesson_data = {
                    "course_code": course.code,
                    "chapter_code": chapter_code_map.get(lesson.chapter_id) if lesson.chapter_id else None,
                    "title": lesson.title,
                    "description": lesson.description,
                    "status": lesson.status.value,
                    "content": lesson.content,
                    "tags": lesson.tags,
                    "cover_image_url": lesson.cover_image_url,
                    "difficulty_level": lesson.difficulty_level.value if lesson.difficulty_level else None,
                    "estimated_duration": lesson.estimated_duration,
                    "reference_notes": lesson.reference_notes
                }
                export_data["data"]["lessons"].append(lesson_data)
    
    # 添加学科和年级数据
    export_data["data"]["subjects"] = list(subjects_dict.values())
    export_data["data"]["grades"] = list(grades_dict.values())
    
    # 转换为JSON字符串
    json_str = json.dumps(export_data, ensure_ascii=False, indent=2, default=str)
    
    # 创建字节流
    output = io.BytesIO()
    output.write(json_str.encode('utf-8'))
    output.seek(0)
    
    # 返回文件下载
    import urllib.parse
    filename = urllib.parse.quote(f"完整课程体系导出_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    return StreamingResponse(
        output,
        media_type="application/json",
        headers={
            "Content-Disposition": f"attachment; filename*=UTF-8''{filename}"
        }
    )


@router.post("/import")
async def import_courses(
    file: UploadFile = File(...),
    overwrite_existing: bool = Form(False),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin_or_researcher)
):
    """导入课程数据"""
    
    # 验证文件类型
    if not file.filename or not file.filename.endswith('.json'):
        raise HTTPException(400, "文件必须是JSON格式")
    
    try:
        # 读取文件内容
        content = await file.read()
        
        if len(content) == 0:
            raise HTTPException(400, "上传的文件为空")
        
        # 解析JSON数据
        try:
            import_data = json.loads(content.decode('utf-8'))
        except json.JSONDecodeError as e:
            raise HTTPException(400, f"JSON解析失败: {str(e)}")
        
        # 验证数据格式
        if not isinstance(import_data, dict) or 'data' not in import_data:
            raise HTTPException(400, "无效的导入文件格式")
        
        data = import_data['data']
        
        # 导入结果统计
        import_result = {
            "subjects": {"created": 0, "skipped": 0},
            "grades": {"created": 0, "skipped": 0},
            "courses": {"created": 0, "skipped": 0},
            "chapters": {"created": 0, "skipped": 0},
            "lessons": {"created": 0, "skipped": 0},
            "resources": {"created": 0, "skipped": 0},
            "errors": []
        }
        
        # 创建映射字典
        subject_code_map = {}
        grade_level_map = {}
        course_code_map = {}
        chapter_code_map = {}
        
        # 1. 导入学科
        for subject_data in data.get('subjects', []):
            try:
                # 检查是否已存在
                existing = await db.execute(
                    select(Subject).where(Subject.code == subject_data['code'])
                )
                existing_subject = existing.scalar_one_or_none()
                
                if existing_subject:
                    if overwrite_existing:
                        # 更新现有学科
                        for key, value in subject_data.items():
                            if key != 'code':
                                setattr(existing_subject, key, value)
                        await db.commit()
                        import_result["subjects"]["skipped"] += 1
                    else:
                        import_result["subjects"]["skipped"] += 1
                else:
                    # 创建新学科
                    subject = Subject(**subject_data)
                    db.add(subject)
                    await db.commit()
                    await db.refresh(subject)
                    import_result["subjects"]["created"] += 1
                
                subject_code_map[subject_data['code']] = existing_subject.id if existing_subject else subject.id
                
            except Exception as e:
                import_result["errors"].append(f"导入学科失败 {subject_data.get('name', '')}: {str(e)}")
        
        # 2. 导入年级
        for grade_data in data.get('grades', []):
            try:
                # 检查是否已存在
                existing = await db.execute(
                    select(Grade).where(Grade.level == grade_data['level'])
                )
                existing_grade = existing.scalar_one_or_none()
                
                if existing_grade:
                    if overwrite_existing:
                        # 更新现有年级
                        for key, value in grade_data.items():
                            if key != 'level':
                                setattr(existing_grade, key, value)
                        await db.commit()
                        import_result["grades"]["skipped"] += 1
                    else:
                        import_result["grades"]["skipped"] += 1
                else:
                    # 创建新年级
                    grade = Grade(**grade_data)
                    db.add(grade)
                    await db.commit()
                    await db.refresh(grade)
                    import_result["grades"]["created"] += 1
                
                grade_level_map[grade_data['level']] = existing_grade.id if existing_grade else grade.id
                
            except Exception as e:
                import_result["errors"].append(f"导入年级失败 {grade_data.get('name', '')}: {str(e)}")
        
        # 3. 导入课程
        for course_data in data.get('courses', []):
            try:
                # 获取学科和年级ID
                subject_id = subject_code_map.get(course_data['subject_code'])
                grade_id = grade_level_map.get(course_data['grade_level'])
                
                if not subject_id or not grade_id:
                    import_result["errors"].append(f"课程 {course_data.get('name', '')} 的学科或年级不存在")
                    continue
                
                # 检查是否已存在
                existing = await db.execute(
                    select(Course).where(
                        Course.subject_id == subject_id,
                        Course.grade_id == grade_id
                    )
                )
                existing_course = existing.scalar_one_or_none()
                
                if existing_course:
                    if overwrite_existing:
                        # 更新现有课程
                        for key, value in course_data.items():
                            if key not in ['subject_code', 'grade_level']:
                                setattr(existing_course, key, value)
                        await db.commit()
                        import_result["courses"]["skipped"] += 1
                    else:
                        import_result["courses"]["skipped"] += 1
                else:
                    # 创建新课程
                    course = Course(
                        subject_id=subject_id,
                        grade_id=grade_id,
                        name=course_data['name'],
                        code=course_data['code'],
                        description=course_data.get('description'),
                        is_active=course_data.get('is_active', True),
                        display_order=course_data.get('display_order', 0),
                        created_by=current_user.id
                    )
                    db.add(course)
                    await db.commit()
                    await db.refresh(course)
                    import_result["courses"]["created"] += 1
                
                course_code_map[course_data['code']] = existing_course.id if existing_course else course.id
                
            except Exception as e:
                import_result["errors"].append(f"导入课程失败 {course_data.get('name', '')}: {str(e)}")
        
        # 4. 导入章节
        for chapter_data in data.get('chapters', []):
            try:
                # 获取课程ID
                course_id = course_code_map.get(chapter_data['course_code'])
                if not course_id:
                    import_result["errors"].append(f"章节 {chapter_data.get('name', '')} 的课程不存在")
                    continue
                
                # 处理父章节关系
                parent_id = None
                if chapter_data.get('parent_code'):
                    parent_id = chapter_code_map.get(chapter_data['parent_code'])
                    if not parent_id:
                        import_result["errors"].append(f"章节 {chapter_data.get('name', '')} 的父章节不存在")
                        continue
                
                # 检查是否已存在
                existing = await db.execute(
                    select(Chapter).where(
                        Chapter.course_id == course_id,
                        Chapter.code == chapter_data['code']
                    )
                )
                existing_chapter = existing.scalar_one_or_none()
                
                if existing_chapter:
                    if overwrite_existing:
                        # 更新现有章节
                        for key, value in chapter_data.items():
                            if key not in ['course_code', 'parent_code']:
                                setattr(existing_chapter, key, value)
                        existing_chapter.parent_id = parent_id
                        await db.commit()
                        import_result["chapters"]["skipped"] += 1
                    else:
                        import_result["chapters"]["skipped"] += 1
                else:
                    # 创建新章节
                    chapter = Chapter(
                        course_id=course_id,
                        parent_id=parent_id,
                        name=chapter_data['name'],
                        code=chapter_data['code'],
                        description=chapter_data.get('description'),
                        display_order=chapter_data.get('display_order', 0),
                        is_active=chapter_data.get('is_active', True)
                    )
                    db.add(chapter)
                    await db.commit()
                    await db.refresh(chapter)
                    import_result["chapters"]["created"] += 1
                
                chapter_code_map[chapter_data['code']] = existing_chapter.id if existing_chapter else chapter.id
                
            except Exception as e:
                import_result["errors"].append(f"导入章节失败 {chapter_data.get('name', '')}: {str(e)}")
        
        # 5. 导入教案
        for lesson_data in data.get('lessons', []):
            try:
                # 获取课程ID
                course_id = course_code_map.get(lesson_data['course_code'])
                if not course_id:
                    import_result["errors"].append(f"教案 {lesson_data.get('title', '')} 的课程不存在")
                    continue
                
                # 获取章节ID
                chapter_id = None
                if lesson_data.get('chapter_code'):
                    chapter_id = chapter_code_map.get(lesson_data['chapter_code'])
                    if not chapter_id:
                        import_result["errors"].append(f"教案 {lesson_data.get('title', '')} 的章节不存在")
                        continue
                
                # 检查是否已存在
                existing = await db.execute(
                    select(Lesson).where(
                        Lesson.course_id == course_id,
                        Lesson.title == lesson_data['title']
                    )
                )
                existing_lesson = existing.scalar_one_or_none()
                
                if existing_lesson:
                    if overwrite_existing:
                        # 更新现有教案
                        for key, value in lesson_data.items():
                            if key not in ['course_code', 'chapter_code']:
                                setattr(existing_lesson, key, value)
                        existing_lesson.chapter_id = chapter_id
                        await db.commit()
                        import_result["lessons"]["skipped"] += 1
                    else:
                        import_result["lessons"]["skipped"] += 1
                else:
                    # 创建新教案
                    lesson = Lesson(
                        course_id=course_id,
                        chapter_id=chapter_id,
                        title=lesson_data['title'],
                        description=lesson_data.get('description'),
                        status=lesson_data.get('status', 'draft'),
                        content=lesson_data.get('content', []),
                        tags=lesson_data.get('tags', []),
                        cover_image_url=lesson_data.get('cover_image_url'),
                        difficulty_level=lesson_data.get('difficulty_level'),
                        estimated_duration=lesson_data.get('estimated_duration'),
                        reference_notes=lesson_data.get('reference_notes'),
                        creator_id=current_user.id
                    )
                    db.add(lesson)
                    await db.commit()
                    await db.refresh(lesson)
                    import_result["lessons"]["created"] += 1
                
            except Exception as e:
                import_result["errors"].append(f"导入教案失败 {lesson_data.get('title', '')}: {str(e)}")
        
        # 6. 导入资源
        for resource_data in data.get('resources', []):
            try:
                # 获取章节ID
                chapter_id = chapter_code_map.get(resource_data['chapter_code'])
                if not chapter_id:
                    import_result["errors"].append(f"资源 {resource_data.get('title', '')} 的章节不存在")
                    continue
                
                # 检查是否已存在
                existing = await db.execute(
                    select(Resource).where(
                        Resource.chapter_id == chapter_id,
                        Resource.title == resource_data['title']
                    )
                )
                existing_resource = existing.scalar_one_or_none()
                
                if existing_resource:
                    if overwrite_existing:
                        # 更新现有资源
                        for key, value in resource_data.items():
                            if key != 'chapter_code':
                                setattr(existing_resource, key, value)
                        await db.commit()
                        import_result["resources"]["skipped"] += 1
                    else:
                        import_result["resources"]["skipped"] += 1
                else:
                    # 创建新资源
                    resource = Resource(
                        chapter_id=chapter_id,
                        title=resource_data['title'],
                        description=resource_data.get('description'),
                        resource_type=resource_data['resource_type'],
                        file_url=resource_data.get('file_url'),
                        file_size=resource_data.get('file_size'),
                        page_count=resource_data.get('page_count'),
                        thumbnail_url=resource_data.get('thumbnail_url'),
                        is_official=resource_data.get('is_official', False),
                        is_downloadable=resource_data.get('is_downloadable', True),
                        is_active=resource_data.get('is_active', True),
                        display_order=resource_data.get('display_order', 0),
                        created_by=current_user.id
                    )
                    db.add(resource)
                    await db.commit()
                    await db.refresh(resource)
                    import_result["resources"]["created"] += 1
                
            except Exception as e:
                import_result["errors"].append(f"导入资源失败 {resource_data.get('title', '')}: {str(e)}")
        
        return {
            "message": "导入完成",
            "result": import_result,
            "summary": {
                "total_created": sum(
                    import_result[key]["created"] 
                    for key in ["subjects", "grades", "courses", "chapters", "lessons", "resources"]
                ),
                "total_skipped": sum(
                    import_result[key]["skipped"] 
                    for key in ["subjects", "grades", "courses", "chapters", "lessons", "resources"]
                ),
                "total_errors": len(import_result["errors"])
            }
        }
        
    except Exception as e:
        raise HTTPException(400, f"导入失败: {str(e)}")
