#!/bin/bash

# InspireEd Ubuntu 部署脚本
# 使用方法: sudo bash deploy-ubuntu.sh

set -e

echo "🚀 InspireEd Ubuntu 部署脚本"
echo "================================"

# 检查是否为 root 用户
if [ "$EUID" -ne 0 ]; then 
    echo "❌ 请使用 sudo 运行此脚本"
    exit 1
fi

# 配置变量
PROJECT_DIR="/opt/inspireed-platform"
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR/frontend"
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
else
    echo "✅ Docker 已安装"
fi

# 4. 安装 Docker Compose
echo "🐳 安装 Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
else
    echo "✅ Docker Compose 已安装"
fi

# 5. 安装 Python 3.10
echo "🐍 安装 Python 3.10..."
apt install -y python3.10 python3.10-venv python3-pip

# 6. 安装 Node.js 18
echo "📦 安装 Node.js 18..."
if ! command -v node &> /dev/null; then
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
    apt install -y nodejs
else
    echo "✅ Node.js 已安装: $(node --version)"
fi

# 7. 安装 pnpm
echo "📦 安装 pnpm..."
if ! command -v pnpm &> /dev/null; then
    npm install -g pnpm
else
    echo "✅ pnpm 已安装: $(pnpm --version)"
fi

# 8. 安装 Nginx
echo "🌐 安装 Nginx..."
if ! command -v nginx &> /dev/null; then
    apt install -y nginx
    systemctl start nginx
    systemctl enable nginx
else
    echo "✅ Nginx 已安装"
fi

# 9. 配置防火墙
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

# 10. 检查项目目录
echo "📁 检查项目目录..."
if [ ! -d "$PROJECT_DIR" ]; then
    echo "❌ 项目目录不存在: $PROJECT_DIR"
    echo "请先克隆或上传项目代码到此目录"
    exit 1
fi

# 11. 启动 Docker 服务
echo "🐳 启动 Docker 服务..."
if [ -d "$DOCKER_DIR" ]; then
    cd "$DOCKER_DIR"
    docker-compose up -d
    echo "✅ Docker 服务已启动"
    sleep 5
    docker-compose ps
else
    echo "⚠️  Docker 目录不存在: $DOCKER_DIR"
fi

# 12. 后端部署
echo "🔧 部署后端..."
if [ -d "$BACKEND_DIR" ]; then
    cd "$BACKEND_DIR"
    
    # 检查 .env 文件
    if [ ! -f ".env" ]; then
        if [ -f "env.example" ]; then
            cp env.example .env
            echo "⚠️  已创建 .env 文件，请编辑配置："
            echo "   vim $BACKEND_DIR/.env"
        else
            echo "❌ 未找到 env.example 文件"
        fi
    fi
    
    # 创建虚拟环境
    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi
    
    # 激活虚拟环境并安装依赖
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    
    # 运行数据库迁移
    echo "📊 运行数据库迁移..."
    alembic upgrade head
    
    echo "✅ 后端部署完成"
else
    echo "❌ 后端目录不存在: $BACKEND_DIR"
fi

# 13. 前端部署
echo "🎨 部署前端..."
if [ -d "$FRONTEND_DIR" ]; then
    cd "$FRONTEND_DIR"
    
    # 检查 .env.production 文件
    if [ ! -f ".env.production" ]; then
        if [ -f "env.example" ]; then
            cp env.example .env.production
            echo "⚠️  已创建 .env.production 文件，请编辑配置："
            echo "   vim $FRONTEND_DIR/.env.production"
        fi
    fi
    
    # 安装依赖
    pnpm install
    
    # 构建
    pnpm build
    
    echo "✅ 前端部署完成"
else
    echo "❌ 前端目录不存在: $FRONTEND_DIR"
fi

# 14. 创建 systemd 服务
echo "⚙️  配置后端服务..."
SERVICE_FILE="/etc/systemd/system/inspireed-backend.service"

if [ ! -f "$SERVICE_FILE" ]; then
    cat > "$SERVICE_FILE" << EOF
[Unit]
Description=InspireEd Backend API Service
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=$BACKEND_DIR
Environment="PATH=$BACKEND_DIR/venv/bin"
ExecStart=$BACKEND_DIR/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
    
    systemctl daemon-reload
    systemctl enable inspireed-backend
    systemctl start inspireed-backend
    
    echo "✅ 后端服务已配置并启动"
else
    echo "✅ 后端服务已存在"
    systemctl restart inspireed-backend
fi

# 15. 检查服务状态
echo "📊 检查服务状态..."
echo ""
echo "Docker 服务:"
docker-compose -f "$DOCKER_DIR/docker-compose.yml" ps
echo ""
echo "后端服务:"
systemctl status inspireed-backend --no-pager -l
echo ""
echo "Nginx 服务:"
systemctl status nginx --no-pager -l

echo ""
echo "================================"
echo "✅ 基础部署完成！"
echo ""
echo "📝 下一步操作："
echo "1. 编辑后端环境变量: vim $BACKEND_DIR/.env"
echo "2. 编辑前端环境变量: vim $FRONTEND_DIR/.env.production"
echo "3. 配置 Nginx: 参考 docs/deployment/UBUNTU_DEPLOYMENT_GUIDE.md"
echo "4. 安装 SSL 证书: sudo certbot --nginx -d yourdomain.com"
echo "5. 配置域名 DNS 记录"
echo ""
echo "📚 详细文档: docs/deployment/UBUNTU_DEPLOYMENT_GUIDE.md"

