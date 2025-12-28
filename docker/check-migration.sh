#!/bin/bash
# 检查迁移状态和数据库连接的简单脚本

set -e

echo "🔍 检查迁移和数据库状态..."
echo ""

# 检查后端容器
if ! docker ps | grep -q inspireed-backend; then
    echo "❌ 后端容器未运行"
    exit 1
fi

# 1. 检查数据库连接
echo "1️⃣ 测试数据库连接..."
docker exec inspireed-backend python3 -c "
from app.core.config import settings
print(f'数据库 URI: {str(settings.DATABASE_URI).split(\"@\")[1] if \"@\" in str(settings.DATABASE_URI) else \"***\"}')
" 2>&1 || echo "❌ 无法读取配置"

# 2. 检查 alembic 命令
echo ""
echo "2️⃣ 检查 Alembic 命令..."
docker exec inspireed-backend which alembic 2>&1 || echo "❌ alembic 未安装"

# 3. 检查迁移版本
echo ""
echo "3️⃣ 检查迁移版本..."
docker exec inspireed-backend alembic current 2>&1 || echo "⚠️  无法获取版本（可能是新数据库）"

# 4. 检查数据库表
echo ""
echo "4️⃣ 检查数据库表..."
docker exec inspireed-backend python3 << 'PYTHON_SCRIPT'
import sys
try:
    from sqlalchemy import inspect, text
    from app.core.database import engine
    import asyncio

    async def check_tables():
        try:
            async with engine.connect() as conn:
                inspector = inspect(conn.sync_engine)
                tables = inspector.get_table_names()
                
                print(f"   数据库中的表数量: {len(tables)}")
                if tables:
                    print(f"   表列表: {', '.join(tables[:10])}")
                    if len(tables) > 10:
                        print(f"   ... 还有 {len(tables) - 10} 个表")
                
                # 检查关键表
                key_tables = ['users', 'alembic_version', 'subjects', 'courses']
                print("")
                print("   关键表状态:")
                for table in key_tables:
                    status = "✅" if table in tables else "❌"
                    print(f"     {status} {table}")
                
                return 'users' in tables
        except Exception as e:
            print(f"   ❌ 检查失败: {e}")
            return False

    result = asyncio.run(check_tables())
    sys.exit(0 if result else 1)
except Exception as e:
    print(f"   ❌ 脚本执行失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
PYTHON_SCRIPT

echo ""
echo "✅ 检查完成！"

