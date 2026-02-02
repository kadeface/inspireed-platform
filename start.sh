#!/bin/bash
#
# InspireEd 本地开发环境启动脚本
#
# 使用场景：本地开发调试
# - 基础服务（PostgreSQL、Redis、MinIO）在 Docker 中运行
# - 前后端在本地运行，支持热重载
# - 前端端口：5173，后端端口：8000
#
# 其他启动脚本：
# - start-prod.sh: 生产环境（全容器化，前端端口 80）
# - start-cloudstudio.sh: CloudStudio 云端环境（全容器化，前端端口 5173）
#
# 详细说明请查看：START_SCRIPTS_GUIDE.md

echo "🚀 启动 InspireEd 本地开发环境..."

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

# 检查 Docker 是否运行，如果未运行则尝试启动
if ! docker info > /dev/null 2>&1; then
    echo "⚠️  Docker 未运行，尝试自动启动 Docker..."
    
    # 根据操作系统尝试启动 Docker
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS - 启动 Docker Desktop
        if command -v open &> /dev/null; then
            echo "🚀 正在启动 Docker Desktop..."
            open -a Docker
        else
            echo "❌ 无法启动 Docker Desktop（未找到 open 命令）"
            exit 1
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux - 尝试使用 systemctl 或 service 启动
        if command -v systemctl &> /dev/null; then
            echo "🚀 正在启动 Docker 服务 (systemd)..."
            sudo systemctl start docker 2>/dev/null || {
                echo "⚠️  需要 root 权限启动 Docker，请手动执行: sudo systemctl start docker"
                exit 1
            }
        elif command -v service &> /dev/null; then
            echo "🚀 正在启动 Docker 服务 (service)..."
            sudo service docker start 2>/dev/null || {
                echo "⚠️  需要 root 权限启动 Docker，请手动执行: sudo service docker start"
                exit 1
            }
        else
            echo "❌ 无法启动 Docker（未找到 systemctl 或 service 命令）"
            exit 1
        fi
    else
        echo "❌ 不支持的操作系统，请手动启动 Docker"
        exit 1
    fi
    
    # 等待 Docker 启动（最多等待 2 分钟）
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
    
    # 再次检查 Docker 是否成功启动
    if ! docker info > /dev/null 2>&1; then
        echo "❌ Docker 启动超时，请手动启动 Docker 后重试"
        exit 1
    fi
fi

# 启动基础服务（仅 postgres/redis/minio，后端和前端在本地运行，避免拉取 python/node 镜像）
echo "📦 启动基础服务 (PostgreSQL, Redis, MinIO)..."
cd docker
docker compose up -d postgres redis minio 2>/dev/null || docker-compose up -d postgres redis minio
cd ..

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 5

# 等待 PostgreSQL 可连接（最多约 60 秒）
echo "⏳ 等待 PostgreSQL 就绪..."
POSTGRES_MAX_ATTEMPTS=30
POSTGRES_ATTEMPT=0
until nc -z 127.0.0.1 5432 2>/dev/null; do
    POSTGRES_ATTEMPT=$((POSTGRES_ATTEMPT + 1))
    if [ $POSTGRES_ATTEMPT -ge $POSTGRES_MAX_ATTEMPTS ]; then
        echo "❌ PostgreSQL 启动超时，请检查 Docker 容器: docker-compose -f docker/docker-compose.yml ps"
        exit 1
    fi
    echo "   等待中... ($POSTGRES_ATTEMPT/$POSTGRES_MAX_ATTEMPTS)"
    sleep 2
done
echo "✅ PostgreSQL 已就绪"

# 检查服务状态
echo "🔍 检查服务状态..."
(docker compose -f docker/docker-compose.yml ps 2>/dev/null || docker-compose -f docker/docker-compose.yml ps) || true

# 启动后端服务
echo "🔧 启动后端服务..."
cd backend

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 创建 Python 虚拟环境..."
    python -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
echo "📥 安装后端依赖..."
pip install -r requirements.txt

# 创建环境配置
if [ ! -f ".env" ]; then
    echo "⚙️ 创建环境配置文件..."
    cp env.example .env
fi

# 运行数据库迁移
echo "🗄️ 运行数据库迁移..."
alembic upgrade head

# 启动后端服务（后台运行）
echo "🚀 启动后端服务 (端口 8000)..."
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > ../logs/backend.log 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > ../logs/backend.pid

cd ..

# 等待后端启动
echo "⏳ 等待后端服务启动..."
sleep 3

# 检查后端健康状态
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ 后端服务启动成功"
else
    echo "❌ 后端服务启动失败，请检查日志: logs/backend.log"
fi

# 启动前端服务
echo "🎨 启动前端服务..."
cd frontend

# 安装依赖
echo "📥 安装前端依赖..."
pnpm install

# 创建环境配置
if [ ! -f ".env.local" ]; then
    echo "⚙️ 创建前端环境配置文件..."
    cp env.example .env.local
fi

# 启动前端服务（后台运行）
echo "🚀 启动前端服务 (端口 5173)..."
pnpm dev > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > ../logs/frontend.pid

cd ..

# 等待前端启动
echo "⏳ 等待前端服务启动..."
sleep 5

# 创建日志目录
mkdir -p logs

# 检测是否使用 HTTPS（通过环境变量或检测是否为公网环境）
# 如果 USE_HTTPS 环境变量设置为 true，则使用 https
# 如果检测到公网 IP，则使用 https
USE_HTTPS=${USE_HTTPS:-false}

# 获取本机 IP 地址
get_local_ip() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        ifconfig | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}' | head -n 1
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        hostname -I | awk '{print $1}'
    else
        # 其他系统
        echo ""
    fi
}

# 检测是否为私有 IP
is_private_ip() {
    local ip=$1
    if [[ -z "$ip" ]]; then
        return 0  # 空值视为私有
    fi
    # 私有 IP 段：10.x.x.x, 192.168.x.x, 172.16-31.x.x, 127.x.x.x
    if [[ "$ip" =~ ^10\. ]] || \
       [[ "$ip" =~ ^192\.168\. ]] || \
       [[ "$ip" =~ ^172\.(1[6-9]|2[0-9]|3[0-1])\. ]] || \
       [[ "$ip" =~ ^127\. ]]; then
        return 0  # 是私有 IP
    fi
    return 1  # 不是私有 IP（可能是公网 IP）
}

# 获取公网 IP（用于判断是否为互联网部署）
get_public_ip() {
    if command -v curl &> /dev/null; then
        curl -s --max-time 2 ifconfig.me 2>/dev/null || \
        curl -s --max-time 2 ipinfo.io/ip 2>/dev/null || echo ""
    else
        echo ""
    fi
}

LOCAL_IP=$(get_local_ip)
PUBLIC_IP=$(get_public_ip)

# 判断是否使用 HTTPS
PROTOCOL="http"
if [[ "$USE_HTTPS" == "true" ]]; then
    PROTOCOL="https"
elif [[ ! -z "$PUBLIC_IP" ]] && ! is_private_ip "$PUBLIC_IP"; then
    # 如果获取到公网 IP 且不是私有 IP，说明是互联网部署，使用 https
    PROTOCOL="https"
fi

echo ""
echo "🎉 服务启动完成！"
echo ""
echo "📱 访问地址："
echo ""
echo "   【本机访问】"
echo "   前端应用: ${PROTOCOL}://localhost:5173"
echo "   后端API: ${PROTOCOL}://localhost:8000"
echo "   API文档: ${PROTOCOL}://localhost:8000/docs"

if [ ! -z "$LOCAL_IP" ]; then
    echo ""
    if is_private_ip "$LOCAL_IP"; then
        echo "   【局域网访问】（其他设备使用这些地址）"
        echo "   前端应用: ${PROTOCOL}://$LOCAL_IP:5173"
        echo "   后端API: ${PROTOCOL}://$LOCAL_IP:8000"
        echo "   API文档: ${PROTOCOL}://$LOCAL_IP:8000/docs"
    else
        echo "   【公网访问】"
        echo "   前端应用: ${PROTOCOL}://$LOCAL_IP:5173"
        echo "   后端API: ${PROTOCOL}://$LOCAL_IP:8000"
        echo "   API文档: ${PROTOCOL}://$LOCAL_IP:8000/docs"
    fi
    echo ""
    echo "   💡 提示："
    if [[ "$PROTOCOL" == "https" ]]; then
        echo "   - 当前使用 HTTPS 协议（互联网部署模式）"
    else
        echo "   - 确保设备连接到同一局域网"
    fi
    echo "   - 防火墙需允许 5173 和 8000 端口"
    echo "   - 移动设备可访问: ${PROTOCOL}://$LOCAL_IP:5173"
fi

echo ""
echo "🔐 测试账号："
echo "   管理员: admin@inspireed.com / admin123"
echo "   教师: teacher@inspireed.com / teacher123"
echo "   学生: student@inspireed.com / student123"
echo "   研究员: researcher@inspireed.com / researcher123"
echo ""
echo "📋 管理命令："
echo "   查看日志: tail -f logs/backend.log 或 tail -f logs/frontend.log"
echo "   停止服务: ./stop.sh"
echo "   重启服务: ./restart.sh"
echo "   网络配置: ./get-network-info.sh"
echo ""
echo "🌐 局域网配置："
echo "   查看配置指南: cat 局域网访问配置说明.md"
echo "   详细文档: NETWORK_ACCESS_GUIDE.md"
echo ""
echo "✨ 开始使用 InspireEd 吧！"
