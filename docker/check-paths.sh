#!/bin/bash
# 路径检查脚本 - 用于 CloudStudio 环境

echo "🔍 检查 Docker Compose 构建路径..."
echo ""

# 获取当前脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "📁 Docker Compose 文件位置: $SCRIPT_DIR"
echo ""

# 检查 backend 路径
BACKEND_PATH="$SCRIPT_DIR/../backend"
BACKEND_DOCKERFILE="$BACKEND_PATH/Dockerfile"

echo "🔍 检查 Backend:"
echo "   期望路径: $BACKEND_PATH"
if [ -d "$BACKEND_PATH" ]; then
    echo "   ✅ Backend 目录存在"
    if [ -f "$BACKEND_DOCKERFILE" ]; then
        echo "   ✅ Backend Dockerfile 存在: $BACKEND_DOCKERFILE"
    else
        echo "   ❌ Backend Dockerfile 不存在: $BACKEND_DOCKERFILE"
    fi
else
    echo "   ❌ Backend 目录不存在: $BACKEND_PATH"
    echo "   🔍 正在搜索 Backend Dockerfile..."
    find "$SCRIPT_DIR/.." -name "Dockerfile" -path "*/backend/*" 2>/dev/null | head -1
fi
echo ""

# 检查 frontend 路径
FRONTEND_PATH="$SCRIPT_DIR/../frontend"
FRONTEND_DOCKERFILE="$FRONTEND_PATH/Dockerfile"

echo "🔍 检查 Frontend:"
echo "   期望路径: $FRONTEND_PATH"
if [ -d "$FRONTEND_PATH" ]; then
    echo "   ✅ Frontend 目录存在"
    if [ -f "$FRONTEND_DOCKERFILE" ]; then
        echo "   ✅ Frontend Dockerfile 存在: $FRONTEND_DOCKERFILE"
    else
        echo "   ❌ Frontend Dockerfile 不存在: $FRONTEND_DOCKERFILE"
    fi
else
    echo "   ❌ Frontend 目录不存在: $FRONTEND_PATH"
    echo "   🔍 正在搜索 Frontend Dockerfile..."
    find "$SCRIPT_DIR/.." -name "Dockerfile" -path "*/frontend/*" 2>/dev/null | head -1
fi
echo ""

# 查找所有 Dockerfile
echo "📋 找到的所有 Dockerfile:"
find "$SCRIPT_DIR/.." -name "Dockerfile" -type f 2>/dev/null | while read -r file; do
    echo "   - $file"
done
echo ""

# 检查 backend 目录内容
echo "📦 Backend 目录内容（前10项）:"
if [ -d "$BACKEND_PATH" ]; then
    ls -la "$BACKEND_PATH" 2>/dev/null | head -12
else
    echo "   目录不存在"
fi
echo ""

# 检查 frontend 目录内容
echo "📦 Frontend 目录内容（前10项）:"
if [ -d "$FRONTEND_PATH" ]; then
    ls -la "$FRONTEND_PATH" 2>/dev/null | head -12
else
    echo "   目录不存在"
fi
echo ""

echo "💡 解决方案:"
echo ""
if [ ! -f "$BACKEND_DOCKERFILE" ] || [ ! -f "$FRONTEND_DOCKERFILE" ]; then
    echo "   ❌ Dockerfile 文件缺失！"
    echo ""
    echo "   请执行以下操作之一："
    echo "   1. 确认项目文件已完整上传到 CloudStudio"
    echo "   2. 检查 git 仓库是否已完整克隆"
    echo "   3. 如果使用 git，运行: git checkout . 或 git pull"
    echo "   4. 手动创建 Dockerfile（参考项目仓库）"
    echo ""
fi
echo "   如果路径不正确，请根据上述信息调整 docker-compose.prod.yml 中的路径"
echo "   或者将项目移动到正确的目录结构"

