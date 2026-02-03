#!/bin/bash
#
# InspireEd 全 Docker 启动脚本（前后端均在容器中）
#
# 使用场景：本地或服务器上全容器化运行
# - 所有服务（PostgreSQL、Redis、MinIO、后端、前端）均在 Docker 中运行
# - 默认使用 docker-compose.yml（前端端口 80，后端 8000）
#
# 用法：
#   ./start-docker.sh           # 使用 docker-compose.yml
#   ./start-docker.sh prod       # 使用 docker-compose.prod.yml（生产）
#   COMPOSE_FILE=prod ./start-docker.sh   # 同上
#
# 其他脚本：
#   ./start.sh       - 本地开发（仅基础服务 Docker，前后端本地跑）
#   ./stop-docker.sh - 停止全 Docker 服务
#   ./restart-docker.sh - 重启全 Docker 服务
#

set -e
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR/docker" || exit 1

# 生产环境：使用 docker-compose.prod.yml
COMPOSE_FILE="docker-compose.yml"
if [ "${1:-}" = "prod" ] || [ "${COMPOSE_FILE_ENV:-}" = "prod" ]; then
    COMPOSE_FILE="docker-compose.prod.yml"
    echo "📦 使用生产配置: $COMPOSE_FILE"
fi

echo "🚀 启动 InspireEd（全 Docker）..."

if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker 未运行，请先启动 Docker"
    exit 1
fi

echo "📦 启动所有服务（PostgreSQL, Redis, MinIO, Backend, Frontend）..."
docker compose -f "$COMPOSE_FILE" up -d

echo "⏳ 等待服务就绪..."
sleep 8

echo "🔍 服务状态："
docker compose -f "$COMPOSE_FILE" ps

echo ""
echo "🎉 服务已启动"
echo ""
echo "📱 访问地址："
echo "   前端: http://localhost"
echo "   后端: http://localhost:8000"
echo "   API 文档: http://localhost:8000/docs"
echo ""
echo "📋 管理："
echo "   停止: ./stop-docker.sh"
echo "   重启: ./restart-docker.sh"
echo "   日志: cd docker && docker compose -f $COMPOSE_FILE logs -f"
echo ""
