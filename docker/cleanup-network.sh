#!/bin/bash
# 清理现有网络，让 Docker Compose 重新创建
# 解决网络标签不匹配的问题

set -e

echo "🧹 清理现有网络..."
echo ""

TARGET_NET="docker_inspireed-network"

# 检查网络是否存在
if docker network inspect $TARGET_NET >/dev/null 2>&1; then
    echo "📊 检查网络状态..."
    
    # 检查网络是否被使用
    CONTAINERS=$(docker network inspect $TARGET_NET --format='{{len .Containers}}' 2>/dev/null || echo "0")
    
    if [ "$CONTAINERS" != "0" ]; then
        echo "⚠️  网络 $TARGET_NET 正在被 $CONTAINERS 个容器使用"
        echo "   先停止所有服务..."
        
        # 停止所有相关容器
        docker-compose -f docker-compose.prod.yml down 2>/dev/null || true
        
        # 等待容器完全停止
        sleep 3
        
        # 再次检查
        CONTAINERS=$(docker network inspect $TARGET_NET --format='{{len .Containers}}' 2>/dev/null || echo "0")
    fi
    
    if [ "$CONTAINERS" = "0" ]; then
        echo "✅ 网络为空，可以安全删除"
        echo "   删除网络: $TARGET_NET"
        docker network rm $TARGET_NET 2>/dev/null && echo "   ✅ 网络已删除" || echo "   ⚠️  无法删除网络"
    else
        echo "❌ 网络仍在使用中，无法删除"
        echo "   请手动停止所有容器后重试"
        exit 1
    fi
else
    echo "ℹ️  网络 $TARGET_NET 不存在，无需清理"
fi

echo ""
echo "✅ 清理完成！"
echo ""
echo "💡 下一步："
echo "   运行: docker-compose -f docker-compose.prod.yml up -d"
echo "   Compose 会自动创建正确配置的网络"

