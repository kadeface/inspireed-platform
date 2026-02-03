#!/bin/bash
#
# InspireEd 全 Docker 停止脚本
# 停止由 start-docker.sh 启动的所有容器（PostgreSQL、Redis、MinIO、后端、前端）
#
# 用法：
#   ./stop-docker.sh           # 使用 docker-compose.yml
#   ./stop-docker.sh prod       # 使用 docker-compose.prod.yml
#

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR/docker" || exit 1

COMPOSE_FILE="docker-compose.yml"
if [ "${1:-}" = "prod" ] || [ "${COMPOSE_FILE_ENV:-}" = "prod" ]; then
    COMPOSE_FILE="docker-compose.prod.yml"
fi

echo "🛑 停止 InspireEd 全 Docker 服务..."
docker compose -f "$COMPOSE_FILE" down

echo "✅ 所有容器已停止"
echo "💡 重新启动: ./start-docker.sh"
