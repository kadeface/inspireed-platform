#!/bin/bash
# 后端容器诊断脚本
# 用于排查 Cloud Studio 上后端容器无法启动的问题

set -e

echo "🔍 开始诊断后端容器问题..."
echo ""

# 检查容器状态
echo "📊 检查容器状态："
docker ps -a | grep inspireed-backend || echo "❌ 后端容器不存在"
echo ""

# 检查容器日志
echo "📋 后端容器日志（最后 50 行）："
docker logs inspireed-backend --tail 50 2>&1 || echo "❌ 无法获取日志"
echo ""

# 检查健康状态
echo "🏥 检查容器健康状态："
docker inspect inspireed-backend --format='{{.State.Health.Status}}' 2>/dev/null || echo "❌ 无法获取健康状态"
echo ""

# 检查依赖服务
echo "🔗 检查依赖服务状态："
echo "PostgreSQL:"
docker ps | grep inspireed-postgres && echo "✅ PostgreSQL 运行中" || echo "❌ PostgreSQL 未运行"
echo "Redis:"
docker ps | grep inspireed-redis && echo "✅ Redis 运行中" || echo "❌ Redis 未运行"
echo "MinIO:"
docker ps | grep inspireed-minio && echo "✅ MinIO 运行中" || echo "❌ MinIO 未运行"
echo ""

# 测试数据库连接
echo "🗄️ 测试数据库连接："
docker exec inspireed-postgres psql -U postgres -d inspireed -c "SELECT version();" 2>&1 || echo "❌ 数据库连接失败"
echo ""

# 测试后端健康端点
echo "🌐 测试后端健康端点："
docker exec inspireed-backend python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health').read()" 2>&1 && echo "✅ 健康检查通过" || echo "❌ 健康检查失败"
echo ""

# 检查环境变量
echo "⚙️ 检查后端环境变量："
docker exec inspireed-backend env | grep -E "POSTGRES|REDIS|MINIO" || echo "❌ 无法获取环境变量"
echo ""

# 检查端口
echo "🔌 检查端口占用："
netstat -tuln | grep 8000 || echo "⚠️ 端口 8000 未被占用（可能容器未启动）"
echo ""

# 检查网络连接
echo "🌐 测试容器间网络连接："
docker exec inspireed-backend ping -c 2 postgres 2>&1 | head -2 || echo "❌ 无法连接到 postgres"
docker exec inspireed-backend ping -c 2 redis 2>&1 | head -2 || echo "❌ 无法连接到 redis"
docker exec inspireed-backend ping -c 2 minio 2>&1 | head -2 || echo "❌ 无法连接到 minio"
echo ""

echo "✅ 诊断完成！"
echo ""
echo "💡 常见问题解决方案："
echo "1. 如果数据库连接失败，检查 POSTGRES_SERVER 环境变量是否为 'postgres'"
echo "2. 如果健康检查失败，等待更长时间（start_period 为 60s）"
echo "3. 查看完整日志：docker logs inspireed-backend -f"
echo "4. 重启服务：docker-compose -f docker-compose.prod.yml restart backend"

