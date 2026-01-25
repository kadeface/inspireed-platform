#!/bin/bash
set -e

echo "🚀 InspireEd 远程更新脚本"
echo "================================"
echo ""

PROJECT_DIR="/root/inspireed-platform_20260107172453"
BACKUP_DIR="/root/inspireed-backups"
BRANCH="feature/cloudstudio-deploy"

# 1. 备份数据库
echo "📦 步骤1: 备份数据库..."
/root/backup-database.sh

# 2. 备份当前代码
echo ""
echo "📁 步骤2: 备份当前代码..."
mkdir -p $BACKUP_DIR
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
tar -czf $BACKUP_DIR/code-backup-$TIMESTAMP.tar.gz -C /root inspireed-platform_20260107172453/ 2>/dev/null || true
echo "代码备份完成: $BACKUP_DIR/code-backup-$TIMESTAMP.tar.gz"

# 3. 进入项目目录
cd $PROJECT_DIR

# 4. 检查是否有 Git 仓库
if [ ! -d ".git" ]; then
    echo ""
    echo "🔧 步骤3: 初始化 Git 仓库..."
    git init
    git remote add origin https://github.com/kadeface/inspireed-platform.git || true
fi

# 5. 拉取最新代码
echo ""
echo "⬇️  步骤4: 拉取最新代码..."
git fetch origin $BRANCH --depth=1
git reset --hard origin/$BRANCH

echo ""
echo "✅ 代码已更新到最新版本"

# 6. 检测当前运行模式
echo ""
echo "🔍 步骤5: 检测当前运行模式..."
cd $PROJECT_DIR/docker

CURRENT_MODE="unknown"
if docker ps --format '{{.Names}}' | grep -q "inspireed-frontend"; then
    FRONTEND_PORT=$(docker port inspireed-frontend 2>/dev/null | grep -oP '0.0.0.0:\K\d+' | head -1)
    if [ "$FRONTEND_PORT" = "5173" ]; then
        CURRENT_MODE="development"
        echo "当前模式: 开发模式 (端口5173)"
    elif [ "$FRONTEND_PORT" = "80" ]; then
        CURRENT_MODE="production"
        echo "当前模式: 生产模式 (端口80)"
    fi
else
    echo "未检测到运行中的容器"
fi

# 7. 选择部署模式
echo ""
echo "📋 请选择部署模式："
echo "  1) 生产模式 (推荐 - Nginx静态文件，端口80)"
echo "  2) 开发模式 (Vite开发服务器，端口5173)"
echo ""

# 自动选择生产模式（推荐）
DEPLOY_MODE="production"
if [ "$CURRENT_MODE" = "development" ]; then
    echo "⚠️  检测到当前为开发模式，建议切换到生产模式"
    echo "默认使用: 生产模式 (10秒后自动继续，Ctrl+C取消)"
    
    # 等待10秒，允许用户中断
    for i in {10..1}; do
        echo -n "$i... "
        sleep 1
    done
    echo ""
else
    echo "✅ 使用生产模式部署"
fi

# 8. 重启服务
echo ""
echo "🔄 步骤6: 重启服务..."

if [ "$DEPLOY_MODE" = "production" ]; then
    echo "使用生产模式配置: docker-compose.prod.yml"
    
    # 停止所有可能运行的容器
    docker-compose down 2>/dev/null || true
    docker-compose -f docker-compose.prod.yml down 2>/dev/null || true
    
    # 启动生产模式
    docker-compose -f docker-compose.prod.yml up -d --build
    
    FRONTEND_URL="http://111.230.61.28"
    COMPOSE_FILE="docker-compose.prod.yml"
else
    echo "使用开发模式配置: docker-compose.yml"
    
    # 停止所有可能运行的容器
    docker-compose -f docker-compose.prod.yml down 2>/dev/null || true
    docker-compose down 2>/dev/null || true
    
    # 启动开发模式
    docker-compose up -d --build
    
    FRONTEND_URL="http://111.230.61.28:5173"
    COMPOSE_FILE="docker-compose.yml"
fi

echo ""
echo "⏳ 等待服务启动..."
sleep 15

# 9. 健康检查
echo ""
echo "🏥 健康检查..."
for i in {1..30}; do
    if docker-compose -f $COMPOSE_FILE ps | grep -q "(healthy)"; then
        echo "✅ 服务健康检查通过"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "⚠️  健康检查超时，请手动检查服务状态"
    else
        echo "   等待服务就绪... ($i/30)"
        sleep 2
    fi
done

echo ""
echo "📋 服务状态："
docker-compose -f $COMPOSE_FILE ps

echo ""
echo "================================"
echo "✅ 更新完成！"
echo "================================"
echo ""
echo "📍 访问地址："
echo "   前端: $FRONTEND_URL"
echo "   后端: http://111.230.61.28:8000"
echo "   API文档: http://111.230.61.28:8000/api/v1/docs"
echo ""
echo "📝 查看日志："
echo "   docker-compose -f $COMPOSE_FILE logs -f"
echo ""
echo "🔧 如需切换模式："
if [ "$DEPLOY_MODE" = "production" ]; then
    echo "   切换到开发模式: cd docker && docker-compose -f docker-compose.prod.yml down && docker-compose up -d"
else
    echo "   切换到生产模式: cd docker && docker-compose down && docker-compose -f docker-compose.prod.yml up -d"
fi
echo ""
