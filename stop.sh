#!/bin/bash

echo "🛑 停止 InspireEd 教师教研系统..."

# 停止前端服务
if [ -f "logs/frontend.pid" ]; then
    FRONTEND_PID=$(cat logs/frontend.pid)
    if ps -p $FRONTEND_PID > /dev/null; then
        echo "🛑 停止前端服务 (PID: $FRONTEND_PID)..."
        kill $FRONTEND_PID
        rm logs/frontend.pid
    fi
fi

# 停止后端服务
if [ -f "logs/backend.pid" ]; then
    BACKEND_PID=$(cat logs/backend.pid)
    if ps -p $BACKEND_PID > /dev/null; then
        echo "🛑 停止后端服务 (PID: $BACKEND_PID)..."
        kill $BACKEND_PID
        rm logs/backend.pid
    fi
fi

# 强制停止相关进程
echo "🔍 查找并停止相关进程..."
pkill -f "uvicorn app.main:app" 2>/dev/null
pkill -f "pnpm dev" 2>/dev/null

# 停止 Docker 服务
echo "📦 停止 Docker 服务..."
cd docker
docker-compose down
cd ..

echo "✅ 所有服务已停止"
echo ""
echo "💡 如需重新启动，请运行: ./start.sh"
