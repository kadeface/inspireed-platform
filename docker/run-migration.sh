#!/bin/bash
# 运行数据库迁移脚本
# 适用于 Cloud Studio 和本地 Docker 环境

set -e

echo "🔄 开始运行数据库迁移..."
echo ""

# 检查后端容器是否运行
if ! docker ps | grep -q inspireed-backend; then
    echo "❌ 错误：后端容器未运行"
    echo "   请先启动后端服务："
    echo "   docker-compose -f docker-compose.prod.yml up -d backend"
    exit 1
fi

echo "🔍 检查数据库连接配置..."
echo "   数据库服务器:"
docker exec inspireed-backend python -c "from app.core.config import settings; print(f'  POSTGRES_SERVER={settings.POSTGRES_SERVER}')" 2>&1 || echo "  ⚠️  无法读取配置"
echo "   数据库 URI (隐藏密码):"
docker exec inspireed-backend python -c "from app.core.config import settings; uri = str(settings.DATABASE_URI); print(f'  {uri.split(\"@\")[1] if \"@\" in uri else \"***\"}')" 2>&1 || echo "  ⚠️  无法读取 URI"
echo ""

echo "📊 检查当前数据库版本..."
docker exec inspireed-backend alembic current 2>&1 || echo "⚠️  无法获取当前版本（可能是新数据库）"
echo ""

echo "🔄 运行数据库迁移..."
if docker exec inspireed-backend alembic upgrade head; then
    echo ""
    echo "✅ 数据库迁移完成！"
    echo ""
    echo "📊 当前数据库版本："
    docker exec inspireed-backend alembic current
else
    echo ""
    echo "❌ 数据库迁移失败"
    echo ""
    echo "💡 故障排查："
    echo "1. 查看详细错误：docker logs inspireed-backend"
    echo "2. 检查数据库连接：docker exec inspireed-backend python -c 'from app.core.config import settings; print(settings.DATABASE_URI)'"
    echo "3. 手动进入容器运行：docker exec -it inspireed-backend bash"
    exit 1
fi

