#!/bin/bash
# 修复迁移状态脚本
# 用于解决迁移失败后的数据库状态问题

set -e

echo "🔧 修复迁移状态..."
echo ""

# 检查后端容器是否运行
if ! docker ps | grep -q inspireed-backend; then
    echo "❌ 错误：后端容器未运行"
    echo "   请先启动后端服务："
    echo "   docker-compose -f docker-compose.prod.yml up -d backend"
    exit 1
fi

echo "📊 检查当前迁移状态..."
CURRENT_VERSION_OUTPUT=$(docker exec inspireed-backend alembic current 2>&1)
if echo "$CURRENT_VERSION_OUTPUT" | grep -q "version_num"; then
    CURRENT_VERSION=$(echo "$CURRENT_VERSION_OUTPUT" | grep "version_num" | awk '{print $1}' || echo "unknown")
    echo "   当前版本: ${CURRENT_VERSION}"
else
    echo "   ⚠️  无法获取当前版本（可能是新数据库）"
    CURRENT_VERSION="none"
fi
echo ""

# 检查是否有失败的迁移
echo "🔍 检查数据库表状态..."
USERS_EXISTS=$(docker exec inspireed-backend python3 -c "
import sys
try:
    from sqlalchemy import inspect, text
    from app.core.database import engine
    import asyncio

    async def check():
        try:
            async with engine.connect() as conn:
                inspector = inspect(conn.sync_engine)
                tables = inspector.get_table_names()
                return 'users' in tables
        except Exception as e:
            print(f'检查错误: {e}', file=sys.stderr)
            return False

    result = asyncio.run(check())
    print('yes' if result else 'no')
except Exception as e:
    print(f'导入错误: {e}', file=sys.stderr)
    print('error')
    sys.exit(1)
" 2>&1)

# 检查输出
if echo "$USERS_EXISTS" | grep -q "error\|Error\|Traceback"; then
    USERS_EXISTS="error"
    echo "   ⚠️  检查过程中出现错误"
    echo "   错误信息:"
    echo "$USERS_EXISTS" | head -5 | sed 's/^/      /'
else
    USERS_EXISTS=$(echo "$USERS_EXISTS" | tail -1)
fi

if [ "$USERS_EXISTS" = "error" ]; then
    echo "⚠️  无法检查数据库状态"
    echo "   请手动检查数据库"
    exit 1
fi

if [ "$USERS_EXISTS" = "no" ]; then
    echo "⚠️  users 表不存在"
    echo ""
    echo "💡 解决方案："
    echo "   1. 重置迁移版本（如果迁移部分完成）"
    echo "   2. 重新运行迁移"
    echo ""
    read -p "是否要重置迁移版本到 001？(y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🔄 重置迁移版本..."
        docker exec inspireed-backend python3 -c "
import sys
try:
    from sqlalchemy import text
    from app.core.database import engine
    import asyncio

    async def reset():
        try:
            async with engine.begin() as conn:
                # 检查 alembic_version 表是否存在
                result = await conn.execute(text(\"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'alembic_version')\"))
                exists = result.scalar()
                
                if exists:
                    # 更新版本为 001
                    await conn.execute(text(\"UPDATE alembic_version SET version_num = '001'\"))
                    print('✅ 迁移版本已重置为 001')
                else:
                    # 创建 alembic_version 表并设置版本
                    await conn.execute(text(\"CREATE TABLE alembic_version (version_num VARCHAR(32) NOT NULL, CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num))\"))
                    await conn.execute(text(\"INSERT INTO alembic_version (version_num) VALUES ('001')\"))
                    print('✅ 创建 alembic_version 表并设置版本为 001')
        except Exception as e:
            print(f'❌ 重置失败: {e}', file=sys.stderr)
            sys.exit(1)

    asyncio.run(reset())
except Exception as e:
    print(f'❌ 脚本执行失败: {e}', file=sys.stderr)
    sys.exit(1)
" 2>&1
        
        if [ $? -ne 0 ]; then
            echo "❌ 重置迁移版本失败"
            echo "   请手动检查数据库连接和权限"
            exit 1
        fi
        
        echo ""
        echo "🔄 重新运行迁移..."
        docker exec inspireed-backend alembic upgrade head
    else
        echo "   取消操作"
        exit 0
    fi
else
    echo "✅ users 表已存在"
    echo ""
    echo "🔄 继续运行迁移..."
    if docker exec inspireed-backend alembic upgrade head; then
        echo "✅ 迁移完成"
    else
        echo "❌ 迁移失败，请查看错误信息"
        exit 1
    fi
fi

echo ""
echo "✅ 修复完成！"
echo ""
echo "📊 最终迁移状态："
docker exec inspireed-backend alembic current 2>&1 || echo "⚠️  无法获取迁移状态"

