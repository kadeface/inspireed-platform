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

# 检查并清理端口 8000（只终止 uvicorn 进程，避免误杀 Docker 容器）
echo "🔍 检查端口 8000 占用情况..."
UVICORN_FOUND=false
NON_UVICORN_FOUND=false

if command -v lsof > /dev/null 2>&1; then
  # 查找占用端口 8000 的进程，并检查是否是 uvicorn 进程
  PORT_PIDS=$(lsof -ti:8000 2>/dev/null || true)
  if [ ! -z "$PORT_PIDS" ]; then
    for PID in $PORT_PIDS; do
      # 检查进程的命令行是否包含 uvicorn
      CMD=$(ps -p $PID -o cmd= 2>/dev/null || true)
      if echo "$CMD" | grep -q "uvicorn"; then
        UVICORN_FOUND=true
        echo "⚠️  发现 uvicorn 进程 $PID 占用端口 8000，正在停止..."
        kill $PID 2>/dev/null || true
        sleep 1
        # 如果还在运行，强制终止
        if ps -p $PID > /dev/null 2>&1; then
          kill -9 $PID 2>/dev/null || true
        fi
      else
        # 如果不是 uvicorn 进程（可能是 Docker 容器），只记录不终止
        NON_UVICORN_FOUND=true
        echo "ℹ️  端口 8000 被进程 $PID 占用（非 uvicorn 进程，可能是 Docker 容器，跳过）"
      fi
    done
    sleep 1
  fi
fi

# 使用 pkill 作为备选方案，确保所有 uvicorn 进程都被终止
pkill -f "uvicorn app.main:app" 2>/dev/null && UVICORN_FOUND=true && echo "✅ 已清理 uvicorn 进程" || true
sleep 1

# 如果仍然有非 uvicorn 进程占用端口，给出警告
if command -v lsof > /dev/null 2>&1; then
  REMAINING_PIDS=$(lsof -ti:8000 2>/dev/null || true)
  if [ ! -z "$REMAINING_PIDS" ]; then
    echo "⚠️  警告：端口 8000 仍被其他进程占用（可能是 Docker 容器）"
    echo "   如果后端服务启动失败，请检查并手动释放端口 8000"
    lsof -i:8000 | head -5
  fi
fi

# 启动后端服务
echo "🚀 启动后端服务 (端口 8000)..."
$VENV_PYTHON -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

