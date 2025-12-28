#!/bin/bash
# 后端容器启动问题快速修复脚本
# 适用于腾讯 Cloud Studio 环境

set -e

echo "🔧 开始修复后端容器启动问题..."
echo ""

# 检查是否在正确的目录
if [ ! -f "docker-compose.prod.yml" ]; then
    echo "❌ 错误：请在 docker 目录下运行此脚本"
    exit 1
fi

# 1. 停止现有服务
echo "📦 停止现有服务..."
docker-compose -f docker-compose.prod.yml down backend 2>/dev/null || true
echo "✅ 服务已停止"
echo ""

# 2. 检查依赖服务
echo "🔍 检查依赖服务状态..."
POSTGRES_OK=$(docker ps | grep inspireed-postgres | grep -q "healthy" && echo "yes" || echo "no")
REDIS_OK=$(docker ps | grep inspireed-redis | grep -q "healthy" && echo "yes" || echo "no")
MINIO_OK=$(docker ps | grep inspireed-minio | grep -q "healthy" && echo "yes" || echo "no")

if [ "$POSTGRES_OK" != "yes" ] || [ "$REDIS_OK" != "yes" ] || [ "$MINIO_OK" != "yes" ]; then
    echo "⚠️  检测到依赖服务未就绪，先启动基础服务..."
    docker-compose -f docker-compose.prod.yml up -d postgres redis minio
    echo "⏳ 等待依赖服务启动（30秒）..."
    sleep 30
fi
echo "✅ 依赖服务检查完成"
echo ""

# 3. 重新构建后端镜像（如果需要）
echo "🔨 重新构建后端镜像..."
docker-compose -f docker-compose.prod.yml build backend
echo "✅ 镜像构建完成"
echo ""

# 4. 启动后端服务
echo "🚀 启动后端服务..."
docker-compose -f docker-compose.prod.yml up -d backend
echo "✅ 后端服务已启动"
echo ""

# 5. 等待服务启动
echo "⏳ 等待后端服务完全启动（60秒）..."
echo "   这包括："
echo "   - 应用启动"
echo "   - 数据库连接和初始化"
echo "   - 健康检查通过"
echo ""

for i in {1..12}; do
    sleep 5
    STATUS=$(docker inspect inspireed-backend --format='{{.State.Health.Status}}' 2>/dev/null || echo "starting")
    echo "   进度: $((i*5))秒 - 状态: $STATUS"
    
    if [ "$STATUS" = "healthy" ]; then
        echo ""
        echo "✅ 后端服务已健康！"
        break
    fi
done

echo ""

# 6. 检查最终状态
echo "📊 最终服务状态："
docker-compose -f docker-compose.prod.yml ps
echo ""

# 7. 测试健康端点
echo "🌐 测试健康端点："
if docker exec inspireed-backend python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health').read()" 2>/dev/null; then
    echo "✅ 健康检查端点正常"
else
    echo "⚠️  健康检查端点未响应，请查看日志："
    echo "   docker logs inspireed-backend --tail 50"
fi
echo ""

# 8. 显示日志
echo "📋 后端服务最新日志（最后 20 行）："
docker logs inspireed-backend --tail 20 2>&1 | tail -20
echo ""

echo "✅ 修复完成！"
echo ""
echo "💡 如果问题仍然存在，请运行诊断脚本："
echo "   ./diagnose-backend.sh"
echo ""
echo "📖 详细故障排查指南："
echo "   cat CLOUDSTUDIO_BACKEND_FIX.md"

