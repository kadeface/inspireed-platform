#!/bin/bash

echo "🚀 启动 InspireEd 教师教研系统..."

# 检查 Docker 是否运行
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker 未运行，请先启动 Docker"
    exit 1
fi

# 启动基础服务
echo "📦 启动基础服务 (PostgreSQL, Redis, MinIO, Kafka)..."
cd docker
docker-compose up -d
cd ..

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 5

# 检查服务状态
echo "🔍 检查服务状态..."
docker-compose -f docker/docker-compose.yml ps

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

LOCAL_IP=$(get_local_ip)

echo ""
echo "🎉 服务启动完成！"
echo ""
echo "📱 访问地址："
echo ""
echo "   【本机访问】"
echo "   前端应用: http://localhost:5173"
echo "   后端API: http://localhost:8000"
echo "   API文档: http://localhost:8000/docs"

if [ ! -z "$LOCAL_IP" ]; then
    echo ""
    echo "   【局域网访问】（其他设备使用这些地址）"
    echo "   前端应用: http://$LOCAL_IP:5173"
    echo "   后端API: http://$LOCAL_IP:8000"
    echo "   API文档: http://$LOCAL_IP:8000/docs"
    echo ""
    echo "   💡 提示："
    echo "   - 确保设备连接到同一局域网"
    echo "   - 防火墙需允许 5173 和 8000 端口"
    echo "   - 移动设备可访问: http://$LOCAL_IP:5173"
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
