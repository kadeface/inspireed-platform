#!/bin/bash
#
# 快速修复脚本：安装 Neo4j 依赖并重启后端
#

echo "🔧 修复 Neo4j 依赖..."

# 检查虚拟环境
if [ ! -f "backend/venv/bin/activate" ]; then
    echo "❌ 虚拟环境不存在，请先运行 ./start.sh"
    exit 1
fi

# 激活虚拟环境并安装 Neo4j 依赖
cd backend
source venv/bin/activate

echo "📦 安装 Neo4j 依赖..."
pip install neo4j==5.15.0

echo "✅ Neo4j 依赖安装完成"
echo ""
echo "💡 提示："
echo "   1. 如果需要启动后端服务，运行："
echo "      cd backend && source venv/bin/activate"
echo "      uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "   2. 或者重新运行完整启动脚本："
echo "      ./start.sh"

