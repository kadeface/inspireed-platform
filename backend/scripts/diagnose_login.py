"""
诊断登录问题
检查数据库连接、用户数据、密码验证等
"""

import asyncio
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.core.security import verify_password, get_password_hash
from app.models import User
import traceback


async def diagnose_login():
    """诊断登录相关问题"""
    print("🔍 开始诊断登录问题...\n")
    
    try:
        # 1. 测试数据库连接
        print("1️⃣ 测试数据库连接...")
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(User).limit(1))
            user_count = result.scalar_one_or_none()
            print("   ✅ 数据库连接正常")
        print()
        
        # 2. 检查admin用户
        print("2️⃣ 检查admin用户...")
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(User).where(User.username == "admin")
            )
            user = result.scalar_one_or_none()
            
            if user:
                print(f"   ✅ 找到admin用户")
                print(f"      ID: {user.id}")
                print(f"      用户名: {user.username}")
                print(f"      邮箱: {user.email}")
                print(f"      角色: {user.role}")
                print(f"      激活状态: {user.is_active}")
                print(f"      密码哈希: {user.hashed_password[:20]}..." if user.hashed_password else "      密码哈希: None")
            else:
                print("   ❌ 未找到admin用户")
                print("   💡 建议运行: python scripts/ensure_admin_user_simple.py")
                return
        print()
        
        # 3. 测试密码验证
        print("3️⃣ 测试密码验证...")
        test_password = "admin123"
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(User).where(User.username == "admin")
            )
            user = result.scalar_one_or_none()
            
            if user and user.hashed_password:
                try:
                    is_valid = verify_password(test_password, str(user.hashed_password))
                    if is_valid:
                        print(f"   ✅ 密码验证成功 (密码: {test_password})")
                    else:
                        print(f"   ❌ 密码验证失败 (密码: {test_password})")
                        print("   💡 建议运行: python scripts/ensure_admin_user_simple.py")
                except Exception as e:
                    print(f"   ❌ 密码验证出错: {type(e).__name__}: {e}")
                    print(f"   错误详情:")
                    print(traceback.format_exc())
                    print("   💡 可能是 bcrypt 版本问题，建议:")
                    print("      pip install --upgrade 'bcrypt==3.2.2'")
                    print("      或运行: python scripts/ensure_admin_user_simple.py")
            else:
                print("   ⚠️  无法测试：用户或密码哈希不存在")
        print()
        
        # 4. 测试密码哈希生成
        print("4️⃣ 测试密码哈希生成...")
        try:
            test_hash = get_password_hash(test_password)
            print(f"   ✅ 密码哈希生成成功")
            print(f"      哈希值: {test_hash[:30]}...")
        except Exception as e:
            print(f"   ❌ 密码哈希生成失败: {type(e).__name__}: {e}")
            print(f"   错误详情:")
            print(traceback.format_exc())
            print("   💡 可能是 bcrypt 版本问题，建议:")
            print("      pip install --upgrade 'bcrypt==3.2.2'")
        print()
        
        # 5. 检查配置
        print("5️⃣ 检查配置...")
        from app.core.config import settings
        print(f"   SECRET_KEY: {'已设置' if settings.SECRET_KEY else '❌ 未设置'}")
        print(f"   ACCESS_TOKEN_EXPIRE_MINUTES: {settings.ACCESS_TOKEN_EXPIRE_MINUTES}")
        print(f"   ALGORITHM: {settings.ALGORITHM}")
        print()
        
        print("=" * 50)
        print("✅ 诊断完成")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n❌ 诊断过程出错: {type(e).__name__}: {e}")
        print(traceback.format_exc())


if __name__ == "__main__":
    asyncio.run(diagnose_login())

