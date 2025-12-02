"""
课程合并工具函数
"""
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.models import Course, Lesson, Chapter, Grade
from app.schemas.curriculum import CourseMergeRequest, CourseMergeResponse, CourseResponse


async def _delete_chapter_and_children(db: AsyncSession, chapter_id: int):
    """递归删除章节及其所有子章节和资源"""
    from app.models.resource import Resource
    
    # 查找所有子章节
    children_result = await db.execute(
        select(Chapter).where(Chapter.parent_id == chapter_id)
    )
    children = children_result.scalars().all()
    
    # 递归删除子章节
    for child in children:
        await _delete_chapter_and_children(db, child.id)
    
    # 删除章节关联的资源（标记为禁用，而不是删除文件）
    resources_result = await db.execute(
        select(Resource).where(Resource.chapter_id == chapter_id)
    )
    resources = resources_result.scalars().all()
    for resource in resources:
        resource.is_active = False
        resource.chapter_id = None
    
    # 删除当前章节
    chapter_result = await db.execute(
        select(Chapter).where(Chapter.id == chapter_id)
    )
    chapter = chapter_result.scalar_one_or_none()
    if chapter:
        await db.delete(chapter)


async def _merge_chapter_children(
    db: AsyncSession,
    source_parent_id: int,
    target_parent_id: int,
    target_course_id: int,
    chapter_id_mapping: dict,
    merge_request: CourseMergeRequest,
    errors: list
) -> dict:
    """递归合并子章节，返回合并统计"""
    merged = 0
    skipped = 0
    
    # 查找源章节的所有子章节
    children_result = await db.execute(
        select(Chapter)
        .where(Chapter.parent_id == source_parent_id)
        .order_by(Chapter.display_order, Chapter.id)
    )
    children = children_result.scalars().all()
    
    for child in children:
        try:
            # 检查目标父章节下是否已有相同名称的子章节
            existing_child = None
            if child.code:
                existing_result = await db.execute(
                    select(Chapter).where(
                        Chapter.course_id == target_course_id,
                        Chapter.parent_id == target_parent_id,
                        Chapter.code == child.code
                    )
                )
                existing_child = existing_result.scalar_one_or_none()
            
            if not existing_child and child.name:
                existing_result = await db.execute(
                    select(Chapter).where(
                        Chapter.course_id == target_course_id,
                        Chapter.parent_id == target_parent_id,
                        Chapter.name == child.name
                    )
                )
                existing_child = existing_result.scalar_one_or_none()
            
            if existing_child:
                if merge_request.handle_conflicts == "skip":
                    skipped += 1
                    chapter_id_mapping[child.id] = existing_child.id
                    # 递归处理子章节的子章节
                    child_stats = await _merge_chapter_children(
                        db, child.id, existing_child.id,
                        target_course_id, chapter_id_mapping,
                        merge_request, errors
                    )
                    merged += child_stats['merged']
                    skipped += child_stats['skipped']
                    continue
                elif merge_request.handle_conflicts == "rename":
                    child.name = f"{child.name} (来自合并)"
                    if child.code:
                        child.code = f"{child.code}-merged"
                elif merge_request.handle_conflicts == "overwrite":
                    await _delete_chapter_and_children(db, existing_child.id)
            
            # 更新子章节
            old_id = child.id
            child.course_id = target_course_id
            child.parent_id = target_parent_id
            
            await db.flush()
            chapter_id_mapping[old_id] = child.id
            merged += 1
            
            # 递归处理子章节的子章节
            child_stats = await _merge_chapter_children(
                db, old_id, child.id,
                target_course_id, chapter_id_mapping,
                merge_request, errors
            )
            merged += child_stats['merged']
            skipped += child_stats['skipped']
        except Exception as e:
            errors.append(f"合并子章节 '{child.name}' 失败: {str(e)}")
            skipped += 1
    
    return {'merged': merged, 'skipped': skipped}


async def merge_courses_impl(
    merge_request: CourseMergeRequest,
    db: AsyncSession,
    source_course: Course,
    target_course: Course,
) -> CourseMergeResponse:
    """课程合并实现逻辑"""
    from app.models.lesson import Lesson
    
    errors = []
    merged_lessons_count = 0
    merged_chapters_count = 0
    skipped_lessons_count = 0
    skipped_chapters_count = 0
    
    # 合并教案
    if merge_request.merge_lessons:
        lessons_result = await db.execute(
            select(Lesson).where(Lesson.course_id == source_course.id)
        )
        source_lessons = lessons_result.scalars().all()
        
        for lesson in source_lessons:
            try:
                # 检查目标课程中是否已有相同标题的教案
                existing_lesson_result = await db.execute(
                    select(Lesson).where(
                        Lesson.course_id == target_course.id,
                        Lesson.title == lesson.title
                    )
                )
                existing_lesson = existing_lesson_result.scalar_one_or_none()
                
                if existing_lesson:
                    if merge_request.handle_conflicts == "skip":
                        skipped_lessons_count += 1
                        continue
                    elif merge_request.handle_conflicts == "rename":
                        # 重命名教案标题
                        lesson.title = f"{lesson.title} (来自{source_course.name})"
                    elif merge_request.handle_conflicts == "overwrite":
                        # 删除目标课程中的教案
                        await db.delete(existing_lesson)
                
                # 更新教案的课程ID
                lesson.course_id = target_course.id
                # 如果教案关联了章节，先清空章节关联（章节会在下面统一处理）
                if lesson.chapter_id:
                    lesson.chapter_id = None
                
                merged_lessons_count += 1
            except Exception as e:
                errors.append(f"合并教案 '{lesson.title}' 失败: {str(e)}")
                skipped_lessons_count += 1
    
    # 合并章节（先处理顶级章节，再处理子章节）
    if merge_request.merge_chapters:
        # 先获取所有顶级章节（parent_id为None）
        top_chapters_result = await db.execute(
            select(Chapter)
            .where(
                Chapter.course_id == source_course.id,
                Chapter.parent_id == None
            )
            .order_by(Chapter.display_order, Chapter.id)
        )
        top_chapters = top_chapters_result.scalars().all()
        
        # 构建章节映射（用于处理父子关系）
        chapter_id_mapping = {}  # {old_id: new_id}
        
        # 先处理顶级章节
        for chapter in top_chapters:
            try:
                # 检查目标课程中是否已有相同代码或名称的章节
                existing_chapter = None
                if chapter.code:
                    existing_result = await db.execute(
                        select(Chapter).where(
                            Chapter.course_id == target_course.id,
                            Chapter.code == chapter.code,
                            Chapter.parent_id == None
                        )
                    )
                    existing_chapter = existing_result.scalar_one_or_none()
                
                if not existing_chapter and chapter.name:
                    existing_result = await db.execute(
                        select(Chapter).where(
                            Chapter.course_id == target_course.id,
                            Chapter.name == chapter.name,
                            Chapter.parent_id == None
                        )
                    )
                    existing_chapter = existing_result.scalar_one_or_none()
                
                if existing_chapter:
                    if merge_request.handle_conflicts == "skip":
                        skipped_chapters_count += 1
                        # 记录映射关系，以便处理子章节
                        chapter_id_mapping[chapter.id] = existing_chapter.id
                        # 递归处理子章节，映射到现有章节
                        child_stats = await _merge_chapter_children(
                            db, chapter.id, existing_chapter.id, 
                            target_course.id, chapter_id_mapping,
                            merge_request, errors
                        )
                        merged_chapters_count += child_stats['merged']
                        skipped_chapters_count += child_stats['skipped']
                        continue
                    elif merge_request.handle_conflicts == "rename":
                        # 重命名章节
                        chapter.name = f"{chapter.name} (来自{source_course.name})"
                        if chapter.code:
                            chapter.code = f"{chapter.code}-merged"
                    elif merge_request.handle_conflicts == "overwrite":
                        # 删除目标课程中的章节（会级联删除子章节和资源）
                        await _delete_chapter_and_children(db, existing_chapter.id)
                
                # 更新章节的课程ID
                old_id = chapter.id
                chapter.course_id = target_course.id
                chapter.parent_id = None  # 顶级章节
                
                # 保存新章节ID到映射表
                await db.flush()  # 确保章节有ID
                chapter_id_mapping[old_id] = chapter.id
                
                merged_chapters_count += 1
                
                # 递归处理子章节
                child_stats = await _merge_chapter_children(
                    db, old_id, chapter.id,
                    target_course.id, chapter_id_mapping,
                    merge_request, errors
                )
                merged_chapters_count += child_stats['merged']
                skipped_chapters_count += child_stats['skipped']
            except Exception as e:
                errors.append(f"合并章节 '{chapter.name}' 失败: {str(e)}")
                skipped_chapters_count += 1
    
    # 删除源课程（如果所有数据都已迁移）
    if merge_request.merge_lessons and merge_request.merge_chapters:
        # 检查源课程是否还有教案或章节
        remaining_lessons_result = await db.execute(
            select(func.count(Lesson.id)).where(Lesson.course_id == source_course.id)
        )
        remaining_lessons = remaining_lessons_result.scalar() or 0
        
        remaining_chapters_result = await db.execute(
            select(func.count(Chapter.id)).where(Chapter.course_id == source_course.id)
        )
        remaining_chapters = remaining_chapters_result.scalar() or 0
        
        if remaining_lessons == 0 and remaining_chapters == 0:
            await db.delete(source_course)
        else:
            # 如果还有数据，只标记为禁用
            source_course.is_active = False
    
    # 重新加载目标课程
    target_result = await db.execute(
        select(Course)
        .options(selectinload(Course.subject), selectinload(Course.grade))
        .where(Course.id == target_course.id)
    )
    target_course = target_result.scalar_one()
    
    return CourseMergeResponse(
        success=True,
        target_course=target_course,
        merged_lessons_count=merged_lessons_count,
        merged_chapters_count=merged_chapters_count,
        skipped_lessons_count=skipped_lessons_count,
        skipped_chapters_count=skipped_chapters_count,
        errors=errors
    )

