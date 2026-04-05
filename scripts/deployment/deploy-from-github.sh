#!/bin/bash
set -e

echo "========================================"
echo "  InspireEd 自动部署脚本"
echo "========================================"

# 切换到项目目录
cd /root/20260126164255_20260126205435

echo "[1/5] 拉取最新代码..."
git fetch origin
git checkout production-deploy
git pull origin production-deploy

echo "[2/5] 检查是否有配置文件变更..."
if [ ! -f "docker/.env" ]; then
    echo "警告: docker/.env 不存在"
    echo "正在从 .env.prod 复制..."
    cp docker/.env.prod docker/.env
fi

if [ ! -f "backend/.env" ]; then
    echo "警告: backend/.env 不存在"
    echo "正在从 backend/.env.prod 复制..."
    cp backend/.env.prod backend/.env
fi

echo "[3/5] 重新构建并启动服务..."
cd docker
docker-compose down

echo "[4/5] 构建新的镜像..."
docker-compose build --no-cache frontend
docker-compose build --no-cache backend

echo "[5/5] 启动服务..."
docker-compose up -d

echo "========================================"
echo "  部署完成！"
echo "========================================"
echo "等待服务启动..."
sleep 10

echo "检查服务状态："
docker-compose ps

echo "\n健康检查："
FRONTEND_STATUS=$(curl -s -o /dev/null -w '%{http_code}' http://localhost/)
BACKEND_STATUS=$(curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/health)

echo "前端状态: $FRONTEND_STATUS"
echo "后端状态: $BACKEND_STATUS"

if [ "$FRONTEND_STATUS" = "200" ] && [ "$BACKEND_STATUS" = "200" ]; then
    echo "\n✅ 部署成功！所有服务正常运行"
else
    echo "\n⚠️  部署完成但有些服务可能有问题，请检查日志"
    echo "查看日志: docker-compose logs -f"
fi
