#!/bin/bash
# 测试数据库连接脚本
# 用于排查数据库连接问题

set -e

echo "🔍 测试数据库连接..."
echo ""

# 检查后端容器是否运行
if ! docker ps | grep -q inspireed-backend; then
    echo "❌ 错误：后端容器未运行"
    exit 1
fi

echo "1️⃣ 检查环境变量："
echo "   POSTGRES_SERVER:"
docker exec inspireed-backend env | grep POSTGRES_SERVER || echo "   ⚠️  未设置"
echo "   POSTGRES_USER:"
docker exec inspireed-backend env | grep POSTGRES_USER || echo "   ⚠️  未设置"
echo "   POSTGRES_DB:"
docker exec inspireed-backend env | grep POSTGRES_DB || echo "   ⚠️  未设置"
echo ""

echo "2️⃣ 检查应用配置："
echo "   数据库 URI (隐藏密码):"
docker exec inspireed-backend python -c "
from app.core.config import settings
uri = str(settings.DATABASE_URI)
if '@' in uri:
    parts = uri.split('@')
    print(f'   {parts[0].split(\":\")[0]}://***@{parts[1]}')
else:
    print(f'   {uri}')
" 2>&1 || echo "   ❌ 无法读取配置"
echo ""

echo "3️⃣ 测试网络连接："
echo "   测试连接到 postgres 服务:"
docker exec inspireed-backend ping -c 2 postgres 2>&1 | head -3 || echo "   ❌ 无法连接到 postgres"
echo ""

echo "4️⃣ 测试数据库连接（使用 Python）："
docker exec inspireed-backend python -c "
import asyncio
from app.core.database import engine

async def test_connection():
    try:
        async with engine.connect() as conn:
            result = await conn.execute('SELECT 1')
            print('   ✅ 数据库连接成功')
            return True
    except Exception as e:
        print(f'   ❌ 数据库连接失败: {e}')
        return False

asyncio.run(test_connection())
" 2>&1 || echo "   ❌ 测试失败"
echo ""

echo "5️⃣ 测试 Alembic 配置："
echo "   检查 Alembic 使用的数据库 URL:"
docker exec inspireed-backend python -c "
from app.core.config import settings
from alembic import context
from alembic.config import Config

config = Config('alembic.ini')
config.set_main_option('sqlalchemy.url', str(settings.DATABASE_URI))
url = config.get_main_option('sqlalchemy.url')
if '@' in url:
    parts = url.split('@')
    print(f'   {parts[0].split(\":\")[0]}://***@{parts[1]}')
else:
    print(f'   {url}')
" 2>&1 || echo "   ⚠️  无法检查"
echo ""

echo "✅ 测试完成！"

