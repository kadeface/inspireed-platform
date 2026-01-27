#!/bin/bash

echo "🛑 停止 InspireEd 生产环境服务..."

# 检测使用哪个 Docker Compose 命令
if command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE_CMD="docker-compose"
elif docker compose version &> /dev/null; then
    DOCKER_COMPOSE_CMD="docker compose"
else
    echo "❌ 未找到 docker-compose 或 docker compose 命令"
    exit 1
fi

# 获取脚本所在目录的绝对路径
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DOCKER_DIR="$SCRIPT_DIR/docker"

# 进入 docker 目录
cd "$DOCKER_DIR" || exit 1

# 停止所有服务
echo "📦 停止所有服务..."
$DOCKER_COMPOSE_CMD -f docker-compose.prod.yml down

echo "✅ 所有服务已停止"

