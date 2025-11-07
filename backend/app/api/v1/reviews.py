"""
评分评论相关API
"""

from typing import Optional, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func

from app.core.database import get_db
from app.api import deps
from app.models import User, Review, Lesson
from app.schemas.review import (
    ReviewCreate,
    ReviewUpdate,
    ReviewResponse,
    ReviewWithUser,
    LessonRatingStats,
)

router = APIRouter()


@router.post("/", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_review(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
    review_in: ReviewCreate,
) -> Any:
    """
    创建评论
    """
    # 检查课程是否存在
    result = await db.execute(select(Lesson).where(Lesson.id == review_in.lesson_id))
    lesson = result.scalar_one_or_none()
    if not lesson:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="课程不存在")

    # 检查是否已经评论过
    existing_result = await db.execute(
        select(Review).where(
            Review.user_id == current_user.id, Review.lesson_id == review_in.lesson_id
        )
    )
    existing = existing_result.scalar_one_or_none()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="已经评论过该课程，请使用更新接口"
        )

    # 创建评论
    review = Review(
        user_id=current_user.id,
        lesson_id=review_in.lesson_id,
        rating=review_in.rating,
        comment=review_in.comment,
    )
    db.add(review)
    await db.commit()

    # 更新课程的平均评分和评论数
    await _update_lesson_rating(db, review_in.lesson_id)

    await db.refresh(review)
    return review


@router.put("/{review_id}", response_model=ReviewResponse)
async def update_review(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
    review_id: int,
    review_in: ReviewUpdate,
) -> Any:
    """
    更新评论
    """
    result = await db.execute(select(Review).where(Review.id == review_id))
    review = result.scalar_one_or_none()
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="评论不存在")

    # 检查权限
    if review.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权修改此评论")

    # 更新评论
    review.rating = review_in.rating
    review.comment = review_in.comment
    await db.commit()

    # 更新课程的平均评分
    await _update_lesson_rating(db, review.lesson_id)

    await db.refresh(review)
    return review


@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_review(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
    review_id: int,
) -> None:
    """
    删除评论
    """
    result = await db.execute(select(Review).where(Review.id == review_id))
    review = result.scalar_one_or_none()
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="评论不存在")

    # 检查权限
    if review.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权删除此评论")

    lesson_id = review.lesson_id
    await db.delete(review)
    await db.commit()

    # 更新课程的平均评分
    await _update_lesson_rating(db, lesson_id)

    return None


@router.get("/lesson/{lesson_id}", response_model=list[ReviewWithUser])
async def get_lesson_reviews(
    *,
    db: AsyncSession = Depends(get_db),
    lesson_id: int,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    获取课程的所有评论
    """
    result = await db.execute(
        select(Review)
        .where(Review.lesson_id == lesson_id)
        .order_by(desc(Review.created_at))
        .offset(skip)
        .limit(limit)
    )
    reviews = result.scalars().all()

    # 组装返回数据
    review_list = []
    for review in reviews:
        user_result = await db.execute(select(User).where(User.id == review.user_id))
        user = user_result.scalar_one_or_none()
        review_list.append(
            ReviewWithUser(
                id=review.id,
                user_id=review.user_id,
                lesson_id=review.lesson_id,
                rating=review.rating,
                comment=review.comment,
                created_at=review.created_at,
                updated_at=review.updated_at,
                user_name=user.full_name or user.username if user else "未知用户",
                user_avatar=user.avatar_url if user else None,
            )
        )

    return review_list


@router.get("/lesson/{lesson_id}/stats", response_model=LessonRatingStats)
async def get_lesson_rating_stats(
    *, db: AsyncSession = Depends(get_db), lesson_id: int
) -> Any:
    """
    获取课程的评分统计
    """
    # 检查课程是否存在
    result = await db.execute(select(Lesson).where(Lesson.id == lesson_id))
    lesson = result.scalar_one_or_none()
    if not lesson:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="课程不存在")

    # 计算评分分布
    rating_distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    reviews_result = await db.execute(select(Review).where(Review.lesson_id == lesson_id))
    reviews = reviews_result.scalars().all()

    for review in reviews:
        rating_distribution[review.rating] += 1

    return LessonRatingStats(
        lesson_id=lesson_id,
        average_rating=lesson.average_rating,
        review_count=lesson.review_count,
        rating_distribution=rating_distribution,
    )


@router.get("/my/{lesson_id}", response_model=Optional[ReviewResponse])
async def get_my_review(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
    lesson_id: int,
) -> Any:
    """
    获取我对某课程的评论
    """
    result = await db.execute(
        select(Review).where(
            Review.user_id == current_user.id, Review.lesson_id == lesson_id
        )
    )
    review = result.scalar_one_or_none()

    return review


async def _update_lesson_rating(db: AsyncSession, lesson_id: int) -> None:
    """
    更新课程的平均评分和评论数
    """
    result = await db.execute(
        select(
            func.avg(Review.rating).label("avg_rating"),
            func.count(Review.id).label("count"),
        ).where(Review.lesson_id == lesson_id)
    )
    stats = result.first()

    lesson_result = await db.execute(select(Lesson).where(Lesson.id == lesson_id))
    lesson = lesson_result.scalar_one_or_none()
    if lesson and stats:
        lesson.average_rating = float(stats.avg_rating) if stats.avg_rating else 0.0
        lesson.review_count = stats.count if stats.count else 0
        await db.commit()
