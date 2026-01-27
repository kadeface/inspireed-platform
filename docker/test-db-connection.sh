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
echo "   测试连接到 postgres 服务 (使用 Python socket):"
docker exec inspireed-backend python -c "
import socket
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)
    result = sock.connect_ex(('postgres', 5432))
    sock.close()
    if result == 0:
        print('   ✅ 可以连接到 postgres:5432')
    else:
        print(f'   ❌ 无法连接到 postgres:5432 (错误码: {result})')
except Exception as e:
    print(f'   ❌ 连接测试失败: {e}')
" 2>&1 || echo "   ⚠️  网络测试失败"
echo ""

echo "4️⃣ 测试数据库连接（使用 Python）："
docker exec inspireed-backend python -c "
import asyncio
import sys
from app.core.config import settings
from app.core.database import engine

async def test_connection():
    try:
        print(f'   尝试连接: {str(settings.DATABASE_URI).split(\"@\")[1] if \"@\" in str(settings.DATABASE_URI) else \"***\"}')
        async with engine.connect() as conn:
            result = await conn.execute('SELECT 1')
            print('   ✅ 数据库连接成功')
            return True
    except Exception as e:
        error_msg = str(e)
        print(f'   ❌ 数据库连接失败')
        print(f'   错误类型: {type(e).__name__}')
        print(f'   错误信息: {error_msg[:200]}')
        
        # 提供诊断建议
        if 'Name or service not known' in error_msg or 'gaierror' in error_msg:
            print('   💡 诊断: DNS 解析失败，可能的原因：')
            print('      1. 容器不在同一个 Docker 网络中')
            print('      2. postgres 服务名无法解析')
            print('      3. 网络配置问题')
        elif 'Connection refused' in error_msg or 'refused' in error_msg.lower():
            print('   💡 诊断: 连接被拒绝，可能的原因：')
            print('      1. PostgreSQL 服务未启动')
            print('      2. 端口不正确')
            print('      3. 防火墙阻止连接')
        elif 'authentication' in error_msg.lower() or 'password' in error_msg.lower():
            print('   💡 诊断: 认证失败，检查用户名和密码')
        
        return False

asyncio.run(test_connection())
" 2>&1 || echo "   ❌ 测试失败"
echo ""

echo "5️⃣ 检查容器网络："
echo "   后端容器网络:"
docker inspect inspireed-backend --format='{{range .NetworkSettings.Networks}}{{.NetworkID}} ({{.IPAddress}}){{end}}' 2>&1 || echo "   ⚠️  无法获取"
echo "   PostgreSQL 容器网络:"
docker inspect inspireed-postgres --format='{{range .NetworkSettings.Networks}}{{.NetworkID}} ({{.IPAddress}}){{end}}' 2>&1 || echo "   ⚠️  无法获取"
echo "   检查是否在同一网络:"
BACKEND_NET=$(docker inspect inspireed-backend --format='{{range $k, $v := .NetworkSettings.Networks}}{{$k}}{{end}}' 2>/dev/null)
POSTGRES_NET=$(docker inspect inspireed-postgres --format='{{range $k, $v := .NetworkSettings.Networks}}{{$k}}{{end}}' 2>/dev/null)
if [ "$BACKEND_NET" = "$POSTGRES_NET" ] && [ -n "$BACKEND_NET" ]; then
    echo "   ✅ 容器在同一网络中: $BACKEND_NET"
else
    echo "   ❌ 容器不在同一网络中"
    echo "      后端: $BACKEND_NET"
    echo "      PostgreSQL: $POSTGRES_NET"
fi
echo ""

echo "6️⃣ 测试 Alembic 配置："
echo "   检查 Alembic 使用的数据库 URL:"
docker exec inspireed-backend python -c "
from app.core.config import settings
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

