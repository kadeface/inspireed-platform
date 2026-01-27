#!/bin/bash

# Docker 自动启动卸载脚本
# 用于卸载 macOS 上的 Docker Compose 自动启动服务

set -e

LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"
PLIST_FILE="$LAUNCH_AGENTS_DIR/com.inspireed.docker.plist"

echo "🗑️  卸载 Docker 自动启动..."

# 检查文件是否存在
if [ ! -f "$PLIST_FILE" ]; then
    echo "ℹ️  未找到配置文件: $PLIST_FILE"
    echo "   可能已经卸载或从未安装"
    exit 0
fi

# 停止并卸载服务
if launchctl list | grep -q "com.inspireed.docker"; then
    echo "⏹️  停止服务..."
    launchctl stop com.inspireed.docker 2>/dev/null || true
    
    echo "📤 卸载服务..."
    launchctl unload "$PLIST_FILE" 2>/dev/null || true
fi

# 删除配置文件
echo "🗑️  删除配置文件..."
rm -f "$PLIST_FILE"

echo "✅ Docker 自动启动已卸载"
echo ""
echo "💡 提示："
echo "   - Docker 容器不会在系统启动时自动启动"
echo "   - 你仍然可以使用 'docker-compose up -d' 手动启动服务"
echo "   - 容器仍会使用 restart: unless-stopped 策略（如果 Docker 正在运行）"

