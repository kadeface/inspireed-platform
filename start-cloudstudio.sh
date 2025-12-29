#!/bin/bash

echo "🚀 启动 InspireEd CloudStudio 环境（Docker Compose）..."

# 等待 Docker 启动（最多等待 2 分钟）
WAIT_DOCKER=${WAIT_DOCKER:-false}
if [ "$WAIT_DOCKER" = "true" ]; then
    echo "⏳ 等待 Docker 启动..."
    max_attempts=24
    attempt=0
    while [ $attempt -lt $max_attempts ]; do
        if docker info > /dev/null 2>&1; then
            echo "✅ Docker 已启动"
            sleep 3  # 额外等待确保 Docker 完全就绪
            break
        fi
        attempt=$((attempt + 1))
        if [ $((attempt % 5)) -eq 0 ]; then
            echo "等待 Docker 启动中... ($attempt/$max_attempts)"
        fi
        sleep 5
    done
fi

# 检查 Docker 是否运行
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker 未运行，请先启动 Docker"
    exit 1
fi

# 检测使用哪个 Docker Compose 命令
if command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE_CMD="docker-compose"
    echo "📦 使用 docker-compose 命令"
elif docker compose version &> /dev/null; then
    DOCKER_COMPOSE_CMD="docker compose"
    echo "📦 使用 docker compose 命令（新版本）"
else
    echo "❌ 未找到 docker-compose 或 docker compose 命令"
    exit 1
fi

# 获取脚本所在目录的绝对路径
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DOCKER_DIR="$SCRIPT_DIR/docker"

# 进入 docker 目录
cd "$DOCKER_DIR" || exit 1

# 停止可能存在的旧容器
echo "🛑 停止可能存在的旧容器..."
$DOCKER_COMPOSE_CMD -f docker-compose.cloudstudio.yml down 2>/dev/null || true

# 启动所有服务（使用 CloudStudio 配置）
echo "📦 启动所有服务（PostgreSQL, Redis, MinIO, Backend, Frontend）..."
$DOCKER_COMPOSE_CMD -f docker-compose.cloudstudio.yml up -d --build

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 15

# 检查服务状态
echo "🔍 检查服务状态..."
$DOCKER_COMPOSE_CMD -f docker-compose.cloudstudio.yml ps

# 等待后端健康检查
echo "⏳ 等待后端服务健康检查..."
max_wait=180
wait_time=0
while [ $wait_time -lt $max_wait ]; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ 后端服务已就绪"
        break
    fi
    sleep 5
    wait_time=$((wait_time + 5))
    if [ $((wait_time % 15)) -eq 0 ]; then
        echo "等待后端服务启动中... (${wait_time}s/${max_wait}s)"
    fi
done

# 等待前端健康检查
echo "⏳ 等待前端服务健康检查..."
wait_time=0
while [ $wait_time -lt $max_wait ]; do
    if curl -s http://localhost:5173 > /dev/null 2>&1; then
        echo "✅ 前端服务已就绪"
        break
    fi
    sleep 5
    wait_time=$((wait_time + 5))
    if [ $((wait_time % 15)) -eq 0 ]; then
        echo "等待前端服务启动中... (${wait_time}s/${max_wait}s)"
    fi
done

cd "$SCRIPT_DIR" || exit 1

echo ""
echo "🎉 CloudStudio 环境服务启动完成！"
echo ""
echo "📱 访问地址："
echo ""
echo "   【本地访问】"
echo "   前端应用: http://localhost:5173"
echo "   后端API: http://localhost:8000"
echo "   API文档: http://localhost:8000/docs"
echo "   MinIO控制台: http://localhost:9001 (minioadmin/minioadmin)"
echo ""
echo "   【CloudStudio 公网访问】"
echo "   请在 CloudStudio 的 '端口' 面板中查看："
echo "   - 前端端口 5173 的访问地址"
echo "   - 后端端口 8000 的访问地址"
echo ""
echo "   💡 提示："
echo "   - 前端会自动检测 CloudStudio 环境并配置正确的 API 地址"
echo "   - 前端 URL 格式：{id}--5173.{region}.cloudstudio.club"
echo "   - 后端 URL 格式：{id}--8000.{region}.cloudstudio.club"
echo ""
echo "🔐 测试账号："
echo "   管理员: admin@inspireed.com / admin123"
echo "   教师: teacher@inspireed.com / teacher123"
echo "   学生: student@inspireed.com / student123"
echo "   研究员: researcher@inspireed.com / researcher123"
echo ""
echo "📋 管理命令："
echo "   查看日志: cd docker && $DOCKER_COMPOSE_CMD -f docker-compose.cloudstudio.yml logs -f [service_name]"
echo "   查看所有日志: cd docker && $DOCKER_COMPOSE_CMD -f docker-compose.cloudstudio.yml logs -f"
echo "   停止服务: cd docker && $DOCKER_COMPOSE_CMD -f docker-compose.cloudstudio.yml down"
echo "   重启服务: cd docker && $DOCKER_COMPOSE_CMD -f docker-compose.cloudstudio.yml restart [service_name]"
echo "   查看状态: cd docker && $DOCKER_COMPOSE_CMD -f docker-compose.cloudstudio.yml ps"
echo ""
echo "✨ 开始使用 InspireEd CloudStudio 环境！"

