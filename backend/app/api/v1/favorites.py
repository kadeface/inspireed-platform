"""
收藏相关API
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import desc, select
from typing import Any

from app.api.deps import get_db, get_current_active_user
from app.models import User, Favorite, Lesson
from app.schemas.favorite import FavoriteCreate, FavoriteResponse, FavoriteWithLesson

router = APIRouter()


@router.post("/", response_model=FavoriteResponse, status_code=status.HTTP_201_CREATED)
async def create_favorite(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    favorite_in: FavoriteCreate,
) -> Any:
    """
    创建收藏
    """
    # 检查课程是否存在
    result = await db.execute(select(Lesson).where(Lesson.id == favorite_in.lesson_id))
    lesson = result.scalar_one_or_none()
    if not lesson:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="课程不存在")

    # 检查是否已经收藏
    result = await db.execute(
        select(Favorite).where(
            Favorite.user_id == current_user.id, 
            Favorite.lesson_id == favorite_in.lesson_id
        )
    )
    existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="已经收藏过该课程")

    # 创建收藏
    favorite = Favorite(user_id=current_user.id, lesson_id=favorite_in.lesson_id)
    db.add(favorite)
    await db.commit()
    await db.refresh(favorite)

    return favorite


@router.delete("/{lesson_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_favorite(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    lesson_id: int,
) -> None:
    """
    取消收藏
    """
    result = await db.execute(
        select(Favorite).where(
            Favorite.user_id == current_user.id, 
            Favorite.lesson_id == lesson_id
        )
    )
    favorite = result.scalar_one_or_none()

    if not favorite:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="未收藏该课程")

    await db.delete(favorite)
    await db.commit()

    return None


@router.get("/", response_model=list[FavoriteWithLesson])
async def get_my_favorites(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    获取我的收藏列表
    """
    result_query = await db.execute(
        select(Favorite)
        .where(Favorite.user_id == current_user.id)
        .order_by(desc(Favorite.created_at))
        .offset(skip)
        .limit(limit)
    )
    favorites = result_query.scalars().all()

    # 组装返回数据
    result = []
    for fav in favorites:
        lesson_result = await db.execute(select(Lesson).where(Lesson.id == fav.lesson_id))
        lesson = lesson_result.scalar_one_or_none()
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
async def check_favorite(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    lesson_id: int,
) -> bool:
    """
    检查是否已收藏某课程
    """
    result = await db.execute(
        select(Favorite).where(
            Favorite.user_id == current_user.id, 
            Favorite.lesson_id == lesson_id
        )
    )
    favorite = result.scalar_one_or_none()

    return favorite is not None
