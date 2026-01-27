#!/bin/bash

# InspireEd 阿里云 Docker 部署脚本
# 使用方法: sudo bash deploy-aliyun-docker.sh

set -e

echo "🚀 InspireEd 阿里云 Docker 部署脚本"
echo "===================================="

# 检查是否为 root 用户
if [ "$EUID" -ne 0 ]; then 
    echo "❌ 请使用 sudo 运行此脚本"
    exit 1
fi

# 配置变量
PROJECT_DIR="/opt/inspireed-platform"
DOCKER_DIR="$PROJECT_DIR/docker"

# 1. 更新系统
echo "📦 更新系统包..."
apt update && apt upgrade -y

# 2. 安装基础工具
echo "📦 安装基础工具..."
apt install -y git curl wget vim build-essential software-properties-common

# 3. 安装 Docker
echo "🐳 安装 Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
    systemctl start docker
    systemctl enable docker
    echo "✅ Docker 已安装"
else
    echo "✅ Docker 已安装: $(docker --version)"
fi

# 4. 安装 Docker Compose
echo "🐳 安装 Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    echo "✅ Docker Compose 已安装"
else
    echo "✅ Docker Compose 已安装: $(docker-compose --version)"
fi

# 5. 配置防火墙
echo "🔥 配置防火墙..."
if command -v ufw &> /dev/null; then
    ufw allow 22/tcp
    ufw allow 80/tcp
    ufw allow 443/tcp
    ufw --force enable
    echo "✅ 防火墙已配置"
else
    apt install -y ufw
    ufw allow 22/tcp
    ufw allow 80/tcp
    ufw allow 443/tcp
    ufw --force enable
fi

# 6. 检查项目目录
echo "📁 检查项目目录..."
if [ ! -d "$PROJECT_DIR" ]; then
    echo "❌ 项目目录不存在: $PROJECT_DIR"
    echo "请先克隆或上传项目代码到此目录"
    exit 1
fi

# 7. 创建环境变量文件
echo "⚙️  配置环境变量..."
if [ ! -f "$DOCKER_DIR/.env" ]; then
    echo "📝 创建环境变量文件..."
    cat > "$DOCKER_DIR/.env" << 'EOF'
# PostgreSQL 配置
POSTGRES_USER=postgres
POSTGRES_PASSWORD=changeme_password_please
POSTGRES_DB=inspireed
POSTGRES_PORT=5432

# Redis 配置
REDIS_PASSWORD=changeme_redis_password
REDIS_PORT=6379

# MinIO 配置
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=changeme_minio_password
MINIO_PORT=9000
MINIO_CONSOLE_PORT=9001
MINIO_BUCKET_NAME=inspireed

# 后端配置
BACKEND_PORT=8000
SECRET_KEY=changeme_secret_key_please_make_it_long_and_random
BACKEND_CORS_ORIGINS=["http://localhost","http://localhost:80"]
ALLOW_LAN_ACCESS=false

# 前端配置
FRONTEND_PORT=80
VITE_API_BASE_URL=http://localhost:8000/api/v1
EOF
    echo "⚠️  已创建环境变量文件: $DOCKER_DIR/.env"
    echo "📝 请编辑此文件，修改密码和配置："
    echo "   vim $DOCKER_DIR/.env"
    echo ""
    read -p "按 Enter 继续（请确保已修改 .env 文件）..."
else
    echo "✅ 环境变量文件已存在"
fi

# 8. 构建并启动 Docker 服务
echo "🐳 构建并启动 Docker 服务..."
cd "$DOCKER_DIR"

# 先启动基础服务（数据库等）
echo "📦 启动基础服务..."
docker-compose up -d

# 等待服务启动
echo "⏳ 等待基础服务启动..."
sleep 10

# 构建并启动所有服务
echo "🚀 构建并启动所有服务..."
docker-compose -f docker-compose.prod.yml up -d --build

# 9. 运行数据库迁移
echo "📊 运行数据库迁移..."
sleep 5  # 等待后端服务启动
docker exec inspireed-backend alembic upgrade head || {
    echo "⚠️  数据库迁移失败，请手动执行："
    echo "   docker exec -it inspireed-backend alembic upgrade head"
}

# 10. 检查服务状态
echo "📊 检查服务状态..."
docker-compose -f docker-compose.prod.yml ps

echo ""
echo "===================================="
echo "✅ Docker 部署完成！"
echo ""
echo "📝 下一步操作："
echo "1. 检查服务状态: cd $DOCKER_DIR && docker-compose -f docker-compose.prod.yml ps"
echo "2. 查看日志: docker-compose -f docker-compose.prod.yml logs -f"
echo "3. 配置 Nginx 反向代理（如果需要域名访问）"
echo "4. 配置 SSL 证书（生产环境）"
echo ""
# 检测是否使用 HTTPS（部署脚本默认使用 https）
USE_HTTPS=${USE_HTTPS:-true}
PROTOCOL="https"
if [[ "$USE_HTTPS" == "false" ]]; then
    PROTOCOL="http"
fi

SERVER_IP=$(hostname -I | awk '{print $1}')
echo "🌐 访问地址："
echo "   - 前端: ${PROTOCOL}://${SERVER_IP}"
echo "   - 后端 API: ${PROTOCOL}://${SERVER_IP}:8000"
echo "   - API 文档: ${PROTOCOL}://${SERVER_IP}:8000/docs"
echo ""
echo "📚 详细文档: docs/deployment/ALIYUN_DEPLOYMENT_GUIDE.md"

