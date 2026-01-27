#!/bin/bash

# Docker 自动启动设置脚本
# 用于在 macOS 上设置 Docker Compose 服务自动启动

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"
PLIST_FILE="$LAUNCH_AGENTS_DIR/com.inspireed.docker.plist"
DOCKER_DIR="$PROJECT_DIR/docker"

echo "🔧 设置 Docker 自动启动..."

# 检查项目目录
if [ ! -d "$DOCKER_DIR" ]; then
    echo "❌ 错误：找不到 docker 目录: $DOCKER_DIR"
    exit 1
fi

# 创建 LaunchAgents 目录
mkdir -p "$LAUNCH_AGENTS_DIR"

# 检查是否已存在
if [ -f "$PLIST_FILE" ]; then
    echo "⚠️  发现已存在的配置文件: $PLIST_FILE"
    read -p "是否要覆盖？(y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ 已取消"
        exit 1
    fi
    # 卸载旧服务
    launchctl unload "$PLIST_FILE" 2>/dev/null || true
fi

# 创建 plist 文件
echo "📝 创建 LaunchAgent 配置文件..."
cat > "$PLIST_FILE" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.inspireed.docker</string>
    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>-c</string>
        <string>cd "$DOCKER_DIR" && /usr/local/bin/docker-compose up -d</string>
    </array>
    <key>WorkingDirectory</key>
    <string>$PROJECT_DIR</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <false/>
    <key>StandardOutPath</key>
    <string>$PROJECT_DIR/logs/docker-autostart.log</string>
    <key>StandardErrorPath</key>
    <string>$PROJECT_DIR/logs/docker-autostart.error.log</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/opt/homebrew/bin</string>
    </dict>
    <key>ThrottleInterval</key>
    <integer>10</integer>
</dict>
</plist>
EOF

# 创建日志目录
mkdir -p "$PROJECT_DIR/logs"

# 加载服务
echo "🚀 加载 LaunchAgent 服务..."
launchctl load "$PLIST_FILE"

# 等待一下
sleep 2

# 检查服务状态
if launchctl list | grep -q "com.inspireed.docker"; then
    echo "✅ Docker 自动启动已设置成功！"
    echo ""
    echo "📋 服务信息："
    echo "   配置文件: $PLIST_FILE"
    echo "   日志文件: $PROJECT_DIR/logs/docker-autostart.log"
    echo ""
    echo "🔍 管理命令："
    echo "   查看状态: launchctl list | grep com.inspireed.docker"
    echo "   手动启动: launchctl start com.inspireed.docker"
    echo "   停止服务: launchctl stop com.inspireed.docker"
    echo "   卸载服务: launchctl unload $PLIST_FILE"
    echo ""
    echo "💡 提示："
    echo "   - 服务会在系统登录时自动启动"
    echo "   - 确保 Docker Desktop 已设置为开机自启"
    echo "   - 重启系统后，Docker 容器会自动启动"
else
    echo "⚠️  警告：服务可能未正确加载，请检查日志"
    exit 1
fi

