#!/bin/bash
# CloudStudio 前端启动脚本（用于 preview.yml）
# 这个脚本会启动前端服务，适用于 CloudStudio 环境

set -e

# 等待后端服务就绪（最多等待30秒）
echo "⏳ 等待后端服务启动..."
max_attempts=30
attempt=0
while [ $attempt -lt $max_attempts ]; do
  if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ 后端服务已就绪"
    break
  fi
  attempt=$((attempt + 1))
  if [ $attempt -eq $max_attempts ]; then
    echo "⚠️  后端服务可能未启动，前端将继续启动"
  fi
  sleep 1
done

# 进入前端目录
cd frontend

# 检查并安装依赖
if [ ! -d "node_modules" ]; then
  echo "📥 安装前端依赖..."
  pnpm install
fi

# 创建环境配置（如果不存在）
if [ ! -f ".env.local" ]; then
  echo "⚙️ 创建前端环境配置文件..."
  cp env.example .env.local
  echo "# Cloud Studio 环境：API 地址会自动根据前端 URL 计算" >> .env.local
  echo "# 如需手动设置，请取消注释并修改下面的配置：" >> .env.local
  echo "# VITE_API_BASE_URL=https://your-backend-id--8000.region.cloudstudio.club/api/v1" >> .env.local
fi

# 启动前端服务
echo "🚀 启动前端服务 (端口 5173)..."
pnpm dev --host 0.0.0.0

