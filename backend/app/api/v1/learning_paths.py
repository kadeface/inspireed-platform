"""
学习路径相关API
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.api import deps
from app.models import User, UserRole, LearningPath, LearningPathLesson, Lesson
from app.schemas.learning_path import (
    LearningPathCreate, LearningPathUpdate, LearningPathResponse,
    LearningPathWithLessons, LearningPathListItem,
    LearningPathLessonCreate, LearningPathLessonWithDetails
)

router = APIRouter()


@router.post("/", response_model=LearningPathResponse, status_code=status.HTTP_201_CREATED)
def create_learning_path(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    path_in: LearningPathCreate
):
    """
    创建学习路径（仅教师和研究员）
    """
    if current_user.role not in [UserRole.TEACHER, UserRole.RESEARCHER, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有教师和研究员可以创建学习路径"
        )
    
    # 创建学习路径
    learning_path = LearningPath(
        title=path_in.title,
        description=path_in.description,
        creator_id=current_user.id,
        difficulty_level=path_in.difficulty_level,
        cover_image_url=path_in.cover_image_url,
        estimated_hours=path_in.estimated_hours
    )
    db.add(learning_path)
    db.flush()
    
    # 添加课程
    for lesson_data in path_in.lessons:
        # 检查课程是否存在
        lesson = db.query(Lesson).filter(Lesson.id == lesson_data.lesson_id).first()
        if not lesson:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"课程 {lesson_data.lesson_id} 不存在"
            )
        
        path_lesson = LearningPathLesson(
            learning_path_id=learning_path.id,
            lesson_id=lesson_data.lesson_id,
            order_index=lesson_data.order_index,
            is_required=lesson_data.is_required
        )
        db.add(path_lesson)
    
    db.commit()
    db.refresh(learning_path)
    
    return learning_path


@router.put("/{path_id}", response_model=LearningPathResponse)
def update_learning_path(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    path_id: int,
    path_in: LearningPathUpdate
):
    """
    更新学习路径
    """
    learning_path = db.query(LearningPath).filter(LearningPath.id == path_id).first()
    if not learning_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="学习路径不存在"
        )
    
    # 检查权限
    if learning_path.creator_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权修改此学习路径"
        )
    
    # 更新字段
    update_data = path_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(learning_path, field, value)
    
    db.commit()
    db.refresh(learning_path)
    
    return learning_path


@router.delete("/{path_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_learning_path(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    path_id: int
):
    """
    删除学习路径
    """
    learning_path = db.query(LearningPath).filter(LearningPath.id == path_id).first()
    if not learning_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="学习路径不存在"
        )
    
    # 检查权限
    if learning_path.creator_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权删除此学习路径"
        )
    
    db.delete(learning_path)
    db.commit()
    
    return None


@router.get("/", response_model=list[LearningPathListItem])
def get_learning_paths(
    *,
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    published_only: bool = True
):
    """
    获取学习路径列表
    """
    query = db.query(LearningPath)
    
    if published_only:
        query = query.filter(LearningPath.is_published == True)
    
    paths = query.order_by(desc(LearningPath.created_at)).offset(skip).limit(limit).all()
    
    # 组装返回数据
    result = []
    for path in paths:
        lesson_count = db.query(LearningPathLesson).filter(
            LearningPathLesson.learning_path_id == path.id
        ).count()
        
        creator = db.query(User).filter(User.id == path.creator_id).first()
        creator_name = creator.full_name or creator.username if creator else "未知"
        
        result.append(LearningPathListItem(
            id=path.id,
            title=path.title,
            description=path.description,
            creator_id=path.creator_id,
            difficulty_level=path.difficulty_level.value,
            cover_image_url=path.cover_image_url,
            is_published=path.is_published,
            estimated_hours=path.estimated_hours,
            created_at=path.created_at,
            updated_at=path.updated_at,
            lesson_count=lesson_count,
            creator_name=creator_name
        ))
    
    return result


@router.get("/{path_id}", response_model=LearningPathWithLessons)
def get_learning_path(
    *,
    db: Session = Depends(deps.get_db),
    path_id: int
):
    """
    获取学习路径详情
    """
    learning_path = db.query(LearningPath).filter(LearningPath.id == path_id).first()
    if not learning_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="学习路径不存在"
        )
    
    # 获取路径中的课程
    path_lessons = db.query(LearningPathLesson).filter(
        LearningPathLesson.learning_path_id == path_id
    ).order_by(LearningPathLesson.order_index).all()
    
    lessons_details = []
    for pl in path_lessons:
        lesson = db.query(Lesson).filter(Lesson.id == pl.lesson_id).first()
        if lesson:
            lessons_details.append(LearningPathLessonWithDetails(
                id=pl.id,
                learning_path_id=pl.learning_path_id,
                lesson_id=pl.lesson_id,
                order_index=pl.order_index,
                is_required=pl.is_required,
                created_at=pl.created_at,
                lesson_title=lesson.title,
                lesson_description=lesson.description,
                lesson_cover_image=lesson.cover_image_url,
                lesson_difficulty=lesson.difficulty_level.value if lesson.difficulty_level else None,
                lesson_rating=lesson.average_rating,
                lesson_duration=lesson.estimated_duration
            ))
    
    # 获取创建者信息
    creator = db.query(User).filter(User.id == learning_path.creator_id).first()
    creator_name = creator.full_name or creator.username if creator else "未知"
    
    return LearningPathWithLessons(
        id=learning_path.id,
        title=learning_path.title,
        description=learning_path.description,
        creator_id=learning_path.creator_id,
        difficulty_level=learning_path.difficulty_level.value,
        cover_image_url=learning_path.cover_image_url,
        is_published=learning_path.is_published,
        estimated_hours=learning_path.estimated_hours,
        created_at=learning_path.created_at,
        updated_at=learning_path.updated_at,
        lessons=lessons_details,
        lesson_count=len(lessons_details),
        creator_name=creator_name
    )


@router.post("/{path_id}/lessons", response_model=LearningPathLessonWithDetails, status_code=status.HTTP_201_CREATED)
def add_lesson_to_path(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    path_id: int,
    lesson_data: LearningPathLessonCreate
):
    """
    向学习路径添加课程
    """
    learning_path = db.query(LearningPath).filter(LearningPath.id == path_id).first()
    if not learning_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="学习路径不存在"
        )
    
    # 检查权限
    if learning_path.creator_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权修改此学习路径"
        )
    
    # 检查课程是否存在
    lesson = db.query(Lesson).filter(Lesson.id == lesson_data.lesson_id).first()
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="课程不存在"
        )
    
    # 添加课程
    path_lesson = LearningPathLesson(
        learning_path_id=path_id,
        lesson_id=lesson_data.lesson_id,
        order_index=lesson_data.order_index,
        is_required=lesson_data.is_required
    )
    db.add(path_lesson)
    db.commit()
    db.refresh(path_lesson)
    
    # 返回详细信息
    return LearningPathLessonWithDetails(
        id=path_lesson.id,
        learning_path_id=path_lesson.learning_path_id,
        lesson_id=path_lesson.lesson_id,
        order_index=path_lesson.order_index,
        is_required=path_lesson.is_required,
        created_at=path_lesson.created_at,
        lesson_title=lesson.title,
        lesson_description=lesson.description,
        lesson_cover_image=lesson.cover_image_url,
        lesson_difficulty=lesson.difficulty_level.value if lesson.difficulty_level else None,
        lesson_rating=lesson.average_rating,
        lesson_duration=lesson.estimated_duration
    )


@router.delete("/{path_id}/lessons/{lesson_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_lesson_from_path(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    path_id: int,
    lesson_id: int
):
    """
    从学习路径移除课程
    """
    learning_path = db.query(LearningPath).filter(LearningPath.id == path_id).first()
    if not learning_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="学习路径不存在"
        )
    
    # 检查权限
    if learning_path.creator_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权修改此学习路径"
        )
    
    path_lesson = db.query(LearningPathLesson).filter(
        LearningPathLesson.learning_path_id == path_id,
        LearningPathLesson.lesson_id == lesson_id
    ).first()
    
    if not path_lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="该课程不在此学习路径中"
        )
    
    db.delete(path_lesson)
    db.commit()
    
    return None

