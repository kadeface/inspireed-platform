#!/bin/bash
#
# InspireEd 生产环境启动脚本
#
# 使用场景：正式生产服务器部署
# - 所有服务都在 Docker 容器中运行
# - 前端使用 Nginx 提供静态文件（生产构建）
# - 前端端口：80，后端端口：8000
#
# 其他启动脚本：
# - start.sh: 本地开发环境（混合模式，前端端口 5173）
# - start-cloudstudio.sh: CloudStudio 云端环境（全容器化，前端端口 5173）
#
# 详细说明请查看：START_SCRIPTS_GUIDE.md

echo "🚀 启动 InspireEd 生产环境（Docker Compose）..."

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

# 启动所有服务（使用生产环境配置）
echo "📦 启动所有服务（PostgreSQL, Redis, MinIO, Backend, Frontend）..."
# 如果设置了 COMPOSE_BAKE=true，使用 Bake 构建以提升性能
if [ "${COMPOSE_BAKE:-false}" = "true" ]; then
    echo "⚡ 使用 Bake 构建模式（提升构建性能）..."
    COMPOSE_BAKE=true $DOCKER_COMPOSE_CMD -f docker-compose.prod.yml up -d --build
else
    $DOCKER_COMPOSE_CMD -f docker-compose.prod.yml up -d
fi

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 10

# 检查服务状态
echo "🔍 检查服务状态..."
$DOCKER_COMPOSE_CMD -f docker-compose.prod.yml ps

# 等待后端健康检查
echo "⏳ 等待后端服务健康检查..."
max_wait=120
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
    if curl -s http://localhost/health > /dev/null 2>&1 || curl -s http://localhost:80/health > /dev/null 2>&1; then
        echo "✅ 前端服务已就绪"
        break
    fi
    sleep 5
    wait_time=$((wait_time + 5))
    if [ $((wait_time % 15)) -eq 0 ]; then
        echo "等待前端服务启动中... (${wait_time}s/${max_wait}s)"
    fi
done

# 返回项目根目录
cd "$SCRIPT_DIR" || exit 1

# 检测是否使用 HTTPS（生产环境默认使用 https）
# 如果 USE_HTTPS 环境变量设置为 false，则使用 http（用于本地测试）
USE_HTTPS=${USE_HTTPS:-true}

# 获取服务器 IP 地址
get_server_ip() {
    if command -v curl &> /dev/null; then
        # 尝试从外部服务获取公网 IP
        curl -s --max-time 2 ifconfig.me 2>/dev/null || curl -s --max-time 2 ipinfo.io/ip 2>/dev/null || echo ""
    elif command -v hostname &> /dev/null; then
        hostname -I | awk '{print $1}' 2>/dev/null || echo ""
    else
        echo ""
    fi
}

SERVER_IP=$(get_server_ip)

# 判断协议：生产环境公网访问使用 https，本地访问使用 http
PROTOCOL_LOCAL="http"
PROTOCOL_PUBLIC="https"
if [[ "$USE_HTTPS" == "false" ]]; then
    PROTOCOL_PUBLIC="http"
fi

echo ""
echo "🎉 生产环境服务启动完成！"
echo ""
echo "📱 访问地址："
echo ""
echo "   【本地访问】"
echo "   前端应用: ${PROTOCOL_LOCAL}://localhost"
echo "   后端API: ${PROTOCOL_LOCAL}://localhost:8000"
echo "   API文档: ${PROTOCOL_LOCAL}://localhost:8000/docs"
echo "   MinIO控制台: ${PROTOCOL_LOCAL}://localhost:9001 (minioadmin/minioadmin)"

if [ ! -z "$SERVER_IP" ]; then
    echo ""
    echo "   【公网访问】（如果已配置）"
    echo "   前端应用: ${PROTOCOL_PUBLIC}://$SERVER_IP"
    echo "   后端API: ${PROTOCOL_PUBLIC}://$SERVER_IP:8000"
    echo "   API文档: ${PROTOCOL_PUBLIC}://$SERVER_IP:8000/docs"
fi

echo ""
echo "🔐 测试账号："
echo "   管理员: admin@inspireed.com / admin123"
echo "   教师: teacher@inspireed.com / teacher123"
echo "   学生: student@inspireed.com / student123"
echo "   研究员: researcher@inspireed.com / researcher123"
echo ""
echo "📋 管理命令："
echo "   查看日志: cd docker && $DOCKER_COMPOSE_CMD -f docker-compose.prod.yml logs -f [service_name]"
echo "   查看所有日志: cd docker && $DOCKER_COMPOSE_CMD -f docker-compose.prod.yml logs -f"
echo "   停止服务: cd docker && $DOCKER_COMPOSE_CMD -f docker-compose.prod.yml down"
echo "   重启服务: cd docker && $DOCKER_COMPOSE_CMD -f docker-compose.prod.yml restart [service_name]"
echo "   查看状态: cd docker && $DOCKER_COMPOSE_CMD -f docker-compose.prod.yml ps"
echo ""
echo "💡 提示："
echo "   - 确保防火墙已开放 80 和 8000 端口"
echo "   - 如需修改前端端口，设置环境变量: export FRONTEND_PORT=8080"
echo "   - 如需修改 API 地址，设置环境变量: export VITE_API_BASE_URL=http://your-domain:8000/api/v1"
echo ""
echo "⚡ 性能优化："
echo "   - 使用 Bake 构建（提升构建速度）: COMPOSE_BAKE=true ./start-prod.sh"
echo ""
echo "✨ 开始使用 InspireEd 生产环境！"

