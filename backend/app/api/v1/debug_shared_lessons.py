"""
调试脚本：诊断共享教案显示问题
用于排查为什么教研组显示有N个教案，但列表中不显示
"""
from typing import cast, Optional
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_db, get_current_user
from app.models.subject_group import SubjectGroup, SharedLesson, GroupMembership
from app.models.lesson import Lesson
from app.models.user import User

router = APIRouter()


@router.get("/debug/group/{group_id}/lessons")
async def debug_shared_lessons(
    group_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """
    诊断共享教案显示问题
    返回详细的调试信息，包括：
    - 教研组基本信息
    - 统计字段 vs 实际数量
    - 所有共享教案详情（包括软删除的）
    - 权限检查结果
    - 关联教案的状态
    """
    
    # 1. 检查教研组是否存在
    group = await db.get(SubjectGroup, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="教研组不存在")
    
    group_info = {
        "id": group.id,
        "name": group.name,
        "is_active": group.is_active,
        "is_public": group.is_public,
        "lesson_count": group.lesson_count,  # 统计字段
    }
    
    # 2. 检查用户权限
    user_membership = await db.scalar(
        select(GroupMembership).where(
            and_(
                GroupMembership.group_id == group_id,
                GroupMembership.user_id == cast(int, current_user.id),
            )
        )
    )
    
    permission_info = {
        "is_member": user_membership is not None,
        "membership_active": user_membership.is_active if user_membership else None,
        "user_role": user_membership.role if user_membership else None,
        "can_access": user_membership is not None or cast(bool, group.is_public),
    }
    
    # 3. 查询所有共享教案（包括软删除的）
    all_shared_lessons = await db.execute(
        select(SharedLesson).where(SharedLesson.group_id == group_id)
    )
    all_lessons_list = all_shared_lessons.scalars().all()
    
    # 4. 统计信息
    active_count = sum(1 for sl in all_lessons_list if sl.is_active)
    inactive_count = sum(1 for sl in all_lessons_list if not sl.is_active)
    
    statistics = {
        "total_in_db": len(all_lessons_list),
        "active_count": active_count,
        "inactive_count": inactive_count,
        "stored_lesson_count": group.lesson_count,
        "count_mismatch": group.lesson_count != active_count,
    }
    
    # 5. 详细教案信息
    lessons_detail = []
    for shared_lesson in all_lessons_list:
        # 获取关联的教案信息
        lesson = await db.get(Lesson, shared_lesson.lesson_id)
        
        # 获取分享者信息
        sharer = await db.get(User, shared_lesson.sharer_id)
        
        lesson_info = {
            "shared_lesson_id": shared_lesson.id,
            "lesson_id": shared_lesson.lesson_id,
            "is_active": shared_lesson.is_active,
            "shared_at": shared_lesson.shared_at.isoformat() if shared_lesson.shared_at else None,
            "share_note": shared_lesson.share_note,
            "view_count": shared_lesson.view_count,
            "download_count": shared_lesson.download_count,
            
            # 教案信息
            "lesson_exists": lesson is not None,
            "lesson_title": lesson.title if lesson else None,
            "lesson_is_active": lesson.is_active if lesson else None,
            "lesson_is_public": lesson.is_public if lesson else None,
            "lesson_creator_id": lesson.creator_id if lesson else None,
            "lesson_cell_count": lesson.cell_count if lesson else None,
            
            # 分享者信息
            "sharer_id": shared_lesson.sharer_id,
            "sharer_name": sharer.full_name if sharer else None,
            "sharer_username": sharer.username if sharer else None,
            "sharer_is_active": sharer.is_active if sharer else None,
        }
        
        # 判断为什么不显示
        reasons_not_shown = []
        if not shared_lesson.is_active:
            reasons_not_shown.append("共享记录已软删除 (is_active=false)")
        if not lesson:
            reasons_not_shown.append("关联的教案不存在（已被删除）")
        elif not lesson.is_active:
            reasons_not_shown.append("关联的教案已被停用 (lesson.is_active=false)")
        if not permission_info["can_access"]:
            reasons_not_shown.append("用户无权限访问（非成员且非公开教研组）")
        
        lesson_info["reasons_not_shown"] = reasons_not_shown
        lesson_info["should_show"] = len(reasons_not_shown) == 0
        
        lessons_detail.append(lesson_info)
    
    # 6. 返回完整诊断信息
    return {
        "group_info": group_info,
        "permission_info": permission_info,
        "statistics": statistics,
        "lessons_detail": lessons_detail,
        "diagnosis": {
            "problem_detected": statistics["count_mismatch"] or not permission_info["can_access"],
            "likely_causes": get_likely_causes(statistics, permission_info, lessons_detail),
        },
    }


def get_likely_causes(statistics: dict, permission_info: dict, lessons_detail: list) -> list:
    """分析可能的原因"""
    causes = []
    
    # 权限问题
    if not permission_info["can_access"]:
        causes.append("🔒 权限问题：用户不是教研组成员，且教研组为私密")
    
    # 统计不一致
    if statistics["count_mismatch"]:
        causes.append(
            f"📊 统计不一致：lesson_count={statistics['stored_lesson_count']}, "
            f"实际激活数量={statistics['active_count']}"
        )
    
    # 软删除问题
    if statistics["inactive_count"] > 0:
        causes.append(f"🗑️ 有 {statistics['inactive_count']} 个教案被软删除（is_active=false）")
    
    # 教案缺失
    missing_lessons = sum(1 for l in lessons_detail if not l["lesson_exists"])
    if missing_lessons > 0:
        causes.append(f"❌ 有 {missing_lessons} 个共享记录的关联教案不存在（已被删除）")
    
    # 教案停用
    inactive_lessons = sum(
        1 for l in lessons_detail 
        if l["lesson_exists"] and not l.get("lesson_is_active", True)
    )
    if inactive_lessons > 0:
        causes.append(f"⚠️ 有 {inactive_lessons} 个关联的教案被停用")
    
    # 如果所有教案都应该显示但没显示
    should_show_count = sum(1 for l in lessons_detail if l["should_show"])
    if should_show_count > 0 and should_show_count == statistics["active_count"]:
        causes.append("✅ 数据正常，可能是前端缓存或加载问题")
    
    if not causes:
        causes.append("✅ 未发现明显问题，数据状态正常")
    
    return causes
