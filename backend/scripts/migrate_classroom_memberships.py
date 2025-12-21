"""
数据补齐脚本：从 User.classroom_id 回填 classroom_memberships

使用方法：
    python -m scripts.migrate_classroom_memberships

注意：运行前请备份数据库
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.models import User, Classroom, ClassroomMembership, RoleInClass


async def migrate_classroom_memberships():
    """将 User.classroom_id 的学生数据迁移到 classroom_memberships"""
    async with AsyncSessionLocal() as db:
        try:
            # 查找所有有 classroom_id 的学生
            result = await db.execute(
                select(User).where(
                    User.classroom_id.isnot(None),
                    User.role == "student",
                )
            )
            users = result.scalars().all()
            
            print(f"找到 {len(users)} 个需要迁移的学生")
            
            migrated_count = 0
            skipped_count = 0
            error_count = 0
            
            for user in users:
                try:
                    classroom_id = user.classroom_id
                    if not classroom_id:
                        continue
                    
                    # 检查班级是否存在
                    classroom = await db.get(Classroom, classroom_id)
                    if not classroom:
                        print(f"⚠️  用户 {user.id} ({user.username}) 的班级 {classroom_id} 不存在，跳过")
                        skipped_count += 1
                        continue
                    
                    # 检查是否已存在成员关系
                    existing = await db.execute(
                        select(ClassroomMembership).where(
                            ClassroomMembership.user_id == user.id,
                            ClassroomMembership.classroom_id == classroom_id,
                        )
                    )
                    if existing.scalar_one_or_none():
                        print(f"⏭️  用户 {user.id} ({user.username}) 已存在成员关系，跳过")
                        skipped_count += 1
                        continue
                    
                    # 创建成员关系
                    membership = ClassroomMembership(
                        classroom_id=classroom_id,
                        user_id=user.id,
                        role_in_class=RoleInClass.STUDENT,
                        is_active=True,
                        is_primary_class=True,  # 标记为主班级
                    )
                    db.add(membership)
                    migrated_count += 1
                    print(f"✅ 已创建用户 {user.id} ({user.username}) 的成员关系")
                    
                except Exception as e:
                    print(f"❌ 处理用户 {user.id} ({user.username}) 时出错: {e}")
                    error_count += 1
                    continue
            
            # 提交所有更改
            await db.commit()
            
            print("\n" + "=" * 50)
            print(f"迁移完成！")
            print(f"  - 成功迁移: {migrated_count} 个")
            print(f"  - 跳过: {skipped_count} 个")
            print(f"  - 错误: {error_count} 个")
            print("=" * 50)
            
        except Exception as e:
            await db.rollback()
            print(f"❌ 迁移过程出错: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(migrate_classroom_memberships())
