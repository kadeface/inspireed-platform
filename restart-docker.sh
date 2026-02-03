#!/bin/bash
#
# InspireEd 全 Docker 重启脚本
# 先停止再启动所有容器（用于更新代码后重新构建并运行）
#
# 用法：
#   ./restart-docker.sh           # 使用 docker-compose.yml
#   ./restart-docker.sh prod       # 使用 docker-compose.prod.yml
#   ./restart-docker.sh prod --build   # 生产环境并重新构建镜像
#

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPOSE_ARG="${1:-}"
EXTRA_ARGS="${2:-}"

echo "🔄 重启 InspireEd 全 Docker 服务..."
"$ROOT_DIR/stop-docker.sh" $COMPOSE_ARG
sleep 3

cd "$ROOT_DIR/docker" || exit 1
COMPOSE_FILE="docker-compose.yml"
if [ "$COMPOSE_ARG" = "prod" ] || [ "${COMPOSE_FILE_ENV:-}" = "prod" ]; then
    COMPOSE_FILE="docker-compose.prod.yml"
fi

echo "📦 重新启动..."
if [ "$EXTRA_ARGS" = "--build" ]; then
    docker compose -f "$COMPOSE_FILE" up -d --build
else
    docker compose -f "$COMPOSE_FILE" up -d
fi

echo "⏳ 等待服务就绪..."
sleep 8
docker compose -f "$COMPOSE_FILE" ps

echo ""
echo "✅ 重启完成"
echo "   前端: http://localhost"
echo "   后端: http://localhost:8000"
echo ""
