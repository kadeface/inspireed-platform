"""
评分评论相关API
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

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
def create_review(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    review_in: ReviewCreate,
):
    """
    创建评论
    """
    # 检查课程是否存在
    lesson = db.query(Lesson).filter(Lesson.id == review_in.lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="课程不存在")

    # 检查是否已经评论过
    existing = (
        db.query(Review)
        .filter(Review.user_id == current_user.id, Review.lesson_id == review_in.lesson_id)
        .first()
    )

    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="已经评论过该课程，请使用更新接口")

    # 创建评论
    review = Review(
        user_id=current_user.id,
        lesson_id=review_in.lesson_id,
        rating=review_in.rating,
        comment=review_in.comment,
    )
    db.add(review)
    db.commit()

    # 更新课程的平均评分和评论数
    _update_lesson_rating(db, review_in.lesson_id)

    db.refresh(review)
    return review


@router.put("/{review_id}", response_model=ReviewResponse)
def update_review(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    review_id: int,
    review_in: ReviewUpdate,
):
    """
    更新评论
    """
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="评论不存在")

    # 检查权限
    if review.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权修改此评论")

    # 更新评论
    review.rating = review_in.rating
    review.comment = review_in.comment
    db.commit()

    # 更新课程的平均评分
    _update_lesson_rating(db, review.lesson_id)

    db.refresh(review)
    return review


@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_review(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    review_id: int,
):
    """
    删除评论
    """
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="评论不存在")

    # 检查权限
    if review.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权删除此评论")

    lesson_id = review.lesson_id
    db.delete(review)
    db.commit()

    # 更新课程的平均评分
    _update_lesson_rating(db, lesson_id)

    return None


@router.get("/lesson/{lesson_id}", response_model=list[ReviewWithUser])
def get_lesson_reviews(
    *, db: Session = Depends(deps.get_db), lesson_id: int, skip: int = 0, limit: int = 100
):
    """
    获取课程的所有评论
    """
    reviews = (
        db.query(Review)
        .filter(Review.lesson_id == lesson_id)
        .order_by(desc(Review.created_at))
        .offset(skip)
        .limit(limit)
        .all()
    )

    # 组装返回数据
    result = []
    for review in reviews:
        user = db.query(User).filter(User.id == review.user_id).first()
        result.append(
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

    return result


@router.get("/lesson/{lesson_id}/stats", response_model=LessonRatingStats)
def get_lesson_rating_stats(*, db: Session = Depends(deps.get_db), lesson_id: int):
    """
    获取课程的评分统计
    """
    # 检查课程是否存在
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="课程不存在")

    # 计算评分分布
    rating_distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    reviews = db.query(Review).filter(Review.lesson_id == lesson_id).all()

    for review in reviews:
        rating_distribution[review.rating] += 1

    return LessonRatingStats(
        lesson_id=lesson_id,
        average_rating=lesson.average_rating,
        review_count=lesson.review_count,
        rating_distribution=rating_distribution,
    )


@router.get("/my/{lesson_id}", response_model=Optional[ReviewResponse])
def get_my_review(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    lesson_id: int,
):
    """
    获取我对某课程的评论
    """
    review = (
        db.query(Review)
        .filter(Review.user_id == current_user.id, Review.lesson_id == lesson_id)
        .first()
    )

    return review


def _update_lesson_rating(db: Session, lesson_id: int):
    """
    更新课程的平均评分和评论数
    """
    result = (
        db.query(func.avg(Review.rating).label("avg_rating"), func.count(Review.id).label("count"))
        .filter(Review.lesson_id == lesson_id)
        .first()
    )

    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if lesson:
        lesson.average_rating = float(result.avg_rating) if result.avg_rating else 0.0
        lesson.review_count = result.count if result.count else 0
        db.commit()
