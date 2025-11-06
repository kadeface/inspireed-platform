"""
收藏相关API
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.api import deps
from app.models import User, Favorite, Lesson
from app.schemas.favorite import FavoriteCreate, FavoriteResponse, FavoriteWithLesson

router = APIRouter()


@router.post("/", response_model=FavoriteResponse, status_code=status.HTTP_201_CREATED)
def create_favorite(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    favorite_in: FavoriteCreate,
):
    """
    创建收藏
    """
    # 检查课程是否存在
    lesson = db.query(Lesson).filter(Lesson.id == favorite_in.lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="课程不存在")

    # 检查是否已经收藏
    existing = (
        db.query(Favorite)
        .filter(Favorite.user_id == current_user.id, Favorite.lesson_id == favorite_in.lesson_id)
        .first()
    )

    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="已经收藏过该课程")

    # 创建收藏
    favorite = Favorite(user_id=current_user.id, lesson_id=favorite_in.lesson_id)
    db.add(favorite)
    db.commit()
    db.refresh(favorite)

    return favorite


@router.delete("/{lesson_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_favorite(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    lesson_id: int,
):
    """
    取消收藏
    """
    favorite = (
        db.query(Favorite)
        .filter(Favorite.user_id == current_user.id, Favorite.lesson_id == lesson_id)
        .first()
    )

    if not favorite:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="未收藏该课程")

    db.delete(favorite)
    db.commit()

    return None


@router.get("/", response_model=list[FavoriteWithLesson])
def get_my_favorites(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    skip: int = 0,
    limit: int = 100,
):
    """
    获取我的收藏列表
    """
    favorites = (
        db.query(Favorite)
        .filter(Favorite.user_id == current_user.id)
        .order_by(desc(Favorite.created_at))
        .offset(skip)
        .limit(limit)
        .all()
    )

    # 组装返回数据
    result = []
    for fav in favorites:
        lesson = db.query(Lesson).filter(Lesson.id == fav.lesson_id).first()
        if lesson:
            result.append(
                FavoriteWithLesson(
                    id=fav.id,
                    user_id=fav.user_id,
                    lesson_id=fav.lesson_id,
                    created_at=fav.created_at,
                    lesson_title=lesson.title,
                    lesson_description=lesson.description,
                    lesson_cover_image=lesson.cover_image_url,
                    lesson_difficulty=(
                        lesson.difficulty_level.value if lesson.difficulty_level else None
                    ),
                    lesson_rating=lesson.average_rating,
                )
            )

    return result


@router.get("/check/{lesson_id}", response_model=bool)
def check_favorite(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    lesson_id: int,
):
    """
    检查是否已收藏某课程
    """
    favorite = (
        db.query(Favorite)
        .filter(Favorite.user_id == current_user.id, Favorite.lesson_id == lesson_id)
        .first()
    )

    return favorite is not None
