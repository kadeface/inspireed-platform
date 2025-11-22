#!/bin/bash

# InspireEd Ubuntu Apache 部署脚本（不使用 Docker）
# 使用方法: sudo bash deploy-apache-no-docker.sh

set -e

echo "🚀 InspireEd Ubuntu Apache 部署脚本（不使用 Docker）"
echo "===================================================="

# 检查是否为 root 用户
if [ "$EUID" -ne 0 ]; then 
    echo "❌ 请使用 sudo 运行此脚本"
    exit 1
fi

# 配置变量
PROJECT_DIR="/opt/inspireed-platform"
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR/frontend"

# 1. 更新系统
echo "📦 更新系统包..."
apt update && apt upgrade -y

# 2. 安装基础工具
echo "📦 安装基础工具..."
apt install -y git curl wget vim build-essential software-properties-common

# 3. 安装 Python 3.10
echo "🐍 安装 Python 3.10..."
apt install -y python3.10 python3.10-venv python3-pip python3-dev libpq-dev

# 4. 安装 Node.js 18
echo "📦 安装 Node.js 18..."
if ! command -v node &> /dev/null; then
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
    apt install -y nodejs
else
    echo "✅ Node.js 已安装: $(node --version)"
fi

# 5. 安装 pnpm
echo "📦 安装 pnpm..."
if ! command -v pnpm &> /dev/null; then
    npm install -g pnpm
else
    echo "✅ pnpm 已安装: $(pnpm --version)"
fi

# 6. 安装 Apache
echo "🌐 安装 Apache..."
if ! command -v apache2 &> /dev/null; then
    apt install -y apache2
    a2enmod rewrite
    a2enmod proxy
    a2enmod proxy_http
    a2enmod proxy_wstunnel
    a2enmod ssl
    a2enmod headers
    systemctl start apache2
    systemctl enable apache2
else
    echo "✅ Apache 已安装"
fi

# 7. 安装 PostgreSQL
echo "🐘 安装 PostgreSQL..."
if ! systemctl is-active --quiet postgresql; then
    apt install -y postgresql postgresql-contrib
    systemctl start postgresql
    systemctl enable postgresql
    echo "⚠️  请手动设置 PostgreSQL 密码："
    echo "   sudo -u postgres psql -c \"ALTER USER postgres PASSWORD 'your-password';\""
    echo "   sudo -u postgres psql -c \"CREATE DATABASE inspireed;\""
else
    echo "✅ PostgreSQL 已安装并运行"
fi

# 8. 安装 Redis
echo "📦 安装 Redis..."
if ! systemctl is-active --quiet redis-server; then
    apt install -y redis-server
    systemctl start redis-server
    systemctl enable redis-server
    echo "⚠️  请手动配置 Redis 密码（编辑 /etc/redis/redis.conf）"
else
    echo "✅ Redis 已安装并运行"
fi

# 9. 安装 MinIO
echo "📦 安装 MinIO..."
if ! command -v minio &> /dev/null; then
    cd /opt
    wget -q https://dl.min.io/server/minio/release/linux-amd64/minio
    chmod +x minio
    mv minio /usr/local/bin/
    
    # 创建 MinIO 用户和数据目录
    if ! id "minio-user" &>/dev/null; then
        useradd -r -s /bin/false minio-user
    fi
    mkdir -p /opt/minio/data /opt/minio/config
    chown -R minio-user:minio-user /opt/minio
    
    # 创建 MinIO 服务文件
    if [ ! -f "/etc/systemd/system/minio.service" ]; then
        cat > /etc/systemd/system/minio.service << 'EOF'
[Unit]
Description=MinIO Object Storage
After=network.target

[Service]
Type=simple
User=minio-user
Group=minio-user
ExecStart=/usr/local/bin/minio server /opt/minio/data --console-address ":9001"
Restart=always
RestartSec=5

Environment="MINIO_ROOT_USER=minioadmin"
Environment="MINIO_ROOT_PASSWORD=changeme"

[Install]
WantedBy=multi-user.target
EOF
        echo "⚠️  请编辑 MinIO 服务文件设置密码："
        echo "   sudo vim /etc/systemd/system/minio.service"
        systemctl daemon-reload
        systemctl start minio
        systemctl enable minio
    fi
else
    echo "✅ MinIO 已安装"
fi

# 10. 配置防火墙
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

# 11. 检查项目目录
echo "📁 检查项目目录..."
if [ ! -d "$PROJECT_DIR" ]; then
    echo "❌ 项目目录不存在: $PROJECT_DIR"
    echo "请先克隆或上传项目代码到此目录"
    exit 1
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
    if systemctl is-active --quiet postgresql; then
        alembic upgrade head
    else
        echo "⚠️  PostgreSQL 未运行，跳过数据库迁移"
    fi
    
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
After=network.target postgresql.service redis-server.service

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
echo "后端服务:"
systemctl status inspireed-backend --no-pager -l
echo ""
echo "Apache 服务:"
systemctl status apache2 --no-pager -l
echo ""
echo "PostgreSQL 服务:"
systemctl status postgresql --no-pager -l
echo ""
echo "Redis 服务:"
systemctl status redis-server --no-pager -l
echo ""
echo "MinIO 服务:"
systemctl status minio --no-pager -l

echo ""
echo "===================================================="
echo "✅ 基础部署完成！"
echo ""
echo "📝 下一步操作："
echo "1. 设置 PostgreSQL 密码和创建数据库"
echo "2. 配置 Redis 密码（编辑 /etc/redis/redis.conf）"
echo "3. 配置 MinIO 密码（编辑 /etc/systemd/system/minio.service）"
echo "4. 编辑后端环境变量: vim $BACKEND_DIR/.env"
echo "5. 编辑前端环境变量: vim $FRONTEND_DIR/.env.production"
echo "6. 配置 Apache 虚拟主机: 参考 docs/deployment/UBUNTU_APACHE_NO_DOCKER_GUIDE.md"
echo "7. 安装 SSL 证书: sudo certbot --apache -d yourdomain.com"
echo "8. 配置域名 DNS 记录"
echo ""
echo "📚 详细文档: docs/deployment/UBUNTU_APACHE_NO_DOCKER_GUIDE.md"

