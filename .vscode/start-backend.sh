#!/bin/bash
set -e

# 检查并启动 Docker 服务
if ! docker info > /dev/null 2>&1; then
  echo "❌ Docker 未运行，请先启动 Docker"
  exit 1
fi

# 启动基础服务（如果未运行）
cd docker && docker-compose up -d && cd ..

# 等待服务启动
echo "⏳ 等待 Docker 服务启动..."
sleep 5

# 进入后端目录
cd backend

# 检查并创建虚拟环境
if [ ! -d "venv" ]; then
  echo "📦 创建 Python 虚拟环境..."
  python3 -m venv venv
fi

# 使用虚拟环境中的 Python 和 pip
VENV_PYTHON=./venv/bin/python
VENV_PIP=./venv/bin/pip

# 安装/更新依赖
echo "📥 检查并安装后端依赖..."
$VENV_PIP install --upgrade pip
$VENV_PIP install -r requirements.txt

# 创建环境配置（如果不存在）
if [ ! -f ".env" ]; then
  echo "⚙️ 创建环境配置文件..."
  cp env.example .env
  echo "⚠️  请检查并配置 backend/.env 文件中的数据库连接等信息"
fi

# 运行数据库迁移
echo "🗄️ 运行数据库迁移..."
$VENV_PYTHON -m alembic upgrade head

# 检查并清理端口 8000（如果被占用）
if command -v lsof > /dev/null 2>&1; then
  PORT_PID=$(lsof -ti:8000 2>/dev/null)
  if [ ! -z "$PORT_PID" ]; then
    echo "⚠️  端口 8000 被进程 $PORT_PID 占用，正在停止..."
    kill $PORT_PID 2>/dev/null || true
    sleep 2
    if lsof -ti:8000 > /dev/null 2>&1; then
      kill -9 $(lsof -ti:8000) 2>/dev/null || true
      sleep 1
    fi
  fi
else
  pkill -f "uvicorn app.main:app" 2>/dev/null || true
  sleep 2
fi

# 启动后端服务
echo "🚀 启动后端服务 (端口 8000)..."
$VENV_PYTHON -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

