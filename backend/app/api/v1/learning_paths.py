"""
学习路径相关API
"""

from datetime import datetime
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.api import deps
from app.models import User, UserRole, LearningPath, LearningPathLesson, Lesson
from app.schemas.learning_path import (
    LearningPathCreate,
    LearningPathUpdate,
    LearningPathResponse,
    LearningPathWithLessons,
    LearningPathListItem,
    LearningPathLessonCreate,
    LearningPathLessonWithDetails,
)

router = APIRouter()


def _safe_int(value: Any, default: int = 0) -> int:
    """将值安全转换为整数。"""
    if value is None:
        return default
    if isinstance(value, bool):
        return int(value)
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _safe_optional_int(value: Any) -> Optional[int]:
    """将值安全转换为可选整数。"""
    if value is None:
        return None
    if isinstance(value, bool):
        return int(value)
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _safe_str(value: Any, default: str = "") -> str:
    """将值安全转换为字符串。"""
    if value is None:
        return default
    return str(value)


def _safe_optional_str(value: Any) -> Optional[str]:
    """将值安全转换为可选字符串。"""
    if value is None:
        return None
    return str(value)


def _safe_bool(value: Any, default: bool = False) -> bool:
    """将值安全转换为布尔值。"""
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    return default


def _safe_float(value: Any, default: float = 0.0) -> float:
    """将值安全转换为浮点数。"""
    if value is None:
        return default
    if isinstance(value, bool):
        return float(value)
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _safe_datetime(value: Any, default: Optional[datetime] = None) -> Optional[datetime]:
    """将值安全转换为 datetime。"""
    if isinstance(value, datetime):
        return value
    return default


def _get_role_value(role: Any) -> str:
    """获取角色的字符串值。"""
    if isinstance(role, UserRole):
        return role.value
    if role is None:
        return ""
    return str(role)


@router.post("/", response_model=LearningPathResponse, status_code=status.HTTP_201_CREATED)
def create_learning_path(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    path_in: LearningPathCreate,
):
    """
    创建学习路径（仅教师和研究员）
    """
    if current_user.role not in [UserRole.TEACHER, UserRole.RESEARCHER, UserRole.ADMIN]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="只有教师和研究员可以创建学习路径")

    # 创建学习路径
    learning_path = LearningPath(
        title=path_in.title,
        description=path_in.description,
        creator_id=current_user.id,
        difficulty_level=path_in.difficulty_level,
        cover_image_url=path_in.cover_image_url,
        estimated_hours=path_in.estimated_hours,
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
                status_code=status.HTTP_404_NOT_FOUND, detail=f"课程 {lesson_data.lesson_id} 不存在"
            )

        path_lesson = LearningPathLesson(
            learning_path_id=learning_path.id,
            lesson_id=lesson_data.lesson_id,
            order_index=lesson_data.order_index,
            is_required=lesson_data.is_required,
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
    path_in: LearningPathUpdate,
):
    """
    更新学习路径
    """
    learning_path = db.query(LearningPath).filter(LearningPath.id == path_id).first()
    if not learning_path:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="学习路径不存在")

    # 检查权限
    creator_id = getattr(learning_path, "creator_id", None)
    current_user_id = getattr(current_user, "id", None)
    current_user_role = _get_role_value(getattr(current_user, "role", None))
    is_admin = current_user_role == UserRole.ADMIN.value

    if creator_id != current_user_id and not is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权修改此学习路径")

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
    path_id: int,
):
    """
    删除学习路径
    """
    learning_path = db.query(LearningPath).filter(LearningPath.id == path_id).first()
    if not learning_path:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="学习路径不存在")

    # 检查权限
    creator_id = getattr(learning_path, "creator_id", None)
    current_user_id = getattr(current_user, "id", None)
    current_user_role = _get_role_value(getattr(current_user, "role", None))
    is_admin = current_user_role == UserRole.ADMIN.value

    if creator_id != current_user_id and not is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权删除此学习路径")

    db.delete(learning_path)
    db.commit()

    return None


@router.get("/", response_model=list[LearningPathListItem])
def get_learning_paths(
    *,
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    published_only: bool = True,
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
        path_id = _safe_int(getattr(path, "id", None))
        lesson_count = (
            db.query(LearningPathLesson)
            .filter(LearningPathLesson.learning_path_id == path_id)
            .count()
        )

        creator = db.query(User).filter(User.id == getattr(path, "creator_id", None)).first()
        creator_full_name = (
            _safe_optional_str(getattr(creator, "full_name", None)) if creator else None
        )
        creator_username = (
            _safe_optional_str(getattr(creator, "username", None)) if creator else None
        )
        creator_name = creator_full_name or creator_username or "未知"

        difficulty_attr = getattr(path, "difficulty_level", None)
        difficulty_value = getattr(difficulty_attr, "value", difficulty_attr)

        created_at_raw = getattr(path, "created_at", None)
        updated_at_raw = getattr(path, "updated_at", None)
        timestamp_fallback = datetime.utcnow()
        created_at_value = _safe_datetime(created_at_raw, timestamp_fallback) or timestamp_fallback
        updated_at_value = _safe_datetime(updated_at_raw, timestamp_fallback) or timestamp_fallback

        result.append(
            LearningPathListItem(
                id=path_id,
                title=_safe_str(getattr(path, "title", "")),
                description=_safe_optional_str(getattr(path, "description", None)),
                creator_id=_safe_int(getattr(path, "creator_id", None)),
                difficulty_level=_safe_str(difficulty_value, ""),
                cover_image_url=_safe_optional_str(getattr(path, "cover_image_url", None)),
                is_published=_safe_bool(getattr(path, "is_published", False)),
                estimated_hours=_safe_optional_int(getattr(path, "estimated_hours", None)),
                created_at=created_at_value,
                updated_at=updated_at_value,
                lesson_count=lesson_count,
                creator_name=_safe_str(creator_name),
            )
        )

    return result


@router.get("/{path_id}", response_model=LearningPathWithLessons)
def get_learning_path(*, db: Session = Depends(deps.get_db), path_id: int):
    """
    获取学习路径详情
    """
    learning_path = db.query(LearningPath).filter(LearningPath.id == path_id).first()
    if not learning_path:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="学习路径不存在")

    # 获取路径中的课程
    path_lessons = (
        db.query(LearningPathLesson)
        .filter(LearningPathLesson.learning_path_id == path_id)
        .order_by(LearningPathLesson.order_index)
        .all()
    )

    lessons_details = []
    for pl in path_lessons:
        lesson = db.query(Lesson).filter(Lesson.id == getattr(pl, "lesson_id", None)).first()
        if not lesson:
            continue

        difficulty_attr = getattr(lesson, "difficulty_level", None)
        difficulty_value = getattr(difficulty_attr, "value", difficulty_attr)
        timestamp_fallback = datetime.utcnow()

        lessons_details.append(
            LearningPathLessonWithDetails(
                id=_safe_int(getattr(pl, "id", None)),
                learning_path_id=_safe_int(getattr(pl, "learning_path_id", None)),
                lesson_id=_safe_int(getattr(pl, "lesson_id", None)),
                order_index=_safe_int(getattr(pl, "order_index", None)),
                is_required=_safe_bool(getattr(pl, "is_required", False)),
                created_at=_safe_datetime(getattr(pl, "created_at", None), timestamp_fallback)
                or timestamp_fallback,
                lesson_title=_safe_str(getattr(lesson, "title", "")),
                lesson_description=_safe_optional_str(getattr(lesson, "description", None)),
                lesson_cover_image=_safe_optional_str(getattr(lesson, "cover_image_url", None)),
                lesson_difficulty=_safe_optional_str(difficulty_value),
                lesson_rating=_safe_float(getattr(lesson, "average_rating", 0.0)),
                lesson_duration=_safe_optional_int(getattr(lesson, "estimated_duration", None)),
            )
        )

    # 获取创建者信息
    creator = db.query(User).filter(User.id == getattr(learning_path, "creator_id", None)).first()
    creator_full_name = (
        _safe_optional_str(getattr(creator, "full_name", None)) if creator else None
    )
    creator_username = (
        _safe_optional_str(getattr(creator, "username", None)) if creator else None
    )
    creator_name = creator_full_name or creator_username or "未知"

    difficulty_attr = getattr(learning_path, "difficulty_level", None)
    difficulty_value = getattr(difficulty_attr, "value", difficulty_attr)
    timestamp_fallback = datetime.utcnow()

    return LearningPathWithLessons(
        id=_safe_int(getattr(learning_path, "id", None)),
        title=_safe_str(getattr(learning_path, "title", "")),
        description=_safe_optional_str(getattr(learning_path, "description", None)),
        creator_id=_safe_int(getattr(learning_path, "creator_id", None)),
        difficulty_level=_safe_str(difficulty_value, ""),
        cover_image_url=_safe_optional_str(getattr(learning_path, "cover_image_url", None)),
        is_published=_safe_bool(getattr(learning_path, "is_published", False)),
        estimated_hours=_safe_optional_int(getattr(learning_path, "estimated_hours", None)),
        created_at=_safe_datetime(getattr(learning_path, "created_at", None), timestamp_fallback)
        or timestamp_fallback,
        updated_at=_safe_datetime(getattr(learning_path, "updated_at", None), timestamp_fallback)
        or timestamp_fallback,
        lessons=lessons_details,
        lesson_count=len(lessons_details),
        creator_name=_safe_str(creator_name),
    )


@router.post(
    "/{path_id}/lessons",
    response_model=LearningPathLessonWithDetails,
    status_code=status.HTTP_201_CREATED,
)
def add_lesson_to_path(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    path_id: int,
    lesson_data: LearningPathLessonCreate,
):
    """
    向学习路径添加课程
    """
    learning_path = db.query(LearningPath).filter(LearningPath.id == path_id).first()
    if not learning_path:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="学习路径不存在")

    # 检查权限
    creator_id = getattr(learning_path, "creator_id", None)
    current_user_id = getattr(current_user, "id", None)
    current_user_role = _get_role_value(getattr(current_user, "role", None))
    is_admin = current_user_role == UserRole.ADMIN.value

    if creator_id != current_user_id and not is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权修改此学习路径")

    # 检查课程是否存在
    lesson = db.query(Lesson).filter(Lesson.id == lesson_data.lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="课程不存在")

    # 添加课程
    path_lesson = LearningPathLesson(
        learning_path_id=path_id,
        lesson_id=lesson_data.lesson_id,
        order_index=lesson_data.order_index,
        is_required=lesson_data.is_required,
    )
    db.add(path_lesson)
    db.commit()
    db.refresh(path_lesson)

    # 返回详细信息
    difficulty_attr = getattr(lesson, "difficulty_level", None)
    difficulty_value = getattr(difficulty_attr, "value", difficulty_attr)
    timestamp_fallback = datetime.utcnow()

    return LearningPathLessonWithDetails(
        id=_safe_int(getattr(path_lesson, "id", None)),
        learning_path_id=_safe_int(getattr(path_lesson, "learning_path_id", None)),
        lesson_id=_safe_int(getattr(path_lesson, "lesson_id", None)),
        order_index=_safe_int(getattr(path_lesson, "order_index", None)),
        is_required=_safe_bool(getattr(path_lesson, "is_required", False)),
        created_at=_safe_datetime(getattr(path_lesson, "created_at", None), timestamp_fallback)
        or timestamp_fallback,
        lesson_title=_safe_str(getattr(lesson, "title", "")),
        lesson_description=_safe_optional_str(getattr(lesson, "description", None)),
        lesson_cover_image=_safe_optional_str(getattr(lesson, "cover_image_url", None)),
        lesson_difficulty=_safe_optional_str(difficulty_value),
        lesson_rating=_safe_float(getattr(lesson, "average_rating", 0.0)),
        lesson_duration=_safe_optional_int(getattr(lesson, "estimated_duration", None)),
    )


@router.delete("/{path_id}/lessons/{lesson_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_lesson_from_path(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    path_id: int,
    lesson_id: int,
):
    """
    从学习路径移除课程
    """
    learning_path = db.query(LearningPath).filter(LearningPath.id == path_id).first()
    if not learning_path:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="学习路径不存在")

    # 检查权限
    creator_id = getattr(learning_path, "creator_id", None)
    current_user_id = getattr(current_user, "id", None)
    current_user_role = _get_role_value(getattr(current_user, "role", None))
    is_admin = current_user_role == UserRole.ADMIN.value

    if creator_id != current_user_id and not is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权修改此学习路径")

    path_lesson = (
        db.query(LearningPathLesson)
        .filter(
            LearningPathLesson.learning_path_id == path_id,
            LearningPathLesson.lesson_id == lesson_id,
        )
        .first()
    )

    if not path_lesson:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="该课程不在此学习路径中")

    db.delete(path_lesson)
    db.commit()

    return None
