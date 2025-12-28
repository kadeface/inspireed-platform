#!/bin/bash
# 修复容器网络问题
# 确保所有容器都在同一个 Docker 网络中

set -e

echo "🔧 修复容器网络配置..."
echo ""

# 检查是否在正确的目录
if [ ! -f "docker-compose.prod.yml" ]; then
    echo "❌ 错误：请在 docker 目录下运行此脚本"
    exit 1
fi

# 1. 检查当前网络状态
echo "📊 检查当前网络状态："
echo ""

BACKEND_NET=$(docker inspect inspireed-backend --format='{{range $k, $v := .NetworkSettings.Networks}}{{$k}}{{end}}' 2>/dev/null || echo "")
POSTGRES_NET=$(docker inspect inspireed-postgres --format='{{range $k, $v := .NetworkSettings.Networks}}{{$k}}{{end}}' 2>/dev/null || echo "")
REDIS_NET=$(docker inspect inspireed-redis --format='{{range $k, $v := .NetworkSettings.Networks}}{{$k}}{{end}}' 2>/dev/null || echo "")
MINIO_NET=$(docker inspect inspireed-minio --format='{{range $k, $v := .NetworkSettings.Networks}}{{$k}}{{end}}' 2>/dev/null || echo "")

echo "   后端容器网络: ${BACKEND_NET:-未运行}"
echo "   PostgreSQL 容器网络: ${POSTGRES_NET:-未运行}"
echo "   Redis 容器网络: ${REDIS_NET:-未运行}"
echo "   MinIO 容器网络: ${MINIO_NET:-未运行}"
echo ""

# 检查目标网络
TARGET_NET="docker_inspireed-network"
if [ -z "$(docker network ls | grep $TARGET_NET)" ]; then
    echo "⚠️  目标网络不存在，将创建..."
    docker network create $TARGET_NET 2>/dev/null || true
fi

# 2. 停止所有服务
echo "🛑 停止所有服务..."
docker-compose -f docker-compose.prod.yml down
echo ""

# 3. 确保网络存在
echo "🌐 确保网络存在..."
docker network create docker_inspireed-network 2>/dev/null || echo "   网络已存在"
echo ""

# 4. 重新启动所有服务
echo "🚀 重新启动所有服务（使用 docker-compose.prod.yml）..."
docker-compose -f docker-compose.prod.yml up -d
echo ""

# 5. 等待服务启动
echo "⏳ 等待服务启动（30秒）..."
sleep 30
echo ""

# 6. 验证网络配置
echo "✅ 验证网络配置："
echo ""

BACKEND_NET_NEW=$(docker inspect inspireed-backend --format='{{range $k, $v := .NetworkSettings.Networks}}{{$k}}{{end}}' 2>/dev/null || echo "")
POSTGRES_NET_NEW=$(docker inspect inspireed-postgres --format='{{range $k, $v := .NetworkSettings.Networks}}{{$k}}{{end}}' 2>/dev/null || echo "")
REDIS_NET_NEW=$(docker inspect inspireed-redis --format='{{range $k, $v := .NetworkSettings.Networks}}{{$k}}{{end}}' 2>/dev/null || echo "")
MINIO_NET_NEW=$(docker inspect inspireed-minio --format='{{range $k, $v := .NetworkSettings.Networks}}{{$k}}{{end}}' 2>/dev/null || echo "")

echo "   后端容器网络: ${BACKEND_NET_NEW:-未运行}"
echo "   PostgreSQL 容器网络: ${POSTGRES_NET_NEW:-未运行}"
echo "   Redis 容器网络: ${REDIS_NET_NEW:-未运行}"
echo "   MinIO 容器网络: ${MINIO_NET_NEW:-未运行}"
echo ""

# 检查是否都在同一网络
if [ "$BACKEND_NET_NEW" = "$POSTGRES_NET_NEW" ] && [ "$POSTGRES_NET_NEW" = "$REDIS_NET_NEW" ] && [ "$REDIS_NET_NEW" = "$MINIO_NET_NEW" ] && [ -n "$BACKEND_NET_NEW" ]; then
    echo "✅ 所有容器现在都在同一网络中: $BACKEND_NET_NEW"
else
    echo "⚠️  警告：容器可能不在同一网络中"
    echo "   请检查 docker-compose.prod.yml 配置"
fi
echo ""

# 7. 测试网络连接
echo "🔍 测试网络连接..."
if docker exec inspireed-backend python -c "
import socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(2)
result = sock.connect_ex(('postgres', 5432))
sock.close()
exit(0 if result == 0 else 1)
" 2>/dev/null; then
    echo "✅ 后端可以连接到 PostgreSQL"
else
    echo "❌ 后端无法连接到 PostgreSQL"
    echo "   请检查服务状态：docker-compose -f docker-compose.prod.yml ps"
fi
echo ""

echo "✅ 网络修复完成！"
echo ""
echo "💡 下一步："
echo "   1. 运行数据库连接测试: ./test-db-connection.sh"
echo "   2. 运行数据库迁移: ./run-migration.sh"

