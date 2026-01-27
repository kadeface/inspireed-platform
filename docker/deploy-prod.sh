#!/bin/bash

# 生产环境部署脚本
# 使用 docker-compose.prod.yml 配置

set -e

echo "========================================"
echo "InspireEd 生产环境部署"
echo "========================================"

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$SCRIPT_DIR"

# 检查是否已有运行的容器
if docker ps -a --format '{{.Names}}' | grep -q "inspireed-"; then
    echo ""
    echo "⚠️  检测到已有运行的InspireEd容器"
    echo ""
    echo "请选择操作："
    echo "  1) 停止并删除现有容器，重新部署"
    echo "  2) 仅重启容器（不重新构建）"
    echo "  3) 取消操作"
    echo ""
    read -p "请输入选项 (1/2/3): " choice
    
    case $choice in
        1)
            echo ""
            echo "🛑 停止并删除现有容器..."
            docker-compose -f docker-compose.prod.yml down
            ;;
        2)
            echo ""
            echo "🔄 重启容器..."
            docker-compose -f docker-compose.prod.yml restart
            echo ""
            echo "✅ 容器重启完成"
            exit 0
            ;;
        3)
            echo ""
            echo "❌ 操作已取消"
            exit 0
            ;;
        *)
            echo ""
            echo "❌ 无效选项，操作已取消"
            exit 1
            ;;
    esac
fi

# 检查 backend/.env 文件
if [ ! -f "$PROJECT_ROOT/backend/.env" ]; then
    echo ""
    echo "⚠️  未找到 backend/.env 文件"
    echo "   请根据 backend/.env.example 创建配置文件"
    exit 1
fi

# 询问是否设置API地址
echo ""
echo "📝 前端API地址配置"
echo ""
echo "当前服务器IP地址："
ip addr show | grep -oP '(?<=inet\s)\d+(\.\d+){3}' | grep -v 127.0.0.1 | head -1
echo ""
echo "请选择API地址配置方式："
echo "  1) 自动检测（推荐 - 前端会根据访问地址自动适配）"
echo "  2) 手动指定API地址"
echo ""
read -p "请输入选项 (1/2): " api_choice

if [ "$api_choice" = "2" ]; then
    echo ""
    read -p "请输入API地址 (例如: http://111.230.61.28:8000/api/v1): " api_url
    export VITE_API_BASE_URL="$api_url"
    echo "✅ API地址已设置为: $VITE_API_BASE_URL"
else
    export VITE_API_BASE_URL=""
    echo "✅ 使用自动检测模式"
fi

echo ""
echo "🏗️  开始构建和启动容器..."
echo ""

# 构建并启动容器（生产模式）
docker-compose -f docker-compose.prod.yml up -d --build

echo ""
echo "⏳ 等待服务启动..."
sleep 10

# 检查服务状态
echo ""
echo "📊 服务状态："
docker-compose -f docker-compose.prod.yml ps

# 检查健康状态
echo ""
echo "🏥 健康检查："
for i in {1..30}; do
    if docker-compose -f docker-compose.prod.yml ps | grep -q "(healthy)"; then
        echo "✅ 服务已就绪"
        break
    fi
    echo "   等待服务就绪... ($i/30)"
    sleep 2
done

echo ""
echo "========================================"
echo "✅ 部署完成！"
echo "========================================"
echo ""
echo "📍 访问地址："
echo ""
echo "   前端: http://localhost"
SERVER_IP=$(ip addr show | grep -oP '(?<=inet\s)\d+(\.\d+){3}' | grep -v 127.0.0.1 | head -1)
if [ -n "$SERVER_IP" ]; then
    echo "         http://$SERVER_IP"
fi
echo ""
echo "   后端: http://localhost:8000"
if [ -n "$SERVER_IP" ]; then
    echo "         http://$SERVER_IP:8000"
fi
echo ""
echo "   API文档: http://localhost:8000/api/v1/docs"
echo ""
echo "📝 查看日志："
echo "   docker-compose -f docker-compose.prod.yml logs -f"
echo ""
echo "🛑 停止服务："
echo "   docker-compose -f docker-compose.prod.yml down"
echo ""
