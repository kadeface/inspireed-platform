#!/bin/bash

# InspireEd 自动启动安装脚本
# 此脚本将配置系统在登录时自动启动 InspireEd 服务

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PLIST_NAME="com.inspireed.plist"
PLIST_TEMPLATE="$PROJECT_DIR/$PLIST_NAME"
LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"
PLIST_TARGET="$LAUNCH_AGENTS_DIR/$PLIST_NAME"

echo "🚀 安装 InspireEd 自动启动服务..."
echo ""

# 检查 Docker 是否运行
if ! docker info > /dev/null 2>&1; then
    echo "⚠️  警告: Docker 未运行"
    echo "   请确保 Docker Desktop 已启动，并且已设置为开机自动启动"
    echo "   Docker Desktop -> Settings -> General -> ✅ Start Docker Desktop when you log in"
    echo ""
    read -p "是否继续安装？(y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ 安装已取消"
        exit 1
    fi
fi

# 检查 start.sh 是否存在
if [ ! -f "$PROJECT_DIR/start.sh" ]; then
    echo "❌ 错误: 找不到 start.sh 文件"
    exit 1
fi

# 确保 start.sh 有执行权限
chmod +x "$PROJECT_DIR/start.sh"

# 创建 LaunchAgents 目录（如果不存在）
mkdir -p "$LAUNCH_AGENTS_DIR"

# 检查是否已安装
if [ -f "$PLIST_TARGET" ]; then
    echo "⚠️  检测到已存在的服务配置"
    read -p "是否卸载旧配置并重新安装？(y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🛑 卸载旧配置..."
        launchctl unload "$PLIST_TARGET" 2>/dev/null || true
        rm -f "$PLIST_TARGET"
    else
        echo "❌ 安装已取消"
        exit 1
    fi
fi

# 从模板创建 plist 文件
if [ ! -f "$PLIST_TEMPLATE" ]; then
    echo "❌ 错误: 找不到 plist 模板文件: $PLIST_TEMPLATE"
    exit 1
fi

echo "📝 创建 LaunchAgent 配置文件..."
sed "s|PROJECT_PATH|$PROJECT_DIR|g" "$PLIST_TEMPLATE" > "$PLIST_TARGET"

# 加载服务
echo "📦 加载服务..."
launchctl load "$PLIST_TARGET"

# 等待一下让服务启动
sleep 2

# 检查服务状态
if launchctl list | grep -q "com.inspireed"; then
    echo "✅ 服务已成功安装并加载"
else
    echo "⚠️  警告: 服务可能未正确加载，请检查日志"
fi

echo ""
echo "🎉 安装完成！"
echo ""
echo "📋 服务信息："
echo "   - 配置文件: $PLIST_TARGET"
echo "   - 日志文件: $PROJECT_DIR/logs/launchd.log"
echo "   - 错误日志: $PROJECT_DIR/logs/launchd.error.log"
echo ""
echo "🔍 验证安装："
echo "   launchctl list | grep inspireed"
echo ""
echo "📖 常用命令："
echo "   # 查看服务状态"
echo "   launchctl list | grep inspireed"
echo ""
echo "   # 手动启动服务"
echo "   launchctl load $PLIST_TARGET"
echo ""
echo "   # 停止服务（不会卸载）"
echo "   launchctl unload $PLIST_TARGET"
echo ""
echo "   # 查看日志"
echo "   tail -f $PROJECT_DIR/logs/launchd.log"
echo "   tail -f $PROJECT_DIR/logs/backend.log"
echo "   tail -f $PROJECT_DIR/logs/frontend.log"
echo ""
echo "   # 卸载服务"
echo "   $PROJECT_DIR/scripts/uninstall-autostart.sh"
echo ""
echo "💡 提示："
echo "   - 服务将在下次登录时自动启动"
echo "   - 如需立即测试，请注销并重新登录，或运行: launchctl unload $PLIST_TARGET && launchctl load $PLIST_TARGET"
echo "   - 首次启动可能需要 2-5 分钟，请耐心等待"
echo ""

