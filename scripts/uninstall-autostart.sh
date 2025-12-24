#!/bin/bash

# InspireEd 自动启动卸载脚本

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PLIST_NAME="com.inspireed.plist"
LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"
PLIST_TARGET="$LAUNCH_AGENTS_DIR/$PLIST_NAME"

echo "🛑 卸载 InspireEd 自动启动服务..."
echo ""

# 检查服务是否存在
if [ ! -f "$PLIST_TARGET" ]; then
    echo "ℹ️  未找到已安装的服务，无需卸载"
    exit 0
fi

# 停止并卸载服务
echo "📦 停止服务..."
launchctl unload "$PLIST_TARGET" 2>/dev/null || true

# 删除配置文件
echo "🗑️  删除配置文件..."
rm -f "$PLIST_TARGET"

echo "✅ 卸载完成！"
echo ""
echo "💡 提示："
echo "   - 服务已从自动启动中移除"
echo "   - 当前运行的服务不会被停止"
echo "   - 如需停止当前服务，请运行: $PROJECT_DIR/stop.sh"
echo ""

