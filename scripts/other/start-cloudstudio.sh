#!/bin/bash
#
# InspireEd CloudStudio 云端环境启动脚本
#
# 使用场景：腾讯云 CloudStudio 环境
# - 所有服务都在 Docker 容器中运行
# - 前端使用 Vite 开发模式（支持热重载）
# - 前端端口：5173，后端端口：8000
# - 自动清理端口冲突，自动配置 CORS
#
# 其他启动脚本：
# - start.sh: 本地开发环境（混合模式，前端端口 5173）
# - start-prod.sh: 生产环境（全容器化，前端端口 80）
#
# 详细说明请查看：START_SCRIPTS_GUIDE.md

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

# 清理端口 5173（前端端口）
echo "🔍 检查端口 5173 占用情况..."
if command -v lsof > /dev/null 2>&1; then
    PORT_5173_PID=$(lsof -ti:5173 2>/dev/null)
    if [ ! -z "$PORT_5173_PID" ]; then
        echo "⚠️  发现端口 5173 被进程 $PORT_5173_PID 占用"
        echo "📋 进程详情:"
        ps -p $PORT_5173_PID -o pid,ppid,cmd 2>/dev/null || true
        echo ""
        echo "🛑 正在停止进程 $PORT_5173_PID..."
        kill $PORT_5173_PID 2>/dev/null || true
        sleep 2
        
        # 检查是否还在运行，如果是则强制停止
        if ps -p $PORT_5173_PID > /dev/null 2>&1; then
            echo "⚠️  进程仍在运行，强制停止..."
            kill -9 $PORT_5173_PID 2>/dev/null || true
            sleep 1
        fi
        
        # 再次检查端口
        if lsof -ti:5173 > /dev/null 2>&1; then
            echo "❌ 端口仍然被占用，强制清理所有占用该端口的进程..."
            kill -9 $(lsof -ti:5173) 2>/dev/null || true
            sleep 1
        fi
        
        if ! lsof -ti:5173 > /dev/null 2>&1; then
            echo "✅ 端口 5173 已成功释放"
        else
            echo "❌ 端口 5173 仍然被占用，请手动清理:"
            lsof -i:5173
            echo ""
            echo "💡 可以手动执行: kill -9 \$(lsof -ti:5173)"
        fi
    else
        echo "✅ 端口 5173 未被占用"
    fi
else
    # 如果没有 lsof，尝试使用其他方法
    echo "ℹ️  lsof 不可用，尝试使用其他方法清理端口 5173..."
    # 尝试停止可能的前端进程
    pkill -f "vite" 2>/dev/null && echo "✅ 已停止 vite 进程" || echo "ℹ️  没有找到运行中的 vite 进程"
    pkill -f "pnpm dev" 2>/dev/null && echo "✅ 已停止 pnpm dev 进程" || echo "ℹ️  没有找到运行中的 pnpm dev 进程"
    sleep 1
fi

# 进入 docker 目录
cd "$DOCKER_DIR" || exit 1

# 停止可能存在的旧容器
echo "🛑 停止可能存在的旧容器..."
$DOCKER_COMPOSE_CMD -f docker-compose.cloudstudio.yml down 2>/dev/null || true

# 检查是否有其他 Docker 容器占用端口 5173
echo "🔍 检查是否有 Docker 容器占用端口 5173..."
CONFLICTING_CONTAINER=$(docker ps --format "{{.Names}}" | xargs -I {} docker port {} 2>/dev/null | grep ":5173" | head -1)
if [ ! -z "$CONFLICTING_CONTAINER" ]; then
    echo "⚠️  发现 Docker 容器占用端口 5173，正在停止..."
    docker stop $(docker ps -q --filter "publish=5173") 2>/dev/null || true
    sleep 2
fi

# 启动所有服务（使用 CloudStudio 配置）
echo "📦 启动所有服务（PostgreSQL, Redis, MinIO, Backend, Frontend）..."
# 如果设置了 COMPOSE_BAKE=true，使用 Bake 构建以提升性能
if [ "${COMPOSE_BAKE:-false}" = "true" ]; then
    echo "⚡ 使用 Bake 构建模式（提升构建性能）..."
    COMPOSE_BAKE=true $DOCKER_COMPOSE_CMD -f docker-compose.cloudstudio.yml up -d --build
else
    $DOCKER_COMPOSE_CMD -f docker-compose.cloudstudio.yml up -d --build
fi

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
echo "⚡ 性能优化："
echo "   使用 Bake 构建（提升构建速度）: COMPOSE_BAKE=true ./start-cloudstudio.sh"
echo ""
echo "✨ 开始使用 InspireEd CloudStudio 环境！"

