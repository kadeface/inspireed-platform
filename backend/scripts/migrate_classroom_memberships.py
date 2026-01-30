"""
数据迁移脚本：为所有用户创建 ClassroomMembership 记录
将 User.classroom_id 迁移到 ClassroomMembership，确保数据一致性
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from app.core.config import settings


async def migrate_classroom_memberships():
    """为所有有 classroom_id 但没有 ClassroomMembership 的用户创建记录"""
    
    # 创建数据库引擎
    database_url = str(settings.DATABASE_URI)
    engine = create_async_engine(
        database_url,
        echo=False,
        future=True,
    )
    
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as db:
        print("=" * 80)
        print("数据迁移：为所有用户创建 ClassroomMembership 记录")
        print("=" * 80)
        print()
        
        # 1. 查找所有有 classroom_id 但没有 ClassroomMembership 的用户
        print("1. 查找需要迁移的用户...")
        result = await db.execute(
            text("""
                SELECT u.id, u.username, u.full_name, u.classroom_id, u.role
                FROM users u
                WHERE u.classroom_id IS NOT NULL
                  AND NOT EXISTS (
                      SELECT 1 
                      FROM classroom_memberships cm
                      WHERE cm.user_id = u.id 
                        AND cm.classroom_id = u.classroom_id
                        AND cm.is_active = true
                  )
            """)
        )
        users_to_migrate = result.fetchall()
        
        if not users_to_migrate:
            print("✅ 所有用户都已经有 ClassroomMembership 记录，无需迁移")
            return
        
        print(f"找到 {len(users_to_migrate)} 个需要迁移的用户")
        print()
        
        # 2. 统计信息
        print("2. 统计信息...")
        student_count = sum(1 for u in users_to_migrate if u[4] == 'student')
        teacher_count = sum(1 for u in users_to_migrate if u[4] == 'teacher')
        other_count = len(users_to_migrate) - student_count - teacher_count
        
        print(f"   学生: {student_count} 人")
        print(f"   教师: {teacher_count} 人")
        print(f"   其他: {other_count} 人")
        print()
        
        # 3. 执行迁移
        print("3. 执行迁移...")
        migrated_count = 0
        error_count = 0
        
        for user_row in users_to_migrate:
            user_id = user_row[0]
            username = user_row[1]
            full_name = user_row[2]
            classroom_id = user_row[3]
            user_role = user_row[4]
            
            try:
                # 确定角色
                if user_role == 'student':
                    role_in_class = 'student'
                elif user_role == 'teacher':
                    role_in_class = 'teacher'
                else:
                    # 其他角色默认为学生
                    role_in_class = 'student'
                
                # 检查是否已存在（可能是不活跃的记录）
                result = await db.execute(
                    text("""
                        SELECT id, is_active, role_in_class
                        FROM classroom_memberships
                        WHERE user_id = :user_id AND classroom_id = :classroom_id
                    """).bindparams(user_id=user_id, classroom_id=classroom_id)
                )
                existing = result.fetchone()
                
                if existing:
                    # 如果存在但不活跃，激活它并设置为主班级
                    await db.execute(
                        text("""
                            UPDATE classroom_memberships
                            SET is_active = true,
                                is_primary_class = true,
                                role_in_class = COALESCE(role_in_class, :role_in_class),
                                updated_at = NOW()
                            WHERE id = :id
                        """).bindparams(
                            id=existing[0],
                            role_in_class=role_in_class
                        )
                    )
                    print(f"   ✅ 更新: {username} ({full_name}) - 班级 {classroom_id}")
                else:
                    # 创建新记录
                    await db.execute(
                        text("""
                            INSERT INTO classroom_memberships 
                            (classroom_id, user_id, role_in_class, is_active, is_primary_class, created_at, updated_at)
                            VALUES 
                            (:classroom_id, :user_id, :role_in_class, true, true, NOW(), NOW())
                        """).bindparams(
                            classroom_id=classroom_id,
                            user_id=user_id,
                            role_in_class=role_in_class
                        )
                    )
                    print(f"   ✅ 创建: {username} ({full_name}) - 班级 {classroom_id}")
                
                migrated_count += 1
                
            except Exception as e:
                error_count += 1
                print(f"   ❌ 错误: {username} ({full_name}) - {str(e)}")
                import traceback
                traceback.print_exc()
        
        # 提交更改
        try:
            await db.commit()
            print()
            print(f"✅ 迁移完成: 成功 {migrated_count} 条，失败 {error_count} 条")
        except Exception as e:
            await db.rollback()
            print()
            print(f"❌ 提交失败: {str(e)}")
            return
        
        print()
        
        # 4. 验证迁移结果
        print("4. 验证迁移结果...")
        result = await db.execute(
            text("""
                SELECT COUNT(*) 
                FROM users u
                WHERE u.classroom_id IS NOT NULL
                  AND NOT EXISTS (
                      SELECT 1 
                      FROM classroom_memberships cm
                      WHERE cm.user_id = u.id 
                        AND cm.classroom_id = u.classroom_id
                        AND cm.is_active = true
                  )
            """)
        )
        remaining = result.scalar()
        
        if remaining == 0:
            print("✅ 所有用户都已迁移完成")
        else:
            print(f"⚠️ 仍有 {remaining} 个用户未迁移")
        
        print()
        print("=" * 80)
        print("迁移完成")
        print("=" * 80)
    
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(migrate_classroom_memberships())
