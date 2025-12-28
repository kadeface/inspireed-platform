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
CURRENT_VERSION=$(docker exec inspireed-backend alembic current 2>&1 | grep -oP '^\w+' || echo "none")
echo "   当前版本: ${CURRENT_VERSION}"
echo ""

# 检查是否有失败的迁移
echo "🔍 检查数据库表状态..."
USERS_EXISTS=$(docker exec inspireed-backend python -c "
from sqlalchemy import inspect, text
from app.core.database import engine
import asyncio

async def check():
    async with engine.connect() as conn:
        inspector = inspect(conn.sync_engine)
        return 'users' in inspector.get_table_names()

result = asyncio.run(check())
print('yes' if result else 'no')
" 2>/dev/null || echo "error")

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
        docker exec inspireed-backend python -c "
from sqlalchemy import text
from app.core.database import engine
import asyncio

async def reset():
    async with engine.begin() as conn:
        # 检查 alembic_version 表是否存在
        result = await conn.execute(text(\"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'alembic_version')\"))
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

asyncio.run(reset())
" 2>&1
        
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
    docker exec inspireed-backend alembic upgrade head
fi

echo ""
echo "✅ 修复完成！"
echo ""
echo "📊 最终迁移状态："
docker exec inspireed-backend alembic current

